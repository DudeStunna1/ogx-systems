# Branch Protection Strategy — OGX Systems

> THARA Sentinel Intelligence · Governance Layer v1.0

## Branch Strategy by Domain

| Branch Pattern | Domain | Ruleset | Approvals | Merge Queue |
|---|---|---|---|---|
| `main` | All | critical | 2 | ✅ |
| `release/**` | All | critical | 2 | ✅ |
| `hotfix/**` | All | critical | 2 | ✅ |
| `develop` | All | feature | 1 | ❌ |
| `thara/**` | THARA | feature | 1 | ❌ |
| `ogx-prime/**` | OGX Prime | feature | 1 | ❌ |
| `ogx/**` | OGX | feature | 1 | ❌ |
| `oogx/**` | OOGX | feature | 1 | ❌ |
| `cores-os/**` | Cores-OS | feature | 1 | ❌ |
| `minios/**` | MiniOS | feature | 1 | ❌ |
| `feature/**` | General | feature | 1 | ❌ |

---

## Critical Branches Ruleset

Applied to: `main`, `release/**`, `hotfix/**`

- **Pull Request required** — no direct push
- **2 approvals minimum** — at least one must be a code owner
- **Stale reviews dismissed** on new push
- **Required status checks** (must pass before merge):
  - `build`
  - `test`
  - `quality`
  - `secret-scan`
  - `dependency-review`
- **Linear history** enforced (no merge commits)
- **Signed commits** required
- **Merge queue** enabled (squash merge)
- **Force push** disabled
- **Branch deletion** disabled

---

## Feature Branches Ruleset

Applied to: `develop`, `feature/**`, `thara/**`, `ogx/**`, `oogx/**`, `ogx-prime/**`, `cores-os/**`, `minios/**`

- **Pull Request required**
- **1 approval minimum** — code owner review required
- **Required status checks**:
  - `build`
  - `lint`
- **Linear history** enforced
- **Force push** disabled
- **Branch deletion** disabled

---

## Domain-Specific Requirements

### THARA (`thara/**`)
- 2 approvals from `@THARA-leads`
- Checks: `build`, `test`, `quality`, `secret-scan`, `e2e`
- Max review delay: 48h

### OGX Prime (`ogx-prime/**`)
- 2 approvals from `@OGX-prime-core`
- Checks: `build`, `test`, `quality`, `performance-benchmark`, `dependency-review`
- Max review delay: 24h

### Cores-OS (`cores-os/**`)
- 2 approvals from `@infra-team`
- Checks: `build`, `test`, `hardening-scan`, `dependency-review`, `secret-scan`
- Max review delay: 24h

### OGX / OOGX (`ogx/**`, `oogx/**`)
- 1 approval from `@OGX-prime-core`
- Checks: `build`, `test`, `quality`
- Max review delay: 72h

### MiniOS (`minios/**`)
- 1 approval from `@minios-team`
- Checks: `build`, `compatibility-matrix`
- Max review delay: 96h

---

## Break-Glass Procedure

In case of emergency requiring a bypass of branch protection:

1. Contact repository admin (`@DudeStunna1`)
2. Document reason in `docs/governance/audit/` with timestamp
3. Bypass actor: `RepositoryRole:Admin` (actor_id: 5)
4. Post-incident: create issue tagged `incident:break-glass` with full RCA

---

## CODEOWNERS Summary

| Path | Owners |
|---|---|
| `*` (fallback) | `@DudeStunna1` |
| `/thara/` | `@DudeStunna1` `@THARA-leads` |
| `/ogx-prime/` | `@DudeStunna1` `@OGX-prime-core` |
| `/ogx/` | `@DudeStunna1` `@OGX-prime-core` |
| `/oogx/` | `@DudeStunna1` `@OGX-prime-core` |
| `/cores-os/` | `@DudeStunna1` `@infra-team` |
| `/minios/` | `@DudeStunna1` `@minios-team` |
| `/.github/` | `@DudeStunna1` |
| `/docs/governance/` | `@DudeStunna1` |
