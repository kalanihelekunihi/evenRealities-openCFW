# R1 optical statistics and float comparator in C

`native_gomore_statistics.c` supplies mean `0x62000`, median `0x62034`, sample
standard deviation `0x6208c` and the float sort callback `0x58a40`. The
[receipt](gomore-statistics-c-review.json) binds production source/object, native
instructions, REA, replay and qualification. No assembly or persistent RAM is
added. The guarded generic APIs retain their original behavior under `_checked`
names; the native functions retain raw signed-word count semantics.

Mean accumulates sample before accumulator, returns positive zero for zero count
and divides by the signed count otherwise. Median calls sort before selecting,
loads upper before lower for even counts, and retains signed division/parity and
wrapped addressing. Zero count therefore preserves the native read before the
buffer rather than inventing an empty-median policy. Standard deviation calls
mean, then native power with exponent two for every sample, and divides by count
minus one except for singleton input. The singleton still performs the power
call and retains its FP effects before returning square root of zero. The callback
uses signaling comparisons and returns zero for unordered inputs.

The production object passes **4,579 native/C cases**, including **28 faults**,
with native sort, power and square root. A further **4,771 cases**, also with
**28 faults**, model provider returns/clobbers and allow negative/huge median
counts without executing unbounded sorting. Checks cover raw FP/int results,
array mutation and write order, FP status, errno, preserved registers, invalid
accesses, logical provider arguments and restored SP. Independent checks include
zero/negative mean signs and singleton deviation. Eight compiled defects are
rejected, including skipped sort, wrong median averaging load order, wrong
sample denominator and omitted singleton behavior.

The same **4,579 cases** pass with the existing C qsort linked to the new C
callback. That run compares top-level sort arguments, results, writes and faults;
it allows internal no-op terminal recursion entries to differ. The C backend
optimizes away such an entry. Callback addresses are explicitly recorded and are
not claimed identical. Power/square root still execute natively in that run.

The actual optical estimator passes **112 heavy-path caller pairs** with all four
C providers substituted: **304 mean**, **112 median**, **152 deviation** and
**512 comparator calls**. These counts match stock. The C extrema/append/compaction
helpers also run. Native sort/power/sqrt and remaining peak matching, interval and
selection code execute from stock; their C bodies and the optical root remain
unfinished.

REA resolves the three statistics functions but does not define a procedure at
`0x58a40`. The comparator supplement is grounded in median's authenticated callback
literal `0x58a41` at `0x62084`, its complete decoded 34-byte returning body and
executed native comparisons. This analysis limitation remains explicit.

Median and deviation retain native 16/32-byte frames at their provider calls.
Mean and comparator use eight private bytes versus native zero. Private frame
bytes and physical FP alignment behavior remain outside the proof. No physical
hardware or complete source-only final link is claimed.

The normal build compiles **697 units**, with no failures or duplicate strong
symbols and unchanged **179 application / 34 bootloader imports**. All **695 prior
units** outside the renamed generic owner retain source/object hashes. Scoped
qualification selects no executable replacement; the canonical plan is unchanged.
Hybrid equality passes with **4,381 source-built executable bytes**, **641,779 stock
executable bytes** and **248 resource bytes**. This does not prove complete C
reconstruction or executable byte identity for these functions.

The pending peak matcher at `0x64380` requires instruction-led reconstruction.
Its decompiled early-counter loop and recovered comparison carry temporaries are
misleading: native low-count paths clean up and return failure. Its `0x27f0c`
comparisons order encoded double keys rather than implementing IEEE unordered
comparisons. For those carry-only branches, keys are `bits` for negative words
and `0x8000000000000000 - bits` otherwise, with carry determined by comparing
transformed second operand against first. This must be preserved when that
matcher is implemented; ordinary C double comparisons cannot simply replace it.
