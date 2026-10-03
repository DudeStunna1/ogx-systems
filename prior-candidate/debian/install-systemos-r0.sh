#!/usr/bin/env bash
set -euo pipefail

echo "=== OGX SYSTEMS.OS R0 Debian preflight ==="
. /etc/os-release
printf 'OS=%s VERSION_ID=%s\n' "$PRETTY_NAME" "$VERSION_ID"
printf 'ARCH=%s\n' "$(uname -m)"
printf 'PYTHON=%s\n' "$(python3 --version 2>&1 || true)"
printf 'GIT=%s\n' "$(git --version 2>&1 || true)"

case "${VERSION_ID:-}" in
  13) ;;
  *) echo "STOP: expected Debian 13; observed ${VERSION_ID:-UNKNOWN}" >&2; exit 20 ;;
esac

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PREFIX="${OGX_SYSTEMS_PREFIX:-$HOME/.local/share/ogx/systems-os}"
BIN_DIR="${OGX_SYSTEMS_BIN:-$HOME/.local/bin}"

mkdir -p "$PREFIX" "$BIN_DIR"
cp "$ROOT/ogx-domain.yaml" "$PREFIX/ogx-domain.yaml"
cp -R "$ROOT/contracts" "$PREFIX/contracts"
cp -R "$ROOT/foundry" "$PREFIX/foundry"

cat > "$BIN_DIR/ogx-systems" <<EOF
#!/usr/bin/env bash
set -euo pipefail
PREFIX="$PREFIX"
case "\${1:-status}" in
  status)
    echo "SYSTEMS_OS=INSTALLED_R0"
    echo "PREFIX=\$PREFIX"
    echo "EFFECT_CEILING=E0_NO_EXTERNAL_EFFECT"
    ;;
  verify)
    test -f "\$PREFIX/ogx-domain.yaml"
    test -f "\$PREFIX/contracts/system-genome.schema.json"
    test -f "\$PREFIX/contracts/system-passport.schema.json"
    test -f "\$PREFIX/foundry/foundry-manifest.yaml"
    echo "SYSTEMS_OS_VERIFY=PASS"
    ;;
  *)
    echo "usage: ogx-systems [status|verify]" >&2
    exit 2
    ;;
esac
EOF
chmod 0755 "$BIN_DIR/ogx-systems"

echo "INSTALLATION=COMPLETE"
echo "PREFIX=$PREFIX"
echo "NEXT=$BIN_DIR/ogx-systems verify"
echo "PROVIDER_MUTATION=false"
echo "DEPLOYMENT=false"
echo "ACTIVATION=false"

