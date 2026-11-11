# R1 interpolation in C

`native_gomore_linear.c` supplies stock interpolation `0x882ec` with its five-word
ABI. The [receipt](gomore-linear-c-review.json) binds the production source/object,
REA bytes, direct/integrated replay, conversion checks, defect controls,
consolidation, qualification and normal composition.

Equal rates preserve overlap-safe native movement, wrapped byte length and its
observed raw return. Unequal rates preserve signed SDIV behavior, wrapped produced
count, signed float ratio, truncating position conversion, right-index clamping,
right-before-left sample loads and ordered non-fused floating-point operations.
There are no pointer/count guards. C saturation guards avoid undefined invalid
float casts while reproducing stock results and IOC. No inline assembly,
executable data or persistent RAM is introduced.

Strict GCC C helpers preserve VMUL/VSUB/VADD operand order and emit the native
VNMLS fraction operation from `ratio * index - left`. The native integer-to-double,
floor and double-to-integer sequence operates on an already integral signed word;
the C candidate retains that wrapped word directly. This substitution is supported
by 4,101 actual stock round trips with unchanged result/FPSCR. It is not claimed
as a byte-identical instruction sequence.

The production object passes **4,723 direct native/C cases**, including **14 fault
cases**, across signed counts, division/wrapping boundaries, overlapping buffers,
NaNs, infinities, subnormals/signed zero, four rounding modes, default-NaN and
flush-to-zero. Non-stack writes, full memory views, raw return and FPSCR are
compared; completed calls also check saved integer/high-FP registers and SP.
**747 equal-rate cases** have independent copy/return expectations. The guarded
float conversion separately matches stock for **16,536 raw-bit/mode cases**.
Six independently compiled defects are rejected. These matrices do not prove
arbitrary huge-loop termination or exhaust all 32-bit values.

The actual native/C host adapters, resamplers, wrappers, filters and interpolation
pass **334 integration cases**, including **nine fault cases** and **984 modeled
logger/final-algorithm calls**. Numeric scratch pointers are compared without
normalization. Stock clear and memory movement still execute on both paths.
This fixture does not establish a completely source-executed graph. Wrapper and
outer sensor-update stack differences remain open, as does physical device proof.

The superseded generic interpolation owner and declaration are removed. Its one
motion-feature caller now passes the same sample pointers and fixed 25/30/25
counts to the native provider and ignores the raw return. All other generic
source remains unchanged; one stock implementation is retained.

The normal build compiles **683 units** (609 application, 74 bootloader), with
**165 application and 34 bootloader unresolved imports**. All **681 preceding
units outside the consolidated generic owner** retain identical source/object
hashes. Source checks and relocatable composition pass without new failures or
duplicate strong symbols. This resolves interpolation without adding imports.

Qualification selects no new replacement and the canonical source plan remains
unchanged. Hybrid raw equality still uses executable stock pull-through, and does
not prove fully C firmware, a complete source-only final link or byte-identical
source reconstruction. Experiments and reproduction scripts remain under
`build/goal-r1-gomore-linear-c/`; the normal report is
`build/sources-goal-r1-gomore-linear-c/report.json`.
