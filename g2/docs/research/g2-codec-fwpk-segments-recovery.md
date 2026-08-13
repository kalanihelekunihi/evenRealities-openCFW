# G2 codec FWPK segment-destination recovery

Status: both FWPK segment destinations resolved conclusively at
container/interface level; fail-closed reproduction in
`tools/analyze_g2_codec_fwpk_segments.py` with the machine-readable map in
`tools/manifests/g2-codec-fwpk-segment-map.tsv`. The codec image remains an
explicitly proprietary NationalChip boundary: everything below is format,
placement, and protocol identification plus hash-pinned byte accounting — no
vendor implementation text is claimed, copied, or reconstructed.

## Result

The official G2 2.2.6.10 `firmware_codec.bin` (326,092 bytes, SHA-256
`b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0`, verified
against `blobs/official/g2-2.2.6.10/PROVENANCE.md`) is an `FWPK` container,
version `0x00000203`, with two 16-byte records
`<type><size><offset><crc32>`. Both record CRCs are standard zlib CRC-32 over
the payload and verify. `16 + 2*16 + 38,236 + 287,808 = 326,092` exactly; no
trailing bytes exist.

### Segment 1 (type 1, "boot image", 38,236 B) — volatile, never flashed

The segment is byte-compatible with the **public NationalChip grus (GX8002)
UART boot container** documented by the MIT-licensed
`NationalChip/lvp_kws` / `lvp_sed` SDKs
(`lvp/common/uart_upgrade/uart_sendboot.c`, `scripts/patch_boot.c`):

| Offset | Field | Value | Meaning |
|---:|---|---|---|
| 0 | chip_id (LE u16) | `0x8002` | GX8002 (`CHIP_ID_GX8002`, "grus") |
| 2 | chip_type / version | 1 / 1 | `CHIP_VERSION_V1` |
| 4 | boot_delay / baud / rsv | 0 / 0 / 0 | |
| 8 | stage1_size (BE u32) | `0x2800` (10,240) | |
| 12 | stage2_baud_rate (BE) | 1,500,000 | stage-2 UART baud |
| 16 | stage2_size (BE) | `0x6D3C` (27,964) | |
| 20 | stage2_checksum (BE) | `0x24D441` | byte-sum of stage2, verified |
| 24 | reserved | 8 zero bytes | |

`32 + 10,240 + 27,964 = 38,236` exactly. The four BE fields at offsets
8/12/16/20 match the Apollo DFU behavior previously recovered (read LE,
forwarded in file byte order onto the wire).

Destinations, pinned by self-referential vector tables (C-SKY-style 64-word
tables, reset vector = load base + 0x100):

| Sub-region | File offset | Size | Load address | Entry | Evidence |
|---|---:|---:|---|---|---|
| stage1 | 32 | 10,240 | `0x10000000` (MCU IRAM) | `0x10000100` (vector[0]) | vectors [1–31]→`0x10000130`, [32–63]→`0x10000134` |
| stage2 | 10,272 | 27,964 | `0x10002800` (IRAM, directly after stage1) | `0x10002900` (vector[0]) | all 64 vectors inside `[0x10002800, 0x1000953C)`; handlers `0x10002994` / `0x10003124` |

Both stages are streamed into the codec's on-chip SRAM during DFU and are
gone at power-off; they own no flash extent.

### Segment 2 (type 2, "main image", 287,808 B) — codec SPI NOR flash offset 0

The Apollo DFU flash stage is pinned by disassembly of
`semantic_CodecFlashImage` (`service_codec_dfu.c`, run `[0x005796C8,0x00579C6A)`):
at run `0x005797EE` it formats **`serialdown 0 <image_size> 8192`** into the
8-KiB scratch `0x2035EE18` — flash offset **0**, chunk **0x2000** (format
string at file `0x3435EC`, pool word at run `0x00579FAC`, call-site bytes
hash-pinned in the analyzer). The whole segment therefore lands at codec
external SPI NOR flash `[0x0, 0x46440)`.

The segment is a **dual-firmware BINH concatenation** (the public SDK's
`Makefile`/`scripts/loader_write.c` layout: 24-byte `BINH` header inside the
`0x3000` stage1 block; stage1 block ends with a CRC-32/MPEG-2; one u32
`stage2_xip_len` word; then stage2 body). Both images are present and all
internal CRCs verify:

| Image | Segment extent | stage1 block | stage1 CRC-32/MPEG-2 | stage2 | XIP text |
|---|---|---|---|---|---|
| A (main) | `[0x0, 0x2F3B0)` | flash `0x0`, 12,288 B → IRAM `0x10000000` | `0x21C58EDB` ✓ | flash `0x3004`, 51,200 B, ends exactly `0xF804` | 36,484 B (`0x8E84`) |
| B (backup) | `[0x2F3B0, 0x46440)` | flash `0x2F3B0`, 12,288 B → IRAM `0x10000000` | `0xA582510C` ✓ | flash `0x323B4`, 82,060 B, ends exactly at segment end | 0 (SRAM only) |

Both stage1 blocks carry the same 64-word vector shape (`0x10000100` /
`0x10000130` at block+`0x18`) but differ in 5,039 bytes — distinct builds.
`BINH` occurs exactly twice (`0x0`, `0x2F3B0`). Image A's trailing
`[0xF804, 0x2F3B0)` region (129,964 B, SHA-256
`7bd407a60d16aeb6ad1289184c8d75bad39dc7d7d3704cfea5ce9402e64ec387`) is the
NPU/audio payload; the 24-byte header format carries no offsets for it, so
its internal split is an explicit remaining gate.

Version chain closes: FWPK version `0x203` ≡ both BINH headers' soft version
`0x00000203` ≡ string `0.0.2.3` at segment offset `0x96B4`.

## Protocol / interface facts established this increment

- FWPK record CRC algorithm pinned: zlib CRC-32 over payload (both records).
- Boot wire format is the public NationalChip grus protocol: `0xEF` sync →
  `M`; `'Y'` + stage1 word count; stage1; `E`/`F` CRC verdict; `wfb` → `OK`
  → 4-byte LE baud → `OK` → switch to header-specified 1,500,000 baud;
  `'S'` + checksum + size; `ready`/`O` chunk loop; `boot> ` CLI prompt. This
  matches the previously recovered Apollo DFU behavior and the public
  MIT-licensed `uart_sendboot.c`. Public default stage-1 baud 230,400 matches
  the recovered Apollo UART setup.
- Flash stage pinned from Apollo code: `serialdown 0 <size> 8192\n`, CRC-32,
  `~sta~`/chunk/`~fin~`, `[Result]:`/`SUCC` (public protocol; Apollo-side
  arguments recovered here).
- Codec memory constants (public `arch/soc/grus/include/soc_config.h` /
  `base_addr.h`, cross-confirmed by in-image vectors): MCU IRAM base
  `0x10000000`, DRAM base `0x20000000` (BINH `stage1_load_addr` field),
  flash XIP base `0x10200000` (public default; hardware-gated for this
  build), stage1 block `0x3000`.

## Reproduction

```sh
python3 openCFW/tools/analyze_g2_codec_fwpk_segments.py
python3 -m unittest openCFW.tests.test_analyze_g2_codec_fwpk_segments
```

The analyzer authenticates the codec blob and Apollo image by SHA-256,
re-derives every field above, verifies both record CRCs, the stage2
byte-sum, both stage1-block CRC-32/MPEG-2 values, all four vector tables,
both exact-fit layouts, the version chain, the Apollo `serialdown` call-site
bytes, and the segment-map manifest row-for-row. Any change fails closed.

## Confidence

- FWPK layout, record CRCs, boot container split, stage checksum: conclusive
  (self-verifying arithmetic).
- Segment 1 load addresses (`0x10000000` / `0x10002800`): conclusive at
  interface level (self-referential vector tables + public format);
  execution is hardware-mediated by the mask ROM (hardware-gated).
- Segment 2 flash offset 0 and chunk 0x2000: conclusive (Apollo call-site
  bytes pinned).
- BINH dual-firmware layout, stage1 CRCs, exact fits: conclusive.
- DRAM/XIP runtime mapping of stage2 sections: identified from public SDK
  constants; build-specific split is a remaining gate (below).

## Remaining gates

- Image-A stage2 section split beyond the `0x8E84` XIP-text length
  (SRAM text/data boundaries and their IRAM/DRAM addresses); requires
  C-SKY-aware disassembly — capstone has no C-SKY support, so this is
  tooling-gated. The CPU is C-SKY ABI v2 per the public SDK toolchain
  (`csky-abiv2-elf`), consistent with the vector-table form.
- Internal structure of the 129,964-byte image-A extra payload
  (gxNPU command/weights/data, audio assets): identification-level only.
- Dual-firmware selection policy (which of A/B boots when): lives in the
  codec ROM/stage1; hardware-gated.
- Confirmation that this build uses the public default XIP base
  `0x10200000` and 512-KiB external flash geometry: hardware-gated.
- Codec-side stage2 `boot> ` CLI and the runtime `BUXX` service remain
  proprietary NationalChip code; this increment grants no license and claims
  no source ownership. Production ownership stays zero.

## Ownership statement

Container formats and the wire protocol match NationalChip's MIT-licensed
public SDK (lvp_kws/lvp_sed). The Apollo-side implementation remains Even
first-party `service_codec_dfu.c` (previously closed, production ownership
zero). The codec blob contents — both boot stages, both BINH images, the NPU
payload — remain a proprietary NationalChip boundary. No public codec or LC3
library is claimed to replace any part of the DSP image.
