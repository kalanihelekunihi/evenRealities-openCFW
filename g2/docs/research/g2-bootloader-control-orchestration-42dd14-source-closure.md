# G2 bootloader control-orchestration source closure

The non-returning event/control orchestrator at `0x0042DD14..0x0042DD68` and
critical dispatch transaction at `0x0042DE0E..0x0042DE58` are now source-owned
MIT C. The orchestrator has one stored Thumb entry pointer at `0x0042E174`; the
transaction has three bounded direct callers.

Apple clang 21 and Homebrew clang 22 reproduce all 158 authenticated bytes
exactly from mnemonic-only Arm source under thirteen strict call relocations.
Portable tests cover event-status dispatch eligibility and the four-word
transaction copy/dispatch contract. Live scheduler/event, retained RAM,
interrupt-mask, terminal-mode, logging, timing, reset, and cold-boot behavior
is blocked by unavailable physical evidence.
