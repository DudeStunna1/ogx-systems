#!/usr/bin/env bash
# Legacy unsafe installer disabled in the repair proposal.
printf '%s\n' 'INSTALLER=STOP' 'REASON=REPAIR_QUALIFICATION_GATE_FAILED' 'ZBOOK_INSTALLED=false' >&2
exit 20
