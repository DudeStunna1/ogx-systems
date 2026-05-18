# OGX Systems Architecture

## Goal

Create a repository that supports both the public image of OGX Systems and the future operational layers behind it.

## Current implementation

- `apps/web` delivers the first premium public-facing surface
- root scripts proxy development commands into the web app
- the repository now has documentation that describes the intended platform direction

## Target platform layers

### 1. Brand surface

- landing page
- corporate narrative
- positioning and trust content
- acquisition pathways

### 2. Control layer

- admin views
- dashboards
- workflow control panels
- status and monitoring surfaces

### 3. Automation layer

- agent orchestration
- event-driven workflows
- execution queues
- internal command surfaces

### 4. Trust layer

- documentation
- release discipline
- security conventions
- observability and audit posture

## Recommended repository evolution

### Near term

- keep the public experience in `apps/web`
- add more branded sections and case-study style proof points
- establish deployment and preview workflows

### Mid term

- introduce `apps/portal` for internal operations
- extract shared brand tokens and UI primitives into packages
- formalize environment configuration and release standards

### Long term

- add real data integrations
- connect workflow execution modules
- expose health, governance, and metrics surfaces
