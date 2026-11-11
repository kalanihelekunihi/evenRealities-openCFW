# Spectral wrappers and the real FFT multiply-subtract correction

`native_spectral_prepare.c` implements the 192-byte prepare wrapper and 48-byte copy wrapper in ordinary C. The fixture executes the actual C allocator, resize/free, FFT, memory, packed 5/10 conversion and encoded math helpers. Fatal/platform guards are never called. No writable owner or assembly is added.

**1,377 stock/C wrapper scenarios pass:** 1,352 matrix cases, 16 independent DFT-prefix cases and nine positive control-baseline cases. All 240 newly owned instruction bytes execute. Twelve compiled wrapper defects are rejected. Full public RAM, FPSCR, saved registers, SP and masks agree.

The new legacy copy cases exposed a NaN-sign error in the existing real FFT core. Stock VMLS negates the rounded product before addition; plain subtraction is different for selected NaNs. Four C sites now use the correct operation sequence. The corrected production object passes 3,139 FFT scenarios, including 577 independent oracles, and the shared arithmetic sequence passes 262,144 isolated VMLA/VMLS comparisons across 32 FP mode/status combinations. The previously failing 16-point special-value copy now matches.

Wrapper cases cover raw/packed inputs, normalization on/off, existing/new output, wilderness/exact/oversized/split heap shapes, boundary lengths and selected legacy non256 calls. Exact reuse exposes the following heap header value 1036 to the second mirrored-tail read. The compatibility port preserves the native allocation request and live reads; safe padding remains an improvement opportunity after caller integration.

Normalization visits every transform word before trimming. Existing output copies then frees scratch; empty output resizes and publishes it. The copy wrapper exposes legacy incoming-R9 coefficients as a ninth C argument. This is a deliberate C interface change; 256-point transforms own their coefficients.

All 912 R1 units compile and compose without failures or duplicate strong symbols. The tested wrapper and corrected FFT objects equal the normal build. The other 900 prior nongenerated source/object pairs are unchanged. Imports remain 87 application/22 boot. Source-plan and cache layout remain unchanged.

Mapped output300 stress cases preserve observed growth/copy effects beyond useful bins. Arbitrary malformed inputs/aliases, allocation failure, cold FPU, concurrency, physical IRQ/timing, stack budget, startup/layout, sensors and boot remain unverified. Peak/harmonic dependencies, the spectral parent and ten top-level processing boundaries remain open. Relocatable composition is not bootable firmware.

[Machine-readable evidence](goodix-spectral-prepare-c-review.json) records contracts, exact results and hashes.
