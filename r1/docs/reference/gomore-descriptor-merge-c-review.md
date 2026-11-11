# R1 descriptor merge in C

`native_gomore_descriptor_merge.c` implements the 158-byte native interface at
`0x72024` in ordinary C, with no new RAM or assembly. The [receipt](gomore-descriptor-merge-c-review.json)
binds REA bytes, production hashes, paired comparisons, negative controls,
qualification and builds. The native seven-argument ABI and raw R0 returns
are preserved; the existing portable boolean API is not substituted.

Following the [native analysis](gomore-descriptor-merge-native-analysis.md),
the implementation clears forty output bytes before source reads, writes type,
initial start and low profile byte in order, and skips source accesses for any
nonzero bypass. Merged paths reload source words and store sums in offset
order 8, 20, 12, 16, 24. All sums wrap unsigned. A nonpositive signed combined
count skips count/mean stores. A positive total is stored before reloading
the weighting counts, preserving output/source aliases. Completed bypass
returns are 3; merged returns are the raw combined count.

The weighted mean uses separate binary32 count conversions, products, addition
and division. The production unit disables FP contraction and uses volatile
source reads; no FP assembly boundary is needed for the tested aligned-record
ABI. Actual stock/C result bits and FPSCR values match for signed zeros,
NaNs with payloads, signaling NaNs, infinities, subnormals, maximum finite
values, count extremes, directed rounding, DN/FZ and preexisting flags.
This does not establish equivalence for broader misaligned VLDR inputs.

Validation passes **3,640 direct stock/C cases**, including 19 faults, 3,145 FP
paths and 941 independent exact-rational finite-result checks. The corpus
includes the native analysis cases plus 1,024 seeded random combinations of
mean bits, counts, aliases and FPSCR modes. Actual C EABI memory clear and
upstream musl memset execute; native memory clear executes on the stock side.
The FP context is warmed before assigning FPSCR. Independent sequential-memory
and rational shadows remain active alongside direct stock/C equality.

The 36 clear-return mutations change source counts and both means. Changing
both means closes a coverage gap: when addition aliases the cleared output,
a stale weighting count multiplied by a cleared zero mean could otherwise
look correct. The strengthened corpus rejects that defect while stock and
production C still agree. On interrupted faults, incidental R0 values are
excluded; completed return values remain compared.

A further **2,152 stock/C cases** execute the actual C interval engine and
merge with setter and memory routines. Another **2,328 cases** execute the
actual C interval-update caller, engine, merge, memory routines, propagation
and packed accessors. Compose remains modeled. These integrated corpora
contain 32 and 400 matching faults respectively. Total: **8,120 paired cases,
451 faults and 7,669 completed returns**.

Comparisons include provider arguments/order, guarded SRAM, ordered stores and
widths, output bits, saved integer/FP registers, SP, masks and FPSCR on completed
returns. Private stack bytes and caller-clobbered state are excluded. Internal
memory-provider writes are excluded from width comparisons when actual C
providers execute; resulting memory remains compared. Concurrent and physical
hardware execution are not established.

Ten compiled defects are rejected: numerical sum order, cached previous or
addition weighting counts, wrong bypass return, FP on zero total, boolean
return, unsigned weight conversion, wide profile store, rounding each divided
term separately and omitted count store.

All **668 units** compile and both relocatable compositions pass without
duplicate strong symbols. All **667 previous sources and objects** remain
unchanged. Resolving merge adds no imports, leaving **164 application / 34
bootloader imports**. Compose at `0x67558` remains native.

Instruction qualification rejects the merge's relocation pattern. The
canonical plan remains 4,369 source-built bytes, 641,791 executable pull-through
bytes and 248 resource bytes; a fresh hybrid application matches the locked
artifact through pull-through. Complete source-only linking, byte-identical
reconstruction, context initialization and physical validation remain unfinished.
