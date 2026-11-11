# R1 wear motion statistics in C

The subsequent [active-FP followup](wear-range-c-review.md) corrects the emulator
setup used for FPSCR mode coverage and replays the unchanged statistics and motion
objects. It passes all direct/integrated cases with 404 bounded prefixes. The
original counts and fixture descriptions below remain historical; mode labels
alone did not establish active FZ/DN/rounding settings before that followup.

`native_wear_motion_statistics.c` supplies stock `0x3ceec` as ordinary C without
assembly arithmetic. The [review receipt](wear-statistics-c-review.json) binds
REA bytes, production hashes, direct/integrated comparisons and qualification.
The working span is corrected from 378 to 382 bytes to include the final store
and return; exact qualification was rerun against the full span.

The routine accumulates signed 16-bit interleaved axes into the supplied output's
existing first three float words, divides them by the freshly read halfword count,
then accumulates squared deviations into the existing final three words and divides
again to produce population variances. It does not initialize the output itself.
FP contraction is disabled to preserve the stock rounding stages. Sample reads,
output stores and fresh count reads preserve order, including aliases. Means are
captured for the second pass while variance accumulators remain freshly loaded.
Both loops use wrapping eight-bit indices. Stable counts above 255 do not terminate;
the implementation preserves that behavior rather than capping or widening them.
No new RAM or imports are introduced.

Direct verification covers 1,910 paired executions/prefixes, including signed axis
patterns, seeded accumulators, zeros, subnormals, infinities, quiet/signaling NaNs,
rounding/FZ/DN modes, zero counts, counts through 65535, output aliases into packet
data/count and null faults. Of these, 408 are bounded prefixes stopped after 512
Z stores, not completed executions. Actual memory and FPSCR are compared, with
preserved registers/SP checked on normal returns and interrupt masks checked.
Another 1,624 paired cases execute the actual C statistics inside the C motion
coordinator, modeling clear/on/off/multicast providers and comparing FPSCR at those
boundaries. The integration instruction allowance was increased to accommodate
actual 255-sample loops. The total is 3,126 completed comparisons plus 408 prefixes.

Six compiled defects are rejected: unsigned axes, sample rather than population
variance, widened loop index, byte count, lost initial seed and wrong sample stride.
Void R0, fault PC, caller-clobbered registers, APSR and private stack residue are
excluded. Bounded-prefix agreement does not establish completed high-count calls.
Physical/concurrent behavior remains unverified.

All 646 units compile and both relocatable compositions pass without duplicate
strong symbols. All 645 earlier sources and objects remain unchanged. Statistics
is resolved without new imports, leaving application/bootloader imports at 173/34.
Manifest validation passes. The body does not qualify as exact. The source plan
remains at 4,345 source-built bytes; a fresh hybrid matches the locked application
with 641,815 executable pull-through and 248 resource bytes. Complete source-only
linking and byte identity from C remain unfinished.
