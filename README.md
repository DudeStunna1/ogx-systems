# OGX Systems

> **Core Infrastructure Layer for the OGX Empire**  
> Agents · Workflows · Monitoring · Sentinel Workers · Cloud Pipelines

---

## 🏛️ Empire Architecture

```
OGX Systems
├── THARA          — Brand core, highest confidentiality & quality bar
├── OGX Prime      — Flagship product, CEO-track governance
├── OGX            — Standard operations layer
├── OOGX           — Extended OGX operations
├── Cores-OS       — Infrastructure & hardened system layer
└── MiniOS         — Lightweight, compatibility-first sub-system
```

---

## 🤖 THARA Sentinel Intelligence (THARA-SI)

THARA-SI is an autonomous GitHub Actions agent that intercepts every critical repository event, calculates the optimal path using the **Decision Matrix**, and presents a pre-analyzed decision — you approve, it executes.

### How It Works

1. **Every PR, push, or issue** triggers THARA-SI
2. THARA-SI **detects the brand domain** from the branch name or changed files
3. A **structured decision comment** is posted on the PR with required approvals, checks, and next steps
4. You respond with a command — THARA-SI executes

### Quick Commands

| Command | Action |
|---|---|
| `/thara analyze` | Re-run domain analysis on the current PR |
| `/thara approve` or `/approve` | Trigger the auto-execute pipeline for the next step |
| `/thara rollback` | Cancel and notify the responsible team |

---

## 🌿 Branch Strategy

| Branch | Domain | Protection |
|---|---|---|
| `main` | All | 🔴 Critical — 2 approvals, merge queue, signed commits |
| `release/**` | All | 🔴 Critical — 2 approvals, merge queue |
| `hotfix/**` | All | 🔴 Critical — 2 approvals |
| `thara/**` | THARA | 🟡 Standard — 1 approval, build+lint |
| `ogx-prime/**` | OGX Prime | 🟡 Standard — 1 approval |
| `ogx/**` | OGX | 🟡 Standard — 1 approval |
| `oogx/**` | OOGX | 🟡 Standard — 1 approval |
| `cores-os/**` | Cores-OS | 🟡 Standard — 1 approval |
| `minios/**` | MiniOS | 🟢 Low — 1 approval |
| `feature/**` | General | 🟢 Low — 1 approval |

---

## 📁 Repository Structure

```
.github/
├── CODEOWNERS                         — Module ownership by brand domain
├── sentinel/
│   └── decision-matrix.yml            — Brand domain rules, checks, approvals
├── rulesets/
│   ├── critical-branches.json         — Rules for main/release/hotfix
│   └── feature-branches.json          — Rules for all domain branches
└── workflows/
    ├── thara-sentinel.yml             — Domain detection & PR decision comment
    ├── auto-next-step.yml             — Command handler & auto-execute pipeline
    └── governance-checks.yml          — CI: build, lint, quality, secret-scan
docs/
└── governance/
    ├── branch-protection.md           — Full branch strategy documentation
    ├── decision-log.md                — Audit trail of all THARA-SI decisions
    ├── kpi-dashboard.md               — Governance health metrics
    ├── rollout-phases.md              — 3-phase deployment plan
    └── audit/                         — Monthly auto-generated audit logs
```

---

## 🚀 Rollout Status

| Phase | Description | Status |
|---|---|---|
| **Phase 1** | Governance foundation (rulesets, CODEOWNERS, CI) | ✅ Done |
| **Phase 2** | Sentinel active (domain detection, PR decisions, commands) | 🔄 In Progress |
| **Phase 3** | Auto-loop (autonomous low-risk decisions, full AI pipeline) | 📅 Planned |

See [`docs/governance/rollout-phases.md`](docs/governance/rollout-phases.md) for details.

---

## 📊 Governance

- **Decision Matrix**: [`.github/sentinel/decision-matrix.yml`](.github/sentinel/decision-matrix.yml)
- **KPI Dashboard**: [`docs/governance/kpi-dashboard.md`](docs/governance/kpi-dashboard.md)
- **Decision Log**: [`docs/governance/decision-log.md`](docs/governance/decision-log.md)

---

*THARA Sentinel Intelligence · OGX Systems · DIAMONDLY CRAFTED & TAILORED*
