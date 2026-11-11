# STACMD recovery delay in C

`r1/src/application/board/native_stacmd_delay.c` now uses the Arm Clang
`__builtin_arm_nop()` intrinsic in ordinary C. The old inline assembly loop
made 209 iterations of four NOPs plus increment, compare and conditional
branch. Under the manifest's Clang `-Os` profile, five intrinsic NOPs compile
to a rotated decrement loop. Both compiled functions occupy 20 bytes and
execute the same 1,466 instruction addresses per call: 209 iterations of
seven instructions, plus entry, zero return and branch to caller. The fifth
NOP accounts for the compare removed by the compiler's countdown loop.

The ignored probe at `build/r1-stacmd-delay-pure-c-20261111/verify.py`
emulates the prior source object and the actual newly compiled manifest
object on a Cortex-M4. It checks the entire dynamic PC trace, return value,
APSR and stack pointer. This is instruction-count and register evidence; it
does not measure physical GPIO pulse widths, flash wait-state effects or
peripheral timing on an R1 board.

The STACMD transmit and receive pulse waits now use four of the same C
intrinsics per iteration. The actual manifest objects differ from their prior
objects at only two 16-bit instructions in each function: Clang moves the
decrement between the NOPs. All other function bytes are unchanged. The
ignored `build/r1-stacmd-pulse-intrinsics-20261111/verify_pulses.py` probe
compares the old and new compiled loop traces for transmit counts 13 and 52
and receive count 26. PC trace, loop result and APSR agree. Each iteration
still has six 16-bit instructions. Physical wire timing is not yet measured.

`build/sources-r1-stacmd-pulse-intrinsics-20261111/report.json` compiles all
944 application and 82 bootloader units with no failures or duplicate strong
symbols. The strict bootloader receipt
`build/r1-boot-link-stacmd-pulse-intrinsics-20261111/report.json` links and has a
valid vector. The strict application receipt
`build/r1-link-stacmd-pulse-intrinsics-20261111/report.json` remains at nine
undefined functions and 653,880/696,320 flash bytes. These changes replace
three handwritten assembly sites; 26 R1 C files still contain inline assembly or
register-bound assembly syntax.
