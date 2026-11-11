# GXT310 temperature conversion in C

The logic from native `r1_gxt310_temperature_read` at `0x6f600` now lives in
`r1_gxt310_temperature_read_body` in `runtime/native_temperature.c`. A
ten-byte bridge retains the native four-byte scratch word at caller SP-8
and restores the full word into R3 on return. The C body clears that word,
calls the existing transfer provider with `(address, 0, frame, 2)`, ignores
its status, loads the low halfword, reverses its bytes, sign-extends it and
performs the native floating-point calculation.

The C expression retains the separate `0.0078125f` and `1000.0f` multiplies
and signed conversion toward zero. Raw instructions and REA agree on the
native sequence. The compiled body uses actual VFP conversions and both
multiplies; it does not substitute an integer approximation.

The execution probe passed 66,208 stock/C comparisons: all 65,536 halfword
values under default FPSCR, 160 selected edge-value/rounding/flag cases,
and 512 randomized absent, partial, halfword and full-word transfer writes.
Transfer status varies independently and remains ignored. Only the
transfer callback is modeled; floating-point instructions execute in
Cortex-M4 emulation. FPSCR is initialized with architectural VMSR/VMRS
instructions before each case.

Checks compare R0, restored R3, final FPSCR, exact transport arguments and
scratch contents. They verify zero initialization and a halfword load,
callee-saved integer and floating-point registers, SP, interrupt masks,
and eight-byte callback alignment. Native transfer callback SP is caller
SP-8; the C callback uses SP-16 while retaining the buffer at SP-8.

All other temperature function/data sections retain their bytes and
relocation identities; the other 561 source units are unchanged. All 562
R1 units compile without failures or duplicate strong symbols. Manifest
eligibility and import sets remain unchanged at 214 application and 34
bootloader imports. `make sources-check` passes.

The 80-byte C body and ten-byte bridge differ from the native 56-byte
instruction body and eight-byte constant pool. Private C stack frames,
faults, exception/lazy-FPU stacking, physical FPU/sensor operation, bus
timing, final placement/linking, provider qualification and whole-image
byte identity remain unproven. Selected non-default FPSCR tests are not
the full input/mode cross product. No G2 gate or source-plan entry changes.

Exact bindings are in [the machine-readable review](temperature-c-convert-review.json).
