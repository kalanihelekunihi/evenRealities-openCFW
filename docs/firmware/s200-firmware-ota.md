# s200_firmware_ota.bin — Apollo510b Main Application

The primary application firmware for the Even G2 glasses. Runs on the Ambiq Apollo510b SoC and contains the entire glasses operating system: display rendering, BLE protocol stack, audio pipeline, gesture handling, and all user-facing features.

**Target**: Ambiq Apollo510b (ARM Cortex-M55, 512 KB SRAM)
**EVENOTA entry**: ID 6, type 0 (Main FW)
**Flash address**: `0x00438000`

---

## 1. File Structure

```
┌──────────────────────────────────────────────────────────────┐
│ Preamble (32 bytes = 0x20)                                   │
│   +0x00: LE32  size_field (low 24 bits = payload size)       │
│   +0x04: LE32  CRC32 over bytes [0x08 .. EOF]                │
│   +0x08: 8×00  reserved                                      │
│   +0x10: LE32  flags (0xCB)                                  │
│   +0x14: LE32  load_address = 0x00438000                     │
│   +0x18: 8×00  reserved                                      │
├──────────────────────────────────────────────────────────────┤
│ ARM Cortex-M55 Vector Table (starts at +0x20)                │
│   +0x20: SP  = 0x2007FB00 (top of 512 KB SRAM)               │
│   +0x24: Reset = 0x005C9777 (Thumb entry point)              │
│   +0x28..+0x11F: Exception/interrupt handlers                │
├──────────────────────────────────────────────────────────────┤
│ Application Code + Data (~3.1 MB)                            │
│   FreeRTOS tasks, LVGL GUI, BLE Cordio stack,                │
│   protobuf handlers, drivers, LittleFS ops                   │
└──────────────────────────────────────────────────────────────┘
```

### Preamble Fields (v2.0.7.16)

| Offset | Size | Field | Value | Notes |
|--------|------|-------|-------|-------|
| +0x00 | 4 | Size | `0x0430A9C0` | Low 24 bits = `0x30A9C0` = 3,189,184 (file size) |
| +0x04 | 4 | CRC32 | `0x7BA2383F` | Standard CRC32 over `file[0x08:]` |
| +0x08 | 8 | Reserved | `0x00...` | |
| +0x10 | 4 | Flags | `0x000000CB` | Boot flags (meaning TBD) |
| +0x14 | 4 | Load address | `0x00438000` | Apollo510b application base |
| +0x18 | 8 | Reserved | `0x00...` | |

### Checksum Validation

```
Algorithm: CRC32 (standard zlib)
Init:     0x00000000
Poly:     0x04C11DB7
Coverage: file[0x08 : EOF]
Result:   stored at file[0x04]
```

### Raw Image

`s200_firmware_raw.bin` = `ota_s200_firmware_ota.bin[0x20:]` — the ARM image without the 32-byte preamble, directly executable at `0x00438000`.

---

## 2. Flash Memory Region

```
Apollo510b Internal Flash:
  0x00438000 ┌────────────────────────────────────┐
             │ ARM Vector Table                   │
             │   SP = 0x2007FB00                  │
             │   Reset = 0x005C9777               │
             ├────────────────────────────────────┤
             │ Application Code                   │
             │   Protocol handlers, BLE stack,    │
             │   display/audio drivers, GUI       │
             ├────────────────────────────────────┤
             │ Read-Only Data                     │
             │   Strings, fonts, protobuf schemas │
             ├────────────────────────────────────┤
             │ Initialized Data / BSS             │
  ~0x742A00  └────────────────────────────────────┘

  Execution span: 0x00438000 – 0x0074299F (~3.1 MB)
```

The bootloader at `0x00410000` hands off to this region by setting `SCB->VTOR = 0x00438000`, loading MSP from the vector table, and jumping to the Reset handler.

---

## 3. Software Stack

The main application contains the entire G2 operating system:

| Layer | Components |
|-------|-----------|
| **RTOS** | FreeRTOS + FreeRTOS-Plus-CLI |
| **GUI** | LVGL v9.3 + NemaGFX GPU + FreeType fonts |
| **BLE** | Cordio host stack (NOT Nordic SoftDevice) |
| **Audio** | GX8002B codec driver (TinyFrame), LC3 encoding |
| **Display** | JBD4010 uLED driver (MSPI), A6NG alternate |
| **Sensors** | ICM-45608 IMU, OPT3007 ALS |
| **Power** | BQ25180 charger, BQ27427 fuel gauge, nPM1300 PMIC |
| **Storage** | LittleFS on MX25U25643G 32 MB QSPI flash |
| **Memory** | TLSF allocator, ring buffers |

### Firmware Source Tree

Build path: `D:\01_workspace\s200_ap510b_iar\` (IAR Embedded Workbench)

```
s200_ap510b_iar/
├── app/gui/          conversate, EvenAI, EvenHub, dashboard, navigation,
│                     teleprompt, translate, health, quicklist, menu, setting
├── app/ux/           battery_sync, production, settings, system, wear_detect
├── driver/           buzzer, chg, codec, flash, hal, pdm, rtc, sensor, touch, uled, wdt
├── framework/        event_loop, page_manager, display_thread, uart_sync
├── platform/ble/     central, peripheral, discovery, profiles (ancc, efs, nus, ota, ring)
├── platform/protocols/  pb_service_* (protobuf handlers), efs_service, ota_service
├── platform/service/    DFU, eAT, evenAI, flashDB, box_detect, settings, time
├── platform/threads/    audio, ble_msgrx, ble_msgtx, evenai, input, notification, ring
├── product/s200/     board_config, main, redirect, rtos
└── third_party/      cordio, littlefs, lvgl_v9.3, TinyFrame, ringBuffer, tlsf
```

---

## 4. OTA Sub-Component Orchestration

When the main application receives an EVENOTA package, it orchestrates flashing each sub-component in order (from handler string offsets in the binary):

| Order | Component | Handler Offset | Target | Protocol |
|-------|-----------|---------------|--------|----------|
| 1 | box.bin | `0x23B3D8` | Case MCU | Wired relay (`glasses_case` proto) |
| 2 | ble_em9305.bin | `0x269D34` | EM9305 | HCI (`service_em9305_dfu.c`) |
| 3 | touch.bin | `0x27D768` | CY8C4046FNI | I2C DFU |
| 4 | codec.bin | `0x28EF88` | GX8002B | TinyFrame serial (BINH bootloader) |

The bootloader and main app are written to internal flash directly.

---

## 5. Cross-Version Size History

| Version | Build Date | Size (bytes) | Delta |
|---------|-----------|-------------|-------|
| 2.0.1.14 | 2025-12-11 | 2,471,336 | — |
| 2.0.3.20 | 2025-12-31 | 3,069,108 | +597,772 (+24%) |
| 2.0.5.12 | 2026-01-17 | 3,158,492 | +89,384 |
| 2.0.6.14 | 2026-01-29 | 3,184,984 | +26,492 |
| 2.0.7.16 | 2026-02-13 | 3,189,184 | +4,200 |

The major jump at v2.0.3.20 (+24%) corresponds to significant feature additions. Growth has stabilized in recent versions.

---

## 6. Deep Binary Analysis (firmware string extraction)

### RTOS Thread Architecture

| Thread | Source | Role |
|--------|--------|------|
| `thread_manager` | `threads/thread_manager.c` | System startup synchronization |
| `thread_ble_msgrx` | `threads/thread_ble_msgrx.c` | BLE message receive |
| `thread_ble_msgtx` | `threads/thread_ble_msgtx.c` | BLE message transmit |
| `thread_ble_wsf` | `threads/thread_ble_wsf.c` | Cordio WSF (RTOS abstraction) |
| `thread_evenai` | `threads/thread_evenai.c` | Even AI processing |
| `thread_notification` | `threads/thread_notification.c` | Notification handling |
| `display_thread` | `sync/display_thread.c` | Display rendering |
| `thread_pool` | `sync/thread_pool.c` | General purpose thread pool |

### Display System

- **JBD4010** primary display driver via MSPI (`drv_mspi_jbd4010.c`)
- **Hongshi A6N-G** alternative display driver (`drv_mspi_a6ng.c`) — second-source panel
- **LVGL v9.3** with Ambiq NemaGFX GPU acceleration
- **Screen modes**: `0x71`, `0x72`, `0x73`, `0x74` (4 distinct JBD4010 display modes)
- **Display commands**: INIT, POWER_UP, POWER_DOWN, BRIGHT_CTRL, CLEAR_SCREEN, REFLASH
- **FreeType** font rendering + BMP decoder
- **No LFSR/scramble in firmware** — 0x6402 display telemetry scrambling is JBD4010 hardware-level

### Brightness Control (confirmed)

```
[service.settings]Convert brightness level %d to lum %d, max_lum=%d
[service.settings]Convert brightness level %d to current %d, lum=%d
[service.settings]auto_brightness_enabled: %d
[service.settings]brightness_level: %d
[service.settings]left_brightness_calibration_level: %d
[service.settings]right_brightness_calibration_level: %d
```

ALS-driven auto-brightness: `[sensor_als]ALS polling, als_value:%d, peak_value:%d, brightness_level_converted:%d`

### Inter-Eye Sync Framework

- **Left eye = MASTER_ROLE** (auth primary, manages display sync)
- **Right eye = SLAVE_ROLE** (audio/ring primary)
- **Transport**: wired UART (`sync/uart_sync.c`) + TinyFrame protocol
- **Messages**: SEND_DATA_TO_PEER, SEND_INPUT_EVENT_TO_PEERS, display start/stop sync
- **Battery sync**: `Receive battery sync from peer: msg_id=%d, soc=%d, is_charging=%d`
- **Settings sync**: `recv slave settings sync, crc value not match, send config to slave`
- **Dominant hand** setting (0=left, 1=right) — user preference, separate from eye role

### BLE Profiles (GATT services, from source tree)

| Profile Source | Service | Description |
|---------------|---------|-------------|
| `profile_efs.c` | Even File Service | 0x7401/0x7402 file transfer |
| `profile_ess.c` | Even Sensor Service | 0x6401/0x6402 display telemetry |
| `profile_eus.c` | Even UART Service | 0x5401/0x5402 protobuf transport |
| `profile_nus.c` | Nordic UART Service | 6E400001 NUS |
| `profile_ota.c` | OTA Service | Firmware update |
| `profile_ring.c` | Ring Service | R1 ring communication |
| `profile_ancc.c` | ANCS Client | Apple notification relay |

### EvenAI Guard Conditions

```
warn: can not ctrl evenai, product_mode = %d, ota_status = %d,
  voice_switch = %d, onboarding_status = %d, calibration_ui_status = %d
```

EvenAI is gated on: product mode, OTA status, voice switch, onboarding completion, calibration UI status.

### VAD (Voice Activity Detection)

Separate EvenAI notification type: `APP_PbNotifyEncodeEvenAIVADInfo` — distinct from CTRL/ASK/REPLY/SKILL types.

### Menu System (on-device)

8 menu items: Notifications, Conversate, Teleprompt, Translate, Navigate, Even AI, Dashboard, Silent Mode.

### Device Config Command IDs

`AUTHENTICATION`, `BASE_CONNECT_HEART_BEAT`, `TIME_SYNC`, `GET_DEVICE_INFO`, `SET_DEVICE_INFO`, `DISCONNECT_INFO`, `BLE_CONNECT_PARAM`, `PIPE_ROLE_CHANGE`, `RING_CONNECT_INFO`, `UNPAIR_INFO`, `COMMAND_EXCEPTION`, `QUICK_RESTART`, `AUD_CONTROL`, `PRODUCTION_CLOSE_MIC`, `RESTORE_TO_FACTORY_SETTINGS`

### Additional Hardware (newly discovered)

- **BQ27427** fuel gauge — `bq27427_checksum_dm_block`, `bq27427_i2c_write_block`
- **Magnetometer** — `DRV_MAGReadWhoAmI` (compass/navigation)
- **YHM2217, YHM2510, 4005** — auxiliary ICs in charging case (LED/fuel gauge/peripheral)

### LittleFS Filesystem Layout

```
/firmware/   — sub-component firmware images (codec, BLE, touch, box)
/ota/        — OTA update staging (s200_firmware_ota.bin, s200_bootloader.bin)
/user/       — user data/settings
/log/        — system logs (compress_log_%d.bin, hardfault.txt)
L:/log/      — left eye log path
R:/log/      — right eye log path
```

### Production Test Shell Commands (FreeRTOS CLI)

```
AT^BLES [Bondable/Disbondable/DISCONN/RESET9305/HOSTRESET/APPDB]
AT^BRIGHTNESS
AT^IMU_RAWDATA / AT^ALS_READ
codec mic state | mic gain <0-48> | mic on|off | dmic on|off
set screen height <value> | set screen mode <0x71-0x74>
set autobrightness <enable|disable>
get dominant_hand | get gesture_app | get temperature_unit
buzzer play <type>    — 0=touch, 1=alarm, 2=call
onboarding getFlag | setFlag <0|1>
dispReflash | singleReflash
file2xip <filepath> <xip_address>    — XIP flash write (range: 0x80000000-0x81FFFFFF)
```

---

## Related Documents

- [firmware-files.md](firmware-files.md) — EVENOTA container format, device mapping
- [s200-bootloader.md](s200-bootloader.md) — Bootloader that hands off to this image
- [firmware-reverse-engineering.md](firmware-reverse-engineering.md) — Preamble analysis, source tree reconstruction
- [../devices/g2-glasses.md](../devices/g2-glasses.md) — G2 hardware BOM
