# OGX Systems

OGX Systems — systems engineering, runtime, providers, recovery and qualification.

## R0 application surface

This repository now contains a real static application surface for OGX Systems.

Current bounded state:

- application code: implemented in repository;
- CI: defined;
- GitHub Pages activation workflow: defined and manual;
- public deployment: not verified;
- `ogxsystems.com` DNS/custom-domain binding: not verified;
- runtime qualification: not verified.

## Activation order

1. Merge an approved release candidate.
2. Enable/authorize the Pages deployment environment if required.
3. Run **OGX Systems Pages Activation**.
4. Read back the deployed URL.
5. Bind/verify `ogxsystems.com` through the authorized DNS/provider path.
6. Observe HTTPS and content revision.
7. Record recovery and qualification evidence.

`MERGED != DEPLOYED != DNS_BOUND != OBSERVED != QUALIFIED`.
