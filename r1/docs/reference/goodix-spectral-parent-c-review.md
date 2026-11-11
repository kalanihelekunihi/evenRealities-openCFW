# Native SpO2 spectral parent in C

The parent at`0x766ac` now connects the real source-owned rolling buffer, allocator, quartile mask, cleanup/window, FFT, peak and harmonic stages in ordinary C. It adds no assembly or writable state. Its shared typed header also corrects the caller declaration; the caller object stays unchanged.

**3,268 native/C scenario pairs pass**, including768 independent signal/DFT oracles,4 positive control cases and64 final normal-product pipeline pairs. Twelve compiled defects are rejected. Checks compare public RAM, FPSCR, saved registers, SP/masks, ordered calls and live stage snapshots across all256 descriptor bytes,32 FP mode/status settings, two heap shapes and real125/128-sample constructor/push sequences.

Of478 native instruction bytes,470 execute. The remaining eight belong to capacity>=125 arms; the actual fixed ceiling calculation returns53 in every tested FP setting. Integer rounding and a separate constant-result proof establish why these arms are unreachable. No fabricated helper outputs are used.

Independent analytic window checks account for the native coefficient approximation. Direct DFT checks use the live125-sample window padded to256 and unnormalized magnitudes. The actual C heap and algorithm providers execute throughout. Existing transitive math providers still have some assembly. The FFT wrapper retains its observed tail-read behavior for a separate safety improvement.

All915 R1 units compile and compose without failures or duplicate strong symbols. Application imports fall87 to86; boot imports remain22.902 prior source/object pairs remain unchanged, with an intentional math-provider conversion and one interface-only caller change whose object is unchanged. Production and probe executable sections/relocations match; only their ELF source-file name strings differ. Source-plan/cache layout are unchanged.

Nine later SpO2 stages, malformed-input/fatal paths, enabled traps, cold FPU, physical timing/sensors, final startup/layout and boot remain open. Relocatable composition is not bootable firmware. No paid compiler or byte identity is required.

[Machine-readable evidence](goodix-spectral-parent-c-review.json) records contracts, results and hashes.
