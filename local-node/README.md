# OGX Local Foundry Node R0

Permanent Debian 13/WSL2 installation surface for the ZBook.

## Separation
- source: ~/runner-work/*
- installed artifacts: ~/.local/share/ogx
- mutable state/logs/evidence: ~/.local/state/ogx
- CLI: ~/.local/bin/ogx

R0 is local-only (E0). It does not configure providers, deploy, activate production, install secrets, or enable autostart.

## Gate
Run `bash local-node/install-local-node-r0.sh`, then `ogx doctor` and `ogx status`.
