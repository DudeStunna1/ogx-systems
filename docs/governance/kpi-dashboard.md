# KPI Dashboard — THARA Sentinel Intelligence

> Governance health metrics for the OGX Systems empire.
> Updated automatically by daily audit sweep (`.github/workflows/thara-sentinel.yml`).

---

## Core KPIs

| Metric | Target | Current | Status |
|---|---|---|---|
| Average PR review time | < 24h (critical), < 72h (standard) | — | 🔄 Collecting |
| Approval rate (first pass) | > 80% | — | 🔄 Collecting |
| Blocked PRs (> max delay) | 0 | — | 🔄 Collecting |
| Secret scan alerts | 0 | 0 | ✅ |
| Governance files coverage | 100% | 100% | ✅ |
| Auto-execute success rate | > 95% | — | 🔄 Collecting |

---

## Domain Health

| Domain | Open PRs | Avg Age | Last Merge | Owners Active |
|---|---|---|---|---|
| THARA | — | — | — | — |
| OGX Prime | — | — | — | — |
| OGX | — | — | — | — |
| OOGX | — | — | — | — |
| Cores-OS | — | — | — | — |
| MiniOS | — | — | — | — |

---

## Rollout Phase Progress

| Phase | Status | Completion |
|---|---|---|
| Phase 1 — Governance | ✅ Done | 2026-05-18 |
| Phase 2 — Sentinel Active | 🔄 In Progress | — |
| Phase 3 — Auto-Loop | 📅 Planned | — |

---

## Definitions

- **Blocked PR**: A PR that has not received required approvals or failed required checks beyond its domain's `max_delay_hours`
- **First-pass approval rate**: PRs approved without requesting changes on first review cycle
- **Auto-execute success**: Auto-execute pipeline runs that completed without manual intervention

---

*Maintained by THARA Sentinel Intelligence · OGX Systems*
