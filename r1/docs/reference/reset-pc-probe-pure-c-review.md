# R1 reset trace PC probe in C

`r1/src/application/runtime/native_reset_writer.c` now implements
`r1_reset_trace_program_counter_probe` with a C label address. The stock
two-instruction leaf reads PC at its entry and returns entry plus four. The C
function has eight-byte entry alignment, so setting bit 2 of its label address
and clearing the Thumb function-pointer bit yields the same relative address.
This records the location of the relocated source function, which is what the
reset trace needs after a source rebuild. It retains no stock executable bytes.

The actual Arm Clang `-Os` object uses a relocated literal load, `ORR`, `BIC`,
and `BX LR`. None of those instructions changes APSR. The ignored probe in
`build/r1-reset-pc-probe-pure-c-20261111/verify.py` links both the previous
and new production objects at `0x1000` and executes nine initial APSR cases
under Cortex-M4 emulation. Return `0x1004`, R1–R12, SP, LR, and NZCVQ match in
all cases. The current strict application map places the new entry at
`0xBD3F8`, divisible by eight. A different linker placement must retain this
alignment. The new body occupies 16 flash bytes versus the old four.

`build/sources-r1-reset-pc-probe-pure-c-20261111/report.json` compiles all
945 application and 82 bootloader units with no failures or duplicate strong
symbols. `build/r1-boot-link-reset-pc-probe-pure-c-20261111/report.json` links
the bootloader and validates its C vector. The application receipt
`build/r1-link-reset-pc-probe-pure-c-20261111/report.json` still has
eight unresolved application functions and uses 658,744 of 696,320 flash
bytes, with no overflow. This changes only the reset trace's internal PC
record; full reset and hardware behavior remain unverified.
