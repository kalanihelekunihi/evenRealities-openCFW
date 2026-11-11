# Native harmonic grouping in C

`native_spectral_harmonic.c` implements the grouping function at `0x35850` and its shared tail at `0x35c78`. Its 1,162 instruction bytes span two ranges separated by a 56-byte literal pool. All instructions execute in the fixture. No writable state, coefficient array or assembly is added.

**5,329 stock/C scenarios pass:** 3,744 matrix cases, 1,312 independent signal/metamorphic oracles, 256 caller-count cases and 17 positive control-baseline cases. Twelve compiled arithmetic/resource deviations are rejected. Tests execute actual C heap, memory and math helpers, including all six allocations and ordered frees; no algorithm boundary is modeled.

Independent checks cover empty inputs, exact harmonic series, a stronger isolated interferer, zero weighting, nonpositive/unordered amplitudes, 128 amplitude-scaling pairs and caller peak counts two/four. Full public RAM, FPSCR, saved registers, SP and masks match. Actual allocation/free/sqrt call inputs and order also match.

The source preserves encoded-double predicates, signed raw-float-bit limits, nearest-distance amplitude ties, wrapped arithmetic, guarded SDIV, octave suppression and early termination. VMLS and VNMLS require distinct operation sequences. The latter is independently checked by 131,072 primitive instruction pairs across 32 FP mode/status settings.

A targeted case suppresses the final base. Skipping its last amplitude comparison leaves a different FPSCR on return even though output buffers match. The compiled control catches that difference. Suppression cases use real input peaks instead of fabricated internal-entry register state.

The parent uses three harmonics and at most five peaks. The allocator's minimum eight-byte payload keeps the internal fourth flag byte mapped and zero for that observed three-byte request. Related cases through six harmonics cover the otherwise unused suppression logic.

All 914 R1 units compile and compose without failures or duplicate strong symbols. The tested object equals normal build; 903 prior nongenerated source/object pairs remain unchanged. Imports stay 87 application/22 boot. Source-plan and cache layout remain unchanged.

Malformed inputs, heap exhaustion, enabled traps, cold FPU, concurrency, physical IRQ/timing, stack budget, final startup/layout, sensors and boot remain unverified. The spectral parent, ten later processing boundaries and other hardware support remain open. Relocatable composition is not bootable firmware.

[Machine-readable evidence](goodix-spectral-harmonic-c-review.json) records contracts, exact results and hashes.
