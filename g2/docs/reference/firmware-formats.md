# G2 firmware container and payload formats

Scope: the official G2 OTA bundle `s200_v2.2.6.10` and the six payloads it
carries. Citations are `path:line` at commit `832137ec`. Confidence levels:

- **Proven**: byte or hash evidence reproduces the official bytes exactly.
- **Strong**: independent structural evidence, with no byte-exact rebuild.
- **Inferred**: a consistent reading with a single evidence line.
- **Unverified**: stated in the sources but not checked.

The only byte-exact producer in the repository is the EVENOTA repack of the
six official payloads (`g2/tools/open_cfw.py`). It reproduces the locked
bundle hash, so every container field below that the repack writes is
**Proven**.

## 1. Locked target identity

Bundle `s200_v2.2.6.10`:

- 4,301,227 bytes;
- SHA-256 `f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`;
- build date/time `2026-07-06 21:39:36`.

Sources: `g2/workflow/target.json:7-8`, `g2/manifests/g2-2.2.6.10.json:6-11`,
`g2/blobs/official/g2-2.2.6.10/PROVENANCE.md:5-11`.

| # | Payload id | Package filename | Type ID | Size (B) | SHA-256 |
|---:|---|---|---:|---:|---|
| 1 | `codec` (GX8002) | `firmware/codec.bin` | 4 | 326,092 | `b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0` |
| 2 | `ble_em9305` | `firmware/ble_em9305.bin` | 5 | 211,948 | `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9` |
| 3 | `touch` (PSoC 4000T) | `firmware/touch.bin` | 3 | 34,464 | `0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d` |
| 4 | `case` (STM32G0) | `firmware/box.bin` | 6 | 55,784 | `36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374` |
| 5 | `apollo_bootloader` | `ota/s200_bootloader.bin` | 1 | 148,599 | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` |
| 6 | `apollo_main` | `ota/s200_firmware_ota.bin` | 0 | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |

Table sources:

- sizes and hashes: `g2/workflow/target.json:24-83` and
  `g2/blobs/official/g2-2.2.6.10/PROVENANCE.md:18-25`;
- type IDs: `g2/manifests/g2-2.2.6.10.json:18,58,122,156,193,219`.

Confidence: Proven.

All six payloads have `storage_type = 3`, and the entry IDs run 1..6 in table
order (`g2/manifests/g2-2.2.6.10.json:15-220`). The payloads are
vendor-proprietary. The repository tracks only their provenance, not the bytes
(`g2/blobs/official/g2-2.2.6.10/PROVENANCE.md:27-29`).

## 2. EVENOTA outer container

Source: `g2/tools/open_cfw.py:36-41` (constants), `:1168-1191`
(`component_header`), `:1193-1248` (`assemble_evenota`) and `:1250-1304`
(`validate_evenota_image`). Explanation: `g2/docs/memory-map.md:7-21`.
Confidence: Proven, because a repack reproduces the locked SHA-256.

All integers are little-endian u32.

| Offset | Size | Field |
|---:|---:|---|
| `0x00` | 8 | magic `"EVENOTA\0"` |
| `0x08` | 4 | entry count (6) |
| `0x0C` | 4 | 0 |
| `0x10` | 16 | build date, NUL-padded ASCII (`2026-07-06`) |
| `0x20` | 16 | build time (`21:39:36`) |
| `0x30` | 16 | version (`s200_v2.2.6.10`) |
| `0x40` | 16 × n | TOC entries `{entry_id, file_offset, entry_size, crc32c}` |
| `0x40+16n` | 16 | TOC trailer `"evenota\0"` + 8 zero bytes |
| `0xB0` (n = 6) | ... | entry bodies, contiguous, in TOC order, closing exactly at EOF |

Each entry is a 128-byte component header followed by the payload, so
`entry_size = 128 + payload size`. The component header is:

| Off | Value | Off | Value |
|---:|---|---:|---|
| `0x00` | 0 | `0x1C` | `0xFFFFFFFF` |
| `0x04` | 0 | `0x20` | 0 |
| `0x08` | payload size | `0x24` | type ID |
| `0x0C` | CRC-32C of payload (same value as TOC) | `0x28` | storage type (3) |
| `0x10` | 0 | `0x2C` | `0xFFFFFFFF` |
| `0x14` | magic `0x4E455645` (`"EVEN"` LE) | `0x30..0x7F` | package filename, NUL-padded (80 B) |
| `0x18` | `0xFFFFFFFF` | | |

**Checksum.** CRC-32C (Castagnoli), non-reflected ("MSB-first"):

- polynomial `0x1EDC6F41`;
- init 0, xorout 0;
- computed over the payload only.

Source: `g2/tools/open_cfw.py:224-248`.

**Official layout.** The entry offsets below are derived from the header
arithmetic above and the payload sizes; the sum closes at 4,301,227 bytes.

| Component | Entry offset | Payload offset |
|---|---:|---:|
| codec | `0xB0` | `0x130` |
| ble_em9305 | `0x4FAFC` | `0x4FB7C` |
| touch | `0x83768` | `0x837E8` |
| case | `0x8BE88` | `0x8BF08` |
| apollo_bootloader | `0x998F0` | `0x99970` |
| apollo_main | `0xBDDE7` | `0xBDE67` |

Entry offsets are not aligned (see the last row). Any change in the size of an
earlier component moves every later offset (`g2/docs/memory-map.md:9-12`).

## 3. Apollo main: 32-byte OTA staging preamble

Sources:

- `g2/tools/open_cfw.py:751-774` (`validate_apollo_main`);
- `g2/tools/open_cfw.py:2313-2341` (`wrap_main_image`);
- `g2/docs/memory-map.md:1202-1203`.

Confidence: Proven.

| Off | Field |
|---:|---|
| `0x00` | `(0x04 << 24) \| total_size`: 24-bit size including the preamble; flags byte `0x04` |
| `0x04` | zlib CRC-32 (reflected, poly `0x04C11DB7`) over payload bytes `[0x08, end)` |
| `0x08`, `0x0C` | 0 |
| `0x10` | data type `0xCB` |
| `0x14` | install/run address `0x00438000` |
| `0x18`, `0x1C` | 0 |
| `0x20..` | raw Cortex-M55 image: vector table first, installed at `0x00438000` |

Two address relations follow:

- **Run address from file offset.** `run = file_offset + 0x00437FE0`, so file
  `0x20` maps to run `0x438000`
  (`g2/docs/research/cordio-ble-stack-identity-audit.md:14-16`).
- **Installed image span.** The installed image is `[0x00438000, 0x00794324)`,
  3,523,364 bytes (`g2/docs/memory-map.md:309`).

The bootloader DFU task consumes the same header:

- it masks the size to 24 bits;
- its CRC check skips the first 8 bytes;
- the programmer skips the 32-byte header;
- it normalizes the vector base to `0x00438000`.

Sources: `g2/docs/research/g2-bootloader-dfu-image-crc-check-42d890-source-closure.md:9-10`,
`g2/docs/research/g2-bootloader-dfu-payload-program-42dae8-source-closure.md:7-8`,
`g2/docs/research/g2-bootloader-dfu-service-task-42de58-source-closure.md:15-19`.
Confidence: Strong.

## 4. Apollo bootloader

The bootloader payload is a raw Cortex-M55 image with no wrapper, linked at
`0x00410000` (`g2/tools/open_cfw.py:737-748`,
`g2/manifests/g2-2.2.6.10.json:190-213`).

- The image ends at `0x00434477`.
- Free partition headroom runs to `0x00438000`
  (`g2/docs/memory-map.md:250,308`).

Confidence: Proven.

## 5. Case (STM32G0): `EVEN` wrapper

Sources:

- `g2/tools/open_cfw.py:710-734` (sum and validation);
- `g2/tools/open_cfw.py:2344-2365` (wrapper);
- `g2/manifests/g2-2.2.6.10.json:153-187`.

Confidence: Proven.

| Off | Size | Field |
|---:|---:|---|
| `0x00` | 4 | `"EVEN"` |
| `0x04` | 4 | version bytes `major, minor, patch, 0`: `01 02 39 00` = case 1.2.57 |
| `0x08` | 4 | **big-endian** raw image length (`0x0000D9C8` = 55,752) |
| `0x0C` | 4 | **big-endian** additive checksum: sum of the raw image read as big-endian u32 words (zero-padded to 4 bytes), mod 2^32 |
| `0x10` | 16 | zero |
| `0x20..` | | raw Cortex-M0+ image, vector table at `0x08000000` (alias `0x08040000`) |

The case updater verifies the same 32-bit additive sum after programming
(`g2/docs/memory-map.md:1763-1766`). For flash banks and preserved windows,
see `memory-map.md` §6.

## 6. Touch (PSoC 4000T): FWPK, one type-3 record

Sources:

- `g2/tools/open_cfw.py:697-707` and `:2368-2387`;
- `g2/docs/research/g2-touch-identity-recovery.md:80-84,113-121`.

| Off | Field |
|---:|---|
| `0x00` | `"FWPK"` |
| `0x04` | bytes `01 00 02 02` (LE `0x02020001`; meaning unresolved) |
| `0x08` | record count = 1 |
| `0x0C` | 0 |
| `0x10` | record: type 3 |
| `0x14` | record: size (`0x8680` = 34,432) |
| `0x18` | record: offset `0x20` |
| `0x1C` | record: **reflected** CRC-32C of the payload (official `0x48674BC7`) |
| `0x20..` | flash-linear Cortex-M0+ image, linked at `0x00003300` (see `memory-map.md` §6) |

The CRC is CRC-32C with poly `0x82F63B78` reflected, init and xorout
`0xFFFFFFFF` (`g2/tools/open_cfw.py:251-258`).

The payload carries a second checksum in its last word: the reflected CRC-32C
of all preceding payload bytes (`0xF75CF6F4`). The programmed length is
therefore `0x867C` (`g2/docs/research/g2-touch-identity-recovery.md:80-84,118-120`).

Confidence:

- container and both CRCs: Proven;
- the meaning of the word at `0x04`: Unverified.

Host DFU framing (Strong; `g2/docs/research/g2-touch-identity-recovery.md:103-110`):

- frame layout `0x01 | cmd | len16le | payload<=32 | cksum16 | 0x17`;
- programming in 128-byte rows;
- commands `0x38` enter, `0x4C` metadata, `0x37` packet, `0x49` program,
  `0x31` verify, `0x3B` exit.

## 7. Codec (GX8002): FWPK, two segments

Sources:

- `g2/tools/open_cfw.py:650-667`;
- `g2/docs/research/g2-codec-fwpk-segments-recovery.md:13-19,83-84`;
- `g2/docs/memory-map.md:1896-1907`.

Confidence: Proven, because the arithmetic closes exactly and both CRCs
verify.

The FWPK header is 16 bytes:

- `"FWPK"`;
- version `0x00000203` at `+4`;
- segment count 2 at `+8`.

It is followed by 16-byte records `<type, size, offset, crc32>` at `0x10`.
Segments are contiguous from `0x10 + 16·count`, close at EOF, and carry a
zlib CRC-32 each. The layout closes as `16 + 2·16 + 38,236 + 287,808 =
326,092` bytes.

The FWPK version `0x203` equals both BINH soft-version fields and the string
`0.0.2.3` at segment-2 offset `0x96B4`
(`g2-codec-fwpk-segments-recovery.md:83-84`).

| Seg | Type | Payload offset | Size | Role |
|---:|---:|---:|---:|---|
| 1 | 1 | `0x30` | 38,236 | UART boot container (volatile; streamed into codec IRAM) |
| 2 | 2 | `0x958C` | 287,808 | dual BINH flash image; written to codec SPI NOR at offset 0 |

The segment table itself carries no load addresses. The addresses below come
from the recovery documents.

### 7.1 Segment 1: NationalChip "grus" UART boot container

Source: `g2/docs/research/g2-codec-fwpk-segments-recovery.md:21-52,86-98`.
Confidence: Proven for the layout; the addresses are Strong.

The format matches the public MIT `lvp_kws` `uart_sendboot.c` /
`patch_boot.c`. The container header is 32 bytes:

| Off | Field | Value |
|---:|---|---|
| 0 | `chip_id` (LE u16) | `0x8002` |
| 2 | chip type, version | 1, 1 |
| 4 | boot delay, baud, reserved | 0 |
| 8 | stage-1 size (BE) | `0x2800` |
| 12 | stage-2 baud (BE) | 1,500,000 |
| 16 | stage-2 size (BE) | `0x6D3C` |
| 20 | stage-2 checksum (BE) | `0x24D441`, the byte sum of stage 2 |
| 24 | reserved | 8 zero bytes |

The two stages that follow:

- **Stage 1:** 10,240 bytes at file offset 32. Loaded to IRAM `0x10000000`,
  entry `0x10000100`.
- **Stage 2:** 27,964 bytes at file offset 10,272. Loaded to IRAM
  `0x10002800`, entry `0x10002900`.

Both stages use C-SKY 64-word vector tables with `reset = base + 0x100`. The
wire protocol is:

1. `0xEF` sync, then `M`;
2. `Y` plus the stage-1 word count, then stage 1;
3. an `E`/`F` CRC verdict;
4. `wfb`, `OK`, the baud, `OK`, then the switch to 1.5 Mbaud;
5. `S` plus checksum and size;
6. a `ready`/`O` chunk loop ending at the `boot> ` prompt.

The flash stage runs `serialdown 0 <size> 8192\n`:

- the Apollo side formats this command at run `0x005797EE`;
- data follows in `~sta~`/chunk/`~fin~` framing;
- the result is reported as `[Result]:`/`SUCC`.

### 7.2 Segment 2: dual BINH image (codec SPI NOR `[0x0, 0x46440)`)

Sources: `g2/docs/research/g2-codec-fwpk-segments-recovery.md:54-81`,
`g2/docs/research/g2-codec-stage2-sections-recovery.md:44-95`.
Confidence: Proven for extents and CRCs; placement is Strong.

Each image has three parts:

- a `0x3000` stage-1 block containing a 24-byte `BINH` header and ending with
  a CRC-32/MPEG-2;
- a u32 `stage2_xip_len`;
- the stage-2 body.

The `BINH` magic occurs exactly twice, at `0x0` and `0x2F3B0`.

| Image | Extent | Stage-1 block CRC | Stage 2 |
|---|---|---|---|
| A (main) | `[0x0, 0x2F3B0)` | `0x21C58EDB` | flash `0x3004`, 51,200 B |
| B (backup) | `[0x2F3B0, 0x46440)` | `0xA582510C` | flash `0x323B4`, 82,060 B, SRAM-only (xip_len 0) |

The two stage-1 blocks differ in 5,039 bytes.

Image A stage-2 sections (`xip_len = 0x8E84`):

| Section | Flash extent | Size | Runtime placement |
|---|---|---:|---|
| XIP text | `[0x3004, 0xBE88)` | 36,484 | executes in place (public default XIP base `0x10200000`; Inferred for this build) |
| SRAM text | `[0xBE88, 0xEF6C)` | 12,516 | IRAM `[0x10023400, 0x100264E4)`, entry `0x10023500` |
| pad | `[0xEF6C, 0xEF70)` | 4 | `0xFFFFFFFF` |
| SRAM data | `[0xEF70, 0xF804)` | 2,196 | IRAM `[0x100264E8, 0x10026D7C)` |
| KWS NPU command stream | `[0xF804, 0x11BD0)` | 9,164 | staged to DRAM `0x20003304` (decoded) |
| KWS NPU weights | `[0x11BD0, 0x2F3B0)` | 120,800 | staged to DRAM `0x200056D0` (decoded) |

The NPU payload offset `0xF804` is a literal in the KWS init code (at flash
`0x6D40`/`0x6D84`). The check `0xF804 + 9,164 + 120,800 = 0x2F3B0` proves
there is no third section.

Image B loads to IRAM `[0x10003000, 0x1001708C)`, entry `0x10003100`, stack
`0x2002FFFC`. Its internal text/data split is heuristic.

## 8. EM9305: record-table package

Sources:

- `g2/components/em9305/source_image/record_package.py:12-141` (the parser and
  builder, which rebuild the stock container byte-for-byte);
- `g2/components/em9305/source_image/README.md:5-14`;
- `g2/tools/open_cfw.py:670-694`;
- `g2/manifests/g2-2.2.6.10.json:55-116`.

Confidence: Proven.

| Off | Field |
|---:|---|
| `0x00` | magic bytes `00 02 04 04` |
| `0x04` | total record-payload length (u32) |
| `0x08` | record count (4) |
| `0x0C` | erase-sector count (u32) |
| `0x10` | descriptors `{file_offset, size, target_address}` × count (12 B each), contiguous and canonical |
| then | erase-sector IDs, u16 each |
| then | zero padding to a 4-byte boundary; metadata = `align4(16 + 12·rec + 2·erase)` |
| then | record payloads, back-to-back |

Official records (the metadata is 124 bytes):

| Record | File offset | Size | Target |
|---|---:|---:|---:|
| 0 | 124 | 224 | `0x00300000` |
| 1 | 348 | 656 | `0x00300400` |
| 2 FHDR | 1,004 | 56 | `0x00302000` (image descriptor; entry point `0x00302028`) |
| 3 application | 1,060 | 210,888 | `0x00302400` |

The builder preserves the gaps between records and never produces a gap-filled
flat image (`g2/docs/memory-map.md:1780-1791`). The erase-sector count is 29 or
30 (inferred from the 124-byte metadata size, not stated in the sources).

## 9. Case backup windows (device data outside OTA)

Sources:

- `g2/blobs/official/case-backup-2026-08-09/PROVENANCE.md:23-44`;
- `g2/manifests/g2-2.2.6.10.json:266-292`;
- `g2/docs/memory-map.md:1768-1776`.

Confidence: Proven from one captured device.

| Captured alias | Contents |
|---|---|
| `0x08000000–0x0800D9C8` | case 1.2.57 application (exact OTA raw match) |
| `0x0800D9C8–0x0803F000` | erased |
| `0x0803F000–0x08040000` | two 2 KiB device-data pages: first page 16 non-`FF` bytes at `0x0803F000`, second page 8 at `0x0803F800` |
| `0x08040000–0x0804D8F8` | case 1.2.56 application (the previous release, in the other bank) |
| `0x0804D8F8–0x0807F000` | erased |
| `0x0807F000–0x08080000` | device-data pages mirroring bank 1 |

The protected windows that must survive a case update are:

- `0x0803F000+16`;
- `0x0803F800+8`;
- `0x0807F000+16`;
- `0x0807F800+8`.

The option bytes are separate, 128 bytes at `0x1FFF7800`. The raw split image
is not a safe whole-flash replacement.

## 10. Checksum summary

| Where | Algorithm | Source |
|---|---|---|
| EVENOTA TOC and component header | CRC-32C, non-reflected, init 0, xorout 0, payload only | `g2/tools/open_cfw.py:224-248` |
| Apollo main preamble `+4` | zlib CRC-32 over `[8, end)` | `g2/tools/open_cfw.py:763,2340` |
| Case `EVEN` `+0x0C` | big-endian additive u32 word sum | `g2/tools/open_cfw.py:710-715` |
| Touch FWPK record, and touch payload tail | reflected CRC-32C | `g2/tools/open_cfw.py:251-258`; `g2-touch-identity-recovery.md:80-84` |
| Codec FWPK records | zlib CRC-32 | `g2/tools/open_cfw.py:662`; `g2-codec-fwpk-segments-recovery.md:88` |
| Codec BINH stage-1 block | CRC-32/MPEG-2 | `g2-codec-fwpk-segments-recovery.md:66-73` |
| Codec UART stage 2 | byte sum (BE u32 field) | `g2-codec-fwpk-segments-recovery.md:36` |
| EM9305 package | none at container level | `record_package.py` |
