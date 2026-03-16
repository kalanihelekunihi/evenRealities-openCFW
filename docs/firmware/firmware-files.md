# Firmware Files — Device-to-Hardware Mapping

Date: 2026-03-03
Sources: CDN EVENOTA packages (5 versions), Even.app DFU bundles, binary analysis, BLE captures

---

## 1. Device Inventory

The Even Realities ecosystem comprises four physical products. Only three contain firmware.

| Device | SoC | Has Firmware | Update Protocol | FCC ID |
|--------|-----|-------------|-----------------|--------|
| **G2 Glasses (Left)** | Ambiq Apollo510b | Yes — 6-component EVENOTA | Custom OTA (0xC4/0xC5) | 2BFKR-G2 |
| **G2 Glasses (Right)** | Ambiq Apollo510b | Yes — identical to Left | Custom OTA (0xC4/0xC5) | 2BFKR-G2 |
| **G2 Charging Case** | Unknown ARM MCU (STM32-like) | Yes — `firmware/box.bin` | Via G2 glasses (wired relay) | (part of G2) |
| **R1 Ring** | Nordic nRF5x (likely nRF52832/33) | Yes — separate Nordic DFU | FE59 Buttonless + MCUmgr SMP | 2BFKR-R01 |
| **R1 Charging Cradle** | None | **No firmware** — passive | N/A | 2BFKR-R1C |

**Key facts:**
- G2 Left and Right run **identical firmware images**. Left/right identity is a runtime BLE name config (`Even G2_32_L_xxx` vs `Even G2_32_R_xxx`), not a build split.
- The Charging Case has no direct BLE connection to the phone. Firmware is relayed through the G2 glasses via wired inter-eye link.
- The R1 Charging Cradle is electrically passive with no microcontroller, BLE radio, or DFU capability.

---

## 2. Firmware-to-Hardware Map

### 2.1 EVENOTA Package (G2 + Case)

The primary G2 firmware is distributed as a single EVENOTA package downloaded from `cdn.evenreal.co`. It contains **6 components** targeting 5 different hardware chips:

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ EVENOTA Package (e.g. g2_2.0.7.16.bin, 3.96 MB)                                      │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ Component              │ Target Hardware         │ Target Device    │ Wrapper Format │
├────────────────────────┼─────────────────────────┼──────────────────┼────────────────┤
│ ota/s200_firmware_ota  │ Apollo510b main SoC     │ G2 Left + Right  │ Preamble+ARM VT│
│ ota/s200_bootloader    │ Apollo510b bootloader   │ G2 Left + Right  │ Raw ARM VT     │
│ firmware/ble_em9305    │ EM9305 BLE radio        │ G2 Left + Right  │ Segmented patch│
│ firmware/codec         │ GX8002B audio codec     │ G2 Left + Right  │ FWPK (dual)    │
│ firmware/touch         │ CY8C4046FNI touch ctrl  │ G2 Left + Right  │ FWPK (single)  │
│ firmware/box           │ Case ARM MCU            │ G2 Charging Case │ EVEN wrapper   │
└────────────────────────┴─────────────────────────┴──────────────────┴────────────────┘
```

Each component targets a specific IC on the G2 hardware BOM:

| Component | EVENOTA Type | IC | Interface to Apollo510b | Flash Method |
|-----------|-------------|-----|------------------------|-------------|
| `s200_firmware_ota` | 0 (Main FW) | Ambiq Apollo510b | Internal | Direct flash write at `0x00438000` |
| `s200_bootloader` | 1 (Bootloader) | Ambiq Apollo510b | Internal | Direct flash write at boot region |
| `touch` | 3 (Touch) | Cypress CY8C4046FNI | I2C (`drv_cy8c4046fni.c`) | I2C DFU to touch controller |
| `codec` | 4 (Codec) | Nationalchip GX8002B | TinyFrame (`drv_gx8002b.c`) | Serial bootloader (BINH stage1+2) |
| `ble_em9305` | 5 (BLE) | EM Micro EM9305 | HCI (`srv_em9305*.c`) | HCI patch records → `0x00300000` region |
| `box` | 6 (Box/Case) | Unknown ARM MCU | Wired link through frame | Relayed from G2 to case via `glasses_case` proto |

### 2.2 Nordic DFU Bundles (Legacy/Auxiliary, in Even.app)

Three Nordic DFU packages are bundled as Flutter assets in Even.app. These target an **nRF52840** and use standard Nordic Secure DFU with ECDSA P-256 signed init packets:

| Package | Contents | Size | Purpose |
|---------|----------|------|---------|
| `B210_ALWAY_BL_DFU_NO.zip` | Bootloader (debug, fail-safe) | 24,180 B | Emergency recovery bootloader |
| `B210_BL_DFU_NO_v2.0.3.0004.zip` | Bootloader (debug, versioned) | 24,420 B | Production bootloader update |
| `B210_SD_ONLY_NO_v2.0.3.0004.zip` | SoftDevice S140 v7.0.0 | 153,140 B | BLE stack update |

**Role uncertainty**: These target nRF52840 hardware (1 MB flash, S140 SoftDevice), but the G2 main SoC is Apollo510b with EM9305 BLE. The nRF52840 DFU path may serve:
- The EM9305 BLE radio's auxiliary nRF-based bootstrap
- A legacy G1-generation update path
- The R1 Ring (which uses Nordic nRF5x)

Both bootloaders accept dual SoftDevice FWIDs (`0x0100` = S140 v7.0.0, `0x0102` = S140 v7.2.0), enabling field upgrade of the BLE stack. Both are debug builds (`is_debug=true`) for easier recovery.

### 2.3 R1 Ring Firmware

The R1 Ring uses a completely separate update pipeline from the G2:

| Aspect | Detail |
|--------|--------|
| **SoC** | Nordic nRF5x (likely nRF52832 or nRF52833) |
| **DFU Entry** | FE59 Buttonless Secure DFU service (BLE SIG registered) |
| **Transfer** | SMP/MCUmgr via characteristic `DA2E7828-FBCE-4E01-AE9E-261174997C48` |
| **Image Mgmt** | Dual-image slot (MCUboot): `bootable`, `pending`, `confirmed`, `active`, `permanent` |
| **Upgrade Modes** | `TEST_ONLY`, `CONFIRM_ONLY`, `TEST_AND_CONFIRM`, `UPLOAD_ONLY` |
| **Distribution** | Current corpus contains Even.app-bundled Nordic DFU artifacts; standalone ring runtime image not yet isolated |
| **Version Boundary** | `v2.03.00.01` — feature/protocol changes above vs. below |

Ring firmware is NOT included in the EVENOTA package. Current live API sweeps on `2026-03-05` did not surface a separate ring firmware CDN artifact: `GET /v2/g/check_latest_firmware` continued to return only G2 EVENOTA packages, while `GET /v2/g/check_firmware` remained unresolved with `code: 1401` (`Params error`). Until a working ring-specific route is confirmed, the taggable R1 artifacts in this repo are the Even.app-bundled Nordic DFU bundles now materialized under `captures/firmware/tagged/r1-ring/`.

Bundled Nordic auxiliary binaries now have instruction-level startup/wait anchors in local analysis:
- Bootloader path: `0x000F83D8 -> 0x000F8200 -> 0x000FADC8/0x000FADBC`, init-walker loop `0x000F84DE -> 0x000F84CE`.
- SoftDevice path: pre-reset idle loop `0x00025FDC (wfe)` + `0x00025FDE -> 0x00025FDC`, then reset dispatch `0x00025FE0 -> 0x00001108`.
- Artifact: `captures/firmware/analysis/2026-03-05-r1-nordic-stage2-idle-paths.md`

**MCUmgr extended capabilities** available on the R1:
- Filesystem read/write (CRC32 + SHA-256 checksums)
- Crash dump retrieval (div0, jump0, ref0, assert, watchdog)
- Runtime stats and log retrieval
- Bootloader info queries
- SUIT envelope support (secure firmware delivery)
- XIP (Execute-in-Place) from flash

### 2.4 R1 Charging Cradle

**No firmware.** The R1 Charging Cradle (FCC ID: 2BFKR-R1C, IC: 32408-R1C) is a passive accessory that provides inductive/contact charging to the R1 Ring. It has no microcontroller, no BLE radio, and no update capability.

---

## 3. EVENOTA Container Format

### 3.1 Package Structure

```
┌─────────────────────────────────────────────────────────┐
│ Outer Header (160 bytes = 0xA0)                         │
│   0x00: "EVENOTA\0" magic (8 bytes)                     │
│   0x08: entry_count (LE32) = 6                          │
│   0x10: build_date (16 bytes, null-padded)              │
│   0x20: build_time (16 bytes, null-padded)              │
│   0x30: version (16 bytes, null-padded)                 │
│   0x40: TOC entries (N × 16 bytes)                      │
├─────────────────────────────────────────────────────────┤
│ Entry 1: firmware/codec.bin      [sub-header + payload] │
│ Entry 2: firmware/ble_em9305.bin [sub-header + payload] │
│ Entry 3: firmware/touch.bin      [sub-header + payload] │
│ Entry 4: firmware/box.bin        [sub-header + payload] │
│ Entry 5: ota/s200_bootloader.bin [sub-header + payload] │
│ Entry 6: ota/s200_firmware_ota   [sub-header + payload] │
└─────────────────────────────────────────────────────────┘
```

### 3.2 TOC Entry (16 bytes each)

| Offset | Size | Field |
|--------|------|-------|
| +0x00 | 4 | Entry ID (1-based, LE32) |
| +0x04 | 4 | Data offset (absolute, LE32) |
| +0x08 | 4 | Data size (includes 128-byte sub-header, LE32) |
| +0x0C | 4 | CRC32C checksum (non-reflected, MSB-first) |

### 3.3 Per-Entry Sub-Header (128 bytes = 0x80)

| Offset | Size | Field |
|--------|------|-------|
| +0x00 | 8 | Padding (zeros) |
| +0x08 | 4 | Payload size (LE32, = data_size - 128) |
| +0x0C | 4 | CRC32C checksum (matches TOC checksum) |
| +0x14 | 4 | Magic `EVEN` |
| +0x24 | 4 | Entry type (LE32): 0=Main, 1=Boot, 3=Touch, 4=Codec, 5=BLE, 6=Box |
| +0x28 | 4 | Format version = 3 |
| +0x30 | 32 | Filename (null-padded ASCII) |

### 3.4 Checksum Algorithm

**CRC32C (Castagnoli), non-reflected/MSB-first:**
- Polynomial: `0x1EDC6F41`
- Init: `0x00000000`, XOR-out: `0x00000000`
- Coverage: payload bytes only (`sub[0x80 : data_size]`)
- Both TOC and sub-header checksums are identical (validated across all 5 versions)

### 3.5 Entry Layout (v2.0.7.16 example)

Entries are packed contiguously with zero gaps:

| ID | Offset | Size | End | Gap |
|---:|---:|---:|---:|---:|
| 1 | `0x0000B0` | `0x04E00C` | `0x04E0BC` | 0 |
| 2 | `0x04E0BC` | `0x033C6C` | `0x081D28` | 0 |
| 3 | `0x081D28` | `0x0085A0` | `0x08A2C8` | 0 |
| 4 | `0x08A2C8` | `0x00D880` | `0x097B48` | 0 |
| 5 | `0x097B48` | `0x02418F` | `0x0BBCD7` | 0 |
| 6 | `0x0BBCD7` | `0x30AA40` | `0x3C6717` | 0 (EOF) |

---

## 4. Sub-Component Wrapper Formats

Each EVENOTA entry uses a different internal wrapper format appropriate for its target hardware.

### 4.1 Main Application — Preamble + ARM Vector Table

`ota/s200_firmware_ota.bin` has a 32-byte preamble before the standard ARM Cortex-M55 vector table:

```
+0x00: LE32  size field (low 24 bits = payload size)
+0x04: LE32  CRC32 over bytes [0x08..end]
+0x08: 8×00  reserved
+0x10: LE32  flags (0xCB)
+0x14: LE32  load address = 0x00438000
+0x18: 8×00  reserved
+0x20: ARM vector table (SP=0x2007FB00, Reset=0x005C9777)
```

The raw firmware image (without preamble) = `ota_s200_firmware_ota.bin[0x20:]`.

### 4.2 Bootloader — Raw ARM Vector Table

`ota/s200_bootloader.bin` is a raw ARM Cortex-M55 image with the vector table at offset 0:
- SP: `0x2007FB00`
- Reset: `0x004324CF`
- Execution span: `0x00410000` – `0x00438000` (bootloader region)
- Hands off to application at `0x00438000` via VTOR relocation

### 4.3 FWPK (Touch + Codec)

Both touch and codec firmware use `FWPK` magic headers but with different checksum semantics:

**Touch (`firmware/touch.bin`):**
- Header: 0x20 bytes, magic `FWPK`
- Checksum at `+0x1C`: CRC32C (Castagnoli, reflected, init/xor `0xFFFFFFFF`) over `file[0x20:]`
- Contains ARM vector table at `+0x20` (SP=`0x20002000`, Reset=`0x000044D9`)

**Codec (`firmware/codec.bin`):**
- Header: 0x30 bytes, magic `FWPK`
- Dual-segment layout:
  - Segment 0: `file[0x30 : 0x30 + seg0_size]`, CRC32 (standard zlib) at `+0x1C`
  - Segment 1: offset/size at `+0x28`/`+0x24`, CRC32 at `+0x2C`
- Segment 1 contains two `BINH` boot image blocks (GX8002B serial bootloader protocol):
  - Block 1 at offset `0x0`, Block 2 at offset `0x2D970`
  - Each: `BINH` magic + `0x55AA55AA` sync + stage1_size (0x200) + stage2_size (0x3000)

### 4.4 EVEN Wrapper (Box/Case)

`firmware/box.bin` uses an `EVEN`-magic wrapper:

```
+0x00: "EVEN" magic (4 bytes)
+0x04: 4 bytes padding
+0x08: BE32  payload length (file_size - 0x20)
+0x0C: BE32  checksum = sum_be32(file[0x20 : 0x20 + payload_len])
+0x10: 16 bytes padding
+0x20: ARM vector table (SP=0x20002C88, Reset=0x08000145)
```

The Reset vector `0x08000145` indicates an STM32-like flash base (`0x08000000`), suggesting the case MCU is an STM32 or compatible ARM Cortex-M.

Checksum algorithm: **32-bit big-endian additive checksum** — sum all 4-byte big-endian words in the payload region. Validated across all 5 firmware versions.

### 4.5 EM9305 Segmented Patch

`firmware/ble_em9305.bin` is a segmented patch file for the EM9305 BLE radio (NOT a flat MCU image):

| Offset | Size | Field | Value |
|--------|------|-------|-------|
| 0x00 | 4 | Version | `0x04040200` |
| 0x04 | 4 | Total payload length | 211,824 |
| 0x08 | 4 | Record count | 4 |
| 0x0C | 4 | Erase pages | 29 |

Each record (12 bytes) specifies: `(file_offset, size, target_address)` targeting the EM9305's `0x00300000` memory region. The Apollo510b writes these records to the EM9305 via HCI commands (`service_em9305_dfu.c`).

---

## 5. BLE Firmware Transfer Protocol

### 5.1 G2 OTA Transfer (EVENOTA → Glasses)

The phone-to-glasses firmware update uses a custom protocol over the G2 BLE file service:

```
Phone (Even.app)                                G2 Glasses
  │                                                  │
  │  1. POST /v2/g/check_firmware                    │
  │     ─────────▶ api2.evenreal.co                  │
  │     ◀───────── { otaInfo, downloadUri }          │
  │                                                  │
  │  2. GET downloadUri                              │
  │     ─────────▶ cdn.evenreal.co                   │
  │     ◀───────── EVENOTA package                   │
  │                                                  │
  │  3. OTA_TRANSMIT_START (via 0xC4/0xC5 file svc)  │
  │     ──────────────────────────────────▶          │
  │  4. OTA_TRANSMIT_INFORMATION                     │
  │     ──────────────────────────────────▶          │
  │  5. OTA_TRANSMIT_FILE (chunked data)             │
  │     ──────────────────────────────────▶          │
  │  6. OTA_TRANSMIT_RESULT_CHECK                    │
  │     ──────────────────────────────────▶          │
  │     ◀──────────── OTA_RECV_RSP_SUCCESS           │
  │  7. System restart                               │
  │     ◀──────────── (glasses reboot)               │
```

**BLE transport details:**
- **Service IDs**: `0xC4-00` (file commands), `0xC5-00` (file data)
- **BLE characteristic**: `0x7401` (TX, phone→glasses write), `0x7402` (RX, glasses→phone notify)
- **Pipe type**: `BleG2PsType.File` (type 1)
- **Max packet payload**: 244 bytes (observed)
- **Packet format**: Standard G2 AA-envelope with CRC-16
- **L2CAP**: `CBL2CAPChannel` delegate present in Even.app — may be used for higher-throughput OTA transfer

**OTA header sent during TRANSMIT_START** (`BleG2OtaHeader`):
- `otaMagic1`, `otaMagic2` — validation bytes
- `componentNum` — number of firmware components
- Per-component: `fileType`, `fileLength`, `fileCrc32` (CRC32C), `fileSign`, `fileId`

**Wire tokens during transfer:**
- `fileTransmitCid` — transfer channel ID
- `packetLen`, `packetSerialNum`, `packetTotalNum` — chunk sequencing
- `partsTotal`, `currentPart` — multi-part progress
- `packetAck` — acknowledgment

**OTA prerequisite**: Device must be charging AND battery above 50%.

**OTA response codes:**

| Code | Constant | Description |
|------|----------|-------------|
| 0 | `OTA_RECV_RSP_SUCCESS` | Transfer successful |
| 1 | `OTA_RECV_RSP_FAIL` | Generic failure |
| 2 | `OTA_RECV_RSP_HEADER_ERR` | Invalid OTA header |
| 3 | `OTA_RECV_RSP_PATH_ERR` | Invalid file path |
| 4 | `OTA_RECV_RSP_CRC_ERR` | CRC32C mismatch |
| 5 | `OTA_RECV_RSP_FLASH_WRITE_ERR` | Flash write failure |
| 6 | `OTA_RECV_RSP_NO_RESOURCES` | Insufficient resources |
| 7 | `OTA_RECV_RSP_TIMEOUT` | Transfer timeout |
| 8 | `OTA_RECV_RSP_CHECK_FAIL` | Result verification failed |
| 9 | `OTA_RECV_RSP_SYS_RESTART` | System restarting |
| 10 | `OTA_RECV_RSP_UPDATING` | Update in progress |

### 5.2 G2 Sub-Component Flashing

After the phone transfers the EVENOTA package to the G2 glasses, the Apollo510b firmware orchestrates flashing each sub-component to its target hardware:

| Component | Flash Path | Protocol |
|-----------|-----------|----------|
| `s200_firmware_ota` | Direct internal flash write | ARM flash API at `0x00438000` |
| `s200_bootloader` | Direct internal flash write | ARM flash API at boot region |
| `ble_em9305` | Apollo510b → EM9305 | HCI commands (`service_em9305_dfu.c`, `AT^EM9305`) |
| `codec` | Apollo510b → GX8002B | TinyFrame serial protocol (`drv_gx8002b.c`, BINH bootloader) |
| `touch` | Apollo510b → CY8C4046FNI | I2C DFU (`drv_cy8c4046fni.c`) |
| `box` | Apollo510b → Case MCU | Wired link relay (`glasses_case` protobuf, `GlassesCaseDataPackage`) |

The case firmware (`box.bin`) is notable: the phone never communicates directly with the case. The EVENOTA package is sent to the G2 glasses, which then relay the case firmware to the charging case MCU over the wired inter-eye/case link.

### 5.3 R1 Ring DFU Transfer

The R1 Ring uses standard Nordic DFU, completely separate from the G2 OTA path:

```
Phone (Even.app)                               R1 Ring
  │                                                │
  │  1. Write to FE59 Buttonless service           │
  │     ─────────────────────────────────▶         │
  │     (ring resets into bootloader mode)         │
  │                                                │
  │  2. MCUmgr SMP Upload (DA2E7828-... char)      │
  │     ─────────────────────────────────▶         │
  │  3. SMP Test / Confirm image slot              │
  │     ─────────────────────────────────▶         │
  │  4. SMP Reset                                  │
  │     ─────────────────────────────────▶         │
  │     (ring boots new firmware from slot)        │
```

**BLE UUIDs:**
- `FE59` — Nordic Buttonless Secure DFU (BLE SIG registered)
- `DA2E7828-FBCE-4E01-AE9E-261174997C48` — SMP/MCUmgr data transfer
- `8EC90001-...` through `8EC90004-...` — Nordic Secure DFU service

**MCUboot dual-image slots**: The ring maintains two firmware image slots. New firmware is uploaded to the inactive slot, tested, and either confirmed or rolled back. States: `bootable`, `pending`, `confirmed`, `active`, `permanent`.

### 5.4 Nordic DFU Bundles (Legacy/Auxiliary)

The three B210 DFU packages bundled in Even.app use standard Nordic Secure DFU:

```
manifest.json → bin_file + dat_file
```

Each `.dat` file is a protobuf-encoded init packet containing:
- `hw_version = 52` (Nordic nRF52 family)
- `sd_req = [0x0100, 0x0102]` (accepts S140 v7.0.0 or v7.2.0)
- ECDSA P-256 signature over the binary

Tagged copies for these ring-oriented bundles now live at:
- `captures/firmware/tagged/r1-ring/failsafe-bootloader/`
- `captures/firmware/tagged/r1-ring/bootloader-2.0.3.0004/`
- `captures/firmware/tagged/r1-ring/softdevice-2.0.3.0004/`

**DFU verification key** (identical in both bootloaders):
```
X: 7a7de304b95ede3310178189bdf9828b9149b5acdcc6365e3fb7b58b4456119d
Y: 553442c9df04a6a417e55b8184501a30813e7f3c6395f1f66dd747c49f0fa398
```

---

## 6. Flash Memory Maps

### 6.1 Apollo510b (G2 Runtime — Primary)

```
Apollo510b Internal Flash:
  ┌──────────────────────────────────────────────────────────────┐
  │ 0x00410000 │ Bootloader (s200_bootloader.bin)   │  ~148 KB   │
  │            │   Vector: SP=0x2007FB00            │            │
  │            │   Reset=0x004324CF                 │            │
  │            │   VTOR relocation + app handoff    │            │
  ├────────────┼────────────────────────────────────┼────────────┤
  │ 0x00438000 │ Main Application                   │  ~3.1 MB   │
  │            │   (s200_firmware_ota.bin[0x20:])   │            │
  │            │   Vector: SP=0x2007FB00            │            │
  │            │   Reset=0x005C9777                 │            │
  │            │   Execute: 0x438000–0x742A00       │            │
  └────────────┴────────────────────────────────────┴────────────┘

Apollo510b SRAM (512 KB):
  0x20000000 – 0x2007FFFF
  Stack pointer: 0x2007FB00

External QSPI Flash (32 MB — Macronix MX25U25643G):
  ┌─────────────────────────────────────────────────────────────┐
  │ LittleFS filesystem                                         │
  │   L:/ and R:/ partitions                                    │
  │   Log files, notification whitelist, user data              │
  │   LVGL assets, fonts, animations                            │
  └─────────────────────────────────────────────────────────────┘

EM9305 BLE Radio Memory:
  0x00300000 – 0x003xxxxx  (patch target addresses)
  4 records: config, params, handler, main patch
  29 pages erased during update

GX8002B Audio Codec:
  Dual BINH boot stages via TinyFrame serial:
    Stage 1: 0x200 bytes (loader)
    Stage 2: 0x3000 bytes (main codec firmware)
```

### 6.2 nRF52840 (Legacy DFU Bootloader Path)

```
nRF52840 Flash (1 MB):
  ┌────────────┬────────────────────────────────────┬────────────┐
  │ 0x00000000 │ MBR (Master Boot Record)           │   4 KB     │
  ├────────────┼────────────────────────────────────┼────────────┤
  │ 0x00001000 │ SoftDevice S140 v7.0.0             │ 153 KB     │
  │            │   FWID 0x0100, BLE API v140        │            │
  │            │   SRAM boundary: 0x200059C4        │            │
  ├────────────┼────────────────────────────────────┼────────────┤
  │ 0x00027000 │ Application region                 │ ~836 KB    │
  ├────────────┼────────────────────────────────────┼────────────┤
  │ 0x000F8000 │ Bootloader (Secure DFU)            │  24 KB     │
  │            │   ECDSA P-256 verification         │            │
  │            │   DFU advertised name: "B210_DFU"  │            │
  ├────────────┼────────────────────────────────────┼────────────┤
  │ 0x000FE000 │ Bootloader Settings                │   4 KB     │
  ├────────────┼────────────────────────────────────┼────────────┤
  │ 0x000FF000 │ MBR Parameters                     │   4 KB     │
  └────────────┴────────────────────────────────────┴────────────┘

nRF52840 RAM (256 KB):
  0x20000000 – 0x200059C3: SoftDevice (~22.4 KB)
  0x200059C4 – 0x2003FFFF: Application (~233 KB)
```

### 6.3 Case MCU (STM32-like)

Minimal information from the ARM vector table in `box.bin`:
- Flash base: `0x08000000` (STM32 convention)
- Reset vector: `0x08000145`
- Stack pointer: `0x20002C88` (~11 KB SRAM)

---

## 7. Firmware Version History

### 7.1 Version Evolution Table

Data from 5 acquired EVENOTA packages:

| Version | Build Date | Main App | Bootloader | Touch | Box | Codec | BLE EM9305 |
|---------|-----------|----------|------------|-------|-----|-------|-----------|
| **2.0.1.14** | 2025-12-11 | 2,471,336 | 147,364 | 27,808 | 53,296 | 319,372 | 211,948 |
| **2.0.3.20** | 2025-12-31 | 3,069,108 | 147,360 | 28,192 | 55,120 | 319,372 | 211,948 |
| **2.0.5.12** | 2026-01-17 | 3,158,492 | 147,657 | 28,320 | 55,120 | 319,372 | 211,948 |
| **2.0.6.14** | 2026-01-29 | 3,184,984 | 147,657 | 34,080 | 55,296 | 319,372 | 211,948 |
| **2.0.7.16** | 2026-02-13 | 3,189,184 | 147,727 | 34,080 | 55,296 | 319,372 | 211,948 |

### 7.2 Component Stability Analysis

| Component | Stable? | Notes |
|-----------|---------|-------|
| **Codec** (GX8002B) | **Byte-identical** across all 5 versions | 319,372 bytes, never changes |
| **BLE** (EM9305) | **Byte-identical** across all 5 versions | 211,948 bytes, never changes |
| **Touch** (CY8C4046FNI) | Changed twice | +22% at v2.0.6.14 (27,808 → 34,080) |
| **Box** (Case) | Changed twice | +3.7% at v2.0.3.20 (53,296 → 55,120), +0.3% at v2.0.6.14 |
| **Bootloader** | Changed twice | Minor growth (+363 bytes total over 5 versions) |
| **Main App** | Changed every version | +29% over 2 months (2.47 MB → 3.19 MB) |

The codec and BLE radio firmware are completely stable — identical binaries ship in every EVENOTA package. The main application firmware grows with each release as features are added.

This stability data is codified in the iOS SDK's `G2FirmwareVersionRegistry` (in `G2EVENOTAParser.swift`), which contains known checksums, component sizes, and changelog text for all 5 versions. Downloaded EVENOTA packages are automatically cross-validated against this registry.

### 7.3 CDN Distribution

Firmware is served via threshold-based version matching:

| App `versionName` Range | Returns FW Version | `minAppVer` | CDN `fileSign` (MD5) |
|------------------------|-------------------|-------------|---------------------|
| `0.0.1` – `2.0.2` | 2.0.1.14 | `0.0.0` | `09fe9c0df7b14385c023bc35a364b3a9` |
| `2.0.3` – `2.0.4` | 2.0.3.20 | `2.0.3` | `57201a6e7cd6dadeee1bdb8f6ed98606` |
| `2.0.5` | 2.0.5.12 | `2.0.5` | `53486f03b825cb22d13e769187b46656` |
| `2.0.6` | 2.0.6.14 | `2.0.6` | `0c9f9ca58785547278a5103bc6ae7a09` |
| `2.0.7` + | 2.0.7.16 | `2.0.7` | `650176717d1f30ef684e5f812500903c` |

API: `GET https://api2.evenreal.co/v2/g/check_latest_firmware` (requires auth headers).
CDN: `https://cdn.evenreal.co/firmware/{fileSign}.bin` (**no auth required**).

---

## 8. Firmware Acquisition

### 8.1 iOS SDK Download

The EvenG2Shortcuts app includes a built-in firmware download and parsing pipeline:

```swift
// Check for latest firmware
let response = try await G2FirmwareAPIClient.checkLatestFirmwareFull()
guard let fw = response.data, let subPath = fw.subPath else { return }

// Download from CDN (no auth needed) with MD5 verification
let binary = try await G2FirmwareAPIClient.downloadFirmware(
    subPath: subPath,
    expectedMD5: fw.fileSign,
    expectedSize: fw.fileSize
)

// Parse EVENOTA container and verify CRC32C checksums
let package = try G2EVENOTAParser.parse(binary)
print(package.summary)  // "2.0.7.16 (2025-11-29 11:34:32, 6 components, 3.8 MB)"
```

### 8.2 Automated Download (Python)

```bash
# Fetch latest firmware (auto-detects auth from captures/)
python3 tools/fetch_latest_firmware.py --extract

# Output:
#   captures/firmware/g2_<version>.bin           ← raw EVENOTA package
#   captures/firmware/g2_<version>.json          ← API metadata
#   captures/firmware/extracted/                 ← individual component binaries
#     firmware_codec.bin
#     firmware_ble_em9305.bin
#     firmware_touch.bin
#     firmware_box.bin
#     ota_s200_bootloader.bin
#     ota_s200_firmware_ota.bin
#     evenota_metadata.json
```

### 8.3 Local Firmware Archive

All 5 versions are archived with extracted components:

```
captures/firmware/
├── g2_extracted/                    ← latest (v2.0.7.16) extracted
│   ├── evenota_metadata.json
│   ├── firmware_codec.bin
│   ├── firmware_ble_em9305.bin
│   ├── firmware_touch.bin
│   ├── firmware_box.bin
│   ├── ota_s200_bootloader.bin
│   ├── ota_s200_firmware_ota.bin
│   └── s200_firmware_raw.bin        ← firmware_ota without 32-byte preamble
├── versions/
│   ├── v2.0.1.14/extracted/         ← per-version extractions
│   ├── v2.0.3.20/extracted/
│   ├── v2.0.5.12/extracted/
│   ├── v2.0.6.14/extracted/
│   └── v2.0.7.16/extracted/
├── tagged/
│   ├── g2-case/<version>/           ← explicit case-image tags from G2 EVENOTA
│   │   ├── firmware_box.bin
│   │   └── artifact.json
│   └── r1-ring/                     ← explicit ring DFU tags from Even.app bundles
│       ├── failsafe-bootloader/
│       ├── bootloader-2.0.3.0004/
│       └── softdevice-2.0.3.0004/
├── B210_ALWAY_BL_DFU_NO/           ← Nordic DFU bundles (from Even.app)
├── B210_BL_DFU_NO_v2.0.3.0004/
└── B210_SD_ONLY_NO_v2.0.3.0004/
```

Inventory artifact:

- `captures/firmware/analysis/2026-03-05-tagged-firmware-artifacts.md`
- `captures/firmware/analysis/2026-03-05-tagged-firmware-artifacts.json`

---

## 9. Naming Conventions

| Term | Meaning |
|------|---------|
| **S200** | Product designation for G2 glasses (GATT Device Information) |
| **B210** | Board version 2, Revision 10 (internal hardware revision) |
| **EVENOTA** | Even Realities' custom multi-component OTA container format |
| **FWPK** | Firmware Package — wrapper for touch and codec binaries |
| **EVEN** | Wrapper for box/case firmware (magic bytes, BE checksums) |
| **BINH** | Binary Header — GX8002B codec bootloader boot stage format |
| **SMP** | Simple Management Protocol (MCUmgr, used for R1 Ring DFU) |
| **FE59** | BLE SIG UUID for Nordic Buttonless Secure DFU service |

---

## Related Documents

- [firmware-updates.md](firmware-updates.md) — API details, auth capture, download scripts
- [firmware-reverse-engineering.md](firmware-reverse-engineering.md) — Full binary analysis, hardware BOM, AT commands, source tree
- [even-app-reverse-engineering.md](even-app-reverse-engineering.md) — Even.app structure, DFU bootloader analysis, protobuf modules
- [../protocols/packet-structure.md](../protocols/packet-structure.md) — G2 packet format used by file transfer
- [../protocols/services.md](../protocols/services.md) — Service ID registry including 0xC4/0xC5 file services
- [../devices/r1-ring.md](../devices/r1-ring.md) — R1 Ring BLE protocol and dual-link architecture
