# Native complex and real FFT core in C

`native_spectral_fft.c` implements bit reversal (22 bytes), pair permutation (72), complex transform (396) and real magnitude transform (318). It owns the exact 260-byte quarter-cosine table, adds no writable state and uses no inline assembly. Sqrt and memory helpers execute as actual C.

**2,833 stock/C scenario pairs pass:** 2,242 matrix cases, 577 independent oracle cases and 14 positive control-baseline cases. The oracles include 48 direct finite DFT checks. All 808 native instruction bytes execute, and twelve compiled defects are rejected. Full public RAM, active FPSCR, saved registers, SP and masks agree across the tested FP modes, special values, selected live aliases and tail contents. Source execution cannot enter stock code.

The 256-point path owns its coefficients. Legacy non256 calls depended on incoming R9; the C interface makes that dependency an explicit fourth pointer argument. This is a deliberate C API change, not a claim of stock three-argument ABI identity or general transform-size support.

The real core reads two live words beyond the transform data. Its native prepare wrapper requests only one extra word. The actual allocator uses four-byte alignment, so the second read can reach a following heap header. Core tests preserve those reads with varied tail contents; actual allocator/wrapper integration remains open.

All 911 R1 units compile and compose without failures or duplicate strong symbols. The tested object equals normal build; 900 prior nongenerated source/object pairs are unchanged. Imports remain 87 application/22 boot. Source-plan and cache layout remain unchanged.

Tests cover complex128 step2; real256 input counts0/1/125/256; selected legacy non256 sizes0/2/4/8/16; and bounded mapped buffers. Invalid/faulting inputs, actual heap lifecycle, cold FPU, physical IRQ/timing, stack budget, startup/layout, sensors and boot remain unverified. Prepare/copy wrappers, spectral orchestration and ten top-level processing boundaries remain open. Relocatable composition is not bootable firmware.

[Machine-readable evidence](goodix-spectral-fft-c-review.json) records contracts, exact results and hashes.
