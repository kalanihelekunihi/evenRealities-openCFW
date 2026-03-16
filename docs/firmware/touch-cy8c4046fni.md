# firmware_touch.bin — CY8C4046FNI Touch Controller

Firmware for the Cypress CY8C4046FNI capacitive touch controller on the G2 glasses temple. Uses a single-segment FWPK wrapper with CRC32C integrity and contains an ARM Cortex-M vector table for the PSoC4 processor.

**Target**: CY8C4046FNI (Cypress/Infineon PSoC4)
**EVENOTA entry**: ID 3, type 3 (Touch)
**Interface**: I2C DFU from Apollo510b (`drv_cy8c4046fni.c`)

---

## 1. File Structure

```
┌──────────────────────────────────────────────────────────────┐
│ FWPK Header (0x20 bytes = 32 bytes)                          │
│   +0x00: "FWPK" magic (4 bytes)                              │
│   +0x04: 0x00 0x06 0x00 0x02  (version/flags)                │
│   +0x08..+0x1B: reserved/padding                             │
│   +0x1C: LE32  CRC32C(payload) = 0x48674BC7                  │
├──────────────────────────────────────────────────────────────┤
│ ARM Cortex-M Vector Table (starts at +0x20)                  │
│   +0x20: SP    = 0x20002000 (8 KB SRAM)                      │
│   +0x24: Reset = 0x000044D9 (Thumb entry point)              │
├──────────────────────────────────────────────────────────────┤
│ Touch Controller Firmware (payload)                          │
│   Capacitive touch sensing, gesture recognition,             │
│   I2C slave communication with Apollo510b                    │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. FWPK Header Fields

| Offset | Size | Field | Value (v2.0.7.16) |
|--------|------|-------|-------------------|
| +0x00 | 4 | Magic | `FWPK` (ASCII) |
| +0x04 | 4 | Version/flags | `0x00060002` |
| +0x1C | 4 | Payload CRC32C | `0x48674BC7` |

### Checksum Algorithm

```
Algorithm: CRC32C (Castagnoli, reflected)
Poly:     0x1EDC6F41 (reflected: 0x82F63B78)
Init:     0xFFFFFFFF
XOR-out:  0xFFFFFFFF
Coverage: file[0x20 : EOF] (all payload bytes after header)
```

Note: This differs from the codec's FWPK which uses standard CRC32 (zlib). The touch FWPK uses CRC32C.

---

## 3. ARM Vector Table

| Offset | Field | Value | Notes |
|--------|-------|-------|-------|
| +0x20 | Stack Pointer | `0x20002000` | Top of ~8 KB SRAM |
| +0x24 | Reset Handler | `0x000044D9` | Thumb entry (LSB=1) |

The CY8C4046FNI uses a zero-based flash address space (`0x00000000`), typical for Cypress PSoC4 devices. The 8 KB SRAM (`0x20000000 – 0x20001FFF`) is significantly smaller than the Apollo510b's 512 KB.

---

## 4. Flashing Protocol

The Apollo510b updates the touch controller firmware over I2C:

```
Apollo510b                              CY8C4046FNI
    │                                      │
    │  1. I2C: enter DFU mode              │
    │     ────────────────────────▶        │
    │  2. I2C: erase application flash     │
    │     ────────────────────────▶        │
    │  3. I2C: write firmware rows         │
    │     ────────────────────────▶        │
    │  4. I2C: verify CRC                  │
    │     ────────────────────────▶        │
    │  5. I2C: exit DFU, reset             │
    │     ────────────────────────▶        │
    │     (touch controller operational)   │
```

Driver file: `drv_cy8c4046fni.c` in the G2 firmware source tree.

---

## 5. CY8C4046FNI in the G2 Architecture

| Aspect | Detail |
|--------|--------|
| **Role** | Capacitive touch sensing on glasses temple arm |
| **Gestures** | Tap, double-tap, triple-tap, long press, swipe forward/back |
| **Interface** | I2C slave to Apollo510b |
| **Driver** | `drv_cy8c4046fni.c` |
| **DFU** | Cypress PSoC4 I2C bootloader (row-based flash write) |
| **Events** | Reported on G2 service 0x01-01 (tap/swipe) and 0x0D-01 (long press) |

---

## 6. Cross-Version Size History

| Version | Size (bytes) | Delta | Notes |
|---------|-------------|-------|-------|
| 2.0.1.14 | 27,808 | — | |
| 2.0.3.20 | 28,192 | +384 | Minor update |
| 2.0.5.12 | 28,320 | +128 | Minor update |
| 2.0.6.14 | 34,080 | +5,760 (+20%) | Major touch firmware update |
| 2.0.7.16 | 34,080 | 0 | Stable |

The significant +20% jump at v2.0.6.14 correlates with two new features found in firmware binary strings:
- **Proximity baseline capture** (`touch_component_prox_baseline` at offset 0x77C1) — capacitive proximity sensing baseline learning for wear detection integration
- **Fast click reset** (`touch_component_fast_click_reset` at offset 0x7841) — improved debounce/reset timing for rapid tap sequences (triple-tap gesture recognition)

After v2.0.6.14, the touch firmware stabilized — v2.0.7.16 ships an identical binary.

Validated in the iOS SDK by `G2FirmwareVersionRegistry` (in `G2EVENOTAParser.swift`) which tracks this as a "VARIED" component with 4 distinct sizes across 5 versions.

---

## Related Documents

- [firmware-files.md](firmware-files.md) — EVENOTA container, FWPK wrapper comparison
- [firmware-reverse-engineering.md](firmware-reverse-engineering.md) — FWPK checksum semantics
- [../devices/g2-glasses.md](../devices/g2-glasses.md) — G2 touch hardware
- [../features/gestures.md](../features/gestures.md) — Gesture protocol (events from touch controller)
