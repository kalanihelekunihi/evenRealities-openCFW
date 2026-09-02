# G2 bootloader DFU service-task source closure

The authenticated interval `[0x0042DE58,0x0042E104)` is production-routed
from `runtime_dfu_service_task_42de58.c`. Apple clang 21 and Homebrew clang 22
reproduce all 684 stock bytes after 29 strict provider relocations. The stock
body SHA-256 is
`52e1f7a3ed50f4a8167463ae705cccee6ac690db1de524927a2eca9eb424557f`;
the unrelocated body SHA-256 is
`759dc2f405b33a3e61e91d43484cc390e102b717c3e6a7c7d4729f1705b112b8`.
Its sole direct caller is `0x0042E1CC`; no interior or stored-pointer ingress
exists. Twenty authenticated literal cells pin the retained queue, file,
header, logging, image-base, and runtime-state references.

The task clears its queue record, waits for a command, selects stream mode,
opens and reads the 32-byte image header, closes the file on every terminal
read path, reports header fields, invokes the source-routed image CRC and
payload programmer, normalizes the active vector base to `0x00438000`, checks
the SRAM-stack-vector predicate, disables the runtime, and transfers through
the retained vector-handoff provider. The alternate command path validates
the published vector pointer before the same guarded handoff. Portable tests
cover successful CRC/program/handoff, open and read failures, alternate-vector
handoff, receive termination, loop continuation, and source reviewability.

The 7,096-byte MIT source has SHA-256
`2b34b8873824bbb361e4886933c7fc98781c150362c2fdf11c2072487d8bb3a4`.
Focused tests, strict dual-toolchain compilation, manifest ownership, provider
conservation, and unsigned complete-image assembly are verified offline. Live
queue/scheduler behavior, filesystem and storage reads, CRC/programming against
flash, vector-table validity, interrupt state, handoff, reset, and cold boot
are blocked by unavailable physical evidence. No signing, flashing, reset,
vector transfer, register access, or other hardware operation occurred;
functional completeness is not claimed.
