# Image-B core entry admission

The separate C-SKY target build `build-gsc-angle-create-admission-round/receipt.json`
contains 227 source units and linked relocatable SHA-256
`f03f66837d9261f511d5b8b2905b1237a9807f525d6da0ba060ea5e5f59ae43b`.
The source snapshot has seven genuine imports. Native entry symbols `0x1000c6e8`
and `0x1000ce14` now bind to their complete C angle and create compositions.
The inherited runtime callback table remains an external RAM contract.

Finite QEMU native/source checks on this exact receipt: angle 10/10, create
2/2, active process 10/10, and the selected product active case through the
new entry symbols 1/1. The corresponding receipts are under `native-oracle-run/`;
all record receipt SHA-256
`7d7ad9f55616bfb436501e5f2909981ca1a8be2ad876f267dbc9696508ae4cfe`.
The ten-case process receipt is preserved as
`active-10case-admission-receipt.json` because the single product case writes
the standard `active-receipt.json` path.

Process core `0x1000d46c` remains a real import. Its sole identified rooted
caller at `0x1000bb58` places `r11` in the fifth stack argument slot and
overwrites the return register at `0x1000bb5e`, so that caller does not observe
the native process return value. The direct process disassembly through
`0x1000dd44` contains no stack access to the forwarded fifth word. The C
experimental composition still has separate ring and energy word pointer
parameters, which need typed linker RAM contracts before native ABI binding.
Neither the finite tests nor the seven-import link establishes final loaded
image placement, hardware FP behavior, or complete product initialization.

## Subsequent process entry binding

`build-gsc-process-ram-binding-round/receipt.json` contains 228 C-SKY source
units and linked SHA-256
`ee7554b1e8273a82aa972892367562c46c4583a0d8d79ddbd8f8f680678afd5c`.
It closes the native process code import while opening explicit external
`gx8002_image_b_process_energy_first_use_2002d79c` and
`gx8002_image_b_process_ring_counter_2002d7a0` RAM symbols. The graph therefore
has eight unresolved names, all data, ambient, or placement contracts. The
fixture maps those two names to their authenticated SRAM addresses with
linker `--defsym`; the source archive itself leaves them unresolved. The
native `0x1000dea0` wrapper still forwards the fifth stack word. Its rooted
call site discards R0, so the source result is void. This does not establish
an ABI for any as yet unidentified indirect consumer.

The bound-core finite QEMU suite now passes all 10 original/source active
cases, including the explicitly seeded two-word prior state. Its receipt is
`native-oracle-run/active-bound-core-receipt.json` and records the 228-unit
source receipt SHA-256
`70255ae46d3b6313d6df23ddc9ec81c5e3b56f11d8e13c3bf8a3f570e923d49d`.
The fixture's `--defsym` addresses are a bounded test placement; a production
loaded-stage linker and startup owner must still establish those RAM symbols.
