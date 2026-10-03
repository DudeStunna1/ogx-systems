"""Portable installer storage mechanism. Only owned CLOUD_TEST_ENVIRONMENT fixtures.

This is not an eligible Debian/ZBook installer. It installs blueprint artifact
releases in private test fixtures and never claims domain runtime installation.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'foundry'))
from system_foundry_r2 import Sandbox, canonical, digest, load, schema_validate, validate, validate_fleet, no_symlink_chain

ENV = 'CLOUD_TEST_ENVIRONMENT'
EXPECTED_FILES = {'system-genome.json','system-passport.json','build-manifest.json','qualification-plan.json','recovery-plan.json','MANIFEST.sha256'}

def atomic_json(path, data):
    fd, tmp = tempfile.mkstemp(prefix='.pending-',dir=path.parent)
    with os.fdopen(fd,'w',encoding='utf-8') as stream:
        stream.write(canonical(data)); stream.flush(); os.fsync(stream.fileno())
    os.replace(tmp,path)
    parent_fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
    try: os.fsync(parent_fd)
    finally: os.close(parent_fd)

def tree_digest(root):
    no_symlink_chain(root)
    records={}
    for p in sorted(root.rglob('*')):
        if p.is_symlink(): raise ValueError('release_symlink')
        if p.is_file(): records[str(p.relative_to(root))]=digest(p.read_bytes())
        elif not p.is_dir(): raise ValueError('release_special_file')
    return digest(canonical(records).encode())

def verify_bundle(root):
    no_symlink_chain(root)
    genomes=[]
    entries=list(root.iterdir())
    if len(entries)!=7 or any(not p.is_dir() or p.is_symlink() for p in entries): raise ValueError('bundle_cardinality')
    for folder in sorted(entries):
        files=list(folder.iterdir())
        if {p.name for p in files}!=EXPECTED_FILES or any(not p.is_file() or p.is_symlink() for p in files): raise ValueError('bundle_file_set')
        hashes=load(folder/'MANIFEST.sha256')
        if set(hashes)!=EXPECTED_FILES-{'MANIFEST.sha256'}: raise ValueError('manifest_file_set')
        for name,h in hashes.items():
            if digest((folder/name).read_bytes())!=h: raise ValueError('artifact_digest_mismatch')
        g=load(folder/'system-genome.json'); p=load(folder/'system-passport.json')
        validate(g); schema_validate(p,'system-passport.schema.json')
        if p['system_ref']!=g['system_ref'] or p['genome_ref']!='sha256:'+digest(canonical(g).encode()): raise ValueError('passport_genome_mismatch')
        if folder.name!=g['system_ref']: raise ValueError('domain_folder_mismatch')
        b=load(folder/'build-manifest.json')
        if b['system_ref']!=g['system_ref'] or b['source_genome']!=p['genome_ref'] or b['external_effect'] is not False or b['artifact_state']!='GENERATED': raise ValueError('build_manifest_mismatch')
        if load(folder/'qualification-plan.json')['qualification_issued'] is not False: raise ValueError('qualification_self_issued')
        genomes.append(g)
    validate_fleet(genomes)
    return tree_digest(root)

class FixtureNode:
    def __init__(self, sandbox, label='node'):
        if type(sandbox) is not Sandbox: raise ValueError('fixture_sandbox_required')
        self.root=sandbox.output(label)
        self.root.mkdir(mode=0o700)
        for rel in ['share/releases','share/staging','state/installations','state/qualification','state/recovery','config','bin']:
            (self.root/rel).mkdir(parents=True,mode=0o700)
        atomic_json(self.root/'state/fixture.json', {'environment':ENV,'scope':'BLUEPRINT_ARTIFACT_RELEASE','ZBOOK_INSTALLED':False})

    def selection(self):
        p=self.root/'state/selection.json'
        return load(p) if p.exists() else {'current':None,'previous':None}

    def verify_release(self, rid):
        if not isinstance(rid,str) or not re.fullmatch('r2-[0-9a-f]{64}',rid): raise ValueError('invalid_release_id')
        release=self.root/'share/releases'/rid
        if verify_bundle(release)!=rid[3:]: raise ValueError('release_digest_mismatch')
        evidence=load(self.root/'state/installations'/f'{rid}.json')
        if evidence.get('release')!=rid or evidence.get('digest')!=rid[3:] or evidence.get('environment')!=ENV or evidence.get('scope')!='BLUEPRINT_ARTIFACT_RELEASE' or evidence.get('ZBOOK_INSTALLED') is not False: raise ValueError('installation_evidence_mismatch')
        return evidence

    def qualified(self,rid):
        if rid is None: return False
        self.verify_release(rid)
        p=self.root/'state/qualification'/f'{rid}.json'
        if not p.exists(): return False
        q=load(p)
        return q=={'release':rid,'digest':rid[3:],'environment':ENV,'scope':'SYNTHETIC_PRIOR_QUALIFICATION_TEST_FIXTURE','qualification_origin':'TEST_SCENARIO_SEED','qualification_state':'QUALIFIED','activated':False}

    def install(self,bundle,fail_at=None):
        no_symlink_chain(self.root)
        lock=open(self.root/'state/install.lock','a')
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            source_digest=verify_bundle(bundle)
            rid='r2-'+source_digest
            selection=self.selection()
            current=selection['current']
            if current: self.verify_release(current)
            destination=self.root/'share/releases'/rid
            if destination.exists():
                self.verify_release(rid)
            else:
                stage=Path(tempfile.mkdtemp(prefix='stage-',dir=self.root/'share/staging'))
                for p in sorted(bundle.iterdir()): shutil.copytree(p,stage/p.name)
                if fail_at=='stage': raise RuntimeError('injected_stage_failure')
                if verify_bundle(stage)!=source_digest: raise ValueError('stage_digest_mismatch')
                if fail_at=='verify': raise RuntimeError('injected_verify_failure')
                for p in stage.rglob('*'):
                    if p.is_file():
                        with p.open('rb') as stream: os.fsync(stream.fileno())
                os.rename(stage,destination)
                atomic_json(self.root/'state/installations'/f'{rid}.json', {'release':rid,'digest':source_digest,'environment':ENV,'scope':'BLUEPRINT_ARTIFACT_RELEASE','installation_state':'INSTALLED','domain_runtime_state':'NOT_INSTALLED','ZBOOK_INSTALLED':False,'external_effect':False})
            self.verify_release(rid)
            if fail_at=='publish': raise RuntimeError('injected_publish_failure')
            previous=selection['previous']
            if current!=rid and current and self.qualified(current): previous=current
            if current==rid: return rid
            atomic_json(self.root/'state/selection.json', {'current':rid,'previous':previous})
            return rid
        finally: lock.close()

    def qualify_fixture(self,rid):
        """Seed the prior-qualified scenario. This is not qualification issuance.

        Real portable mechanism qualification is issued separately by the test
        runner only after the complete recovery and negative suite succeeds.
        """
        self.verify_release(rid)
        atomic_json(self.root/'state/qualification'/f'{rid}.json', {'release':rid,'digest':rid[3:],'environment':ENV,'scope':'SYNTHETIC_PRIOR_QUALIFICATION_TEST_FIXTURE','qualification_origin':'TEST_SCENARIO_SEED','qualification_state':'QUALIFIED','activated':False})

    def rollback(self):
        no_symlink_chain(self.root)
        with open(self.root/'state/install.lock','a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            selection=self.selection(); previous=selection['previous']
            if not self.qualified(previous): raise ValueError('rollback_target_not_qualified')
            # One atomic record owns both pointers. No inconsistent pair of symlinks.
            atomic_json(self.root/'state/selection.json', {'current':previous,'previous':selection['current'] if self.qualified(selection['current']) else None})
            atomic_json(self.root/'state/recovery/last.json', {'restored_release':previous,'environment':ENV,'scope':'BLUEPRINT_ARTIFACT_STORAGE_ONLY','ZBOOK_INSTALLED':False,'external_effect':False})
            return previous

def status(root):
    """Read-only; directory existence never proves an installation."""
    node=object.__new__(FixtureNode);node.root=Path(root)
    try:
        no_symlink_chain(node.root)
        if load(node.root/'state/fixture.json')['environment']!=ENV: raise ValueError('wrong_environment')
        rid=node.selection()['current']
        if not rid: raise ValueError('no_selected_installation')
        evidence=node.verify_release(rid)
        return {'artifact_installation':'INSTALLED_WITH_EVIDENCE','environment':ENV,'release':rid,'artifact_qualification':'TEST_SCENARIO_QUALIFIED_MARKER' if node.qualified(rid) else 'UNTESTED','domain_runtime_state':'NOT_INSTALLED','ZBOOK_INSTALLED':False,'activated':False}
    except Exception:
        return {'artifact_installation':'NOT_PROVEN','environment':ENV,'ZBOOK_INSTALLED':False,'activated':False}
