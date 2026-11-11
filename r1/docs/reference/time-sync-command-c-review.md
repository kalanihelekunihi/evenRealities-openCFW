# R1 time-sync command source replay

The C owner `r1/src/application/runtime/native_time_sync_command.c` supplies
the stock `0x846dc` command. It cancels the pending timeout, reads the packet's
six-byte time payload, forms and publishes a twelve-byte event, sends the
acknowledgements, selects the NV recovery path, and emits the selected logs.
The existing source comment labels its lower private-frame and recovery
admission as separate gates; this replay covers its outer control flow only.

The ignored Cortex-M4 replay at
`build/r1-time-sync-command-replay-20261111/report.json` compares 256 paired
stock/source executions: missing or present payload, both recovery branches,
all eight log-mode masks and eight input seeds. The modeled providers return
the same seeded values to both implementations. The ordered provider calls,
arguments, published twelve-byte event, selected log strings and final R0
match in every case. Both executions restore SP and R4–R11. The replay does
not execute the delayed timer, packet decoder, clock, recovery services,
logger or BLE senders; it does not compare the private stack scratch bytes.

The receipt binds stock SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
and current source ELF SHA-256
`4b640ceffbf99a3102515d7138cadf74412bdd68e7ea67e18d4ce560b0377750`.
The strict application and bootloader links at
`build/r1-link-event-dispatch-ordered-20261111/report.json` and
`build/r1-boot-link-event-dispatch-ordered-20261111/report.json` pass without
undefined symbols or retained stock executable code in those regions. This
is bounded behavior evidence, not hardware execution or whole-device
C-source coverage.
