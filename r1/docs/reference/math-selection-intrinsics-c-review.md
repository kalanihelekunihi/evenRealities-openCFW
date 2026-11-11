# Math selection through C and compiler intrinsics

`native_math_selection.c` removes three inline assembly blocks. Ceiling/floor now retain their status-producing addition through a volatile C result. Encoded comparison rules and FPSCR builtins replace VCMPE-zero/VMRS. The flag-returning helper uses the compiler APSR intrinsic, which produces an object identical to the tested probe.

**316,256 verified calls pass:**295104 native/C arithmetic calls,12268 independent value-oracle calls,84 positive control calls 8704 native/C/integer-oracle APSR calls and96 actual parent-operand calls. Six compiled defects are rejected. Checks cover32 FP control/status settings, NaNs, subnormals, infinities, signed zeros, inexact addition, saved state and public RAM.

The APSR checks establish R0/NZCV and clearingQ. The emulator register API could not seedGE; preservation is inferred from the unchanged MSR APSR_nzcvq instruction. Other arithmetic helpers have caller-clobbered APSR outside their proof. REA ceiling/floor dossiers and a complete stock-matching absolute-value byte read/disassembly support the reconstruction.

One assembly bridge remains because the native fabs core entry exposes its result in both core registers andD0. This needs a separate caller/interface proof.

All915 units compile and compose without failures or duplicate strong symbols. Imports stay86 application/22 boot.904 prior source/object pairs from the intermediate spectral-parent build remain unchanged; the combined parent/math change leaves902 unrelated pairs and the caller object unchanged from the previous accepted build. Source-plan/cache layout are unchanged.

Enabled traps, cold FPU, physical timing, final placement/startup and boot remain unverified. Relocatable composition is not bootable firmware. No paid compiler or byte identity is required.

[Machine-readable evidence](math-selection-intrinsics-c-review.json) records exact results and hashes.
