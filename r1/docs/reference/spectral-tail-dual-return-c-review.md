# Owned FFT tails and C dual-register math returns

The spectral wrapper now allocates **1,032 bytes**, four more than stock, so the real FFT owns both tail words it reads. Its old 1,028-byte request exposed adjacent heap metadata as a float operand. The real allocator zero-fills the additional word. This deliberately improves memory safety; byte identity is not an acceptance requirement.

`native_math_selection.c` now contains **no inline assembly**. Its core-register fabs entry calls the existing `noinline` hard-float fabs provider, then returns the same encoded value in R0/R1. The emitted return leaves the required result in D0 as well. The existing fabs body is unchanged and no duplicate implementation is introduced.

The dual return passes **282,176 pairs**: 278,592 native/C/encoding-oracle pairs, 3,328 actual atan/tanh/pow C caller-chain pairs and 256 positive control pairs. Three compiled defects are rejected. Both return interfaces, FPSCR, saved registers, SP/masks and public RAM are checked. Caller-clobbered R2/R3/D1 and private frame contents are outside this contract.

The final normal-build pipeline passes **576 old/new source comparisons**, including 512 independent DFT checks and 64 special-value cases. All live stage outputs match bit-for-bit. FP controls and NZCV match; cumulative exception flags are recorded separately because the unsafe tail read could consume a denormal heap header. Both source pipelines run without stock code or data mapped.

An additional **64 exact-size-reuse wrapper comparisons** place the next live guard block header (word value 1,036) at the old second-tail address. The new allocation avoids that undersized hole. Spectrum bits and initial sticky flags are preserved. The fix removes artificial underflow/inexact flags in eight cases and input-denormal flags in sixteen; forty retain the same status. These cases also pass direct DFT checks, bringing the total to 576 DFT checks. A compiled one-tail allocation control is rejected.

All **915 R1 units** compile and compose without failures or duplicate strong symbols. Imports remain **86 application / 22 boot**. The 903 unrelated source/object pairs, source-plan and cache layout are unchanged. Production and probe executable sections, relocations and symbol contracts match; source-file name metadata differs. The repository source check exits successfully, with zero unbuilt R1 sources and one existing unbuilt G2 source.

The observed 256-point sensor path is verified. Malformed inputs, exhaustion/fatal paths, traps, cold FPU, physical IRQ/timing, stack/throughput, final startup/layout, sensors and boot remain open. Relocatable composition is not bootable firmware.

[Machine-readable evidence](spectral-tail-dual-return-c-review.json) records exact results, status differences, bounds and hashes.
