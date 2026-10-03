#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

DOMAINS=(systems vault global studios academy shop horizon)

echo "=== OGX 7 DOMAIN GENOMES R2 ==="
for d in "${DOMAINS[@]}"; do
  G="$ROOT/genomes/$d.system-genome.json"
  test -f "$G"
  python3 "$ROOT/foundry/system_foundry_r1.py" "$G" "$TMP/a-$d"
  python3 "$ROOT/foundry/system_foundry_r1.py" "$G" "$TMP/b-$d"
  diff -ru "$TMP/a-$d" "$TMP/b-$d"
  test "$(sha256sum "$TMP/a-$d/MANIFEST.sha256"|cut -d' ' -f1)" = "$(sha256sum "$TMP/b-$d/MANIFEST.sha256"|cut -d' ' -f1)"
  grep -q '"effect_ceiling": "E0_NO_EXTERNAL_EFFECT"' "$TMP/a-$d/system-passport.json"
  grep -q '"qualification_issued": false' "$TMP/a-$d/qualification-plan.json"
  echo "DOMAIN=$d GENERATION=PASS DETERMINISM=PASS E0=PASS"
done

python3 - "$ROOT" <<'PY'
import json,sys
from pathlib import Path
root=Path(sys.argv[1])
files=sorted((root/"genomes").glob("*.system-genome.json"))
seen={}
for p in files:
    g=json.loads(p.read_text())
    if g["system_ref"] in seen: raise SystemExit("duplicate system_ref")
    seen[g["system_ref"]]=p.name
    if g["effect_classes"] != ["E0_NO_EXTERNAL_EFFECT"]: raise SystemExit("non-E0 genome")
expected={"SYSTEMS.OS","VAULT.OS","GLOBAL.OS","STUDIOS.OS","ACADEMY.OS","SHOP.OS","HORIZON.OS"}
if set(seen)!=expected: raise SystemExit("fleet mismatch")
# high-risk ownership tokens must remain in designated domain
owners={"SECRETS_MODELING":"VAULT.OS","ORDER_MODELING":"SHOP.OS","CREATIVE_PRODUCTION":"STUDIOS.OS","SYSTEM_ENGINEERING":"SYSTEMS.OS","JURISDICTION_MODELING":"GLOBAL.OS","LEARNING_PATHWAYS":"ACADEMY.OS","FEDERATION_DIRECTORY":"HORIZON.OS"}
for p in files:
    g=json.loads(p.read_text())
    for cap in g["capabilities"]:
        if cap in owners and owners[cap]!=g["system_ref"]:
            raise SystemExit("boundary collision:"+cap)
print("FLEET_CARDINALITY=7_PASS")
print("CROSS_DOMAIN_BOUNDARY=PASS")
PY

echo "SEVEN_DOMAIN_GENOMES_R2=PASS"
echo "DOMAIN_REPOSITORY_MUTATION=false"
echo "PROVIDER_MUTATION=false"
echo "DEPLOYMENT=false"
echo "ACTIVATION=false"

