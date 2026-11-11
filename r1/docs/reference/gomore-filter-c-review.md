# R1 IIR filter in C

`native_gomore_filter.c` supplies stock `0x641f0` with the three-word native ABI.
The [receipt](gomore-filter-c-review.json) binds REA bytes, production source/object,
replay, compiler probes, defect controls, consolidation and build checks.
No inline assembly, executable data or persistent RAM is introduced.

The implementation loads the filter order after each initial sample multiply,
retains signed comparisons and wrapping address/index arithmetic, performs input
and output history copies in descending order, rereads the input after copying,
and publishes input history, output history and sample output in stock order.
Ready word one is written even for zero or negative signed sample counts.
The observed raw R0 remains the state pointer. Pointer/order guards are absent,
matching stock rather than the former generic checked API.

Strict GCC C helpers emit the native non-fused `VMUL`, `VMLA` and `VMLS` operations.
The non-inlined helpers preserve operand order and NaN selection. A compiler
probe confirms contraction off emits VMLA/VMLS; contraction fast emits fused
VFMA/VFMS and is unsuitable. No explicit assembly supplies those operations.

The production object passes **5,180 native/C cases**, including **25 fault
cases**, covering signed counts/orders, aliased state/sample ranges, pointer
faults, NaN/zero/infinity/subnormal values, four rounding modes, default-NaN and
flush-to-zero. Completed calls check saved integer/high FP registers and final
SP. Fifteen finite low-order cases additionally compare an independent byte and
arithmetic model. Six compiled defects are rejected, including fused addition,
reversed history copying, altered order/ready/offset and swapped multiplication.
Arbitrary huge-order termination and physical alignment traps are not proven.

Actual native/C host adapters, resamplers, kernel wrappers and filters pass
**442 integration cases** with **2,700 modeled lower-provider calls**. Interpolation,
logging and final algorithm output remain modeled; stock memory clearing executes
on both paths. Existing wrapper and outer sensor-update stack differences remain
open. This does not establish whole-chain ABI equality or physical execution.

The superseded unused generic `gomore_primitives_iir_filter_apply` definition and
header declaration are removed, leaving one stock owner. The rest of the generic
owner source is unchanged. The normal build compiles **682 units** (608 application,
74 bootloader), with **166 application and 34 bootloader unresolved imports**.
All **680 prior units outside the consolidated generic owner** retain identical
source/object hashes. Source checks and relocatable composition pass without
new failures or duplicate strong symbols. Interpolation remains unresolved.

Qualification selects no new replacement and the canonical source plan is
unchanged. Hybrid equality still includes executable stock pull-through; fully C
firmware, a complete source-only link and byte-identical source reconstruction
remain unproven. Reproduction artifacts are under `build/goal-r1-gomore-filter-c/`;
the production report is `build/sources-goal-r1-gomore-filter-c/report.json`.

The subsequent [interpolation review](gomore-linear-c-review.md) supplies that
provider in C and extends actual host-chain replay. Clear/move still execute
from stock in that fixture; logging and final algorithm output remain modeled.
