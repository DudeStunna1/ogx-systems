#!/usr/bin/env python3
import argparse, hashlib, json, re, shutil, sys
from pathlib import Path

EFFECTS={"E0_NO_EXTERNAL_EFFECT","E1_REPOSITORY_ONLY","E2_PROVIDER_CONFIGURATION","E3_RUNTIME_STATE","E4_PRODUCTION_EFFECT"}
FORBIDDEN_KEY=re.compile(r"^(secret|password|token|api[_-]?key|credential)(s)?$",re.I)

def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def validate(g):
    req=["system_ref","domain_ref","capabilities","interfaces","runtime_profiles","effect_classes"]
    missing=[k for k in req if k not in g]
    if missing: raise ValueError("missing:"+",".join(missing))
    for k in req:
        if not isinstance(g[k], (str if k in ("system_ref","domain_ref") else list)):
            raise ValueError("invalid_type:"+k)
    bad=[x for x in g["effect_classes"] if x not in EFFECTS]
    if bad: raise ValueError("invalid_effect:"+",".join(bad))
    if any(x!="E0_NO_EXTERNAL_EFFECT" for x in g["effect_classes"]):
        raise ValueError("R1_SANDBOX_REQUIRES_E0")
    raw=json.dumps(g,sort_keys=True)
    if FORBIDDEN.search(raw): raise ValueError("credential_like_material_forbidden")

def canonical(obj):
    return json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False)+"\n"

def write(root, rel, data):
    p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(data,encoding="utf-8")

def generate(g,out):
    validate(g)
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    genome_hash=hashlib.sha256(canonical(g).encode()).hexdigest()
    passport={"schema":"OGX_SYSTEM_PASSPORT_R0","system_ref":g["system_ref"],"genome_ref":"sha256:"+genome_hash,"version":"0.1.0","qualification_state":"UNTESTED","authority_state":"NONE","recovery_state":"DOCUMENTED","effect_ceiling":"E0_NO_EXTERNAL_EFFECT","evidence_refs":[]}
    build={"schema":"OGX_BUILD_MANIFEST_R0","system_ref":g["system_ref"],"source_genome":"sha256:"+genome_hash,"generator":"OGX_SYSTEM_FOUNDRY_R1","external_effects":False}
    qualification={"schema":"OGX_QUALIFICATION_PLAN_R0","gates":["SCHEMA_VALID","DETERMINISTIC_OUTPUT","DOMAIN_BOUNDARY_ENFORCED","EFFECT_CEILING_E0","RECOVERY_DEFINED"],"qualification_issued":False}
    recovery={"schema":"OGX_RECOVERY_PLAN_R0","strategy":"DELETE_GENERATED_SANDBOX_ONLY","provider_rollback_required":False,"persistent_external_state":False}
    write(out,"system-genome.json",canonical(g)); write(out,"system-passport.json",canonical(passport))
    write(out,"build-manifest.json",canonical(build)); write(out,"qualification-plan.json",canonical(qualification)); write(out,"recovery-plan.json",canonical(recovery))
    hashes={}
    for p in sorted(out.glob("*.json")): hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    write(out,"MANIFEST.sha256",canonical(hashes))
    return hashlib.sha256(canonical(hashes).encode()).hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("genome"); ap.add_argument("output"); a=ap.parse_args()
    try:
        h=generate(load(a.genome),Path(a.output))
        print("SYSTEMFOUNDRY_R1=PASS"); print("OUTPUT_DIGEST="+h); print("EFFECT_CEILING=E0_NO_EXTERNAL_EFFECT")
    except Exception as e:
        print("SYSTEMFOUNDRY_R1=STOP",file=sys.stderr); print("REASON="+str(e),file=sys.stderr); return 20
    return 0
if __name__=="__main__": raise SystemExit(main())
