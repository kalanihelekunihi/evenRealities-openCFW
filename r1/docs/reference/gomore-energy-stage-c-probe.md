# R1 energy updater C integration, 2026-11-10

Stock `0x5f56c` is now bound by
`r1/src/application/runtime/native_gomore_energy_update.c` to the shared
`gomore_primitives_energy_update` implementation and source-owned C math.
The binding passes the control byte from pointer offset `+1`, as shown by
the stock `ldrsb` at `0x5f74a`.

Stock state offset `0x58` holds a pointer to a reference record. The routine
reads and writes the float at record offset `+4`; the shared state now
represents that pointer. The shared energy formulas now use the clamped
normalized position in variant two modes 1, 2, 4 and 5, retain the initial
dispatch rate in variant two mode 3, and use the stock `vnmls` blend factor
`metric * 0.25 - 0.5`.

The ignored Cortex-M4 probes in `build/r1-energy-stage-20261110/` link the
actual manifest Clang math and shared-primitive objects with a provisional
adapter. Full return values, the 92-byte state, 44-byte output and reference
record match stock in all 96 controlled cases, 800 varied cases, and 500
cases with populated history, counters, blend and accumulator state. These
1,396 comparisons exercise all six modes and three variants, but they do not
establish behavior for every reachable state, integration with sensors, or
physical energy accuracy.

`./make.sh sources-check` passes: 980 R1 units from 767 source files, none
unbuilt. The source build receipt is
`build/sources-r1-energy-update-c-20261110/report.json`: all 898 application
and 82 bootloader units compile and compose with no duplicate strong symbols.
The strict bootloader receipt at
`build/r1-boot-link-energy-update-c-20261110/report.json` passes with a valid
512-byte C vector. The strict application receipt at
`build/r1-link-energy-update-c-20261110/report.json` still fails with 20
unresolved functions; it reports 626,408 of 696,320 flash bytes used and no
overflow. This is one closed import, not a complete application executable.
