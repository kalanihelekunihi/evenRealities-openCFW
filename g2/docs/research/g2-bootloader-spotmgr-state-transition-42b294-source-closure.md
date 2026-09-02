# G2 bootloader SPOT-manager state-transition source closure

The authenticated interval `[0x0042B294,0x0042B69C)` is production-routed
from `runtime_spotmgr_state_transition_42b294.c`. Apple clang 21 and Homebrew
clang 22 reproduce all 1,032 stock bytes after 12 strict provider relocations.
The stock body SHA-256 is
`0393f03222d8b7e8c67ed0e7ffbba640f8030dac259a909ec7dbb20846325c2b`;
the unrelocated body SHA-256 is
`66cef2c5e94a5aefda464abf3c541bbd8103cf62e89ceb076811a6c3199b45a6`.
Its sole caller is `0x0042BD14`; no interior or stored-pointer ingress exists.
The Apollo-main analogue at `0x005A0FC4` matches 996 of 1,032 bytes. Fifteen
literal cells pin rank tables, state records, retained flags, MMIO registers,
and the system-control register.

The service orders transitions through the two authenticated rank tables,
handles equal-state retrim, gates special states 1, 5, 8, 12, 14, 15, and 17,
publishes saved and bounded ten-bit/seven-bit register fields, chooses the
50/200/2,000-unit transition delay, invokes trim/start or wait providers,
manages the wake/interrupt path, and performs reverse-order trim finalization,
restoration, and profile clearing. Portable tests cover equal-state guarding,
forward publish/start and wake/interrupt behavior, forward interpolation/wait,
and reverse restoration/finalization.

The 14,347-byte MIT source has SHA-256
`858dc5a87b78e22b803f987645d573d364b024d354fcb230126f510498e599f0`.
Focused tests, strict dual-toolchain compilation, manifest ownership, provider
conservation, and unsigned complete-image assembly are verified offline. This
admission reduces the exhaustive post-MSPI ledger to zero unresolved executable
spans and zero unresolved executable bytes. Live rank/state tables, retained
SRAM, MMIO, trim and power effects, delay accuracy, interrupts, concurrency,
reset, and cold boot are blocked by unavailable physical evidence. No signing,
flashing, reset, register access, or other hardware operation occurred;
functional completeness is not claimed.
