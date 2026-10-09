# Original-address SCB wrapper source correspondence

All three predeclared wrapper sections link exactly against stock with the
unchanged14.2.1 object: ReadArray30bytes, WriteArray48bytes and
WriteDefaultArray48bytes. Three original BL instructions resolve the one
R_ARM_THM_CALL in each wrapper to its previously exact no-check helper. No
source recompilation, flags, relocation addends or instructions were changed.

The new wrappers total126bytes. The linked image also includes128previously
matched helper bytes as dependencies; these are explicitly marked reused in
`results.json` and cannot be double-counted as new comparison coverage.
Absolute payload coordinates, complete section hashes/equality, original call
bytes/targets, object/linker/script/ELF hashes and actual argv/exit/diagnostics
are recorded. A bounded current scope scan finds no recognized overlap.

The public source correspondence explains the application-facing contracts:
ReadArray clamps requested count to current RX FIFO occupancy before invoking
ReadArrayNoCheck. WriteArray and WriteDefaultArray clamp requested count to
remaining TX FIFO capacity before invoking their no-check helpers. The wrappers
return the selected transferred count; they do not wait for requested count to
be fully available or claim eventual wire delivery. FIFO register inputs remain
hardware-dependent; this source match supplies software interpretation, not a
physical transfer trace. The no-check bodies retain their previously identified
byte/halfword width behavior.

This extends selected-source linkage evidence in the separate SCB translation
unit; it is not a complete PDL/touch build or unique producer identification.
Independent review/admission remain pending. Approved nonprivileged Docker
linking used no network, minimal read-only tool/object mounts and task-only
writable outputs. No production/device/Git/campaign mutation occurred.
