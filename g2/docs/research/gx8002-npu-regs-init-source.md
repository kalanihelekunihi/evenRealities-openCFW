# GX8002 NPU register initialization recovery

The stock function at package 0xeedc / runtime 0x10205950 performs six calls,
reloading the driver register pointer at 0x20027914 before every call:

| Helper | Argument |
| --- | ---: |
| npu_set_clock_gate | 1 |
| npu_set_idle_cycle | 2000 |
| npu_set_idle_mode | 0 |
| npu_clr_interrupt | 111 |
| npu_en_interrupt | 109 |
| npu_set_overtime_thr | 1048576 |

The authenticated pinned SDK `snpu.o` names the routine `npu_regs_init` and
identifies these call targets. The source references only the observed pointer
slot as an external volatile object. This does not claim understanding or
ownership of the other driver state. It preserves the live pointer reads;
combining them into one snapshot would change behavior when helpers mutate
that slot.

Native macOS C-SKY compilation produces 64 bytes including its literal pool,
within the original 76-byte envelope. Source compilation and decoded stock
execution are compared against the explicit table above, with pointer changes
after each helper, caller clobbers, exact arguments, and eight-byte frame.
Qualification passes 888 cases and eight tests. Pointer encodings are tested
as forwarded bits, not asserted to denote valid devices. Helper internals have
separate qualification; this wrapper evidence is not physical MMIO validation.

The source, builder, verifier, and tests use the `npu_regs_init` name. Reviewed
report: `gx8002-npu-regs-init-verification.json`. It is registered in the integrated build. Admission artifact name is `npu-regs-init.elf`.
