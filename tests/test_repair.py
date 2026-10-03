import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import unittest

WORK = Path(__file__).resolve().parents[1]
BASE = WORK
sys.path.insert(0,str(WORK/'foundry'))
sys.path.insert(0,str(WORK/'local-node'))
from system_foundry_r2 import Sandbox, canonical, generate, load, passport, schema_validate, sensitive_fields, validate, validate_fleet
from release_store import FixtureNode, status, tree_digest, verify_bundle
from jsonschema.exceptions import ValidationError

TEMP = BASE/'test-sandboxes'
TEMP.mkdir(exist_ok=True)
GENOMES = [load(p) for p in sorted((WORK/'genomes').glob('*.system-genome.json'))]
EVIDENCE = {'environment':'CLOUD_TEST_ENVIRONMENT','scope':'PROPOSED_CONTRACTS_SANDBOX_COMPILER_AND_BLUEPRINT_RELEASE_STORAGE','ZBOOK_INSTALLED':False,'schema':[],'determinism':[],'negative':[],'installer':[]}

def tree(root):
    return {str(p.relative_to(root)):('SYMLINK:'+str(p.readlink()) if p.is_symlink() else 'DIR' if p.is_dir() else hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(root.rglob('*'))}

# Bundle is assembled from already verified generated output trees. The Foundry
# rejects nesting; do not weaken its direct-child guard for the installer test.
def make_bundle(revision=None):
    parent=Sandbox.create(TEMP)
    bundle=parent.output('bundle');bundle.mkdir()
    for genome in GENOMES:
        g=copy.deepcopy(genome)
        if revision:g['evidence_refs'].append('LOCAL_TEST_REVISION:'+revision)
        generated=Sandbox.create(TEMP)
        generate(g,'output',generated)
        shutil.copytree(generated.root/'output',bundle/g['system_ref'])
    return bundle

class RepairTests(unittest.TestCase):
    def reject(self,label,func,expected=(ValueError,ValidationError)):
        with self.assertRaises(expected):func()
        EVIDENCE['negative'].append({'case':label,'result':'REJECTED_AS_EXPECTED'})

    def test_01_schemas_and_determinism(self):
        validate_fleet(GENOMES)
        for g in GENOMES:
            a,b=Sandbox.create(TEMP),Sandbox.create(TEMP)
            da=generate(g,'output',a);db=generate(g,'output',b)
            self.assertEqual(tree(a.root/'output'),tree(b.root/'output'))
            self.assertEqual(da,db)
            p=load(a.root/'output/system-passport.json')
            schema_validate(g,'system-genome.schema.json');schema_validate(p,'system-passport.schema.json')
            self.assertEqual(p['qualification_state'],'UNTESTED');self.assertEqual(p['authority_state'],'NONE')
            self.assertIs(p['external_effect'],False);self.assertEqual(p['artifact_state'],'GENERATED')
            self.assertEqual(p['installation_evidence_refs'],[])
            EVIDENCE['schema'].append({'system_ref':g['system_ref'],'genome':'VALID_DRAFT_2020_12','passport':'VALID_DRAFT_2020_12'})
            EVIDENCE['determinism'].append({'system_ref':g['system_ref'],'digest':da,'complete_tree_equal':True,'sandbox_a':str(a.root),'sandbox_b':str(b.root),'independently_created':True})

    def test_02_sensitive_fields_and_legitimate_identifiers(self):
        vault=next(g for g in GENOMES if g['system_ref']=='VAULT.OS')
        validate(vault)
        self.assertIn('SECRETS_MODELING',vault['capabilities']);self.assertIn('CREDENTIAL_BOUNDARY_MODELING',vault['capabilities'])
        for field in ['secret','secrets','password','token','api_key','API-KEY','credential','credentials','access_token','refresh-token','privateKey','client_secret']:
            self.reject('sensitive:'+field,lambda f=field:sensitive_fields({'metadata':[{'nested':{f:'SYNTHETIC_VALUE'}}]}))
            g=copy.deepcopy(vault);g[field]='SYNTHETIC_VALUE'
            sb=Sandbox.create(TEMP);before=tree(sb.root)
            self.reject('genome_sensitive:'+field,lambda:generate(g,'output',sb))
            self.assertEqual(tree(sb.root),before);self.assertFalse((sb.root/'output').exists())

    def test_03_full_schema_negative(self):
        mutations={'missing_required':lambda g:g.pop('interfaces'),'unknown_property':lambda g:g.update(unsupported=True),'empty_identity':lambda g:g.update(system_ref=''),'duplicate_capability':lambda g:g['capabilities'].append(g['capabilities'][0]),'non_string_array_item':lambda g:g['interfaces'].append(8),'empty_effects':lambda g:g.update(effect_classes=[]),'non_E0':lambda g:g.update(effect_classes=['E2_PROVIDER_CONFIGURATION']),'wrong_domain':lambda g:g.update(domain_ref='OGX_HORIZON'),'wrong_repository':lambda g:g.update(repository='DudeStunna1/other'),'wrong_fqdn':lambda g:g.update(fqdn='wrong.example')}
        for label,change in mutations.items():
            g=copy.deepcopy(GENOMES[0]);change(g)
            sb=Sandbox.create(TEMP);before=tree(sb.root)
            self.reject(label,lambda:generate(g,'output',sb))
            self.assertEqual(tree(sb.root),before);self.assertFalse((sb.root/'output').exists())

    def test_04_fleet_negative(self):
        for key in ['system_ref','domain_ref','fqdn','repository']:
            fleet=copy.deepcopy(GENOMES);fleet[1][key]=fleet[0][key]
            self.reject('duplicate_'+key,lambda:validate_fleet(fleet))
        fleet=copy.deepcopy(GENOMES);fleet[0]['capabilities'].append(GENOMES[1]['capabilities'][0])
        self.reject('cross_domain_capability_conflict',lambda:validate_fleet(fleet))
        self.assertEqual(next(g['domain_ref'] for g in GENOMES if g['system_ref']=='HORIZON.OS'),'OGX_GLOBAL_HORIZON')

    def test_05_unsafe_output_paths_do_not_mutate(self):
        sb=Sandbox.create(TEMP)
        protected=Sandbox.create(TEMP).root
        for label in ['repository','installation','state']:
            (protected/label).mkdir();(protected/label/'sentinel').write_text('PRESERVE')
        (protected/'repository/.git').mkdir()
        unsafe=[Path('/'),Path.home(),WORK,protected/'repository',protected/'installation',protected/'state',protected/'outside',sb.root,sb.root/'../escape']
        before=tree(protected);owned_before=tree(sb.root)
        for path in unsafe:self.reject('unsafe_output:'+str(path),lambda p=path:generate(GENOMES[0],p,sb))
        self.assertEqual(before,tree(protected));self.assertEqual(owned_before,tree(sb.root))
        self.assertFalse((protected/'outside').exists())
        link=sb.root/'linked';link.symlink_to(protected/'installation',target_is_directory=True)
        self.reject('symlink_output',lambda:generate(GENOMES[0],link,sb));self.assertEqual(before,tree(protected))
        existing=sb.root/'existing';existing.mkdir();(existing/'sentinel').write_text('PRESERVE')
        self.reject('existing_output',lambda:generate(GENOMES[0],existing,sb));self.assertEqual((existing/'sentinel').read_text(),'PRESERVE')
        self.reject('repository_sandbox_parent',lambda:Sandbox.create(protected/'repository'))
        self.reject('root_sandbox_parent',lambda:Sandbox.create('/'))
        self.reject('home_sandbox_parent',lambda:Sandbox.create(Path.home()))
        self.reject('non_owned_sandbox',lambda:generate(GENOMES[0],'output',object()))

    def test_06_passport_contract_fail_closed(self):
        good=passport(GENOMES[0])
        for key,value in [('qualification_state','QUALIFIED'),('authority_state','BOUNDED'),('artifact_state','INSTALLED'),('external_effect',True),('activated',True),('unexpected',True),('installation_evidence_refs',['FORGED'])]:
            bad=dict(good);bad[key]=value
            self.reject('passport_mismatch:'+key,lambda:schema_validate(bad,'system-passport.schema.json'))
        spec=importlib.util.spec_from_file_location('old_foundry',BASE/'prior-candidate/foundry/system_foundry_r1.py')
        original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
        self.reject('preserved_original_NameError',lambda:original.validate(load(BASE/'prior-candidate/genomes/systems.system-genome.json')),NameError)

    def test_07_installer_upgrade_failure_and_rollback(self):
        node=FixtureNode(Sandbox.create(TEMP))
        self.assertEqual(status(node.root)['artifact_installation'],'NOT_PROVEN')
        a=make_bundle('A');b=make_bundle('B');c=make_bundle('C')
        ra=node.install(a);self.assertEqual(node.install(a),ra)
        self.assertEqual(status(node.root)['artifact_installation'],'INSTALLED_WITH_EVIDENCE')
        self.assertFalse(status(node.root)['ZBOOK_INSTALLED'])
        self.assertEqual(node.verify_release(ra)['domain_runtime_state'],'NOT_INSTALLED')
        node.qualify_fixture(ra)
        baseline=tree(node.root/'share/releases'/ra)
        for phase in ['stage','verify','publish']:
            self.reject('failed_upgrade:'+phase,lambda ph=phase:node.install(b,fail_at=ph),RuntimeError)
            self.assertEqual(node.selection()['current'],ra);self.assertEqual(tree(node.root/'share/releases'/ra),baseline)
        rb=node.install(b)
        self.assertEqual(node.selection(),{'current':rb,'previous':ra})
        rc=node.install(c)
        self.assertEqual(node.selection(),{'current':rc,'previous':ra})
        self.assertEqual(node.rollback(),ra)
        self.assertEqual(node.selection()['current'],ra)
        self.assertEqual(tree(node.root/'share/releases'/ra),baseline)
        # No generated passport inherits the separate fixture qualification record.
        for p in (node.root/'share/releases'/ra).glob('*/system-passport.json'):
            self.assertEqual(load(p)['qualification_state'],'UNTESTED')
        EVIDENCE['installer'].append({'stage_verify_publish':'PASS','idempotency':'PASS','failure_injection':['stage','verify','publish'],'qualified_fixture_preserved':True,'rollback':'PASS','current':ra,'previous_scope':'SYNTHETIC_PRIOR_QUALIFICATION_TEST_SCENARIO','ZBOOK_INSTALLED':False})

    def test_08_installer_corruption_and_evidence(self):
        node=FixtureNode(Sandbox.create(TEMP));a=make_bundle('D');b=make_bundle('E')
        ra=node.install(a);node.qualify_fixture(ra);rb=node.install(b)
        before=node.selection()
        corrupt=node.root/'share/releases'/ra/'SYSTEMS.OS/system-genome.json'
        corrupt.write_text(corrupt.read_text()+' ')
        self.reject('corrupt_rollback_target',node.rollback)
        self.assertEqual(node.selection(),before)
        bad=make_bundle('BAD');(bad/'SYSTEMS.OS/extra.json').write_text('{}')
        self.reject('unexpected_bundle_file',lambda:node.install(bad));self.assertEqual(node.selection(),before)
        (node.root/'state/installations'/f'{rb}.json').unlink()
        self.assertEqual(status(node.root)['artifact_installation'],'NOT_PROVEN')
        self.reject('missing_installation_evidence',lambda:node.verify_release(rb),FileNotFoundError)

    def test_09_domain_proposals(self):
        proposals=[load(p) for p in (BASE/'proposals').glob('*/ogx-domain.yaml')]
        self.assertEqual(len(proposals),7)
        for p in proposals:
            self.assertFalse(p['canonical']);self.assertEqual(p['status'],'PROPOSED')
            self.assertEqual(p['fqdn']['dns_ownership'],'UNRESOLVED')
            self.assertEqual(p['human_owner']['status'],'UNRESOLVED')
            self.assertTrue(p['evidence_refs'])

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(RepairTests)
    result=unittest.TextTestRunner(verbosity=2,failfast=True).run(suite)
    EVIDENCE['GLOBAL_PASS']=bool(result.wasSuccessful())
    EVIDENCE['tests_run']=result.testsRun
    EVIDENCE['schema_validator']='python-jsonschema 4.17.3 Draft202012Validator; official source'
    (BASE/'evidence/cloud-qualification.json').write_text(canonical(EVIDENCE))
    raise SystemExit(0 if result.wasSuccessful() else 20)
