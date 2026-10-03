#!/usr/bin/env bash
# Run in a child process. No unconditional PASS strings.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"${OGX_PYTHON:-python3}" "$ROOT/tests/test_repair.py"
