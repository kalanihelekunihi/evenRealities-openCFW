# Powf signaling zero comparison in C, 2026-11-10

`native_powf_core.c` now computes the VCMPE-with-zero FPSCR result in C using
the same bit-level policy as the existing powf dispatcher: FZ input flushing,
input-denormal and invalid cumulative flags, and NZCV for finite values,
zeros, infinities and NaNs. Clang's Arm FPSCR get/set intrinsics make the
architectural status write explicit. The reduced powf core has no remaining
inline assembly.

An ignored fixture at `build/r1-powf-zero-c-20261110/verify_zero.py` calls the
normal-profile C helper and an instruction-level VCMPE/VMRS oracle in the
same linked emulator. **33,344** paired raw binary32 values and 32 FP modes
match in returned carry and complete FPSCR. The C core also passes **4,224**
stock/C powf dispatcher cases and **2,048** normal-range cases with the
existing dispatcher fixture, comparing result bits, FPSCR, public RAM and
saved ABI state. The oracle's assembly is confined to the ignored probe.

The normal source build at `build/sources-r1-powf-zero-pure-c-20261110/report.json`
compiles all 975 R1 units without failures or duplicate strong symbols.
`make sources-check` and the strict bootloader link pass. The incomplete
application link still has 24 undefined functions and 28,424 bytes of full
flash overflow, 96 bytes above the preceding checkpoint. This does not prove
all input behavior, physical hardware timing, final linkage or byte identity.
