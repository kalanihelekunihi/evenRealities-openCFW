# Spectral quantile, sorting and outlier mask in C

`native_spectral_quantile.c` implements the312-byte quantile estimator,62-byte insertion sort and130-byte quartile mask. It preserves raw float sorting, native encoded math/comparisons, original-input endpoint behavior and live input/mask aliases. No writable owner or inline assembly is added.

**6,806 native/C scenario pairs pass:**6,444 main cases (including288 independent finite rational oracle cases) and362 positive control-baseline cases. The272 three-call mask/cleanup/window chains give7,350 top-level entry-call pairs. All504 new native instruction bytes execute. Allocator/free are modeled; algorithm, math and memory helpers execute as real C/native code.

Tests compare full public RAM, active FPSCR, saved registers, stack and masks across all FP settings,125-sample inputs, NaNs/denormals, selected aliases, scratch clobbers and original-input mutations. Twelve compiled defects are rejected. Early interpolation-loop exit changes FPSCR even when the returned estimate matches; the tests catch it. A targeted overlapping-mask case proves the final sample reload matters.

Low/high quantiles intentionally return first/last original input elements. Interior estimates use sorted scratch. Independent oracles retain that stock behavior and use ordered rational rounding for the normal finite range.

All910 R1 units compile and compose without failures or duplicate strong symbols. The tested object equals normal build;899 prior nongenerated source/object pairs are unchanged. Imports stay87 application/22 boot. Source-plan and cache-layout files remain unchanged.

Quantile/mask counts1..125 and bounded buffers are tested; standalone sort also tests0. Invalid/faulting buffers, heap exhaustion/actual allocator lifecycle, private aliases, cold FPU, physical IRQ/concurrency, stack budget/throughput, final startup/layout and sensors/boot remain unverified. FFT/spectral orchestration and ten top-level processing boundaries remain open. Relocatable composition is not bootable firmware.

[Machine-readable evidence](goodix-spectral-quantile-c-review.json) records contracts, profiles and hashes.
