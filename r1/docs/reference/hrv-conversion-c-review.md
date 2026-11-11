# R1 HRV producer conversion in C

The producer at stock `0x4a24c` now contains **no inline assembly**. Its last
unsigned-conversion boundary is expressed in C under the existing pinned GCC 9
strict floating-point profile. The preceding [comparison review](hrv-positive-c-review.md)
remains the evidence for signaling comparison behavior.

Only positive, non-NaN results reach conversion after the comparison and wear
predicate. For positive binary32 encodings below `0x4f800000` (2^32), the unsigned
cast is in range and the compiler emits native truncating conversion. At or
above that boundary, including positive infinity, C returns `UINT32_MAX` and a
volatile zero/zero floating operation raises the stock invalid-operation flag.
This avoids out-of-range C casts. The operation and its FPSCR behavior are
verified for this compiler/target; this is not a portable exception-handling
claim for arbitrary C implementations. The result is then narrowed to the event
halfword exactly as before. No state, provider or import is added.

The [receipt](hrv-conversion-c-review.json) binds REA bytes to the locked raw
application, production source/object hashes and replay artifacts. **8,944 paired
stock/C cases** pass, including **16 expected payload faults**. The original
4,608 callback cases are supplemented with 4,336 conversion cases covering
positive bit-pattern samples, subnormals, integer and overflow boundaries, all
rounding/FZ/DN combinations, sticky flags and FPSCR changes by the time provider.
Checks compare event contents, provider traces, SRAM, preserved registers, masks
and FPSCR. The private stack, caller-clobbered APSR/registers and void R0 are
excluded. Actual C cleanup/clear/coordinator execute; RMSSD and external event,
wear/time/log/unregister/lower timer providers remain modeled.

Thirteen compiled negative controls are rejected: the preceding ten callback
and quiet-comparison defects plus missing invalid-operation flag, incorrect
saturation and a premature overflow threshold. Every control must compile before
its behavioral mismatch counts.

All **672 units** compile with no duplicate strong symbols. The other **671
source/object pairs**, manifest and import sets are unchanged: **163 application /
34 bootloader** unresolved symbols. The qualifier rejects the producer's anchored
relocation pattern. The canonical plan remains **4,369 source-built bytes**, and
the fresh hybrid matches the locked application using executable pull-through.
No full source-only link, new instruction-qualified bytes, first-use FP activation
or physical hardware operation is established. RMSSD retains its separate
conversion assembly boundary.
