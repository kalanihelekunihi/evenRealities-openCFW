# firmware_codec.bin — GX8002B Audio Codec

Firmware for the Nationalchip GX8002B audio codec processor. Uses a dual-segment FWPK wrapper containing two independent BINH boot image blocks for the GX8002B's serial bootloader protocol.

**Target**: GX8002B audio codec (Nationalchip)
**EVENOTA entry**: ID 1, type 4 (Codec)
**Interface**: TinyFrame serial from Apollo510b (`drv_gx8002b.c`)
**Stability**: Byte-identical across all 5 firmware versions (319,372 bytes)

---

## 1. File Structure

```
┌──────────────────────────────────────────────────────────────┐
│ FWPK Header (0x30 bytes = 48 bytes)                          │
│   +0x00: "FWPK" magic (4 bytes)                              │
│   +0x04: 0x00 0x02 0x00 0x00  (version/flags)                │
│   +0x1C: LE32  CRC32(segment 0)  = 0x307E8A10                │
│   +0x24: LE32  segment 1 size    = 0x44A00 (281,088 B)       │
│   +0x28: LE32  segment 1 offset  = 0x958C                    │
│   +0x2C: LE32  CRC32(segment 1)  = 0xB281D56C                │
├──────────────────────────────────────────────────────────────┤
│ Segment 0 (38,236 bytes)  [0x30 – 0x958B]                    │
│   Codec configuration / initialization data                  │
├──────────────────────────────────────────────────────────────┤
│ Segment 1 (281,088 bytes) [0x958C – 0x4DF8B]                 │
│   Two BINH boot image blocks:                                │
│   ├── Block 1 @ +0x0000: stage1 + stage2 loader              │
│   └── Block 2 @ +0x2D970: alternate boot image               │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. FWPK Header Fields

| Offset | Size | Field | Value |
|--------|------|-------|-------|
| +0x00 | 4 | Magic | `FWPK` (ASCII `0x46575044`) |
| +0x04 | 4 | Version/flags | `0x00020000` |
| +0x1C | 4 | Segment 0 CRC32 | `0x307E8A10` |
| +0x24 | 4 | Segment 1 size | `0x00044A00` (281,088 bytes) |
| +0x28 | 4 | Segment 1 offset | `0x0000958C` |
| +0x2C | 4 | Segment 1 CRC32 | `0xB281D56C` |

### Checksum Algorithm

Both segments use **standard CRC32** (zlib, poly `0x04C11DB7`), NOT CRC32C:
- Segment 0: `crc32(file[0x30 : 0x958C])` = `0x307E8A10`
- Segment 1: `crc32(file[0x958C : 0x4DF8C])` = `0xB281D56C`

Segment lengths: `0x955C + 0x44A00` = `file_size - 0x30` (exact coverage, no gaps).

---

## 3. BINH Boot Image Blocks

Segment 1 contains two BINH blocks — the GX8002B's serial bootloader protocol for firmware loading:

### Block Layout

| Offset | Size | Field | Block 1 | Block 2 |
|--------|------|-------|---------|---------|
| +0x00 | 4 | Magic | `BINH` | `BINH` |
| +0x04 | 4 | Sync marker | `0x55AA55AA` | `0x55AA55AA` |
| +0x08 | 4 | `stage1_size` | `0x00000200` (512 B) | `0x00000200` (512 B) |
| +0x0C | 4 | `stage2_baud_rate`* | `0x0000ADC0` | `0x0001408C` |
| +0x10 | 4 | `stage2_size` | `0x00003000` (12,288 B) | `0x00003000` (12,288 B) |
| +0x14 | 4 | `stage2_checksum` | `0x20000000` | `0x20000000` |
| +0x18 | 4 | Entry/vector word | `0x10000100` | `0x10000100` |
| +0x1C | 4 | Handler word | `0x10000130` | `0x10000130` |

*Field `+0x0C` is labeled `stage2_baud_rate` by firmware logging, but values are atypical for standard UART baud rates.

### Block Positions (relative to segment 1 start at file offset `0x958C`)

- **Block 1**: offset `0x0000` within segment 1
- **Block 2**: offset `0x2D970` within segment 1

### Disassembly Correlation

The main application firmware (`s200_firmware_ota.bin`) contains functions that parse these BINH headers:

| Function | Address | Reads |
|----------|---------|-------|
| `print_bootheader` | `0x0054404C` | `stage1_size` (+0x08), `stage2_size` (+0x10), `stage2_checksum` (+0x14) |
| `download_bootimg_stage2` | `0x005449DC` | `stage2_size` (+0x10), checksum (+0x14), rejects zero values |

---

## 4. Flashing Protocol

The Apollo510b loads firmware into the GX8002B via a two-stage serial boot process using the TinyFrame protocol:

```
Apollo510b                              GX8002B
    │                                      │
    │  1. TinyFrame: send stage1 (512 B)   │
    │     ────────────────────────▶        │
    │     (GX8002B executes stage1 loader) │
    │                                      │
    │  2. TinyFrame: send stage2 (12 KB)   │
    │     ────────────────────────▶        │
    │     (GX8002B verifies checksum)      │
    │     (GX8002B executes stage2 main)   │
    │                                      │
    │  3. TinyFrame: send codec data       │
    │     ────────────────────────▶        │
    │     (codec fully operational)        │
```

The GX8002B handles audio encoding/decoding — it processes microphone input into LC3 frames for BLE transmission and decodes incoming audio for the speaker.

---

## 5. GX8002B in the G2 Architecture

| Aspect | Detail |
|--------|--------|
| **Role** | Audio codec processor — LC3 encoding, voice activity detection |
| **Interface** | TinyFrame serial (UART-like) |
| **Driver** | `drv_gx8002b.c` in firmware source tree |
| **DFU Path** | `platform/audio/codec_dfu` |
| **Boot Protocol** | BINH two-stage loader |
| **Frame Format** | LC3, 10 ms frames, 40 bytes/frame |

---

## 6. Deep Binary Analysis (from firmware strings)

### NationalChip LVP Software Stack

```
[LVP]Copyright (C) 2001-2020 NationalChip Co., Ltd
[LVP]Low-Power Voice Preprocess
```

Board ID: `grus_gx8002b_dev_1v` — "Grus" board (constellation naming convention).
Firmware version: `0.0.2.0`

### Wake Words

Two trigger phrases hardcoded in codec firmware:
- `hey_even`
- `hi_even`

### Audio Processing Pipeline

1. **Dual-mic beamforming**: GSC (Generalized Sidelobe Canceller)
2. **Three denoise modes**:
   - `DOUBLE_MIC_DENOISE` — GSC beamforming (primary)
   - `SINGLE_MIC_DENOISE` — IMCRA noise estimation
   - `ORIGIN_MIC` — raw mic passthrough
3. **DRC** (Dynamic Range Compression): `FrameDrcStateInit`
4. **Audio output**: PCM, I2S, DAC, source rate conversion
5. **VAD** (Voice Activity Detection): 3 configurable parameters
6. **PGA gain**: Configurable microphone preamp (0-48 range)
7. **G-sensor**: Motion sensor integration for activity-aware processing

### Boot Prompt (multi-stage from main SoC)

```
1. reading boot header ...
2. start boot stage1 ...
3. download boot stage1 ... → wait for "wfb" prompt
4. boot stage1 ok !
5. start boot stage2 ...
6. download boot stage2 ... → wait for "OK" prompt
7. boot stage2 ok !
8. waiting "boot>" ... → wait for boot prompt
9. get "boot>" !           → boot complete
```

### TinyFrame Message Format

```
Pack message: cmd=0x%04X(NR=0x%02X, TYPE=0x%02X), seq=0x%02X, flags=0x%02X, length=%d, crc32=0x%08X
```

CRC32 (not CRC16 like BLE), with NR/TYPE/seq/flags fields.

### Debug CLI Commands (factory shell)

```
boot>                    — command prompt
help                     — print command list
eraseall                 — flash erase
serialdown               — burn flash from serial
reboot                   — reset MCU through watchdog
wdt                      — watchdog test
```

---

## 7. Cross-Version Stability

The GX8002B codec firmware is **completely byte-identical** across all 5 analyzed firmware versions:

| Version | Size | Status |
|---------|------|--------|
| 2.0.1.14–2.0.7.16 | 319,372 bytes | Identical |

**Implication**: No audio codec logic changes, no LC3 encoder variations, and no VAD/beamforming drift across the G2 version family. Audio processing behavior is guaranteed consistent regardless of firmware version.

Like the EM9305 BLE patch, the codec firmware is a hardware-specific binary (Nationalchip GX8002B) that handles audio processing independently from the Apollo510b main application. It doesn't change with G2 feature updates.

Validated in the iOS SDK by `G2FirmwareVersionRegistry` (in `G2EVENOTAParser.swift`) which tracks this as a "STABLE" component.

---

## Related Documents

- [firmware-files.md](firmware-files.md) — EVENOTA container, FWPK wrapper spec
- [firmware-reverse-engineering.md](firmware-reverse-engineering.md) — FWPK checksums, BINH header map
- [../devices/g2-glasses.md](../devices/g2-glasses.md) — G2 audio hardware
- [../protocols/nus-protocol.md](../protocols/nus-protocol.md) — NUS audio streaming (LC3 via 0xF1 prefix)
