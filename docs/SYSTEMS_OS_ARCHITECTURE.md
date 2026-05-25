# SYSTEMS.OS Architecture

- `worker.js`: HTTP runtime router for SYSTEMS.OS endpoints.
- `services/health-runtime.js`: runtime health signal source.
- `services/system-registry.js`: reads registry JSON data.
- `services/workflow-registry.js`: creates queued workflow receipts.
- `config/systems.yaml` and `data/system_registry.json`: baseline systems configuration data.
