# R1 packed timeline and two-bit sample access in C

`native_gomore_timeline.c` supplies timeline extraction at `0x68354`, packed
sample reading at `0x69500` and writing at `0x8ed2c`. All three are ordinary C,
with no new assembly, globals or executable blobs. The [review receipt](gomore-timeline-c-review.json)
binds production source/object hashes, REA stock bytes, replay artifacts,
negative controls, qualification and normal composition.

The reader uses an unsigned index modulo 2,880, selecting one of four two-bit
samples in each byte. The writer has a different contract: its index is signed,
with signed remainder and division toward zero. It preserves ARM register-shift
semantics for unusual negative indices, does not mask the incoming value to two
bits, and returns the full shifted value in R0. Bounds checks or a normalized
boolean return would change the observed contract.

Extraction takes eight integer arguments. A null output returns zero without
reading context. When the unsigned difference between the fourth argument and
start is at most 900, it clears nonzero packed samples from start to that fourth
argument in 30-second steps. Otherwise it uses the alternate clear range only
when its start argument is nonzero. The fifth argument is unused. It then expands
samples from start to end every 30 seconds, stopping at 2,880 output bytes. The
stock stride selector is initialized to one and never changed; its unreachable
stride-two branch is unnecessary in C. Arithmetic wraps as in stock. No capacity,
pointer validation or termination policy is invented for pathological clear spans.

The direct fixture runs the actual getter and setter under extraction, with
2,238 paired native/C cases. It covers sample boundaries and ring wrap, signed
extreme write indices, high input bits and full R0 results, zero and aliased output,
900-second clear selection, extraction cap, unsigned timestamp wrap, logical null
faults and interrupt masks. Another 1,537 pairs execute the actual C consumer,
timeline, getter/setter, history shift and prefix marker together. Those compare
payload and workspace bytes, provider arguments, raw stack padding and FPSCR.
Table lookup, refinement, scoring and clearing remain modeled chain boundaries.
Six compiled defects are rejected: wrong ring size, unsigned write index, masked
write value, wrong 900-second edge, wrong stride and an off-by-one extraction cap.
Total: 3,775 paired cases. Caller-clobbered registers, APSR and private stack
residue are excluded. Physical and concurrent behavior remain unverified.

All 630 units compile and both relocatable compositions succeed without duplicate
strong symbols. All 629 previous objects remain identical. Application imports
drop from 171 to 170; bootloader imports remain 34. The consumer still depends on
native table lookup `0x684b4`, refinement `0x81040` and scoring wrapper `0x68fbc`.
Manifest checks pass. None of the three new roots passes byte qualification.
The exact source plan remains unchanged at 4,299 source-built bytes; a fresh
hybrid application matches the locked official artifact, retaining 641,861
executable pull-through bytes and 248 resource bytes. This does not establish a
complete source-only link or firmware hardware validation.

The subsequent [score-flow reconstruction](gomore-score-flow-c-review.md) supplies
the two-stage statistics and prepare/score coordinators in C. Three numerical
providers remain native imports; the actual C chain fixture now includes both
coordinators.
