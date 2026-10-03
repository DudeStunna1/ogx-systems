import copy, hashlib, json, os, pathlib, subprocess, sys, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'local-node'))
from ogx_node import Node,fixture_home,build,files,read,encode,COMPONENTS,PHASES
SHA=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
REPORT={'environment':'CLOUD_TEST_ENVIRONMENT','native_debian13':'NOT_YET_ZBOOK_VERIFIED','ZBOOK_INSTALLED':False,'cases':[]}
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.parent=pathlib.Path(tempfile.mkdtemp(prefix='ogx-adapter-tests-',dir=ROOT.parent));cls.h=fixture_home(cls.parent);cls.n=Node(cls.h,True);cls.n.initialize();cls.bundle=build(cls.n,ROOT,SHA)
 def setUp(self):
  self.h=fixture_home(self.parent);self.n=Node(self.h,True);self.n.initialize();self.b=self.n.roots['cache']/'fixture-bundle';self.b.mkdir()
  import shutil
  shutil.copytree(self.bundle/'vault',self.b/'vault')
 def tearDown(self):REPORT['cases'].append(self.id())
 def install(self):return self.n.install('vault',self.b/'vault',SHA)
 def upgrade(self):
  d=read(self.b/'vault/runtime-descriptor.json');d['revision']='upgrade';(self.b/'vault/runtime-descriptor.json').write_bytes(encode(d));m=read(self.b/'vault/manifest.json');f=files(self.b/'vault');f.pop('manifest.json');m['files']=f;(self.b/'vault/manifest.json').write_bytes(encode(m));return 'r-'+hashlib.sha256(encode(m)).hexdigest()
 def test_01_fresh_repeat_all_components_and_cli(self):
  for c in COMPONENTS:self.n.install(c,self.bundle/c if False else self.copy_component(c),SHA)
  self.n.install_cli();s=self.n.status();self.assertTrue(all(x['state']=='INSTALLED' and not x['running'] for x in s['components'].values()));self.assertEqual(self.install(),self.install())
  for args in [['status'],['doctor'],['fleet','status'],['verify'],['release','status'],['recovery','status']]+[[c,'status'] for c in COMPONENTS[1:]]:
   p=subprocess.run([str(self.n.cli),'--home',str(self.h),'--cloud-fixture',*args],capture_output=True,text=True);self.assertEqual(p.returncode,0,p.stdout+p.stderr);json.loads(p.stdout)
 def copy_component(self,c):
  import shutil
  p=self.b/c
  if not p.exists():shutil.copytree(self.bundle/c,p)
  return p
 def test_02_upgrade_rollback_repeat(self):
  a=self.install();b=self.upgrade();self.assertEqual(self.install(),b);self.assertEqual(self.n.selection('vault')['previous'],a);self.assertEqual(self.n.rollback('vault'),a);self.assertEqual(self.n.rollback('vault'),'NO_PREVIOUS_RELEASE');self.n.verify_release('vault',a)
 def test_03_failures_every_phase_and_resume(self):
  for phase in PHASES:
   h=fixture_home(self.parent);n=Node(h,True);n.initialize();import shutil
   b=n.roots['cache']/'input';shutil.copytree(self.b/'vault',b);a=n.install('vault',b,SHA);d=read(b/'runtime-descriptor.json');d['revision']=phase;(b/'runtime-descriptor.json').write_bytes(encode(d));m=read(b/'manifest.json');f=files(b);f.pop('manifest.json');m['files']=f;(b/'manifest.json').write_bytes(encode(m))
   with self.assertRaises(RuntimeError):n.install('vault',b,SHA,fail=phase)
   n.verify_release('vault',a);j=n.pending('vault')[0];self.assertIn(n.classify(j),['SAFE_TO_RESUME','SAFE_TO_ROLLBACK']);n.recover(j['id'],'resume');self.assertFalse(n.pending('vault'));self.assertEqual(n.status()['components']['vault']['state'],'INSTALLED');n.verify_release('vault',a)
 def test_04_after_switch_rollback(self):
  a=self.install();self.upgrade()
  with self.assertRaises(RuntimeError):self.n.install('vault',self.b/'vault',SHA,fail='ATOMIC_SWITCH')
  j=self.n.pending('vault')[0];self.assertEqual(self.n.classify(j),'SAFE_TO_ROLLBACK');self.n.recover(j['id'],'rollback');self.assertEqual(self.n.selection('vault')['current'],a)
 def test_05_corrupt_missing_candidates_and_manifests(self):
  a=self.install();self.upgrade();(self.b/'vault/system-genome.json').write_text('{}')
  with self.assertRaises(Exception):self.install()
  self.n.verify_release('vault',a)
  with self.assertRaises(Exception):self.n.install('vault',self.n.roots['cache']/'missing',SHA)
  m=self.n.component('vault')/'releases'/a/'manifest.json';saved=m.read_bytes();m.write_text('{}');self.assertEqual(self.n.status()['components']['vault']['state'],'BLOCKED');m.write_bytes(saved);self.n.verify_release('vault',a)
 def test_06_passport_corruption_wrong_sha_wrong_digest(self):
  a=self.install()
  with self.assertRaises(ValueError):self.n.install('vault',self.b/'vault','0'*40)
  p=self.b/'vault/system-passport.json';v=read(p);v['artifact_state']='INSTALLED';p.write_bytes(encode(v));m=read(self.b/'vault/manifest.json');f=files(self.b/'vault');f.pop('manifest.json');m['files']=f;(self.b/'vault/manifest.json').write_bytes(encode(m))
  with self.assertRaises(Exception):self.install()
  self.n.verify_release('vault',a)
  ev=self.n.roots['state']/'installations'/('vault-'+a+'.json');v=read(ev);v['manifest_digest']='0'*64;ev.write_bytes(encode(v));self.assertEqual(self.n.status()['components']['vault']['state'],'BLOCKED')
 def test_07_path_rejections_without_mutation(self):
  before=files(self.h)
  targets=[pathlib.Path('/'),pathlib.Path.home(),ROOT,self.h,self.h/'outside',pathlib.Path('/mnt/c/ogx'),self.n.roots['install'],self.n.roots['state']]
  for p in targets:
   with self.assertRaises(ValueError):self.n.confined(p,'cache')
  self.assertEqual(files(self.h),before)
  with self.assertRaises(ValueError):Node(ROOT,True)
  h=fixture_home(self.parent);p=h/'.local/share/ogx';p.mkdir(parents=True);(p/'sentinel').write_text('PRESERVE')
  with self.assertRaises(ValueError):Node(h,True).initialize()
  self.assertEqual((p/'sentinel').read_text(),'PRESERVE');self.assertFalse((h/'.local/state/ogx').exists())
 def test_08_symlink_escape(self):
  out=fixture_home(self.parent);link=self.n.roots['cache']/'escape';link.symlink_to(out,target_is_directory=True);before=files(out)
  with self.assertRaises(ValueError):self.n.install('vault',link,SHA)
  self.assertEqual(files(out),before)
 def test_09_doctor_readonly_and_no_false_running(self):
  self.install();before=files(self.h);o=self.n.doctor();self.assertEqual(files(self.h),before);self.assertFalse(o['repair_performed']);self.assertFalse(o['fleet']['components']['vault']['running'])
  empty=fixture_home(self.parent);n=Node(empty,True);before=files(empty);self.assertEqual(n.status()['components']['vault']['state'],'NOT_INSTALLED');n.doctor();self.assertEqual(files(empty),before)
 def test_10_evidence_and_journal_truth(self):
  a=self.install();ev=self.n.roots['state']/'installations'/('vault-'+a+'.json');ev.unlink();self.assertEqual(self.n.status()['components']['vault']['state'],'BLOCKED')
 def test_11_ambiguous_and_pending_no_blind_retry(self):
  a=self.install();self.upgrade()
  with self.assertRaises(RuntimeError):self.n.install('vault',self.b/'vault',SHA,fail='VERIFY')
  with self.assertRaises(ValueError):self.install()
  j=self.n.pending('vault')[0];(self.n.component('vault')/'current').write_bytes(encode({'current':'r-'+'0'*64,'previous':None}));self.assertEqual(self.n.classify(j),'AMBIGUOUS_STOP')
  with self.assertRaises(ValueError):self.n.recover(j['id'],'resume')
 def test_12_native_platform_gate_and_source_sha(self):
  with self.assertRaises(ValueError):Node().initialize()
  with self.assertRaises(ValueError):build(self.n,ROOT,'0'*40)
 def test_13_tested_qualified_are_separate_evidence(self):
  rid=self.install();report=self.n.roots['state']/'fixture-report.json';report.write_bytes(encode({'PASS':True,'scope':'SYNTHETIC_TEST_FIXTURE'}))
  for directory,label in [('tests','TESTED'),('qualifications','QUALIFIED')]:
   v={'component':'vault','release_id':rid,'manifest_digest':rid[2:],'state':label,'scope':'LOCAL_ARTIFACT_ONLY','origin':'SYNTHETIC_TEST_FIXTURE','report_path':'fixture-report.json','report_digest':hashlib.sha256(report.read_bytes()).hexdigest()};(self.n.roots['state']/directory/('vault-'+rid+'.json')).write_bytes(encode(v));self.assertEqual(self.n.status()['components']['vault']['state'],label)
  self.assertFalse(self.n.status()['components']['vault']['running']);report.write_text('{}');self.assertEqual(self.n.status()['components']['vault']['state'],'BLOCKED')
 def test_14_corrupt_or_missing_after_switch_recover_old(self):
  for mode in ['missing','corrupt']:
   h=fixture_home(self.parent);n=Node(h,True);n.initialize();import shutil
   b=n.roots['cache']/'input';shutil.copytree(self.b/'vault',b);a=n.install('vault',b,SHA);d=read(b/'runtime-descriptor.json');d['revision']=mode;(b/'runtime-descriptor.json').write_bytes(encode(d));m=read(b/'manifest.json');f=files(b);f.pop('manifest.json');m['files']=f;(b/'manifest.json').write_bytes(encode(m))
   with self.assertRaises(RuntimeError):n.install('vault',b,SHA,fail='ATOMIC_SWITCH')
   j=n.pending('vault')[0];p=n.component('vault')/'releases'/j['candidate']
   if mode=='missing':p.rename(n.component('vault')/'preserved-missing-candidate')
   else:(p/'system-genome.json').write_text('{}')
   self.assertEqual(n.classify(j),'SAFE_TO_ROLLBACK');n.recover(j['id'],'rollback');self.assertEqual(n.selection('vault')['current'],a);n.verify_release('vault',a)
 def test_15_cache_build_symlink_no_escape(self):
  external=fixture_home(self.parent);(self.n.roots['cache']/'builds').symlink_to(external,target_is_directory=True);before=files(external)
  with self.assertRaises(ValueError):build(self.n,ROOT,SHA)
  self.assertEqual(files(external),before)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2,failfast=True).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests));REPORT.update(tests_total=result.testsRun,tests_pass=result.testsRun-len(result.failures)-len(result.errors),tests_fail=len(result.failures)+len(result.errors),PASS=result.wasSuccessful());(ROOT.parent/'adapter-test-evidence.json').write_text(json.dumps(REPORT,indent=2)+'\n');raise SystemExit(0 if result.wasSuccessful() else 20)
