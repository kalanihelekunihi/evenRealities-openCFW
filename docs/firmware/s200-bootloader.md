# s200_bootloader.bin — Apollo510b Bootloader

The bootloader for the Even G2 glasses. Runs on the Ambiq Apollo510b SoC at `0x00410000` and is responsible for boot validation, DFU mode entry, and handing off execution to the main application at `0x00438000`.

**Target**: Ambiq Apollo510b (ARM Cortex-M55, 512 KB SRAM)
**EVENOTA entry**: ID 5, type 1 (Bootloader)
**Flash address**: `0x00410000`

---

## 1. File Structure

The bootloader is a raw ARM Cortex-M55 image with no preamble — the vector table begins at byte 0:

```
┌──────────────────────────────────────────────────────────────┐
│ ARM Cortex-M55 Vector Table (offset 0x00)                    │
│   +0x00: SP    = 0x2007FB00 (top of 512 KB SRAM)             │
│   +0x04: Reset = 0x004324CF (Thumb entry, bootloader start)  │
│   +0x08..+0xFF: 59 non-zero exception/interrupt handlers     │
│                 span: 0x00416027 – 0x004324ED                │
├──────────────────────────────────────────────────────────────┤
│ Bootloader Code (~148 KB)                                    │
│   Boot validation, DFU state machine,                        │
│   flash writer, sub-component OTA orchestration              │
├──────────────────────────────────────────────────────────────┤
│ Literal Data & Strings                                       │
│   "bootMetadataInfo.targetRunAddr = 0x%x(0x%x)"              │
│   "APP jumpaddr app(0x%x) = 0x%x"                            │
│   "ota/s200_firmware_ota.bin"                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Flash Memory Region

```
Apollo510b Internal Flash:
  0x00410000 ┌────────────────────────────────────┐
             │ Bootloader Vector Table            │
             │   SP = 0x2007FB00                  │
             │   Reset = 0x004324CF               │
             ├────────────────────────────────────┤
             │ Bootloader Code                    │
             │   DFU state machine                │
             │   Flash write/erase                │
             │   Sub-component orchestration      │
             ├────────────────────────────────────┤
             │ Bootloader Data                    │
             │   Key literals:                    │
             │   0x00410000 (vector base)         │
             │   0xE000ED08 (SCB->VTOR)           │
             │   0x2007D000 (RAM stack marker)    │
  0x00438000 ├────────────────────────────────────┤
             │ Main Application (separate image)  │
             └────────────────────────────────────┘
```

---

## 3. Boot Sequence

### Power-On Decision

```
1. ARM core reads vector table at 0x00410000
2. Stack pointer loaded: MSP = 0x2007FB00
3. Reset handler executes at 0x004324CF
4. Bootloader checks:
   ├── DFU trigger set?     → Enter DFU mode
   ├── No valid app?        → Enter DFU mode
   └── Valid app present?   → Hand off to application
```

### Application Handoff (disassembly at file offset 0x1DBDC)

The bootloader hands off to the main application via VTOR relocation:

```arm
; Runtime address: 0x0042DBDC
movw r1, #0xED08
movt r1, #0xE000        ; r1 = SCB->VTOR (0xE000ED08)
str  r0, [r1]           ; SCB->VTOR = 0x00438000
ldr.w sp, [r0]          ; MSP = *(0x00438000) = 0x2007FB00
ldr  r1, [r0, #4]       ; entry = *(0x00438004) = 0x005C9777
bx   r1                 ; Jump to application Reset handler
```

The handoff is preceded by logging:
- `0x0042DF6E`: `"bootMetadataInfo.targetRunAddr = 0x%x(0x%x)"`
- `0x0042DFBC`: `"APP jumpaddr app(0x%x) = 0x%x"`
- `0x0042DF5E–0x0042DF88`: Normalizes run base to `0x00438000`

### Key Addresses

| Address | Purpose |
|---------|---------|
| `0x00410000` | Bootloader vector base (literal at offset 0x224E0) |
| `0xE000ED08` | ARM SCB->VTOR register |
| `0x2007D000` | RAM stack marker |
| `0x00438000` | Application load address (`targetRunAddr`) |

---

## 4. DFU Update Process (from firmware strings)

The bootloader startup message is `>>> Even Bootloader start <<<`.

### RTOS Architecture

Two FreeRTOS tasks:
- `task.manager` — system startup synchronization
- `task.dfu` — firmware update processing

Uses EasyLogger v2.2.99 for structured logging.

### Boot Sequence (from strings)

```
1. Hardware init: MSPI flash init (MX25U25643G), ADC calibration, I2C4 init
2. Flash setup: 4-byte address mode, quad-enable, timing scan calibration
3. LittleFS mount on MX25U25643G (32MB QSPI flash)
4. Create directories if missing: /firmware, /ota, /user, /log
5. Read OTA flag: "otaFlag = 0x%x"
6. Decision:
   ├── If OTA flag set: "need updata firmware" → DFU process
   └── If clear: "DO NOT need updata firmware, GO TO APP" → jump to app
```

### DFU Process (firmware update)

```
1. Read ota/s200_firmware_ota.bin from LittleFS
2. "filesize %d desAddr 0x%x" — validate file size and destination
3. "blobSize = %d(0x%x)" — validate blob
4. app_dfu_image_crc_check: "calc CRC = 0x%x(0x%x)", "crcCheck = %d"
5. app_dfu_system_program: "Installing ...", "Installing %d(%d)", "---Install end---"
6. _verifyFlashContent — post-write verification
7. Success: "updata firmware success SP = 0x%x"
   Failure: "Bootloader ota fail, system reset!!!" → bootloader_error_reset
8. "boot_count: %d" — reset counter persisted across boots
```

### Application Handoff

```
"bootMetadataInfo.targetRunAddr = 0x%x(0x%x)" — read target from metadata
"app firmware SP = 0x%x" — validate stack pointer
"APP jumpaddr app(0x%x) = 0x%x" — jump to main application
```

### Software Stack (from source paths)

```
D:\01_workspace\s200_ap510b_iar\
  product\s200\bootloader\config\main.c
  product\s200\bootloader\threads\thread_manager.c
  product\s200\bootloader\threads\thread_dfu.c
  driver\flash\drv_mx25u25643g.c
  driver\hal\src\hal_i2c.c
  third_party\EasyLogger-master\ (elog v2.2.99)
  third_party\littlefs\ (LittleFS with MX25U25643G porting)
  third_party\tlsf\ (memory allocator)
```

---

## 5. Cross-Version Size History

| Version | Size (bytes) | Delta |
|---------|-------------|-------|
| 2.0.1.14 | 147,364 | — |
| 2.0.3.20 | 147,360 | -4 |
| 2.0.5.12 | 147,657 | +297 |
| 2.0.6.14 | 147,657 | 0 |
| 2.0.7.16 | 147,727 | +70 |

The bootloader changes minimally between versions — only +363 bytes total across 5 releases. The DFU process, VTOR handoff logic, and flash write routines appear structurally unchanged. The small size deltas likely reflect minor build toolchain differences or constant data updates rather than functional changes.

Validated in the iOS SDK by `G2FirmwareVersionRegistry` (in `G2EVENOTAParser.swift`) which tracks this as a "VARIED" component with 4 distinct sizes.

---

## Related Documents

- [s200-firmware-ota.md](s200-firmware-ota.md) — Main application this bootloader launches
- [firmware-files.md](firmware-files.md) — EVENOTA container format, full flash map
- [firmware-reverse-engineering.md](firmware-reverse-engineering.md) — Bootloader load/execute correlation
- [../devices/g2-glasses.md](../devices/g2-glasses.md) — G2 hardware BOM
