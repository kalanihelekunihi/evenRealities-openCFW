# YHM2710 ladder native C provider

The register-pinned implementation below is superseded by the
[ordinary C kernel review](yhm-ladder-kernel-c-review.md). Its historical
private-frame and live-register proof does not describe the current kernel.

`board/native_yhm_ladder.c` supplies the native charger ladder routine at
`0x35508` and its `0x50750` dispatch tail. The new manifest unit and frontier
entries replace the unresolved native routes. The high-level vendor convenience
API has a different signature and aborts its update on read failure; it is not
the native provider.

REA verified the stock code/literals, eight binary32 multipliers and the
compare-based absolute helper. The native path selects the nearest scaled table
entry, keeps the earlier entry on a tie, ignores read status, replaces register
one's upper three bits and returns the selected index regardless of write status.
Its scratch bytes retain existing stack contents until transport writes them.
The C root preserves its 40-byte provider frame, live R4-R6, packed S16-S18 and
final saved registers. Empty compiler constraints retain these ABI observations;
all executed operations in the ladder unit are C.

The normal product object passes 23,872 paired stock/C cases (47,744 executions).
The actual existing C-backed math helper executes in both the dependency chain
and the source fixture. Tests cover 611 floating-point inputs, table points and
tie neighbors, special values and random encodings across 32 FPSCR configurations
(rounding modes, flush-to-zero, default-NaN and sticky flags). They compare all
eight helper operands, FPSCR snapshots, provider stack/arguments, live R4-R11 and
S16-S31, partial and untouched reads, raw errors, scratch words, callback writes,
returns, final registers, stack and interrupt masks.

Four compiled negative controls are rejected: selecting a later tied entry,
initializing scratch, aborting on read errors and substituting an ordinary C
absolute-value comparison. For quiet NaN `0x7fc00001`, that simpler helper loses
the stock invalid-operation flag (`0x30000011` versus `0x30000010`). The pinned
Clang target rejects FENV_ACCESS support, so the existing architectural math
helper remains. Strict GCC compiles the ladder root but moves index/table values
into R4/R6 before the first helper call and changes final FPSCR flags; it remains
unqualified even where the return index agrees.

All 578 R1 units compile and compose without failures or duplicate strong
symbols. All 577 existing objects and import sets are unchanged (164 application,
34 bootloader). Official qualification selects the four-byte dispatch tail;
only that generated selection was added to the canonical source plan. The full
root and its normal final placement remain unqualified.

The locked hybrid application retains SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 4,043 selected source bytes, 642,117 binary fallback bytes and 248 resource
bytes. Counts include assembly and data elsewhere. The normal report is
`build/sources-goal-r1-yhm-ladder-c/report.json`.

[Machine-readable evidence](yhm-ladder-c-review.json) includes REA records,
build hashes, counterexamples and audits. Probes live under ignored
`build/goal-r1-yhm-ladder-c/`. The source table is linked at its authenticated
native address for ABI comparison. Transport is modeled; physical charger and
single-wire timing, arbitrary private-frame aliases, APSR, other caller-clobbered
registers, faults and concurrency remain unproven. Original Arm Compiler 5 is
unavailable. Complete source-only, byte-identical firmware remains incomplete.
