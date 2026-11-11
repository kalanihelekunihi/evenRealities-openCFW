# R1 RMSSD native contract and corrected body boundary

Follow-up: the [C RMSSD review](rmssd-c-review.md) now implements this contract
with a retained unsigned FP conversion helper for diagnostics. The unresolved
status below describes this earlier native analysis snapshot.

The [receipt](rmssd-native-analysis.json) binds REA bytes, locked artifact and
ELF hashes, **6,485 native probes: 6,483 returns and two bounded nonterminating
prefixes**, and the frontier correction. The actual code body `0x575d8` through
`0x577ef` is **536 bytes**, including the final `VMOV S0,S18` and branch omitted
by the inventory's 530-byte extent. The frontier remains unresolved; this
boundary correction does not claim a C implementation or exact source bytes.

Null input or unsigned count below two returns float −1 without allocation.
The first allocation requests one validity byte per input sample and fills
all bytes with one. Activity mode **exactly 1** selects ceiling 1,500; other
mode values select 1,100. For each adjacent pair, stock rejects when
`(uint32_t)(current - previous + 150) > 300` or `current > ceiling`, clearing
**both endpoint flags**. Differences ±150 are accepted. The ceiling applies
to the current sample, so `[1101,1100]` can pass at ceiling 1,100 while its
reverse does not. Zero samples have no separate rejection rule. One rejected
pair can invalidate adjacent otherwise-good differences through the shared
endpoint mask.

The second allocation requests `(count * 2 - 2)` bytes with 32-bit arithmetic,
then clears it. Both endpoint flags must remain nonzero to append the absolute
halfword difference. For accepted differences, stock squares in integer
arithmetic, interprets the low 32-bit product as signed, converts to float32,
then performs sequential **square + sum**, float32 division by accepted count,
and the native square-root helper. The independent oracle uses exact rational
comparisons for float rounding and square-root direction. Normal filtering
limits accepted differences to 150; the signed product behavior still matters
if future tests permit providers to alter input/masks between phases.

No accepted differences leaves **sum, mean and result all −1**. Both buffers
are freed, in allocation order, before result logging. Ring logs promote
result/mean/sum to doubles; SDK logs use native unsigned float conversions and
accepted count. SDK logging can therefore set IOC on the unchanged −1 result,
where disabled logging leaves that exception clear. A C implementation must
retain this side effect rather than returning early for an empty result.
First allocation failure logs and returns −1 without freeing. Second failure
frees the first buffer, logs, then returns −1.

Loop indices and accepted count are **16-bit**. Count 65,535 completes in the
probe. Counts 65,536 and 65,537 cannot terminate the first filter loop: its
index wraps through zero. Two probes stop after 65,538 loop-header visits,
after observing zero and repetition. At wrapped index zero, the predecessor
read and flag write also reach before the respective input/mask starts.
These are bounded prefix observations, not completed calls. The huge-count
allocation-failure path is separately covered without assuming allocation
success for an impossible physical request.

Cases cover threshold direction, zero inputs, chained mask rejection, random
vectors, both allocation failures, exact mode selection, changing log modes,
FZ/DN and all rounding directions. Native memory-fill/clear, float-to-double
and sqrt helpers execute; allocation/free/activity/logging providers are
modeled. The FP context is warmed architecturally before FPSCR setup. Saved
integer/FP registers, SP, masks, heap guards, mask/difference bytes, log values,
return bits and FPSCR are checked or recorded. The largest input is held in
an isolated fixture mapping to avoid overlapping the firmware errno cell.
All 656 current source/object hashes, manifest and source plan remain unchanged.
C equivalence, physical allocation, concurrency and final source linking remain
unproven.
