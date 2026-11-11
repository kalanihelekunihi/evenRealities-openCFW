# R1 SpO2 stream-first scheduler in C

Follow-up: the [timeout callback](spo2-timeout-c-review.md) is now implemented
in C; the sample callback remains native. Dependency/build counts below
describe this scheduler review's earlier snapshot.

`native_spo2_scheduler.c` implements the 384-byte scheduler at `0x4af10` with
ordinary C control flow, timing arithmetic, logging and provider calls. It adds
no RAM or assembly. The [receipt](spo2-scheduler-c-review.json) binds production
source/object hashes, REA bytes, comparisons, rejected defects, qualification
and builds. The [native analysis](spo2-scheduler-native-analysis.md) records
the stock contract.

Initial flags must be zero and mode exactly 1, followed by enabled health,
truthy wear mode and an empty timing-stream slot. Initial conditions are not
rechecked after settings/wear providers change them. An existing timer and
stream slot 0 do not block registration. Nonzero input skips the clock and
labels success `hourly`; zero uses unsigned `3600 - timestamp % 3600` and
`catchup`. Remaining time at or below 150 seconds skips scheduling. Accepted
starts use 120 seconds.

The scheduler registers `spo2` / `timing` with callback `0x4ada1` and arguments
1,1, then publishes the stream late. Only a successful registration creates
the timer (`0x4b235`, 120,000 milliseconds, argument zero), publishing its
result late and potentially overwriting an existing timer without release.
Registration failure logs and returns. Timer failure logs, reads the fresh
stream slot, unregisters it **including zero**, then clears it after the
provider returns. There is no timer-release call or session-buffer clear.

A non-inlined C helper uses a volatile local to obtain a **16-byte frame**
under the production Clang profile. Combined with the **24-byte C caller**, it
preserves stock's 40-byte depth at the existing flag getter. The getter's
eight-byte frame and reader's 64-byte frame place the raw record **112 bytes
below scheduler entry**. Existing getter/reader assembly boundaries remain
unchanged. This caller adds no assembly, but its frame property must be
revalidated after compiler/profile or structural changes. Failed/partial NV
reads consume unwritten bytes, so a narrower frame is not equivalent.

The production object passed **3,584 paired comparisons**, including **768
with the actual C getter and record-reader kernel/boundary**. Full, prefix24,
prefix25, flag-only and absent writes, ignored storage status, four flag bytes
and sixteen poisoned-stack seeds are covered. Record contents and offsets
agree. The C reader kernel adds provider-call depth below the record without
moving it. Additional cases check existing timers, time boundaries/wrap, exact
registration/timer arguments, late publication, zero-handle failure cleanup,
and mutations to stream/timer/mode/flags inside providers. Comparisons cover
provider order/arguments/state, guards, saved integer/FP registers, SP, masks
and FPSCR. Void R0, caller-clobbered registers/APSR and private stack bytes
are excluded. Storage and lower stream/timer/wear/time/logging providers are
modeled; actual physical behavior and concurrency remain outside this proof.

Eleven compiled defects were rejected: late precondition recheck, direct or
too-small flag-helper frame, null cleanup guard, cached cleanup handle,
existing-timer guard, wrong time boundary, early stream clear, wrong duration,
wrong label and wrong registration argument.

All **662 units** compile and both relocatable compositions pass without
duplicate strong symbols. All **661 previous source/object hashes** are
unchanged. Resolving the scheduler exposes sample and timeout callbacks,
leaving **166 application / 34 bootloader imports**. Those two callback bodies
remain native dependencies. No scheduler body qualifies as instruction-exact.
The canonical plan stays at 4,369 source-built bytes, and the fresh hybrid
matches the locked application through executable pull-through. Complete
source-only linking and physical SpO2 scheduling remain unproven.
