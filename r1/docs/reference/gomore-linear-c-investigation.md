# GoMore linear interpolation C investigation

This is the pre-integration checkpoint. The subsequent [C review](gomore-linear-c-review.md) records consolidated ownership and normal-build integration.

Stock `0x882ec` is the remaining interpolation provider. The experimental C
candidate remains in `build/goal-r1-gomore-linear-c/`; production still imports
this provider. The [receipt](gomore-linear-c-investigation.json) binds REA bytes,
compiler probes and initial native/C replay.

Equal input/output rates tail-call native memory movement with length
`source_total << 2`, including overlap-safe copying and its non-ISO raw return
word. The generic owner currently uses a forward float loop, which does not
preserve this overlap behavior. Unequal rates use signed SDIV (zero divisor
produces zero), wrapped multiplication, signed-to-double, floor and double-to-int
before computing a signed float ratio. The produced count is returned in R0.
The experimental C substitutes the exact integer round trip with its original
wrapped integer; broader flag/boundary verification is pending.

The position conversion truncates toward zero, then stock clamps only the right
sample index. Fraction calculation uses non-fused VNMLS, followed by right-sample
load, left-sample load, subtraction, multiplication and addition in that order.
Strict GCC `ratio * index - left` emits VNMLS directly. The apparently equivalent
`-(left - ratio * index)` emits VMLS plus VNEG, so it is not assumed equivalent
for NaN payload/sign and exceptional cases. No inline assembly is used by the
experimental candidate.

The expanded candidate passes **4,723 native/C cases**, including
**14 fault cases**, with complete memory views, non-stack write observations,
raw returns, FPSCR and completed-call register preservation. Coverage includes
signed counts, negative-rate arithmetic, wrapping division cases, aliased output,
NaNs, infinities, signed zero/subnormals, four rounding modes, default-NaN and
flush-to-zero. **747 equal-rate cases** additionally check an
independent overlap-copy/return oracle. Arbitrary huge-loop termination and
physical alignment/trap behavior remain unproven.

The explicit float-to-signed guard separately matches stock VCVT result/FPSCR
for **16,536 cases** across boundary and seeded raw float bits and
FP modes. **4,101 actual stock integer/double/floor/integer sequences**
return the original word with unchanged FPSCR, supporting the integer-round-trip
elision in the candidate. These finite tests do not constitute exhaustive
32-bit enumeration. Six independently compiled defective variants are rejected
(copy length, ratio, fraction sign, negative-count guards, difference order and
return). Compilation failures do not count as defect detection.

The actual native/C host adapters, resampling adapters, wrappers, filters and
interpolation pass **334 integration cases**, including **9 fault cases**,
with **984 modeled logger/final-algorithm calls**. Stock clear and memory
move execute on both paths. Input arrays contain finite or selected raw FP
samples; numeric scratch pointers are compared without normalization. The old
modeled-kernel mutation duplicates were removed once those providers actually
executed. The observed fault cases now include real interpolation dereferences
through aliased host metadata; this remains emulator evidence.

Before production promotion, consolidate the existing generic interpolation
owner and its motion-feature caller, run the normal source build and
qualification, and bind replay to that production object. Wrapper/outer-caller
stack differences remain open. No source manifest or canonical source selection
changes at this checkpoint. The normal build remains 682 units with 166
application and 34 bootloader unresolved imports.
