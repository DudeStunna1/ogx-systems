# Installer R2 proposal — portable fixture scope

The executable storage mechanism is intentionally confined to a sandbox owned by
the Foundry test harness. It installs seven **blueprint artifact** trees, not seven
OS runtimes. Its installation evidence names this scope and CLOUD_TEST_ENVIRONMENT.
Generated passports remain UNTESTED and NONE after the fixture installation;
installation and fixture qualification live in separate state records.

Pipeline: inspect input and full file manifests → create a unique staging directory
→ copy → revalidate schemas, identity links and hashes → publish a content-addressed
release → record installation evidence → atomically replace selection.json.
This single record owns current and previous, avoiding torn pairs of symlinks.
Repeat installation of an identical release is idempotent. Existing release bytes
are never overwritten. Upgrade preserves the previous qualified fixture release.
Rollback requires a still-valid qualification record and reverified digests.
Failures retain the current pointer and all earlier release bytes. Staging leftovers
are preserved as evidence; no arbitrary recursive deletion is performed.

The lock excludes concurrent installer/recovery effects in the fixture. Files and
selection records are fsynced; power-loss durability across filesystem types and
WSL host failures is not proven. Threat model excludes hostile same-UID processes.
SHA-256 detects accidental content drift; it is not a signature or principal proof.
Prior qualification records are synthetic test-scenario seeds. The real portable
mechanism qualification is issued separately after the complete suite passes. No autostart or provider adapter is executed.

Target mapping to prepare after target preflight and source selection:
source checkout != ~/.local/share/ogx/releases != ~/.local/state/ogx evidence
!= ~/.config/ogx policy != runtime processes != qualification passports.
The real Debian adapter must adopt an existing healthy node only after identifying
its owner, qualified releases and recovery contract. It must refuse foreign state,
dirty/unexpected refs, public binds, and unsupported runtimes. The legacy installers
are disabled in this proposal. This fixture is not authorization to install ZBook.
