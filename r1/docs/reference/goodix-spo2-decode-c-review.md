# SpO2 numeric decoding and calibration in C

The [batch-accumulation review](goodix-spo2-batch-c-review.md) adds actual C window accumulation and averaging, with two-window lifecycles and the real frame pipeline. Incomplete-window status3 is preserved. Twelve later processing stages remain unfinished.

`native_spo2_decode.c` implements the522-byte native sample decoder. It preserves signed sample conversion, unsigned16 drives, register-shift behavior, live header reloads and the exact float32/software-double operation order. It uses actual C arithmetic helpers and contains no inline assembly.

One writable30-word object owns the120 nominal TIA calibration bytes at20007d10..20007d88. Cross-table indices stay live. Reserved codes preserve reads from surrounding physical SRAM; neighboring callback state is not copied or owned.

**5,127 stock-versus-C pairs pass**:

- 2,758 direct cases use independent rational float32/float64 oracles and include21 matching faults, output/input/gain-state aliases, signed group arithmetic and byte-range shifts/gains.
- 2,047 core cases execute the actual core, assembler, parity helpers, decoder and polynomial. All522 new decoder bytes and682 core bytes execute.
- 322 frame cases execute the actual frame-to-decoder path, including memory-clear helpers and result publication. R1's fixed chip1/type0 path covers288 decoder bytes; broader cases are covered directly. Public RAM, full active FPSCR, saved registers, stack and masks agree.
- Fourteen compiled defects are rejected. Source cannot execute stock.

The stock startup RW handler and an independent decoder agree on all120 initializer bytes, with two poison patterns and full-region guards. Separately,96 complete stock pow calls establish exact constants for10^3,10^9 and2^17, including clear/set exception flags and every rounding/FZ/DN combination. Only those three fixed calls are replaced.

All **903 R1 units** compile and compose without failures or duplicate strong symbols. The tested object equals the normal object;892 prior nongenerated source/object pairs and source-plan/cache files are unchanged. No new imports are added; application imports fall91 to90, with22 bootloader imports.

Thirteen later processing stages and allocator/free ports remain modeled. Physical sampling/concurrency, cold FPU, reserved-SRAM final layout and full source startup remain unverified. This is relocatable composition, not a complete SpO2 engine or bootable firmware.

[Machine-readable evidence](goodix-spo2-decode-c-review.json) records exact contracts and hashes.
