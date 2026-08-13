# G2 codec BINH stage2 section and gxNPU payload recovery

Status: image-A stage2 SRAM text/data load addresses, sizes, and entry points
closed conclusively; gxNPU (KWS model) payload offsets closed by exact-fit
arithmetic. Fail-closed reproduction in
`tools/analyze_g2_codec_stage2_sections.py`; machine-readable map in
`tools/manifests/g2-codec-stage2-section-map.tsv`. The codec image remains an
explicitly proprietary NationalChip boundary — this is placement/interface
identification, not source recovery.

## Disassembler path and validation

Capstone (5.0.7 and 6.0.0) has no C-SKY support; official LLVM 22.1.8 release
binaries do not register the CSKY target; upstream GNU binutils 2.43.1
includes C-SKY but **mis-decodes the 32-bit instruction forms** used here
(`mtcr`/`bsr`/32-bit `lrw` decoded as data), making it unusable. The working
path is the **official C-SKY backend fork** `c-sky/binutils-gdb`
(`github.com/c-sky/binutils-gdb`, commit
`2409f5af709d5fef4f41cbeb30ef59bc1046b252`), built as
`csky-elfabiv2-objdump` on the `lorelei` workstation (build needed
`-std=gnu89` and warning relaxations under GCC 16; the repo is not required
there — inputs were copied with scp). CPU is `ck804ef` per the public
NationalChip SDK Makefile (`-mcpu=ck804ef`).

Decode validation evidence (all fail-closed pinned in the analyzer):

1. Four independent reset entries (boot stage1, boot stage2, image-A app,
   image-B app) decode to the **same canonical GX8002 CRT0 sequence**:
   `lrw r0, 0x80000200; mtcr r0, cr<0,0>; mfcr r1, cr<31,0>; bclri r1, 3;
   mtcr r1, cr<31,0>; lrw r3, <sp>; mov r14, r3; bsr ×n; br .` — the fork
   decodes these correctly where upstream binutils emits `.long`.
2. Boot stage2's startup contains a textbook BSS-zero loop over DRAM
   `[0x2000953C, 0x2000A1FC)`.
3. Every vector-table handler resolves inside its image's resolved load span.
4. The flash-model-load function references debug strings that read as
   meaningful `[LVP_KWS ]...` log lines at the decoded addresses.
5. Exact-fit arithmetic (below) closes three independent section systems to
   the byte.

All decoded facts were then re-expressed as raw-byte pins, vector-table
self-reference checks, and exact-fit arithmetic in the analyzer, so
reproduction requires no disassembler.

## Image-A stage2 layout (conclusive)

The public NationalChip SPL (`arch/soc/grus/spl/spl.c`) loads stage2 as:
read `stage2_xip_text_len` at `stage1_size` (flash `0x3000`), copy
`sram_text + sram_data` from `0x3000 + 4 + xip_len` to
`_stage2_sram_start_text_`, jump to `IRAM_BASE + NPU_SRAM_SIZE + 0x100`.
Applied to the blob (xip_len `0x8E84`, stage2_size `0xC800`):

| Section | Flash extent | Size | Runtime location | Entry |
|---|---|---:|---|---|
| XIP text | `[0x3004, 0xBE88)` | 36,484 | executes in place from flash (public default XIP base `0x10200000`, hardware-gated) | — |
| SRAM text | `[0xBE88, 0xEF6C)` | 12,516 | IRAM `[0x10023400, 0x100264E4)` | `0x10023500` (vector[0]) |
| pad | `[0xEF6C, 0xEF70)` | 4 | `0xFFFFFFFF` fill | — |
| SRAM data | `[0xEF70, 0xF804)` | 2,196 | IRAM `[0x100264E8, 0x10026D7C)` | — |

Combined SRAM copy `[0x10023400, 0x10026D7C)` = 14,716 B = `0x397C` =
`stage2_size − xip_len` exactly. The SRAM load base is proven by the app's
own 64-word vector table at flash `0xBE88` (reset `0x10023500` = base +
0x100; handlers `0x10023640` / `0x10025574` inside the span). Implied
`NPU_SRAM_SIZE` = `0x23400` (141 KiB): the gxNPU owns IRAM
`[0x10000000, 0x10023400)` at runtime. App stack pointer `0x2002F7FC` (DRAM).
The text/data boundary sits at the last function return (`jmp r15` at
`0x100264DE`) plus two literal-pool words and one `0xFFFFFFFF` fill word;
data begins zero-initialized at `0x100264E8`.

## Image-B stage2 layout (backup firmware)

SRAM-only (xip_len 0): combined copy flash `[0x323B4, 0x46440)` → IRAM
`[0x10003000, 0x1001708C)` (82,060 B), entry `0x10003100`, handlers
`0x10003240` / `0x10004880`, stack `0x2002FFFC`. Its implied NPU reservation
is only `0x3000` (backup firmware does not run the NPU model). Internal
text/data boundary is derived (last `pop r4-r9, r15` at `0x10016518`):
text ≈ 79,132 B, data ≈ 2,928 B — marked heuristic in the manifest; the
combined extent and entry are conclusive.

## gxNPU payload offsets (conclusive, exact-fit)

Image A's post-stage2 payload `[0xF804, 0x2F3B0)` is entirely the **LVP_KWS
keyword-spotting gxNPU model**. The KWS init function (XIP text) performs
two flash reads via a literal `LD_NPU_IMAGE_OFFSET = 0xF804` (pinned: 32-bit
`lrw r8, 0xf804` at flash `0x6D40`, literal word at `0x6D84`) with sizes from
tiny constant-return getters (pinned instruction bytes):

| Region | Flash extent | Size | DRAM staging (decoded) |
|---|---|---:|---|
| KWS NPU command stream | `[0xF804, 0x11BD0)` | 9,164 (`movi r0, 9164`) | `0x20003304` |
| KWS NPU weights | `[0x11BD0, 0x2F3B0)` | 120,800 (`movi r0, 55264; bseti r0, 16`) | `0x200056D0` |

`0xF804 + 9,164 + 120,800 = 0x2F3B0` — the payload ends **exactly** at the
image-B offset, proving both the split and that no third (audio/data) section
exists. Module identity is confirmed by `[LVP_KWS ]Init Flash Failed` /
`Kws Use:%d ms` / `Read Flash Failed` strings referenced by the loader.

## Reproduction

```sh
python3 openCFW/tools/analyze_g2_codec_stage2_sections.py
python3 -m unittest openCFW.tests.test_analyze_g2_codec_stage2_sections
```

The analyzer authenticates the blob, re-derives all offsets from the BINH
header fields and the public SPL formula, verifies both app vector tables,
both CRT0 prefixes, both stack literals, all evidence instruction bytes, the
boundary fill word, the KWS identity strings, and every exact-fit identity,
then checks the manifest row-for-row. Any change fails closed.

## Confidence

- Image-A section split, load addresses, entry: conclusive (vector
  self-reference + exact-fit + byte pins).
- KWS cmd/weight offsets and sizes: conclusive (constant getters + exact fit
  to image-B offset).
- XIP base `0x10200000`: public SDK default; hardware-gated for this build.
- Image-B internal text/data boundary: derived (heuristic), combined extent
  conclusive.
- DRAM staging addresses (`0x20003304`/`0x200056D0`): decoded behavior,
  byte-level pinned only at the getter sites; marked `(decoded)`.

## Remaining gates

- gxNPU command-stream semantics (the 44-byte record structure at `0xF804`;
  likely gxNPU register/DMA op sequences): identification-level only;
  decoding it needs the gxDNN command format and is a separate increment.
- KWS model provenance/version (which wake words; likely a custom Even
  Realities model trained via NationalChip viva): not derivable from
  structure alone.
- Runtime mapping of NPU SRAM `[0x10000000, 0x10023400)` (how the app DMAs
  cmd/weights from DRAM staging into NPU SRAM): partially decoded, not
  pinned here.
- Hardware-gated: XIP base, dual-firmware selection, flash geometry.

## Ownership statement

The section map, SPL load procedure, and KWS loader structure match
NationalChip's MIT-licensed public SDKs (lvp_kws/lvp_sed/gxDNN tooling). The
KWS model weights are proprietary trained-model data (vendor and/or Even
Realities). The codec image remains a proprietary boundary; this increment
claims zero source and zero model content.
