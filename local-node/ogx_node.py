#!/usr/bin/env python3
"""E0 artifact installer. Runtime and target qualification are separate evidence."""
import argparse, contextlib, fcntl, hashlib, json, os, platform, re, shutil, stat, subprocess, sys, tempfile, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor'))
from jsonschema import Draft202012Validator
COMPONENTS=('prime','systems','vault','global','studios','academy','shop','horizon')
STATE_VOCABULARY=('NOT_INSTALLED','INSTALLED','TESTED','QUALIFIED','RUNNING','BLOCKED','UNRESOLVED')
PHASES=('PREPARE','BUILD','VERIFY','STAGE','INSTALL_RELEASE','RECORD_EVIDENCE','ATOMIC_SWITCH','POST_VERIFY','COMMIT')
def encode(v):return (json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def read(p):
 safe(p)
 def pairs(xs):
  d={}
  for k,v in xs:
   if k in d:raise ValueError('duplicate_json_key')
   d[k]=v
  return d
 return json.loads(Path(p).read_text(),object_pairs_hook=pairs)
def safe(p):
 p=Path(p).absolute()
 if '..' in p.parts or str(p).startswith('/mnt/'):raise ValueError('unsafe_path')
 for x in (p,*p.parents):
  if x.is_symlink():raise ValueError('symlink_path')
 return p
def files(p):
 result={}
 for f in sorted(p.rglob('*')):
  safe(f)
  if f.is_file():result[str(f.relative_to(p))]=digest(f.read_bytes())
  elif not f.is_dir():raise ValueError('unsupported_payload_entry')
 return result
def atomic(p,v):
 safe(p);tmp=p.parent/('.atomic-'+uuid.uuid4().hex)
 with tmp.open('xb') as f:f.write(encode(v));f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
 fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
def schema(v,name):
 s=read(ROOT/'local-node'/name);Draft202012Validator.check_schema(s);Draft202012Validator(s).validate(v)
def target_observation():
 osdata={}
 for s in Path('/etc/os-release').read_text().splitlines():
  if '=' in s:k,v=s.split('=',1);osdata[k]=v.strip('"')
 kernel=platform.release();return {'os':osdata.get('ID'),'version':osdata.get('VERSION_ID'),'architecture':platform.machine(),'wsl2':bool(re.search(r'microsoft.*wsl2|wsl2.*microsoft',kernel,re.I)),'environment':'CLOUD_TEST_ENVIRONMENT' if osdata.get('ID')!='debian' else 'OBSERVED_HOST'}
def fixture_home(parent):
 p=safe(parent)
 if p in (Path('/'),Path.home()) or (p/'.git').exists():raise ValueError('unsafe_fixture_parent')
 h=Path(tempfile.mkdtemp(prefix='ogx-cloud-fixture-',dir=p));(h/'.ogx-cloud-fixture').write_bytes(encode({'environment':'CLOUD_TEST_ENVIRONMENT'}));return h
class Node:
 def __init__(self,home=None,fixture=False):
  self.home=safe(home or Path.home());self.fixture=fixture
  if self.home==Path('/') or (self.home/'.git').exists():raise ValueError('invalid_home')
  if fixture and (not self.home.name.startswith('ogx-cloud-fixture-') or not (self.home/'.ogx-cloud-fixture').is_file()):raise ValueError('unowned_fixture')
  if not fixture and self.home!=Path.home():raise ValueError('foreign_home')
  self.roots={'install':self.home/'.local/share/ogx','state':self.home/'.local/state/ogx','config':self.home/'.config/ogx','cache':self.home/'.cache/ogx'}
  self.cli=self.home/'.local/bin/ogx';self.source=self.home/'runner-work'
  for p in [*self.roots.values(),self.cli]:safe(p)
  self.environment='CLOUD_TEST_ENVIRONMENT' if fixture else 'ZBOOK_TARGET_OBSERVATION'
 def owned(self):
  tokens=[]
  for role,p in self.roots.items():
   safe(p);m=read(p/'.ogx-owner.json')
   if m.get('role')!=role or m.get('home')!=str(self.home):raise ValueError('foreign_root')
   tokens.append(m['node_id'])
  if len(set(tokens))!=1:raise ValueError('ownership_mismatch')
  return tokens[0]
 def initialize(self):
  if not self.fixture:
   o=target_observation()
   if o['os']!='debian' or o['version']!='13' or not o['wsl2']:raise ValueError('NOT_YET_ZBOOK_VERIFIED')
  existing=[p.exists() for p in self.roots.values()]
  if any(existing):
   if not all(existing):raise ValueError('partial_ownership_stop')
   self.owned();return
  # Validate the entire write plan before creating any owned root.
  if self.cli.exists():raise ValueError('unowned_cli')
  for p in self.roots.values():
   if p.exists() or p==self.source or self.source in p.parents:raise ValueError('unowned_root')
  node=uuid.uuid4().hex
  for role,p in self.roots.items():
   safe(p);p.mkdir(parents=True,mode=0o700);atomic(p/'.ogx-owner.json',{'node_id':node,'role':role,'home':str(self.home)})
  for p in [self.roots['install']/'components',self.roots['state']/'transactions',self.roots['state']/'installations',self.roots['state']/'qualifications',self.roots['state']/'tests']:p.mkdir(mode=0o700)
 def confined(self,p,role):
  self.owned();p=safe(p);root=self.roots[role]
  if p==root or root not in p.parents:raise ValueError('outside_owned_root')
  if any((x/'.git').exists() for x in [p,*p.parents] if x!=root and root in x.parents):raise ValueError('repository_write_target')
  return p
 @contextlib.contextmanager
 def lock(self):
  self.owned();p=self.confined(self.roots['state']/'lock','state')
  fd=os.open(p,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
  try:fcntl.flock(fd,fcntl.LOCK_EX);yield
  finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
 def component(self,c):
  if c not in COMPONENTS:raise ValueError('unknown_component')
  return self.confined(self.roots['install']/'components'/c,'install')
 def selection(self,c):
  p=self.component(c)/'current';return read(p) if p.exists() else {'current':None,'previous':None}
 def verify_payload(self,p,c,expected):
  safe(p);m=read(p/'manifest.json');schema(m,'artifact-manifest.schema.json')
  if m['component']!=c or m['source_commit']!=expected:raise ValueError('source_mismatch')
  actual=files(p);actual.pop('manifest.json',None)
  if actual!=m['files']:raise ValueError('manifest_mismatch')
  d=read(p/'runtime-descriptor.json')
  schema(d,'runtime-descriptor.schema.json')
  if d['component']!=c or d['runtime_implemented'] or d['runtime_class'] not in ['INSTALLABLE_BLUEPRINT','CONTRACT_ONLY']:raise ValueError('runtime_claim')
  if c!='prime':
   for name in ['system-genome','system-passport']:
    s=read(ROOT/'contracts'/(name+'.schema.json'));Draft202012Validator(s).validate(read(p/(name+'.json')))
   sys.path.insert(0,str(ROOT/'foundry'))
   from system_foundry_r2 import validate,canonical
   g=read(p/'system-genome.json');validate(g)
   if read(p/'system-passport.json')['genome_ref']!='sha256:'+digest(canonical(g).encode()):raise ValueError('passport_genome_binding')
  return digest(encode(m))
 def verify_release(self,c,rid):
  if not re.fullmatch('r-[a-f0-9]{64}',rid):raise ValueError('invalid_release')
  p=self.component(c)/'releases'/rid;self.confined(p,'install')
  ev=read(self.confined(self.roots['state']/'installations'/(c+'-'+rid+'.json'),'state'));schema(ev,'installation-evidence.schema.json')
  if ev['component']!=c or ev['release_id']!=rid or ev['node_id']!=self.owned():raise ValueError('evidence_binding')
  if self.verify_payload(p,c,ev['source_commit'])!=ev['manifest_digest'] or rid!='r-'+ev['manifest_digest']:raise ValueError('digest_mismatch')
  return ev
 def pending(self,c):
  out=[]
  for p in (self.roots['state']/'transactions').glob('*.json'):
   safe(p);j=read(p)
   if j['component']==c and j['outcome'] not in ['COMPLETE','ROLLED_BACK']:out.append(j)
  return out
 def install(self,c,bundle,expected,fail=None):
  # Input is an explicitly owned builder directory, never an external path.
  self.owned();b=self.confined(bundle,'cache');self.verify_payload(b,c,expected)
  with self.lock():
   if self.pending(c):raise ValueError('pending_transaction_requires_readback')
   old=self.selection(c);rid='r-'+digest(encode(read(b/'manifest.json')))
   if old['current']==rid:self.verify_release(c,rid);return rid
   if old['current']:self.verify_release(c,old['current'])
   cp=self.component(c);cp.mkdir(exist_ok=True);(cp/'releases').mkdir(exist_ok=True)
   tx=uuid.uuid4().hex;j={'id':tx,'component':c,'kind':'INSTALL','phase':'PREPARE','outcome':'PENDING','old':old,'candidate':rid,'source_commit':expected,'bundle':str(b),'environment':self.environment}
   jp=self.roots['state']/'transactions'/(tx+'.json');atomic(jp,j)
   try:
    for phase in PHASES:
     j['phase']=phase;atomic(jp,j)
     release=cp/'releases'/rid;stage=cp/('stage-'+tx)
     if phase=='BUILD':self.verify_payload(b,c,expected)
     if phase=='VERIFY':self.verify_payload(b,c,expected)
     if phase=='STAGE':
      self.confined(stage,'install');shutil.copytree(b,stage);self.verify_payload(stage,c,expected)
      for f in stage.rglob('*'):
       if f.is_file():
        with f.open('rb') as stream:os.fsync(stream.fileno())
      fd=os.open(stage,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
     if phase=='INSTALL_RELEASE':
      if release.exists():self.verify_payload(release,c,expected)
      else:os.rename(stage,release)
      fd=os.open(release.parent,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
     if phase=='RECORD_EVIDENCE':
      ev={'schema':'OGX_INSTALLATION_EVIDENCE_R0','component':c,'release_id':rid,'source_commit':expected,'manifest_digest':rid[2:],'node_id':self.owned(),'transaction_id':tx,'environment':self.environment,'scope':'LOCAL_ARTIFACT_RELEASE','runtime_implemented':False,'qualification_state':'UNTESTED','external_effect':False}
      schema(ev,'installation-evidence.schema.json');atomic(self.roots['state']/'installations'/(c+'-'+rid+'.json'),ev)
     if phase=='ATOMIC_SWITCH':
      atomic(cp/'current',{'current':rid,'previous':old['current'] or old['previous']});atomic(cp/'previous',{'release_id':old['current'] or old['previous'],'view_of':'current.previous'})
     if phase=='POST_VERIFY':self.verify_release(c,rid)
     if fail==phase:raise RuntimeError('INJECTED_FAILURE_'+phase)
    j['outcome']='COMPLETE';atomic(jp,j);return rid
   except Exception:
    j['outcome']='INTERRUPTED';atomic(jp,j);raise
 def classify(self,j):
  if j['outcome'] in ['COMPLETE','ROLLED_BACK']:return 'COMPLETE'
  try:
   c=j['component'];sel=self.selection(c)
   if sel==j['old']:
    if j['old']['current']:self.verify_release(c,j['old']['current'])
    return 'SAFE_TO_RESUME'
   if sel['current']==j['candidate']:
    if j['old']['current']:self.verify_release(c,j['old']['current']);return 'SAFE_TO_ROLLBACK'
    self.verify_release(c,j['candidate']);return 'SAFE_TO_RESUME'
  except Exception:return 'AMBIGUOUS_STOP'
  return 'AMBIGUOUS_STOP'
 def recover(self,tx,action):
  if not re.fullmatch('[a-f0-9]{32}',tx):raise ValueError('invalid_transaction')
  with self.lock():
   p=self.confined(self.roots['state']/'transactions'/(tx+'.json'),'state');j=read(p);kind=self.classify(j)
   if kind=='COMPLETE':return kind
   if kind=='AMBIGUOUS_STOP':raise ValueError(kind)
   c=j['component'];cp=self.component(c)
   if action=='resume' and self.selection(c)['current']==j['candidate']:
    self.verify_release(c,j['candidate']);atomic(cp/'previous',{'release_id':self.selection(c)['previous'],'view_of':'current.previous'});j['phase']='COMMIT';j['outcome']='COMPLETE';atomic(p,j);return 'COMPLETE'
   # Abort preserves all release bytes; restore only a verified prior selection.
   if action=='resume' and j['kind']=='INSTALL':
    b=self.confined(j['bundle'],'cache')
    if 'r-'+self.verify_payload(b,c,j['source_commit'])!=j['candidate']:raise ValueError('resume_input_changed')
   if j['old']['current']:self.verify_release(c,j['old']['current'])
   atomic(cp/'current',j['old']);atomic(cp/'previous',{'release_id':j['old']['previous'],'view_of':'current.previous'});j['outcome']='ROLLED_BACK';atomic(p,j)
  if action=='resume':return self.install(c,j['bundle'],j['source_commit'])
  return 'COMPLETE'
 def rollback(self,c):
  with self.lock():
   if self.pending(c):raise ValueError('pending_transaction_requires_recovery')
   s=self.selection(c);rid=s['previous']
   if rid is None:return 'NO_PREVIOUS_RELEASE'
   self.verify_release(c,rid)
   tx=uuid.uuid4().hex;p=self.roots['state']/'transactions'/(tx+'.json');j={'id':tx,'component':c,'kind':'ROLLBACK','phase':'ATOMIC_SWITCH','outcome':'PENDING','old':s,'candidate':rid,'source_commit':self.verify_release(c,rid)['source_commit'],'bundle':None,'environment':self.environment};atomic(p,j)
   # Consume previous, making repeated rollback idempotent rather than a toggle.
   atomic(self.component(c)/'current',{'current':rid,'previous':None});atomic(self.component(c)/'previous',{'release_id':None,'view_of':'current.previous'});self.verify_release(c,rid);j['phase']='COMMIT';j['outcome']='COMPLETE';atomic(p,j);return rid
 def status(self):
  try:self.owned()
  except FileNotFoundError:return {'environment':self.environment,'components':{c:{'state':'NOT_INSTALLED','running':False} for c in COMPONENTS}}
  except Exception:return {'environment':self.environment,'state':'BLOCKED','reason':'OWNERSHIP_OR_PATH_INVALID'}
  result={}
  for c in COMPONENTS:
   try:
    s=self.selection(c);state='NOT_INSTALLED';ev=None
    origin=None
    if s['current']:
     ev=self.verify_release(c,s['current']);tx=read(self.roots['state']/'transactions'/(ev['transaction_id']+'.json'))
     if tx['outcome']!='COMPLETE':raise ValueError('incomplete_installation')
     if read(self.component(c)/'previous')!={'release_id':s['previous'],'view_of':'current.previous'}:raise ValueError('pointer_view_out_of_sync')
     state='INSTALLED'
     for directory,label in [('tests','TESTED'),('qualifications','QUALIFIED')]:
      record=self.roots['state']/directory/(c+'-'+s['current']+'.json')
      if record.exists():
       v=read(record);schema(v,'component-verification.schema.json')
       proof=self.confined(self.roots['state']/v['report_path'],'state')
       if v['component']!=c or v['release_id']!=s['current'] or v['manifest_digest']!=ev['manifest_digest'] or v['state']!=label or digest(proof.read_bytes())!=v['report_digest'] or read(proof).get('PASS') is not True:raise ValueError('invalid_verification_evidence')
       if label=='QUALIFIED' and state!='TESTED':raise ValueError('qualification_without_testing')
       if v['origin']=='SYNTHETIC_TEST_FIXTURE' and not self.fixture:raise ValueError('synthetic_target_qualification')
       state=label;origin=v['origin']
    # No runtime backend selected: never infer RUNNING, TESTED or QUALIFIED.
    result[c]={'state':state,'release':s['current'],'previous':s['previous'],'source_commit':None if ev is None else ev['source_commit'],'runtime_class':'CONTRACT_ONLY' if c=='prime' else 'INSTALLABLE_BLUEPRINT','runtime_implemented':False,'runtime_state':'UNRESOLVED','qualification_state':'QUALIFIED_LOCAL_ARTIFACT_ONLY' if state=='QUALIFIED' else 'UNTESTED','verification_origin':origin,'running':False,'activated':False,'pending_transactions':[{**j,'recovery_class':self.classify(j)} for j in self.pending(c)]}
   except Exception:result[c]={'state':'BLOCKED','reason':'RELEASE_OR_EVIDENCE_INVALID','running':False}
  return {'environment':self.environment,'state_vocabulary':STATE_VOCABULARY,'components':result}
 def doctor(self):
  o=target_observation();s=self.status();disk=shutil.disk_usage(self.home)
  return {'observation':o,'disk_free':disk.free,'roots':{k:str(v) for k,v in self.roots.items()},'fleet':s,'repair_performed':False,'native_debian13_wsl2_verification':'NOT_YET_ZBOOK_VERIFIED','source_provenance':'RELEASE_INSTALLATION_EVIDENCE; NO_SOURCE_MUTATION','runtime_backend':'NONE_SELECTED'}
 def install_cli(self):
  ev=self.verify_release('systems',self.selection('systems')['current']);path=self.component('systems')/'releases'/ev['release_id']/'tools/local-node/ogx_node.py';safe(path)
  owner=self.roots['config']/'cli-evidence.json'
  if self.cli.exists():
   if not owner.exists() or read(owner)['sha256']!=digest(self.cli.read_bytes()):raise ValueError('unowned_cli')
  self.cli.parent.mkdir(parents=True,exist_ok=True);safe(self.cli)
  content=('#!/bin/sh\nexec python3 -I -B '+str(path)+' "$@"\n').encode()
  # Paths with whitespace/metacharacters must not become shell code.
  import shlex
  content=('#!/bin/sh\nexec python3 -I -B '+shlex.quote(str(path))+' "$@"\n').encode();tmp=self.cli.parent/('.ogx-'+uuid.uuid4().hex)
  with tmp.open('xb') as f:f.write(content);f.flush();os.fsync(f.fileno())
  tmp.chmod(0o700);os.replace(tmp,self.cli);atomic(owner,{'sha256':digest(content),'component':'systems','release_id':ev['release_id']})
def build(node,source,expected,revision=''):
 source=safe(source)
 if not re.fullmatch('[a-f0-9]{40}',expected):raise ValueError('invalid_source_sha')
 head=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
 if head!=expected or subprocess.check_output(['git','-C',str(source),'diff','--name-only','HEAD']):raise ValueError('wrong_source_sha_or_dirty')
 if not node.fixture and node.source not in source.parents and source!=node.source:raise ValueError('source_outside_runner_work')
 tracked=subprocess.check_output(['git','-C',str(source),'ls-tree','-r','--full-tree','HEAD'],text=True).splitlines();tracked_paths=[]
 for line in tracked:
  meta,path=line.split('\t',1);mode,kind,blob=meta.split()
  if kind!='blob' or mode not in ['100644','100755']:raise ValueError('unsupported_source_entry')
  f=safe(source/path);data=f.read_bytes()
  if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=blob:raise ValueError('source_digest_mismatch')
  tracked_paths.append(path)
 node.owned();parent=node.confined(node.roots['cache']/'builds','cache');parent.mkdir(exist_ok=True);out=Path(tempfile.mkdtemp(prefix='build-',dir=parent));sys.path.insert(0,str(source/'foundry'))
 from system_foundry_r2 import generate,load,Sandbox
 for c in COMPONENTS:
  p=out/c;p.mkdir()
  if c=='prime':
   for rel in tracked_paths:
    if rel.startswith('local-node/prime-contracts/'):shutil.copyfile(source/rel,p/Path(rel).name)
  else:
   sb=Sandbox.create(out);g=load(source/'genomes'/(c+'.system-genome.json'));generate(g,'output',sb)
   for f in (sb.root/'output').iterdir():shutil.copyfile(f,p/f.name)
  if c=='systems':
   tools=p/'tools';tools.mkdir()
   for rel in tracked_paths:
    if rel.split('/')[0] in ['vendor','contracts','local-node','foundry']:
     target=tools/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/rel,target)
  desc={'component':c,'runtime_class':'CONTRACT_ONLY' if c=='prime' else 'INSTALLABLE_BLUEPRINT','runtime_implemented':False,'network_binding':None,'external_effect':False,'contract_status':'PROPOSED','source_commit':expected,'revision':revision};(p/'runtime-descriptor.json').write_bytes(encode(desc))
  m={'schema':'OGX_ARTIFACT_MANIFEST_R0','component':c,'source_commit':expected,'files':files(p)};schema(m,'artifact-manifest.schema.json');(p/'manifest.json').write_bytes(encode(m));node.verify_payload(p,c,expected)
 return out
def main(argv=None):
 ap=argparse.ArgumentParser();ap.add_argument('--home');ap.add_argument('--cloud-fixture',action='store_true');ap.add_argument('command',choices=['status','doctor','fleet','verify','release','recovery','install','rollback','resume','prime',*COMPONENTS[1:]]);ap.add_argument('detail',nargs='?',default='status');ap.add_argument('--source');ap.add_argument('--expected-sha');ap.add_argument('--transaction');a=ap.parse_args(argv)
 try:
  n=Node(a.home,a.cloud_fixture)
  if a.command=='install':
   n.initialize();b=build(n,a.source,a.expected_sha)
   result={c:n.install(c,b/c,a.expected_sha) for c in COMPONENTS};n.install_cli();out={'artifact_installations':result,'runtime_installed':False}
  elif a.command=='rollback':out={'rollback':n.rollback(a.detail)}
  elif a.command=='resume':out={'recovery':n.recover(a.transaction,'resume')}
  elif a.command=='recovery' and a.detail in ['resume','rollback']:out={'recovery':n.recover(a.transaction,a.detail)}
  elif a.command=='doctor':out=n.doctor()
  else:
   out=n.status()
   if a.command in COMPONENTS:out=out.get('components',{}).get(a.command,{'state':'BLOCKED'})
   if a.command=='verify':out={'result':'PASS' if all(x['state']=='INSTALLED' for x in out.get('components',{}).values()) and len(out.get('components',{}))==8 else 'BLOCKED','fleet':out}
  print(json.dumps(out,sort_keys=True));return 0
 except Exception as e:print(json.dumps({'state':'BLOCKED','error_class':type(e).__name__,'environment':'CLOUD_TEST_ENVIRONMENT' if a.cloud_fixture else 'OBSERVED_HOST','ZBOOK_INSTALLED':False}));return 20
if __name__=='__main__':raise SystemExit(main())
