# GX8002 UART boot stage-1 ID-cell and clock-source leaves (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime `0x10000000..0x10002000`).
Prior passes decoded the span (`gx8002-uart-boot-stage1-cd001-analysis.md`)
and closed the arithmetic/noop leaves (`gx8002-uart-stage1-divmod-source.md`:
128 stock bytes), the reset prologue (`gx8002-uart-stage1-reset-source.md`:
48 stock bytes), four PMU trim-bit leaves
(`gx8002-uart-stage1-pmubits-source.md`: 72 stock bytes), and four
polled-UART leaves (`gx8002-uart-stage1-serial-source.md`: 124 stock
bytes). This tranche closes two further leaves as production-routed
reviewed source in the experimental codec candidate: **42 stock bytes
replaced by 40 compiled bytes plus 2 generated fill bytes**.

## Envelopes

| Symbol | Runtime | Package | Stock | Compiled | Kind |
| --- | --- | --- | --- | --- | --- |
| `open_cfw_gx8002_uart_stage1_get_stored_id` | `0x100002BC` | `0x30C` | 12 | 10 | compiled_c |
| `open_cfw_gx8002_uart_stage1_pmu_bit_modify` | `0x10000840` | `0x890` | 30 | 30 | compiled_c |

The getter envelope is 8 bytes of code (`lrw` from a literal pool, `ld.w`,
`rts`) plus its 4-byte pool word (`0x20002008`). A full-span scan shows
that pool word is referenced only by this leaf (one `// 0x100002C4`
reference in the rewrapped disassembly), so the envelope is
self-contained. The C body synthesizes the cell address with
`movi`/`bseti` and needs no pool; it fills 10 of the 12 bytes, hence 2
bytes of generated unreachable fill.

The bit-modify envelope is 30 bytes of straight-line code plus its 2-byte
`bkpt` alignment pad, with no pool and no calls. The compiled C is
additionally byte-identical to the stock envelope (pinned by test), but
admission rests on decoded-trace equivalence like every other tranche.

Behavior, in upstream terms:

- `get_stored_id`: returns the stage-1-local ID word at `0x20002008`
  (chip-revision low nibble stored by the early init routine at
  `0x100001FC`; its only in-image reader is the `bsr` at `0x100001CE`).
- `pmu_bit_modify`: single-bit read-modify-write of `PMU_CFG_SOURCE_SEL0`
  (`0xA001008C`, the clock-source-select register) from a descriptor:
  `word[0]` is the bit index, `byte[4]` is the bit value. The stock
  computes the clear mask with `rotl(0xFFFFFFFE, bit)`; the C expresses
  the same rotation as `(all << bit) | (all >> (32 - bit))`, which this
  toolchain lowers to the identical `rotl` instruction. Both in-range
  callers (`bsr` at `0x10001E28` with `r0 = 0x200024B0`, `bsr` at
  `0x10001E30` with `r0 = r4 + 64`) pass descriptor pointers.

## Provenance

Clean-room MIT C in
`components/shared/gx8002/runtime_gx8002_uart_stage1_idbit.c`, against
the pinned NationalChip grus SDK `arch/soc/grus/include/base_addr.h`
(`PMU_CFG_SOURCE_SEL0`, commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`, blob
`536d2e51e19f12f3a7f4e354fba53be906e05702`; SDK repo-level MIT LICENSE
blob `37a1e362999f2040c2c0cda1a3231b6b5913efbf`; the SDK's own
`boards/.../clock_board.c` reads the same register). Only the numeric
register address and the call/return conventions cross the boundary; the
bodies were written from the decoded stock control flow. The
GPL-licensed SDK headers (`common.h`, `spl/spl.h`) were deliberately not
used: no SDK text is reproduced. See
`NATIONALCHIP-UART-BOOT-STAGE1-IDBIT-NOTICE.txt`.

## Verification

`g2/tools/verify_gx8002_uart_stage1_idbit.py` (report
`docs/research/gx8002-uart-stage1-idbit-verification.json`, 642 cases):

- Compiles the C with `-Os -mcpu=ck804ef -mhard-float -ffreestanding
  -fno-builtin -ffunction-sections -fdata-sections -fno-tree-loop-optimize`,
  links both sections at their runtime entries into one `idbit.elf` with
  no undefined symbols and no relocations; each section fits its stock
  envelope at an aligned package offset.
- The stock span is rewrapped with the CK804EF ELF flags and shifted to
  its runtime base (the `gx8002-uart-boot-stage1-cd001-analysis.md`
  recipe) so decoded addresses are absolute on both sides.
- Decoded-target execution of stock vs linked bodies: identical `r0`,
  identical final memory, identical exact access traces (kind, address,
  width, value of every read/write), descriptor words preserved,
  callee-saved registers preserved, no traffic outside the modeled cells.
- Independent Python oracle on every case: the getter covers 12 cell
  seeds; the modifier covers bit indices 0..31 plus 32/33/63 × values
  {0, 1, 0xFF} × register seeds {0, all-ones, alternating} × 2
  descriptor bases, formulated as a clear-then-set idiom independently of
  the stock rotate instruction.
- `g2/tests/test_gx8002_uart_stage1_idbit.py` (9 tests): host execution
  of both C leaves against redirected cells, interpreter unit checks for
  the new opcodes (`movih`, `rotl`, `and`, `lsl`, `or`, `ld.b`) and the
  stock pool shape, stock-envelope regression, fit/no-relocation
  regression, and the bit-modify byte-identity pin.

Accepted boundary (documented, not verified): shift counts of 32 or more
follow the observed low-5-bit convention pinned by stock/source
agreement on every such case; descriptor/register state outside the
modeled cells is unmodeled. Hardware timing and whole-device behavior
remain unqualified (`hardware_qualified: false`).

## Integration

Registered as `uart-stage1-idbit` in
`tools/build_gx8002_source_candidate.py` (artifact `idbit.elf`, baseline
above) and in the `gx8002-source-candidate` test list in `g2/Makefile`.
`make -C g2 gx8002-source-candidate` currently fails before reaching
this tranche at the pre-existing stale `rtc-init` baseline (checked-in
JSON pins `build_transparent_image.py` sha `eeab8517…`, the unmodified
HEAD file is `dfb2d65e…`; failure exists at HEAD and is left for its
owner). Tranche admission was verified through the builder's exact
`reviewed_replacements` + `compose` path in a private output dir, and
50 candidate/stage-1 tests pass. Once the `rtc-init` baseline is
re-pinned, ownership will split the former `retained_stock` spans at
package `0x30C..0x318` (10 compiled + 2 fill) and `0x890..0x8AE`
(30 compiled, zero fill); the generated
`gx8002-source-candidate-build.{json,md}` and experimental manifest pins
regenerate from that green run, so they are deliberately not hand-edited
here.

## Remains (CD-001, still retained)

CD-001 is now 414/8192 bytes source-owned (128 divmod + 48 reset + 72
pmubits + 124 serial + 42 here). Still retained: vector table
(`0x10000000..0x100000FF`, blocked on unreconstructed trap targets),
init routine (`0x100001BC`), the chip-id/early-UART routine
(`0x100001FC`), the image-receive routine (`0x100002C8`), the baud
computation (`0x100004D0`, two retained lookup callees at `0x10000D98` /
`0x10000EA0`), the configure routine (`0x100005C4`), the checksum helper
(`0x1000065C`, out-of-range callees), the handshake/receive loop, and
everything else up to `0x10002000`. Hardware qualification stays blocked
by unavailable physical evidence.
