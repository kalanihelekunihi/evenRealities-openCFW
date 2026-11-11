# R1 HRV timeout cleanup callback in C

Follow-up: the [producer](hrv-producer-c-review.md) is now implemented in C with
two FP instruction boundaries; RMSSD remains native. Counts and producer status
below describe the timeout review's earlier build.

`native_hrv_timeout.c` implements the 82-byte callback at `0x49e5c` in
ordinary C, reusing the existing HRV state and session buffer. The
[receipt](hrv-timeout-c-review.json) binds REA bytes, production hashes,
direct and integrated replay, rejected defects, qualification and builds.
There is no new RAM or assembly.

The callback captures its incoming timer argument, queries fresh log modes
and emits the stock ring/SDK timeout messages. It then calls the actual C
session teardown, releases the **captured argument** regardless of the shared
timer field, clears that shared field after the release returns, and finally
writes flag byte 2 to **1**. It does not add a null guard. Changes made by
logging or cleanup providers therefore cannot substitute another timer for
the original argument. Changes to the shared timer during release are cleared
late. The timer-expiry caller at `0x8a434` ignores callback R0, setting its own
fired result immediately after the indirect call; the C expiry implementation
also discards that result.

Validation passed **6,912 direct paired cases** and **3,840 actual timer-chain
cases**. Every case executes the C session teardown, EABI memory-clear wrapper
and musl memset. Integration additionally executes the actual C timer release,
list unlink and list accessors, with single/head/tail/middle removal and
free-provider mutations. Models cover fresh logging queries, changing shared
state during logging/unregister/release/free, mismatched shared and incoming
timers, provider return failures and interrupt-mask states. Comparisons include
call order/arguments, public state, buffer/list/node contents with guards,
write widths and values, SP, saved integer/FP registers, masks and FPSCR.
Void R0, caller-clobbered registers/APSR and private stack bytes are excluded.

**768 integrated null-argument cases** execute the lower timer-release guard.
Stock and C both set BASEPRI to 64 and fault on the invalid zero-store at
`0xffffffff`, after session teardown but before the callback's final timer
clear/flag write. These are matched fault cases, not completed returns. Direct
tests model a returning release provider, including for invalid arguments;
physical allocator/unregister/logging behavior and concurrency remain unproven.

Eight compiled defects were rejected: releasing the shared timer instead of
the argument, skipping null release, clearing the timer early, writing the
completion flag early, omitting session cleanup, wrong ring/SDK tags, and a
wrong completion flag value.

All **655 units** compile and both relocatable compositions pass without
duplicate strong symbols. All **654 previous source/object hashes** are
unchanged. The timeout import resolves with no new imports, leaving **169
application / 34 bootloader imports**. The HRV producer `0x4a24c` remains native.
The timeout does not qualify as instruction-exact under production bindings.
The source plan stays unchanged at 4,369 source-built bytes, and the fresh
hybrid still matches the locked artifact using executable pull-through.
Complete source-only linking and physical HRV operation remain unproven.
