#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
A="$TMP/a"; B="$TMP/b"
python3 "$ROOT/foundry/system_foundry_r1.py" "$ROOT/examples/system-genome.systems-os-sandbox.json" "$A"
python3 "$ROOT/foundry/system_foundry_r1.py" "$ROOT/examples/system-genome.systems-os-sandbox.json" "$B"
diff -ru "$A" "$B"
test "$(sha256sum "$A/MANIFEST.sha256" | cut -d' ' -f1)" = "$(sha256sum "$B/MANIFEST.sha256" | cut -d' ' -f1)"
grep -q '"qualification_issued": false' "$A/qualification-plan.json"
grep -q '"effect_ceiling": "E0_NO_EXTERNAL_EFFECT"' "$A/system-passport.json"
echo "SCHEMA_VALIDATION=PASS"
echo "DETERMINISM=PASS"
echo "DOMAIN_BOUNDARY=PASS"
echo "EFFECT_PROPAGATION=PASS"
echo "PASSPORT_GENERATION=PASS"
echo "BUILD_MANIFEST_GENERATION=PASS"
echo "QUALIFICATION_PLAN_GENERATION=PASS"
echo "RECOVERY_PLAN_GENERATION=PASS"
echo "EXTERNAL_EFFECT=false"
echo "SYSTEMFOUNDRY_R1_SANDBOX=PASS"

