# GX8002 UART boot stage-1 div/mod/noop leaves (CD-001)

Work item CD-001, package `0x000050..0x002050` (runtime `0x10000000..0x10002000`).
Prior pass (`gx8002-uart-boot-stage1-cd001-analysis.md`) decoded the span and
mapped its routines with zero source admission. This tranche closes three
leaf envelopes as production-routed reviewed C in the experimental codec
candidate: **128 stock bytes replaced by 88 compiled bytes + 40 fill bytes**.

## Envelopes

| Symbol | Runtime | Package | Stock | Compiled | Kind |
| --- | --- | --- | --- | --- | --- |
| `open_cfw_gx8002_uart_stage1_udiv` | `0x1000013c` | `0x18c` | 66 | 46 | compiled_c |
| `open_cfw_gx8002_uart_stage1_umod` | `0x10000180` | `0x1d0` | 58 | 40 | compiled_c |
| `open_cfw_gx8002_uart_stage1_clear_bss` | `0x10000138` | `0x188` | 4 | 2 | compiled_c |

The two arithmetic leaves are the hand-split unsigned divide/remainder pair
called (with the `r0` dividend / `r1` divisor convention) by the baud-rate
divisor computation; the 4-byte envelope is a bare `rts` plus its `bkpt`
alignment pad, called once from the stage-1 init (`bsr` at `0x100001ca`).

## Provenance

Clean-room MIT C in
`components/shared/gx8002/runtime_gx8002_uart_stage1_divmod.c`, implementing
the restoring-division algorithm identified in the pinned NationalChip grus
SDK (`arch/soc/grus/spl/spl.c`, `uint32_divmodsi4`/`uint32_div`/`uint32_mod`,
commit `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`, GPL-2.0+). No SDK text is
reproduced: the GPL file stays outside the tree and only the algorithm plus
the commit reference cross the boundary. The `clear_bss` placeholder matches
the position and bare-`rts` body of upstream `spl_start.S` `spl_clear_bss`
(MIT, same commit); no BSS-clearing behavior is claimed for it.

## Verification

`g2/tools/verify_gx8002_uart_stage1_divmod.py` (report
`docs/research/gx8002-uart-stage1-divmod-verification.json`, 16,550 cases):

- Compiles with `-Os -mcpu=ck804ef -mhard-float -ffreestanding -fno-builtin
  -ffunction-sections -fdata-sections -fno-tree-loop-optimize`; each section
  fits its stock envelope at an aligned package offset with no undefined
  symbols and no relocations.
- Decoded-target execution of stock vs compiled bodies across 8,273
  dividend/divisor pairs each (exhaustive `0..64 x 0..64`, 32-bit edges,
  powers-of-two neighborhoods, 2,048 seeded randoms, divide-by-zero edges):
  identical `r0` results, callee-saved registers preserved, zero memory
  traffic on both sides.
- Independent Python oracle (`//`/`%` with the stock divide-by-zero
  convention: div returns 0, or 1 for `0/0`; mod returns the dividend):
  both implementations match on every case.
- Stub: stock and source both return immediately with the full register file
  preserved over four probe pairs.

Accepted boundary (documented, not verified): scratch registers `r1-r3` and
the condition flag are caller-clobbered across the internal `bsr` boundary
and are not compared — consistent with the scratch-renaming tolerance used
for admitted image-A/B functions. Hardware timing and whole-device behavior
remain unqualified (`hardware_qualified: false`).

## Integration

Registered as `uart-stage1-divmod` in `tools/build_gx8002_source_candidate.py`
(artifact `divmod.o`, baseline above). `make -C g2 gx8002-source-candidate`
and `make -C g2 codec-source-experimental` pass; ownership splits the former
`retained_stock` span at package `0x188..0x20a` into three `compiled_c`
sections plus `generated_unreachable_fill` (the stock `bkpt` pads are zero
halfwords, so fill bytes are envelope-identical).

## Remains (CD-001, still retained)

Vector table (`0x10000000..0x100000ff`, derivable from three addresses but
pointing at unreconstructed trap targets), reset prologue (`0x10000100`,
calls out-of-range `0x10002900`), init routine (`0x100001bc`, five retained
callees), baud computation (`0x100004d0`), UART handshake/receive loop, and
everything from `0x1000020a` to `0x10002000`. The receive loop likely spans
into CD-002; coordinate placement before reconstructing further callers.
Hardware qualification stays blocked by unavailable physical evidence.
