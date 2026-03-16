# Image Formats and Boot Path

This document records the clean-room view of the firmware image/container formats and the Apollo boot handoff path.

## Identified Format Matrix

| Artifact | State | Wrapper / Container | Check / Integrity | Key Anchors |
|---|---|---|---|---|
| `ota_s200_firmware_ota.bin` | Identified | 32-byte preamble + raw ARM image | CRC32 over `file[0x08:]` | load address `0x00438000`, reset `0x005C9777` |
| `ota_s200_bootloader.bin` | Identified | Raw ARM image | Vector-table sanity + bootloader-internal OTA checks | base `0x00410000`, reset `0x004324CF` |
| `firmware_ble_em9305.bin` | Partial | 16-byte patch header + record table + payload records | header total + record-table consistency | target region `0x00300000+` |
| `firmware_codec.bin` | Partial | `FWPK` with two segments and BINH blocks | CRC32 on segments | codec stage loader blocks |
| `firmware_touch.bin` | Identified container | `FWPK` single-segment payload | CRC32C on payload | reset `0x000044D9` |
| `firmware_box.bin` | Identified container | `EVEN` wrapper + raw ARM payload | additive 32-bit word sum, big-endian | reset `0x08000145` |
| `B210_ALWAY_BL_DFU_NO`, `B210_BL_DFU_NO_v2.0.3.0004`, `B210_SD_ONLY_NO_v2.0.3.0004` | Partial | Nordic DFU package set | Nordic DFU/MCUboot flow | ring-side bootloader and SoftDevice artifacts; standalone app still missing |
| R1 runtime image | Blocked | Missing from corpus | Unknown | No standalone runtime bundle available |

## Apollo Main App Format

### Identified

`ota_s200_firmware_ota.bin` preamble:

| Offset | Field | Identified Meaning |
|---|---|---|
| `+0x00` | Size field | low 24 bits carry payload size |
| `+0x04` | CRC32 | standard CRC32 over `file[0x08:]` |
| `+0x10` | Flags | stable field, exact semantics still open |
| `+0x14` | Load address | `0x00438000` |

The payload after the preamble is a directly executable ARM image with the vector table at `file[0x20:]`.

### Inferred

- The flags field likely participates in boot/install policy.
- Any clean-room writer will need to preserve the existing preamble contract before live flashing is attempted.

## Apollo Bootloader and Handoff

### Identified

- Bootloader base: `0x00410000`
- App base: `0x00438000`
- VTOR register used in handoff: `0xE000ED08`
- Handoff sequence:
  1. write VTOR to app base
  2. load MSP from app vector table
  3. load reset handler from app vector table
  4. branch to app reset handler

### Partial

- Boot metadata selection/validation logic is clearly present but not fully decoded structurally.
- Recovery and rollback semantics are bounded but not authoritative enough for a replacement boot story.

## Peripheral Bundle Formats

### EM9305 BLE Patch

#### Identified

- 16-byte header
- record count and total payload fields
- four records targeting `0x00300000`, `0x00300400`, `0x00302000`, and `0x00302400`

#### Inferred

- records correspond to config, parameters, handlers, and main patch code

#### Unidentified

- function-level semantics inside the controller patch

### GX8002B Codec Bundle

#### Identified

- `FWPK` magic
- two-segment container
- segment CRC32 values
- embedded `BINH` boot-image blocks used by the Apollo host

#### Inferred

- one header field is labeled as a stage-2 baud-rate field in surrounding evidence, but its semantics are not fully settled

#### Unidentified

- full codec-local command/state contract

### CY8C4046FNI Touch Bundle

#### Identified

- `FWPK` magic
- payload CRC32C
- vector table directly after 0x20-byte header
- I2C DFU ownership from Apollo side

#### Inferred

- growth in later versions reflects added proximity baseline and fast-click behavior

#### Unidentified

- row-level bootloader/update grammar and internal calibration tables

### Case Bundle

#### Identified

- `EVEN` wrapper
- big-endian payload length and additive checksum
- ARM payload begins at `+0x20`
- reset/startup and scheduler handoff are instruction-anchored

#### Inferred

- MCU is STM32-like
- dual-bank or bank-swap behavior is real

#### Unidentified

- exact MCU part number
- full relay/UART opcode grammar

## Unidentified / Blocked Format Areas

| Area | Why It Matters |
|---|---|
| Exact boot metadata structure | Needed for any safe boot-image replacement or recovery tooling |
| Exact rollback / validity policy | Needed before live bootloader interaction beyond parsing |
| Exact meanings of some FWPK flag/header fields | Needed for full clean-room packer parity |
| Exact case bank metadata format | Needed for full case relay/update compatibility |
| Standalone R1 runtime image | Needed before ring runtime re-implementation can start |

## Clean-Room Guidance

- Build parsers and validators for all known container types first.
- Only plan to emit the Apollo main-app preamble in the near term.
- Treat bootloader, EM9305, codec, touch, case, and R1 formats as recognition/parsing targets unless stronger closure appears.

## Source Documents

- `../firmware/s200-firmware-ota.md`
- `../firmware/s200-bootloader.md`
- `../firmware/ble-em9305.md`
- `../firmware/codec-gx8002b.md`
- `../firmware/touch-cy8c4046fni.md`
- `../firmware/box-case-mcu.md`
- `../firmware/device-boot-call-trees.md`
