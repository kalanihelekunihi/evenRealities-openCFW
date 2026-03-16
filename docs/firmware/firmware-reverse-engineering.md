# Even Realities G2 & R1 Firmware Reverse Engineering

Sources: `captures/firmware/` binaries, Even.app static RE, BLE captures, mock firmware, protocol documentation

> **Cross-reference**: Hardware BOM, device variants, and per-component firmware structure are documented in:
> - [g2-glasses.md](../devices/g2-glasses.md) — G2 hardware, variants, inter-eye architecture
> - [g2-case.md](../devices/g2-case.md) — Charging case hardware and protocol
> - [r1-ring.md](../devices/r1-ring.md) — R1 Ring SoC, health sensors, DFU
> - [firmware-files.md](firmware-files.md) — EVENOTA container format, component table

---

## 1. Hardware Platform Identification

### G2 Glasses — Ambiq Apollo510b

The G2 main SoC is **Ambiq Micro Apollo510b**, confirmed via OTA firmware binary analysis (build path `s200_ap510b_iar`). The nRF52840/S140 components identified in §3-6 below are from the DFU bootloader firmware in the Even.app bundle, likely related to the R1 Ring update path.

**Updated hardware identification (from OTA firmware binary strings):**

| Property | Value | Confidence | Evidence |
|---|---|---|---|
| **Main SoC** | Ambiq Micro Apollo510b | **CONFIRMED** | Build path `s200_ap510b_iar`; `lv_ambiq_display.c`; NemaGFX GPU; Cordio BLE host |
| **CPU** | ARM Cortex-M55 | CONFIRMED | Vector table at SP=0x2007FB00 (512KB SRAM), Reset=0x005C9777 |
| **SRAM** | 512 KB+ (0x20000000 – 0x2007FFFF) | CONFIRMED | SP placement at 0x2007FB00 |
| **Flash Base** | 0x00438000 (application) | CONFIRMED | OTA preamble load address |
| **BLE Radio** | EM9305 (EM Microelectronic) | CONFIRMED | `ble_em9305.bin`; `service_em9305_dfu.c`; `AT^EM9305` command |
| **BLE Host** | Cordio (Ambiq) | CONFIRMED | `third_party\cordio\` in build paths; NOT Nordic SoftDevice |
| **Audio Codec** | GX8002B (Nationalchip) | CONFIRMED | `drv_gx8002b.c`; TinyFrame protocol; FWPK firmware |
| **Display** | JBD4010 (Jade Bird Display) uLED | CONFIRMED | `drv_mspi_jbd4010.c`; MSPI interface |
| **Touch** | CY8C4046FNI (Cypress PSoC4) | CONFIRMED | `drv_cy8c4046fni.c`; separate DFU |
| **IMU** | ICM-45608 (TDK InvenSense) | CONFIRMED | `imu_icm45608.c` |
| **ALS** | OPT3007 (TI) | CONFIRMED | `opt3007_registers.c` |
| **Charger** | BQ25180 (TI) | CONFIRMED | `drv_bq25180.c` |
| **Fuel Gauge** | BQ27427 (TI) | CONFIRMED | `drv_bq27427.c` |
| **PMIC** | Nordic nPM1300 | CONFIRMED | `npmx_driver` strings |
| **External Flash** | MX25U25643G (Macronix) 32MB | CONFIRMED | `drv_mx25u25643g.c`; LittleFS |
| **GUI** | LVGL v9.3 + NemaGFX GPU | CONFIRMED | Build paths; FreeType font rendering |
| **RTOS** | FreeRTOS | CONFIRMED | FreeRTOS-Plus-CLI; `thread_*.c` |
| **Board Revision** | B210 | HIGH | All firmware package directory names; `B210_DFU` advertised string in bootloader binary |
| **Hardware Model** | S200 | HIGH | GATT Device Information Service response |
| **Firmware Version** | 2.0.7.16 (current production) | HIGH | GATT response; device info probe 0x09-01 |
| **Manufacturer** | Even Realities Ltd. | HIGH | GATT 0x2A29 response; "Building West 2603, LEPU TOWER, Nanshan District" |
| **Variants** | G2 A / G2 B in Brown, Green, Grey | HIGH | Even.app asset manifest |

**Original nRF52840 identification (from DFU bootloader in Even.app bundle — applies to R1/legacy DFU path):**

| Property | Value | Confidence | Evidence |
|---|---|---|---|
| **SoC** | Nordic nRF52840 | MEDIUM (may be R1 Ring) | Bootloader at 0xF0000 requires 1MB flash (nRF52832 QFAA max 512KB); APP_CODE_BASE 0x27000 matches S140 (nRF52840-specific), not S132 (nRF52832-specific) |
| **CPU** | ARM Cortex-M4F @ 64 MHz | HIGH | Vector table format; `hw_version=52` in DFU init packets (Nordic nRF52 family indicator) |
| **FPU** | Hardware single-precision FPU | HIGH | Cortex-M55 standard |
| **Flash** | 1 MB (0x00000000 – 0x000FFFFF) | HIGH | Bootloader placement at 0xF8000; SoftDevice vector table range |
| **RAM** | 256 KB (0x20000000 – 0x2003FFFF) | HIGH | nRF52840 spec; bootloader stack at 0x2000CFA0 |
| **BLE Stack** | SoftDevice S140 v7.0.0 (FWID 0x0100) | HIGH | SoftDevice info struct at file offset 0x2000; FWID field confirmed |
| **BLE Version** | Bluetooth 5.0 | HIGH | S140 supports 5.0: 1M/2M/Coded PHY, DLE, Extended Advertising |
| **Board Revision** | B210 | HIGH | All firmware package directory names; `B210_DFU` advertised string in bootloader binary |
| **Hardware Model** | S200 | HIGH | GATT Device Information Service response |
| **Firmware Version** | 2.0.7.16 (current production) | HIGH | GATT response; device info probe 0x09-01 |
| **Manufacturer** | Even Realities Ltd. | HIGH | GATT 0x2A29 response |
| **Variants** | G2 A / G2 B in Brown, Green, Grey | HIGH | Even.app asset manifest |

### R1 Ring — Nordic nRF5x

| Property | Value | Confidence | Evidence |
|---|---|---|---|
| **SoC** | Nordic nRF5x series (likely nRF52832 or nRF52833) | MEDIUM | FE59 DFU service (Nordic Buttonless Secure DFU, BLE SIG registered); SMP/MCUmgr firmware transfer; NUS BLE service |
| **DFU Protocol** | Nordic DFU + MCUmgr (iOSMcuManagerLibrary) | HIGH | Even.app embeds `mcumgr_flutter` framework; SMP characteristic UUID DA2E7828-FBCE-4E01-AE9E-261174997C48 discovered |
| **Health Sensors** | HR, SpO2, temperature, steps, sleep, wear detection | HIGH | Even.app health data models (`HealthSingleData`, `HealthMultData`) |
| **Camera** | Photo capture | LOW | `take_photo` voice intent in BERT model; no further protocol evidence yet |
| **Communication** | Dual BLE links — Ring↔Phone + Ring↔G2 | HIGH | R1 analysis confirmed: only battery/state/menu on phone link; full gestures go Ring→G2 directly |
| **FCC ID** | 2BFKR-R01 | HIGH | Even.app regulatory strings |
| **HVIN** | Even R01 | HIGH | Even.app: "Even R1 HVIN: Even R01" |
| **Model Variant** | S201 (possible next-gen or alternate SKU) | LOW | Single "S201" reference in Even.app strings alongside S200 |

### Glasses Case — Secondary Device

| Property | Value | Confidence | Evidence |
|---|---|---|---|
| **Product Name** | Even G2 Case | HIGH | Even.app: "Model Name: Even G2 Case", "Smart Glasses Case" |
| **Communication** | Via G2 glasses (not direct BLE to phone) | HIGH | No separate BLE service UUID; uses `glasses_case` protobuf module via G2 control channel |
| **Protocol** | `GlassesCaseDataPackage` protobuf with `eGlassesCaseCommandId` | HIGH | Dedicated protobuf module `glasses_case` (@1415496902), `GlassesCaseInfo` model |
| **App ID** | `UX_GLASSES_CASE_APP_ID` | HIGH | Even.app string reference |
| **Capabilities** | Battery level, charging status | MEDIUM | `GlassesCaseInfo` model in Even.app |
| **Firmware** | Separate case firmware payload exists (`firmware/box.bin`) | HIGH | CDN OTA `EVENOTA` entry type 6 (55,296 bytes) |

### R1 Charger — Passive Accessory

| Property | Value | Confidence | Evidence |
|---|---|---|---|
| **Product Name** | Even R1 Charger | HIGH | Even.app: "Model Name: Even R1 Charger", "Smart Ring Charger" |
| **FCC ID** | 2BFKR-R1C | HIGH | Even.app regulatory strings |
| **IC** | 32408-R1C | HIGH | Even.app regulatory strings |
| **Firmware** | None — passive charging cradle | HIGH | No BLE service, no DFU capability, no firmware references in Even.app |

### Regulatory Identifiers (all products)

| Product | FCC ID | IC | HVIN |
|---|---|---|---|
| Even G2 Glasses | 2BFKR-G2 | 32408-G2 | — |
| Even R1 Ring | 2BFKR-R01 | 32408-R01 | Even R01 |
| Even R1 Charger | 2BFKR-R1C | 32408-R1C | — |

---

## 2. Device-to-Firmware Mapping

> See also: [firmware-files.md](firmware-files.md) for EVENOTA container format and component details.

### Which firmware covers which device?

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Firmware Package              │ Target Device       │ Notes                  │
├──────────────────────────────────────────────────────────────────────────────┤
│ B210_BL_DFU_NO_v2.0.3.0004    │ G2 Left + G2 Right  │ Production bootloader  │
│ B210_ALWAY_BL_DFU_NO          │ G2 Left + G2 Right  │ Recovery bootloader    │
│ B210_SD_ONLY_NO_v2.0.3.0004   │ G2 Left + G2 Right  │ SoftDevice (BLE stack) │
│ s200_firmware_ota.bin (CDN)   │ G2 Left + G2 Right  │ Main app image present │
│ firmware/touch.bin (CDN OTA)  │ Touch controller    │ FWPK-wrapped component │
│ firmware/codec.bin (CDN OTA)  │ Audio codec MCU     │ FWPK-wrapped component │
│ firmware/ble_em9305.bin (CDN) │ EM9305 BLE radio    │ Segmented patch format │
│ firmware/box.bin (CDN OTA)    │ Glasses case MCU    │ Separate case firmware │
├──────────────────────────────────────────────────────────────────────────────┤
│ R1 Ring firmware (CDN)        │ R1 Ring only        │ Nordic DFU + MCUmgr    │
├──────────────────────────────────────────────────────────────────────────────┤
│ (none)                        │ R1 Charger          │ Passive device         │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Key findings:**

1. **G2 Left and G2 Right share identical firmware images**. Current CDN OTA payloads provide one shared S200 application image (`ota/s200_firmware_ota.bin`) for both eyes, and the older B210 bootloader/stack bundles were also shared. Left/right identity is runtime configuration (GATT name: `Even G2_32_L_xxx` vs `Even G2_32_R_xxx`), not a firmware build split.

2. **The Glasses Case does have separate firmware payloads**, but delivery is mediated by the G2. The OTA package contains `firmware/box.bin` (entry type 6), and case update orchestration is still routed through the glasses (`glasses_case` protobuf / `UX_GLASSES_CASE_APP_ID`) rather than direct BLE from phone to case.

3. **The R1 Ring has its own firmware**, updated via Nordic DFU (FE59 buttonless service) + MCUmgr (SMP characteristic). The R1 firmware is downloaded from CDN on demand, not bundled in the app. It uses a completely different update protocol from the G2.

4. **The R1 Charger is a passive accessory** with its own FCC ID (2BFKR-R1C) but no firmware, no BLE, and no update capability. It is the charging cradle for the R1 Ring — there is no separate "R1 Dock" product.

5. **No G1 firmware in bundle**, but Even.app retains G1 glasses command protocol infrastructure (legacy support).

---

## 3. Legacy Nordic DFU Memory Map (B210 Bundle, Not Main S200 Runtime)

> This section describes the older Nordic B210 DFU bundle extracted from Even.app (`B210_*` images). It is useful for legacy/auxiliary DFU analysis, but it is **not** the runtime memory map of the current S200 Apollo510b application in `ota/s200_firmware_ota.bin`.

```
nRF52840 Flash (1 MB):
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 0x00000000 │ MBR (Master Boot Record)                      │   4 KB     │
  ├────────────┼───────────────────────────────────────────────┼────────────┤
  │ 0x00001000 │ SoftDevice S140 v7.0.0                        │ 153 KB     │
  │            │   BLE stack, radio driver, SVC dispatch       │            │
  │            │   Info struct at 0x2000 (magic 0xFFFFFF2C)    │            │
  │            │   FWID 0x0100, API version 140                │            │
  ├────────────┼───────────────────────────────────────────────┼────────────┤
  │ 0x00027000 │ Application Firmware                          │ ~836 KB    │
  │            │   G2 protocol handlers, display driver,       │  (NOT      │
  │            │   gesture input, audio/mic, NUS service,      │  EXTRACTED)│
  │            │   protobuf codec, file system (L:/R:/)        │            │
  ├────────────┼───────────────────────────────────────────────┼────────────┤
  │ 0x000F8000 │ Bootloader (Secure DFU)                       │  24 KB     │
  │            │   Nordic DFU state machine, flash writer,     │            │
  │            │   ECDSA P-256 signature verification          │            │
  ├────────────┼───────────────────────────────────────────────┼────────────┤
  │ 0x000FE000 │ Bootloader Settings                           │   4 KB     │
  │            │   Boot validation, CRC, app validity flag     │            │
  ├────────────┼───────────────────────────────────────────────┼────────────┤
  │ 0x000FF000 │ MBR Parameters                                │   4 KB     │
  └────────────┴───────────────────────────────────────────────┴────────────┘

RAM (256 KB):
  0x20000000 – 0x200059C3: SoftDevice RAM (~22.4 KB, confirmed from binary)
  0x200059C4 – 0x2003FFFF: Application RAM (~233 KB)
  SoftDevice stack pointer: 0x200013C0
  Bootloader stack pointer: 0x2000CFA0
```

**Refined from binary analysis**: The SoftDevice SRAM boundary at 0x200059C4 was extracted from the SoftDevice binary. This is lower than the typical ~48 KB estimate, leaving more RAM for the application firmware.

**Scope note**: The above layout applies to the legacy B210 DFU bundle (now at `captures/firmware/B210_*/`). The CDN OTA package at `captures/firmware/g2_2.0.7.16.bin` **does** include the S200 application image (`ota/s200_firmware_ota.bin`), plus touch/codec/EM9305/case component firmware payloads.

---

## 4. Boot Process

> **Scope**: This section describes the **Nordic DFU boot process** (nRF52840 MBR → SoftDevice → Application). For the Apollo510b application bootloader boot process (0x00410000 → 0x00438000 VTOR handoff), see [s200-bootloader.md](s200-bootloader.md).

### Power-On Sequence (inferred from Nordic SDK architecture + firmware binaries)

```
┌──────────────────────────────────────────────────────────────────────┐
│  1. RESET                                                            │
│     ARM Cortex-M55 reads vector table at 0x00000000                  │
│     Initial SP = 0x2000C013 (MBR stack)                              │
│     Reset handler = 0x00025FE1 (MBR entry point)                     │
├──────────────────────────────────────────────────────────────────────┤
│  2. MBR (Master Boot Record, 4 KB)                                   │
│     Checks bootloader settings page at 0xFE000                       │
│     If DFU trigger set OR no valid app: → jump to Bootloader         │
│     If valid app: → forward SVC calls, jump to SoftDevice            │
├──────────────────────────────────────────────────────────────────────┤
│  3a. SOFTDEVICE S140 (normal boot)                                   │
│     Initializes BLE radio hardware (RADIO peripheral)                │
│     Configures 2.4 GHz transceiver, BLE link layer                   │
│     Sets up SVC interrupt handler for SD API calls                   │
│     Reserves RAM 0x20000000 – 0x2000BFFF                             │
│     Jumps to application at 0x00027000                               │
├──────────────────────────────────────────────────────────────────────┤
│  3b. BOOTLOADER (DFU mode)                                           │
│     SP = 0x2000CFA0, Reset handler = 0x0008FD9 (relative to 0xF8000) │
│     Advertises as "B210_DFU" via Nordic DFU UUID 8EC90000-...        │
│     Waits for signed firmware image via BLE                          │
│     Verifies ECDSA P-256 signature against embedded public key       │
│     Writes validated firmware to flash                               │
│     Resets to normal boot                                            │
├──────────────────────────────────────────────────────────────────────┤
│  4. APPLICATION (runtime)                                            │
│     Registers BLE services (G2 custom + NUS + GATT standard)         │
│     Initializes display controller, touch/gesture handler            │
│     Starts auth listener, heartbeat timer, sensor streams            │
│     Enters main event loop (SD events + app timers)                  │
└──────────────────────────────────────────────────────────────────────┘
```

### DFU Mode Entry Triggers

The G2 enters bootloader (DFU) mode when:
1. **GPREGRET magic values**: Written by application firmware via `sd_power_gpregret_set()` before reset. Five values trigger DFU (checked in cascading CMP sequence at fail-safe 0x2FBE / versioned 0x304E):
   - `0xB1` — Nordic standard `NRF_BL_DFU_ENTER_METHOD_GPREGRET` (highest priority, checked first via GPREGRET2)
   - `0x01` — Generic DFU entry
   - `0xA5` — Debug/development DFU mode
   - `0xAA` — Bootloader retain (stay in bootloader, do not jump to app)
   - `0xAC` — Alternate DFU mode (possibly serial DFU vs OTA)
2. **No valid application**: Bootloader settings page (`0xFF000`) CRC indicates corrupted/missing app image
3. **Button press during boot**: Hardware button held during power-on (typical Nordic pattern, exact GPIO TBD)
4. **BLE command**: FE59 Buttonless DFU service triggers controlled reset into DFU mode (writes GPREGRET then resets)

When in DFU mode, the device advertises as `B210_DFU` with the Nordic Secure DFU service UUID instead of normal G2 services.

**Watchdog timer**: Both bootloaders configure WDT at 0x40010000 with Nordic standard reload magic `0x6E524635` via WDT.RR[0].

---

## 5. SoftDevice Analysis

> **Scope**: This section describes the **Nordic SoftDevice S140** from the DFU bootloader bundle in `Even.app`. It does NOT apply to the G2's Apollo510b runtime, which uses the Cordio BLE stack. The SoftDevice is relevant to the R1 Ring DFU path and the G2's failsafe Nordic DFU bootloader.

### SoftDevice S140 v7.0.0

| Field | Value | Location |
|---|---|---|
| Magic marker | `0xFFFFFF2C` | softdevice.bin offset 0x2000 |
| SD variant magic | `0x51B1E5DB` | softdevice.bin offset 0x2004 |
| APP_CODE_BASE | `0x00027000` (156 KB) | softdevice.bin offset 0x2008 |
| FWID | `0x0100` (S140 v7.0.0) | softdevice.bin offset 0x200C |
| BLE API version | `0x8C` (140) | softdevice.bin offset 0x2010 |
| SD version encoding | `7,002,000` → v7.2.0 | softdevice.bin offset 0x2014 |
| Binary size | 153,140 bytes | `B210_SD_ONLY_NO_v2.0.3.0004/softdevice.bin` |
| SHA-256 | `90d76a00...0446062c` | Code integrity hash in SD info struct |
| ASCII strings | `nRF5x` only | No app-level strings present |
| SVC opcodes | 2 (0xFE + 0xFF) | ARM SVC instruction scan (757× `SVC 0xFF`, 1× `SVC 0xFE`) |
| API functions | 84 unique (via dispatch tables) | Function pointer table analysis at 0x25148 + 0x25248 |

**Note on version discrepancy**: The FWID 0x0100 maps to S140 v7.0.0 in Nordic's official FWID registry, but the version encoding field reads v7.2.0. This likely means the binary was built from S140 v7.2.0 SDK sources but linked with FWID 0x0100 for backward compatibility with devices originally shipped with v7.0.0. The `sd_req` field `[0x0100, 0x0102]` confirms both S140 v7.0.0 (FWID 0x0100) and S140 v7.2.0 (FWID 0x0102) are accepted as prerequisites.

### SVC Dispatch Architecture

Nordic S140 uses a **two-level dispatch** mechanism — NOT one SVC number per API call:

1. **SVC 0xFE** (1 occurrence): SoftDevice enable (`sd_softdevice_enable`)
2. **SVC 0xFF** (757 occurrences): Universal API gate — extracts the function ID from the caller's link register and indexes into a function pointer dispatch table

**Main dispatch table** at file offset 0x25148 (64 entries, 59 real + 5 placeholders):

| Index | API Functions | Subsystem |
|---|---|---|
| 0-10 | `sd_ble_enable`, `sd_ble_evt_get`, `sd_ble_cfg_set`, `sd_ble_uuid_vs_add/decode/encode`, `sd_ble_version_get`, `sd_ble_user_mem_reply`, `sd_ble_opt_set/get`, `sd_ble_uuid_vs_remove` | BLE Common (11) |
| 12-23 | `sd_ble_gap_addr_set/get`, `sd_ble_gap_whitelist_set`, `sd_ble_gap_device_identities_set`, `sd_ble_gap_privacy_set/get`, `sd_ble_gap_adv_set_configure`, `sd_ble_gap_adv_start/stop`, `sd_ble_gap_conn_param_update`, `sd_ble_gap_disconnect`, `sd_ble_gap_tx_power_set` | GAP Connection (12) |
| 24-29 | `sd_flash_write/erase/protect`, `sd_evt_get`, `sd_power_system_off`, `sd_power_gpregret_*` | SoC/System (6) |
| 30-54 | GAP Security (authenticate, sec_params_reply, auth_key_reply, lesc_dhkey_reply, lesc_oob_data_*), GAP Info (appearance/ppcp/device_name set/get), PHY (scan/connect/phy_update/data_length), RSSI, QoS | GAP Extended (25) |
| 59-63 | `sd_ble_l2cap_ch_setup/release/rx/tx/flow_control` | L2CAP (5) |

**Second dispatch table** at file offset 0x25248 (29 entries):

| Index | API Functions | Subsystem |
|---|---|---|
| 0-10 | `sd_ble_gattc_primary_services_discover`, `sd_ble_gattc_relationships_discover`, `sd_ble_gattc_characteristics/descriptors_discover`, `sd_ble_gattc_attr_info_discover`, `sd_ble_gattc_read/write`, `sd_ble_gattc_hv_confirm`, `sd_ble_gattc_exchange_mtu_request` | GATTC (9) |
| 11-24 | `sd_ble_gatts_service/include/characteristic/descriptor_add`, `sd_ble_gatts_value_set/get`, `sd_ble_gatts_hvx`, `sd_ble_gatts_service_changed`, `sd_ble_gatts_rw_authorize_reply`, `sd_ble_gatts_sys_attr_set/get`, `sd_ble_gatts_exchange_mtu_reply` | GATTS (12) |
| 25-28 | `sd_clock_hfclk_request/release/is_running`, `sd_ppi_channel_enable` | Clock/PPI (4) |

**Total: 84 unique API functions** across 2 dispatch tables (59 + 25 real entries).

**ISR architecture**: All 9 SD-reserved IRQs use identical 6-byte forwarding stubs that jump to a unified ISR dispatcher at address 0x0000C194:

```
Stub (per IRQ):   LDR R3, =<handler>; LDR R1, =0xC195; BX R1
Dispatcher:       LDR R2, [0x2000005C]  ; SD enable flag
                  CMP R2, #0xCAFEBABE   ; is SD active?
                  BNE forward_to_app    ; no → app handler
                  BX  R3                ; yes → SD handler
```

The `CAFEBABE` magic at RAM address `0x2000005C` acts as the SD enable flag. When SD is disabled, all interrupts forward to application handlers.

### BLE Capabilities (confirmed from 84 API functions)

The S140 SoftDevice provides:
- **PHY Modes**: 1M, 2M, Coded PHY (LE Long Range) — confirmed by RADIO.MODECNF0 (0x40001650) and RADIO.PHYCNF (0x40001778) register references in SoftDevice
- **Data Length Extension**: Up to 251 bytes PDU
- **L2CAP Connection-Oriented Channels**
- **Extended Advertising**: Multiple advertising sets
- **TX Power Control**: Per-connection TX power adjustment
- **LE Secure Connections**: ECDH key exchange
- **Vendor-Specific UUIDs**: Custom 128-bit UUID support
- **AES-CCM/ECB**: Hardware-accelerated encryption
- **Flash operations**: SoftDevice-safe flash read/write/erase
- **Central + Peripheral + Observer + Broadcaster** roles simultaneously

### Interrupt Service Routines (from vector table analysis)

**SoftDevice** — 9 active ISR handlers:
| IRQ | Peripheral | Purpose |
|---|---|---|
| POWER_CLOCK | Power/Clock | Power management, clock events |
| RADIO | 2.4 GHz Radio | BLE packet TX/RX |
| TIMER0 | Timer 0 | BLE timing (reserved by SD) |
| RTC0 | Real-Time Counter 0 | BLE event scheduling |
| RNG | Random Number Generator | BLE address randomization, crypto |
| ECB | AES ECB | BLE encryption |
| CCM_AAR | AES-CCM + Address Resolver | BLE link encryption + privacy |
| SWI5_EGU5 | Software Interrupt 5 | SoftDevice event dispatch to app |
| MWU | Memory Watch Unit | Memory protection faults |

**Bootloader** — 4 active ISR handlers:
| IRQ | Peripheral | Purpose |
|---|---|---|
| WDT | Watchdog Timer | DFU timeout recovery |
| SWI2_EGU2 | Software Interrupt 2 | Flash operation completion |
| RTC2 | Real-Time Counter 2 | DFU timeout tracking |
| CRYPTOCELL | ARM CryptoCell-310 | ECDSA signature verification |

**Note**: The CryptoCell-310 is a hardware security module present on nRF52840 (but not nRF52832), providing hardware-accelerated ECDSA, AES, SHA-256, and TRNG. Its presence in the bootloader vector table further confirms nRF52840 identification.

### Peripheral Register References (from binary analysis)

**SoftDevice RESERVED** (exclusive SD control, application MUST NOT access):

| Peripheral | Base Address | ISR | Register Refs | Unique Regs | Key Registers |
|---|---|---|---|---|---|
| RADIO | 0x40001000 | IRQ1 | 58 | 37 | TASKS_TXEN/RXEN, MODE, PACKETPTR, DACNF, DFE GPIO/PACKET (BLE 5.1 direction-finding) |
| PPI | 0x4001F000 | — | 26 | 8 | CHENSET/CHENCLR (9+8 refs), CH[17-19] EEP/TEP. **Channels 0-16, 20-31 available to app** |
| TIMER0 | 0x40008000 | IRQ8 | 21 | 11 | TASKS_START (6 refs), CC[0-3] compare/capture for BLE timing |
| CCM/AAR | 0x4000F000 | IRQ15 | 16 | 10 | TASKS_KSGEN, MICSTATUS, ENABLE, CNFPTR — BLE link encryption + address resolution |
| MWU | 0x40020000 | IRQ32 | 11 | 5 | REGIONEN (7 refs) — memory protection for flash write safety |
| CLOCK/POWER | 0x40000000 | IRQ0 | 11 | 11 | HFCLKSTAT, LFCLKSRC, GPREGRET, DCDCEN, USBREGSTATUS, SYSTEMOFF |
| NVMC | 0x4001E000 | — | 6 | 3 | READY (poll), CONFIG (RW/erase mode), ICACHECNF |
| RTC0 | 0x4000B000 | IRQ11 | 5 | 4 | TASKS_START, COUNTER, PRESCALER — BLE event scheduling |
| RNG | 0x4000D000 | IRQ13 | 4 | 2 | TASKS_START, CONFIG (bias correction) |
| ECB (AES) | 0x4000E000 | IRQ14 | 3 | 2 | TASKS_STARTECB, ECBDATAPTR |
| EGU5/SWI5 | 0x40019000 | IRQ25 | 0 | 0 | SVC dispatch / SD event signaling (no direct register access) |

**SoftDevice RESTRICTED** (SD uses, app can access via SVC or with care):

| Peripheral | Base Address | Refs | Notes |
|---|---|---|---|
| GPIOTE | 0x40006000 | 1 | TASKS_OUT[0] only (PPI-driven GPIO toggle). App uses GPIOTE via SVC |
| TEMP | 0x4000C000 | 3 | TASKS_START (2 refs), result register. Used for HFCLK RC calibration; app accesses via `sd_temp_get` SVC |

**Application AVAILABLE** (zero SoftDevice references, free for G2 firmware):

| Peripheral | Base Address | Likely nRF52840 App Use |
|---|---|---|
| UART0/UARTE0 | 0x40002000 | Inter-eye UART link or serial debug |
| SPI0/TWI0 (TWIM0) | 0x40003000 | I2C sensor bus (IMU, compass, ALS) |
| SPI1/TWI1 (TWIM1) | 0x40004000 | I2C bus — **referenced in bootloader** (external EEPROM for DFU settings, separate from 0xFE000) |
| NFCT | 0x40005000 | NFC tag — almost certainly unused (no flow logic in app) |
| SAADC (ADC) | 0x40007000 | ALS ambient light sensor, battery voltage monitoring |
| TIMER1 | 0x40009000 | General timer |
| TIMER2 | 0x4000A000 | General timer |
| WDT | 0x40010000 | Watchdog timer (heartbeat feed) |
| RTC1 | 0x40011000 | Application timekeeping |
| QDEC | 0x40012000 | Quadrature decoder (unlikely used) |
| COMP/LPCOMP | 0x40013000 | Comparator |
| EGU0-4/SWI0-4 | 0x40014000-0x40018000 | Software interrupts (EGU0/1 may be used by SD via SVC) |
| TIMER3/4 | 0x4001A000/0x4001B000 | General timers |
| PWM0-3 | 0x4001C000+ | Display/LED brightness control |
| PDM | 0x4001D000 | **Digital microphone** (LC3 encode input, right eye) |
| PWM1/2 | 0x40021000/0x40022000 | Additional PWM channels |
| SPI2 (SPIM2) | 0x40023000 | **JBD display controller SPI bus** (confirmed: 205-byte frames at ~20Hz) |
| RTC2 | 0x40024000 | Application timekeeping |
| I2S | 0x40025000 | Audio interface (alt mic path or speaker) |
| FPU | 0x40026000 | Hardware floating point (display math) |
| USBD | 0x40027000 | USB device (charging detection or data) |
| UARTE1 | 0x40028000 | Second serial port |
| PWM3 | 0x40029000 | Additional PWM channel |
| SPIM3 | 0x4002F000 | High-speed SPI master |
| GPIO P0/P1 | 0x50000000/0x50000300 | All GPIO pins (SD does NOT access GPIO directly) |
| CryptoCell-310 | 0x5002A000 | **Not used by SD** — only used by bootloader for ECDSA DFU verification |

**PPI channel reservation**:

| Channels | Status |
|---|---|
| CH[0-16] | Application available |
| CH[17-19] | SD reserved (RADIO↔TIMER0 event-task wiring for BLE timing) |
| CH[20-31] | Application available |
| CHG[0] | SD reserved |
| CHG[1-5] | Application available |

**SD RAM state variables** (confirmed from literal pool analysis):

| RAM Address | Refs | Purpose |
|---|---|---|
| 0x20000004 | 5 | ISR forwarding base / state pointer |
| 0x20000008 | 2 | SD internal state |
| 0x2000005C | 7 | **SD enable flag** (`0xCAFEBABE` when active — checked by all ISR stubs) |
| 0x20000068 | 6 | SD internal state |
| 0x200001F0 | 2 | SD internal state |

**Key findings**:
- **No CryptoCell in SD**: All BLE crypto uses dedicated ECB and CCM/AAR hardware accelerators. CryptoCell-310 is exclusively used by the bootloader for ECDSA signature verification
- **No direct GPIO access**: SD never touches GPIO P0/P1 registers. All GPIO interactions go through GPIOTE TASKS for PPI-triggered events
- **BLE 5.1 direction-finding registers**: RADIO offsets 0x73C-0x788 (DFE GPIO pin selection, DFE packet registers) are accessed, indicating S140 v7.0.0 includes direction-finding radio driver support even on nRF52840
- **PPI wiring**: Channels 17-19 create hardware-timed RADIO↔TIMER0 event chains for BLE radio state machine without CPU intervention
- PDM presence confirms on-board digital microphone for voice capture. No GPIO pin assignments exist in bootloader or SoftDevice — all pin configuration is in the application firmware at 0x27000+

### SD Signature Block (address 0x000260C0)

```
+0x00: 0xCAFEBABE  — SD enable magic (written to RAM[0x2000005C] when active)
+0x04: 0x0000139B  — Build ID / internal version (5019)
+0x08: 0x00024485  — SVC dispatch function pointer
+0x0C: 0x00024E9F  — Secondary dispatch function pointer
+0x10: 0x20000004  — RAM state base pointer
+0x14: ISR forwarding stubs begin here
```

### MBR Magic Values

- `CAFEBABE` (`MBR_INIT_MAGIC`) found at SoftDevice offset 0x0324 — this is the initialization handshake magic between MBR and SoftDevice, confirming standard Nordic boot flow. The same magic is used as the SD enable flag at runtime (RAM address 0x2000005C).

### What the SoftDevice Does NOT Contain

The SoftDevice is purely a BLE radio/protocol stack. It does **not** contain:
- Any G2-specific protocol logic (all in application firmware)
- Display drivers, gesture handlers, or audio processing
- Protobuf encoding/decoding
- File system operations
- Application-level authentication

---

## 6. Bootloader Analysis

> **Scope**: This section describes the **Nordic DFU bootloader** from the Even.app bundle (`B210_BL_DFU_NO` / `B210_ALWAY_BL_DFU_NO`). These are nRF52840 bootloaders used for failsafe DFU recovery, NOT the Apollo510b application bootloader (`ota_s200_bootloader.bin`). For the Apollo510b bootloader, see [s200-bootloader.md](s200-bootloader.md).

### Two Bootloader Variants

| Package | Size | Variant | Purpose |
|---|---|---|---|
| `B210_BL_DFU_NO_v2.0.3.0004` | 24,420 bytes | Versioned | Production bootloader with version tracking |
| `B210_ALWAY_BL_DFU_NO` | 24,180 bytes | Fail-safe | Recovery bootloader (240 bytes smaller), always enters DFU |

Both share:
- Identical initial stack pointer: `0x2000CFA0`
- Identical vector table (all ISR handler addresses match)
- Identical P-256 curve constants from nrf_cc310 library (at different offsets)
- Full CC310 ECDSA verification code linked in (72 CC310 register references each)
- `B210_DFU` device name string embedded
- Nordic DFU UUID base: `8EC90000-F315-4F60-9FB8-838830DAEA50`
- `is_debug = TRUE` flag (allows re-flashing without version checks)
- Identical NVMC flash write routines (10 references each)

**Strings extracted from bootloader binaries** (`strings -n5`):
- `B210_DFU` — BLE advertised device name in DFU mode (offset 0x2BD7 in ALWAY, 0x2BE3 in v2.0.3)
- `nRFHp` — Nordic nRF code fragment (appears twice — main + relay code paths)
- `0123456789ABCDEF` — Hex digit table for debug/trace output during DFU operations (confirming debug printf capability in bootloader)
- No CC310 library marker strings ("CRYS", "nrf_cc310") — the library is compiled as a static blob without debug strings

**ALWAY variant differences** (240 bytes smaller, 6 code insertions):

The 240 extra bytes in the versioned bootloader are distributed across **6 insertion points**:

| # | Fail-safe Offset | Insertion Size | Content |
|---|---|---|---|
| 1 | 0x2AEC | +12 bytes | RAM address literal + small function stub (`MOVS R0, #1; STRB R0, [R1]; BX LR`) |
| 2 | 0x2F4C | **+132 bytes** | **Major**: enhanced boot validation with CC310 init, flash validation call (0x3004), MSR instructions setting CONTROL/BASEPRI/FAULTMASK/PRIMASK, jump-to-app sequence |
| 3 | 0x30A8 | +24 bytes | Error handler + function call to DFU settings (0x3988) + branch back |
| 4 | 0x30BC | +4 bytes | Literal pool entry: `0x000FAAE5` (flash function address) |
| 5 | 0x36C4 | +12 bytes | Hardware register write (`MOV.W R0, #0x10000; LSL R1, R0, #16; STR R0, [R1]`) |
| 6 | 0x57C0 | +4 bytes | Alignment padding (4 zero bytes) |

The 132-byte insertion (#2) at `0x2F58-0x2FDC` is the most significant — it represents an **enhanced boot validation path** that:
1. Validates the application image more thoroughly before jumping to it
2. Sets proper ARM privilege levels and interrupt state (MSR CONTROL, BASEPRI, FAULTMASK, PRIMASK)
3. Has additional error recovery paths with CC310 cleanup (branch to 0x1DC4)
4. Performs load-SP-and-PC jump-to-app sequence

The ALWAY variant skips this enhanced validation — `nrf_dfu_enter_check()` always returns true, so the bootloader always enters DFU mode regardless of GPREGRET state. Use case: factory provisioning (flash blank devices) or emergency recovery (bricked devices where settings page is corrupted).

**NVMC flash write routines** (identical in both bootloaders):

| Register | Address | Refs | Purpose |
|---|---|---|---|
| NVMC Base | 0x4001E000 | 1 | Base reference |
| NVMC READY | 0x4001E400 | 5 | Flash ready status polling |
| NVMC CONFIG | 0x4001E504 | 4 | Set read-only/write-enable/erase-enable mode |
| NVMC ERASEUICR | 0x4001E514 | 1 | UICR erase trigger |

Flash write pattern: `STR #1, [NVMC_CONFIG]` (enable writes) → perform write → poll `NVMC_READY` loop → `STR #0, [NVMC_CONFIG]` (back to read-only). No direct ERASEPAGE (`0x4001E508`) or ERASEALL (`0x4001E50C`) references — page/mass erase is handled via MBR SVC calls (SVC #0x29).

**DFU settings page access** (`0xFF000`): 6 functions in each bootloader handle settings read/write/validate, using SVC instructions for MBR-mediated flash operations.

**Bootloader tail structure** (both bootloaders):
```
0x000FA8F9  — Flash address (boot validation entry point)
0x00001000  — SoftDevice start address (4096 = 0x1000)
0x00100000  — End of flash / total flash size (1 MB)
0x03D09000  — HFCLK frequency constant (64,000,000 = 64 MHz)
```
All function pointer values differ by exactly **0xEC** (236 bytes) between fail-safe and versioned, confirming the code shift.

### DFU Init Packet Structure (decoded from .dat files)

The `.dat` files are Nordic DFU protobuf init packets with this structure:

```
Packet {
  signed_command (field 2) {
    command (field 1) {
      op_code: 1 (INIT)
      init (field 2) {
        fw_version: 3            // Bootloader version
        hw_version: 52           // nRF52 family
        sd_req: [0x0100, 0x0102] // Compatible SoftDevices
        type: 2                  // BOOTLOADER
        sd_size: 0
        bl_size: 24420           // Matches binary exactly
        app_size: 0
        is_debug: true
        hash: <SHA-256 of binary, little-endian>
        boot_validation: { type: 1 }
      }
    }
    signature: <64 bytes ECDSA P-256>
  }
}
```

**SoftDevice init packet** differs:
- `type: 1` (SOFTDEVICE)
- `sd_size: 153140` (matches softdevice.bin)
- `bl_size: 0`, `app_size: 0`
- `is_debug: false`
- `fw_version: 4294967295` (0xFFFFFFFF — max version, always accepted)

### ECDSA P-256 Crypto Constants & DFU Signing

**CORRECTION**: The data at offset 0x5DB4 (versioned) / 0x5CC4 (ALWAY) previously identified as a "custom DFU verification key" is actually the **standard P-256 generator point (Gx, Gy)**, part of the nrf_cc310 library's compiled-in crypto constants.

The complete P-256 curve constant layout (versioned bootloader):

| Offset | Parameter | Value (big-endian) |
|---|---|---|
| 0x5D50 | P (prime) | `FFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF` |
| 0x5D70 | A (curve param) | `FFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC` |
| 0x5D90 | N (curve order) | `FFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551` |
| 0x5DB4 | Gx (generator X) | `6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296` |
| 0x5DD4 | Gy (generator Y) | `4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B0840681C171DE0D1F2C34F` |

All values are stored in **little-endian** format in the binary (reversed byte order). The data previously called "hash prefix `512563fc`" is the tail of the P-256 curve order N (`...FC632551` → `512563fc` LE).

**Where is the actual DFU public key?** The custom Even Realities signing key is **NOT embedded as a visible 64-byte block** in either bootloader binary. It is likely:
1. Loaded from the **DFU settings page** (`0xFF000`) at runtime
2. Stored interleaved with other `nrf_dfu_validation` structure data
3. Provisioned during factory flashing (not in the bootloader image itself)

Both bootloaders have full CryptoCell-310 ECDSA verification code linked in (72 CC310 register references per bootloader, including 30+ PKA engine references for public key operations). The verification is NOT stubbed out — any DFU package MUST be signed with the correct private key.

**CC310 register usage breakdown** (per bootloader):

| CC310 Register Range | Purpose | References |
|---|---|---|
| +0x500 (ENABLE) | Power control (enable/disable CC310) | 4 |
| +0x1078-0x10E4 | PKA engine (public key accelerator for ECDSA) | ~30 |
| +0x1640-0x165C | Hash engine (SHA-256) | 10 |
| +0x17C8-0x17D0 | ECDSA signature verification registers | 3 |
| +0x1818-0x181C | AES/MAC control | 3 |
| +0x1900-0x1928 | RNG/DRBG | 4 |
| +0x1A04-0x1A24 | Interrupt/status | 8 |

**Second key found in Even.app binary** (this one IS likely a custom key):
```
X: 7a7de304b95ede3310178189bdf9828b9149b5acdcc6365e3fb7b58b4456119d
Y: 553442c9df04a6a417e55b8184501a30813e7f3c6395f1f66dd747c49f0fa398
```
This app-side key has higher entropy (~7.9 bits/byte) and likely serves as the actual DFU signing public key (loaded into bootloader at runtime from settings page), cloud API signing key, or R1 Ring DFU key.

### Naming Convention

```
B210_BL_DFU_NO_v2.0.3.0004
  │    │  │   │  └── Version string
  │    │  │   └───── NO = Nordic/Norway region code (default)
  │    │  └───────── DFU = Device Firmware Update package
  │    └──────────── BL = Bootloader payload
  └───────────────── B210 = Board/hardware revision

B210_ALWAY_BL_DFU_NO
       └───────────── ALWAY = "Always" enter DFU (fail-safe recovery)
```

---

## 7. Internal Hardware Communication

### G2 Glasses Internal Architecture (inferred)

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Even G2 Glasses                              │
│                                                                      │
│  ┌───────────────────┐     ┌───────────────────┐                     │
│  │   LEFT EYE        │     │   RIGHT EYE       │                     │
│  │   Apollo510b (L)  │◀═══▶│   Apollo510b (R)  │  Wired link         │
│  │   (auth primary)  │     │   (audio primary) │  (UART/I2C)         │
│  │  • Control 5401/02│     │  • Control 5401/02│                     │
│  │  • Display 6401/02│     │  • Display 6401/02│                     │
│  │  • File    7401/02│     │  • File    7401/02│                     │
│  │  • NUS     6E40xx │     │  • NUS     6E40xx │                     │
│  │  • Auth    (own)  │     │  • Auth    (own)  │                     │
│  │  • JBD Display    │     │  • JBD Display    │                     │
│  │  • Touchbar       │     │  • Mic/Audio      │                     │
│  └───────────────────┘     └───────────────────┘                     │
│          │                        │                                  │
│          │ BLE (phone link)       │ BLE (phone link)                 │
└──────────┼────────────────────────┼──────────────────────────────────┘
           │                        │
    ┌──────┴────────────────────────┴──────┐
    │            Phone (iOS/Android)       │
    │    Even.app connects to BOTH eyes    │
    │    simultaneously via CoreBluetooth  │
    └──────────────────────────────────────┘
```

### Dual-Eye Architecture

Each G2 eye is an **independent Apollo510b SoC** (with EM9305 BLE radio) with its own:
- BLE radio and connection to the phone
- Authentication state (auth success echoed independently, right eye ~2s late)
- Packet sequence counter (glasses-generated, never echoes TX seq)
- Display controller (JBD micro-display)
- Sensor suite

Evidence for dual independent SoCs:
- Both eyes respond to heartbeat independently with different sequence numbers (50-100ms apart)
- Auth responses arrive on both eyes separately (~2s delta)
- Per-eye firmware versioning in cloud API (`glasses_left_firmware_version`, `glasses_right_firmware_version`)
- Per-eye brightness calibration (`leftMaxBrightness`, `rightMaxBrightness`)
- Device names: `Even G2_32_L_56ACFA` (left) / `Even G2_32_R_3383CA` (right)

### Internal Eye-to-Eye Communication

The two eyes communicate via a **wired link** (HIGH confidence: UART or I2C through the glasses frame bridge). This is an application-level command relay, not a shared radio.

**Evidence for wired (not BLE) inter-eye link**:
- **Physical path**: Glasses frame has conductive traces/flex cable between temples — standard for dual-display eyewear (avoids BLE radio contention and latency)
- **Heartbeat multiplicity**: Each heartbeat TX produces 4 RX echoes (2 per eye). Each eye independently echoes to the phone, and forwards the command to the other eye via wired link, which also echoes. This explains the 50-100ms inter-eye timing offset
- **Auth keepalive is single-eye only**: Type=6 keepalive on 0x80-01 arrives from one eye only (~9.8s interval). If both eyes shared a BLE link, both would respond. Instead, the primary eye handles keepalive and relays auth state via wire
- **R1 Ring gesture relay**: Ring connects to one eye via BLE, but gestures appear on both eyes' response channels. The receiving eye forwards ring events to the other eye over the wired link
- **SoC peripheral evidence**: I2C (TWIM) and UART peripherals available on the Apollo510b. One of these interfaces likely serves as the inter-eye bus
- **No BLE evidence for inter-eye**: No secondary BLE connections observed in any capture; both eyes advertise independently to the phone, never to each other

**Primary/secondary eye roles** (MEDIUM confidence):
- **Left eye**: Primary for auth keepalive, primary BLE connection target (phone connects to left eye first)
- **Right eye**: Primary for microphone/audio (PDM peripheral, LC3 encoder), primary for R1 Ring BLE connection
- **Both eyes**: Independent display controllers, independent sensor suites, independent packet sequence counters

**Display is monoscopic** (HIGH confidence):
- Same display content rendered to both eyes (no stereo disparity)
- All display commands sent to both eyes simultaneously with identical payloads
- Single display config region set (no left/right offset or stereo parameters)
- EvenHub canvas is 576×288 — a single viewport, not a stereo pair

**Firmware transport protocol layer** (from `service_codec_host.c` log strings):
- Message format: `"Pack message: cmd=0x%04X(NR=0x%02X, TYPE=0x%02X), seq, flags, length, crc32"`
  - `NR` (high byte) = service number (matches service_hi in G2 packet)
  - `TYPE` (low byte) = command type within service (matches service_lo)
  - `seq` = sequence counter, `flags` = reliability/ack flags
  - `crc32` = full message checksum
- Unhandled message type error: `"[TF] :errorUnhandled message, type %d"`
- Timeout handling: `"_rxNextPacketTimeout: forwarding to BLE thread, serviceID, syncID, pipeID"` — TPL (Transport Protocol Layer) forwards timeouts to BLE thread for retry/error handling

**Inter-eye relay protocol** (from firmware binary strings):
- `SEND_DATA_TO_PEER` — forward raw data to peer eye via wired link
- `SEND_INPUT_EVENT_TO_PEERS` — forward user input events (gestures, touch) to peer
- Each relay message carries an `applicationID` for routing to the correct handler on the receiving eye
- Received phone commands are forwarded to the peer eye (application-level relay, not BLE eavesdropping)
- Each eye generates its own response independently (different packet sequence numbers, different timing)
- Config state changes (`0x0D-01` display mode) synchronize both eyes — one eye notifies the phone, the other reflects the change locally
- The `selectPipeChannel` / `BleG2PsType` mechanism routes traffic to the correct BLE characteristic (control/display/file) but does NOT control inter-eye routing

### Peripheral Connections

Note: SPI/I2C addresses below are from DFU bootloader analysis (nRF52840). The Apollo510b runtime uses equivalent MSPI/I2C interfaces — see [g2-glasses.md](../devices/g2-glasses.md) for the confirmed hardware BOM.

| Peripheral | Interface | Eye | Evidence | Status |
|---|---|---|---|---|
| JBD Micro-Display | MSPI (drv_mspi_jbd4010) | Both | 205-byte frames at ~20Hz, LFSR-scrambled sensor telemetry (5×40-byte blocks + 5-byte trailer). Scrambling is hardware LFSR in display controller silicon, not SoC firmware | Active — JBD display controller with integrated IMU/sensors |
| Touchbar | I2C (CY8C4046FNI) | Both(?) | `drv_cy8c4046fni.c` driver; gesture events on 0x01-01 (tap/swipe) and 0x0D-01 (long press) | Active |
| Microphone | PDM → GX8002B codec | Right only | Audio frames on NUS RX with 0xF1 prefix; LC3 codec on-device via GX8002B | Active |
| ALS (Ambient Light Sensor) | I2C (OPT3007) | Both(?) | `ALSInfo` protobuf message (@2347168945); auto-brightness; `drv_opt3007.c` driver | Active |
| Magnetometer/Compass | I2C (likely TWIM) | Both(?) | Compass calibration + heading changes, user instruction: "look around to calibrate compass" | Active |
| IMU (Accel/Gyro) | I2C/SPI (ICM-45608) | Both(?) | `imu_icm45608.c` driver; head angle in display stream trailer; `MotionSettingsOutModel` | Active |
| Wear Detection Sensor | GPIO/ADC | Both(?) | `Wear_Detection_Setting`, `setWearDetection`, configurable on/off switch. **Wear detection gates BLE transmission**: `isSendAllow isWearing = false` blocks command TX when not worn | Active |
| NFC (Near Field Communication) | NFCT (0x40005000) | Unknown | NFC peripheral found in DFU bootloader SoftDevice analysis (nRF52840) — not confirmed on Apollo510b runtime | Almost certainly unused — no NFC flow logic in app |

**Compass/magnetometer protocol** (5 OS notification events):
- `OS_NOTIFY_COMPASS_CALIBRATE_STRAT` (typo "STRAT" in original) — calibration started
- `OS_NOTIFY_COMPASS_CALIBRATE_COMPLETE` — calibration complete
- `OS_NOTIFY_COMPASS_CHANGED` — heading changed
- `OS_NOTIFY_LOCATION_SELECTED` — user selected a location (navigation context)
- `OS_NOTIFY_MENU_STARTUP_REQUEST_LOCATION_LIST` — menu requests favorite locations
- Related: `CompassCalibrateStatus`, `compassIndex`, `compassMsg`

**Sensor ICs** (confirmed from OTA firmware strings): ICM-45608 (TDK InvenSense IMU, `imu_icm45608.c`), OPT3007 (TI ALS, `opt3007_registers.c`), CY8C4046FNI (Cypress touch, `drv_cy8c4046fni.c`). The `imu7` reference may indicate a 7-axis IMU configuration (accel + gyro + magnetometer) or a sensor config parameter. Compass/magnetometer IC is not yet identified from firmware strings.

**TWIM1 (I2C bus 1) in bootloader**: The bootloader references TWIM1, suggesting an I2C-connected external flash or EEPROM used for DFU settings persistence. This is separate from the internal flash at 0xFE000 (bootloader settings page).

**JBD display MSPI bus**: The SoC reads 200-byte sensor telemetry blocks from the JBD display IC via MSPI (`drv_mspi_jbd4010`), appends a 5-byte trailer (activity, padding, head angle int16, counter), and forwards the 205-byte frame over BLE characteristic 0x6402 at ~20 Hz. The LFSR scrambling occurs inside the display controller silicon before readout — the SoC handles raw bytes without descrambling. (Note: SPIM2 at 0x40023000 was identified from DFU bootloader analysis; the Apollo510b runtime uses MSPI.)

### Power Management

**Battery status fields** (from ProtoBaseSettings):
- `batteryStatus0` — left eye battery level (%)
- `batteryStatus1` — right eye battery level (%)
- `deviceRunningStatus` — overall device power state

**Charging telemetry fields** (from ProtoBaseSettings):
- `chargingCurrent` — charging current (mA)
- `chargingTemp` — charging temperature
- `chargingVBat` — battery voltage during charging
- `chargeStates` — charge state enum
- `chargingStatus` — overall charging status (0=not charging, 1=charging)
- `chargingError` — error code
- `readChargeStatus` — query command

Note: Standard BLE Battery Service (0x180F) does NOT exist on G2 (confirmed by probe). All battery data arrives through the proprietary protocol, likely via device info 0x09-xx or ProtoBaseSettings on 0x0D-00.

**Per-eye power control**:
- `powerLeft` / `powerRight` — individual eye power status
- `powerControl` — power management command
- `powerOff` / `shutdown` / `shutdownRead` / `shutdownWrite` — shutdown commands
- `wakeFromSleep` — wake command

**Low power mode**: Glasses support a `low_power_mode` toggle. R1 Ring has a separate `setRingLowPerformanceMode` that reduces ring activity. Both have corresponding UI toggles.

### ProtoBaseSettings Method Map (19 methods on 0x0D-00)

All methods route through `ProtoBaseSettings` → `G2SettingPackage` → service 0x0D-00:

| Method | Purpose |
|---|---|
| `setBrightness` | Set brightness level (0-42) |
| `setBrightnessAuto` | Toggle auto-brightness |
| `setBrightnessCalibration` | Per-eye brightness calibration (left/right max) |
| `setGlassGridDistance` | Display X offset (via `DisplaySettingsExt`) |
| `setGlassGridHeight` | Display Y offset (via `DisplaySettingsExt`) |
| `headUpSetting` | Head-up angle/switch/trigger (via `MotionSettingsExt`) |
| `setSilentMode` | Silent mode toggle |
| `setWearDetection` | Wear detection enable/disable |
| `setOnBoardingStartUp` | Trigger onboarding startup |
| `setOnBoardingStart` | Start onboarding sequence |
| `setOnBoardingEnd` | End onboarding sequence |
| `requestScreenOffInterval` | Query auto screen-off timer |
| `updateScreenOffInterval` | Set auto screen-off timer |
| `setGestureControlList` | Configure gesture→action mappings |
| `getGlassesConfig` | Query current config (brightness, grid, headUp, wearDetection, workMode) |
| `getGlassesIsWear` | Query current wear status |
| `getOnGlassesWear` | Register wear status callback |
| `getBoardingIsHeadup` | Check head-up during onboarding calibration |
| `getGlassesCaseInfo` | Query case battery/charging/in-case status |
| `sendSysLanguageChangeEvent` | Sync language setting |

### Display Settings (from G2SettingPackage `DeviceReceive_*`)

| Setting | Description |
|---|---|
| `DeviceReceive_Brightness` | Brightness level 0-42 |
| `DeviceReceive_X_Coordinate` | Horizontal display offset (per-user calibration) |
| `DeviceReceive_Y_Coordinate` | Vertical display offset (per-user calibration) |
| `DeviceReceive_APP_PAGE` | Active application page |
| `DeviceReceive_Head_UP_Setting` | HeadUp display trigger angle |
| `DeviceReceive_Advanced_Setting` | Advanced display settings |
| `DeviceReceive_Silent_Mode_Setting` | Silent mode |

**Universal settings** (from firmware binary strings, synced via ProtoBaseSettings):
| Setting | Purpose |
|---|---|
| `metric_unit` | Metric vs imperial units |
| `date_format` | Date display format |
| `distance_unit` | Distance display unit |
| `temperature_unit` | Temperature display unit (°C/°F) |
| `time_format` | 12h vs 24h time format |
| `dominant_hand` | Left/right hand preference (affects gesture interpretation) |

**Grid settings**: `setGlassGridDistance` / `setGlassGridHeight` — control display projection geometry (optical calibration).

**Screen off**: `auto_screen_off` with `requestScreenOffInterval` / `updateScreenOffInterval`. Option: `allow_long_press_while_display_off`.

**HeadUp dashboard**: Motion-triggered display activation. Configurable `wakeupAngle` via `MotionSettingsExt|setHeadUpAngle`. `setHeadUpTriggerDashboard` enables motion-activated dashboard.

---

## 8. BLE Communication Architecture

### G2 BLE Service/Characteristic Map

**Base UUID**: `00002760-08C2-11E1-9073-0E8AC72Exxxx`

| Suffix | Full UUID | Role | Properties | Purpose |
|---|---|---|---|---|
| `0001` | `...0001` | Service discovery | Write | Registration/binding |
| `0002` | `...0002` | Service discovery | Notify | Registration/binding |
| `1001` | `...1001` | Unknown | Unknown | Possibly OTA or bidirectional pipe |
| **5401** | `...5401` | **Control TX** | Write Without Response | All G2 protocol commands (phone→glasses) |
| **5402** | `...5402` | **Control RX** | Notify | All G2 protocol responses (glasses→phone) |
| `5450` | `...5450` | Control service | Service declaration | Parent service UUID for control pipe (5401/5402 are children) |
| **6401** | `...6401` | **Display TX** | Write Without Response | Display rendering commands |
| **6402** | `...6402` | **Display RX** | Notify | LFSR-scrambled sensor stream (~20Hz, 205 bytes) |
| `6450` | `...6450` | Display service | Service declaration | Parent service UUID for display pipe (6401/6402 are children) |
| **7401** | `...7401` | **File TX** | Write Without Response | File transfer commands + data |
| **7402** | `...7402` | **File RX** | Notify | File transfer ACKs (2-byte LE status) |
| `7450` | `...7450` | File service | Service declaration | Parent service UUID for file pipe (7401/7402 are children) |

**Private Service Types (BleG2PsType)** — runtime characteristic routing via `selectPipeChannel`:
- Type 0 = Basic/Control (5401/5402, service 5450)
- Type 1 = File (7401/7402, service 7450)
- Type 2 = Display (6401/6402, service 6450)

`selectPipeChannel` is a settings command on 0x0D-00 that dynamically switches which BLE pipe is active. `PipeRoleChange` / `PIPE_ROLE_CHANGE2` events fire when the active characteristic set changes. This may enable bandwidth management or concurrent operations (e.g., file transfer on one pipe while display updates continue on another).

### Nordic UART Service (NUS)

| UUID | Role |
|---|---|
| `6E400001-B5A3-F393-E0A9-E50E24DCCA9E` | NUS Service |
| `6E400002-B5A3-F393-E0A9-E50E24DCCA9E` | NUS TX (phone→glasses) |
| `6E400003-B5A3-F393-E0A9-E50E24DCCA9E` | NUS RX (glasses→phone) |

NUS uses simple 1-2 byte commands (no G2 packet envelope):
- `0xF5 + code`: Gesture events (tap=0x01, double=0x00, triple=0x04/0x05, long=0x17, release=0x24, slide fwd=0x02, slide back=0x03)
- `[0x0E, 0x01]`: Enable microphone
- `[0x0E, 0x00]`: Disable microphone
- `0x4E + UTF-8`: Text display
- `0x15 + BMP`: Image display
- `0x25`: Heartbeat (single byte)
- `0xF1 + PCM data`: Audio frame (mic stream, right eye only)

### R1 Ring BLE Services

| UUID | Role |
|---|---|
| `BAE80001-4F05-4503-8E65-3AF1F7329D1F` | Ring Primary Service |
| `BAE80012-...` | Ring TX (phone→ring write) |
| `BAE80013-...` | Ring RX (ring→phone notify) |
| `FE59` | Nordic Buttonless Secure DFU |
| `DA2E7828-FBCE-4E01-AE9E-261174997C48` | SMP/MCUmgr (firmware transfer) |

**R1 initialization**: Write `0xFC`, 200ms pause, write `0x11`, then keepalive `0x11` every 5s.

**R1 gesture format**: `[0xFF] [type] [param]` — types: 0x03=HOLD, 0x04=TAP, 0x05=SWIPE.

### Firmware BLE Profile Implementations (from binary analysis)

The `ota_s200_firmware_ota.bin` binary contains source path references to 7 dedicated BLE profile implementations, each with independent CCCD (Client Characteristic Configuration Descriptor) management:

| Profile | Source Path | Purpose | CCCD Pattern |
|---------|------------|---------|-------------|
| **EFS** | `profile_efs.c` | Even File Service — file transfer, maps, images | `cccdEnable`/`ProcCccState` |
| **EUS** | `profile_eus.c` | Even UART Service — NUS-compatible UART bridge | `cccdEnable`/`ProcCccState` |
| **NUS** | `profile_nus.c` | Nordic UART Service — gestures, mic, text display | `cccdEnable`/`ProcCccState` |
| **OTA** | `profile_ota.c` | OTA firmware update service | `cccdEnable`/`ProcCccState` |
| **Ring** | `profile_ring.c` | R1 Ring integration profile | `cccdEnable`/`ProcCccState` |
| **GATT** | `profile_gatt.c` | Standard GATT service | `cccdEnable`/`ProcCccState` |
| **ANCS** | `profile_ancc.c` | Apple Notification Center Service (iOS push) | `cccdEnable`/`ProcCccState` |

**EFS vs NUS**: EFS (Even File Service) handles structured file transfers (BMP maps, notification images) on the 0x7401/0x7402 characteristic pair. EUS (Even UART Service) is a separate UART bridge profile — relationship to NUS unclear (may be G2-native vs Nordic-standard variant). Both coexist in firmware.

**ANCS** (Apple Notification Center Service): Confirms native iOS notification forwarding support — the glasses can receive Apple push notifications directly via ANCS without phone-side relay, though the Even.app also implements explicit notification forwarding on 0x02-20.

**ANCS whitelist filtering** (from firmware binary strings): The glasses firmware maintains a whitelist of app bundle IDs. Only notifications from whitelisted apps are forwarded to the display. The whitelist is configured by the phone app via the notification file transfer protocol (the `user/notify_whitelist.json` file sent via 0xC4/0xC5). This explains the dual notification path: ANCS handles native iOS push delivery, while the custom 0x02-20 protocol handles filtered, formatted notification display.

### G2 BLE Standard Services

| Service UUID | Name | Status |
|---|---|---|
| 0x1800 | Generic Access | Present (device name, appearance) |
| 0x1801 | Generic Attribute | Present |
| 0x180A | Device Information | Present (model, FW version, HW version, manufacturer, SN) |
| 0x180F | Battery Service | **NOT present** (confirmed via probe) |

### G2 ATT Handle Map

| Handle | Characteristic | Role |
|---|---|---|
| 0x0842 | 5401 | Control TX (write) |
| 0x0844 | 5402 | Control RX (notify) |
| 0x0864 | 6402 | Display RX (notify) |
| 0x0874 | 7401 | File TX (write) |
| 0x0876 | 7402 | File RX (notify) |
| 0x0884 | (secondary) | Secondary control |

### Connection Parameters

```
Connection Interval: 7.5ms – 30ms (typical)
Slave Latency: 0
Supervision Timeout: 2000ms
MTU: 512 bytes (negotiated via GATT)
Simultaneous Connections: 2 (left + right eye to phone)
PHY: 1M (default), 2M (high throughput), Coded (long range)
```

**Measured throughput** (from BLE capture analysis):
- Display sensor stream: 205 bytes × ~20 Hz ≈ **4.1 kB/s** per eye (sustained when display active)
- Audio stream: 40 bytes × 100 Hz (10ms frames) ≈ **4.0 kB/s** (right eye mic only)
- Max display write: 204 bytes per 0x6401 command
- Max file fragment: 174 bytes per data chunk (204 − 30 bytes protobuf overhead)
- Max G2 packet payload: 244 bytes (observed in file transfer captures)

### Host-Side BLE Connection State Machine

The Even.app (via `flutter_ezw_ble`) follows this connection sequence:
```
connecting → contactDevice → searchService → searchChars → startBinding → connectFinish
```

**Error states**: `emptyUuid`, `noBleConfigFound`, `noDeviceFound`, `alreadyBound`, `boundFail`, `serviceFail`, `charsFail`, `timeout`, `bleError`, `systemError`

**iOS background persistence**: The Even.app uses a `SilentAudioPlayer` that plays `teleprompt_silence_misuc.mp3` via AVAudioSession. Background keepalive sends heartbeats every **3 seconds** (`_startBackgroundKeepAlive` / `_stopBackgroundKeepAlive`).

**L2CAP channel support**: The `even_runner` native binary includes `CBL2CAPChannel` delegate methods (`peripheral:didOpenL2CAPChannel:error:`), indicating L2CAP Connection-Oriented Channels are supported. L2CAP provides higher-throughput BLE data transfer than GATT characteristics — likely used for OTA firmware updates or bulk file transfers where the 512-byte MTU GATT path is a bottleneck.

### Protocol Timing Constants (from Even.app)

These timing values are hardcoded in the Even.app and define the expected firmware response windows:

| Timer | Value | Context |
|---|---|---|
| BLE command response timeout | **30s** | Maximum time app waits for firmware ACK. Commands with delayed ACKs (Controller: 53-468ms, Tasks: 69-103ms) are well within limit. Longer delays cause silent failures |
| BLE reconnect interval | **20s** | Time between reconnection attempts after disconnect |
| Soniox session limit | **2h** | Maximum duration for Soniox ASR/translate sessions |
| Audio pipeline startup | **3s** | Delay before first audio frame expected after mic enable |
| Weather update interval | **15s** | Dashboard weather widget polling |
| Conversate segment interval | **50-1000ms** | Valid range for ASR partial result delivery |
| ASR result delivery interval | **100-1000ms** | Valid range for final transcription delivery |
| Background keepalive | **3s** | Silent audio heartbeat interval (iOS background persistence) |
| Auth keepalive | **~9.8s** | Firmware-originated 0x80-01 type=6 interval |
| Device info periodic | **~15s** | Unsolicited 0x09-01 responses from firmware |

---

## 9. G2 Protocol Packet Format

### Packet Envelope

```
┌────┬──────┬─────┬─────┬───────┬─────┬────────┬────────┬──────────┬──────────┐
│ AA │ Type │ Seq │ Len │ Total │ Num │ SvcHi  │ SvcLo  │ Payload  │ CRC16-LE │
│ 1B │  1B  │ 1B  │ 1B  │  1B   │ 1B  │  1B    │  1B    │ variable │   2B     │
└────┴──────┴─────┴─────┴───────┴─────┴────────┴────────┴──────────┴──────────┘
  │     │      │     │     │       │      └─────────┘       │         │
  │     │      │     │     │       │      Service ID        │         │
  │     │      │     │     │       │      (hi-lo pair)      │         │
  │     │      │     │     │       Fragment number          │         │
  │     │      │     │     Total fragments                  │         │
  │     │      │     Payload length + 2 (includes svc ID)   │         │
  │     │      Sequence counter (1-255, wraps)              │         │
  │     0x21=TX (phone→glasses), 0x12=RX (glasses→phone)    │         │
  Magic byte (always 0xAA)                                  │         │
                                                    Protobuf payload  │
                                              CRC-16/CCITT over payload only
```

**CRC-16/CCITT**: Init=0xFFFF, Poly=0x1021, computed over **payload bytes only** (not header).

**Exception — Transport ACK**: 8-byte header-only packet (no payload, no CRC). Service ID always 0x80-02 (AuthACK).

### Service ID Routing Table

All 39 known service IDs, grouped by function:

**Authentication (0x80-xx)** — bidirectional, on 5401/5402:
| Service | Direction | Purpose |
|---|---|---|
| 0x80-20 AuthData | TX | Heartbeat, auth handshake packets |
| 0x80-00 AuthControl | RX | Heartbeat echo, auth echoes |
| 0x80-01 AuthResponse | RX | Auth success (type=4), keepalive (type=6, ~10s interval) |
| 0x80-02 AuthACK | RX | Transport-level ACK (8-byte, no CRC) |

**Teleprompter (0x06-xx)** — bidirectional:
| Service | Direction | Purpose |
|---|---|---|
| 0x06-20 Teleprompter | TX | 16 command types: INIT(1), SCRIPT_LIST(2), CONTENT_PAGE(3), CONTENT_COMPLETE(4), PAUSE(5), RESUME(6), EXIT(7), SPEED(8), HEARTBEAT(9), AI_SYNC(10), PLAYING(11), PREVIOUS(12), NEXT(13), FONT_SIZE(14), MIRROR(15), RESET(16), MARKER(255) |
| 0x06-00 TeleprompterResp | RX | Command ACK (f1=0xA6) |
| 0x06-01 TeleprompterProgress | RX | Scroll ticks (f1=0xA4), completion (f1=0xA1) |

**EvenAI / Dashboard / EvenHub (0x07-xx)** — bidirectional:
| Service | Direction | Purpose |
|---|---|---|
| 0x07-20 EvenAI | TX | CTRL(1), ASK(3), REPLY(5), SKILL(6), HEARTBEAT(9), CONFIG, types 11-20 |
| 0x07-00 EvenAIResponse | RX | Echo, COMM_RSP (f12.f1=7 AI, f12.f1=8 Hub). **Types 11-19 ALL respond** with COMM_RSP f12={f1=8} (~90-170ms). Type 20 (Translate) responds with mixed codes (f12.f1=7 from one eye, f12.f1=8 from the other) |
| 0x07-01 EvenAIStatus | RX | Mode enter (f3.f1=2), exit (f3.f1=3). Only EXIT generates status on 0x07-01 |

**EvenAI echo response field mapping** — Each command type echoes on protobuf field `(type + 2)`, with f12 reserved for COMM_RSP:

| Type | Name | Echo Field | Echo Content | Then COMM_RSP |
|---|---|---|---|---|
| 1 | CTRL | f3 | Exact payload echo | f12.f1=7 |
| 3 | ASK | f5 | Empty bytes | f12.f1=7 |
| 4 | ANALYSE | f6 | Empty bytes | f12.f1=7 |
| 5 | REPLY | f7 | Empty bytes | f12.f1=7 |
| 6 | SKILL | f8 | Empty bytes | f12.f1=7 |
| 7 | PROMPT | f9 | Empty bytes | f12.f1=7 |
| 8 | EVENT | f10 | Empty bytes | f12.f1=7 |
| 9 | HEARTBEAT | f11 | `{f2=8}` (session state) | f12.f1=7 |
| 10 | (unnamed) | f13 | Empty bytes (skips f12) | f12.f1=7 |
| 11-19 | Hub types | — | No echo; direct COMM_RSP | f12.f1=8 |
| 20 | TRANSLATE | — | No echo; direct COMM_RSP | f12.f1=7 or 8 (per-eye asymmetric) |
| 161 | COMM_RSP (as cmd) | — | No echo; direct COMM_RSP | f12.f1=8 |

Pattern: `echo_field = type + 2`, except type 10 → f13 (f12 reserved for COMM_RSP payload). Types 1-10 generate two responses (echo + COMM_RSP). Types 11+ generate only COMM_RSP. Responses on 0x07-00 arrive ~50-90ms after TX; COMM_RSP arrives ~80-170ms after echo.

**COMM_RSP is bidirectional** (testAll-3 discovery): Phone-initiated COMM_RSP (type=0xA1 TX on 0x07-20) is accepted by firmware and triggers a completion burst: first `evenAICompletion(type=8)` (EvenHub), then `evenAICompletion(type=7)` (EvenAI). This suggests COMM_RSP serves a bidirectional session-cleanup role — the phone can force-close an active EvenAI/Hub session by sending the same completion marker the glasses normally originate.

**Types 4/7/8 route through EvenHub container dispatcher** (testAll-3 discovery): When sent as bare probes (no payload), the echo responses for ANALYSE(4), PROMPT(7), and EVENT(8) contain EvenHub result codes from the container subsystem:
- Type 4 ANALYSE echo → `APP_REQUEST_UPGRADE_IMAGE_RAW_DATA_SUCCESS` (image container result)
- Type 7 PROMPT echo → `APP_REQUEST_REBUILD_PAGE_FAILD` (page rebuild failure)
- Type 8 EVENT echo → `APP_REQUEST_UPGRADE_TEXT_DATA_SUCCESS` (text container result)

This reveals that types 4, 7, 8 route through the **same EvenHub container dispatcher** that handles display commands, not through a separate AI command handler. The firmware's EvenAI service is actually a unified command router where types 1-3/5-6/9 go to the AI subsystem and types 4/7-8/11-19 go to the EvenHub display subsystem.

**Navigation (0x08-xx)** — TX-only (confirmed write-only):
| Service | Direction | Purpose |
|---|---|---|
| 0x08-20 Navigation | TX | Turn-by-turn directions (10 sub-commands, 36 icon types) |
| 0x08-00 NavigationResp | RX | Not observed in captures |

**Device Info (0x09-xx)** — bidirectional:
| Service | Direction | Purpose |
|---|---|---|
| 0x09-00 DeviceInfo | TX | Query device info |
| 0x09-01 DeviceInfoResp | RX | Async response; also **proactive** after long press AND periodically (~15s interval, testAll-3). f2=glasses counter (incrementing), f4 nested: f1=1, f2=variable, f3=session-variable, f4=1, f5/f6=FW/HW version strings, f7=1, f8=30, f12=dynamic, f18=1 |

**Device info f4.f2 interpretation** — **CONTRADICTED across documents**: `magic-numbers.md` records f4.f2=25 as "battery level percentage" (observed in testAll-2, stable). `unidentified-behaviors.md` records f4.f2 values of 60→60→45→70 over 47s (rapidly fluctuating, consistent with RSSI). The rapid variation rules out battery level. **Best interpretation: f4.f2 = |RSSI| in dBm** (unsigned absolute BLE signal strength). The f4.f2=25 observation likely reflects a -25 dBm reading at very close range (phone touching glasses). Confirmation requires correlating f4.f2 with iOS CoreBluetooth RSSI readings in the same time window.

**Configuration / Settings (0x0D-xx)** — bidirectional:
| Service | Direction | Purpose |
|---|---|---|
| 0x0D-00 ConfigResponse | TX/RX | Brightness, settings queries/responses |
| 0x0D-20 ConfigCommand | TX | Configuration commands |
| 0x0D-01 GestureLongPress | RX | Long-press gesture OR display mode notification (disambiguated by f3 presence) |

**G2 Settings command enum** (`g2_settingCommandId`, 22 commands):
| Command | Direction | Purpose |
|---|---|---|
| `APP_REQUIRE_BASIC_SETTING` | TX | Request current settings |
| `APP_REQUIRE_BRIGHTNESS_INFO` | TX | Request brightness info |
| `APP_SEND_BASIC_INFO` | TX | Send basic settings |
| `APP_SEND_HEARTBEAT_CMD` | TX | Settings heartbeat |
| `APP_SEND_MENU_INFO` | TX | Send menu configuration |
| `APP_SEND_MAX_MAP_FILE` | TX | Send overview map file |
| `APP_SNED_MINI_MAP_FILE` | TX | Send mini map file (typo "SNED" in original) |
| `APP_SET_DASHBOARD_AUTO_CLOSE_VALUE` | TX | Set dashboard auto-close timer |
| `APP_INQUIRE_DASHBOARD_AUTO_CLOSE_VALUE` | TX | Query dashboard auto-close timer |
| `APP_SEND_ERROR_INFO_MSG` | TX | Send error information |
| `SET_DEVICE_INFO` / `GET_DEVICE_INFO` | TX | Device info CRUD |
| `DEVICE_BRIGHTNESS` | RX | Brightness acknowledgment |
| `DEVICE_DISPLAY_MODE` | TX/RX | Display mode (dual/full/minimal) |
| `DEVICE_WORK_MODE` | TX/RX | Work mode setting |
| `DEVICE_ANTI_SHAKE_ENABLE` | TX | Anti-shake toggle |
| `DEVICE_WAKEUP_ANGLE` | TX | Wake-up tilt angle |
| `DEVICE_BLE_MAC` | RX | Device BLE MAC address |
| `DEVICE_GLASSES_SN` / `DEVICE_DEVICE_SN` | RX | Serial numbers |
| `DEVICE_SEND_LOGGER_DATA` | RX | Logger data from glasses |
| `DEVICE_RESPOND_SUCCESS` / `DEVICE_RESPOND_PARAMETER_ERROR` | RX | Response codes |

**g2_settingCommandId numeric mapping** (from mock firmware config.h + testAll-3 sweep):

| ID | Name | Payload | Tested | RX Response |
|---|---|---|---|---|
| 0 | APP_REQUIRE_BASIC | `0800` | Yes | None |
| 1 | APP_REQUIRE_BRIGHT | `0801` | Yes | None |
| 2 | APP_SEND_BASIC | `0802` | Yes | None |
| 3 | APP_HEARTBEAT | `0803` | Yes | None |
| 4 | APP_MENU_INFO | `0804` | Yes | None |
| 7 | DASH_AUTO_CLOSE_SET | — | No | — |
| 8 | DASH_AUTO_CLOSE_GET | `0808` | Yes | None |
| 9 | (unnamed) | `0809` | Yes | None |
| 10 | SET_DEVICE_INFO | — | No | — |
| 11 | GET_DEVICE_INFO | `080b` | Yes | None |
| 12 | DEVICE_BRIGHTNESS | — | No | — |
| 13 | DEVICE_DISPLAY_MODE | `080d` | Yes | None |
| 14 | DEVICE_WORK_MODE | `080e` | Yes | None |
| 15 | DEVICE_ANTI_SHAKE | `080f` | Yes | None |
| 16 | DEVICE_WAKEUP_ANGLE | `0810` | Yes | None |
| 17 | DEVICE_BLE_MAC | `0811` | Yes | None |
| 18 | DEVICE_GLASSES_SN | `0812` | Yes | None |
| 19 | DEVICE_DEVICE_SN | `0813` | Yes | None |
| 20 | DEVICE_SEND_LOGGER | — | No | — |
| 21 | DEVICE_RESPOND_SUCCESS | — | No | — |
| 22 | DEVICE_RESPOND_PARAM_ERR | — | No | — |
| 23-40 | Extended range | `0817`–`0828` | Yes (sweep) | None |

**testAll-3 sweep result**: IDs 0-4, 8-9, 11, 13-19, 23-40 all tested on 0x0D-00. **Zero genuine RX responses** for any ID — confirmed completely write-only. IDs 5-6 (map files) and 7 (dashboard auto-close set) untested. Extended range IDs 23-40 are beyond the documented enum (22 values) and produced no errors or responses, suggesting the firmware silently ignores unknown IDs.

**Clarification on "8 responding cmdIds"**: The testAll-3 sweep reported cmdIds 24, 27, 28, 33, 34, 38 as "responding" during the 23-40 scan. Analysis shows these are **background events** (heartbeat echoes from the glasses' ~10s keepalive loop, auth keepalive on 0x80-01) that happened to arrive within the probe's response window, NOT genuine responses to the settings cmdIds. Evidence: (1) heartbeatEcho and auth(80-01) are autonomous periodic events documented elsewhere, (2) the same cmdIds that "responded" on the first pass did not consistently respond on the second pass (cmdId 27 responded once with auth, then was silent on retry), (3) no response arrived on the settings service 0x0D-00 itself — all "responses" were on unrelated services. Conclusion: all tested settings cmdIds are genuinely write-only.

**Raw brightness format**: Also sent on 0x0D-00 as `[0x01, level(0-42), auto(0/1)]` — 3-byte non-protobuf payload coexisting with protobuf `G2SettingPackage` on the same service.

**Brightness scale note**: The UI representation uses **0-100%** (confirmed by localization keys `brightness_set_to_80`, `brightness_set_to_2`, `brightness_set_to_1` in app strings). Whether the internal `DeviceReceive_Brightness` protobuf uses 0-42 (hardware DAC steps) or 0-100 (percentage mapped internally) remains unknown — our G1-derived 0-42 range does not produce visible results on G2 hardware.

**Conversate / ASR (0x0B-xx, 0x11-xx)** — bidirectional:
| Service | Direction | Purpose |
|---|---|---|
| 0x0B-20 Conversate | TX | Init sequence, transcript updates |
| 0x0B-00 ConversateResp | RX | Command ACK (f1=0xA2) |
| 0x0B-01 ConversateNotify | RX | Auto-close after ~60s (f1=0xA1, f8.f1=2) |
| 0x11-20 ConversateAlt | TX | Alternative format (i-soxi field 7) |

**Display (0x04-xx, 0x0E-xx, 0x81-xx)**:
| Service | Direction | Purpose |
|---|---|---|
| 0x04-20 DisplayWake | TX | Wake display |
| 0x04-00 DisplayWakeResp | RX | ACK: `08011a00` (f1=1, f3=empty). **Variant**: 2/28 responses include f2 (glasses counter): `080110xx1a00` |
| 0x04-01 NotifyResponse | RX | Post-file-transfer device info |
| 0x0E-20 DisplayConfig | TX | 6 regions with IEEE 754 floats (write-only) |
| 0xE0-00 EvenHubResponse | RX | EvenHub completion. Also **proactive unsolicited** heartbeat every ~0.5-1s (testAll-3: glasses send without preceding TX) |
| 0x81-20 DisplayTrigger | TX | Display trigger (f1=1) |
| 0x81-00 DisplayTriggerResp | RX | ACK: f1=1, f2=counter, f3={f1=67}. Value 67 (0x43) is constant across probes — likely a fixed display state/capability indicator rather than live brightness reading (brightness range is 0-42 or 0-100). May be ASCII 'C' (status code) or a JBD display controller state register value |

**Notification (0x02-xx)** — TX-only:
| Service | Direction | Purpose |
|---|---|---|
| 0x02-20 Notifications | TX | Metadata-only proto (app_id + count); text delivered via file transfer (0xC4/0xC5). JSON key: `android_notification`. **File transfer alone is sufficient** for notification display (confirmed testAll-3, no 0x02-20 sent, notification rendered). The metadata proto is optional or provides unknown additional capability (e.g., pre-allocating display space) |

**Gesture (0x01-xx)** — RX-only:
| Service | Direction | Purpose |
|---|---|---|
| 0x01-01 GestureStatus | RX | Tap/swipe events (protobuf pattern `12 04 08 01`=fwd, `12 04 08 02`=back). Gestures are **customizable** via `gesture_customization` settings page. Known gesture types: single_tap, double_tap, long_press, swipe, **five_tap**. Configured via `setGestureControlList` → `gestureControlList` |

**File Transfer (0xC4-xx, 0xC5-xx)** — bidirectional, on 7401/7402:
| Service | Direction | Purpose |
|---|---|---|
| 0xC4-00 FileCommand | TX/RX | `SEND_START`, `SEND_DATA`, `SEND_RESULT_CHECK`, `EXPORT_START`, `EXPORT_DATA`, `EXPORT_RESULT_CHECK` |
| 0xC5-00 FileData | TX/RX | File data chunks (2-byte LE status ACK). Image data: Gray4 4-bit BMP (`_encodeBmp4bit`, `compressBmpData`) |

**File transfer error codes** (8):
| Code | Constant | Meaning |
|---|---|---|
| 0 | `EVEN_FILE_SERVICE_RSP_SUCCESS` | Success |
| 1 | `EVEN_FILE_SERVICE_RSP_FAIL` | Generic failure |
| 2 | `EVEN_FILE_SERVICE_RSP_DATA_CRC_ERR` | CRC error |
| 3 | `EVEN_FILE_SERVICE_RSP_FLASH_WRITE_ERR` | Flash write error |
| 4 | `EVEN_FILE_SERVICE_RSP_NO_RESOURCES` | No resources |
| 5 | `EVEN_FILE_SERVICE_RSP_RESULT_CHECK_FAIL` | Result check failed |
| 6 | `EVEN_FILE_SERVICE_RSP_START_ERR` | Start error |
| 7 | `EVEN_FILE_SERVICE_RSP_TIMEOUT` | Timeout |

**Session / Controller / Tasks**:
| Service | Direction | Purpose |
|---|---|---|
| 0x0A-20 SessionInitTrigger | TX | Session init (speculative, no response observed) |
| 0x10-20 Controller | TX | Controller command |
| 0x10-00 ControllerResp | RX | Delayed ACK: `08011a00` |
| 0x0C-20 Tasks | TX | Tasks command |
| 0x0C-00 TasksResp | RX | Delayed ACK: `08011a00` |
| 0x20-20 Commit | TX | Commit/transaction |
| 0x20-00 CommitResp | RX | Not observed |

### Teleprompter Protocol Detail (0x06-20)

**Type → protobuf field mapping** (each command type maps to a specific protobuf field in the outer message):

| Type | Command | Protobuf Field | Tag |
|---|---|---|---|
| 1 | INIT | field 3 (LD) | 0x1A |
| 2 | SCRIPT_LIST | field 4 (LD) | 0x22 |
| 3 | CONTENT_PAGE | field 5 (LD) | 0x2A |
| 4 | CONTENT_COMPLETE | field 6 (LD) | 0x32 |
| 255 | MARKER | field 13 (LD) | 0x6A |

All types share field 1 = type varint and field 2 = msg_id varint in the outer message.

**TeleprompterScript** (type=2 SCRIPT_LIST sub-message):
```
TeleprompterScript {
  string script_id = 1;    // e.g. "teleprompter_createdId_1766814694346" (timestamp-based)
  string title = 2;        // "Teleprompt Title"
}
```

**Content height scaling formula**: `content_height = (lines * 2665) / 140`. The ratio 2665/140 is confirmed by glasses echo field3=140.

**Scroll start mechanism**: Re-send INIT (type=1) with `state = { f1 = 4 }` to explicitly trigger scroll start. Alternatively, CONTENT_COMPLETE (type=4) triggers automatic scroll.

**Init display settings** (type=1, field 3 sub-message):
| Field | Value | Purpose |
|---|---|---|
| 1 | 1 | Init type |
| 3 | 0 | Unknown |
| 4 | 267 | Display width (constant) |
| 5 | (computed) | Content height |
| 6 | 230 | Line height |
| 7 | 1294 | Viewport height |
| 8 | 5 | Font size |
| 9 | 0 or 1 | Scroll mode (0=manual, 1=auto) |

**Batch send choreography**: pages 0–9, marker (type=255, hex `6A 04 08 00 10 06`), pages 10–11, sync trailer (`6A 00`), pages 12+.

**Scroll timing** (from mock firmware): first tick ~480ms after finalize, then ~1500ms interval, 6 total ticks. Completion signal: f1=0xA1, f7={f1=4} (scroll-complete COMM_RSP on 0x06-01). **Note**: teleprompter completion uses **f7** for the completion subtype, unlike EvenAI which uses **f12** — each service has its own COMM_RSP field number.

### Notification Protocol Detail (0x02-20)

**NotificationMessage** proto:
```
NotificationMessage {
  uint32 type = 1;         // 1 (send notification)
  uint32 msg_id = 2;       // Generated: 10000 + (unix_timestamp % 10000)
  NotificationData data = 3;
}

NotificationData {
  string app_bundle_id = 1;  // e.g. "com.google.android.gm"
  string app_name = 2;       // e.g. "Gmail"
  uint32 action = 3;         // 0 = show notification
  uint32 timestamp = 4;
}
```

Text content is delivered via file transfer (0xC4/0xC5), not in the protobuf message. File path: `user/notify_whitelist.json`. JSON key is `android_notification` even on iOS (firmware expects this key).

**Pre-loaded notification whitelist apps** (8 major apps):
- `com.facebook.orca` (Messenger), `com.whatsapp` (WhatsApp), `com.instagram.android` (Instagram)
- `com.twitter.android` (Twitter/X), `com.facebook.katana` (Facebook), `com.google.android.gm` (Gmail)
- `com.tencent.mm` (WeChat), `com.apple.MobileSMS` (Messages)

**NotifyResponse** on 0x04-01 (async, arrives after file transfer):
```
NotifyResponse {
  uint32 type = 1;              // 2
  uint32 msg_id = 2;
  NotificationAppInfo info = 4; // field 4, length-delimited
}

NotificationAppInfo {
  string app_bundle_id = 1;     // null-terminated (C-style firmware strings)
  string app_display_name = 2;  // null-terminated
}
```

---

## 10. Authentication Protocol

### 7-Packet Handshake Sequence

```
Phone                                    Glasses (both eyes)
  │                                           │
  │  1. Auth capability (0x80-20)             │
  │  ──────────────────────────────────────▶  │
  │                                           │ Glasses respond within ~51ms
  │  2. Auth echo (0x80-00)                   │
  │  ◀──────────────────────────────────────  │ f3=[] or f4=[] (emptied nested)
  │                                           │
  │  3. Time sync (0x80-20)                   │
  │  ──────────────────────────────────────▶  │ f128={f1=UnixTimestamp, f3=TZOffset}
  │                                           │
  │  4. Auth echo (0x80-00)                   │
  │  ◀──────────────────────────────────────  │
  │                                           │
  │  5. Auth success (0x80-01)                │
  │  ◀──────────────────────────────────────  │ f1=4, f2=msgId, f3={f1=1}=success
  │                                           │
  │  6. Auth confirm (0x80-20)                │
  │  ──────────────────────────────────────▶  │ f4={f1=1}
  │                                           │
  │  7. Auth echo (0x80-00)                   │
  │  ◀──────────────────────────────────────  │
  │                                           │
  │  ═══ Session established ═══              │
  │                                           │
  │  Heartbeat (type=0x0E) every 3.0s         │ Precisely 3.000-3.040s interval
  │  ──────────────────────────────────────▶  │ Sent to both eyes, 6-16ms apart
  │  ◀──────────────────────────────────────  │ Echo on 0x80-00
  │                                           │
  │  Auth keepalive (type=6) every 9.78s      │ Range: 9.717-10.149s (glasses-initiated)
  │  ◀──────────────────────────────────────  │ On 0x80-01, f5=empty (tag 0x2A)
```

**Critical safety note**: Only heartbeat type `0x0E` is safe. Type `0x0D` triggers gesture subsystem; type `0x0F` causes BLE disconnect + pairing removal.

**No BLE-level pairing**: The G2 uses application-level auth only. No PIN, no secure pairing, no bonding. Session is established via the protobuf handshake above.

---

## 11. Display & Sensor Subsystem

### Display Canvas

| Property | Value | Source |
|---|---|---|
| **Resolution** | 576 x 288 pixels | Even.app rendering constants |
| **Color depth** | 4-bit greyscale (16 shades) | BMP analysis |
| **Max write size** | 204 bytes per display write (0x6401) | Protocol constraints |
| **Max containers** | 4 per page | Even.app container system |
| **Display modes** | `display_mode_dual`, `display_mode_full`, `display_mode_minimal` | Even.app settings |

### Display Sensor Stream (0x6402)

The display characteristic 0x6402 delivers a **sensor telemetry stream from the JBD micro-LED display controller ASIC**:
- **Frame size**: 205 bytes (consistent)
- **Rate**: ~20 Hz sustained (~50ms interval) when display active, drops to ~16 Hz average due to display-off gaps
- **Format**: JBD-proprietary LFSR-scrambled sensor data (NOT AES, NOT software encryption)
- **Content**: IMU/temperature/LED current sensor telemetry read via SPI (SPIM2) from display controller
- **Purpose**: Head tracking, display health monitoring, wear detection feedback

**Frame internal structure** (205 bytes = 5 × 40 + 5):

```
┌──────────────────────────────────────────────────────────────┐
│ [36 scrambled sensor bytes] [4 cleartext status registers]   │  Block 0
│ [36 scrambled sensor bytes] [4 cleartext status registers]   │  Block 1
│ [36 scrambled sensor bytes] [4 cleartext status registers]   │  Block 2
│ [36 scrambled sensor bytes] [4 cleartext status registers]   │  Block 3
│ [36 scrambled sensor bytes] [4 cleartext status registers]   │  Block 4
│ [5-byte trailer]                                             │  Trailer
└──────────────────────────────────────────────────────────────┘
```

Each frame contains 5 sensor data blocks at ~100 Hz effective rate (5 blocks × 20 Hz frame rate), consistent with IMU sampling requirements for head tracking.

**36-byte scrambled blocks** — LFSR-scrambled sensor telemetry:
- Entropy: 7.996 bits/byte overall (near-random), but **position-dependent gradient**: positions 1-24 near-random (~7.97), position 0 drops to 6.99, positions 31-33 drop to 7.04-7.53
- 99.95% of blocks are unique (content changes every frame even with static display + motionless head)
- XOR of consecutive frames produces random output → rules out simple fixed-key XOR
- Autocorrelation: lag 1 r=0.0001 (none), lag 16 r=-0.024 (weak but detectable)
- 36-byte block size rules out AES (16-byte) and DES (8-byte) block ciphers
- Likely contains: accelerometer/gyroscope (6/7-axis IMU), die temperature, LED drive current, possibly ALS

**4-byte cleartext status registers** (read directly from display controller SPI bus):

| Byte | Entropy | Parity | Purpose |
|---|---|---|---|
| 0 | 4.05 | 95.9% odd | Status/address register. Top values: 0x03, 0x23, 0x83, 0x07 |
| 1 | 3.73 | **100% odd** | Ready/valid flag (bit 0 always set). Top values: 0x85, 0x81, 0x19, 0x1D |
| 2 | 3.96 | **100% even** | Head tilt measurement (bit 0 always clear). **r=0.73 correlation with trailer head angle**. Value ~60 at 0°, ~88 at 66°, ~89 at 90° |
| 3 | 2.76 | **100% odd** | Status register with fixed flags. Dominant value 0x9F (159), bits 5-6 nearly always clear (99.5%) |

The SPI read pattern is: `[read 36 bytes scrambled data] [read 4 bytes status registers]` × 5.

**Scrambling mechanism** — JBD-proprietary LFSR scrambler:
- Implemented **in the display controller silicon**, not by SoC firmware
- The Apollo510b reads raw MSPI data from the JBD display IC and forwards unchanged over BLE
- Polynomial is similar to but distinct from MIPI DSI standard LFSR (`x^16 + x^14 + x^13 + x^11 + 1`)
- Testing with MIPI DSI LFSR partially reduces entropy (6.92 → 5.11 bits/byte) — related but different polynomial
- LFSR appears re-seeded per block or per frame (possibly using frame counter or timing signal)
- Standard practice in display ICs for: **EMI reduction** (spectral flattening), **IP protection** (hiding sensor calibration), **signal integrity** (balanced 0/1 bit ratio on SPI bus)
- Decrypting requires: JBD display IC datasheet (NDA-restricted) or reverse-engineering the LFSR polynomial

**Trailer structure** (last 5 bytes, confirmed from 1,303-frame analysis):

```
Offset 200: [activity]     Variable byte (0x00-0x35), distribution peaks at 0x11-0x15 — display content/activity indicator
Offset 201: [0x00]         Always zero — padding/separator
Offset 202: [angle_lo]     Signed int16 LE low byte
Offset 203: [angle_hi]     Signed int16 LE high byte
Offset 204: [counter]      Monotonic frame counter (wraps at 0xFF)
```

**Head angle**: Signed int16 LE at bytes 202-203, range **-90 to +90**. 15 discrete values observed: 0x0000(0°), 0xF8FF(-8°), 0x0800(+8°), 0x1100(+17°), 0x1B00(+27°), 0x2500(+37°), 0x3100(+49°), 0xEFFF(-17°), 0xE5FF(-27°), 0xA6FF(-90°), 0x5A00(+90°), etc. Mean angle +7.7° in test session (wearer looking slightly upward).

**Display-off gaps**: Three gaps >200ms observed in 80s session:
- 10.9s gap (display off between teleprompter sessions)
- 4.5s gap (display off between conversate and EvenHub)
- 315ms gap (brief display transition)

**Scrambling statistics** (1,303 frames analyzed):

| Test | Result | Implication |
|---|---|---|
| Chi-squared (36-byte blocks) | χ²=1219 (fails uniformity, p≈0) | NOT random — structural bias leaks through LFSR |
| Position 0 entropy | 6.99 bits/byte (vs 7.97 center) | Block header/type byte partially visible |
| Positions 31-33 entropy | 7.04-7.53 bits/byte | Block trailer structure leaks through |
| Block uniqueness | 99.95% unique | Content changes continuously (live sensor data) |
| Consecutive-frame XOR | Random output | Rules out fixed-key XOR cipher |
| MIPI DSI LFSR test | Partial match (6.92→5.11 bits/byte) | Related polynomial but JBD-proprietary variant |

### Display Wake Protocol (0x04-20)

```
DisplayWake {
  uint32 type = 1;              // always 1
  uint32 msg_id = 2;
  DisplayWakeSettings settings = 3;
}

DisplayWakeSettings {
  uint32 field1 = 1;            // 1 (enable flag)
  uint32 field2 = 2;            // 1 (enable flag)
  uint32 field3 = 3;            // 5 (timeout/duration?)
  uint32 field5 = 5;            // 1 (field 4 absent)
}
```

Response on 0x04-00: `f1=1, f2=brightness_level, f3=empty` (~11ms latency). Also triggers COMM_RSP `f1=161, f5={f1=brightness, f2=8}`.

### Display Configuration (0x0E-20)

Display config is sent before rendering any content (teleprompter, EvenHub, conversate, navigation):

```
DisplayConfig {
  uint32 type = 1;              // always 2
  uint32 msg_id = 2;
  DisplaySettings settings = 4; // field 4, length-delimited
}

DisplaySettings {
  uint32 enabled = 1;
  repeated DisplayRegion regions = 2;
  uint32 field3 = 3;
}

DisplayRegion {
  uint32 region_id = 1;         // 2, 3, 4, 5, 6
  uint32 param1 = 2;            // 0 or 13 (region 3 only)
  float param2 = 3;             // IEEE 754 geometry
  float param3 = 4;             // IEEE 754 geometry
  uint32 param4 = 5;            // 0
  uint32 param5 = 6;            // 0
}
```

- `G2DisplayConfigRegion` struct: id, value, x, f2
- Typical config: id=2 (main area), id=3 (font, param1=13), id=4-6 (layout regions)
- **Required before rendering** — without displayConfig, glasses ACK content but never draw
- Write-only (no response from glasses)

### Display Modes (from 0x0D-01 config state notifications)

| Mode Value | State | Trigger |
|---|---|---|
| 0 | Idle | Default / after close |
| 6 | Render | Active display rendering |
| 11 | Conversate | ASR/conversate active |
| 16 | Teleprompter | Teleprompter active |

**Sub-mode field (f3.f2)**: During EvenAI overlay on RENDER mode, f3={f1=6, f2=7} observed — f2=7 indicates an AI overlay sub-mode within the render state.

**Config mode f3.f1 = service high byte pattern** (confirmed): The mode values in 0x0D-01 notifications map directly to the service ID high byte of the active feature: RENDER=6 (0x06 teleprompter), CONVERSATE=11 (0x0B=11 decimal), TELEPROMPTER=16 (0x10=16 decimal). The sub-mode f3.f2=7 during AI overlay corresponds to 0x07 (EvenAI service). EvenHub (0xE0) also reports mode=6 (Render). This means the firmware's config state system uses the service ID routing byte as its internal mode identifier — there is a 1:1 mapping between display mode and active BLE service.

Config close always sends **2 packets**: render mode reset + empty reset via `config_state_close()`.

**Proactive 0xE0-00 (EvenHubResponse)**: testAll-3 reveals the glasses send **unsolicited** 0xE0-00 packets every ~0.5-1s even without preceding TX. These arrive before any EvenHub TX is sent, indicating an autonomous EvenHub heartbeat/status monitor running on the firmware. Format: f1=type(4), f2=counter(incrementing), f3=state payload.

**Interpretation caution**: Some proactive 0xE0-00 packets observed during EvenAI probes (testAll-3 Dashboard HB probe) may be **probe artifacts** — the glasses' EvenHub state machine firing in response to unexpected type values — rather than a true autonomous heartbeat. The Dashboard HB probe on 0x07-20 with a dashboard type triggered `APP_REQUEST_UPGRADE_TEXT_DATA_FAILED` + `evenAICompletion(type=7)`, which are error codes from the container dispatcher, not a periodic heartbeat. The autonomous heartbeat at ~0.5-1s intervals IS genuine (observed during idle periods without any TX), but individual 0xE0-00 packets during active probing may be confused error responses.

### EvenHub Container System

EvenHub renders content via a container-based layout engine on service **0xE0-20** (dedicated handler `evenhub_common_data_handler`). Responses arrive on 0xE0-00. EvenHub does NOT share with teleprompter (0x06-20) or displayConfig (0x0E-20) — those are separate services. All protobuf encoding/BLE communication happens in the host app (Flutter), not in the WebView.

**Lifecycle state machine**:
```
idle → created → rebuilt → active → shutdown → idle
        │                      ▲
        └── textUpgrade/imageUpdate ──┘
```

- `createStartUpPageContainer` — MUST be called exactly once first (subsequent calls have no effect)
- `rebuildPageContainer` — for all page changes after initial creation (unlimited calls)
- `textContainerUpgrade` / `updateImageRawData` — only valid after create/rebuild
- `shutDownPageContainer` — returns to idle
- `audioControl` — prerequisite: `createStartUpPageContainer` must succeed first

**Operation timing** (post-send delays):

| Operation | Delay | Notes |
|---|---|---|
| CreateStartUpPage | 500 ms | Initial page setup |
| RebuildPage | 300 ms | Page replacement |
| TextUpgrade | 200 ms | Text content update |
| ImageUpdate | 300 ms | Image raw data |
| Shutdown | 200 ms | Page teardown |
| Fragment spacing | 20 ms | Between image fragments |
| Display wake | 50 ms | Pause after 0x04-20 |
| Scroll cooldown | 300 ms | Between duplicate scroll events |

**Container protobuf field mappings** (corrected via nanopb struct offset analysis, 2026-03-09):

> **Previous error**: Field numbers below were originally inferred from the TypeScript SDK's
> JSON property declaration order (`index.d.ts`). This was wrong — nanopb uses compile-time
> generated descriptors where fields are ordered by field number in the C struct. The SDK's
> "field overloading" (same field number, different wire types) is impossible with nanopb,
> which maps each field number to exactly one struct slot. The corrected mappings below are
> derived from firmware struct sizes and byte offsets in the decompiled `evenhub_data_parser.c`.

`CreateStartUpPageContainer` / `RebuildPageContainer` (outer message, struct size 0x2654):
| Field # | Wire | Name | Type |
|---|---|---|---|
| 4 | varint | containerTotalNum | int (max 4) |
| 5 | LD (repeated) | List_Object | ListContainerProperty |
| 6 | LD (repeated) | Text_Object | TextContainerProperty |
| 7 | LD (repeated) | Image_Object | ImageContainerProperty |

> Fields 1-3 are the command header (cmd_type, msg_id, sub_type).

`ListContainerProperty` (struct size 0x54C = 1356 bytes):
| Field # | Wire | Name | Offset | Range |
|---|---|---|---|---|
| 1 | varint | X_Position | 0 | 0–576 |
| 2 | varint | Y_Position | 4 | 0–288 |
| 3 | varint | Width | 8 | 0–576 |
| 4 | varint | Height | 12 | 0–288 |
| 5 | varint | Border_Width | 16 | 0–5 |
| 6 | varint | Border_Color | 20 | 0–15 |
| 7 | varint | Border_Rdaius | 24 | 0–10 |
| 8 | varint | Padding_Length | 28 | 0–32 |
| 9 | varint | Container_ID | 32 | random int |
| 10 | LD | Container_Name | 36 | max 16 chars |
| 11 | LD | Item_Container | 52 | sub-message |
| 12 | varint | Is_event_capture | 1348 | 0 or 1 |

`ListItemContainerProperty` (sub-message of field 11):
| Field # | Wire | Name | Range |
|---|---|---|---|
| 1 | varint | Item_Count | 1–20 |
| 2 | varint | Item_Width | 0=auto, >0=fixed |
| 3 | varint | Is_Item_Select_Border_En | 0 or 1 |
| 4 | LD (repeated) | Item_Name | max 20 items, 64 chars each |

`TextContainerProperty` (struct size 0x420 = 1056 bytes):
| Field # | Wire | Name | Offset | Range |
|---|---|---|---|---|
| 1 | varint | X_Position | 0 | 0–576 |
| 2 | varint | Y_Position | 4 | 0–288 |
| 3 | varint | Width | 8 | 0–576 |
| 4 | varint | Height | 12 | 0–288 |
| 5 | varint | Border_Width | 16 | 0–5 |
| 6 | varint | Border_Color | 20 | 0–16 |
| 7 | varint | Border_Rdaius | 24 | 0–10 |
| 8 | varint | Padding_Length | 28 | 0–32 |
| 9 | varint | Container_ID | 32 | random int |
| 10 | LD | Container_Name | 36 | max 16 chars |
| 11 | varint | Is_event_capture | 52 | 0 or 1 |
| 12 | LD | Content | 56 | max 1000 chars startup / 2000 upgrade |

`ImageContainerProperty`:
| Field # | Wire | Name | Range |
|---|---|---|---|
| 1 | varint | X_Position | 0–576 |
| 2 | varint | Y_Position | 0–288 |
| 3 | varint | Width | 20–200 |
| 4 | varint | Height | 20–100 |
| 5 | varint | Container_ID | random int |
| 6 | LD | Container_Name | max 16 chars |

`TextContainerUpgrade` (cmd_type=5/REFLASH, **sub_type=9 required**):
| Field # | Wire | Name | Notes |
|---|---|---|---|
| 4 | varint | Container_ID | (f1-f3 = header: cmd, msgId, subType) |
| 5 | LD | Container_Name | max 16 chars |
| 6 | varint | ContentOffset | byte offset into existing content |
| 7 | varint | ContentLength | |
| 8 | LD | Content | max 2000 chars |

> **sub_type=9 is mandatory**: The reflash handler gates text updates on `sub_type == 9`.
> With sub_type=0, the firmware returns error code 9 and discards the content.

`ImageRawDataUpdate`:
| Field # | Wire | Name | Notes |
|---|---|---|---|
| 1 | varint | Container_ID | |
| 2 | LD | Container_Name | |
| 3 | LD | mapRawData | 4-bit grayscale bytes |
| 4 | varint | mapSessionId | Random int (1–0x7FFFFFFF), shared across fragments |
| 5 | varint | mapTotalSize | Total image bytes across all fragments |
| 6 | varint | compressMode | 0 = uncompressed |
| 7 | varint | mapFragmentIndex | 0-based fragment index |
| 8 | varint | mapFragmentPacketSize | Bytes in this fragment |

`ShutDownContaniner` (typo is canonical):
| Field # | Wire | Name | Values |
|---|---|---|---|
| 1 | varint | exitMode | 0=immediate, 1=user prompt foreground layer |
| `[key]` | any | (open-ended) | Index signature `[key: string]: any` — undocumented extras possible |

`AudioControl`:
| Field # | Wire | Name | Values |
|---|---|---|---|
| 1 | varint | isOpen | 0=close, 1=open |

**Container event rule**: Exactly ONE container per page must have `isEventCapture=1`; all others must be 0.

**OS event types** (7, arrive on 0x0E-00):
| Code | Event | Description |
|---|---|---|
| 0 | `CLICK_EVENT` | User tapped container (**CAUTION**: 0 = proto default, unset field is indistinguishable from click) |
| 1 | `SCROLL_TOP` | Scrolled to top |
| 2 | `SCROLL_BOTTOM` | Scrolled to bottom |
| 3 | `DOUBLE_CLICK` | Double-tapped |
| 4 | `FOREGROUND_ENTER` | Container gained focus |
| 5 | `FOREGROUND_EXIT` | Container lost focus |
| 6 | `ABNORMAL_EXIT` | Abnormal exit |

**Image rendering details**:
- **Gray4 encoding**: 4-bit grayscale, 2 pixels/byte (high nibble = left, low nibble = right)
- **Value range**: 0x00 (black) to 0x0F (white); mapping: `gray4 = gray8 >> 4`
- **Bytes per row**: `(width + 1) / 2` (rounded up for odd widths)
- **Tiling behavior**: Images smaller than container are **tiled** (repeated) by hardware; use `padToFit()` to center on black background
- **Fragment max**: 174 bytes (204 − 30 bytes protobuf overhead)
- **Image queue**: Serial execution only — never send concurrently (`G2ImageQueue.shared.enqueue`)
- **Startup limitation**: Image data NOT transmitted during `createStartUpPageContainer` (placeholder only); must call `updateImageRawData` after creation succeeds

**Image result codes** (5):

| Code | Name | Description |
|---|---|---|
| 0 | success | Image updated |
| 1 | imageException | Generic processing error |
| 2 | imageSizeInvalid / imageToGray4Failed | Dimension or conversion failure |
| 3 | sendFailed | BLE transmission failure |

**Page creation result codes** (4):

| Code | Name | Description |
|---|---|---|
| 0 | success | Page created |
| 1 | invalid | Invalid container configuration |
| 2 | oversize | Response container exceeds limits |
| 3 | outOfMemory | Insufficient memory |

**EvenHub error code names** (13, preserving canonical typos):
`APP_REQUEST_CREATE_PAGE_SUCCESS`, `APP_REQUEST_CREATE_INVAILD_CONTAINER`, `APP_REQUEST_CREATE_OVERSIZE_RESPONSE_CONTAINER`, `APP_REQUEST_CREATE_OUTOFMEMORY_CONTAINER`, `APP_REQUEST_UPGRADE_IMAGE_RAW_DATA_SUCCESS`, `APP_REQUEST_UPGRADE_IMAGE_RAW_DATA_FAILED`, `APP_REQUEST_REBUILD_PAGE_SUCCESS`, `APP_REQUEST_REBUILD_PAGE_FAILD`, `APP_REQUEST_UPGRADE_TEXT_DATA_SUCCESS`, `APP_REQUEST_UPGRADE_TEXT_DATA_FAILED`, `APP_REQUEST_UPGRADE_SHUTDOWN_SUCCESS`, `APP_REQUEST_UPGRADE_SHUTDOWN_FAILED`, `APP_REQUEST_UPGRADE_HEARTBEAT_PACKET_SUCCESS`

**Canonical protobuf typos** (must be matched exactly):
- `Border_Rdaius` (not Radius)
- `ShutDownContaniner` (not Container)
- `APP_REQUEST_CREATE_INVAILD_CONTAINER` (not INVALID)
- `APP_REQUEST_REBUILD_PAGE_FAILD` (not FAILED)
- `meun_main_msg_ctx` (not menu)

**Audio streaming lifecycle** (via EvenHub):
1. `createStartUpPageContainer` must succeed first
2. `audioControl(true)` — sends field 1=1 on 0x06-20
3. Frames arrive via `onEvenHubEvent` with `audioPcm: Uint8Array` (40 bytes/frame, 16kHz, 10ms, LE)
4. `audioControl(false)` — sends field 1=0 on 0x06-20
5. Delays: 300ms post-enable, 100ms post-disable

**WebView bridge architecture**:
- Bridge SDK: `@evenrealities/even_hub_sdk` v0.0.7 (npm, obfuscated JS with `.d.ts` types)
- Transport: `flutter_inappwebview` — `callHandler('evenAppMessage', ...)` (Web→App), `window._listenEvenAppMessage(...)` (App→Web push)
- Message types: `CallEvenAppMethod = "call_even_app_method"`, `ListenEvenAppNotify = "listen_even_app_data"`
- Bridge events: `BridgeReady = "evenAppBridgeReady"`, `DeviceStatusChanged`, `EvenHubEvent`
- `DeviceStatus` callback fields: `sn`, `connectType`, `isWearing?`, `batteryLevel?` (0–100), `isCharging?`, `isInCase?`
- Event union includes `imgEvent → ImageReflashEvent` (defined in protocol but NOT yet in SDK v0.0.7 types)

**Device model enum** (from SDK): `G1="g1"`, `G2="g2"`, `Ring1="ring1"` — confirms G1 as a separate product. `DeviceModel.fromString()` defaults to G1 for unrecognized strings.

---

## 12. Firmware Update Paths

### G2 Glasses: Custom OTA Protocol

The G2 uses an **Even-proprietary OTA protocol** (not standard Nordic DFU) for runtime firmware updates:

```
Phone (Even.app)                                    G2 Glasses
  │                                                      │
  │  1. Check update: POST /v2/g/check_firmware          │
  │     ──────────────▶ api2.evenreal.co                 │
  │     ◀────────────── { otaInfo, downloadUri }         │
  │                                                      │
  │  2. Download: GET downloadUri                        │
  │     ──────────────▶ cdn.evenreal.co                  │
  │     ◀────────────── firmware.zip                     │
  │                                                      │
  │  3. OTA_TRANSMIT_START (BLE file service)            │
  │     ─────────────────────────────────────────▶       │
  │  4. OTA_TRANSMIT_INFORMATION                         │
  │     ─────────────────────────────────────────▶       │
  │  5. OTA_TRANSMIT_FILE (chunks via 0xC4/0xC5)         │
  │     ─────────────────────────────────────────▶       │
  │  6. OTA_TRANSMIT_RESULT_CHECK                        │
  │     ─────────────────────────────────────────▶       │
  │     ◀───────────── OTA_RECV_RSP_SUCCESS              │
  │  7. OTA_RECV_RSP_SYS_RESTART                         │
  │     ◀───────────── (glasses reboot)                  │
```

**OTA Header Structure** (`BleG2OtaHeader`):
```
otaMagic1         — Magic byte 1 (validation)
otaMagic2         — Magic byte 2 (validation)
componentNum      — Number of firmware components
componentInfo     — Per-component metadata:
  fileType        — Component type (SD/BL/APP)
  fileLength      — Total file size in bytes
  fileCrc32       — CRC32C checksum (non-reflected MSB-first, poly 0x1EDC6F41)
  fileSign        — Signature blob
  fileId/fileID   — Unique file identifier
```

**Wire transfer tokens**: `fileTransmitCid`, `packetLen`, `packetSerialNum`, `packetTotalNum`, `partsTotal`, `currentPart`, `packetAck`

**OTA response codes** (11 total):

| Code | Constant | Description |
|---|---|---|
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

**OTA prerequisite**: Must be charging AND battery above 50%

### R1 Ring: Standard Nordic DFU + MCUmgr

```
Phone (Even.app)                               R1 Ring
  │                                                │
  │  1. Enter DFU: FE59 Buttonless service         │
  │     ─────────────────────────────────▶         │
  │     (ring resets into bootloader mode)         │
  │                                                │
  │  2. SMP Upload: via DA2E7828-... char          │
  │     ─────────────────────────────────▶         │
  │  3. SMP Test / Confirm                         │
  │     ─────────────────────────────────▶         │
  │  4. SMP Reset                                  │
  │     ─────────────────────────────────▶         │
  │     (ring boots new firmware)                  │
```

MCUmgr upgrade modes: `TEST_ONLY`, `CONFIRM_ONLY`, `TEST_AND_CONFIRM`, `UPLOAD_ONLY`

**MCUmgr extended capabilities** (from `iOSMcuManagerLibrary` analysis):
- **Filesystem access**: `FileSystemManager` — read/write files on ring, CRC32 and SHA-256 file checksums, file status queries. Enables log retrieval and config file management
- **Crash dump retrieval**: `CrashManager` — read core dumps from ring flash. 5 crash test types: `div0` (divide by zero), `jump0` (jump to null), `ref0` (null reference), `assert` (assertion failure), `wdog` (watchdog timeout)
- **Stats and logs**: `StatsManager` (runtime statistics), `LogManager` (log retrieval), `SettingsManager` (ring configuration)
- **Image management**: Dual-image slot support — `bootable`, `pending`, `confirmed`, `active`, `permanent` states. `ImageUploadAlignment` options: DISABLED, TWO_BYTE, FOUR_BYTE, EIGHT_BYTE, SIXTEEN_BYTE
- **Bootloader info**: `BootloaderInfoQuery` — can query MCUboot bootloader version, mode, board ID
- **SUIT envelope**: `McuMgrSuitEnvelope` — Software Updates for IoT (SUIT) manifest format support for secure firmware delivery
- **XIP (Execute-in-Place)**: `version_MCUBOOT+XIP` — suggests the ring may support XIP firmware execution directly from flash, reducing RAM requirements
- **Ring firmware version boundary**: `judgeRingBelow2030001` — firmware v2.03.00.01 is a feature boundary; features or protocols may differ above/below this version

**OTA export** (G2 → phone file extraction):
- `UX_OTA_EXPORT_FILE_CMD_ID` — command to initiate file export from glasses
- `UX_OTA_EXPORT_FILE_RAW_DATA_ID` — raw data stream during export
- `ringOtaInfo` — ring-specific OTA information query
- `subota` — sub-OTA (possibly component-level firmware update)

### Nordic DFU UUID Map (from `even_runner` binary)

**Legacy DFU** (pre-Secure DFU, older Nordic SDK):
| UUID | Role |
|---|---|
| `00001530-1212-EFDE-1523-785FEABCD123` | Legacy DFU Service |
| `00001531-1212-EFDE-1523-785FEABCD123` | Legacy DFU Control Point |
| `00001532-1212-EFDE-1523-785FEABCD123` | Legacy DFU Packet |
| `00001534-1212-EFDE-1523-785FEABCD123` | Legacy DFU Version |

**Secure DFU** (from app bundle — used by G2 failsafe bootloader and R1 Ring):
| UUID | Role |
|---|---|
| `8EC90001-F315-4F60-9FB8-838830DAEA50` | Secure DFU Service |
| `8EC90002-F315-4F60-9FB8-838830DAEA50` | Secure DFU Control Point |
| `8EC90003-F315-4F60-9FB8-838830DAEA50` | Secure DFU Packet |
| `8EC90004-F315-4F60-9FB8-838830DAEA50` | Secure DFU unknown (signing?) |
| `8E400001-F315-4F60-9FB8-838830DAEA50` | Variant service (unknown) |

**Buttonless DFU** (3 variants for entering DFU mode without physical button):
| Variant | Description |
|---|---|
| `buttonlessExperimentalService` + `buttonlessExperimentalCharacteristic` | Experimental (pre-standard) |
| `buttonlessWithoutBonds` | Standard, no BLE bonding required |
| `buttonlessWithBonds` | Standard, preserves BLE bonding across DFU |

The `enableUnsafeExperimentalButtonlessServiceInSecureDfu` flag allows use of the experimental buttonless service for devices that predate the standardized version.

### Bundled Firmware Packages (in Even.app)

| Package | Type | Size | Used For |
|---|---|---|---|
| `B210_ALWAY_BL_DFU_NO.zip` | Bootloader (fail-safe) | 24,180 B | Emergency recovery |
| `B210_BL_DFU_NO_v2.0.3.0004.zip` | Bootloader (versioned) | 24,420 B | Bootloader update |
| `B210_SD_ONLY_NO_v2.0.3.0004.zip` | SoftDevice | 153,140 B | BLE stack update |

Application firmware is **not** bundled in the app — it is downloaded from CDN on demand.

---

## 13. Firmware Filesystem

The glasses firmware exposes an internal filesystem with these known paths:

```
L:/                          (Left eye filesystem root)
├── log/
│   ├── compress_log_0.bin   (Compressed log file 0)
│   ├── compress_log_1.bin
│   ├── compress_log_2.bin
│   ├── compress_log_3.bin
│   ├── compress_log_4.bin
│   └── hardfault.txt        (Crash dump)
└── user/
    └── notify_whitelist.json (Notification app whitelist)

R:/                          (Right eye filesystem root)
├── log/
│   ├── compress_log_0.bin – 4.bin
│   └── hardfault.txt
└── user/
    └── notify_whitelist.json
```

The file service (0xC4/0xC5) can read and write to this filesystem. The `EVEN_FILE_SERVICE_CMD_EXPORT_*` commands can extract files from glasses to phone.

---

## 14. Protobuf Module Inventory

27 unique protobuf modules confirmed in Even.app `package:even_connect/g2/proto/generated/` (updated from initial count of 28 — `g2_setting` was counted twice):

| # | Module | Library ID | Status | Service ID |
|---|---|---|---|---|
| 1 | common | (shared) | Implemented | — |
| 2 | service_id_def | (enum) | Implemented | — |
| 3 | g2_setting | @1414153617 | Partial | 0x0D-00 |
| 4 | dev_settings | @1411012352 | Implemented | 0x80-xx |
| 5 | dev_config_protocol | @1410360820 | Partial | 0x0D-00 |
| 6 | dev_infomation | @2347168945 | Implemented | 0x09-xx |
| 7 | dev_pair_manager | @2395051248 | Implemented | 0x80-xx |
| 8 | module_configure | @1416454984 | **Not implemented** | 0x0D-00 (via ProtoBaseSettings) |
| 9 | teleprompt | @1443303095 | Implemented | 0x06-xx |
| 10 | conversate | @1922268313 | Implemented | 0x0B-xx |
| 11 | even_ai | @1407414150 | Implemented | 0x07-xx |
| 12 | EvenHub | @2397181980 | Implemented | 0x07-xx |
| 13 | navigation | @1428067439 | Partial (2/10) | 0x08-20 |
| 14 | notification | @1430261884 | Implemented | 0x02-20 |
| 15 | dashboard | @1419512574 | **Not implemented** | 0x07-xx (shares with EvenAI) |
| 16 | menu | @1632267984 | **Not implemented** | 0x0D-00 (likely via g2_setting) |
| 17 | quicklist | @1436323404 | **Not implemented** | TBD (inferred: 0x0F or 0x12-0x1F range) |
| 18 | health | @1421255604 | **Not implemented** | TBD (inferred: 0x03-20, MEDIUM confidence) |
| 19 | glasses_case | @1415496902 | **Not implemented** | 0x0D-00 (via G2) |
| 20 | ring | @1438371976 | Partial | BAE8-xx |
| 21 | onboarding | @1417321442 | **Not implemented** | 0x0D-00 (via ProtoBaseSettings) |
| 22 | sync_info | @1440088238 | **Not implemented** | 0x0D-00 (via ProtoBaseSettings) |
| 23 | logger | @1423103636 | **Not implemented** | TBD (inferred: 0x0F or 0x13-0x1F range) |
| 24 | efs_transmit | (enum) | Partial | 0xC4/0xC5 |
| 25 | ota_transmit | (enum) | **Not implemented** | 0xC4/0xC5 |
| 26 | transcribe | @2396442198 | **Not implemented** | TBD (inferred: 0x05-20, MEDIUM confidence) |
| 27 | translate | @1450417037 | **Not implemented** | 0x07-xx (shares with EvenAI) |

**Summary**: 10 implemented, 3 partial, 14 not implemented. Several modules share service 0x0D-00 via `ProtoBaseSettings` subcommand routing (glasses_case, module_configure, onboarding, sync_info). The `translate` module shares service 0x07-20 with EvenAI and Dashboard (differentiated by type field). Remaining unknown service IDs: menu, quicklist, logger — may have dedicated IDs compiled into Flutter AOT binary. Inferred IDs (MEDIUM confidence): **health → 0x03-20** (UI_HEALTH_APP_ID2 suggests dedicated service, 0x03 is first available gap after 0x02 notifications), **transcribe → 0x05-20** (UI_TRANSCRIBE_APP_ID, 0x05 is available between teleprompter 0x06 and EvenAI 0x07).

**Firmware source file confirmation** (from `ota_s200_firmware_ota.bin` binary string analysis):

| Module | Firmware Source | Confidence |
|--------|----------------|-----------|
| conversate | `pb_service_conversate.c` | CONFIRMED |
| even_ai | `pb_service_even_ai.c` | CONFIRMED |
| teleprompt | `pb_service_teleprompt.c` | CONFIRMED |
| translate | `pb_service_translate.c` | CONFIRMED |
| quicklist | `pb_service_quicklist.c` | CONFIRMED |
| health | `pb_service_health.c` | CONFIRMED |
| ring | `pb_service_ring.c` | CONFIRMED |
| notification | `pb_service_notification.c` | CONFIRMED |
| onboarding | `pb_service_onboarding.c` | CONFIRMED |
| glasses_case | `pb_service_glasses_case.c` | CONFIRMED |
| dev_config | `pb_service_dev_config.c` | CONFIRMED |
| dev_setting | `pb_service_dev_setting.c` | CONFIRMED |
| setting | `pb_service_setting.c` | CONFIRMED |

**Non-protobuf service handlers** (separate firmware implementations):
- `dashboard_service/` — dashboard data routing (uses separate page UI)
- `efs_service/` — Even File Service (maps, images, file transfer)
- `ota_service/` — OTA firmware update service
- `ring_service/` — R1 Ring BLE profile integration

**Service ID prefix convention** (reveals glasses OS architecture):
- `UI_` = foreground protocol (user-facing, needs display state)
- `UI_BACKGROUND_` = background protocol (runs without active display)
- `UX_` = transport-level protocol (device settings, file transfer, OTA)
- `SERVICE_` = infrastructure protocol (sync, configuration)

### BleG2CmdProtoExt Data Package Creators (20)

All protobuf modules route through a single `BleG2CmdProtoExt` class with dedicated creator methods:

```
_createEvenAiDataPackage          _createQuickListDataPackage
_createRingDataPackage            _createLoggerDataPackage
_createDashboardDataPackage       _createFileTransmitDataPackage
_createOnboardingDataPackage      _createEvenHubDataPackage
_createSyncInfoDataPackage        _createModuleConfigureDataPackage
_createNavigationDataPackage      _createMenuDataPackage
_createDevCfgDataPackage          _createG2SettingDataPackage
_createHealthDataPackage          _createNotificationDataPackage
_createTranscribeDataPackage      _createGlassesCaseDataPackage
_createConverseDataPackage        _createTelepromptDataPackage
```

**Notable absence**: No `_createTranslateDataPackage` — Translate routes through EvenAI's data package on 0x07-20.

### Dashboard Protocol (0x07-20, @1419512574)

Dashboard is the glasses' home screen with configurable widget tiles:

**Protobuf messages**: `DashboardDataPackage`, `DashboardSendToApp`, `DashboardReceiveFromApp`, `DashboardRespondToApp`, `AppRespondToDashboard`, `DashboardDisplaySetting`, `DashboardContent`, `DashboardMainPageState`

**6 widget types** (protobuf enum, corrected from initial 29 count which was asset-based):
| Widget | Send | Receive | Expanded View |
|---|---|---|---|
| News | `sNewsWidget` | `rNewsWidget` | `PAGE_TYPE_NEWS_EXPANDED` |
| Schedule | `sScheduleWidget` | `rScheduleWidget` | `PAGE_TYPE_CALENDAR_EXPANDED` |
| Stock | `sStockWidget` | `rStockWidget` | `PAGE_TYPE_STOCK_EXPANDED` |
| Health | (via health module) | `rWidgetComponent` | `PAGE_TYPE_HEALTH_EXPANDED` |
| QuickList | (via quicklist module) | `rWidgetComponent` | `PAGE_TYPE_QUICKLIST_EXPANDED` |
| Status | `sStatusComponent` | `rWidgetComponent` | — |

**Phone→glasses data push**: `sendDashboardBaseSettingInfoToGlass`, `sendWeatherInfoToGlass`, `sendNewsContentToGlass`, `sendStockContentToGlass`, `sendCalendarContentToGlass`, `sendNeedSendNewsCount`

**Weather states**: sunny, night, clouds, fog, mist, sand, drizzle, heavy_drizzle, rain, heavy_rain, freezing_rain, snow, thunderstorm, thunder, squalls, tornado, silent

**Dashboard settings**: auto-close timer (`APP_SET_DASHBOARD_AUTO_CLOSE_VALUE`), temperature unit, combine mode, main widget mode, page view state

**Dashboard sub-pages** (confirmed via firmware source paths in `ota_s200_firmware_ota.bin`):

| Page | Source Files | GUI Source |
|------|-------------|-----------|
| Calendar | `ui_calendar_page.c` | `/app/gui/dashboard/screens/` |
| News | `ui_news_page.c` | `/app/gui/dashboard/screens/` |
| Stock | `ui_stock_page.c` | `/app/gui/dashboard/screens/` |
| Main screen | `ui_DashBaord_Main_Screen.c` | `/app/gui/dashboard/screens/` |

**Page state sync** (from firmware log strings):
- `page_state_sync.c` — persistent UI state synchronization to phone
- Log: `"page_state_sync_init: Successfully synced initial dashboard state (tile=%d, widget=%d)"`
- Tracks: tile index, widget type, quicklist expanded state, completed item UIDs
- Sync direction: glasses → phone (ensures phone app reflects current glasses display state)

### Menu Protocol (@1632267984)

Glasses overlay menu system accessible via gesture/head-up:

**Protobuf messages**: `meun_main_msg_ctx` (typo "meun" is in original code), `MenuInfoSend`, `ResponseMenuInfo`, `Menu_Item_Ctx`

**Commands**: `APP_SEND_MENU_INFO`, `OS_RESPONSE_MENU_INFO`, `OS_NOTIFY_MENU_STARTUP_REQUEST_LOCATION_LIST`

**OS response packet types** (for rendering):
- `OS_RESPONSE_TEXT_DATA_PACKET` — text content
- `OS_RESPONSE_IMAGE_RAW_DATA_PACKET` — icons/images
- `OS_RESPONSE_SHUTDOWN_PAGE_PACKET` — close menu
- `OS_RESPONSE_CREATE_STARTUP_PAGE_PACKET` — startup page
- `OS_RESPONSE_REBUILD_PAGE_PACKET` — refresh/rebuild
- `OS_RESPONSE_AUDIO_CTR_PACKET` — audio control
- `OS_RESPONSE_HEARTBEAT_PACKET` — keepalive

Menu items are typed (`DashboardMenuItemType`) and customizable through dashboard settings.

**10 AI-triggered skills** (voice-invoked via EvenAI SKILL type=6, `sendSkill*` methods):

| skillId | Name | Function |
|---|---|---|
| 0 | `brightness` | Adjust display brightness |
| 1 | `translate` | Start translation mode |
| 2 | `notification` | Show notification list |
| 3 | `teleprompter` | Open teleprompter |
| 4 | `navigate` | Start navigation |
| 5 | `conversate` | Start conversation mode |
| 6 | `quicklist` | Save to quicklist |
| 7 | `auto_brightness` | Toggle auto-brightness |

Menu-only skills (not via SKILL type=6, triggered through menu overlay):
- `show_favorite_location_list` — display favorite locations
- `silent_mode_on` — enable silent mode
- `show_notification` — display notification list

Additional EvenAI commands (discovered, not fully documented):
- `sendWakeupResp` — response to wake word detection
- `sendVadEndFeedBack` — VAD silence feedback
- `sendAnalyzeLoading` — loading state during analysis
- `sendIllegalState` — error/illegal state notification

### QuickList Protocol (0x??, @1436323404)

Note/bookmark system synced to the glasses:

**Protobuf messages**: `QuicklistDataPackage` (with `CommandData` oneof), `QuicklistEvent`, `QuicklistItem`, `QuicklistMultItems`

**Functions**: `sendMultAdd`, `sendMultFullUpdate`, `sendItemSingle`, `respondPagingByUid`, `onListenOsPushEvent`

**Data management**: Items have UIDs, organized into groups, sortable, cached locally. Items can be created from:
- Manual entry
- EvenAI responses ("save to quicklist" skill via `sendSkillQuickList`)
- Shared from other apps (`share_to_quicklist`)

**Firmware-side implementation** (from `ota_s200_firmware_ota.bin` binary analysis):
- `quicklist_data_manager.c` — item CRUD and UID tracking on glasses
- `ui_quicklist_page.c` — LVGL UI page with scroll, focus, and fade animations
- Protobuf item fields: `uid`, `index`, `isCompleted`, `title` (fixed-size), `timestamp`, `ts_type`
- Completed items use temp cache → batch sync via Bluetooth
- Firmware log: `"Successfully sent %d completed UIDs via Bluetooth"`, `"Merged %d items from temp cache to completed items"`
- `quicklist_ext_fifo` — event queue for async UI updates
- GUI features: fade animations on add/remove, scroll position restoration, border animation (focus item highlighting)

### Health Protocol (0x??, @1421255604)

Health data relay from R1 Ring → phone → glasses display:

**8 health data types**: HEART_RATE, BLOOD_OXYGEN (SpO2), TEMPERATURE, STEPS, CALORIES, SLEEP, PRODUCTIVITY, ACTIVITY_MISSING

**Commands**: SINGLE_DATA, MULT_DATA, SINGLE_HIGHLIGHT, MULT_HIGHLIGHT

**Functions**: `sendHealthSingle`, `sendHealthMult`, `sendHealthHighlightMult`, `sendDashboardSnapshot`, `onListenOsHealthEvent`

**Display strings**: `os_dashboard_health_bpm`, `os_dashboard_health_steps`, `os_dashboard_health_calories`, `os_dashboard_health_productivity_score`

"Highlights" are AI-generated health insights summarizing trends.

**R1 Ring health BLE extensions** (commands sent on BAE80012):

| Extension | Method | Purpose |
|---|---|---|
| `BleRing1CmdHealthExt` | `getDailyData` | Fetch daily HR, SpO2, HRV, steps, sleep, skin temp |
| `BleRing1CmdHealthExt` | `ackNotifyData` | Acknowledge health notification data |
| `BleRing1CmdWearStatusExt` | `getWearStatus` | Query on-wrist detection state |
| `BleRing1CmdSettingsStatusExt` | `getHealthSettingsStatus` | Get health monitoring config |
| `BleRing1CmdSettingsStatusExt` | `setHealthSettingsStatus` | Set health monitoring config |
| `BleRing1CmdSettingsStatusExt` | `setHealthEnable` | Enable/disable health monitoring |
| `BleRing1CmdSettingsStatusExt` | `getSystemSettingsStatus` | Get system settings |
| `BleRing1CmdSettingsStatusExt` | `setSystemSettingsStatus` | Set system settings |
| `BleRing1CmdGoMoreExt` | `getAlgoKeyStatus` | Get GoMore algorithm key status |
| `BleRing1CmdGoMoreExt` | `setAlgoKey` | Set GoMore algorithm key |

**Data relay protocol**: Health data traverses Ring → G2 → Phone via:
- `UX_RING_DATA_RELAY_ID` — structured relay through glasses
- `UX_RING_ROW_DATA_ID` — raw ring data passthrough
- `BleG2CmdProtoRingExt|openRingBroadcast` — force ring into BLE advertising
- `BleG2CmdProtoRingExt|switchRingHand` — switch left/right hand config
- `setRingLowPerformanceMode` — toggle ring low power mode

**Cloud health API** (6 endpoints):
- `/v2/g/health/push` — upload health data
- `/v2/g/health/get_info` — health profile
- `/v2/g/health/get_latest_data` — latest readings
- `/v2/g/health/query_window` — time-windowed query
- `/v2/g/health/batch_query_window` — batch multi-window query
- `/v2/g/health/export` — export health data

**Note**: Ring health queries currently return `00 00` (zero data) — ring may require active on-wrist wearing/sensor contact to produce readings. GoMore is a third-party health analytics provider (`get_pkey` API).

**Phone-side health processing**: `FlutterEzwHealthAlgorithmPlugin` is a native framework that performs health data algorithmic processing (e.g., HR/SpO2 calculation from raw sensor readings, sleep staging). The ring sends raw sensor data; the phone computes derived health metrics.

**Health protobuf detailed fields** (from firmware binary analysis):
- Heart rate: `bpm` (int), `timestamp` (int64)
- Blood oxygen: `spo2_percent` (int), `timestamp`
- Temperature: `temp_celsius` (float/int scaled), `timestamp`
- Steps: `step_count` (int), `distance_meters` (int), `calories` (int), `timestamp`
- Sleep: `stage` (enum: awake/light/deep/rem), `duration_minutes` (int), `timestamp`
- Productivity: `score` (0-100), `timestamp`

### Glasses Case Protocol (0x0D-00, @1415496902)

Protocol for querying and receiving case status via G2 control channel.

**Messages**: `GlassesCaseDataPackage`, `GlassesCaseInfo`
**Commands**: `eGlassesCaseCommandId`, `GLS_WEAR_STATUS` (in-case detection)
**Functions**: `ProtoBaseSettings|getGlassesCaseInfo` — single query/response pattern

The case MCU communicates with glasses via wired relay (contact pins through frame, NOT BLE), and glasses forward status to the phone over BLE.

**Firmware log strings** (from `box.detect` subsystem):
```
[box.detect]Receive case sync from peer: msg_id=%d, soc=%d, charging=%d, lid=%d, in_case=%d
[box.detect]Notify glasses case status change: soc=%d, charge=%d, lid=%d, in_case=%d
```

**GlassesCaseInfo fields**:
| Field | Protobuf | Purpose |
|---|---|---|
| `caseElectricity` / `soc` | varint | Case battery level (0-100%) |
| `caseIsCharging` / `charging` | varint (bool) | Charging state |
| `lidOpen` / `lid` | varint (bool) | Case lid open/closed |
| `inCaseStatus` / `in_case` | varint (bool) | Glasses-in-case detection |

**Notification flow**: Case MCU → wired relay → glasses firmware (`box.detect`) → BLE notification on 0x0D-00 → phone app. Status changes are pushed proactively (unsolicited) when case state changes (lid open/close, glasses inserted/removed, charger connected).

**iOS SDK**: `G2GlassesCaseReader` queries on 0x0D-00/0x0D-20, parses responses into `G2GlassesCaseStatus`. Callback: `onGlassesCaseStatus` in `G2ResponseDecoder`. UI: Glasses Case section in DevicesView.

**OTA box timeout**: Firmware sets a 3-minute timeout for case MCU firmware transfer operations.

### Onboarding Protocol (0x0D-00, @1417321442)

First-time setup flow with 7 states:

**Messages**: `OnboardingDataPackage`, `OnboardingConfig`, `OnboardingEvent`, `OnboardingHeartbeat`
**Functions**: `setOnBoardingStartUp`, `setOnBoardingStart`, `setOnBoardingEnd`, `getBoardingIsHeadup`

**State machine** (phone-side):
```
video_state → muti_video_state → wear_state → headup_state →
notification_state → disconnect_state → end_state
```

**8 tutorial videos** (both glasses + ring gestures):
- `video_onboarding_glasses_long_press/single_tap/double_tap/swipe.mp4`
- `video_onboarding_ring_single_tap/double_tap/long_press/swipe.mp4`

Routes through `ProtoBaseSettings` on 0x0D-00. The glasses execute commands; the state machine is entirely phone-side.

**Calibration procedures** (during onboarding):
1. Display focus calibration — verify optical projection alignment
2. Head-up angle detection — set wakeup trigger angle threshold
3. Wear detection sensor verification — confirm nose/temple contact sensing
4. Notification system setup — configure notification forwarding permissions

**Cloud completion**: `postGlassesOnBoardingEnd` → `/v2/g/set_on_boarded` marks the device as onboarded in the cloud backend, preventing re-triggering on subsequent connections.

### Sync Info Protocol (SERVICE_, @1440088238)

Cloud configuration backup/restore:

**Messages**: `sync_info_main_msg_ctx`, `sync_info_data_msg`
**Commands**: `APP_REQUEST_SYNC_INFO`, `OS_NOTIFY_SYNC_INFO`
**Cloud endpoints**: `/v2/g/upload_nv` (backup), `/v2/g/get_nv` (restore) with CRC integrity

Purpose: survive factory resets by restoring NV (non-volatile) settings from cloud.

**Additional cloud endpoint**: `/v2/g/update_set2` — key-value store for named variables (separate from bulk NV backup).

**Data categories synced**:
- Display settings (brightness calibration, grid distance/height offsets)
- Gesture mappings and customization
- Feature toggles (which modules enabled/disabled)
- Menu and QuickList items
- Dashboard widget configuration and layout
- Notification whitelist (`user/notify_whitelist.json`)
- User preferences (temperature unit, language, etc.)

**Integrity protection**: CRC checks on download, version tracking for conflict resolution, server-authoritative on conflicts.

### Logger Protocol (UI_, @1423103636)

Remote logging from glasses to phone:

**Messages**: `logger_main_msg_ctx`, `request_filelist_msg`, `delete_file_msg`, `ble_trans_level_msg`
**Functions**: `sendLiveLogSwitch`, `sendLiveLogLevel`, `sendLogHeartbeat`, `deleteAllLogFiles`
**Log types**: `ProtoLogMessage` with `LogCategory` and `LogLevel` enums

Supports: (1) live log streaming with configurable level/category filtering, (2) log file management (list/delete files on glasses), (3) heartbeat keepalive. The `ble_trans_level_msg` configures what log level to transmit over BLE.

**Firmware-side constraint** (from binary log strings): Log file paths MUST start with `/log/` prefix. The firmware rejects invalid paths with: `"loggerSetting_common_data_handler: invalid file path, must start with /log/: %s"`. This validates the path namespace before file operations, preventing arbitrary filesystem access via the logger protocol. Source: `logger_setting.c` / `pb_service_setting.c`.

**Log levels**: DEBUG, INFO, WARN, ERROR, CRITICAL — configurable minimum level filter for BLE transmission.

**Firmware log file storage** (per-eye, on QSPI flash):
```
L:/log/compress_log_0.bin  through  L:/log/compress_log_4.bin   (left eye, 5 rotating log files)
R:/log/compress_log_0.bin  through  R:/log/compress_log_4.bin   (right eye, 5 rotating log files)
L:/log/hardfault.txt                                             (left eye crash dump)
R:/log/hardfault.txt                                             (right eye crash dump)
```

The `compress_log_*.bin` files are rotating compressed logs (oldest overwritten when full). `hardfault.txt` files capture ARM HardFault crash dumps — these are critical for diagnosing firmware crashes and can be retrieved via the file transfer service (0xC4/0xC5).

**Hardfault log rotation** (from firmware binary strings): The `hardfault.txt` file has a 100KB size limit. When the limit is reached, the firmware rotates (truncates) the file before writing new crash data. This prevents a single persistent crash loop from exhausting flash storage.

### OTA Transmit Protocol (UX_, enum-only)

OTA firmware update command enums (no protobuf messages — uses custom byte serialization):

**Commands**: `OTA_TRANSMIT_START`, `OTA_TRANSMIT_INFORMATION`, `OTA_TRANSMIT_FILE`, `OTA_TRANSMIT_RESULT_CHECK`, `OTA_TRANSMIT_NOTIFY`
**Two channels**: `UX_OTA_TRANSMIT_CMD_ID` (commands), `UX_OTA_TRANSMIT_RAW_DATA_ID` (data)
**Export counterpart**: `UX_OTA_EXPORT_FILE_CMD_ID`, `UX_OTA_EXPORT_FILE_RAW_DATA_ID`
**Implementation classes**: `EvenOtaUpgradeCmd`, `EvenOTAUpgradeCmdResponse` (`.fromBytes`), `EvenOTAUpgradeBigPackage`

The actual command encoding uses custom byte serialization, not protobuf messages.

**OTA response codes** (11 total): See §12 OTA table for canonical names (`OTA_RECV_RSP_SUCCESS` through `OTA_RECV_RSP_UPDATING`). `SYS_RESTART` (code 9) triggers a firmware reboot.

**Safety note**: OTA probing is excluded from test sweeps — sending malformed OTA commands could potentially brick the glasses.

### Transcribe Protocol (UI_, @2396442198)

Display-only speech transcription (separate from Conversate):

**Messages**: `TranscribeDataPackage`, `TranscribeControl`, `TranscribeResp`, `TranscribeNotify`, `TranscribeHeartBeat`, `TranscribeResult`
**4 commands**: TRANSCRIBE_CTRL, TRANSCRIBE_RESULT, TRANSCRIBE_NOTIFY, TRANSCRIBE_HEARTBEAT

**Key differences from Conversate**:
- No AI analysis (Conversate adds keypoints, tags, insights)
- Speaker diarization support (`enable_speaker_diarization`, `enable_speaker_segmentation`, `speaker_id`)
- Simpler protocol (4 commands vs Conversate's 10)
- Uses same ASR backends (Soniox + Azure)

**4 ASR backends** (ranked by typical priority):

| Backend | Class | On-device? | Notes |
|---|---|---|---|
| Apple SFSpeechRecognizer | `EvenTranscribeRecognizer` | Yes | Low latency, iOS-native |
| Azure Speech | `AzureTranscribeRecognizer` | No (cloud) | High accuracy, multiple languages |
| Soniox | `SonioxTranscribeRecognizerV2` | No (cloud) | Backup, `asr_soniox_config_v3` |
| Sherpa-ONNX | (via SherpaOnnx framework) | Yes | ML-based on-device ASR |

**Voice Activity Detection (VAD)**: Silero VAD v4/v5 (ONNX model `vad_model.onnx`) — on-device speech endpoint detection. Triggers result delivery on speech-to-silence transition.

**Timing constants**:
- Segment interval: 50–1000ms (valid range)
- ASR result delivery interval: 100–1000ms (valid range)
- Result callback timeout: 30s
- Audio pipeline: G2 mic → LC3 encode (on-glasses) → NUS 0xF1 frames → flutter_ezw_lc3 decode (PCM) → GTCRN noise reduction → AGC + audio enhance → ASR + VAD → Transcription output

### Translate Protocol (UI_, @1450417037)

Bidirectional translation (routes through 0x07-20 via EvenAI):

**Messages**: `TranslateDataPackage`, `TranslateControl`, `TranslateResp`, `TranslateNotify`, `TranslateHeartBeat`, `TranslateResult`, `TranslateModeSwitch`
**6 commands**: TRANSLATE_CTRL, TRANSLATE_RESULT, TRANSLATE_NOTIFY, TRANSLATE_HEARTBEAT, TRANSLATE_MODE_SWITCH

**Functions**: `sendStartTranslate`, `sendStopTranslate`, `sendPauseTranslate`, `sendResumeTranslate`, `sendTranslateResult`, `sendTranslateHeartbeat`

**Translation modes**:
- `one_way` — translates what other people say to glasses display
- `two_way` — bidirectional (phone mic for user + glasses mic for other speaker)
- Pause/resume supported (preserves session state without ending translation)

**ASR backends**: Same 4 as Transcribe (Apple, Azure, Soniox, Sherpa-ONNX). Primary translation backend: Azure `SPXTranslationRecognizer`.

**Timing**: 2-hour max session (Soniox session limit), 30s result callback timeout, 50–1000ms segment interval.

**Voice intents** (BERT-triggered): `open_translate | language` (start with target language entity), `close_translate` (stop).

**Cloud endpoints**: `/v2/g/translate_delete`, `/v2/g/translate_update`, `/v2/g/translate_ai_summary`

**iOS SDK implementation** (2026-03-03):
- `G2TranslateProtocol.swift`: Payload builders for type 20-23 on 0x07-20
- `G2TranslateSender.swift`: Session lifecycle (start/stop/pause/resume/result), 15s heartbeat, `magic_random` dedup
- Wire format speculative — type values 20-23 inferred from method ordering in Even.app RE
- Result payload uses 30-byte fixed-length text field (same as conversate)
- Integrated into AudioStreamView with "Send to Glasses" toggle

| Type | Command | Fields |
|---|---|---|
| 20 | TRANSLATE_CTRL | f1=20, f2=msgId, f3={f1=action(1-4)}, f8={f1=magic} |
| 21 | TRANSLATE_RESULT | f1=21, f2=msgId, f7={f1=text(30B), f2=isFinal}, f8={f1=magic} |
| 22 | TRANSLATE_HEARTBEAT | f1=22, f2=msgId |
| 23 | TRANSLATE_MODE_SWITCH | f1=23, f2=msgId, f3={f1=mode(1=oneWay,2=twoWay)} |

### Module Configure Protocol (SERVICE_, @1416454984)

Meta-configuration layer managing which features/modules are enabled:

**Messages**: `module_configure_main_msg_ctx`, `module_configure_Cmd_list`
**Wraps**: `dashboard_general_setting` + `send_system_general_setting` + `SYSTEM_GENERAL_SETTING_PACKET`

Configures the dashboard layout, system-wide settings, and module enable/disable state.

**Per-eye brightness calibration**:
- `leftMaxBrightness` / `rightMaxBrightness` — individual max brightness for each JBD display
- Compensates for manufacturing variance between left/right micro-displays
- Values likely 0-42 (matching Format A brightness protocol)

**Feature toggles** (known settings with cmdIds):

| Setting | cmdId | Description |
|---|---|---|
| `DEVICE_ANTI_SHAKE_ENABLE` | 15 | Anti-shake filter for display stability |
| `DEVICE_WAKEUP_ANGLE` | 16 | Head-up angle threshold for display wake |
| `setWearDetection` | — | Enable/disable wear detection gating |
| `setHeadUpTriggerDashboard` | — | Motion-activated dashboard on head-up |

**Display calibration settings** (via `DisplaySettingsExt`):
- `setGridDistance` — X offset (field 3 in config proto)
- `setGridHeight` — Y offset (field 4 in config proto)
- `surfaceBright` — ambient light sensor calibration curve
- `ALSInfo` — ALS sensor data readout

**15 configurable module categories**: Dashboard, Teleprompter, Conversate, Translate, Transcribe, Navigation, QuickList, Health, Notifications, Brightness, Compass, Gestures, Audio, OTA, Logging. Each can be independently enabled/disabled, with state persisted to cloud via Sync Info.

### EvenAI Skill IDs (voice-triggered features)

All skills route through `ProtoAiExt|sendSkill*` on 0x07-20 type=6:

| skillId | Name | Method | Function |
|---|---|---|---|
| 0 | Brightness | `sendSkillBrightness` | Adjust brightness by voice |
| 1 | Translate | `sendSkillTranslate` | Start translation |
| 2 | Notification | `sendSkillNotification` | Show notifications |
| 3 | Teleprompter | `sendSkillTeleprompt` | Start teleprompter |
| 4 | Navigate | `sendSkillNavigate` | Start navigation |
| 5 | Conversate | `sendSkillConverse` | Start conversation |
| 6 | QuickList | `sendSkillQuickList` | Save to quicklist |
| 7 | Auto-brightness | `sendSkillBrightnessAuto` | Toggle auto-brightness |

Additional EvenAI commands (beyond the documented CTRL/ASK/REPLY/SKILL/HEARTBEAT):
- `sendWakeupResp` — acknowledges wake word ("hey_even") detection
- `sendVadEndFeedBack` — VAD (Voice Activity Detection) end-of-speech feedback
- `sendAnalyzeLoading` — loading state indicator during AI analysis
- `sendIllegalState` — error/illegal state signal to glasses

### Conversate Full Command Set (13 commands, for reference)

| Command | Purpose |
|---|---|
| `CONVERSATE_NONE` | Default/unset |
| `CONVERSATE_CONTROL` | Session control |
| `CONVERSATE_HEART_BEAT` | Keepalive |
| `CONVERSATE_SUCCESS` | Operation success |
| `CONVERSATE_TRANSCRIBE_DATA` | Raw ASR text |
| `CONVERSATE_TITLE_DATA` | Session title |
| `CONVERSATE_KEYPOINT_DATA` | AI key points extraction |
| `CONVERSATE_TAG_DATA` | Tag/topic annotations |
| `CONVERSATE_TAG_TRACKING_DATA` | Tag tracking over time |
| `CONVERSATE_COMM_RESP` | Communication response |
| `CONVERSATE_STATUS_NOTIFY` | Status notification |
| `CONVERSATE_ERR_NETWORK` | Network error |
| `CONVERSATE_ERR_FAIL` | General failure |

**5 tag types**: QUESTION, SUGGEST, KNOWLEDGE, PEOPLEWIKI, NONE

**Conversate config flags** (from firmware binary strings):
- `summary_and_tag` — enable AI summary extraction and tag generation
- `transcribe` — enable real-time transcription display
- `auto_pop_en` — auto-popup conversate UI on speech detection
- `use_audio` — use glasses microphone vs phone microphone

**Translate duplicate detection** (from firmware strings):
- `magic_random` field — used to detect duplicate translation packets and prevent re-display

### Navigation Extended Protocol

**10 sub-commands**: start(1), basicInfo(2), miniMap(3), overviewMap(4), heartbeat(5), recalculating(6), arrive(7), stop(8), startError(9), favoriteList(10)

**Map fragment protocol fields**: `mapSessionId`, `mapTotalSize`, `compressMode`, `mapFragmentIndex`, `mapFragmentPacketSize`, `mapRawData`, `miniMapBorderEn`

**6 exit reasons**: `os_navigate_complete`, `os_navigate_connection_time_out`, `os_navigate_fail_location_too_far`, `os_navigate_fail_no_location_access`, `os_navigate_fail_something_went_wrong`, `os_navigate_recalculating`

**Native Navigation API** (19 Pigeon methods via `even_navigate` package):

| Method | Purpose |
|---|---|
| `startNavigation` | Begin turn-by-turn |
| `startNavigationWithWaypoints` | Multi-stop navigation |
| `stopNavigation` | End navigation |
| `calculateRoute` | Route planning |
| `recenter` | Re-center map on user |
| `resetState` | Reset navigation state |
| `switchTravelMode` | Change mode (driving/cycling/walking) |
| `captureMiniMap` | Capture mini-map BMP for glasses |
| `captureOverviewMap` | Capture overview BMP for glasses |
| `cancelAllSnapshots` | Cancel pending map captures |
| `createMapView` / `disposeMapView` | Map lifecycle |
| `fetchCurrentLocation` | Get GPS position |
| `fetchCurrentHeading` | Get compass heading |
| `setNavigateVoiceOnOff` / `getNavigateVoiceOnOff` | Voice guidance |
| `isUserLocationVisible` | Check if user is on-screen |
| `isUserLocationCentered` | Check if user is centered |
| `hasBackgroundLocationPermission` | Permission check |

**Dual map providers**:
- **Mapbox** (international): driving/cycling/walking profiles; custom style for G2 display rendering
- **AMap/Gaode** (Chinese market): `AMapService` class in `even_navigate` package — separate implementation for China where Google Maps/Mapbox are restricted

---

## 15. Glasses OS Application IDs

The firmware runs a lightweight OS with registered application contexts:

| App ID | Function |
|---|---|
| `UI_DEFAULT_APP_ID` | Default/home |
| `UI_TELEPROMPT_APP_ID` | Teleprompter |
| `UI_CONVERSATE_APP_ID` | Conversate |
| `UI_TRANSLATE_APP_ID` | Translation |
| `UI_TRANSCRIBE_APP_ID` | Transcription |
| `UI_QUICKLIST_APP_ID` | Quick list |
| `UI_HEALTH_APP_ID` | Health |
| `UI_ONBOARDING_APP_ID` | Onboarding |
| `UI_SETTING_APP_ID` | Settings |
| `UI_LOGGER_APP_ID` | Logger |
| `UI_BACKGROUND_DASHBOARD_APP_ID` | Dashboard (background) |
| `UI_BACKGROUND_EVENHUB_APP_ID` | EvenHub (background) |
| `UI_FOREGROUND_SYSTEM_ALERT_APP_ID` | System alerts |
| `UI_FOREGROUND_SYSTEM_CLOSE_APP_ID` | System close |
| `UI_FOREGROUND_NOTIFICATION_ID` | Foreground notification |
| `UX_GLASSES_CASE_APP_ID` | Glasses case management |
| `SERVICE_MODULE_CONFIGURE_APP_ID` | Module configuration service |
| `SERVICE_SYNC_INFO_APP_ID` | Sync info service |

**Naming convention**: `UI_` = foreground (needs display), `UI_BACKGROUND_` = background, `UX_` = transport-level, `SERVICE_` = infrastructure.

**Service ID routing key** (`service_id_def.pbenum.dart`): The `service_id_def` protobuf module contains the master enum mapping App IDs → BLE service IDs. Seven IDs have named enum entries but their numeric values are compiled into the Flutter AOT binary and not directly extractable:

| Enum Name | Protocol | Inferred Service ID |
|---|---|---|
| `UI_LOGGER_APP_ID2` | Logger | Unknown (dedicated, not 0x0D-00). Likely 0x0F or 0x13-0x1F |
| `UI_HEALTH_APP_ID2` | Health | **Inferred 0x03-20** (MEDIUM) — first available gap after 0x02-20 (notifications) |
| `UI_QUICKLIST_APP_ID` | QuickList | Unknown (dedicated, not 0x0D-00). Likely 0x0F or 0x12-0x1F |
| `UI_TRANSCRIBE_APP_ID` | Transcribe | **Inferred 0x05-20** (MEDIUM) — gap between teleprompter 0x06 and EvenAI 0x07 |
| `SERVICE_MODULE_CONFIGURE_APP_ID` | Module Configure | 0x0D-00 (confirmed via ProtoBaseSettings) |
| `SERVICE_SYNC_INFO_APP_ID` | Sync Info | 0x0D-00 (confirmed via ProtoBaseSettings) |
| `UX_GLASSES_CASE_APP_ID` | Glasses Case | 0x0D-00 (confirmed via ProtoBaseSettings) |

The 4 unknown service IDs (Logger, Health, QuickList, Transcribe) must occupy gaps in the 0x00-0xFF range. Available hi-bytes: 0x03, 0x05, 0x0F, 0x12-0x1F. Extraction requires Flutter AOT decompilation or BLE traffic interception while the Even.app exercises these features.

---

## 16. Audio Pipeline

### Microphone Path (Right Eye → Phone)

```
G2 Right Eye                                   Phone
┌────────────────────┐                   ┌──────────────────────────────┐
│ Microphone (PDM)   │                   │ Even.app                     │
│       │            │                   │                              │
│  LC3 Encoder       │   NUS BLE         │  LC3 Decoder (flutter_ezw)   │
│  (GX8002B codec)   │ ──────────────▶   │       │                      │
│       │            │  0xF1 + LC3       │  GTCRN Neural Denoiser       │
│  LC3 frames        │  frames           │       │                      │
│  16 kHz, 40 B/frame│                   │  EvenAGC (gain control)      │
└────────────────────┘                   │       │                      │
                                         │  SileroVAD (voice detect)    │
                                         │       │                      │
                                         │  ASR (SherpaOnnx / Soniox)   │
                                         │       │                      │
                                         │  BERT NLU (30 intents)       │
                                         └──────────────────────────────┘
```

- Audio frames arrive on NUS RX (6E400003) with `0xF1` prefix (stripped before delivery)
- 10ms frame duration, 16 kHz sample rate, **40 bytes per frame** (LC3 compressed)
- LC3 codec parameters confirmed from SDK README: `dtUs=10000`, `srHz=16000`, little-endian
- LC3 codec performs on-device encoding; phone-side decode via `flutter_ezw_lc3` FFI (`Lc3Bindings`, `_lc3_decode`)
- **Frame format clarification**: The 40 bytes/frame are LC3-compressed (NOT raw PCM). Raw 16kHz PCM at 10ms would be 320 bytes/frame (16000 × 0.01 × 2 bytes). The 40-byte size confirms the Apollo510b (via GX8002B codec IC) performs LC3 compression on-device before NUS transmission. Our Swift `G2AudioConstants.bytesPerFrame = 40` is correct for the compressed format

### Phone-Side Audio Processing Stack

After LC3 decoding, the phone applies a multi-stage audio processing pipeline:

```
LC3 Decode → EvenAGC → Speech Enhancement → VAD → ASR/Transcription
                │              │                     │
           Custom AGC    ML Denoiser           SileroVAD
           (gain ctrl)   (SherpaOnnx)          (ONNX model)
```

| Component | Technology | Purpose |
|---|---|---|
| **LC3 Decode** | `flutter_ezw_lc3` (FFI) | Bluetooth LE Audio codec decode |
| **AGC** | `EvenAGC` (custom) | Automatic Gain Control for mic levels |
| **Neural Denoising** | GTCRN (via ONNX Runtime) | Neural network noise reduction (primary, after LC3 decode) |
| **Speech Enhancement** | SherpaOnnx `OfflineSpeechDenoiser` | Secondary ML-based noise reduction |
| **VAD** | `SileroVadModelConfig` + `/vad_model.onnx` | Voice Activity Detection |
| **ASR (Primary)** | SherpaOnnx `OnlineStream` | Real-time speech recognition |
| **ASR (Backup)** | Soniox (`asr_soniox_config_v3`) | Secondary ASR provider |
| **Speaker Diarization** | `SherpaOnnxOfflineSpeakerDiarization` | Multi-speaker identification |
| **Language ID** | `SherpaOnnxSpokenLanguageIdentification` | Automatic language detection |
| **Keyword Spotting** | `SherpaOnnxKeywordSpotterConfig` | Wake word ("hey_even") detection |
| **TTS** | `SherpaOnnxCreateOfflineTts` | Text-to-speech synthesis |
| **AAC Encoding** | AAC ADTS encoder | Audio export/streaming format |
| **BERT Model** | Embedded BERT (ONNX) | NLP post-processing |

**SherpaOnnx** is the backbone of the audio intelligence stack — it provides 7 separate ML capabilities, all running on the phone (not on the Apollo510b). The glasses are purely a microphone + display peripheral.

### Firmware Audio Manager (from binary analysis)

The Apollo510b firmware manages audio at the system level via `service_audio_manager.c`:

- **Inter-eye audio sync**: `"sending audio sync msg to peer: msg_id=%d"` — coordinates audio state between left and right eyes via the wired inter-eye link
- **PCM stream tracking**: `"PCM stream is already occupied by app ID %d, unregistering previous app"` — only one app can own the microphone at a time. When a new feature requests audio (e.g., switching from Conversate to EvenAI), the previous owner is forcibly unregistered
- **Codec DFU path**: `service_codec_dfu.c` handles GX8002B firmware updates, `service_touch_dfu.c` handles CY8C4046FNI DFU. Both track firmware type, size, offset, and CRC32 during transfer

### Supported Audio Codec Formats (8)

From `record_ios` native plugin in `even_runner` binary:

| Codec | Constant | Type |
|---|---|---|
| AAC-LC | `aacLc` | Lossy (low complexity) |
| AAC-ELD | `aacEld` | Low-delay (real-time comms) |
| AAC-HE | `aacHe` | High efficiency (low bitrate) |
| AMR-NB | `amrNb` | Narrowband speech (8 kHz) |
| AMR-WB | `amrWb` | Wideband speech (16 kHz) |
| Opus | `opus` | Open standard (variable rate) |
| FLAC | `flac` | Lossless compression |
| PCM 16-bit | `pcm16bits` | Raw uncompressed |

**Recording config**: `bitRate`, `sampleRate`, `numChannels`, `autoGain`, `echoCancel`, `noiseSuppress`, `manageAudioSession`, `defaultToSpeaker`, `allowBluetoothA2DP`, `overrideMutedMicrophoneInterruption`

The Even.app supports all 8 codecs via the `record_ios` plugin. The primary mic path from G2 uses LC3 → PCM, but recorded sessions can be exported/encoded in any of these formats.

---

## 17. AI Agent Architecture

The Even.app implements a phone-side AI agent with a state machine that coordinates voice interaction with the G2 glasses.

### State Machine

```
┌─────────┐    wake word    ┌──────────┐    voice       ┌─────────┐
│  IDLE   │ ──────────────▶ │ WAKEUP   │ ─────────────▶ │  ASR    │
│         │   "hey_even"    │          │   detected     │         │
└─────────┘                 └──────────┘                └────┬────┘
     ▲                                                       │
     │                                                       │ speech
     │                                                       │ recognized
     │                      ┌──────────┐    command    ┌─────▼────────┐
     └────────────────────  │  STAY    │ ◀───────────  │ CMD_DISPATCH │
        timeout/exit        │          │   processed   │              │
                            └──────────┘               └──────────────┘
```

State source files (from Even.app strings):
- `even/common/services/ai_agent/state/idle_state.dart`
- `even/common/services/ai_agent/state/wakeup_state.dart`
- `even/common/services/ai_agent/state/asr_state.dart`
- `even/common/services/ai_agent/state/cmd_dispatch_state.dart`
- `even/common/services/ai_agent/state/stay_state.dart`

### Voice Activation

| Component | Technology | Evidence |
|---|---|---|
| **Wake word** | "hey_even" | `hey_even`, `hey_even_increase_battery_usage` strings |
| **VAD (Voice Activity Detection)** | SileroVAD (ONNX model) | `sileroVad`, `SileroVadModelConfig`, `/vad_model.onnx` |
| **VAD lifecycle** | Start → End → Timeout | `vadStart`, `handleVadEnd`, `sendVadEndFeedBack`, `VAD_TIMEOUT`, `VAD_END from glasses` |
| **Full-duplex** | Supported | `isAIStateFullDuplex` flag |
| **Illegal state handling** | Error recovery | `ProtoAiExt|sendIllegalState`, `AIState is not active, exit` |

### BERT Voice Intent Model (30 intents)

The Even.app includes an on-device BERT intent classifier (`modules/bert/src/tokenizer.cpp`, ONNX Runtime). 30 voice intents are recognized locally without cloud:

| # | Intent | Entity | Category |
|---|---|---|---|
| 1 | `open_teleprompt` | — | Feature |
| 2 | `close_teleprompt` | — | Feature |
| 3 | `open_conversate` | — | Feature |
| 4 | `close_conversate` | — | Feature |
| 5 | `open_translate` | `language` | Feature |
| 6 | `close_translate` | — | Feature |
| 7 | `open_transcribe` | — | Feature |
| 8 | `close_transcribe` | — | Feature |
| 9 | `open_navigate` | `destination` | Feature |
| 10 | `close_navigate` | — | Feature |
| 11 | `open_quicklist` | — | Feature |
| 12 | `close_quicklist` | — | Feature |
| 13 | `open_dashboard` | — | Feature |
| 14 | `close_dashboard` | — | Feature |
| 15 | `set_brightness` | `level` | Setting |
| 16 | `set_volume` | `level` | Setting |
| 17 | `set_silent_mode` | `on/off` | Setting |
| 18 | `take_photo` | — | R1 Ring |
| 19 | `show_notification` | — | Info |
| 20 | `clear_notification` | — | Info |
| 21 | `show_battery` | — | Info |
| 22 | `show_time` | — | Info |
| 23 | `show_weather` | — | Info |
| 24 | `show_calendar` | — | Info |
| 25 | `show_health` | — | Info |
| 26 | `show_stocks` | — | Info |
| 27 | `set_timer` | `duration` | Utility |
| 28 | `set_alarm` | `time` | Utility |
| 29 | `add_quicklist_item` | `text` | Feature |
| 30 | `general_query` | `text` | Cloud AI fallback |

**Note**: Intent #18 (`take_photo`) confirms the R1 Ring has a camera. Intent #30 (`general_query`) is the only one requiring cloud — the other 29 are handled entirely on-device.

### On-Glasses vs Phone-Side Processing

The AI pipeline is split between devices:
- **G2 glasses (Apollo510b)**: Microphone capture → LC3 encoding (GX8002B codec) → BLE transmission via NUS (EM9305)
- **Phone (Even.app)**: LC3 decode → VAD → ASR → command dispatch → response rendering on glasses

The glasses themselves do **not** run the AI state machine — they are an audio input/display output peripheral. All intelligence is phone-side.

---

## 18. R1 Ring Extended System

### Ring System Capabilities (from Even.app)

| Feature | Evidence | Status |
|---|---|---|
| **System Info** | Ring system info queries | Active |
| **Device SN** | `deviceSn` management | Active |
| **NV Recovery** | `BleRing1SystemNvRecover`, `RingNvRecoverLogType`, dedicated debug card | Diagnostic |
| **Algo Key** | `getAlgoKeyStatus`, `setAlgoKey` — **GoMore** health analytics licensing (third-party, `/v2/g/health/get_pkey`) | Active |
| **Wear Status** | `getWearStatus`, `wearStatus`, `wearStatus2` | Active |
| **File Transfer** | Ring file transfer capability | Active |
| **Package ACK** | Ring package acknowledgment protocol | Active |
| **Hand Selection** | Left/right hand configuration page | Active |
| **Low Power Mode** | Reduces BLE connection strength, ring auto-reboots | User-configurable |
| **Camera** | Photo capture capability | `take_photo` voice intent in BERT model |
| **Data Relay** | Phone↔Ring data via G2 glasses as relay | `UX_RING_DATA_RELAY_ID`, `UX_RING_ROW_DATA_ID` |
| **Ring Broadcast** | Glasses open ring discovery | `BleG2CmdProtoRingExt\|openRingBroadcast` |
| **Hand Switch** | Left/right hand config | `BleG2CmdProtoRingExt\|switchRingHand` |

### Ring Health Data Pipeline

The R1 Ring collects extensive health data:

| Data Type | App References |
|---|---|
| Heart Rate | `HealthSingleData`, HR monitoring |
| SpO2 | Blood oxygen saturation |
| Temperature | Body temperature sensing |
| Steps | Step counting / pedometer |
| Sleep Stages | Sleep quality tracking |
| Wear Detection | On-wrist detection sensor |
| Daily Health | `daily_health_factory` — aggregate daily health report |

### Ring Protobuf Schema

**RingDataPackage** (outer envelope):
```
RingDataPackage {
  eRingCommandId command_id = 1;  // 1=EVENT, 2=RAW_DATA
  bytes magic_random = 2;
  oneof payload {
    RingEvent event = 3;
    RingRawData raw_data = 4;
  }
}
```

**RingEvent** (command_id=1):
```
RingEvent {
  string ring_mac = 1;
  eRingEvent event_id = 2;       // BLE_ADV=1
  bytes event_param = 3;
  int32 error_code = 4;
}
```

**RingRawData** (command_id=2, 17 fields with paired timestamps):
```
RingRawData {
  int64 battery = 1;
  int32 charge_states = 2;
  int32 hr = 3;                   // Heart rate (BPM)
  int64 hr_timestamp = 4;
  int32 spo2 = 5;                 // Blood oxygen (%)
  int64 spo2_timestamp = 6;
  int32 hrv = 7;                  // Heart rate variability (ms)
  int64 hrv_timestamp = 8;
  int32 temp = 9;                 // Temperature
  int64 temp_timestamp = 10;
  int32 act_kcal = 11;            // Active calories
  int64 act_kcal_timestamp = 12;
  int32 all_kcal = 13;            // Total calories
  int64 all_kcal_timestamp = 14;
  int32 steps = 15;
  int64 steps_timestamp = 16;
  int32 wear_status = 17;
}
```

### R1 Gesture → G2 Forwarding Table

When the R1 Ring sends a gesture, the G2 glasses (or phone) translate it to the corresponding NUS command:

| Ring Gesture | Ring Bytes | → NUS Command | NUS Bytes |
|---|---|---|---|
| Single Tap | `FF 04 01` | Tap | `F5 01` |
| Double Tap | `FF 04 02` | Double Tap | `F5 00` |
| Hold | `FF 03 01` | Long Press | `F5 17` |
| Swipe Forward | `FF 05 01` | Slide Forward | `F5 02` |
| Swipe Back | `FF 05 02` | Slide Back | `F5 03` |

**Swipe direction heuristic**: `param ≤ 0x01` → forward, `param > 0x01` → backward (derived from BTSnoop captures; not fully confirmed).

**Hold duration indicator**: Gesture parameter `0x20` observed during hold events, meaning unknown.

### R1 Config Value Format

Read config returns 4 bytes: `[type][major][minor][patch]` — e.g., `02010101` = v1.1.1.

**R1 ATT Handle Map** (from BLE capture):

| Handle | Purpose | Notes |
|---|---|---|
| 0x0020 | Battery Level (notify) | |
| 0x0021 | Battery CCCD | Write `0100` to enable |
| 0x0024 | Gesture Events (notify) | |
| 0x0025 | Gesture CCCD | Write `0100` to enable |
| 0x0028 | State/Menu Toggle (notify) | 0x01=Ready/Active, 0x00=Menu/Selection |
| 0x0029 | State CCCD | Write `0100` to enable |
| 0x002C | Config/Version (read) | |
| 0x0030 | Config Commands (write) | |

**Connection sequence timing** (from BLE capture):
```
t+23.74s  Enable battery notifications (0x0021 ← 0100)
t+23.80s  Battery: 100% (0x64)
t+23.81s  Enable gesture notifications (0x0025 ← 0100)
t+23.87s  Read config: 02010101 (v1.1.1)
t+23.96s  Write config: 0xFC (init command)
t+24.02s  Enable state notifications (0x0029 ← 0100)
t+24.08s  State: 0x01 (ready)
t+24.09s  Write config: 0x11 (activate)
t+24.42s  First gesture event
```

**Scanning name prefixes** (fallback scan when UUID not advertised): `Even Ring`, `R1`, `EVEN_RING`, `EvenRing`

**Health Debug Pages** (10 pages in Even.app debug section):
1. `HealthHighlightDebugPage` — health highlights
2. `HealthSyncLogDebugPage` — sync log viewer
3. `HealthPointDebugPage` — health data points
4. `HealthWindowDebugPage` — health time windows
5. `Health1970OffsetDebugPage` — epoch offset debugging
6. `HealthPendingUploadDebugPage` — queued uploads
7. `HealthProductivityDebugPage` — productivity metrics
8. `HealthRawDebugPage` — raw health data viewer
9. `HealthPostRequestDebugPage` — API POST debugging
10. `HealthWindowDebugPage` — health data windowing

---

## 19. Factory, Calibration & Debug Features

### Factory/Calibration Modes

| Feature | Function | Evidence |
|---|---|---|
| **Factory Reset** | `RestoreFactory` — full device reset | `restoreFactory`, `set:restoreFactory`, `BleG2CmdProtoDeviceSettingsExt\|restoreFactory` |
| **Quick Restart** | `quickRestart` — reboot glasses without factory reset | `BleG2CmdProtoDeviceSettingsExt` |
| **Brightness Calibration** | Per-eye brightness calibration | `BrightnessCalibrationSettingsController`, `setBrightnessCalibration`, `_assembleDeviceBrightnessCalibration` |
| **Zero Position Recalibration** | Custom head angle recalibration | `RecalibrateZeroPositionController`, `startCustomAngle`, `stopCustomAngle`, `assembleRecalibrateTipsCard` |
| **Controlled Shutdown** | Firmware shutdown command | `ResponseShutDownCmd` (protobuf @2397181980) |
| **Wear Detection Toggle** | Enable/disable wear sensor | `setWearDetection`, `Wear_Detection_Setting`, `wearDetectionSwitch` |
| **Anti-Shake** | Display stabilization toggle | `DEVICE_ANTI_SHAKE_ENABLE` in g2_settingCommandId |
| **Wake-Up Angle** | Configurable tilt angle for display wake | `DEVICE_WAKEUP_ANGLE` |
| **Screen-Off Interval** | Auto screen-off timer | `requestScreenOffInterval`, `updateScreenOffInterval` |
| **Gesture Control** | Per-gesture action mapping | `setGestureControlList`, `APP_Send_Gesture_Control_List` |
| **Dominant Hand** | Left/right hand config | `APP_Send_Dominant_Hand` |
| **Silent Mode** | Notification mute | `setSilentMode` |
| **Pipe Channel** | Dynamic BLE characteristic routing | `selectPipeChannel` — switches control vs file channel |
| **Ring Connect** | Connect R1 ring through glasses | `connectRing` on `BleG2CmdProtoDeviceSettingsExt` |

### Device Management Commands (via BleG2CmdProtoDeviceSettingsExt)

| Command | Purpose |
|---|---|
| `createTimeSyncCommand` | Time synchronization |
| `sendHeartbeat` | Auth-level heartbeat |
| `startPair` / `unpair` | Pairing management |
| `disconnect` | Graceful disconnect |
| `quickRestart` | Reboot glasses |
| `restoreFactory` | Factory reset |
| `sendFile` / `receiveFile` | File transfer initiation |
| `selectPipeChannel` | Switch BLE pipe (control ↔ file) |
| `connectRing` | Ring discovery through glasses |

### Debug Page (Even.app hidden features)

The Even.app contains an extensive debug section at `pages/debug/` with these sub-widgets:

| Debug Card/Page | Purpose |
|---|---|
| `ota_settings_card` | OTA firmware update configuration |
| `converse_settings_card` | Conversate protocol settings |
| `translation_settings_card` | Translation feature settings |
| `ring_nv_recover_card` | Ring non-volatile memory recovery |
| `quick_list_test_card` | QuickList feature testing |
| `api_mock_card` | API endpoint mocking for testing |
| `base_settings_card` | Base device settings |
| `share_test_card` | Share/export testing |
| `scanner_connect_device_page` | Manual BLE scanner/connect |
| 10x Health debug pages | Health data inspection (see §18) |

### Settings Controllers

| Controller | Purpose |
|---|---|
| `DisplaySettingsController` | Display configuration |
| `MotionSettingsController` | Motion/gesture sensitivity |
| `AdvancedSettingsController` | Advanced device options |
| `TranslationSettingsController` | Translation language pairs |
| `BrightnessCalibrationSettingsController` | Per-eye brightness |

### ProtoBaseSettings Complete Method List

The `ProtoBaseSettings` class provides the full device configuration interface:

**Write methods**: `setBrightness`, `setBrightnessCalibration`, `setBrightnessAuto`, `setGestureControlList`, `setSilentMode`, `setWearDetection`, `setOnBoardingStartUp`, `setOnBoardingStart`, `setOnBoardingEnd`, `setGlassGridDistance`, `setGlassGridHeight`, `headUpSetting`, `requestScreenOffInterval`, `updateScreenOffInterval`, `sendSysLanguageChangeEvent`

**Read methods**: `getGlassesConfig`, `getGlassesIsWear`, `getGlassesCaseInfo`, `getOnGlassesWear`, `getBoardingIsHeadup`

**Notification whitelist**: Pre-loaded with major app bundle IDs: `com.even.sg`, `com.whatsapp`, `com.facebook.orca`, `com.facebook.Facebook`, `com.facebook.Messenger`, `com.burbn.instagram`, `com.instagram.barcelona` (Threads), `com.twitter.android`, `tv.twitch.android.app`. File path: `user/notify_whitelist.json`. Controlled via `whitelistCtrl` / `whitelistDisable` / `NOTIFICATION_WHITELIST_CTRL`.

---

## 20. Even.app Plugin Ecosystem

The Even.app is a Flutter application with 53 registered native iOS plugins (from `even_runner` binary):

### Even-Proprietary Plugins (8)

| Plugin | Purpose |
|---|---|
| `EvenConnectPlugin` | G2 BLE protocol + protobuf communication |
| `EvenCorePlugin` | Core framework / shared utilities |
| `EvenUiPlugin` | Custom UI components |
| `EvenLoggerPlugin` | Logging infrastructure |
| `ConversatePlugin` | Conversate/ASR feature |
| `DashboardPlugin` | Dashboard widget system |
| `TelepromptPlugin` | Teleprompter feature |
| `TranslatePlugin` | Translation feature |
| `NavigatePlugin` | Navigation (wraps Mapbox + AMap) |
| `AppSettingsPlugin` | App settings bridge |

### EZW (Even Zhiwei) Native Plugins (7)

| Plugin | Purpose |
|---|---|
| `FlutterEzwAsrPlugin` | Speech recognition engine |
| `FlutterEzwAudioPlugin` | Audio processing pipeline |
| `FlutterEzwBlePlugin` | BLE connection management |
| `FlutterEzwHealthAlgorithmPlugin` | Health data algorithms (R1 ring) |
| `FlutterEzwLc3Plugin` | LC3 codec (BLE audio) |
| `FlutterEzwUtilsPlugin` | Utility functions |
| `FlutterEzwUtopPlugin` | Unknown (possibly user tracking/ops) |

### Third-Party Plugins (36)

| Plugin | Purpose |
|---|---|
| `McumgrFlutterPlugin` | Nordic MCUmgr / R1 Ring DFU |
| `NordicDfuPlugin` | Nordic DFU / G2 bootloader |
| `AudioSessionPlugin` | iOS audio session management |
| `TaudioPlugin` | Audio recording/playback |
| `RecordIosPlugin` | iOS audio recording (8 codec formats) |
| `ConnectivityPlusPlugin` | Network connectivity |
| `FPPDeviceInfoPlusPlugin` | Device info queries |
| `DeviceCalendarPlugin` | Calendar access (for dashboard) |
| `FilePickerPlugin` | File picker |
| `FirebaseAnalyticsPlugin` | Analytics |
| `FLTFirebaseCorePlugin` | Firebase core |
| `FLTFirebaseCrashlyticsPlugin` | Crash reporting |
| `FLTFirebaseMessagingPlugin` | Push notifications |
| `PathProviderPlugin` | File path utilities |
| `PermissionHandlerPlugin` | Permission management |
| `GeocodingPlugin` | Address → coordinates |
| `GeolocatorPlugin` | GPS location |
| `WebViewFlutterPlugin` | In-app web views |
| `FLTPDFViewFlutterPlugin` | PDF rendering |
| `ReadPdfTextPlugin` | PDF text extraction |
| `SqflitePlugin` | SQLite database |
| `Sqlite3FlutterLibsPlugin` | SQLite native libs |
| `MMKVPlugin` | Key-value storage (WeChat) |
| `FLTImageCropperPlugin` | Image cropping |
| `FLTImagePickerPlugin` | Image picking |
| `SwiftFlutterQrPlusPlugin` | QR code scanning |
| `FlutterKeyboardVisibilityPlugin` | Keyboard detection |
| `FlutterLocalNotificationsPlugin` | Local notifications |
| `FlutterNewBadgerPlugin` | App badge management |
| `FlutterTimezonePlugin` | Timezone utilities |
| `FluttertoastPlugin` | Toast messages |
| `KeyboardHeightPlugin` | Keyboard height tracking |
| `URLLauncherPlugin` | URL opening |
| `FVPVideoPlayerPlugin` | Video playback |
| `VolumeControllerPlugin` | Volume control |
| `FPPSharePlusPlugin` | Share sheet |

**Build environment**: Compiled on macOS by user `niuma` using Xcode DerivedData, with Mapbox Navigation iOS and Google Data Transport as Swift/ObjC package dependencies.

---

## 21. Cloud API & Security

### API Domains

| Domain | Purpose |
|---|---|
| `api2.evenreal.co` | Production REST API |
| `cdn.evenreal.co` | CDN (firmware, assets) |
| `cdn2.evenreal.co` | CDN (legal documents) |
| `api2.ev3n.co` | Staging/pre-production API |
| `pre-g2.evenreal.co` | Pre-production environment |
| `http://192.168.2.113:8888` | Local debug server (hardcoded in app) |

### REST API Endpoint Map (50+ endpoints, all under `/v2/g/`)

**Auth/Account**: `register`, `login`, `check_reg`, `check_password`, `reset_passwd`, `send_code`, `pre_check_code`, `account_del`, `account_logout`

**User**: `user_info`, `user_settings`, `set_profile`, `upload_avatar`, `set_user_prefs`, `get_user_prefs`, `set_on_boarded`, `update_set2`

**Device**: `bind_device`, `unbind_device`, `list_devices`, `check_bind2`, `set_device_remark`, `unbind_terminal`, `update_glasses_settings`, `get_nv`, `upload_nv`

**Firmware**: `check_firmware`, `check_latest_firmware`, `check_app`, `update_ios_app_list`, `get_ios_app_list`

**Health**: `health/push`, `health/export`, `health/query_window`, `health/batch_query_window`, `health/get_latest_data`, `health/get_info`, `health/update_info`, `health/get_pkey` (GoMore analytics key)

**AI/Conversate**: `jarvis/chat`, `jarvis/conversate/list`, `jarvis/conversate/detail`, `jarvis/conversate/messages2`, `jarvis/conversate/ws` (WebSocket), `jarvis/conversate/update`, `jarvis/conversate/finish`, `jarvis/conversate/remove`, `jarvis/message/list`, `jarvis/message/sentiment` (sentiment analysis)

**Translate**: `translate_create`, `translate_get`, `translate_update`, `translate_delete`, `translate_ai_summary` (AI summary), `asr_sconf`

**Stocks**: `stock_intraday`, `stock_tickers`, `stock_favorite_list`, `stock_favorite_create`, `stock_favorite_update`, `stock_favorite_del`

**News**: `news_list`, `news_categories`, `news_sources`, `news_favorites_settings`, `news_favorites_settings_save`

**Notifications**: `notify_list`, `inbox/list2`, `inbox/delete`, `inbox/mark_as_read`, `inbox/unread_count`

**Other**: `func_conf`, `get_privacy_urls`, `filelogs/feedback`

### Encryption & Security

| Component | Technology | Details |
|---|---|---|
| **BLE Data** | AES-256-CBC/PKCS7 | `encryptAesCbc` with 32-byte (256-bit) key; PointyCastle engine |
| **DFU Signing** | ECDSA P-256 (secp256r1) | 64-byte public key in bootloader; `ECDSASigner` verification |
| **Local Storage** | AES (Hive) | `hive_encryption_key` for on-device data |
| **Display Stream** | JBD LFSR scrambler (hardware) | 0x6402 frames: LFSR-scrambled sensor telemetry from JBD display controller silicon. NOT software encryption. Polynomial similar to MIPI DSI LFSR but JBD-proprietary. For EMI reduction + IP protection, not security |
| **CRC32C** | Non-reflected MSB-first | Poly 0x1EDC6F41, used for file transfer checksums |
| **CRC-16/CCITT** | Init 0xFFFF, poly 0x1021 | G2 protocol packet integrity (payload only) |
| **API Auth** | Token-based | `login_token` with `tokenExpired` expiry management |
| **HTTP Tracing** | Custom header | `evenrealities-trace-id` for request correlation |

**Cipher library** (PointyCastle): CBC, CCM, GCM, OFB, CFB, CTR, SIC, ECB, IGE, GCTR, Salsa20, ChaCha20, ChaCha20-Poly1305, RC4, EAX — but primary usage is AES-256-CBC/PKCS7.

**App identity**: `com.even.sg` (bundle ID), URL scheme `evenG2://`

---

## 22. Known Unknowns & Future Work

### Missing / Unknown Components
- **R1 Ring firmware** — downloaded from CDN on demand, not in extracted bundle
- **R1 Ring exact SoC variant** — nRF52832 vs nRF52833 vs nRF52840, not yet determined
- **Inter-eye communication protocol** — wired link confirmed (UART/I2C, HIGH confidence), but baud rate, framing, and command structure unknown without physical teardown
- **Battery capacity (mAh)** — unknown despite charger (BQ25180) and fuel gauge (BQ27427) IC identification
- **Compass/magnetometer IC** — only sensor IC not yet identified from firmware strings
- **S201 model variant** — purpose unknown (next-gen? alternate SKU? regional variant?)
- **`imu7` designation** — meaning unknown (7-axis? model number? config parameter?)
- **JBD LFSR polynomial** — display controller scrambler is JBD-proprietary (similar to MIPI DSI LFSR); extracting requires JBD datasheet or captured data reverse-engineering
- **EvenAI HEARTBEAT `f11={f2=8}`** — likely AI session lifecycle state; `HeartBeatPacket` has distinct request/send paths
- **TWIM1 I2C bus device addresses** — register 0x40004000 confirmed in bootloader but connected peripheral addresses unknown
- **CY8C4046FNI GPIO mapping** — touch IC confirmed, but pin assignments unknown
- **`FlutterEzwUtopPlugin`** — Dart layer is active (EvenBusiness/Config/ConfigProvider classes), likely enterprise tier; full purpose unclear
- **Display pixel pitch** — physical PPI unknown despite 576x288 canvas confirmation
- **DisplayTrigger f3.f1=67** — constant across all probes, meaning unknown (display state? JBD register value?)
- **Device info f4.f2** — likely |RSSI| in dBm (rapid variation rules out battery), needs CoreBluetooth correlation
- **Even.app ECDSA key** — X=`7a7de304...`, Y=`553442c9...` — may be DFU signing public key, cloud API key, or R1 Ring DFU key

### Unexplored BLE Characteristics
- `0x1001` — unknown service (possibly OTA or bidirectional pipe)
- `8E400001-F315-4F60-9FB8-838830DAEA50` — variant DFU service UUID (not `8EC9`), role unknown

Note: `0x5450`, `0x6450`, `0x7450` were previously listed here but are now identified as GATT service declaration UUIDs — parent services for the control, display, and file pipe pairs respectively (see §8).

### Unimplemented Protocol Modules (14 of 27)

We implement 10 modules; 3 are partial; 14 remain unimplemented. All 14 now have detailed protocol descriptions in §14 above. Key unknowns:
- **Numeric BLE service IDs** for QuickList, Logger, Menu — only 3 truly unknown service IDs remain. Health (inferred 0x03-20) and Transcribe (inferred 0x05-20) have MEDIUM-confidence inferences. Onboarding, Module Configure, Sync Info, and Glasses Case all confirmed on 0x0D-00. Translate confirmed on 0x07-xx. The `service_id_def.pbenum.dart` master mapping is compiled into AOT binary and definitive extraction requires decompilation or traffic capture
- **OTA wire protocol** — `EvenOtaUpgradeCmd` uses custom byte encoding (`.fromBytes`), not protobuf
- **L2CAP channel** — CBL2CAPChannel delegate present but usage context unknown (OTA? file transfer?)

### Resolved (previously unknown, now identified)

| Item | Resolution |
|---|---|
| ~~Application firmware~~ | Obtained from CDN — Apollo510b main application (`ota_s200_firmware_ota.bin`, 3.1 MB). See [s200-firmware-ota.md](s200-firmware-ota.md) |
| ~~Glasses Case role~~ | Separate product communicating via G2, has own protobuf module (@1415496902) |
| ~~R1 "Dock"~~ | Is the R1 Charger (2BFKR-R1C), a passive charging cradle with no firmware |
| ~~64-byte key blob~~ | Standard P-256 generator point (Gx, Gy) from nrf_cc310 library crypto constants — NOT a custom DFU key. Real DFU key loaded from settings page (0xFF000) at runtime |
| ~~ALWAY bootloader purpose~~ | Factory/recovery — missing nrf_dfu_settings_t, always enters DFU |
| ~~SoftDevice SRAM boundary~~ | 0x200059C4 (not estimated 0x2000C000), leaving ~233 KB for application |
| ~~CryptoCell presence~~ | Confirmed nRF52840 in DFU bootloader via CryptoCell-310 ISR in vector table (applies to DFU path, not Apollo510b runtime) |
| ~~Sensor inventory~~ | ALS, compass (with calibration flow), IMU (imu7), wear detection — all confirmed |
| ~~Dashboard widget count~~ | 6 protobuf widget types (News, Schedule, Stock, Health, QuickList, Status), not 29 |
| ~~Dashboard protocol~~ | Full bidirectional: 6 send functions, DashboardMainPageState, auto-close timer |
| ~~Menu protocol~~ | Overlay menu with 7 OS_RESPONSE packet types, `Menu_Item_Ctx` items |
| ~~QuickList protocol~~ | Note/bookmark system with UID-based paging, EvenAI "save to quicklist" skill |
| ~~Health protocol~~ | 8 data types (HR, SpO2, temp, steps, cal, sleep, productivity, activity) |
| ~~Glasses Case protocol~~ | Minimal: `getGlassesCaseInfo` query → `GlassesCaseInfo` (battery, charging, wear) |
| ~~Onboarding protocol~~ | 7-state FSM with 8 tutorial videos, head-up calibration |
| ~~Sync Info protocol~~ | Cloud NV backup/restore via `/v2/g/upload_nv` and `/v2/g/get_nv` |
| ~~Logger protocol~~ | Live log streaming with level/category filters + file management |
| ~~OTA Transmit protocol~~ | 5-command flow: START → INFORMATION → FILE → RESULT_CHECK → NOTIFY |
| ~~Transcribe protocol~~ | Display-only ASR (4 commands), speaker diarization, Soniox + Azure backends |
| ~~Translate protocol~~ | One-way + two-way modes, pause/resume, cloud AI summary |
| ~~Module Configure~~ | Meta-config wrapping dashboard_general_setting + system_general_setting |
| ~~Navigation API~~ | 19 native Pigeon methods via `even_navigate`, Mapbox + AMap dual providers |
| ~~Audio codec formats~~ | 8 supported: aacLc, aacEld, aacHe, amrNb, amrWb, opus, flac, pcm16bits |
| ~~Buttonless DFU variants~~ | 3: experimental, withoutBonds, withBonds (all in `even_runner`) |
| ~~EvenAI skill IDs~~ | 8 voice-triggered skills (brightness, navigate, translate, converse, etc.) |
| ~~Conversate command set~~ | 13 commands + 5 tag types (QUESTION, SUGGEST, KNOWLEDGE, PEOPLEWIKI) |
| ~~Types 11-19 on 0x07-20~~ | ALL respond with COMM_RSP f12={f1=8} (~90-170ms); test callback had routing bug |

## 23. OTA Firmware Binary Analysis

Production firmware was obtained from Even's CDN via their `check_latest_firmware` API. The detailed binary format documentation has been moved to dedicated per-component docs.

> **Cross-reference**: Per-component binary structure is now documented in dedicated files:
> - [firmware-files.md](firmware-files.md) — EVENOTA container format, entry layout, checksums
> - [s200-firmware-ota.md](s200-firmware-ota.md) — Apollo510b main application preamble
> - [s200-bootloader.md](s200-bootloader.md) — Apollo510b bootloader vector table, VTOR handoff
> - [ble-em9305.md](ble-em9305.md) — EM9305 segmented patch header
> - [codec-gx8002b.md](codec-gx8002b.md) — GX8002B FWPK dual-segment, BINH blocks
> - [touch-cy8c4046fni.md](touch-cy8c4046fni.md) — CY8C4046FNI FWPK + CRC32C
> - [box-case-mcu.md](box-case-mcu.md) — Case MCU EVEN wrapper + BE checksum

### 23.1 Firmware Acquisition

```
GET https://api2.evenreal.co/v2/g/check_latest_firmware
→ subPath: /firmware/650176717d1f30ef684e5f812500903c.bin
→ Download: https://cdn.evenreal.co/firmware/650176717d1f30ef684e5f812500903c.bin
→ Size: 3,958,551 bytes, MD5: 650176717d1f30ef684e5f812500903c
```

API auth notes:
- `sign` header is NOT path-bound — any valid sign works on any endpoint
- CDN requires NO auth — firmware URL is the only secret
- Required headers: `sign`, `token`, `common`, `region`, `request-id`

### 23.2 Artifact Fingerprints (v2.0.7.16)

First-pass inventory for every extracted artifact (`captures/firmware/g2_extracted/*`):

| Artifact | Size (bytes) | MD5 | SHA-256 | Entropy (bits/byte) | Magic (first 8 bytes) |
|---|---:|---|---|---:|---|
| `firmware_ble_em9305.bin` | 211,948 | `af598d1e9a6dab7a3145d92a1f1bd2c5` | `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9` | 7.0698 | `00 02 04 04 70 3B 03 00` |
| `firmware_box.bin` | 55,296 | `4bd641a15114943b35724a212a8408a9` | `d290f2b6899e69288b2b07b2d52471f193a4bf065f3eefe664c5a89aeadecb52` | 6.8091 | `45 56 45 4E 01 02 36 00` |
| `firmware_codec.bin` | 319,372 | `3222dabe822aa388223171e2fb8802de` | `1c1462aff542d41429203e3a5d4cd53696f973133203cc44b9ae01523a551d03` | 7.0690 | `46 57 50 4B 00 02 00 00` (`FWPK`) |
| `firmware_touch.bin` | 34,080 | `34a7ce2f99241b8e61db4e76b413a09f` | `35c49f3040fd75e251a2957d746f6ebc7c8a8401741f4d2ca8c33bffb3e0b823` | 6.7568 | `46 57 50 4B 00 06 00 02` (`FWPK`) |
| `ota_s200_bootloader.bin` | 147,727 | `d45c5c3ca6d1d6bbfb7e4dfb28cde9c0` | `5a5eb1d24160161e3fe5a020becd1c36ac68a59bdf27b491f47842555762d139` | 6.7806 | `00 FB 07 20 CF 24 43 00` |
| `ota_s200_firmware_ota.bin` | 3,189,184 | `bea21ef8c130eaad9ab04497e56a0863` | `50f48eae3e031885086fa85d5e6f36d3d36582674adf5c6ec1d50da502f029eb` | 6.3995 | `C0 A9 30 04 3F 38 A2 7B` |
| `s200_firmware_raw.bin` | 3,189,152 | `03cb1675b3bcd43110344ad26fe66a7b` | `3bd6e092fb5b3aa6dc35a15a9e380fd7663f97816c630f02fabab58994db1fb4` | 6.3996 | `00 FB 07 20 77 97 5C 00` |

Notes:
- `file(1)` misclassifies `firmware_ble_em9305.bin` as IA64 COFF; direct header parsing shows a deterministic EM9305 patch container (see [ble-em9305.md](ble-em9305.md)).
- Full reproducible inventory is saved at `captures/firmware/analysis/2026-03-03-g2-extracted-wave.md`.




### 23.3 Cross-Version Validation and Firmware API Sweep

Re-authenticated probing (Wave 6) used:
- fresh `token` from replayed `POST /v2/g/login` (`code=0`)
- `common/sign/request-id` profile captured from successful `GET /v2/g/list_devices`

With that profile, a 21-point sweep of `common.versionName` (`0.0.1` through `3.0.0`) against `GET /v2/g/check_latest_firmware` returned `code=0` for every probe and produced the following threshold buckets:

| Request `common.versionName` range | Returned FW version | `minAppVer` | CDN subPath |
|---|---|---|---|
| `0.0.1 .. 2.0.2` | `2.0.1.14` | `0.0.0` | `/firmware/09fe9c0df7b14385c023bc35a364b3a9.bin` |
| `2.0.3 .. 2.0.4` | `2.0.3.20` | `2.0.3` | `/firmware/57201a6e7cd6dadeee1bdb8f6ed98606.bin` |
| `2.0.5` | `2.0.5.12` | `2.0.5` | `/firmware/53486f03b825cb22d13e769187b46656.bin` |
| `2.0.6` | `2.0.6.14` | `2.0.6` | `/firmware/0c9f9ca58785547278a5103bc6ae7a09.bin` |
| `2.0.7 .. 3.0.0` | `2.0.7.16` | `2.0.7` | `/firmware/650176717d1f30ef684e5f812500903c.bin` |

Sweep evidence artifact:
- `captures/firmware/analysis/2026-03-03-api-wave6-threshold-sweep.json`

Downloaded packages already validated at binary/checksum-structure level:
- `captures/firmware/versions/v2.0.6.14/0c9f9ca58785547278a5103bc6ae7a09.bin`
- `captures/firmware/versions/v2.0.5.12/53486f03b825cb22d13e769187b46656.bin`
- `captures/firmware/versions/v2.0.3.20/57201a6e7cd6dadeee1bdb8f6ed98606.bin`
- `captures/firmware/versions/v2.0.1.14/09fe9c0df7b14385c023bc35a364b3a9.bin`

Cross-version rule stability (validated package set: `2.0.1.14`, `2.0.3.20`, `2.0.5.12`, `2.0.6.14`, `2.0.7.16`):
- EVENOTA TOC/sub-header checksum rule remains valid for all entries:
  - `crc32c_msb(payload) == toc_chk == sub_chk` for IDs 1..6.
- Box `EVEN` wrapper checksum rule remains valid:
  - `sum_be32(file[0x20 : 0x20 + len_be]) == chk_be`.
- Codec BINH layout remains stable:
  - two BINH blocks at the same segment offsets (`0x0`, `0x2D970`),
  - `+0x08 == 0x200` (`stage1_size`) and `+0x10 == 0x3000` (`stage2_size`) unchanged.

`check_firmware` status in same authenticated session:
- `GET /v2/g/check_firmware` and candidate parameter variants still return `code=1401` (`Params error`).
- `list_devices.data.devices=[]` (no bound glasses in this account context), so real `device_sn`/per-eye firmware tuples are still unavailable for contract closure.

> **Hardware BOM**: Complete hardware component inventory with part numbers, interfaces, and driver files is in [g2-glasses.md](../devices/g2-glasses.md).

### 23.4 AT Command Debug Interface

Firmware includes production/debug serial console via AT commands:

| Command | Description |
|---------|-------------|
| `AT^INFO` | System information |
| `AT^PSN` | Product serial number |
| `AT^RESET` | System reset |
| `AT^BLE` | BLE general |
| `AT^BLES` | BLE bondable/disbondable/disconnect/reset9305/hostreset/appdb |
| `AT^BLEMC` | BLE master connect/disconnect |
| `AT^BLEM` | BLE master |
| `AT^BLEADV` | BLE advertising control |
| `AT^BLEC` | BLE connect |
| `AT^BLER` | BLE read |
| `AT^EM9305` | EM9305 BLE radio control |
| `AT^CLEANBOND` | Clean BLE bond info |
| `AT^IMU` | IMU (open/close/rawdata/rnv/wnv/mode/calib) |
| `AT^ALS` | Ambient light sensor |
| `AT^BRIGHTNESS` | Brightness control |
| `AT^SCRN` | Screen settings (height) |
| `AT^BUZZER` | Buzzer control (play by type) |
| `AT^AUDIO` | Audio control (DMIC on/off) |
| `AT^NUS` | Nordic UART Service |
| `AT^TP` | Teleprompter |
| `AT^LOGTYPE` | Log type configuration |
| `AT^LS` | List files (LittleFS) |
| `AT^MKDIR` | Create directory |
| `AT^RM` | Remove file |

### 23.5 Firmware Source Tree

```
s200_ap510b_iar/
├── app/gui/               # UI pages (LVGL v9.3)
│   ├── conversate/        # FSM + UI + data + tags + timer
│   ├── EvenAI/            # Animation + timer + text_stream
│   ├── EvenHub/           # Data parser + main + UI + containers
│   ├── dashboard/         # News, stock, calendar, page_state_sync
│   ├── navigation/        # UI + data_handler + main
│   ├── teleprompt/        # FSM + UI + data + timer
│   ├── translate/         # FSM + UI + data
│   ├── health/            # Data manager + UI
│   ├── quicklist/         # Data manager + UI
│   ├── menu/, setting/, onboarding/, MessageNotify/
│   ├── common/, anim/, logger/, sync_info/, system/
│   └── AgingTest/, ProductionTest/, PdtGrayScreen/
├── app/ux/                # UX behaviors
│   └── ux_battery_sync, ux_production, ux_settings, ux_system, ux_wear_detect
├── driver/                # Hardware drivers
│   ├── buzzer/, chg/ (BQ25180+BQ27427), codec/ (GX8002B)
│   ├── flash/ (MX25U25643G), hal/ (I2C), pdm/, rtc/
│   ├── sensor/ (ALS=OPT3007, IMU=ICM-45608)
│   ├── touch/ (CY8C4046FNI), uled/ (JBD4010+A6NG), wdt/
├── framework/             # Core
│   ├── fw_event_loop/, page_manager/
│   └── sync/ (display_thread, uart_sync, thread_pool)
├── platform/
│   ├── audio/ (manager, algo, codec_host, codec_dfu, codec_porting)
│   ├── ble/ (central, peripheral, discovery, connect_params, peer_mgr)
│   │   └── profiles/ (ancc, efs, ess, eus, gatt, nus, ota, ring)
│   ├── protocols/
│   │   ├── pb_service_* (conversate, dev_config, even_ai, glasses_case,
│   │   │   health, notification, onboarding, quicklist, ring, setting,
│   │   │   teleprompt, translate)
│   │   ├── efs_service/ (Even File Service)
│   │   ├── ota_service/ (OTA service + transport)
│   │   └── transport_protocol/
│   ├── service/ (DFU, eAT, evenAI, flashDB/KV+NV, box_detect, settings, time, ...)
│   └── threads/ (audio, ble_msgrx, ble_msgtx, ble_production, ble_wsf,
│                  evenai, input, manager, notification, ring)
├── product/s200/ (board_config, main, redirect, rtos)
├── third_party/
│   ├── cordio/ (BLE host stack)
│   ├── EasyLogger-master/ (logging)
│   ├── littlefs/ (with MX25U port)
│   ├── lvgl_v9.3/ (LVGL + Ambiq porting + FreeType + demo)
│   ├── TinyFrame/ (codec protocol)
│   ├── ringBuffer/, tlsf/ (memory allocator)
└── utils/ (assert, error_check)
```

### 23.6 Firmware Module Tags

Complete list of `[module]` tags found in firmware debug logging:

```
[ble.comm]           [ble.disc]           [ble.dm_conn]
[ble.dm_conn_master] [ble.dm_conn_master_leg] [ble.dm_conn_sm]
[ble.gatt]           [ble.master]         [ble.mgr]
[ble.msgrx]          [ble.msgtx]          [ble.param]
[ble.ring]           [ble.smpdb]          [ble.ui]
[ble.ancc]

[pb.conversate]      [pb.devc]            [pb.evenai]
[pb.glasses_case]    [pb.health]          [pb.notif]
[pb.onboarding]      [pb.quicklist]       [pb.ring]
[pb.ser]             [pb.teleprompt]      [pb.translate]
[pb_service_setting]

[codec.dfu]          [codec.host]         [codec.porting]
[conversate]         [conversate.data]    [conversate.fsm]
[conversate.tag]     [conversate.timer]   [conversate.ui]
[dashboard]          [dashboard.stock]    [dashboard_data_process]
[dashborad.news]     [dashborad.ui]
[display]            [display_thread]
[drv.audio.codec]    [drv.audio.pdm]      [drv.audio.pdm.production]
[drv.buzzer]         [drv.norflash]       [drv.opt.r]
[drv.rtc]            [drv.touch]          [drv.touchdfu]
[evenhub.data_parser] [evenhub.main]      [evenhub.ui]
[generic.animation]  [menu.page]
[navigation.datahandler] [navigation.main] [navigation.ui]
[npmx_driver]        [ota.service]        [ota.tran]
[sensor_als]         [sensor_hub]         [sensor_imu]
[service.audio.manager] [service.evenAI]  [service.settings]
[setting]            [srv.em9305]         [srv.time]
[srv_universal_setting]
[sync.module.api]    [sync.module.framework] [sync.module.uart]
[sync_info.main]
[task.ble.wsf]       [task.ble_production] [task.displaydrvmgr]
[task.evenai]        [task.manager]       [task.notif]
[task.ring]
[teleprompt]         [teleprompt.data]    [teleprompt.fsm]
[teleprompt.timer]   [teleprompt.ui]
[touch.ges]
[common_image_container] [common_list_container] [common_text_container]
```

### 23.7 Key Firmware Insights

1. **Inter-eye sync** uses wired UART: `sync.module.uart`, `uart_sync.c`, `SEND_INPUT_EVENT_TO_PEERS`
2. **Display roles**: MASTER_ROLE (left eye) and SLAVE_ROLE (right eye) for rendering coordination
3. **OTA orchestration**: Glasses relay OTA to all sub-components (box, codec, touch, EM9305)
4. **Auto-brightness**: ALS polling → brightness level conversion → display driver, with x/y coordinate calibration
5. **Audio pipeline**: PDM mic → GX8002B codec (TinyFrame) → BLE/NUS output
6. **Wear detection**: `ux_wear_detect.c` — proximity-based, controls display power
7. **Navigation**: compass calibration, location list selection, map session management
8. **Production testing**: Aging test, gray screen test, mic test, BLE production test
9. **Filesystem**: LittleFS on 32MB external QSPI flash with AT commands for file management
10. **Memory**: TLSF allocator (Two-Level Segregated Fit) for real-time allocation

> Many additional discoveries (86 resolved items) were previously tracked as a changelog in this section. All findings have been incorporated into their respective sections above (§1–§22) and into the dedicated per-component docs.

### 23.8 Binary Analysis Evidence Index (Phase 6-8 Reconciliation)

The following analysis artifacts produced by automated tools validate and extend the claims throughout this document. Each artifact is tied to specific firmware files under `captures/firmware/` and provides byte-level evidence.

| Phase | Artifact | Validates Claims In | Key Evidence |
|-------|----------|---------------------|-------------|
| **2 (Corpus)** | `2026-03-03-firmware-corpus-baseline.md` | §1 (Hardware IDs), §23.2 (Fingerprints) | SHA-256/MD5 fingerprints for all 15 firmware binaries; confirmed codec/BLE byte-identical across all 5 versions |
| **3 (Container)** | `2026-03-03-evenota-header-validation.md` | §23.3 (Cross-Version), firmware-files.md | All 7 EVENOTA packages validated: magic, TOC integrity, payload bounds, CRC32C correctness |
| **4 (Components)** | `2026-03-03-firmware-component-decomposition.md` | §1 (Hardware), §12 (Update Paths), per-component docs | Boot/update chain: bootloader→main→subcomponents; ARM vector tables; FWPK/EVEN/patch formats |
| **5 (Integrity)** | `2026-03-03-integrity-packaging-semantics.md` | §23.3 (Checksums), firmware-files.md | 5 algorithm families confirmed: EVENOTA CRC32C, preamble CRC32, FWPK+CRC32/CRC32C, EVEN+BESum, BLE structural |
| **6 (BLE)** | `2026-03-03-ble-artifact-extraction.md` | §8 (BLE Architecture), §7 (Inter-eye), §23.5 (Module Tags) | 13 embedded UUID artifacts; 9 AT command families; 6 candidate command family clusters; stable offsets across versions |
| **7 (Hardware)** | `2026-03-03-hardware-functionality-mapping.md` | §1 (Hardware Table), §11 (Display), §16 (Audio) | 6 subsystem boundaries confirmed: BLE coprocessor, touch input, audio codec, display optics, box controller, control MCU |
| **8 (Evolution)** | `2026-03-03-cross-version-behavior-evolution.md` | §22 (Unknowns), §12 (Update Paths) | Marker offset deltas +0x64BF8 to +0x727D9; LOW regression risk on BLE, MEDIUM on diagnostics |

**Evidence confidence ratings used throughout §1–§22:**
- **CONFIRMED**: Byte-level evidence in at least 2 independent sources (firmware binary + analysis tool output)
- **HIGH**: Strong evidence from single source (firmware strings, app RE, or protocol observation)
- **MEDIUM**: Inferred from indirect evidence (symbol names, offset patterns, behavior correlation)
- **LOW**: Single unvalidated reference or hypothesis

### 23.8.1 Firmware Version Size Progression

Main application (`ota_s200_firmware_ota.bin`) growth across versions:

| Version | Main OTA | BLE | Codec | Touch | Box | Bootloader | Total Package |
|---------|----------|-----|-------|-------|-----|------------|---------------|
| v2.0.1.14 | 2.47 MB | 211,948 | 319,372 | 27,816 | 55,296 | 82,404 | ~3.0 MB |
| v2.0.3.20 | 3.07 MB | 211,948 | 319,372 | 28,320 | 55,296 | 82,404 | ~3.6 MB |
| v2.0.5.12 | 3.16 MB | 211,948 | 319,372 | 28,320 | 55,296 | 82,404 | ~3.7 MB |
| v2.0.6.14 | 3.18 MB | 211,948 | 319,372 | 34,080 | 55,808 | 82,404 | ~3.8 MB |
| v2.0.7.16 | 3.19 MB | 211,948 | 319,372 | 34,080 | 55,808 | 82,404 | ~3.9 MB |

**Stability observations:**
- BLE (EM9305): byte-identical across ALL versions — no BLE protocol changes
- Codec (GX8002B): byte-identical across ALL versions — audio path stable
- Touch: stable through v2.0.5.12, then +22.6% jump at v2.0.6.14 (gesture/calibration enhancement)
- Box: stable through v2.0.5.12, slight growth at v2.0.6.14 (+512 bytes)
- Bootloader: byte-identical across ALL versions — boot chain stable
- Main app: significant evolution (+29% from v2.0.1.14 to v2.0.7.16)

### 23.9 Deep Binary Analysis Findings (2026-03-03)

Multi-version firmware binary analysis across v2.0.1.14 → v2.0.7.16 extracted the following implementation details:

#### Boot Sequence

- **Bootloader SP**: Fixed at `0x2007FB00` across all versions (consistent 512KB SRAM layout)
- **Reset handler**: Varies per version: v2.0.1.14→`0x004322D3`, v2.0.3.20→`0x004323B3`, v2.0.5.12→`0x0043248B`, v2.0.7.16→`0x004324CF`
- **VTOR Write**: Bootloader writes `SCB->VTOR = targetRunAddr` at offset `0x1DBDC` (movw/movt into r1=0xE000ED08, str r0,[r1])
- **App Jump**: Loads `MSP = *(targetRunAddr + 0)`, then `entry = *(targetRunAddr + 4)`, then `bx r1` (Thumb entry)
- **App Execute Region**: `0x00438000` base, growing: 2.47 MB (v2.0.1.14) → 3.19 MB (v2.0.7.16) = +29%
- **Bootstrap Markers**: Literal tuple at `0x224E0` contains `0x00410000` (vector base), `0xE000ED08` (SCB->VTOR), `0x2007D000` (RAM stack marker)

#### Display Pipeline

- JBD4010 MSPI driver path stable at `0x285A8C` across all versions
- Display config regions (0x0E-20) are write-only — no firmware response expected
- **Image CRC**: OTA transport uses CRC32 (component-level), BLE payload uses CRC16-CCITT (packet-level)
- EvenHub/Navigation image container paths: `path_evenhub_common_image_container`, `path_navigation_data_handler`, `display_navigation_ui`
- Display driver manager marker `displaydrv_manager` added in v2.0.5.12

#### Touch Firmware Evolution

- **v2.0.1.14**: 27,808 bytes (baseline)
- **v2.0.3.20**: 28,192 bytes (+384)
- **v2.0.5.12**: 28,320 bytes (+128)
- **v2.0.6.14**: 34,080 bytes (+5,760) — **Major update**: proximity baseline capture (`touch_component_prox_baseline` at 0x77C1), fast click reset (`touch_component_fast_click_reset` at 0x7841)
- **v2.0.7.16**: 34,080 bytes (stable)

#### BLE Cordio Stack

- **Cordio ATT path**: `0x26F368` (added v2.0.3.20)
- **Cordio DM path**: `0x26D140` (added v2.0.3.20) — device manager for pairing/encryption
- **Connection param retry**: `conn_param_retry=0x26C76B` with 30s backoff
- **SMP pairing events**: `DM_SEC_PAIR_FAIL_IND` at `0x266E9B`, `DM_SEC_ENCRYPT_IND` at `0x267A6A`
- **ANCS service discovery state**: `ble_service_discovery_state=0x268E94` (added v2.0.3.20) — logs `discState`, `EVEN_BLE_DISC_SLAVE_ANCS_SVC`, `phoneType`
- **ANCS handle log**: `ble_ancs_handle_log=0x26EDE4` — logs NS, NS_CCC, CP, DS, DS_CCC handles

#### EM9305 BLE Coprocessor (Stable)

- Header: version `0x4040200`, record_count=4, erase_pages=29
- Record 0: addr=`0x300000`, len=`0xE0`, offset=`0x7C`
- Checksum: CRC32C (MSB-first, poly=0x1EDC6F41) over payload range
- **Byte-identical** across all 5 versions (SHA-256 `91a38f7f...`, 211,948 bytes)

#### Audio Codec (GX8002B) FWPK Structure

- FWPK dual-segment format:
  - Segment 0: offset=0x30, len=0x955C (bootloader stage1, CRC32=`0x307E8A10`)
  - Segment 1: offset=0x958C, len=0x44A00 (main stage2, CRC32=`0xB281D56C`)
- BINH boot header in segment 1 at offset 0x958C:
  - `+0x08` (LE): stage1_size=512 bytes, `+0x10` (LE): stage2_size=12,288 bytes
- Codec stable markers: `path_codec_bin=0x2F908C`, `string_codec_dfu=0x273F65`, `codec_package_info=0x28EF88`
- DMIC digital microphone at `0x13450`, I2S audio clocking at `0x49B84`
- **Byte-identical** across all 5 versions (SHA-256 `1c1462af...`, 319,372 bytes)

#### File System Architecture

- **LittleFS** on MX25U25643G 32MB external flash
- **FlashDB** NV storage: transaction logging marker `efs.tran=0x26FDB5`
- **Transport overflow guard**: `0x26FDBE` tracks packetLen/packetNum/packetTotalNum counters
- Flash write guards enforce 4KB page alignment

#### OTA Transport Details

- Codec transport: `codec_pack_message` at `0x23B7BC`, `codec_unpack_message` at `0x23C258`
- Fields: cmd(16), NR(8), TYPE(8), seq(8), flags(8), length, CRC32
- OTA CRC guard: `ota_crc_guard=0x265E88` (added v2.0.3.20) — per-packet CRC enables implicit resume
- Box OTA coordination: `box_gls_ota_left=0x1208` marker for left eye coordination

#### Inter-Eye Sync

- Timeout state tracking: `transport_timeout=0x26E62B` logs serviceID/syncID/pipeID tuple
- Config close: two-packet sequence (render mode + reset) via `config_state_close()`
- Each eye maintains independent packet counter — NOT synchronized between eyes
- Right eye auth response ~2s delayed (separate BLE connection, async processing)

#### Markers by Version (Diagnostic Feature Evolution)

| Added In | Markers |
|---|---|
| v2.0.3.20 | `ble_service_discovery_state`, `ble_ancs_handle_log`, `ble_master_connect_state`, `ble_ota_crc_guard`, `ble_path_cordio_att`, `ble_path_cordio_dm` |
| v2.0.5.12 | `display_path_displaydrv_manager` |
| v2.0.6.14 | `display_path_evenhub_common_image_container`, `display_evenhub_parser`, `display_menu_page_ble` |

### 23.10 BLE Profile Architecture (2026-03-03)

Deep string analysis of `ota_s200_firmware_ota.bin` reveals the complete BLE profile stack. The G2 firmware implements **8 BLE profiles** at `platform/ble/profiles/`:

| Profile | Source File | Characteristics | Purpose |
|---------|-----------|-----------------|---------|
| **EUS** | `profile_eus.c` | 0x5401 (TX) / 0x5402 (RX) | Even UART Service — main G2 protobuf command transport |
| **EFS** | `profile_efs.c` | 0x7401 (TX) / 0x7402 (RX) | Even File Service — file transfer (notifications, maps, firmware) |
| **ESS** | `profile_ess.c` | 0x6401 (TX) / 0x6402 (RX) | Even Sensor Service — display sensor telemetry stream |
| **NUS** | `profile_nus.c` | 6E400002 (TX) / 6E400003 (RX) | Nordic UART Service — gestures, mic control, text/BMP display |
| **OTA** | `profile_ota.c` | (via EFS pipe) | Over-the-air firmware update |
| **Ring** | `profile_ring.c` | BAE80012/BAE80013 | R1 Ring communication (status, gestures) |
| **ANCC** | `profile_ancc.c` | NS/CP/DS handles | Apple Notification Center Client |
| **GATT** | `profile_gatt.c` | Standard GATT | Standard GATT profile |

Key architecture details:
- All three custom services (EUS, EFS, ESS) follow the same CCC (Client Characteristic Configuration) pattern with `cccdEnable` callbacks
- The pipe system routes data between services: `BLE_PIPE_ESS` is a named pipe type
- `PIPE_ROLE_CHANGE` device config command enables dynamic pipe routing at runtime
- The `x450` characteristics (0x5450/0x6450/0x7450) are GATT service declaration UUIDs (parent services)

**ANCS Integration Details**:
- Full ANCS client with Notification Source (NS), Control Point (CP), Data Source (DS) handles
- Glasses act as **BLE MASTER** when discovering phone's ANCS service
- Notification attributes processed via state machine (`attrState`, `attrCount`)
- Mutex-protected notification queue with add/remove/find/count operations
- Notifications suppressed during calibration UI
- Coexists with custom 0x02-20 notification protocol (custom = rendering, ANCS = raw iOS notifications)
- Source: `service_ancc.c` + `profile_ancc.c`

### 23.11 OTA Protocol Details (2026-03-03)

OTA transfer uses a **4-phase state machine** implemented in `pt_protocol_procsr.c`:

| Phase | Enum | Description |
|-------|------|-------------|
| 1. START | `eOTATransmitCID_OTA_TRANSMIT_START` | Initiate OTA session (timed in ms) |
| 2. INFORMATION | `eOTATransmitCID_OTA_TRANSMIT_INFORMATION` | File header exchange (validated against `EVEN_OTA_FILE_HEADER_SIZE`) |
| 3. FILE | (data transfer) | **1000-byte payloads**, timestamp validation, CRC at `payload_len + 5` |
| 4. RESULT_CHECK | `eOTATransmitCID_OTA_TRANSMIT_RESULT_CHECK` | Final CRC verification (`g_production_ota_crc_result`) |

Low-level send via `OTA_SendPacket`. The OTA profile uses the EFS pipe (file service characteristics).

### 23.12 Firmware Protobuf Service Modules (2026-03-03)

Complete list of `pb_service_*` modules discovered in firmware strings:

| Module | Source File | BLE Service | Purpose |
|--------|-----------|-------------|---------|
| `pb_service_dev_setting` | `pb_service_dev_setting.c` | 0x0D-00 | Brightness, head-up angle, auto-brightness |
| `pb_service_setting` | `pb_service_setting.c` | 0x0D-00 | Universal settings, gesture config, wear detection |
| `pb_service_glasses_case` | `pb_service_glasses_case.c` | 0x0D-00 | Case detection and status |
| `pb_service_onboarding` | `pb_service_onboarding.c` | 0x0D-00 | Onboarding flow |
| `pb_service_notification` | `pb_service_notification.c` | 0x02-20 | Phone notification rendering |
| `pb_service_conversate` | `pb_service_conversate.c` | 0x0B-20 | Conversate/ASR |
| `pb_service_teleprompt` | `pb_service_teleprompt.c` | 0x06-20 | Teleprompter |
| `pb_service_translate` | `pb_service_translate.c` | 0x07-20 (shared) | Translation (type 20-23, via EvenAI service) |
| `pb_service_even_ai` | `pb_service_even_ai.c` | 0x07-20 | Even AI / EvenHub |
| `pb_service_dev_config` | `pb_service_dev_config.c` | (unknown) | Device configuration |
| `pb_service_quicklist` | `pb_service_quicklist.c` | (unknown) | Quicklist/reminders |
| `pb_service_pair_mgr` | `pb_service_pair_mgr.c` | (unknown) | Pairing management |
| `pb_service_health` | `pb_service_health.c` | (unknown) | Health data (type, goal, value, avg, duration, trend) |
| `pb_service_ring` | `pb_service_ring.c` | (unknown) | Ring communication |

Settings use a `magic_random` field for **duplicate message detection** — also present in conversate, teleprompt, and translate modules. The `which_command_data` field suggests oneof-style protobuf structure.

### 23.13 Dashboard, Quicklist, and Page State Sync (2026-03-03)

**Page State Sync** (`page_state_sync.c` at `app/gui/sync_info/`):
- Syncs dashboard state (tile index + widget index) from glasses to app
- Only the **master eye** performs initial state sync
- Uses protobuf encoding via `sync_info_data_handler`
- Source: `sync_info.c` at `app/gui/sync_info/`

**Dashboard**:
- Auto-close value `0xFF55` = disabled (no auto close)
- Stock widget with container-based layout and separator lines (max 185 data points)
- News widget with force-upgrade mechanism
- Menu IDs: `NOTIFICATIONS`, `CONVERSATE`, `TELEPROMPT`, `TRANSLATE`, `NAVIGATE`, `EVEN_AI`, `DASHBOARD`, `SILENT_MODE`

**Quicklist** (`pb_service_quicklist.c`):
- Per-item data: uid, index, isCompleted, title, timestamp, ts_type
- LVGL fade animations for item transitions
- Scroll position caching
- Page state sync integration

### 23.14 Gesture Configuration (2026-03-03)

Gesture-to-app mappings are configurable per display state:

```
[setting]Updated gesture config: screen_off=[%d,%d,%d], screen_on=[%d,%d,%d]
[srv_universal_setting]Set gesture apptype: screen_on=%d, operation_type=%d, apptype=%d
```

This means the gesture control list has TWO independent mappings:
- **Screen ON**: gestures while display is active
- **Screen OFF**: gestures while display is off

The universal setting service provides get/set functions: `svc_universal_setting_get_gesture_apptype` / `svc_universal_setting_set_gesture_apptype`.

**Buzzer/vibration event types** (from CLI help):
| ID | Type |
|----|------|
| 0 | Touch key |
| 1 | Clock alarm |
| 2 | Phone call |
| 3 | Test 1 |
| 4 | Test 2 |
| 5 | Single click |
| 6 | Double click |
| 7 | Long press |
| 8 | Swipe left |
| 9 | Swipe right |
| 10 | Wear |

**iOS SDK implementation** (2026-03-03):
- `G2BuzzerProtocol.swift`: `G2BuzzerType` enum (11 types), trigger via 0x0D-20 with speculative cmdId=30
- DevicesView buzzer section with type picker + trigger button
- BLE wire format **unconfirmed** — buzzer may only be directly triggered via debug CLI (`AT^BUZZER type`).
  The internal firmware API (`drv_buzzer_play`) is called by touch/system events, not exposed as a BLE service endpoint.

### 23.15 Display Control Gating (2026-03-03)

The JBD4010 display driver enforces multiple gating conditions:

```
[service.settings]wear detect input not enabled, jbd4010 ctrl not allowed
[service.settings]OTA is going, jbd4010 ctrl not allowed
[service.settings]glasses in box, jbd4010 ctrl not allowed
```

Display is blocked when:
1. **Not wearing** — wear detection must report proximity
2. **OTA in progress** — firmware update locks display
3. **In charging case** — case detection blocks display

Display has configurable canvas offset (`canvas_x`, `canvas_y`) with range validation. Address range: `0x80000000 - 0x81FFFFFF`.

### 23.16 Inter-Eye Communication (2026-03-03)

The inter-eye link is **wired UART**, confirmed by:
- Source: `uart_sync.c` at `framework/sync/`
- Runs in dedicated `uart_sync_thread` with stream buffer and sender mutex
- Uses protobuf encoding for data relay
- Master/slave roles: left eye = master (auth, display), right eye = slave (audio, ring)
- Audio manager coordinates DMIC control: master can request slave to close DMIC for low-power mode

Inter-eye data relay examples:
- `sync_info_data_handler` for navigation/dashboard state sync
- EvenHub slave forwards `abnormal exit event to master`
- Even AI animation: `Slave LOOP: detected master loop, jumping`
- Universal settings: `Recv slave universal setting sync, values not match, send config to slave`
- Peer BLE status tracking: `selfBleStatus`/`peerBleStatus` and `selfBleRingStatus`/`peerBleRingStatus`

### 23.17 Health Data Architecture (2026-03-03)

Health data managed by `pb_service_health.c` and `health_data_manager.c`:

```
[health.data_mgr]Batch save health data: type=%s, goal=%u, value=%.2f, avg=%.2f, duration=%u, trend=%d
[pb.health]pSingleData:data_type = %d, goal = %d, value = %f, avg_value = %f, duration = %d, trend = %d
```

Per-record fields: `data_type` (string enum), `goal`, `value`, `avg_value`, `duration`, `trend`.
- Batch save capability (multiple records)
- "Highlight" concept with limited on-glasses storage
- Health page UI with page indicators and switching
- Temperature unit: Celsius (1) or Fahrenheit (2), stored in KV database

### 23.18 Cross-Version Feature Delta: v2.0.5.12 → v2.0.6.14 (2026-03-03)

**1,169 new readable strings** in v2.0.6.14. Major additions:

| Category | New Feature |
|----------|-------------|
| **Universal Settings** | `date_format`, `distance_unit`, `dominant_hand`, `gesture_app`, `metric_unit`, `temperature_unit`, `time_format` via `service_universal_setting.c` |
| **Gesture Config** | Per-screen-state mappings: `screen_off=[%d,%d,%d], screen_on=[%d,%d,%d]` |
| **Menu Persistence** | `[kv.module_cfg]` stores menu items (app_id, app_type, icon_num, text_name) in KV database |
| **EvenHub Images** | `[common_image_container]` with BMP validation, 4-bit BMP processing, D-Cache, CRC16 |
| **Image Fragmentation** | session_id, fragment_index, fragment_packet_size, total_size, compress_mode |
| **Duplicate Detection** | `magic_random` dedup in conversate, teleprompt, translate |
| **Audio SSR/TDOA** | Sound Source Recognition with L/R/Front/Rear channels; TDOA per frame |
| **Touch DFU** | `[drv.touchdfu]` touch controller firmware update (FWPK magic, CRC32 verification) |
| **BLE Advertising** | `[Auto Restart]` state machine, legacy advertising delay handling |
| **Ring Protocol** | `glasses status send to ring: %02X %02X` (2-byte status packets) |
| **Localization** | French and Italian UI strings (close timer, language pair descriptions) |
| **Cordio Debug** | Extensive ATT, L2CAP, SMP, DM, HCI source paths |

### 23.19 Corrections from Prior Assumptions

The following claims were initially derived from API traffic, app reverse engineering, or protocol observation and have since been validated, corrected, or refined by binary analysis of the firmware artifacts.

| Original Claim | Source | Correction | Firmware Evidence |
|----------------|--------|-----------|-------------------|
| **G2 SoC is nRF52840** | §3-6 DFU bootloader analysis | **CORRECTED**: G2 SoC is Ambiq Apollo510b. nRF52840 is DFU bootloader for R1 Ring update path | Build path `s200_ap510b_iar` in `ota_s200_firmware_ota.bin`; Cordio host stack (not Nordic SoftDevice) |
| **BLE stack is Nordic SoftDevice S140** | DFU analysis §5 | **CORRECTED**: G2 uses Cordio BLE host on Apollo510b. S140 is only in DFU bootloader (likely R1 path) | `third_party\cordio\` in firmware strings; no S140 symbol tables in main OTA binary |
| **Codec firmware needs custom protocol** | Protocol probe | **CONFIRMED**: TinyFrame serial protocol to GX8002B | `drv_gx8002b.c` + `TinyFrame/` in firmware; FWPK+BINH boot blocks at known offsets |
| **Inter-eye link is BLE** | Initial assumption | **CORRECTED**: Wired UART/I2C through glasses frame | `sync.module.uart`, `uart_sync.c`, `SEND_INPUT_EVENT_TO_PEERS` strings in firmware |
| **BLE EM9305 patch changes across versions** | Hypothesis | **CONFIRMED STABLE**: Byte-identical (211948 B) across all 5 versions (2.0.1.14→2.0.7.16) | SHA-256 `91a38f7f...` matches in all version extractions |
| **Codec firmware changes across versions** | Hypothesis | **CONFIRMED STABLE**: Byte-identical (319372 B) across all 5 versions | SHA-256 `1c1462af...` matches in all version extractions |
| **Touch firmware is static** | Assumption | **CORRECTED**: Evolves significantly — 27.8 KB (v2.0.1.14) → 34.1 KB (v2.0.6.14+) = +22.6% growth. Binary diff shows address relocation (0x41→0x44 pointer table shifts), suggesting code expansion or data structure reorganization for enhanced gesture recognition/calibration | Per-version extraction sizes in corpus baseline; xxd diff of v2.0.5.12 vs v2.0.6.14 `firmware_touch.bin` |
| **EVENOTA checksum is CRC32** | Initial analysis | **REFINED**: CRC32C (Castagnoli), non-reflected (MSB-first) — different polynomial from zlib CRC32 | `G2CRC.crc32c()` validated against all 7 packages |
| **Display mode 6 = generic active** | Protocol observation | **REFINED**: Mode 6 = RENDER (EvenHub/Navigation page content). Mode 16 = Teleprompter, Mode 11 = Conversate | `drv_mspi_jbd4010.c`, LVGL page manager strings |
| **0x5450/0x6450/0x7450 are unknown** | §22 (was listed as unknown) | **RESOLVED**: GATT service declaration UUIDs — parent services for control/display/file pipe pairs | BLE artifact extraction Phase 6: stable offsets across all versions |

### 23.20 Validation Scripts

> Reproducible validation scripts for checksum verification, firmware API sweeps, and disassembly correlation have been archived in `captures/firmware/analysis/`. The analysis artifacts referenced throughout §23 were produced by `tools/analyze_g2_extracted.py` and `tools/fetch_latest_firmware.py`.

```
# Quick container parse + checksum proof (Python 3)
python3 tools/analyze_g2_extracted.py \
  --package captures/firmware/g2_2.0.7.16.bin \
  --extracted-dir captures/firmware/g2_extracted \
  --output captures/firmware/analysis/2026-03-03-g2-extracted-wave.md
```

### 23.21 String Cross-Reference Index (2026-03-03)

Comprehensive cross-version string analysis of all 4 locally available firmware versions (v2.0.1.14 → v2.0.6.14) across all 6 component binaries. Tool: `tools/firmware_string_index.py`.

| Metric | Value |
|--------|-------|
| Total strings extracted | 132,307 |
| Unique strings | 34,866 |
| Protocol-categorized | 8,392 |
| Stable (all 4 versions) | 20,287 |
| Version-specific (1 version only) | 6,408 |
| Per-version: v2.0.1.14 | 28,879 |
| Per-version: v2.0.6.14 | 34,983 (+21%) |

**Top categories**: debug (2,126), protocol (1,611), BLE (1,426), inter-eye (1,205), OTA (1,026), filesystem (972), RTOS (866), config (781), display (678), audio (572), ring (406).

**Version evolution**: v2.0.3.20 was the largest jump (+4,857 strings), introducing structured logging with `[module_name]` prefixes and tagged subsystem identifiers. v2.0.6.14 added production CLI getters (`get dominant_hand`, `get temperature_unit`, `get date_format`, `get time_format`, `get gesture_app`).

Full index: `captures/firmware/analysis/firmware-string-cross-reference.json` (searchable by string, offset, version, category).

### 23.22 Inter-Eye Communication Deep Analysis (2026-03-03)

Extended from §23.16 with string cross-reference evidence. The inter-eye architecture has **three communication layers**:

#### Layer 1: TinyFrame Serial Protocol

The inter-eye wired link uses **TinyFrame** (`third_party/TinyFrame/TinyFrame.c`), a lightweight serial framing library with:

| Function | Purpose |
|----------|---------|
| `TF_Init` / `TF_InitStatic` | Initialize TinyFrame instance |
| `TF_AcceptChar` | Process incoming serial bytes |
| `TF_HandleReceivedMessage` | Dispatch received messages |
| `TF_ClaimTx` | Lock TX for sending |
| `TF_AddTypeListener` | Register handler by message type |
| `TF_AddIdListener` | Register handler by message ID |
| `TF_Multipart_Payload` / `TF_Multipart_Close` | Multi-part message transfer |

Error handling: body checksum mismatch, head checksum mismatch, parser timeout, payload too long.

Both eyes run TF instances:
- `!!! TF Module(Master Mode) start failure.` — left eye is TinyFrame master
- `!!! TF Module(Slave Mode) start failure.` — right eye is TinyFrame slave

The `sync.module.framework` manages the TinyFrame inter-eye transport with `uart_sync_thread` (dedicated RTOS thread).

#### Layer 2: Sync Data Handlers

| Handler | Direction | Data |
|---------|-----------|------|
| `AUDM_SendSyncMsgToPeer` | L→R or R→L | Audio state (mic enable, audio mode) |
| `AUDM_HandlePeerSyncMsg` | receive | Audio sync message processing |
| `AUD_PeerSyncMsg` | either | Audio peer sync wrapper |
| `APP_PbTxEncodeScrollSync` | L→R | Protobuf-encoded scroll position sync |
| `SendInputEventToPeers` | L→R | Touch/gesture input relay |
| `AsyncSendInputEventToPeers` | L→R (async) | Async variant for deferred relay |
| `sync_info_data_handler` | L→R | Navigation/dashboard state sync |

Display sync: `received display sync exit command, app id = %d` — display state changes relayed to peer with application ID for routing.

#### Layer 3: BLE Role Division

Independent from the wired link, each eye has distinct BLE roles:

| Role | Eye | BLE Functions | Peer Connection |
|------|-----|---------------|-----------------|
| **Master** | Left (primary) | `APP_MasterConnectEvent`, `APP_MasterScanEvent`, `_bleMasterScanReport` | Connects to R1 Ring via BLE |
| **Slave** | Right | `APP_BleSlaveAdvStartEvent`, `APP_BleSlaveAsCmdRole`, `APP_SlaveStartSecurityRequestEvent` | Receives phone connection |

The `APP_IsLocalSlaveAsCmdRole` function checks if the local eye is slave acting as command role — suggests the slave eye can relay BLE commands received from the phone to the master via the wired link.

#### Box UART Manager (Glasses↔Case)

Separate from inter-eye, the glasses-to-case communication uses `box_uart_mgr.c`:

```
[box_uart_mgr]Err:serial recv data does not meet the protocol
[box_uart_mgr]crc check failed, data len = %d, tmp_crc: 0x%x, tmp_buf[idx + tmp_len - 1]: 0x%x
[box_uart_mgr]box uart pack err:%d / unpack err:%d / send err:%d
```

Supports: pack/unpack framing, CRC validation, tx flush, and pt (protocol) command execution. The CRC is compared at `tmp_buf[idx + tmp_len - 1]` (last byte of framed message).

### 23.23 OTA Wire Protocol Deep Analysis (2026-03-03)

Extended from §23.11 with string cross-reference evidence. Two OTA paths exist:

#### Path A: Glasses OTA (Phone → Glasses)

Source files:
- `platform/protocols/ota_service/ota_service.c`
- `platform/protocols/ota_service/ota_transport.c`

**4-phase protocol** with wire format evidence:

| Phase | Stable Function | Evidence |
|-------|----------------|----------|
| **START** | `pt_ota_transmit_start` | Timed (`= %d ms`), opens OTA session |
| **INFORMATION** | `pt_ota_transmit_information` | Validates `data_len != EVEN_OTA_FILE_HEADER_SIZE` — header must match expected size |
| **FILE** | `pt_ota_transmit_file` | **1000-byte payload enforced** (`payload_len is not equal to 1000`). Timestamp validation: `timestamp is not equal to upgrade_file_timestamp`. CRC at `recv_value[payload_len + 5]` — implies 5-byte OTA packet header before payload |
| **RESULT_CHECK** | `pt_ota_transmit_result_check` | Final CRC: `g_production_ota_crc_result` |

**Derived OTA packet layout** (FILE phase):
```
Byte 0-4:   OTA header (5 bytes — content unknown)
Byte 5+:    Payload (1000 bytes enforced)
Byte 1005:  CRC (at recv_value[payload_len + 5])
```

**OTA transmit types** (stable across all versions):

| Enum | Target Path (from strings) |
|------|---------------------------|
| `GLASSES_FIRMWARE` | Main app binary |
| `BOOTLOADER` | Bootloader binary |
| `BLE9305_BIN` | EM9305 BLE patch |
| `TOUCH_BIN` | CY8C4046FNI touch firmware |
| `AUDIO_BIN` | GX8002B codec firmware |
| `BOX_BIN` | Case MCU firmware |
| `BOX` | Box firmware (alt path) |
| `FONT` | Font data to external flash |
| `EXTERNAL_FLASH` | Generic external flash data (CRC verified: `crc verify success/failed`) |
| `OTHER_BIN` | Arbitrary binary |

Key OTA functions (all stable):
- `APP_EvenOtaSendDataMsg` — send OTA data message (uses `WsfMsgAlloc`)
- `APP_EvenOtaWriteCback` — OTA write callback
- `APP_EvenOtaDisconnect` — disconnect after OTA
- `APP_ConnectParamOTASetFastMode` — switch BLE connection params for OTA throughput
- `OTA_ReceivePacket` / `OTA_SendPacket` — low-level packet I/O
- `OTA_SetInterface` — configure OTA transport interface
- `OTA_FileSystemSetBootloaderFlag` — set bootloader flag for reboot into DFU
- `OTA_ReplyCrcErrorToAPP` / `OTA_ReplyNoResourcesToAPP` / `OTA_ReplyTimeoutToAPP` — error responses

**File export** (separate from OTA transmit):
- `eOTAExportFileCID_OTA_FILE_EXPORT_CMD_RESULT_CHECK` — export direction uses separate CID

**OTA status tracking**:
- `SYSTEM_OTA_STATUS_ID state come from self = %d` — local OTA state
- `SYSTEM_OTA_STATUS_ID state come from peer = %d` — peer eye OTA state (relayed via wired link)

#### Path B: Box OTA (Glasses → Case)

Separate protocol for case firmware, managed by `box_uart_mgr.c`:

| Phase | Function | Min recv_len |
|-------|----------|-------------|
| 1. `firmware_check` | `pt_box_ota_firmware_check` | ≥ 8 bytes |
| 2. `begin` | `pt_box_ota_begin` | ≥ 4 bytes |
| 3. `file_get` | `pt_box_ota_file_get` | ≥ 9 bytes |
| 4. `result_check` | `pt_box_ota_result_check` | ≥ 9 bytes |

Box OTA details:
- Battery ≥ 50% required: `pt_box_ota_begin: battery level is less than 50%`
- Firmware read from LittleFS: `firmware/box.bin file not exist`
- File position tracking: `file position mismatch, expected=%d, actual=%ld`
- Max chunk size: `read_len > 240` (240-byte chunks for box UART)
- Dual-bank flash: `Running bank: %d`, `Erase bank fail`, `Get running bank`
- CRC verification: `crc_cal: 0x%x, crc_rx:0x%x`
- Version comparison: `new version, cur:1.%d.%d, remote:1.%d.%d, len:%d, crc:0x%x`
- 3-minute timeout: `box OTA timeout (>3 minutes), force clear g_is_box_ota_mode`

#### OTA Guards

EvenAI is disabled during OTA: `warn: can not ctrl evenai, product_mode = %d, ota_status = %d, voice_switch = %d, onboarding_status = %d` — confirms OTA status is tracked globally and blocks non-essential services.
