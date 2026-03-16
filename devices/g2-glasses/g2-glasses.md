# Even G2 Glasses — Hardware Specification

The Even G2 smart glasses are the primary product in the Even Realities ecosystem. Left and right sides share identical hardware and firmware — eye identity is a runtime BLE naming configuration only.

---

## 1. Product Identification

| Property | Value |
|----------|-------|
| **Model** | S200 (GATT Device Information Service) |
| **Board Revision** | B210 (Board v2, Revision 10) |
| **FCC ID** | 2BFKR-G2 |
| **IC** | 32408-G2 |
| **Manufacturer** | Even Realities Ltd. (Building West 2603, LEPU TOWER, Nanshan District) |
| **Firmware** | v2.0.7.16 (current production, 2026-02-13 build) |
| **BLE Name** | `Even G2_32_L_xxxxxx` (left) / `Even G2_32_R_xxxxxx` (right) |

### Hardware Variants

| Variant | Colors |
|---------|--------|
| **G2 A** | Brown, Green, Grey |
| **G2 B** | Brown, Green, Grey |

6 total SKUs (2 frame shapes × 3 colors). Left and right sides within each variant are identical hardware.

---

## 2. System-on-Chip

| Property | Value |
|----------|-------|
| **SoC** | Ambiq Micro Apollo510b |
| **CPU** | ARM Cortex-M55 (Armv8.1-M Mainline with Helium/MVE) |
| **SRAM** | 512 KB (0x20000000 – 0x2007FFFF) |
| **Internal Flash** | Application at 0x00438000, bootloader at 0x00410000 |
| **Build System** | IAR Embedded Workbench |
| **RTOS** | FreeRTOS + FreeRTOS-Plus-CLI |
| **GUI** | LVGL v9.3 + NemaGFX GPU acceleration + FreeType font rendering |
| **Memory Allocator** | TLSF (Two-Level Segregated Fit) |

---

## 3. Complete Hardware BOM

| Category | Component | Part Number | Interface | Firmware Driver |
|----------|-----------|-------------|-----------|-----------------|
| **Main SoC** | Ambiq Apollo510b | AP510b | — | (entire firmware) |
| **BLE Radio** | EM Microelectronic EM9305 (ARC EM / ARCv2 ISA) | EM9305 | HCI | `srv_em9305*.c` |
| **Audio Codec** | Nationalchip GX8002B | GX8002B | TinyFrame (serial) | `drv_gx8002b.c` |
| **Display** | Jade Bird Display JBD4010 | JBD4010 | MSPI | `drv_mspi_jbd4010.c` |
| **Display (alt)** | Hongshi A6NG | A6NG | MSPI | `drv_mspi_a6ng.c` |
| **Touch** | Cypress/Infineon CY8C4046FNI | CY8C4046FNI | I2C | `drv_cy8c4046fni.c` |
| **IMU** | TDK InvenSense ICM-45608 | ICM-45608 | SPI | `imu_icm45608.c` |
| **ALS** | Texas Instruments OPT3007 | OPT3007 | I2C | `opt3007_registers.c` |
| **Charger IC** | Texas Instruments BQ25180 | BQ25180 | I2C | `drv_bq25180.c` |
| **Fuel Gauge** | Texas Instruments BQ27427 | BQ27427 | I2C | `drv_bq27427.c` |
| **PMIC** | Nordic nPM1300 | nPM1300 | I2C | `npmx_driver*.c` |
| **NOR Flash** | Macronix MX25U25643G (32 MB) | MX25U25643G | QSPI | `drv_mx25u25643g.c` |
| **Buzzer** | Piezo | — | PWM | `drv_buzzer.c` |
| **Microphone** | PDM MEMS | — | PDM | `drv_pdm.c` |
| **RTC** | Internal (Apollo510b) | — | — | `drv_rtc.c` |
| **Watchdog** | Internal (Apollo510b) | — | — | `watchdog.c` |

---

## 4. Display

| Property | Value |
|----------|-------|
| **Panel** | JBD4010 micro-LED (uLED) |
| **Resolution** | 576 × 288 pixels |
| **Color Depth** | 4-bit grayscale (Gray4, 16 levels) |
| **Rendering** | Monoscopic (same content both eyes) |
| **Refresh** | ~20 Hz (confirmed via 0x6402 sensor stream) |
| **Interface** | MSPI (high-speed parallel) |
| **GPU** | NemaGFX (hardware-accelerated 2D rendering) |
| **Font Engine** | FreeType |
| **Brightness** | 0–42 internal scale (UI 0–100%), per-eye calibration |

The display sensor stream on BLE characteristic `0x6402` produces JBD LFSR-scrambled telemetry at ~20 Hz (205 bytes/packet). This is the only reliable signal that the physical display is active.

---

## 5. Inter-Eye Architecture

```
┌──────────────────────┐          Wired Link           ┌──────────────────────┐
│    LEFT EYE          │◀──── UART/I2C through ────▶   │    RIGHT EYE         │
│                      │        eyeglass frame         │                      │
│  Primary for:        │                               │  Primary for:        │
│  • Authentication    │                               │  • Audio/microphone  │
│  • Command sequence  │                               │  • R1 Ring comm      │
│  • Heartbeat         │                               │                      │
└──────────┬───────────┘                               └──────────┬───────────┘
           │ BLE                                                  │ BLE
           ▼                                                      ▼
    ┌──────────────┐                                      ┌──────────────┐
    │    Phone     │◀──────── Both eyes connect ────────▶ │    Phone     │
    │  (Left BLE)  │          independently to phone      │  (Right BLE) │
    └──────────────┘                                      └──────────────┘
```

- **Left eye**: Primary for authentication (auth handshake originates here), command sequencing, heartbeat
- **Right eye**: Primary for audio/microphone (LC3 encoding), R1 Ring direct communication
- **Link type**: Wired UART/I2C through the eyeglass frame (NOT BLE between eyes)
- **Firmware**: Identical binary on both sides; role is determined by BLE advertisement name

Both eyes maintain independent BLE connections to the phone. The glasses maintain their own packet sequence counter (separate from phone TX counter).

---

## 6. BLE Characteristics

Base UUID: `00002760-08C2-11E1-9073-0E8AC72Exxxx`

| Suffix | Pipe | Direction | Purpose |
|--------|------|-----------|---------|
| `0001` | — | Service | Service discovery |
| `0002` | — | Service | Service discovery |
| `1001` | Unknown | Unknown | Possibly OTA or bidirectional |
| `5401` | Control | Phone → Glasses (write) | Protocol commands |
| `5402` | Control | Glasses → Phone (notify) | Protocol responses |
| `5450` | Control | Service declaration UUID | Parent declaration for control pipe (`5401`/`5402`) |
| `6401` | Display | Phone → Glasses (write) | Display commands |
| `6402` | Display | Glasses → Phone (notify) | Display sensor telemetry (~20 Hz) |
| `6450` | Display | Service declaration UUID | Parent declaration for display pipe (`6401`/`6402`) |
| `7401` | File | Phone → Glasses (write) | File/OTA data transfer |
| `7402` | File | Glasses → Phone (notify) | File transfer ACKs |
| `7450` | File | Service declaration UUID | Parent declaration for file pipe (`7401`/`7402`) |

**Nordic UART Service (NUS)**:
| UUID | Direction | Purpose |
|------|-----------|---------|
| `6E400002-B5A3-F393-E0A9-E50E24DCCA9E` | Phone → Glasses | Simple commands, text, mic control |
| `6E400003-B5A3-F393-E0A9-E50E24DCCA9E` | Glasses → Phone | Gestures (0xF5+code), audio (0xF1+PCM), heartbeat (0x25) |

**Pipe routing**: `BleG2PsType` enum selects the active characteristic set:
- Type 0 = Control (5401/5402)
- Type 1 = File (7401/7402)
- Type 2 = Display (6401/6402)

---

## 7. Audio

| Property | Value |
|----------|-------|
| **Codec IC** | GX8002B (Nationalchip) |
| **Encoding** | LC3 (Low Complexity Communication Codec) |
| **Frame Size** | 10 ms frames, 40 bytes/frame |
| **Microphone** | PDM MEMS (right eye primary) |
| **Transport** | NUS BLE (0xF1 prefix stripped before callback) |
| **On-device ASR** | sherpa-onnx (via Even.app native bridge) |
| **Cloud ASR** | Azure Speech (via `flutter_ezw_asr`) |

---

## 8. Storage

| Property | Value |
|----------|-------|
| **External Flash** | MX25U25643G, 32 MB QSPI NOR |
| **Filesystem** | LittleFS |
| **Structure** | Separate `L:/` and `R:/` roots per eye |

```
L:/ (Left eye)                    R:/ (Right eye)
├── log/                          ├── log/
│   ├── compress_log_0.bin        │   ├── compress_log_0.bin
│   ├── compress_log_1.bin        │   ├── compress_log_1.bin
│   ├── compress_log_2.bin        │   ├── compress_log_2.bin
│   ├── compress_log_3.bin        │   ├── compress_log_3.bin
│   ├── compress_log_4.bin        │   ├── compress_log_4.bin
│   └── hardfault.txt             │   └── hardfault.txt
└── user/                         └── user/
    └── notify_whitelist.json         └── notify_whitelist.json
```

Files are accessible via the 0xC4/0xC5 file transfer service and AT command debug interface (`AT^LS`, `AT^RM`, `AT^MKDIR`).

---

## 9. AT Command Debug Interface

Production/debug serial console via AT commands:

| Command | Description |
|---------|-------------|
| `AT^INFO` | System information |
| `AT^PSN` | Product serial number |
| `AT^RESET` | System reset |
| `AT^BLE` | BLE general control |
| `AT^BLES` | BLE bondable/disconnect/reset9305/appdb |
| `AT^BLEMC` | BLE master connect/disconnect |
| `AT^BLEADV` | BLE advertising control |
| `AT^EM9305` | EM9305 BLE radio control |
| `AT^CLEANBOND` | Clear BLE bond info |
| `AT^IMU` | IMU (raw data, calibration, mode) |
| `AT^ALS` | Ambient light sensor |
| `AT^BRIGHTNESS` | Brightness control |
| `AT^SCRN` | Screen settings (height) |
| `AT^BUZZER` | Buzzer (play by type) |
| `AT^AUDIO` | Audio (DMIC on/off) |
| `AT^NUS` | Nordic UART Service |
| `AT^TP` | Teleprompter |
| `AT^LOGTYPE` | Log type configuration |
| `AT^LS` | List files (LittleFS) |
| `AT^MKDIR` | Create directory |
| `AT^RM` | Remove file |

---

## 10. Firmware

The G2 uses the EVENOTA multi-component OTA format with 6 entries:

| Component | Target IC | Size (v2.0.7.16) |
|-----------|----------|-----------------|
| Main application | Apollo510b | 3,189,184 B |
| Bootloader | Apollo510b | 147,727 B |
| BLE radio patch | EM9305 | 211,948 B |
| Audio codec | GX8002B | 319,372 B |
| Touch controller | CY8C4046FNI | 34,080 B |
| Case firmware | STM32L0xx Cortex-M0+ (confirmed via RE: 414 functions mapped) | 55,296 B |

See the individual firmware component docs for per-file binary structure details.

### Firmware-domain note

- The G2 OTA container carries mixed-domain artifacts: Ambiq main/bootloader plus vendor-specific sidecars (`EM9305`, `GX8002B`, `CY8C4046FNI`) and one STM32-family case MCU binary.
- This split means any SDK guidance should be component-scoped:
  - Ambiq/Apollo510b: Ambiq + IAR toolchain lineage
  - Peripheral modules: vendor-specific flash/bootloader flows
  - Case MCU: STM32L0xx Cortex-M0+ (confirmed via firmware RE — 414 functions, STM32CubeL0 SDK cross-ref)

---

## Related Documents

- [../firmware/firmware-files.md](../firmware/firmware-files.md) — EVENOTA container, flash maps, version history
- [../firmware/s200-firmware-ota.md](../firmware/s200-firmware-ota.md) — Main application binary structure
- [../firmware/s200-bootloader.md](../firmware/s200-bootloader.md) — Bootloader binary structure
- [../firmware/g2-firmware-modules.md](../firmware/g2-firmware-modules.md) — Module-by-module runtime behavior and simulator parity tracking
- [../firmware/modules/ble-multi-connection.md](../firmware/modules/ble-multi-connection.md) — Multi-endpoint BLE identity behavior (`G2-L/G2-R/R1`) and simulator parity notes
- [../firmware/modules/settings-dispatch.md](../firmware/modules/settings-dispatch.md) — Firmware settings selector dispatch (`1..11`) and simulator compatibility model
- [../firmware/modules/settings-compact-notify.md](../firmware/modules/settings-compact-notify.md) — Compact settings status packets on `0x0D-01` (`f1=1,f3={f1=event[,f2=status]}`) with module-lane correlation and simulator parity model
- [../firmware/modules/settings-envelope-parser.md](../firmware/modules/settings-envelope-parser.md) — Root oneof parser/notify lane (`case3..7`) and inbound case5/case6/7 simulator parity notes
- [../firmware/modules/settings-selector-schema.md](../firmware/modules/settings-selector-schema.md) — Descriptor-recovered settings selector protobuf schema (`envelope + selector 1..11`)
- [../firmware/modules/settings-runtime-context.md](../firmware/modules/settings-runtime-context.md) — Selector runtime context byte map (`+0x08/+0x09/+0x0A..+0x0C/+0x15/+0x16/+0x17`) and gate-side effects
- [../firmware/modules/wear-detection.md](../firmware/modules/wear-detection.md) — Wear detection control flow and settings/onboarding linkage
- [../firmware/ble-em9305.md](../firmware/ble-em9305.md) — BLE radio patch format
- [../firmware/codec-gx8002b.md](../firmware/codec-gx8002b.md) — Audio codec firmware
- [../firmware/touch-cy8c4046fni.md](../firmware/touch-cy8c4046fni.md) — Touch controller firmware
- [../firmware/box-case-mcu.md](../firmware/box-case-mcu.md) — Charging case firmware
- [../protocols/ble-uuids.md](../protocols/ble-uuids.md) — Full BLE UUID reference
- [../protocols/authentication.md](../protocols/authentication.md) — Auth handshake protocol
- [../features/gestures.md](../features/gestures.md) — Gesture protocol (touch + NUS + R1)
