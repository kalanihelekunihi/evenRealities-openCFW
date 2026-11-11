# R1 HRV sample producer in C with FP instruction boundaries

Latest follow-up: [guarded conversion](hrv-conversion-c-review.md) removes the
last producer assembly after the verified strict GCC comparison. Counts and
compiler findings below describe the original Clang review.

Follow-up: [RMSSD](rmssd-c-review.md) is now implemented in C with a retained
diagnostic conversion boundary. The remaining dependency exposed by that work
is the activity-mode getter. Counts below describe the producer review's build.

`native_hrv_producer.c` replaces the 336-byte producer `0x4a24c` with C ring
handling, gating, event construction, logging and cleanup. It reuses existing
HRV state/buffer ownership and adds no RAM. The [receipt](hrv-producer-c-review.json)
binds production source/object hashes, REA evidence, comparisons, rejected
defects, qualification and normal composition. The preceding
[native analysis](hrv-producer-native-analysis.md) describes the stock contract.

The producer ignores context and length, increments the wrapping 16-bit
callback counter before payload access, and skips payload reads below count
10. It consumes at most four nonzero halfword samples, rereading payload count
byte 9 each iteration and each accepted sample after metadata stores. Head,
used and valid counters retain the stock update order and halfword widths.
The full-ring path deliberately retains the unchecked old head: out-of-range
heads can target metadata or memory outside the 208-byte buffer. This behavior
is tested rather than silently clamped. Evaluation requires fresh callback
count at least 60 and valid count at least 70.

After RMSSD returns, the producer captures timer presence, then applies the
positive-result and fresh wear predicate. A successful result forms an eight-byte
kind-7 event containing the narrowed value, zero padding and a fresh backend
timestamp. Publish failures are ignored. Session teardown always runs, followed
by a fresh timer release and a late flag-byte-1 write only when the captured
timer-presence value was true. Failure logs and uses that captured value to
choose buffer-clear-only versus session teardown. Changes to the shared timer
during later providers do not alter this choice, but release uses its fresh
value through the existing C coordinator.

Two small inline instruction boundaries remain: signaling `VCMPE` plus FPSCR
read, and `VCVT.u32` plus result transfer. Quiet/signaling NaNs must fail while
setting IOC; a compiled ordinary C comparison was rejected specifically because
it lost the quiet-NaN exception flag. Native conversion must also retain
saturation and exception flags for infinity/overflow before halfword narrowing.
The surrounding implementation is C; this is not a claim that all inline
assembly has been removed.

The production object passed **4,608 paired stock/C cases: 4,592 completed
returns and 16 expected payload faults**. An independent live-memory ring oracle
covers counter wrap, full/partial rings, head values 0/99/100/65,535, count
0/1/4/5/255, zero samples, and payload aliases with metadata. FP cases cover
signed zero, finite values, infinities, NaNs, denormals, FZ/DN/rounding modes and
FPSCR. The FP context is architecturally warmed before FPSCR initialization;
first-use FP activation remains outside this proof. Another 144 cases mutate
timer/stream/flags/FPSCR inside modeled providers, checking the captured/fresh
state decisions. Preserved integer/FP registers, SP and masks match. Void R0,
caller-clobbered registers/APSR and private stack bytes are excluded.

The actual C session teardown, memory-clear wrapper/musl memset and timer-release
coordinator execute. RMSSD, wear/time, event publishing, logging, unregister and
lower timer-release behavior are modeled. The fixture observes event contents,
provider calls/state, final SRAM and native FPSCR; the ring oracle also checks
unchecked writes before cleanup can erase them. Ten compiled defects were
rejected: clamped head, cached sample/count, lost callback wrap, fresh rather
than captured timer decision, unconditional failure teardown, wrong completion
flag, short event, wrong log tag and quiet FP compare.

All **656 units** compile and both relocatable compositions pass without
duplicate strong symbols. All **655 prior objects** are unchanged; the scheduler
adopts the newly established producer prototype through the shared header.
Resolving the producer exposes `r1_hrv_rmssd`, leaving **169 application /
34 bootloader imports**. No producer body qualifies as instruction-exact.
The canonical plan remains at 4,369 source-built bytes and the fresh hybrid
matches the locked application through executable pull-through. Complete
source-only linking, RMSSD reconstruction and physical HRV operation remain
unproven.
