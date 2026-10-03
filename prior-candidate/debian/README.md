# SYSTEMS.OS R0 — Debian 13

This installer creates a local, non-privileged SYSTEMS.OS R0 baseline under the current user's home directory.

It does not deploy, mutate Cloudflare, modify DNS, install credentials, or enable a persistent service.

## Install

```bash
bash debian/install-systemos-r0.sh
~/.local/bin/ogx-systems verify
~/.local/bin/ogx-systems status
```

Default effect ceiling: `E0_NO_EXTERNAL_EFFECT`.

