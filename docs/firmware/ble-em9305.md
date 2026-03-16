# firmware_ble_em9305.bin — EM9305 BLE Radio Patch

Firmware patch file for the EM Microelectronic EM9305 BLE radio coprocessor. This is NOT a flat MCU image — it is a segmented patch container with 4 records targeting the EM9305's `0x00300000` memory region.

**Target**: EM9305 BLE radio (EM Microelectronic, ARC EM / ARCv2 ISA)
**EVENOTA entry**: ID 2, type 5 (BLE Radio)
**Interface**: HCI from Apollo510b (`service_em9305_dfu.c`, `AT^EM9305`)
**Stability**: Byte-identical across all 5 firmware versions (211,948 bytes)

---

## 1. File Structure

```
┌──────────────────────────────────────────────────────────────┐
│ Header (16 bytes)                                            │
│   +0x00: LE32  version         = 0x04040200                  │
│   +0x04: LE32  total_payload   = 0x00033B70 (211,824 bytes)  │
│   +0x08: LE32  record_count    = 4                           │
│   +0x0C: LE32  erase_pages     = 29                          │
├──────────────────────────────────────────────────────────────┤
│ Record Table (4 × 12 bytes = 48 bytes)                       │
│   Record 0: config  (224 B → 0x00300000)                     │
│   Record 1: params  (656 B → 0x00300400)                     │
│   Record 2: handler (56 B  → 0x00302000)                     │
│   Record 3: main    (211,400 B → 0x00302400)                 │
├──────────────────────────────────────────────────────────────┤
│ Payload Data (211,824 bytes)                                 │
│   Record 0 data at file[0x7C]                                │
│   Record 1 data at file[0x15C]                               │
│   Record 2 data at file[0x3EC]                               │
│   Record 3 data at file[0x424]                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Header Fields

| Offset | Size | Field | Value | Notes |
|--------|------|-------|-------|-------|
| +0x00 | 4 | Version | `0x04040200` | Patch format version |
| +0x04 | 4 | Total payload | `0x00033B70` | 211,824 bytes (sum of all record sizes) |
| +0x08 | 4 | Record count | `4` | Number of patch records |
| +0x0C | 4 | Erase pages | `29` | Flash pages to erase before patching |

---

## 3. Patch Record Table

Each record is 12 bytes: `(file_offset, size, target_address)`

| Record | File Offset | Size | Target Address | Purpose |
|--------|------------|------|---------------|---------|
| 0 | `0x0000007C` | `0x000000E0` (224 B) | `0x00300000` | Configuration data |
| 1 | `0x0000015C` | `0x00000290` (656 B) | `0x00300400` | Parameters |
| 2 | `0x000003EC` | `0x00000038` (56 B) | `0x00302000` | Interrupt/handler table |
| 3 | `0x00000424` | `0x000337C8` (211,400 B) | `0x00302400` | Main patch code |

### Validation Checks

- Sum of record sizes: `0xE0 + 0x290 + 0x38 + 0x337C8` = `0x33B70` = header total payload
- Final record end: `0x424 + 0x337C8` = `0x33BEC` = file size (211,948 bytes)

---

## 4. Target Memory Map

```
EM9305 Patch Region:
  0x00300000 ┌────────────────────────────┐
             │ Config (224 bytes)         │  Record 0
  0x003000E0 ├────────────────────────────┤
             │ (gap: 0x320 bytes)         │
  0x00300400 ├────────────────────────────┤
             │ Parameters (656 bytes)     │  Record 1
  0x00300690 ├────────────────────────────┤
             │ (gap to 0x302000)          │
  0x00302000 ├────────────────────────────┤
             │ Handler Table (56 bytes)   │  Record 2
  0x00302038 ├────────────────────────────┤
             │ (gap: 0x3C8 bytes)         │
  0x00302400 ├────────────────────────────┤
             │ Main Patch (211,400 bytes) │  Record 3
  0x003360C8 └────────────────────────────┘
```

The Apollo510b erases 29 flash pages in the EM9305 before writing the 4 records via HCI commands.

---

## 5. Flashing Protocol

```
Apollo510b                              EM9305
    │                                      │
    │  1. HCI: erase 29 pages              │
    │     ────────────────────────▶        │
    │  2. HCI: write record 0 → 0x300000   │
    │     ────────────────────────▶        │
    │  3. HCI: write record 1 → 0x300400   │
    │     ────────────────────────▶        │
    │  4. HCI: write record 2 → 0x302000   │
    │     ────────────────────────▶        │
    │  5. HCI: write record 3 → 0x302400   │
    │     ────────────────────────▶        │
    │  6. HCI: reset EM9305                │
    │     ────────────────────────▶        │
```

Firmware drivers: `service_em9305_dfu.c`, `srv_em9305*.c`
Debug command: `AT^EM9305`

---

## 6. EM9305 in the G2 Architecture

The EM9305 is the BLE radio coprocessor — it handles the RF layer while the Apollo510b runs the Cordio BLE host stack. This split architecture means:
- The Apollo510b handles all BLE protocol logic (GATT, ATT, GAP, L2CAP)
- The EM9305 handles the physical radio (2.4 GHz transceiver, link layer)
- Communication between them is via HCI (Host Controller Interface)

The G2 does NOT use Nordic SoftDevice for BLE — that is only relevant to the legacy DFU bootloader path.

---

## 7. Cross-Version Stability

The EM9305 BLE radio firmware is **completely byte-identical** across all 5 analyzed firmware versions:

| Version | Size | Status |
|---------|------|--------|
| 2.0.1.14–2.0.7.16 | 211,948 bytes | Identical |

**Implication**: Zero functional drift in BLE radio initialization, patching, or radio layer behavior across the entire G2 version family. Mixed-fleet deployments have no EM9305-related backward-compatibility risk.

This stability is expected — the EM9305 patch is a vendor-provided binary (EM Microelectronic) that configures the radio layer. Unlike the Apollo510b main app, it doesn't contain Even application logic and therefore doesn't change with G2 feature updates.

Validated in the iOS SDK by `G2FirmwareVersionRegistry` (in `G2EVENOTAParser.swift`) which tracks this as a "STABLE" component.

---

## Related Documents

- [firmware-files.md](firmware-files.md) — EVENOTA container, EM9305 entry details
- [firmware-reverse-engineering.md](firmware-reverse-engineering.md) — EM9305 header analysis
- [../devices/g2-glasses.md](../devices/g2-glasses.md) — G2 BLE architecture
- [../protocols/ble-uuids.md](../protocols/ble-uuids.md) — BLE service/characteristic UUIDs
