# R1 SpO2 timeout stream cleanup in C

`native_spo2_timeout.c` implements the 92-byte timeout callback at `0x4b234`
in ordinary C. The [receipt](spo2-timeout-c-review.json) binds REA bytes,
production hashes, direct and timer-chain comparisons, rejected defects,
qualification and builds. Existing SpO2 state and handles are reused; no RAM
or assembly is added. The scheduler now uses the recovered callback prototype.

The callback preserves its incoming timer argument across fresh mode queries
and stock timeout logging. It then reads **timing-stream slot 1 fresh**,
unregisters a nonzero handle with topic `spo2`, and clears that slot after the
provider returns. Slot 0 is preserved. It always releases the **captured timer
argument**, without substituting the shared timer or adding a null guard.
Only after release returns does it clear the shared timer and write flag byte
2 to **1**, in that order. The existing timer-expiry caller discards callback R0.

Validation passed **6,912 direct paired cases** and **3,840 cases running the
actual C timer-release, list-unlink and list-accessor implementations**. Cases
cover mismatched shared/incoming timers, changing log modes, provider errors,
stream/timer/flag changes during logging/unregister/release/free, and single,
head, tail and middle list removals. Comparisons include provider order,
arguments and state, scalar write widths/order, guarded state/streams/list/
nodes, saved integer/FP registers, SP, masks and FPSCR on completed returns.
Void R0, caller-clobbered registers/APSR and private stack bytes are excluded.

**768 integrated null-argument cases** execute the real lower guard: stock
and C both set BASEPRI to 64 and fault on the invalid zero-store at
`0xffffffff`, after stream cleanup but before the callback's final timer clear
and flag write. These are matched fault cases, not completed returns. Direct
cases model a returning release provider, including for invalid arguments;
they do not assert that such calls return with a physical timer implementation.
Unregister/free/logging providers remain modeled.

Ten compiled defects were rejected: shared timer instead of argument, skipping
null release, wrong stream slot, early stream/timer clears, early flag write,
omitted unregister, wrong completion flag, wrong ring tag and wrong topic.

All **663 units** compile and both relocatable compositions pass without
duplicate strong symbols. All **662 previous objects** are unchanged; the
scheduler source only adopts the timeout prototype through the shared header.
Resolving the timeout adds no imports, leaving **165 application / 34 bootloader
imports**. The subsequent [sample review](spo2-sample-c-review.md) supplies its C implementation. No timeout body qualifies
as instruction-exact. The canonical plan stays at 4,369 source-built bytes,
and the fresh hybrid application matches the locked artifact through executable
pull-through. Complete source-only linking, physical timer/stream behavior
and concurrency remain unproven.
