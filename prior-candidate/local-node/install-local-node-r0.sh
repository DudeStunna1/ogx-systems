#!/usr/bin/env bash
set -euo pipefail
ROOT="${OGX_HOME:-$HOME/.local/share/ogx}"
STATE="${OGX_STATE_HOME:-$HOME/.local/state/ogx}"
BIN="$HOME/.local/bin"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
test "$(id -u)" -ne 0 || { echo "STOP=DO_NOT_RUN_AS_ROOT"; exit 20; }
grep -q '^VERSION_ID="\?13' /etc/os-release || { echo "STOP=DEBIAN_13_REQUIRED"; exit 21; }
mkdir -p "$ROOT/releases" "$STATE"/{ledger,qualification,recovery,runtime,logs} "$BIN"
for d in systems vault global studios academy shop horizon; do
  mkdir -p "$ROOT/releases/$d-r0"
  cp "$SRC/genomes/$d.system-genome.json" "$ROOT/releases/$d-r0/system-genome.json"
done
install -m 0755 "$SRC/local-node/ogx" "$BIN/ogx"
printf '%s\n' "OGX_LOCAL_NODE_INSTALL=PASS" "ROOT=$ROOT" "STATE=$STATE" "EFFECT_CEILING=E0_LOCAL_ONLY" "PROVIDER_MUTATION=false" "DEPLOYMENT=false" "ACTIVATION=false"

