# `atan2f` arithmetic without handwritten assembly, 2026-11-10

`r1/src/application/runtime/native_atan2f.c` now uses C for addition,
subtraction, multiplication, division, multiply-add, multiply-subtract and
negation. Its input classification, quadrant logic, data table and external
helper calls are unchanged. The normal Clang `-Os` manifest profile compiles
the unit without an extra flag or assembly.

The ignored Unicorn fixture under `build/r1-atan2f-c-probe-20261110/`
compares the C object with the SHA-pinned official R1 2.2.6.0009 routine at
`0x384c8`. **212,096 paired cases pass**: the Cartesian product of 22 edge
bit patterns for both inputs, 4,096 seeded arbitrary pairs, 2,048 normal
range pairs, four rounding modes, FZ/DN settings and two sticky-flag settings.
Returned S0 bits and full FPSCR match. SP, saved integer registers and
interrupt masks are checked. The replay binds four lower helper calls to the
stock image, so their source implementations and physical FPU timing remain
outside this comparison. The production manifest object exactly matches the
replayed object's allocated sections (824 bytes) and 18 relocations.

The R1-only build at `build/sources-r1-atan2f-pure-c-20261110/report.json`
compiles 889/889 application and 82/82 bootloader units with no known
failures or duplicate strong symbols. The bootloader strict link is valid.
The application strict link still has 28 unresolved functions and 28,712
bytes of flash overflow. Its map discards the `atan2f` section as unreachable
in this incomplete image, so the current flash total is unchanged.
