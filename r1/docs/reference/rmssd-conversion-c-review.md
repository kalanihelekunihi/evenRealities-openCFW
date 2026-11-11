# R1 RMSSD diagnostic conversion in C

The RMSSD routine at stock `0x575d8` now contains **no inline assembly**. Its
unsigned diagnostic conversion classifies binary32 encodings before casting:
NaNs and negative values at or below -1 produce zero with invalid-operation;
positive values at or above 2^32, including infinity, produce `UINT32_MAX` with
invalid-operation. Remaining values are within the C unsigned-cast truncation
range, including negative fractions above -1 and both signed zeros. The pinned
GCC 9 strict floating-point profile emits the native truncating conversion there.
A volatile zero/zero operation supplies the invalid flag on saturated paths.
This is verified compiler/target behavior, not a portable exception-handling
claim for arbitrary C implementations.

The existing unit uses GCC profile 53 with signaling, rounding and trapping math
flags and contraction disabled. No new function copy, RAM owner or import is
added. The [receipt](rmssd-conversion-c-review.json) binds the production object,
source, checked REA bytes and replay artifacts. The original
[RMSSD reconstruction](rmssd-c-review.md) describes the surrounding algorithm.

The isolated helper passes **114,688 stock/C conversion pairs**: 3,584 input
patterns cover every exponent, both signs, selected mantissas and seeded values,
each under 32 rounding/FZ/DN/sticky-flag combinations. The stock `VCVT` bytes at
`0x577c8` execute directly. Return bits and FPSCR match, including infinities,
NaNs, overflow, negative fractions, denormals and invalid/inexact effects.

The full function passes **6,525 paired RMSSD cases**, including **two bounded
nonterminating prefixes** that retain the wrapping 16-bit index and unchecked
predecessor address. The prefix observation point follows the actual GCC loop
header rather than the previous Clang offset. The original 6,505 cases are
supplemented by 20 post-filter input-mutation cases with SDK logging enabled,
exercising signed squared-sample overflow and diagnostic conversion. Those
mutated logging arguments are compared directly against stock; the original
independent filter/rational-FP oracle remains on its supported inputs.
Actual C memset, float-bit promotion and sqrt helpers execute. Allocation/free,
activity and log providers remain modeled. Preserved registers, masks, SRAM,
return bits and FPSCR are checked; private stack and caller-clobbered state are
excluded. Nine compiled defective variants must fail their behavioral replay.

All **672 units** compile and both relocatable compositions pass without duplicate
strong symbols. The other **671 source/object pairs** and both import sets remain
unchanged: **163 application / 34 bootloader** unresolved symbols. The qualifier
rejects this function, so no instruction-qualified bytes are added. The canonical
plan remains at **4,369 source-built bytes**, and the fresh hybrid matches the
locked application through executable pull-through. First-use FP activation,
physical allocator/device behavior, full source-only linking and byte identity
remain unproven. The separately owned [sqrt helper](sqrt-builtin-c-review.md) now uses a
verified C builtin; that follow-up supersedes the earlier assembly boundary.
