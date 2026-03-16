# firmware_box.bin — G2 Charging Case MCU

Firmware for the G2 Charging Case's STM32L0xx microcontroller. Uses an `EVEN`-magic wrapper with big-endian length/checksum fields and contains an ARM Cortex-M0+ vector table at the STM32 flash base address.

**Target**: STM32L0xx ARM Cortex-M0+ (confirmed via GPIO base `0x50000000`)
**EVENOTA entry**: ID 4, type 6 (Box/Case)
**Interface**: Wired relay from Apollo510b via `glasses_case` protobuf
**Update path**: Phone → G2 glasses → Case MCU (no direct BLE)

---

## 1. File Structure

```
┌──────────────────────────────────────────────────────────────┐
│ EVEN Wrapper Header (0x20 bytes = 32 bytes)                  │
│   +0x00: "EVEN" magic (4 bytes ASCII)                        │
│   +0x04: 0x01 0x02 0x36 0x00  (version/padding)              │
│   +0x08: BE32  payload_length  (file_size - 0x20)            │
│   +0x0C: BE32  checksum (additive word sum of payload)       │
│   +0x10: 16×00  padding                                      │
├──────────────────────────────────────────────────────────────┤
│ ARM Cortex-M Vector Table (starts at +0x20)                  │
│   +0x20: SP    = 0x20002C88 (~11 KB SRAM)                    │
│   +0x24: Reset = 0x08000145 (Thumb, STM32 flash base)        │
├──────────────────────────────────────────────────────────────┤
│ Case Firmware (~55 KB)                                       │
│   Battery monitoring, charge state reporting,                │
│   glasses docking detection, wired communication             │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. EVEN Wrapper Header

| Offset | Size | Field | Value (v2.0.7.16) | Endian |
|--------|------|-------|-------------------|--------|
| +0x00 | 4 | Magic | `EVEN` (0x4556454E) | — |
| +0x04 | 4 | Version/padding | `0x01023600` | — |
| +0x08 | 4 | Payload length | `0x0000D7E0` (55,264 B) | **Big-endian** |
| +0x0C | 4 | Checksum | `0x4C44DA98` | **Big-endian** |
| +0x10 | 16 | Padding | zeros | — |

Note: The EVEN wrapper uses **big-endian** for length and checksum fields, unlike the rest of the EVENOTA format which is little-endian. This matches the STM32 convention.

### Checksum Algorithm

```
Algorithm: 32-bit additive word sum (big-endian)
Coverage:  file[0x20 : 0x20 + payload_length]
Method:    Sum all 4-byte big-endian words in payload region
           Zero-pad final partial word if needed
Result:    stored at file[0x0C] (big-endian)
```

Validated across all 5 firmware versions:

| Version | Payload Length (BE) | Checksum (BE) | Match |
|---------|-------------------|---------------|-------|
| 2.0.1.14 | `0x0000D010` | `0xA1D50BFE` | Yes |
| 2.0.3.20 | `0x0000D730` | `0x7054D5D8` | Yes |
| 2.0.5.12 | `0x0000D730` | `0x7054D5D8` | Yes |
| 2.0.6.14 | `0x0000D7E0` | `0x4C44DA98` | Yes |
| 2.0.7.16 | `0x0000D7E0` | `0x4C44DA98` | Yes |

---

## 3. ARM Vector Table

| Offset | Field | Value | Notes |
|--------|-------|-------|-------|
| +0x20 | Stack Pointer | `0x20002C88` | ~11 KB SRAM (0x20000000–0x20002C87) |
| +0x24 | Reset Handler | `0x08000145` | Thumb entry, STM32 flash base `0x08000000` |

The Reset vector at `0x08000000` is characteristic of STM32 microcontrollers. GPIO base address `0x50000000` confirms the STM32L0 family (Cortex-M0+). The relatively small SRAM (~11 KB) is consistent with STM32L071xx/L081xx. Board designation B200, firmware version 1.2.54. All 414 functions mapped (410 HIGH, 4 MEDIUM) using STM32CubeL0 SDK cross-reference.

### Evidence of Bank Switching

Firmware strings reference `running_bank` and `swap_bank`, suggesting the case MCU may support dual-bank firmware with A/B slot switching for reliable OTA updates.

### Startup Callgraph Anchor

Instruction-level reset/startup chain has been recovered from this binary:

```
0x08000144 (reset shim)
  -> 0x080082C6 (preinit thunk)
  -> 0x080000B8 (startup trampoline)
     -> 0x08000270 (constructor walk; table 0x0800D754..0x0800D774)
     -> 0x0800A3B0 (app main init)
        -> steady loop at 0x0800A4EE
```

Artifact: `captures/firmware/analysis/2026-03-05-box-reset-startup-callgraph.md`

Scheduler/task handoff closure (instruction-level):

```
0x0800A3B0 (app main)
  -> 0x08002F64
  -> 0x0800A6F0
  -> 0x0800678C (object/task bring-up)
  -> 0x0800A718 -> 0x0800C09C (scheduler start)
  -> fallback trap if return: 0x0800A4EE
```

Recovered bring-up objects from `0x0800678C`:
- six thread-like entries via `0x0800A860`: `0x08009B89`, `0x0800B965`, `0x0800949D`, `0x0800B605`, `0x0800B9A9`, `0x0800A989`
- four queue/wait entries via `0x0800A754`: `0x08006C41`, `0x08007D45`, `0x08007025`, `0x08008105`

Task-domain idle/wait closure (instruction-level):
- queue workers call wrapper families `0x0800A5EA`/`0x0800A5C8` and transport wait step `0x080034FC`
- low-power idle primitive `0x08004EE8` is reached from queue loops (`0x08007F0C`, `0x080070D4`, `0x08007186`)
- `0x08004EE8` contains explicit `wfi` at `0x08004EFE`
- scheduler start path includes wait setup `0x0800C0C2 -> 0x0800C81E`

Artifact: `captures/firmware/analysis/2026-03-05-box-scheduler-task-map.md`

---

## 4. Flash Memory Map (Inferred)

```
Case MCU Flash:
  0x08000000 ┌────────────────────────────────────┐
             │ ARM Vector Table                   │
             │   SP = 0x20002C88                  │
             │   Reset = 0x08000145               │
             ├────────────────────────────────────┤
             │ Case Firmware Application          │
             │   Battery monitoring               │
             │   Charge state detection           │
             │   Glasses docking sense            │
             │   Wired communication handler      │
  ~0x0800D800└────────────────────────────────────┘

Case MCU SRAM:
  0x20000000 – 0x20002C87 (~11 KB)
```

---

## 5. Update Path

The charging case has no BLE radio — firmware updates are relayed through the G2 glasses:

```
Phone (Even.app)          G2 Glasses (Apollo510b)        Case MCU
    │                          │                              │
    │  EVENOTA package         │                              │
    │  ────────────▶           │                              │
    │  (contains box.bin)      │                              │
    │                          │  Wired relay (UART/I2C)      │
    │                          │  ──────────────────────▶     │
    │                          │  (glasses_case proto)        │
    │                          │                              │
    │                          │  ◀──── ACK / status          │
```

**Protocol**: `GlassesCaseDataPackage` protobuf with `eGlassesCaseCommandId` enum
**Service**: Routed through the G2 glasses control channel (not a separate BLE service)
**App ID**: `UX_GLASSES_CASE_APP_ID`

---

## 6. Case MCU Capabilities (from firmware strings)

| Capability | Detail |
|-----------|--------|
| **Battery level** | Reports case battery via `GlassesCaseInfo` model |
| **Charging status** | Per-eye monitoring: voltage, battery %, current |
| **Docking detection** | Senses when glasses are placed in case |
| **Firmware update** | Receives firmware via wired link from G2 |
| **Dual-bank OTA** | A/B firmware slots with bank swap after flash |
| **Water detection** | L and R charging contacts: `L water detected, disable 5V` |
| **Temperature monitoring** | Charging cutoff on overtemp |
| **Ship mode** | PMIC deep sleep for transport/storage |
| **Aging mode** | Factory burn-in (NOT → PRE → RUNNING → DONE/ERROR) |

### Auxiliary ICs on Case PCB (board: B200)

| IC | Role |
|----|------|
| **YHM2217** | LED driver or hall sensor (chip ID validated at boot) |
| **YHM2510** | Fuel gauge / power management (ADC adjustment) |
| **4005** | Peripheral IC with watchdog |
| **PMIC** | Power management (registers 0x10-0x1B, boost, ship mode) |

### UART Protocol (Box ↔ Glasses)

```
Header: 5A A5 FF [cmd] [data...] [CRC]
```

| Command | Purpose |
|---------|---------|
| `0x13` | Battery/status notification (battery change, hall, USB events) |
| `0x58` | OTA check |

Errors: `receive header timeout`, `receive len timeout`, `receive data timeout`

### Case Firmware Version

`1.2.54` (from firmware strings)

### Box OTA Process (updating glasses)

```
1. Check glasses ready
2. Get running bank number (dual-bank flash)
3. Erase target bank
4. Copy serial number
5. Get bin file from case storage
6. Program glasses flash
7. CRC verify: crc_cal: 0x%x, crc_rx:0x%x
8. Inform glasses of OTA result
9. Bank swap: Swap bank(2->1) & RESET / Swap bank(1->2) & RESET
```

Timeout: 3 minutes. Battery requirement: >50%.

### Standby Reasons

idle, low bat, gls bat full, cmd

---

## 7. Cross-Version Size History

| Version | Size (bytes) | Delta | Notes |
|---------|-------------|-------|-------|
| 2.0.1.14 | 53,296 | — | |
| 2.0.3.20 | 55,120 | +1,824 (+3.4%) | Feature update |
| 2.0.5.12 | 55,120 | 0 | Stable |
| 2.0.6.14 | 55,296 | +176 | Minor update |
| 2.0.7.16 | 55,296 | 0 | Stable |

The case firmware is relatively stable, with two incremental updates across 5 versions (+2,000 bytes total, +3.8%). Changes are focused on charging logic and wear-in detection rather than architectural updates.

Validated in the iOS SDK by `G2FirmwareVersionRegistry` (in `G2EVENOTAParser.swift`) which tracks this as a "VARIED" component with 3 distinct sizes across 5 versions.

---

## Related Documents

- [firmware-files.md](firmware-files.md) — EVENOTA container, EVEN wrapper spec
- [firmware-reverse-engineering.md](firmware-reverse-engineering.md) — Box wrapper decoding
- [../devices/g2-case.md](../devices/g2-case.md) — G2 Charging Case hardware
- [../devices/g2-glasses.md](../devices/g2-glasses.md) — G2 inter-eye/case wired link
