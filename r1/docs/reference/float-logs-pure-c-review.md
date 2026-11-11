# `logf` and `log10f` without handwritten assembly, 2026-11-10

`r1/src/application/runtime/native_float_logs.c` now expresses its
floating point arithmetic, signed integer conversion and result negation in
C. The zero comparison is a forced C comparison followed by Clang's ARM FPSCR
read intrinsic; it preserves the status bits consumed by the stock branches.
The coefficient and lookup tables, exceptional-input branches and lower
helper calls are unchanged. The normal Clang `-Os` manifest profile compiles
both routines without assembly or an added compiler flag.

The ignored Unicorn fixture under `build/r1-float-logs-c-probe-20261110/`
compares the C object with the SHA-pinned official R1 2.2.6.0009 `logf` and
`log10f` routines at `0x39864` and `0x396e4`. **263,552 paired cases pass**:
22 edge bit patterns, 2,048 seeded arbitrary words and 2,048 normal-range
words per routine, across four rounding modes, FZ/DN settings and two
sticky-flag settings. Returned S0 bits and the full FPSCR match; SP, saved
integer registers and interrupt masks are checked. The fixture binds four
lower math/errno helpers to the stock image, so their source implementations
and physical FPU timing remain outside this comparison. The production
manifest object exactly matches the replayed object's allocated sections
(796 bytes) and 12 relocations.

The R1-only build at `build/sources-r1-float-logs-all-c-20261110/report.json`
compiles 889/889 application and 82/82 bootloader units with no known
failures or duplicate strong symbols. The strict bootloader link is valid.
The strict application link still has 28 unresolved functions and 28,712
bytes of flash overflow. Its current map discards these math sections as
unreachable in the incomplete image, so this conversion does not change the
flash total or establish integrated application execution.
