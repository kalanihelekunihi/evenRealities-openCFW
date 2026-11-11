# R1 RMSSD filtering and arithmetic in C

Latest follow-up: [diagnostic conversion in C](rmssd-conversion-c-review.md)
removes the remaining RMSSD assembly. Counts below describe the original review.

Follow-up: the [activity-mode getter](activity-mode-c-review.md) is now
implemented in C and passes the linked RMSSD corpus. The import and build
counts below describe this RMSSD review's earlier snapshot.

`native_hrv_rmssd.c` implements the corrected 536-byte routine at `0x575d8`
with C allocation, mask filtering, difference collection, float arithmetic,
diagnostics and cleanup. The [receipt](rmssd-c-review.json) binds production
hashes, REA bytes, comparisons, rejected defects, qualification and builds.
The [native analysis](rmssd-native-analysis.md) establishes the stock contract.
This unit adds no RAM. One small unsigned FP conversion helper remains for
diagnostic values; the existing sqrt helper retains its own instruction boundary.

Null input or unsigned count below two returns −1. Otherwise the first
workspace has one validity byte per sample, initially one. Activity mode
exactly 1 selects ceiling 1,500; other values select 1,100. Adjacent differences
outside inclusive ±150, or a current sample above the ceiling, clear both
endpoint flags. A second workspace holds absolute differences whose endpoint
flags both survive. The two workspaces are freed in allocation order before
result logging. Each allocation failure preserves its stock cleanup/log path.

Indices and accepted count remain 16-bit. Count 65,535 completes; successful
allocations with counts above 65,535 retain the stock first-loop wrap, including
the wrapped predecessor access before the input/mask. Two matched prefixes
stop after 65,538 filter-phase visits, after observing zero and repetition.
They are not completed calls or physical allocation claims.

Arithmetic retains low-32-bit integer squares interpreted as signed before
float conversion, sequential addition, float32 division and the existing C
sqrt provider. Empty results keep sum, mean and result at −1. Ring logging
uses the existing C binary32-to-binary64 bit provider in stock order; SDK
logging applies native unsigned conversion even to −1, preserving saturation
and IOC. The `VCVT.u32`/`VMOV` helper is retained for this FP status behavior;
the filtering and arithmetic need no new assembly. Stock diagnostic strings,
including the SDK's float-looking format with integer arguments, are preserved.

The production object passed **6,505 paired cases: 6,503 returns and two bounded
prefixes**. Completed cases compare return bits, FPSCR, saved integer/FP
registers, SP, interrupt masks, heap guards, mask/difference contents and log
arguments. Native memory-fill/clear, float promotion and sqrt execute on the
stock side; actual C memset, float-bit promotion and sqrt execute on the C side.
An independent filter/difference oracle and exact-rational rounding checks
cover ordinary vectors, threshold direction, zero samples, chained rejection,
mode selection, both allocation failures, FZ/DN and all rounding directions.
Twenty further cases mutate inputs through the second-allocation provider after
mask filtering. They verify signed integer-square interpretation, negative
sqrt results and errno/FP flags against stock. Allocator/free/activity/logging
providers are modeled. FP context is warmed before FPSCR; first-use activation,
concurrent provider behavior and physical allocation remain outside the proof.

Nine compiled defects were rejected: wrong delta boundary, non-exact mode
test, missing previous-endpoint invalidation, zero-initialized mask, wrong
workspace size, early empty-result return, reversed free order, lost logging
IOC and unsigned square interpretation.

All **657 units** compile and both relocatable compositions pass without
duplicate strong symbols. All **656 previous source/object hashes** are
unchanged. Resolving RMSSD exposes the activity-mode getter, leaving **169
application / 34 bootloader imports**. No instruction-exact RMSSD body qualifies
under production bindings. The canonical plan remains at 4,369 source-built
bytes and the fresh hybrid matches the locked application through executable
pull-through. Complete source-only linking and physical HRV operation remain
unproven.
