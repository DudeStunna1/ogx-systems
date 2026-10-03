# Debian local-node adapter R0

This adapter installs local artifacts, not invented OS runtimes. PRIME is
CONTRACT_ONLY; each of the seven OS components is INSTALLABLE_BLUEPRINT and has
runtime_implemented=false. Historical runtime candidates are not selected.
The eight components have independent transactions and immutable content-addressed
releases. No service, port, DNS, provider or autostart is activated.

Source is ~/runner-work; installation is ~/.local/share/ogx; mutable journal and
evidence are ~/.local/state/ogx; config is ~/.config/ogx; build cache is ~/.cache/ogx;
the CLI file is ~/.local/bin/ogx. All four OGX roots must be absent or carry matching
owner records. Unowned or partially owned roots fail closed; no adoption or cleanup
is attempted. The generic bin directory is reused only for the owned OGX CLI file.
Symlinks, Windows /mnt paths, foreign homes, repository roots and arbitrary output
paths are rejected. There is no recursive deletion. Same-UID hostile concurrency
and physical WSL host power-loss durability are outside the portable test proof.

Per-component paths: components/<component>/releases/<release-id>, current and
previous. `current` is the atomically replaced authoritative JSON record containing
both current and previous IDs. `previous` is a derived pointer view, never a second
authority. A mismatch blocks status; recovery restores the view. This avoids a torn
pair of authoritative pointers. Component transactions are serialized by flock.

PREPARE → BUILD → VERIFY → STAGE → INSTALL_RELEASE → RECORD_EVIDENCE → ATOMIC_SWITCH
→ POST_VERIFY → COMMIT. Journals are persisted before each effect; copied payloads,
release parent directories and atomic journal writes are fsynced. All release bytes
are preserved on failure. Readback classifies COMPLETE, SAFE_TO_RESUME,
SAFE_TO_ROLLBACK or AMBIGUOUS_STOP. Resume before switch verifies the prior state,
aborts the old journal without deleting bytes, then starts a fresh transaction.
Resume after switch revalidates the candidate before committing; rollback requires
verified prior installation evidence. Repeated rollback consumes the previous
pointer and does not oscillate between releases.

INSTALLED requires a complete installation transaction and bound manifest/evidence.
TESTED and QUALIFIED require separate validated reports with matching digest and
release binding; qualification is local-artifact-only. Synthetic test records are
explicitly labeled and refused on native nodes. Runtime remains UNRESOLVED and
running=false because there is no selected executable backend. Files never imply
RUNNING or ACTIVATED. The state vocabulary includes those future observed states.
`doctor` and all status commands are read-only. No repair is inferred from observation.

Native mutation is gated on observed Debian13/WSL2 and the real current HOME.
Cloud tests use explicitly labeled disposable CLOUD_TEST_ENVIRONMENT namespaces,
not a simulated ZBook. Native behavior remains NOT_YET_ZBOOK_VERIFIED.
Production FQDNs and contracts remain PROPOSED; their unresolved bindings do not
block E0 installation of local artifacts.

Future invocation after separate ZBook authorization:

    python3 -I -B local-node/ogx_node.py install --source "$HOME/runner-work/ogx-systems" --expected-sha <qualified-G10-SHA>

Recovery commands: `ogx recovery status`, `ogx recovery resume --transaction <id>`,
`ogx recovery rollback --transaction <id>`, `ogx rollback <component>`.
The installed CLI pins its tooling to the systems release used to install it;
component selection changes do not silently repoint executable tooling.
