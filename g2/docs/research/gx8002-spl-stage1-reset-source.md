# GX8002 image-A SPL stage-1 reset chain and body pad

Work item CD-008 (package `[0x0000958C, 0x0000B58C)`, 8,192 bytes). Status:
**partial**. 3,747 of those bytes (45.7%) are now reviewed source (either
compiled from a pinned public upstream match or generated container/format
data); the remaining 4,445 bytes (`spl_board_init_r` and whatever it calls)
are unchanged and still an opaque, externally-supplied span.

## What this closes

`gx8002-image-a-sram-stage1-boundaries.md` (Wave 5) treated the whole
12,288-byte image-A BINH stage-1 block (package `[0x0000958C, 0x0000C58C)`)
as one opaque span behind a single `authenticated_segment_load` typed
provider (`runtime_gx8002_image_a_stage1_boundary.c`), because "the header
load field and vector-address space do not alone prove the complete ROM
copy/remap behavior."

Disassembling the block's actual bytes (via `csky-unknown-elf-objdump` on a
`csky-unknown-elf-objcopy -I binary -B csky`-wrapped copy of the codec image,
with `e_flags` patched to `0x21006009` so the CK804EF/ABIv2 instruction set
decodes correctly — the same technique `compare_gx8002_platform_gate.py`
already uses on this same image) shows the block is not uniformly opaque:

- `[0x0000958C, 0x0000968C)` (24 + 256 = 280 bytes): the public 24-byte BINH
  header immediately followed by the 64-word C-SKY vector table.
- `[0x000096A4, 0x000096DA)` (54 bytes): the reset entry, its 3-word literal
  pool, the default trap handler, and an unreachable `rts` stub — an
  **exact, byte-for-byte match** (once configuration/link addresses are
  substituted for the immediates) for NationalChip's public MIT-licensed
  `lvp_kws` SDK, `arch/cpu/csky/ck804/spl_start.S`,
  `spl_reset_handler`/`spl_default_handler`/`spl_clear_bss`, commit
  `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5` (the same commit already pinned
  for `runtime_gx8002_reset_entry.S`). The match is conclusive, not
  approximate: the reset handler's second call target, resolved purely from
  the stock bytes' own PC-relative `bsr` encoding, is `0x10023500` — exactly
  the package address this repository's own `open_cfw_gx8002_reset_entry`
  (the already-source-owned stage-two entry, see
  `gx8002-reset-and-main-source.md`) is placed at. The SPL stage boots
  straight into the already-reconstructed stage-two entry.
- `[0x000096DA, 0x0000A837)` (4,445 bytes): dense, varied code — this is
  `spl_board_init_r` (the SDK's board-bring-up hook, called from the reset
  handler before the stage-two entry) and whatever it calls. **Not**
  reconstructed by this item; still `retained_stock` behind the existing
  `runtime_gx8002_image_a_stage1_boundary.c` typed boundary.
- `[0x0000A837, 0x0000B58C)` (3,413 bytes, this item's remaining range): a
  contiguous run of zero bytes — the tail of a longer zero run that
  continues past this item's own upper bound into CD-009's own item
  (`gx8002-image-a-stage1-tail-source.md` independently found and
  reconstructed `[0x0000B58C, 0x0000C588)` as the same run's remainder).
  Confirmed directly against the authenticated stock image (byte `0xA836` is
  `0xFF`; every byte from `0xA837` through `0xB58B` is `0x00`), not assumed.

### Byte accounting for this item's range

| Package range | Size | Content | Disposition |
|---|---:|---|---|
| `[0x0000958C, 0x0000968C)` | 280 B | BINH header + 64-word vector table | now `generated_source_data` |
| `[0x0000968C, 0x000096A4)` | 24 B | padding to the reset entry's `0x10000100` alignment | **unchanged**, `retained_stock`* |
| `[0x000096A4, 0x000096DA)` | 54 B | SPL reset entry + literal pool + default handler + clear_bss stub | now `compiled_assembly` |
| `[0x000096DA, 0x0000A837)` | 4,445 B | `spl_board_init_r` and callees | **unchanged**, still `retained_stock` |
| `[0x0000A837, 0x0000B58C)` | 3,413 B | trailing zero-fill inside the stage-1 block | now `generated_source_data` |

\* The vector table (`[0x958C+0x18, 0x958C+0x118)`) is itself 256 bytes
ending exactly at `0x958C+0x118 = 0x96A4`, where the reset entry begins; the
280-byte header+vector span above already accounts for it in full. There is
no separate 24-byte gap in the real layout — the row exists in this table
only to make the two `[..)` ranges add up to 8,192 without a silent seam;
`0x968C` is inside the vector table (word 32 of 64), not a boundary. See
`Implementation` below for the actual, non-overlapping replacement ranges
(`[0x0000958C, 0x0000968C)` is corrected to `[0x0000958C, 0x000096A4)` by
the 280-byte span, which already reaches `0x96A4`).

## Implementation

- `components/shared/gx8002/runtime_gx8002_image_a_stage1_header.[ch]`: a
  280-byte packed struct (`magic`, `medium`, `version`, `stage2_size`,
  `stage1_block_size`, `stage1_load_address`, `vectors[64]`) placed in
  `.rodata.open_cfw_gx8002_image_a_stage1_header`. The struct fields are
  public BINH format (see `tools/analyze_g2_codec_fwpk_segments.py`
  `parse_binh_image`, which reads the identical `<4sIIIII` layout); the two
  vector values are `&open_cfw_gx8002_spl_reset_entry` and
  `&open_cfw_gx8002_spl_default_handler` — this repository's own symbols,
  not literals, so the vector table always points at whatever this build
  actually links at those addresses.
- `components/shared/gx8002/runtime_gx8002_spl_reset_entry.S`: derived from
  `spl_start.S` (see `NATIONALCHIP-SPL-STARTUP-NOTICE.txt`), adapted the
  same way `runtime_gx8002_reset_entry.S` adapts `start.S` — source symbols
  (`open_cfw_gx8002_spl_vectors`, `open_cfw_gx8002_spl_initial_stack`,
  `open_cfw_gx8002_spl_board_init_r`, `open_cfw_gx8002_reset_entry`) replace
  configuration/link addresses, resolved by the build's own linker script,
  not embedded as opaque bytes.
- `components/shared/gx8002/runtime_gx8002_image_a_stage1_body_pad.[ch]`: a
  3,413-byte all-zero `const` array in
  `.rodata.open_cfw_gx8002_image_a_stage1_body_pad`.
- `tools/build_gx8002_spl_reset_candidate.py`: compiles both the header/data
  translation unit and the assembly translation unit, links them with one
  linker script that places the vector table's targets at their real
  addresses (`0x10000100`/`0x10000130`) and pins `spl_board_init_r`
  (`0x10000acc`, retained) and the stage-two entry (`0x10023500`, already
  source-owned) as external symbols, and requires both compiled sections to
  be byte-exact against the stock image with zero leftover relocations.
- `tools/verify_gx8002_spl_reset_entry.py`: independently recomputes the
  280-byte header+vector span from `analyze_g2_codec_fwpk_segments.py`'s own
  authenticated `parse_fwpk`/`parse_main_image` (cross-checking the header's
  soft version against the FWPK container version, and the block/DRAM
  constants against the analyzer's own `STAGE1_BLOCK`/`DRAM_BASE`), then
  decodes the linked candidate's own disassembly and drives it through a
  small C-SKY interpreter that checks the exact PSR/CR31/VBR writes and the
  two call targets/stack-pointer value against an independent oracle, across
  36 CR31 inputs and 3 register-seed spreads (108 cases). It explicitly does
  **not** model any effect of `spl_board_init_r` itself (see Limits).
- `tools/verify_gx8002_image_a_stage1_body_pad.py`: compiles the pad source,
  independently confirms the assumed span is all-zero in the stock image,
  and requires the compiled bytes to match.
- `tests/test_gx8002_spl_reset_entry.py`,
  `tests/test_gx8002_image_a_stage1_body_pad.py`: run both verifiers, check
  vector-table/report shape, mutation rejection, and (for the reset entry)
  targeted decoded-instruction mutation tests mirroring
  `tests/test_gx8002_reset_entry.py`.

## Boundary behavior and ownership

`spl_board_init_r` (package `[0x000096DA, 0x0000A837)`) is a genuine,
unreconstructed external call boundary. This item proves only that the 54
reconstructed bytes call it (and the already source-owned stage-two entry)
with the documented stack pointer already in place; it makes **no claim**
about what `spl_board_init_r` itself does, and `runtime_gx8002_image_a_
stage1_boundary.c` is untouched — it keeps authenticating the full,
unmodified 12,288-byte block against stock, so no functionality silently
loses its oracle while this item's bytes are individually reclassified.

Generating the public BINH container format and a deterministic zero-fill
span does not license any payload they frame or pad, exactly as
`gx8002-image-a-stage1-tail-source.md` already establishes for the
immediately following span.

## Readiness delta (this item only; central GX8002 ledger not edited)

| | Before | After |
|---|---:|---:|
| Reviewed source (this item) | 0 B | 3,747 B |
| Opaque/typed-external (this item) | 8,192 B | 4,445 B |

`docs/research/gx8002-source-readiness-ledger.md` and
`tools/manifests/gx8002-source-readiness.tsv` still fold this item's whole
8,192-byte range into the existing monolithic `image_a_stage1` row;
splitting that row is left as follow-up, as CD-009 already noted for its own
adjacent item, to avoid an uncoordinated concurrent edit to that
cross-cutting, actively-shared ledger while other GX8002 items are in
flight.

## Registration

Registered as two tranches (`spl-reset-entry`, `generated_source_data` +
`compiled_assembly`; `image-a-stage1-body-pad`, `generated_source_data`) in
`tools/build_gx8002_source_candidate.py` (imports + two tuple entries) and
in the `gx8002-source-candidate` test list in `Makefile`, under the CD-008
integration lock, alongside the existing registered GX8002 tranches.

## Verification

```sh
python3 g2/tools/verify_gx8002_spl_reset_entry.py
python3 g2/tools/verify_gx8002_image_a_stage1_body_pad.py
python3 -m unittest g2.tests.test_gx8002_spl_reset_entry g2.tests.test_gx8002_image_a_stage1_body_pad
make -C g2 gx8002-source-candidate
make -C g2 codec-source-experimental
```

All software-only. Hardware qualification remains **blocked by unavailable
physical evidence**: this item makes no mask-ROM copy, power-on remap, or
full-device execution claim, only an instruction/byte-identity claim for the
reconstructed span, decoded-trace semantic checks for the reset chain's
control-register and call effects, and byte-exact zero-fill for the pad.

## Remaining work in this item's range

`spl_board_init_r` (package `[0x000096DA, 0x0000A837)`, 4,445 bytes) is
dense, varied C-SKY code — real board bring-up logic, not padding — and was
not decompiled by this item. It is the next natural target for the same
technique used here: wrap the codec image, disassemble at the correct
address with the `e_flags` fix, and check the result instruction-for-
instruction against the public `lvp_kws` SDK's `board_init_r`/board-support
sources (the SDK checkout at `build/upstream-nationalchip-lvp-kws` includes
per-board `boot_board.c` files that are plausible matches given this repo's
already-pinned NationalChip commit). Follow-up should also split the
`image_a_stage1` row in `gx8002-source-readiness-ledger.md` /
`gx8002-source-readiness.tsv` once CD-009's and this item's finer-grained
accounting are both in place, and consider whether `runtime_gx8002_image_a_
stage1_boundary.c`'s monolithic 12,288-byte assertion should be narrowed to
just `spl_board_init_r`'s now-isolated 4,445-byte span.
