# Native maximum/index and peak selection in C

`native_spectral_peaks.c` implements the 46-byte maximum/index helper and 334-byte peak selector in ordinary C. It adds no writable state, coefficient data or assembly. Actual C memmove executes; no algorithm boundary is modeled.

**6,840 stock/C scenarios pass:** 5,464 matrix cases, 1,360 independent finite oracles and 16 positive control-baseline cases. Twelve compiled defects are rejected. One malformed shift causes an unmapped read, detected by a narrow invalid-access guard; the other eleven change state or output.

All 378 reachable native instruction bytes execute. Conservative CFG propagation proves the remaining two-byte branch unreachable from normal entry with returning callees: R3 is always one at its CBZ. The proof keeps other condition flags unknown and treats calls as clobbering R3.

The tests include 640 sensor-caller and related cases using 53 bins, five peak slots, begin5/end53, threshold0.1 and radius1/2. The current parent window factor gives radius2. Other cases cover bounded/empty scans, counts1..125, capacity/radius boundaries, special values, all 32 tested FP mode/status combinations and selected input/index/value/count overlaps. Full public RAM, FPSCR, saved registers, SP and masks agree. Source execution cannot enter stock code.

Finite oracles preserve first maximum ties, radius skipping, stable equal insertion, gathered values and the native capacity quirk: a full list can replace its final slot with a lower candidate. This is not ordinary global top-K selection. Maximum reads its first sample unconditionally; count must be positive.

All 913 R1 units compile and compose without failures or duplicate strong symbols. The tested object equals normal build. All 902 prior nongenerated source/object pairs are unchanged. Imports remain 87 application/22 boot; source-plan and cache layout are unchanged.

Malformed bounds/capacities/pointers, arbitrary aliases, cold FPU, enabled FP traps, physical IRQ/timing, stack budget, startup/layout, sensors and boot remain unverified. Harmonic grouping, the spectral parent, ten top-level processing boundaries and other hardware support remain open. Relocatable composition is not bootable firmware.

[Machine-readable evidence](goodix-spectral-peaks-c-review.json) records contracts, exact results and hashes.
