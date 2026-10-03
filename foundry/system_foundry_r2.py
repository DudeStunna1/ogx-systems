#!/usr/bin/env python3
"""Proposed sandbox-only compiler. No installation or authority is issued."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'vendor'))
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SENSITIVE_FIELDS = frozenset({'secret','secrets','password','passwords','token','tokens','apikey','apikeys','credential','credentials','accesstoken','refreshtoken','privatekey','clientsecret'})
_SANDBOX_TOKEN = object()

def canonical(obj):
    return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + '\n'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result: raise ValueError('duplicate_json_key')
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite_json')))

def sensitive_fields(value):
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = re.sub('[^a-z0-9]', '', key.lower())
            if normalized in SENSITIVE_FIELDS: raise ValueError('sensitive_field_forbidden')
            sensitive_fields(item)
    elif isinstance(value, list):
        for item in value: sensitive_fields(item)

def schema_validate(value, name):
    schema = load(ROOT / 'contracts' / name)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

def validate(g):
    sensitive_fields(g)
    schema_validate(g, 'system-genome.schema.json')
    owners = load(ROOT / 'contracts/capability-ownership.json')['owners']
    for cap in g['capabilities']:
        if owners.get(cap) != g['system_ref']: raise ValueError('capability_ownership_conflict')

def validate_fleet(genomes):
    if len(genomes) != 7: raise ValueError('fleet_cardinality')
    for key in ['system_ref','domain_ref','repository','fqdn']:
        values = [g.get(key) for g in genomes]
        if len(set(values)) != 7: raise ValueError('duplicate_' + key)
    for g in genomes: validate(g)
    expected = {d['system_ref'] for d in load(ROOT/'local-node/fleet.json')['domains']}
    if {g['system_ref'] for g in genomes} != expected: raise ValueError('fleet_identity_mismatch')

def no_symlink_chain(path):
    for item in [path, *path.parents]:
        if item.is_symlink(): raise ValueError('symlink_path_forbidden')

class Sandbox:
    def __init__(self, token, root):
        if token is not _SANDBOX_TOKEN: raise ValueError('sandbox_not_owned')
        self.root = root
        self.identity = (root.stat().st_dev, root.stat().st_ino)

    @classmethod
    def create(cls, temporary_parent):
        parent = Path(temporary_parent).absolute()
        no_symlink_chain(parent)
        home = Path.home().resolve()
        protected = [home/'.local/share/ogx', home/'.local/state/ogx', home/'.config/ogx']
        if parent in [Path('/'),home] or any(parent == p or p in parent.parents for p in protected):
            raise ValueError('protected_sandbox_parent')
        if not parent.is_dir(): raise ValueError('temporary_parent_required')
        # Reject the repository root itself. A private fresh temporary child
        # beneath a workspace is still confined by the output/inode/dir_fd guard;
        # an unrelated ancestor marker does not identify this parent as a root.
        if (parent/'.git').exists() or parent==ROOT: raise ValueError('repository_sandbox_parent')
        root = Path(tempfile.mkdtemp(prefix='ogx-owned-sandbox-', dir=parent))
        os.chmod(root, 0o700)
        return cls(_SANDBOX_TOKEN, root)

    def output(self, target):
        if type(self) is not Sandbox: raise ValueError('sandbox_not_owned')
        no_symlink_chain(self.root)
        st = self.root.stat()
        if (st.st_dev,st.st_ino) != self.identity or not stat.S_ISDIR(st.st_mode): raise ValueError('sandbox_replaced')
        target = Path(target)
        if not target.is_absolute(): target = self.root/target
        # Only a fresh direct child is eligible. No normalization of '..'.
        if target.parent != self.root or target.name in {'','.', '..'}: raise ValueError('unsafe_output_path')
        if target.exists() or target.is_symlink(): raise ValueError('output_already_exists')
        return target

def passport(g):
    return {'schema':'OGX_SYSTEM_PASSPORT_R2_PROPOSED','system_ref':g['system_ref'],'genome_ref':'sha256:'+digest(canonical(g).encode()),'version':'0.2.0','artifact_state':'GENERATED','qualification_state':'UNTESTED','authority_state':'NONE','recovery_state':'UNPROVEN','effect_ceiling':'E0_LOCAL_ONLY','external_effect':False,'activated':False,'evidence_refs':[],'installation_evidence_refs':[]}

def generate(g, output, sandbox):
    if type(sandbox) is not Sandbox: raise ValueError('sandbox_not_owned')
    target = sandbox.output(output)
    validate(g)
    p = passport(g)
    schema_validate(p, 'system-passport.schema.json')
    documents = {
        'system-genome.json': g,
        'system-passport.json': p,
        'build-manifest.json': {'schema':'OGX_BUILD_MANIFEST_R2_PROPOSED','system_ref':g['system_ref'],'source_genome':p['genome_ref'],'generator':'OGX_SYSTEM_FOUNDRY_R2_PROPOSED','external_effect':False,'artifact_state':'GENERATED','contract_status':'PROPOSED'},
        'qualification-plan.json': {'schema':'OGX_QUALIFICATION_PLAN_R2_PROPOSED','gates':['SCHEMA_VALID','FLEET_MAPPING_VALID','DETERMINISTIC_OUTPUT','SANDBOX_CONFINED','RECOVERY_TESTED'],'qualification_issued':False},
        'recovery-plan.json': {'schema':'OGX_GENERATED_ARTIFACT_RECOVERY_PLAN_R2_PROPOSED','runtime_recovery_proven':False,'persistent_runtime_state_created':False,'automatic_deletion':False,'strategy':'PRESERVE_SANDBOX_FOR_REVIEW; NO_INSTALLATION_CREATED'}
    }
    files = {name:canonical(obj).encode('utf-8') for name,obj in documents.items()}
    files['MANIFEST.sha256'] = canonical({name:digest(data) for name,data in files.items()}).encode()
    # dir_fd + O_NOFOLLOW prevent a symlink swap from redirecting writes.
    root_fd = os.open(sandbox.root, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        st = os.fstat(root_fd)
        if (st.st_dev,st.st_ino) != sandbox.identity: raise ValueError('sandbox_replaced')
        os.mkdir(target.name, 0o700, dir_fd=root_fd)
        out_fd = os.open(target.name, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW, dir_fd=root_fd)
        try:
            for name,data in sorted(files.items()):
                fd = os.open(name, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600, dir_fd=out_fd)
                with os.fdopen(fd,'wb') as stream:
                    stream.write(data); stream.flush(); os.fsync(stream.fileno())
            os.fsync(out_fd)
        finally: os.close(out_fd)
        os.fsync(root_fd)
    finally: os.close(root_fd)
    return digest(files['MANIFEST.sha256'])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('genome'); parser.add_argument('output_label')
    parser.add_argument('--temporary-parent', required=True)
    args = parser.parse_args()
    try:
        if not re.fullmatch('[a-z0-9][a-z0-9_-]*',args.output_label): raise ValueError('unsafe_output_label')
        g = load(args.genome); validate(g)
        sandbox = Sandbox.create(args.temporary_parent)
        h = generate(g, args.output_label, sandbox)
        print(canonical({'build_result':'GENERATED','output':str(sandbox.root/args.output_label),'output_digest':h,'qualification_state':'UNTESTED','authority_state':'NONE','external_effect':False,'ZBOOK_INSTALLED':False}))
    except Exception as e:
        # Do not print user data, credentials or exception values.
        print('SYSTEMFOUNDRY=STOP ERROR_CLASS='+type(e).__name__,file=sys.stderr); return 20
    return 0

if __name__ == '__main__': raise SystemExit(main())
