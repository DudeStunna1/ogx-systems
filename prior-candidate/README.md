# OGX SYSTEMS — SYSTEMS.OS R0

SYSTEMS.OS is the system-factory and runtime-engineering domain governed by OGX PRIME.

R0 establishes:
- `SystemGenome` contract
- `SystemPassport` contract
- `SystemFoundry` manifest
- Debian 13 local installer
- fail-closed E0 baseline

R0 does **not** imply deployment, qualification, production activation, provider authority, or autonomous external effects.

## Debian 13

```bash
git clone https://github.com/DudeStunna1/ogx-systems.git
cd ogx-systems
git switch fidelis/systems-os-r0-foundry
bash debian/install-systemos-r0.sh
~/.local/bin/ogx-systems verify
```

