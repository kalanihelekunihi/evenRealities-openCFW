# YHM2710 tracking C root

Current implementation: [ordinary C PMIC tracking status ABI](yhm-track-pure-c-review.md). Scratch-register/frame contracts below are historical.

The application charger tracking routine at `0x355bc` now executes C directly.
It replaces the naked assembly bridge and its separately framed helper in
`r1/src/application/board/native_yhm_system_track.c`. Empty register constraints
retain the observed incoming R2/R3 words, live R4 and returned frame words.
No executable assembly instructions remain in this unit.

REA read the 108-byte code/padding envelope from the locked application ELF;
the saved evidence includes its identity and provider limitations. The native
routine exposes a 16-byte provider frame. The C root preserves partial-byte
updates and upper bytes, ignores the read status, sets bit 1, evaluates each
logging-mode getter separately and returns the full write status. Its outgoing
word addresses and callback mutations remain observable.

The normal Clang product object passes 16,512 paired stock/C cases (33,024
executions), including 9,600 callback-mutation cases. Checks cover provider
arguments, strings, logging encodings, getter short circuiting, stack positions,
live R4-R11, final R2/R3, saved registers, masks and stack restoration. Three
compiled negative controls are rejected: missing bit 1, zeroed upper word and
truncated write status. Strict GCC compilation succeeds, but its 32-byte provider
frame fails the stock 16-byte contract at the first read. GCC behavior is not
qualified.

All 577 R1 units compile and compose without duplicate strong symbols or known
failures. The 576 unrelated objects are unchanged; the superseded helper is the
only removed strong definition. The manifest and imports (164 application,
34 bootloader) are unchanged. Official scoped qualification retains only the
existing four-byte charger initializer tail, with no new exact regions.

The canonical hybrid application retains SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`:
4,035 source-built bytes, 642,125 binary fallback bytes and 248 resource bytes.
These counts include assembly and data elsewhere. The source plan is unchanged.

The [machine-readable review](yhm-track-c-review.json) records source/build hashes,
REA evidence and audits. Probes are in ignored `build/goal-r1-yhm-track-c/`;
the normal R1 report is `build/sources-goal-r1-yhm-track-c-r1/report.json`.
Transport and logging providers are modeled. Physical charger/I2C operation,
interrupts, arbitrary private-frame aliases, faults, concurrency, APSR and other
caller-clobbered registers are outside this proof. Original Arm Compiler 5 is
unavailable. Complete source-only firmware and byte identity remain unproven.

The subsequent [clear-tracking review](yhm-clear-c-review.md) adds the matching native ABI clear path in this unit. Existing setter function bytes and relocations are unchanged; its new four-byte dispatch tail increases total exact source selections to 4,039 bytes.
