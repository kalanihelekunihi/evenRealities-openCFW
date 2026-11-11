# Low-battery direct-C boundary counterexamples

The bridge in `board/native_battery_low.c` remains unchanged. Direct-C probes
can generate a 16-byte frame and the count-nine tail call with original SP/LR,
but none of the tested layouts passes the full existing access-order oracle.

Normal `-Os` and `-O2` read the voltage before writing the ring count to the
outgoing saved-word slot; stock performs those accesses in the opposite order.
`-Oz` duplicates the two initial scratch-word stores. `-Og` enters the first
mode provider with 32 bytes; explicitly storing the count before the C call
adds a callee register and uses 24 bytes, versus native 16.

A separate no-ring subset passes 477 stock/C comparisons, including provider
frames, live registers, scratch accesses and event-tail SP/LR. This narrower
result does not establish full admission. The stricter complete oracle remains
in force and the assembly bridge is retained.

[Machine-readable evidence](low-battery-c-boundary-review.json) records REA's
300-byte native envelope, compiled candidates and first counterexamples. Probes
are under ignored `build/goal-r1-low-root-c/`. Providers are modeled; physical
low-battery response and complete firmware byte identity remain unproven.
