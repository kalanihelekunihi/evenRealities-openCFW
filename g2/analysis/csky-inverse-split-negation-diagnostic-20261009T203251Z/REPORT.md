# Single-change inverse-split behavioral diagnostic

**33/33 targeted FFT comparisons PASS under the pinned QEMU model:** the original failing constant32767 inverse-real vector plus the32 previously unexecuted FFT cases. The original corpus/first mismatch are immutable and retain their original failure. This is a new explicitly labelled diagnostic run, not a replacement pass for authentic C.

## One semantic intervention

A separate analysis-only copy of authentic csky_split_rfft_q15.c introduces a fixed-width packed-negation helper and replaces only the little-endian inverse split's scalar `-outI` with that helper. Each16-bit lane is sign-decoded into int32_t, minimum-32768 saturates to32767, other values negate, and masked uint32_t lanes are packed using unsigned shifts. The helper avoids signed overflow, negative shifts and implementation-defined unsigned-to-signed conversion. The remainder of the original C algorithm, compiler recipe and stock tables remains unchanged; its other language-arithmetic limitations are not claimed repaired. Original source hash and exact diff are retained.

Diagnostic exports have a separate namespace. Only generated C-wrapper inverse-split references are redirected; original authentic objects/functions and assembly comparison side remain unchanged. No production or compiler/source flag sweep occurred. Both model ELF and stage ELF link successfully; build-results.json binds exact commands. All execution uses offline read-only containers and prior simulator binary identity.

## Documentation and observed deduction

Discovery's retained manufacturer E804 manual2.0 section15.79 specifies independent signed16 saturating negation, consistent with QEMU and this helper. Original Chinese ASCII equations and translated extraction, hashes and mirror provenance are bound in isa-reference-hashes.json; the community mirror is not claimed an official distribution endpoint. This supports the instruction semantics, not physical GX8002 execution or revision attribution. New diagnostic code still awaits independent artifact review; no canonical fidelity/admission is claimed.

The unchanged implementations previously differed at first split imaginary lane because cross1fffc000 scalar-negates toe0004000 versus packed-negatese0014000; the next product leaves0 versus10000, emitting0 versus1. The diagnostic removes that split distinction. Stage reruns now match for the original vector, endpoint-valid conjugate-mirrored spectrum, DC-only diagnostic, and all seven prefix reductions512..8; split/core/final-doubling outputs agree. Together with33 finite FFT passes, this is evidence that the single negation distinction explains the observed failure in the tested domain. The earlier23 FFT passes used the original C implementation and were not rerun under the diagnostic: do not combine them into a56-case corrected-model pass.

## Simulator MAC discrepancy stays explicit

The manual15.130/131 saturates the full accumulator plus dual signed16 products. Directed tests execute x=y80008000 for z0,-1,INT32_MIN. For both MULACA and MULACAX, QEMU yields80000000; documented expected values are7fffffff,7fffffff,0. These are six expected documented-operation/model differences (four new accumulator probes plus two repeated z0 probes), not passes and not physical failures. No QEMU patch, result normalization or pre-saturation workaround was made.

A bounded static table/source check excludes this specific all-min-pair corner at the three real-split assembly MAC sites: tableA's256 coefficient pairs contain no80008000, and derivedB's saturated-absolute low lane cannot8000. Each MAC takes one such coefficient operand; the triggering pair requires both operands80008000. mac-corner-exclusion.json records table hash/formula and exact source sites. This does not certify all compiler-generated arithmetic, other table sizes/callers or the emulator generally.

## Stopping boundary and useful implication

The requested single-change diagnostic is complete; the observed mismatch is explained and targeted remaining cases execute without new discrepancy. Authentic C is compilable/linkable but remains a distinct numerical implementation from exact-reproduced stock assembly; this labelled model can guide faithful reconstruction, not be substituted into production before current workflow gates. Broader numerical completeness, other arithmetic corners, hardware timing/IRQ/startup and full source/byte-identical firmware remain unproved. Independent audit of this new model and table-bound exclusion is the next review input, not another configuration sweep.

Original seals verify; preservation checks all110inputs/four checkpoints and records observed stable index. No Git/Pigweed/production/canonical/device/simulator-source edits.
