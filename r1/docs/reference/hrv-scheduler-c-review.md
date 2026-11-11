# R1 HRV timer and stream scheduler in C

Follow-up: the [timeout callback](hrv-timeout-c-review.md) is now implemented
in C; the producer remains native. Counts below describe this scheduler
review's earlier build.

`native_hrv_scheduler.c` implements the 382-byte scheduler at `0x49f0c`
with ordinary C control flow, timing arithmetic, logging and provider calls.
It adds no assembly or RAM. The [receipt](hrv-scheduler-c-review.json) binds
production source/object hashes, REA bytes, replay, rejected defects, qualification
and the normal build. The preceding [native analysis](hrv-scheduler-native-analysis.md)
establishes the stock contract.

Initial flags must both be zero and mode must equal 1. The health flag, wear
mode, timer and stream are then checked in stock order. A nonzero argument
skips the local clock and labels success `hourly`; zero input uses unsigned
`3600 - timestamp % 3600` and labels success `catchup`. At or below 150 seconds
remaining it returns. Accepted starts create a 120,000 millisecond timer,
publish it late, clear the 208-byte session buffer and register `hrv` / `algo`
with the stock producer and arguments 1,1, then publish the stream late.
Failed registration logs before releasing the freshly read timer. Provider
mutations to fields are preserved according to these publication/reload points.

The first direct C caller compiled with a 24-byte frame, shifting the existing
settings reader's raw record from entry-SP minus 104 to minus 96. Failed and
partial NV reads consume unwritten bytes, so that shift cannot be accepted.
The production version calls a non-inlined C boolean helper with an eight-byte
frame: caller24 + helper8 + existing getter8 + existing reader64 restores the
stock **104-byte record offset**. No assembly was added to achieve this.
The existing saved-word getter and raw-record reader retain their assembly
boundaries. This is a verified property of the current Clang production profile;
it must be rechecked when compiler/profile or caller structure changes.

The production object passed **2,208 paired stock/C cases**, including **640
with the actual C flag getter and record-reader kernel/boundary**, full/prefix24/
prefix25/flag-only/absent NV writes, both storage statuses, four flag bytes and
sixteen poisoned-stack seeds. Complete raw record contents and offsets agree.
The C reader kernel adds provider-call depth below the record without moving it.
Additional cases cover initial guards, existing handles, zero/full-word input,
hour boundaries and timestamp wrap, allocation/registration failures, changing
log modes and provider changes to initial mode/flags and timer/stream fields.
The actual C timer-release coordinator executes in failure paths. Comparisons
include call order and arguments, state/buffer contents before and after each
modeled provider, final SRAM and guards, saved integer registers, SP, interrupt
masks and FPSCR. Void R0, caller-clobbered registers/APSR and private stack bytes
are excluded. Lower providers and hardware are modeled.

Eight compiled defects were rejected: wrong caller frame, wrong time boundary,
duration, success label, buffer-clear length, omitted release, early timer
publication, and wrong producer argument. Testing early publication required
observing state at provider boundaries; final state alone does not expose it.

All **654 units** compile and both relocatable compositions pass without
duplicate strong symbols. All **653 prior objects** are unchanged; the existing
HRV timing source only adopts the shared state header. Resolving the scheduler
exposes its timeout `0x49e5c` and producer `0x4a24c`, leaving **170 application /
34 bootloader imports**. Those callbacks remain native dependencies. The
scheduler has no exact-qualified body under the tested production bindings.
The canonical plan remains at 4,369 source-built bytes; the fresh hybrid still
matches the locked application using executable pull-through. Complete source-only
linking, full HRV operation and physical/concurrent execution remain unproven.
