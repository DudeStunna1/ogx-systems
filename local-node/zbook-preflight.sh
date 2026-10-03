#!/usr/bin/env bash
# Entire command is a subshell. Shell RC never substitutes for JSON result.
(
  preflight_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
  python3 -I -B - "$preflight_dir/expected-refs.json" "${1:-$HOME/runner-work}" <<'PY'
import json,os,pathlib,platform,re,shutil,subprocess,sys
out={'schema':'OGX_ZBOOK_PREFLIGHT_R0','result':'BLOCKED','read_only':True,'ZBOOK_INSTALLED':False,'ZBOOK_QUALIFIED':False,'PROVIDER_MUTATION':False,'observations':{},'blockers':[]}
try:
 data={}
 for line in pathlib.Path('/etc/os-release').read_text().splitlines():
  if '=' in line:k,v=line.split('=',1);data[k]=v.strip('"')
 out['observations'].update(os=data.get('ID'),version=data.get('VERSION_ID'),architecture=platform.machine(),kernel=platform.release(),python=platform.python_version(),disk_free=shutil.disk_usage(pathlib.Path.home()).free)
 out['observations']['memory']=dict(line.split(':',1) for line in pathlib.Path('/proc/meminfo').read_text().splitlines() if line.startswith(('MemTotal:','MemAvailable:')))
 if data.get('ID')!='debian' or data.get('VERSION_ID')!='13':out['blockers'].append('DEBIAN13_NOT_OBSERVED')
 if not re.search(r'microsoft.*wsl2|wsl2.*microsoft',platform.release(),re.I):out['blockers'].append('WSL2_NOT_OBSERVED')
 expected=json.loads(pathlib.Path(sys.argv[1]).read_text());parent=pathlib.Path(sys.argv[2]);refs=[]
 env={**os.environ,'GIT_OPTIONAL_LOCKS':'0','GIT_TERMINAL_PROMPT':'0'}
 for row in expected:
  p=parent/row['repository'].split('/')[-1];entry={'repository':row['repository'],'expected_sha':row['sha'],'observed_sha':None,'clean':False}
  if any(x.is_symlink() for x in [p,*p.parents]):out['blockers'].append('SOURCE_SYMLINK');refs.append(entry);continue
  def git(*args):return subprocess.check_output(['git','--no-optional-locks','-c','core.fsmonitor=false','-c','core.hooksPath=/dev/null','-C',str(p),*args],env=env,text=True,stderr=subprocess.DEVNULL,timeout=10).strip()
  try:
   entry['observed_sha']=git('rev-parse','HEAD');entry['clean']=not git('status','--porcelain=v1');origin=git('config','--get','remote.origin.url');entry['repository_matches']=bool(re.search(r'(?:github.com[:/]|git.chatgpt-team.site/)(?:'+re.escape(row['repository'])+r')(?:\.git)?$',origin))
   if entry['observed_sha']!=row['sha'] or not entry['clean'] or not entry['repository_matches']:out['blockers'].append('SOURCE_REF_OR_WORKTREE_BLOCKED:'+row['repository'])
  except Exception:out['blockers'].append('SOURCE_UNOBSERVED:'+row['repository'])
  refs.append(entry)
 out['observations']['repositories']=refs;roots={}
 for role,relative in [('INSTALL','.local/share/ogx'),('STATE','.local/state/ogx'),('CONFIG','.config/ogx'),('CACHE','.cache/ogx')]:
  p=pathlib.Path.home()/relative;roots[role]={'exists':p.exists(),'owner_marker_present':(p/'.ogx-owner.json').is_file(),'symlink':any(x.is_symlink() for x in [p,*p.parents])}
  if roots[role]['symlink'] or (roots[role]['exists'] and not roots[role]['owner_marker_present']):out['blockers'].append('UNOWNED_OR_SYMLINK_ROOT:'+role)
 out['observations']['roots']=roots;out['observations']['resource_sufficiency']='UNRESOLVED_RUNTIME_REQUIREMENTS';out['result']='PASS' if not out['blockers'] else 'BLOCKED'
except Exception as e:out['blockers'].append('OBSERVATION_ERROR:'+type(e).__name__)
print(json.dumps(out,sort_keys=True))
PY
) || true
