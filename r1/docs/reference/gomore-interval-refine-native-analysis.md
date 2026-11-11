# R1 interval refinement: native signed and FP contract

REA identifies the complete 200-byte routine at `0x58b70`. The native seven
arguments are output, unused context, previous interval, current interval,
aggregation, policy and unused timezone. The existing portable boolean API
has a different signature and behavioral assumptions. The frontier now records
an unresolved native route. The [receipt](gomore-interval-refine-native-analysis.json)
binds REA code/literals, the native replay, independent checks and production
hashes.

The routine first moves all 32 current bytes to its private snapshot. After
the movement returns, it reads flag bit 3 from the **live current input**, not
the snapshot. Without that bit it publishes the snapshot unchanged. Thus
changes to the movement source or destination can affect different parts of
the operation. There are no null guards.

With current bit 3 set, it loads live current end, previous start, current
start and previous end, in that order. Their wrapping differences are span
and gap. It reads aggregation word 8 as a signed count. Nonzero count causes
signed binary32 conversions of aggregation word 20 and count, followed by
division; zero count loads positive zero without reading the numerator.
This calculation precedes the previous-flag, span and policy rejection tests.
It can therefore set FPSCR inexact even when its numerical result will not
influence the chosen status.

The native status sequence is:

1. Previous flag bit 3 absent: status 2.
2. **Signed** wrapped span greater than 43,200: status 1.
3. **Signed** wrapped gap greater than signed policy halfword 2 times 60:
   status 3.
4. Signed count at least 1,800, the ratio's signed raw binary32 word greater
   than `0x3ea3d70a`, and signed gap greater than 1,800: status 5.
5. Otherwise copy the captured previous start to snapshot word 0, set flag
   bit 4 when signed span is at least 10,800, and set status 0.

The status byte is 29 and flag byte is 26. Other snapshot fields survive.
Large wrapped spans with their sign bit set do not pass the positive duration
limits. The ratio comparison uses integer bits, preserving FPSCR condition
flags rather than executing a floating comparison. The final move publishes
all 32 bytes and its native R0 is forwarded (destination end on the tested
forward path).

The native fixture passes **3,192 cases**: 3,145 completed returns and 47
faults. Cases cover every status, signed/wrapping spans and gaps, policy
halfword extremes, signed count/sum extremes, flags 0/8/128/255, source/output
aliases, unused arguments and invalid pointers. Actual native movement runs.
There are 200 controlled mutations at the first movement's return, affecting
current, previous, aggregation, policy or the private snapshot. An independent
scalar oracle checks the final record, return and guarded SRAM.

There are **2,942 ratio/FP oracle paths**, including 672 zero-count paths and
2,270 actual calculations. Exact rational arithmetic rounds both signed
integer conversions and the division separately to binary32 under all four
rounding modes. Since nonzero integer ratios here stay finite and normal,
it also predicts the cumulative inexact bit. Signed zero is handled explicitly.
The tests check complete FPSCR values, including control modes and seeded
exception flags; 554 nonmerge-status cases acquire new FP flags before their
status is chosen.

A threshold example matters for C: count 1,800 and sum 576 give status 0 under
nearest, negative-infinity and toward-zero rounding, but **status 5 under
positive-infinity rounding** for the tested 1,801-second gap and permissive
policy. Its rounded ratio crosses the stock constant only in that mode.
FP context is activated before assigning FPSCR to avoid Unicorn's lazy-context
reset. Preserved integer/FP registers, SP and interrupt masks are checked on
completed returns; private stack identity and interrupted-fault R0 are excluded.

This is native analysis, not compiled-C equivalence or hardware validation.
All 669 production sources/objects, the manifest and canonical byte-qualified
plan remain unchanged; imports remain 165 application / 34 bootloader. The
upcoming C implementation must preserve live-source reads, signed limits,
early FP evaluation and flags, raw ratio comparison, snapshot fields and the
existing native memory-move return contract.

The subsequent [C review](gomore-interval-refine-c-review.md) implements this
contract and reproduces the native baseline through production C, including
full FPSCR values, then verifies the C compose and engine callers.
