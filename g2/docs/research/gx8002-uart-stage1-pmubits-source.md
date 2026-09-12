# GX8002 UART boot stage-1 PMU trim-bit leaves (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime `0x10000000..0x10002000`).
Prior passes decoded the span (`gx8002-uart-boot-stage1-cd001-analysis.md`),
closed three arithmetic/noop leaves as reviewed C
(`gx8002-uart-stage1-divmod-source.md`: 128 stock bytes), and closed the
reset prologue as reviewed assembly
(`gx8002-uart-stage1-reset-source.md`: 48 stock bytes). This tranche closes
four PMU register leaves as production-routed reviewed source in the
experimental codec candidate: **72 stock bytes replaced by 72 compiled
bytes, zero fill**.

## Envelopes

| Symbol | Runtime | Package | Stock | Compiled | Kind |
| --- | --- | --- | --- | --- | --- |
| `open_cfw_gx8002_uart_stage1_pmu_set_bit0` | `0x10000374` | `0x3c4` | 24 | 24 | compiled_c |
| `open_cfw_gx8002_uart_stage1_pmu_set_bit1` | `0x1000038c` | `0x3dc` | 24 | 24 | compiled_assembly |
| `open_cfw_gx8002_uart_stage1_pmu_get_bit0` | `0x100003a4` | `0x3f4` | 12 | 12 | compiled_c |
| `open_cfw_gx8002_uart_stage1_pmu_get_bit1` | `0x100003b0` | `0x400` | 12 | 12 | compiled_c |

All four operate on the PMU power-on-reset register 1 (OSC trim state) at
`0xA0010030`. The set leaves implement a clear, re-read, OR-back sequence
(clear the target bit, re-read the register, OR in the new bit value);
other bits of this register carry live hardware state, so the re-read is
behavior, not redundancy. The set_bit1 input convention takes the boolean
in bit 0 (`lsli r0, r0, 1` before masking with 2); the observed in-range
callers (`bsr` at `0x1000137e`/`0x10001384` with `r0 = 0`) clear both bits.
The get leaves return bit 0 (`andi`) and bit 1 (`zext r0, r0, 1, 1`).

## Provenance

Clean-room MIT C in
`components/shared/gx8002/runtime_gx8002_uart_stage1_pmubits.c` (three
leaves) plus clean-room MIT assembly in
`components/shared/gx8002/runtime_gx8002_uart_stage1_pmusbit.S` (set_bit1),
against the pinned NationalChip grus SDK register definition
`PMU_CFG_POWER_ON_RESET_REG1 (GX_REG_BASE_PMU_CONFIG + 0x30)` in
`arch/soc/grus/include/base_addr.h` at commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5` (MIT; see
`NATIONALCHIP-UART-BOOT-STAGE1-PMUBITS-NOTICE.txt`). Only the register
address and bit positions cross the boundary; no SDK text is reproduced.

Assembly was used for exactly one leaf: this toolchain lowers the
bit-clear to a 4-byte `andni`, so every probed C shape for set_bit1
compiles to 26 bytes against a 24-byte stock envelope that only fits the
2-byte `bclri` the stock (older NationalChip) toolchain emitted. The
assembled set_bit1 bytes are additionally byte-identical to the stock
envelope (pinned by test), but admission rests on decoded-trace
equivalence like every other tranche.

## Verification

`g2/tools/verify_gx8002_uart_stage1_pmubits.py` (report
`docs/research/gx8002-uart-stage1-pmubits-verification.json`, 308 cases):

- Compiles the C with `-Os -mcpu=ck804ef -mhard-float -ffreestanding
  -fno-builtin -ffunction-sections -fdata-sections -fno-tree-loop-optimize`,
  assembles the `.S` with `-mcpu=ck804ef -mhard-float`, links both with
  `ld -r` into one `pmubits.o`; each section fits its stock envelope at an
  aligned package offset with no undefined symbols and no relocations.
- Decoded-target execution of stock vs compiled bodies with the PMU
  register modeled as stateful MMIO (reads return current value, writes
  update it) across 14 register states x 10 inputs for each setter
  (140 cases each) and 14 register states for each getter: identical final
  register values and identical exact access traces
  (`read,write,read,write` for setters; single `read` for getters),
  callee-saved registers preserved, no traffic outside `0xA0010030`.
- Independent Python oracle for final values and traces on every case.
- `g2/tests/test_gx8002_uart_stage1_pmubits.py` (8 tests): host execution
  of the C leaves against a redirected register, interpreter unit checks
  for the new opcodes, stock-envelope regression, fit/no-relocation
  regression, and the set_bit1 byte-identity pin.

Accepted boundary (documented, not verified): the void set leaves leave
different scratch in `r0` (stock folds its OR there; the source keeps the
argument), so `r0` is caller-clobbered scratch for setters and is not
compared — consistent with the scratch tolerance used for admitted
image-A/B functions. The PMU register is modeled with no external
concurrent updates. Hardware timing and whole-device behavior remain
unqualified (`hardware_qualified: false`).

## Integration

Registered as `uart-stage1-pmubits` in
`tools/build_gx8002_source_candidate.py` (artifact `pmubits.o`, baseline
above). `make -C g2 gx8002-source-candidate` and
`make -C g2 codec-source-experimental` pass; ownership splits the former
`retained_stock` span at package `0x3c4..0x40c` into three `compiled_c`
sections plus one `compiled_assembly` section with no fill.

## Remains (CD-001, still retained)

CD-001 is now 248/8192 bytes source-owned (128 divmod + 48 reset + 72
here). Still retained: vector table (`0x10000000..0x100000ff`, blocked on
unreconstructed trap targets), init routine (`0x100001bc`), baud
computation (`0x100004d0`, two retained lookup callees), polled UART
TX/RX leaves (`0x10000584`, `0x100005a0`, `0x10000620`, `0x10000640`),
status getters, the handshake/receive loop, and everything else up to
`0x10002000`. Hardware qualification stays blocked by unavailable physical
evidence.
