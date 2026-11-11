# R1 optical and quiet-motion wear-off decision in C

The [pure C wear-decision review](wear-decisions-pure-c-review.md) supersedes the remaining assembly boundaries described in this original admission. Both decision units now use the strict GCC C route, with the existing C conversion provider shared by wear-off.

The subsequent [living callback review](wear-living-c-review.md) resolves its
exposed callback dependency and verifies the combined probe sequence. This unit's
compiled object remains unchanged after refining that callback declaration.

`native_wear_off_decision.c` supplies stock `0x3d45c` using C state, scheduling
and logging with explicit signaling-compare and conversion boundaries. The
[review receipt](wear-off-c-review.json) binds REA bytes, production hashes,
comparisons, startup state, rejected defects and qualification.

It captures one OS tick, then uses unsigned subtraction against the living-probe
timestamp. An age greater than 2048 ticks, mode exactly 1, ADT status zero and an
absent living handle register `wear`/`algo` with rate 1 and flags 1, publishing
the raw result after registration. Timestamp is freshly read afterward. Ages at
most 2048 use living status 0/1 to set mode 0/2, leave other statuses alone and
clear both counters. Tick wrapping and registration-time timestamp changes remain
observable.

Older samples use a nonzero ADT stream/count and a fresh unchecked last-history
word strictly below `0x8a1790` to increment the wrapping optical byte counter.
Five low samples apply mode 1 for sleep exactly 1, otherwise mode 0 and optional
living-stream unregister followed by a late handle clear. The optical counter is
then cleared, fresh sleep/history values are logged and the quiet counter clears
after logging. Below five, the optical counter remains incremented.

Otherwise the optical counter clears. The absolute mean-Y raw-bit gate is
`(bits + 0xbb8cffff) < 0x137fff`, with uint32 wrapping; three variances must then
compare strictly below 40 using signaling comparisons. A failure clears the quiet
counter. Sixty quiet samples apply the same sleep-dependent transition and late
release, clear the quiet counter, freshly convert mean Y using native truncation,
then log. Conversion occurs even with logging disabled, preserving out-of-range
and NaN FPSCR behavior after provider mutations. Both counters wrap as bytes.

Five fields own 11 bytes: living handle `0x20006ea0` (four), living timestamp
`0x2001e474` (four), living status `0x2001e470` (one), optical counter `0x2001e47b`
(one) and quiet counter `0x2001e47c` (one). Native RW/ZI handlers execute on poison
with guards; an independent RW decoder agrees all start at zero. Adjacent fields
retain existing ownership. Final source-only RAM placement remains unproven.

Direct verification passes 7,503 paired cases covering tick wrap and 2048 equality,
registration results and timestamp mutation, optical equality and counts through
255, five/sixty thresholds, counter wrapping, late-clear mutations, changing logs,
live history/sleep reads, variance NaNs at each position, mean bit-range boundaries,
signed zero/subnormal/nonfinite means, FZ/DN, preset FPSCR flags and null statistics.
Another 1,624 pairs execute actual C motion coordination, statistics, on/off decisions
and range together. Tick, stream, clear, multicast and log providers remain modeled.
Eight compiled defects are rejected: recency equality, optical equality, lost byte
wrap, quiet threshold, early handle clear, quiet comparison, missing conversion
and stale timestamp. Public state, arguments, logical faults and FPSCR are compared;
preserved registers/SP and masks are checked. Native provider frame depth is 40
bytes versus C 24 or 32, with final SDK tail calls at zero. Void R0, fault PC,
caller-clobbered registers, APSR and private stack are excluded. FP context is
initialized before FPSCR setup; first-use activation and physical/concurrent
behavior remain unverified.

All 649 units compile and both relocatable compositions pass without duplicate
strong symbols. All 648 earlier sources and objects remain unchanged. Wear-off
is resolved while the living-probe callback is exposed, leaving imports at 172/34.
Manifest validation passes. Exact qualification rejects the body. The source plan
stays at 4,345 source-built bytes; a fresh hybrid matches the locked application
with 641,815 executable pull-through and 248 resource bytes. Complete source-only
linking and byte identity from C remain unfinished.
