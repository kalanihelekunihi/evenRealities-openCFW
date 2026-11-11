# `atanf` arithmetic without handwritten assembly, 2026-11-10

`r1/src/application/runtime/native_atanf.c` now expresses its four binary
floating point operations and multiply-add step in C. Its data table,
classification branches and external helper calls are unchanged. The normal
manifest profile compiles the routine with Clang `-Os`; no extra compiler
flag or assembly is used in this unit.

An ignored Unicorn fixture under `build/r1-atanf-c-probe-20261110/` compares
the C object with the SHA-pinned official R1 2.2.6.0009 routine at `0x38774`.
**131,776 paired cases pass** across signed zeros, subnormals, finite values,
infinities, NaNs, 4,096 seeded random words, all four rounding modes, FZ/DN
settings and two sticky-flag settings. Each pair matches the returned S0
bits and full FPSCR; it also verifies SP, saved integer registers and
interrupt masks. The replay binds the three lower classification/math helpers
to the stock image, so their source implementations and physical FPU timing
are outside this comparison. The production manifest object exactly matches
the replayed object's allocated sections (440 bytes) and eight relocations.

The R1-only build at `build/sources-r1-atanf-pure-c-20261110/report.json`
compiles 889/889 application and 82/82 bootloader units with no known
failures or duplicate strong symbols. The bootloader strict link is valid.
The application strict link still has 28 unresolved functions and 28,712
bytes of flash overflow. Its linker map discards the `atanf` section as
unreachable in this incomplete image, so this source change does not alter
that flash total or establish integrated application execution.
