# Even G2 glasses: hardware

> **Citations.** Repository paths cited as `path` or `path:line` refer to the tree at commit `832137ec`. The 2026-09-29 cleanup retires many of those evidence files; after they are removed, `git show 832137ec:<path>` still shows them.


Tags follow the [confidence vocabulary](README.md#confidence-vocabulary):
FW, REG, DS, PR, COM, INF, UNV. Repository paths are relative to the
repository root. Run addresses in the Apollo main image are
`file_offset + 0x00437FE0`.

Internal names: glasses = **S200** (vendor build tree
`D:\01_workspace\s200_ap510b_iar_git\`, i.e. S200 + Apollo510B + IAR;
`g2/docs/research/g2-s200-board-config-recovery.md:4`) [FW]; the FCC antenna
housing is labelled "S200-L&R" [REG]; the case is **B200** [FW]. The G1
project code was S100 [REG, G1 label exhibit].

## 1. System overview

The G2 is two nearly independent computers, one in each temple tip. Each
temple has its own battery, its own Apollo510B running the same firmware
image, its own BLE radio and antenna, its own display panel and its own
peripheral set. The two temples are joined by a flexible circuit through the
frame.

| Statement | Tag | Evidence |
|---|---|---|
| Each temple has an Apollo510B with its own 4 MB MRAM and runs the same main image | FW (High) | `g2/docs/memory-map.md:23` ("Apollo510B internal MRAM — each temple"); one Apollo main payload in EVENOTA (`g2/tools/open_cfw.py:36-41`) |
| Each temple is its own BLE endpoint with its own name, `Even G2_32_L_xxxxxx` / `Even G2_32_R_xxxxxx` | FW, COM | `g2/docs/research/g2-advertised-name-serial-suffix.md`; g2flash `patches/mic_control.c` ("Each temple is its own Apollo510 and its own BLE endpoint") |
| Two independent BLE transmitters, L and R, each with its own LDS antenna | REG | G2 test report N25071003936E §4, §8.1 (L), §8.2 (R) |
| Temple tip holds antenna, processor and battery; a 0.1 mm "dual-sided communication FPC" runs through the frame, so left and right "no longer sync wirelessly" | PR (official blog) | https://www.evenrealities.com/blog/how-we-rebuilt-g2-from-the-inside-out |
| Temple identity is read from a hardware strap: five equal samples, value 1 ⇒ side id 2, else side id 1, mismatch ⇒ 3 (unavailable) | FW (Medium) | `pre-consolidation:g2/components/apollo_main/core_overlay/lens_side_policy.c` |
| Side id 1 = right temple = **master**; side id 2 = left temple. Only the master opens the ambient-light sensor and notifies the phone for some settings | COM | g2flash `patches/zlib_glue.c:184,203`, `patches/settings_ext.c:82,177`, `patches/als_sensor.c:11,307` (firmware 2.3.0.24) |
| The two temples run TinyFrame "uart_sync" with master and slave roles, plus a multipart `sync_framework` | FW (Medium) | `g2/docs/research/g2-uart-sync-recovery.md`; `g2/docs/research/g2-sync-framework-recovery.md:15` |
| The temple-to-temple link is a UART over the frame FPC | INF | FW shows a UART provider under TinyFrame; the official blog says the sides are wired, not wireless. Pads and baud not recovered. |
| Microphone audio to the phone comes from the right arm | G1 only, official | https://github.com/even-realities/EvenDemoApp (G1). Not established for G2. |

### Block diagram (one temple; both temples are the same unless noted)

```mermaid
flowchart LR
  subgraph T["Temple (L or R)"]
    direction LR
    AP["Ambiq Apollo510B<br/>Cortex-M55 + Helium<br/>4 MB MRAM, 3.75 MB SRAM"]
    BLEC["BLE 5.4 controller<br/>'EM9305' image, ARC EM<br/>(in-package BLEC?)"]
    ANT(("LDS antenna<br/>-1.81 dBi L / -2.06 dBi R"))
    NOR["Macronix MX25U25643G<br/>32 MiB 1.8 V QSPI NOR"]
    PANEL["microLED 640x480 4-bpp<br/>JBD4010 or Hongshi A6N-G"]
    GX["NationalChip GX8002B<br/>CK804EF + NPU (voice)"]
    GXNOR["GX8002 SPI NOR<br/>(dual image)"]
    DMIC["DMICs"]
    PDM["PDM mic(s)"]
    TOUCH["Infineon PSoC 4000T<br/>CY8C4046FNI (CapSense)"]
    IMU["TDK ICM-45608 IMU"]
    MAG["Magnetometer 0x1E<br/>(TDK ICT1531x?)"]
    ALS["TI OPT3007 ALS<br/>(master temple)"]
    PMIC["Charger family 1: nPM1300<br/>or family 2: BQ25180 + BQ27427"]
    BAT[["Li-ion 3.87 V 96 mAh"]]
    BUZ["Buzzer (PWM)"]
    AP -- "IOM6 SPI HCI 16 MHz" --- BLEC
    BLEC --- ANT
    AP -- "MSPI1 quad, 96 MHz<br/>XIP 0x80000000" --- NOR
    AP -- "MSPI0 QSPI" --- PANEL
    AP -- "UART3 115200 BUXX<br/>(DFU up to 1.5 Mbaud)" --- GX
    GX -- "I2S 2ch 16 kHz 16-bit" --> AP
    GX --- GXNOR
    DMIC --> GX
    PDM -- "PDM0" --> AP
    AP -- "I2C bus 5 @0x0C + ATTN" --- TOUCH
    AP -- "I2C bus 4 @0x69" --- IMU
    IMU -- "aux I2C" --- MAG
    AP -- "I2C bus 2 @0x45" --- ALS
    AP -- "I2C bus 7: nPM1300 @0x6B<br/>or BQ25180 @0x6A + BQ27427 @0x55" --- PMIC
    PMIC --- BAT
    AP -- "TIMER PWM" --> BUZ
  end
  FPC{{"Frame FPC 0.1 mm<br/>TinyFrame uart_sync"}}
  CASE["Charging case B200<br/>STM32G0B1 (pogo UART + 5 V)"]
  PHONE["Phone app"]
  RING["Even R1 ring"]
  AP --- FPC
  AP -- "pogo UART 5A A5 FF" --- CASE
  BLEC -. "BLE peripheral" .- PHONE
  BLEC -. "BLE central" .- RING
```

## 2. Per-IC table

"Payload" is the EVENOTA component that carries the part's firmware
(`g2/tools/open_cfw.py:1168-1300`, `g2/docs/memory-map.md:7-21`).

| Part | Role | Bus / link | Address / ID | Interrupts | Pins / pads | Clock / data rate | Firmware payload | Evidence | Tag |
|---|---|---|---|---|---|---|---|---|---|
| **Ambiq Apollo510B** | Application MCU per temple: BLE host (Cordio), UI (LVGL + NemaGFX GPU), sensors, audio encode | — | Vector table `0x00438000`, SP `0x2007FB00`, reset `0x005E4233` | — | BGA 153 balls, 96 GPIO (DS) | Cortex-M55 up to 250 MHz (DS) | `ota/s200_firmware_ota.bin` (type 0), `ota/s200_bootloader.bin` (type 1) | `g2/docs/memory-map.md:23,302`; vendor path `s200_ap510b_iar_git`; press: https://www.electronicdesign.com/technologies/embedded/video/55404374/electronic-design-spot-helps-knock-down-edge-ai-noise ; COM: https://github.com/jimrandomh/g2flash | FW High, PR, COM |
| **BLE controller ("EM9305")** | BLE 5.4 link layer; host talks HCI | HCI over **IOM6 SPI, mode 0, 16 MHz** (config `0x200001B4`; `0x004B48A6` → `0x0052DD94(6,…)`), Ambiq "Apollo3-lineage" HCI driver, blocking, 8×260-B TX, 256-B RX, 10 s heartbeat | Vendor HCI: RF power `0xFCC4` (+6 dBm), BD addr `0xFC43` (sent after HCI_Reset), `0xFFF2` local-supported-feature mask; see conflict note below | GPIO group IRQ `GPIO0_607F` handler `0x004B80BE` in BLE-startup area (INF); radio IRQ input GPIO117 (GPIO interrupt channel 0) | Outputs GPIO149 = 1, GPIO93 (BLE_ENABLE, ball E5 per DS) = 0, GPIO136 = 0; inputs GPIO117, GPIO15 | ARC EM at 48 MHz (DS) | `firmware/ble_em9305.bin` (type 5) | Stock emitter plus official Ambiq Zephyr `2e347415`; `am_devices_em9305_init` string at run `0x0071F5D0` (`g2/docs/research/cordio-ble-stack-identity-audit.md:364`); IOM6, pins: [`findings-hardware-drivers.md`](../../g2/docs/reference/findings-hardware-drivers.md#ble-host-to-em9305-controller) | FW (image, HCI, IOM6) High; pins FW Medium; physical form INF |
| **NationalChip GX8002B** ("grus") | Voice DSP + NPU: keyword spotting (LVP_KWS), VAD, beamforming, denoise | Control UART3; audio I2S to Apollo; power/reset GPIOs | Chip id `0x8002` in boot container | GX GPIO2 notification/timestamp line to Apollo; codec pulls Apollo **GPIO29** low for events 0x030C wake word / 0x030D VAD (pin-table handler `0x0057A80E`) | Apollo logical board GPIO 6, 7, 8 (power sequencing 5 ms / 20 ms) = pads **GPIO134 → 5 ms → GPIO143 → 20 ms → GPIO146** (selector `0x00509024`); GPIO134 is shared with the sensor rail | UART 115,200 runtime; boot 230,400 → 1,000,000 → 1,500,000 (conflict: stock always sends 1,000,000 for stage 2 and only logs the header's 1.5 Mbaud) | `firmware/codec.bin` (type 4) | `g2/docs/research/g2-drv-gx8002b-recovery.md`; `g2/docs/research/g2-service-codec-host-recovery.md:29-69`; `g2/docs/research/g2-service-codec-dfu-recovery.md:46-48`; pads, events, baud: [`findings-hardware-drivers.md`](../../g2/docs/reference/findings-hardware-drivers.md) | FW High |
| GX8002 SPI NOR | Holds GX8002 image A `[0,0x2F3B0)` and backup B `[0x2F3B0,0x46440)` | GX8002 DesignWare SPI | — | — | — | — | Codec segment 2 | `g2/docs/research/g2-codec-fwpk-segments-recovery.md` | FW (exists) High; size Low |
| **Macronix MX25U25643G** | 32 MiB external NOR: littlefs, XIP | **MSPI1**, CE0 | JEDEC `C2 25 39` | MSPI1 IRQ 21 prio 4 | CE GPIO49 (MNCE1_0, ball J1); D0–D3 GPIO95–98 (MSPI1_0..3, balls H1/H2/G4/H3); SCK GPIO103 (MSPI1_8, F3); DQS GPIO104 (MSPI1_9, C3, configured, unused) | 96 MHz, SPI mode 0, quad 1-1-4, 4-byte addressing | — | `g2/docs/research/littlefs-g2-mspi-transport-audit.md:7,68-81,120-176`; ball numbers from Apollo510B datasheet pin table | FW High; balls DS |
| **JBD JBD4010** | microLED panel variant 0, 640×480, 4-bit gray | **MSPI0** QSPI | Chip-ID cmd `0x9F` (2 B), die ID `0x81` (12 B) | MSPI0 IRQ 20 prio 4 | Not recovered | Pixel writes quad (mode byte 0x10) | — | `g2/docs/research/g2-uled-jbd4010-recovery.md:101-121`; `g2/docs/research/g2-uled-mspi-common-recovery.md:94-116` | FW High |
| **Hongshi A6N-G** | microLED panel variant 1, 640×480, 4-bit gray | **MSPI0** QSPI, bank/register protocol | Chip reg `0x06 == 0x01`; status preamble `02 00 2A 00 00 00 01 DF` | MSPI0 IRQ 20 | Not recovered | — | — | `g2/docs/research/g2-uled-a6ng-recovery.md` | FW High |
| **Infineon PSoC 4000T CY8C4046FNI** | Touch strip + proximity (wear) controller | **I2C bus 5** (Apollo master) | 7-bit **0x0C** | Active-low attention GPIO (touch side PRT4.0) → Apollo **GPIO27** (pin-table handler `0x0055BA64` → `input_msg_send_touch` `0x00513056`) | I2C pads GPIO47/48 (IOM5, 400 kHz); reset = logical board GPIO 10 (low 10 ms, high, 50 ms) | — | `firmware/touch.bin` (type 3) | `pre-consolidation:g2/components/apollo_main/core_overlay/drv_cy8c4046fni.c:173-200`; `g2/docs/research/g2-touch-identity-recovery.md:15`; `g2/docs/research/g2-touch-i2c-protocol-recovery.md` | FW High |
| **TDK ICM-45608** | 6-axis IMU, FIFO, EDMP (tap, tilt, head-up, AID) | **I2C bus 4** = IOM4 (bus table `0x20000C4C`) | 7-bit **0x69**, WHO_AM_I 0x81 | IOM4 vector cell `0x00438068` → `hal_i2c_irq_handler`; INT1 (active-high, pulsed, push-pull) → Apollo **GPIO38** (handler `0x004A6AE8`) | I2C pads GPIO34/35; power = logical board GPIO 1 | I2C 1 MHz | — | `pre-consolidation:g2/components/apollo_main/core_overlay/imu_icm45608.c:489-503`; `g2/docs/research/g2-imu-icm45608-recovery.md`; `g2/tools/manifests/g2-hal-i2c-function-map.tsv` | FW High (part, addr); Medium (IOM4) |
| Magnetometer | Compass | ICM-45608 auxiliary I2C master | 0x1E, reg 0x01 = 0x45 | — | — | — | — | `pre-consolidation:g2/components/apollo_main/core_overlay/imu_icm45608_tdk_port.c:7,25-33`; chip ID 0x45 equals `ICT1531X_WHOAMI 0x45` in the vendored TDK driver (`g2/third_party/invensense-icm45608/src/Ict1531x/Ict1531x.h:33`); COM: g2flash README (compass). Stock links the TDK `Ict1531x.c` driver at `0x0055D588..0x0055D7D8` (matches `invensense-icm45608` `b79ae575`) | FW Medium (driver); part INF High (TDK ICT1531x) |
| **TI OPT3007** | Ambient light for auto brightness, master temple only | **I2C bus 2** (`hal_i2c_transfer_full(2, 0x45, …)` at `0x513748`) | Fixed 0x45 (DS); mfr ID reg 0x7E = 0x5449, dev ID reg 0x7F = 0x3001 (DS) | — | I2C pads GPIO25/26 (IOM2); rail = GPIO134 (shared), 5 ms after power-on | I2C 400 kHz | — | `g2/docs/research/g2-opt3007-registers-recovery.md:13-14` (driver path `driver\sensor\als\opt3007\`); COM: g2flash `patches/als_sensor.c:9-11` (reads 0x5449/0x3001 at 0x45, calls it OPT3001) | FW High (driver); see note |
| **Nordic nPM1300** (via `npmx` v1.0.1-1-ge1aaec5) | PMIC, charger family 1 | **I2C bus 7** (IOM7), 16-bit register addresses high byte first | **0x6B** | nPM1300 GPIO1 = IRQ out (INF: to Apollo GPIO4, pin-table handler `0x00510FD8`); events: watchdog warning, VBUS detected/removed | — | I2C 400 kHz | — | `g2/docs/research/g2-npmx-main-driver-recovery.md:27`; bus/address: `npmx_main_driver.c` `[0x00511002,0x00512BB1]` in [`findings-hardware-drivers.md`](../../g2/docs/reference/findings-hardware-drivers.md) | FW High |
| **TI BQ25180** | 1-cell linear charger, family 2 | **I2C bus 7** (IOM7, pads GPIO22/23) | **0x6A** | — | — | I2C 400 kHz | — | `g2/docs/research/g2-chg-bq25180-recovery.md:27` | FW High |
| **TI BQ27427** | Fuel gauge, family 2 | **I2C bus 7** (IOM7, pads GPIO22/23) | **0x55** | — | — | I2C 400 kHz | — | `g2/docs/research/g2-chg-bq27427-recovery.md:73` | FW High |
| Buzzer (part unknown) | Notes and alert sounds; 9 predefined "voices" | Apollo TIMER PWM; **TIMER7** (function 4, output 14) per `drv_buzzer.c` `[0x005026BC,0x00502D55]` (conflict with the earlier TIMER15 reading) | — | — | **GPIO145** | 1 kHz, 30 % default; f = 1,000,000 / (0xFFFF − reload); timer clock 96 MHz / (4 << 2·sel), init sel 0 = 24 MHz | — | `g2/docs/research/g2-drv-buzzer-recovery.md:67-69`; COM: g2flash `zlib_glue.c` ("PWM piezo buzzer"); TIMER7/GPIO145: [`findings-hardware-drivers.md`](../../g2/docs/reference/findings-hardware-drivers.md) | FW High (exists); TIMER7/GPIO145 FW Medium; TIMER15 Low |
| PDM microphone(s) | Production mic test / generic capture | Apollo **PDM0** | — | PDM0 IRQ 48 (prio 4), vector cell `0x00438100` | GPIO50/51 | PDM clock 24 MHz HFRC / 15 = 1.6 MHz, SINCRATE 25, +1.5 dB, HPF code 3, mono left (config RAM `0x20000900`/`0x20000928`); 16 kHz implied (INF) | — | `g2/docs/research/g2-drv-pdm-recovery.md`; `g2/docs/research/g2-drv-pdm-production-recovery.md`; pads/config: [`findings-hardware-drivers.md`](../../g2/docs/reference/findings-hardware-drivers.md) | FW High |
| DMICs on GX8002 | Primary voice mics | GX8002 DMIC inputs | — | — | — | — | — | `g2/docs/research/g2-service-codec-host-recovery.md` (cmds 0x0B–0x0E) | FW High |
| Board-ID resistor strap | Board revision (and nominally charger family; see §2.1) | Apollo ADC slot 3, single-ended channel 3 | `[BSP]hw_version: %d, hw_adc_val: %d` | — | **GPIO16** (divider) | 3 samples, mV = sample × 1190 >> 12 | — | `g2/docs/research/g2-s200-board-config-recovery.md`; `board_hw_version_detect` `0x00509134` | FW High |
| Lens-side strap | L/R identity | GPIO or ADC (INF) | — | — | — | — | — | `pre-consolidation:g2/components/apollo_main/core_overlay/lens_side_policy.c` | FW Medium |

Official component count: "Four Microphones" [DS/official spec,
https://support.evenrealities.com/hc/en-us/articles/13499229138959-Specs].
The split between GX8002 DMICs and Apollo PDM mics per temple is not
established.

Not found anywhere in the firmware analysis: PSRAM, NFC, camera, speaker or
audio amplifier, SDIO, USB on the glasses (USB clock only touched in a clock
sweep), Goodix silicon (the `util_error_check.c` helper is copied Goodix
GR551x SDK code, not a Goodix chip) [FW, `g2/docs/upstream-inventory.md`].

**OPT3007 vs OPT3001.** The stock driver path and register-map function are
named `opt3007` [FW]. g2flash names the part OPT3001 from its IDs. The OPT3007
datasheet gives the same fixed address (0x45) and the same ID values
(manufacturer 0x5449, device 0x3001) as the OPT3001, so the IDs cannot
separate the two. The firmware naming favours OPT3007 [INF]. The OPT3007 is a
0.856 mm-class PicoStar part (DS), which fits a temple.

**Conflicts raised by the 2026-10-21 driver reconstruction.** Both readings are kept. Each is
listed in [open question 22](README.md#open-questions--measure-on-hardware):

- **Vendor HCI `0xFFF2`.** Older notes call it the local-supported-feature mask. The BLE-host
  reconstruction reads it as an 8-byte NVDS write. In that reading, the feature-bit change is
  `HciGetLeSupFeat` `0x00530D3C` clearing bit 1 instead.
- **Buzzer timer.** The older reading is TIMER15; the reconstruction reads TIMER7.
- **GX8002 DFU stage-2 baud.** Older notes give 1.5 Mbaud, from the header. The reconstruction
  shows that 1,000,000 is always sent.
- **BQ25180 limits.** The register image `… 06 …` (ILIM code 6) is 700 mA, not the 1000 mA
  argument. ICHG code 0x24 is 90 mA, not 91 mA (§7.1).
- **Touch host commands.** The numbering is superseded by
  [findings-touch-case.md §1.4](../../g2/docs/reference/findings-touch-case.md) (see §4).

### 2.1 Board identification and charger family

`board_hw_version_detect` `0x00509134` reads the GPIO16 divider. It writes a 4-byte board-info
record at RAM `0x20074368`: +0 charger family, +1 hw_version, +2 mV. Selector `0x0050938E` returns
pointers into it.

| ADC window (mV) | hw_version | CLI name (`0x0057E6CC`) | Family byte written |
|---|---|---|---|
| 950–1050 | 6 | "Unknown" | 1 |
| 550–650 | 3 | EVT3 | 1 |
| 300–400 | 4 | DVT1 | 1 |
| 100–250 | 5 | DVT2 | 1 |
| other | 0xFF | "Unknown" | 1 |

- The CLI table names codes 1 EVT1, 2 EVT2, 3 EVT3, 4 DVT1 and 5 DVT2 (strings at ROM
  `0x0078E1A4..0x0078E1C4`). The ADC bins produce only 3–6.
- `power_init` `0x005093D4` selects the charger family: 1 starts the nPM1300 (`0x00512644`); 2
  starts the BQ25180, then the BQ27427.
- Every 2.2.6.10 ADC bin writes family 1. No other code writes the byte; the only literal for the
  cell is at `0x00509494`, and all selector callers only read it.
- INF (High): the BQ25180 + BQ27427 path is present but unreachable in this build.

Tags: FW High (decompile `0x00509134`, float thresholds at `0x00509448..0x00509464`); INF as
marked.

## 3. Buses and pads (Apollo510B side)

| Instance | Base address (DS) | Pads | Mode | Rate | Device | Evidence | Tag |
|---|---|---|---|---|---|---|---|
| MSPI0 | `0x40060000` | Not recovered | Serial for commands/reads; quad for pixels; async write with 3 s semaphore wait | IRQ 20 | Display panel | `g2/docs/research/g2-uled-mspi-common-recovery.md:94-116` | FW High |
| MSPI1 | `0x40061000` | GPIO49 CE0, GPIO95–98 D0–D3, GPIO103 SCK, GPIO104 DQS | SPI mode 0; READ 0x03, QREAD4B 0x6C (8 dummy), PP 0x02, SE 0x20 (4 KiB), EN4B 0xB7 | 96 MHz; IRQ 21; TCB 1 KiB; timing scan fallback `{TxNeg1,RxNeg0,RxCap1,TxDQS6,RxDQS14,TA8}` | MX25U25643G | `g2/docs/research/littlefs-g2-mspi-transport-audit.md:120-176,280+` | FW High |
| XIP window | MSPI1 aperture `0x80000000–0x83FFFFFF` (DS) | — | 32 MiB mapped read-only at `0x80000000`; firmware treats `0x80000000–0x81FFFFFF` as the NOR window (OTA storage type 1 accepts `[0x80000000,0x82000000)`) | — | MX25U25643G | littlefs MSPI audit:238-244; [`findings-hardware-drivers.md`](../../g2/docs/reference/findings-hardware-drivers.md#nor-flash-xip-and-storage) | FW High |
| IOM "I2C bus 4" | IOM4 `0x40054000` | GPIO34/35 (SCL/SDA) | I2C master, command queue 0x800 B at `0x2035CE18` | 1 MHz | ICM-45608 @0x69, magnetometer @0x1E behind it | `imu_icm45608.c:492-503`; bus table `0x20000C4C` (module 4), config `0x20000C38`, pins ROM `0x00786030` | FW High |
| IOM "I2C bus 5" | IOM5 `0x40055000` | GPIO47/48 (SCL/SDA) | I2C master | 400 kHz | CY8C4046FNI @0x0C | `drv_cy8c4046fni.c:173-200`; bus table module 5, config `0x20000C0C`, pins ROM `0x00786040` | FW High |
| IOM "I2C bus 7" | IOM7 `0x40057000` | GPIO22/23 (SCL/SDA) | I2C master | 400 kHz | nPM1300 @0x6B, BQ25180 @0x6A, BQ27427 @0x55 | charger docs; bus table module 7, config `0x20000C0C`, pins ROM `0x00786050` | FW High |
| IOM "I2C bus 2" | IOM2 `0x40052000` | GPIO25/26 (SCL/SDA) | I2C master | 400 kHz | OPT3007 @0x45 | `0x513748`, `0x513780`; bus table module 2, config `0x20000C0C`, pins ROM `0x00786020`; [`findings-hardware-drivers.md`](../../g2/docs/reference/findings-hardware-drivers.md) | FW High |
| IOM6 | `0x40056000` (listed reserved in DS) | Internal | SPI master, mode 0 | 16 MHz | BLE controller HCI | `0x004B48A6` → `0x0052DD94(6,…)`; config `0x200001B4` | FW High |
| `HAL_I2CInit` | IOM0–IOM7 | — | Initialises eight IOM slots with a mutex per bus | — | — | `g2/tools/manifests/g2-hal-i2c-function-map.tsv` row 4; `g2/docs/research/g2-hal-i2c-recovery.md` | FW High |
| UART3 | `0x4003C000` (DS) | Not recovered | 8N1 assumed | 115,200 runtime; 230,400 / 1,000,000 / 1,500,000 in codec DFU | GX8002B | `service_codec_porting.c:56-81`; codec docs | FW High |
| UART, logical "channel 2" | Not recovered | Pogo contacts | `5A A5 FF` frames | Not recovered | Charging case | `g2/docs/research/g2-box-uart-mgr-recovery.md`; "pogo UART module/pins" in `g2/docs/hardware-validation-2026-08-23.md:165` | FW Medium |
| UART (TinyFrame `uart_sync`) | Not recovered | Not recovered | TinyFrame | Not recovered | Peer temple | `g2/docs/research/g2-uart-sync-recovery.md` | FW Medium |
| I2S0 / I2S1 | `0x40208000` / `0x40209000` (DS) | Not recovered | **I2S0** RX-only slave (GX8002 is clock master); 2 ch, 32-bit slots, data delay 1, 16-bit samples; ping/pong DMA `0x20364E18`/`0x20365A98`, 3,200 B per block | 2 ch, 16 kHz, 16-bit; I2S0 IRQ 44 prio 4 | GX8002B | `g2/docs/research/g2-drv-gx8002b-recovery.md`; `g2/docs/research/g2-peripheral-register-cluster-audit.md` (`0x0044B158`); I2S0: [`findings-hardware-drivers.md`](../../g2/docs/reference/findings-hardware-drivers.md) | FW High |
| PDM0 | `0x40201000` (DS) | GPIO50/51 | PDM → 16-bit PCM (bits 23..8); generic 160 words → 320 B (640-B DMA blocks); production 1,600 samples → 3,200 B (6,400-B DMA blocks) | IRQ 48; PDM clock 1.6 MHz | PDM mic(s) | PDM docs; pads: findings-hardware-drivers | FW High |
| TIMER | `0x40008000` (DS) | GPIO145 (TIMER7 OUT0, see conflict note in §2) | PWM | 96 MHz basis | Buzzer | `g2/docs/research/g2-peripheral-register-cluster-audit.md` (`0x004801FC`); `drv_buzzer.c` | FW Medium |
| GPIO | `0x40010000`, PADKEY `0x40010400` (key 0x73) | 224 GPIO register slots (96 bonded on BGA, DS) | — | Group IRQ `GPIO0_607F` (GPIO96–127), handler `0x004B80BE`, vector cell `0x0043812C` | Likely BLE controller or touch attention (INF) | `gpio_pinconfig.c:12-58`; `g2/docs/memory-map.md` | FW High / Medium |
| ADC | GPADC `0x40038000` (DS) | GPIO16 | Board-ID read (slot 3); AmbiqSuite 5.1.0 `am_hal_adc` unchanged | — | Resistor strap | board-config doc; §2.1 | FW High |
| UART0 | `0x40039000` | Not recovered | DMA, writer semaphore; break/parity/framing counters | IRQ 15 | Peer temple (TinyFrame `uart_sync`) | UART channel table RAM `0x20000D2C` (IRQ = module + 15) | FW Medium |

Board pin table (ROM `0x00686DB8`, 97 × 12-B rows `{pad, mode, level, int_dir, handler}`,
initialised by `0x0053A454` from `board_init` `0x005093AC`) [FW High]:

| Pads | Use in the table |
|---|---|
| GPIO4, GPIO27, GPIO29, GPIO38 | Interrupt inputs on GPIO channel 0 (prio 4): GPIO4 is INF the nPM1300 IRQ (handler `0x00510FD8`); GPIO27 is touch attention; GPIO29 is the GX8002 event; GPIO38 is IMU INT1 |
| GPIO9, GPIO10, GPIO134 | Outputs, initially high. GPIO134 is the shared codec/sensor rail; product-test command 0x47 drives it high through WTS4 `0x4001044C` |
| GPIO7, 11, 45, 68, 128, 129, 142, 143, 144, 146, 147 | Outputs, initially low (GPIO143/146 are GX8002 power steps) |
| 22/23, 25/26, 34/35, 47/48, 49, 50/51, 95–98, 103, 145 | Left to their peripheral (I2C, MSPI1, PDM, buzzer) |
| 64–67, 69, 72, 73 | Left to a peripheral, owner not assigned (INF Low: MSPI0 panel pads) |
| GPIO104 (MSPI1 DQS) | Disabled |
| GPIO16 | HW-ID ADC, configured by `board_config.c` (ROM `0x0078EE8C`) |

BLE controller pins (GPIO149, 93, 136, 117, 15) are configured by the HCI driver, not by this
table.

Other peripheral bases seen in firmware: CLKGEN `0x40004044/0x40004050`,
SYNC_READ `0x47FF0000` [FW, `g2/docs/research/g2-peripheral-register-cluster-audit.md`].
The complete Apollo510B peripheral map is on the
[Apollo510B page](components/apollo510b.md#peripheral-memory-map).

Still not recovered: display MSPI0 pads (see the INF row above), UART pads, I2S pads and panel
reset/enable GPIOs. The board-config object `[0x005093D0,0x0050968C)` holds 586 B of pinmux
constants (`g2/docs/research/g2-s200-board-config-recovery.md`). The I2C pads above come from the
bus table at RAM `0x20000C4C` in initialised data, and its pin rows at ROM `0x00786020..0x0078605F`.

Touch controller side (PSoC 4000T): I2C slave on SCB1 `0x40250000` (IRQ 7),
attention on PRT4 pin 0 active-low (DR_CLR `0x40040444`, DR_SET
`0x40040440`), CapSense MSCLP0 `0x40290000`; ports PRT2/3/4 used [FW,
`g2/docs/research/g2-touch-identity-recovery.md:43`].

## 4. Inter-processor links

| Link | Transport | Framing / protocol | Evidence | Tag |
|---|---|---|---|---|
| Apollo ↔ BLE controller | HCI. Cordio host `hci/ambiq/` port + Ambiq HCI driver. Blocking; 8×260-B TX queue; 256-B RX; 10 s heartbeat; failure ⇒ radio shutdown/boot + `DmDevReset`. Physical layer SPI (INF: Apollo510B datasheet says the BLEC uses an SPI subordinate HCI transport with flow control); FW: IOM6, SPI mode 0, 16 MHz (config `0x200001B4`) | H4-style HCI packets (`hciTrSerialRxIncoming`); vendor cmds `0xFCC4` RF power, `0xFC43` BD addr, `0xFFF2` local-supported-feature mask (8-B payload) | Stock emitter/reset sequence; official Ambiq Zephyr `2e347415`; `g2/docs/memory-map.md:3431-3491` | FW High (HCI) / INF (SPI) |
| Apollo ↔ GX8002B control | UART3, 115,200 | `BUXX` magic; 14-B header `{magic4, cmd u16, seq u8, flags u8, len u16, hdrCRC32}`; body ≤16 B + optional 4-B CRC; 3 retries. Cmds 0x02 version, 0x07 beamforming, 0x08 wakeup mode, 0x0B mic gain, 0x0C DMIC open, 0x0D DMIC close, 0x0E 1-bit mic delay, 0x0F I2S output, 0x70 mic state | `g2/docs/research/g2-service-codec-host-recovery.md:29-45` | FW High |
| Apollo → GX8002B firmware load | UART3 | NationalChip grus boot: `0xEF` sync → `M`; `'Y'` + stage-1 words; `wfb`/`OK`; baud switch (1 Mbaud negotiated, 1.5 Mbaud stage 2 per header); `'S'` + checksum + size; `boot>` CLI; `serialdown 0 <size> 8192`, `~sta~`/`~fin~`, `[Result]: SUCC` | `g2/docs/research/g2-service-codec-dfu-recovery.md:46-48`; `g2/docs/research/g2-codec-fwpk-segments-recovery.md` | FW High |
| GX8002B → Apollo audio | I2S + GX GPIO2 notification line | 2 ch, 16 kHz, 16-bit PCM (GX pins 7–10 mux mode 3) | `g2/docs/research/g2-drv-gx8002b-recovery.md`; `g2/docs/source-only-goal.md` | FW Medium–High |
| Apollo ↔ touch PSoC | I2C bus 5 @0x0C + attention GPIO | Runtime: 1–16 B command, cmd 0 version, 1 read baseline, 2 read long-press threshold, 3 save baseline, 4 write gesture cfg (u16 1–65535 ms), 5 enter DFU, 6 read sensor report; reply `{id, status 0/0xFF, 0x17}`; 16-B event `{type, payload[3], baseline u16, channel u16, prox u16, gesture u16}`. DFU: `0x01 | cmd | len16le | payload≤32 | cksum16 | 0x17`; cmds 0x38 enter, 0x4C metadata, 0x37 packet, 0x49 program 128-B row, 0x31 verify, 0x3B exit. **Conflict:** the runtime command numbering here is superseded by [findings-touch-case.md §1.4](../../g2/docs/reference/findings-touch-case.md): 1 version, 2 enter DFU, 3 last event report (16 B), 4 diffs (10 B), 5 save baseline, 6 baseline u16, 7 write threshold (ACK `07 00 17`), 8 read threshold | `g2/docs/research/g2-touch-i2c-protocol-recovery.md`; host driver `drv_cy8c4046fni.c` | FW High |
| Temple ↔ temple | TinyFrame over UART (medium INF: frame FPC) | SOF 0x01; ID/LEN/TYPE 2 B big-endian; CRC-16/ARC; 24 KiB max payload; 6-byte handshake at start; role-qualified service records `0x0103` BLE status, `0x0105` charger SOC sync (12 B: id, len, src role, dst role, {soc, is_charging}) | `g2/docs/research/g2-uart-sync-recovery.md`; `g2/docs/research/tinyframe-wire-format-recovery-audit.md`; `g2/docs/research/g2-charger-common-recovery.md:52` | FW Medium |
| Glasses ↔ case | UART over pogo pins | `5A A5 FF <cmd>` + payload + 8-bit additive checksum seeded with `len-2`; header search in the first 4–5 bytes; 5 rotating 1 KiB RX slots; see [g2-case.md](g2-case.md) | `g2/docs/research/g2-case-uart-update-source-closure.md:9-12`; `g2/docs/research/g2-box-uart-mgr-recovery.md:68` | FW High |
| Glasses ↔ phone | BLE GATT (EUS, ESS, EFS, NUS, Even OTA, ANCS client) | "TPL" `0xAA` multipart, 8-B header, payload ≤0x1000, CRC-16/CCITT (0x1021, init 0xFFFF) on final fragment, nanopb payloads | `g2/docs/research/g2-ble-transport-profiles-recovery.md`; `g2/docs/research/g2-transport-protocol-recovery.md:66-100`; COM: https://github.com/i-soxi/even-g2-protocol | FW High |
| Glasses → R1 ring | BLE, G2 is central | Discovers a 128-bit service with TX/RX/CCC handles; CCC writes at 500/700/900 ms; ring events relayed to phone via protobuf service `0x91` | `g2/docs/research/g2-ble-ota-ring-profiles-recovery.md`; `pre-consolidation:g2/components/apollo_main/core_overlay/ble_ring_profile.c:20-80` | FW High |

## 5. Display pipeline

| Step | Detail | Evidence | Tag |
|---|---|---|---|
| Render | LVGL v9.3-dev fork renders in L8 (8 bpp) with NemaGFX 1.4.12 / NemaVG 1.1.8 on the Apollo GPU; output converted to A4 (4 bpp) at **576×288** (0x14400 B). Root screen 640×480 with eight 72×288 bands | `g2/docs/research/lvgl-version-recovery-audit.md` | FW High |
| Blit | `buffer_sync_to_fb` (`driver\uled\display_preprocess.c`) uses the GPU to place the source region into a 640×480 4-bpp panel framebuffer (even-X constraint) | `g2/docs/research/g2-uled-display-preprocess-recovery.md` | FW High |
| Panel select | ULED manager reads config key byte: `0x06` ⇒ Hongshi A6N-G (type 1), otherwise JBD4010 (type 0); 64-B ops table | `g2/docs/research/g2-uled-manager-recovery.md:50` | FW High |
| Transfer | MSPI0 QSPI, 320 B per scanline (640 × 4 bit) | uled docs | FW High |
| JBD4010 commands | 0x66, 0x99, 0x06, 0x01, 0xC0, 0x97 (latch after async full frame), 0x73, 0x36, 0x46, 0x31, 0xA3, 0xA9; chip ID 0x9F, die ID 0x81, status 0x05/0x35, modes 0x71–0x74, offsets X 2..22 / Y 2..18 | `g2/docs/research/g2-uled-jbd4010-recovery.md` | FW High |
| A6N-G commands | Bank/register/value triples (50-B init stream, 0xFF delay, 0xEE timer markers); brightness reg E2 = `(in*250-451)/98+5`; offsets EF/F0 latched by D9=BF/D9=FF | `g2/docs/research/g2-uled-a6ng-recovery.md` | FW High |
| Recovery | Status check → power cycle / reconfigure / redraw; +5 X shift when flag set and BLE state 2 | uled docs | FW High |
| Panel ops record | A 64-B record selected by the type byte at +0x3C (0 = JBD4010 ROM `0x0070B024`, 1 = A6N-G ROM `0x0070AFE4`), published at RAM `0x20074530`. MSPI0 completion uses a binary semaphore at `0x20074534`, interrupt mask 0x1A80. JBD4010 pixel write 0x62 uses address word `((row<<10)&0x7FC00 \| col&0x3FF)<<8 \| 0xFF`; the status-check reply byte 0 must be 0x90. The A6N-G health check needs reg 0xBE = 0x84 (ASIC), reg 0x62 = 0x77/0x57 (panel), and bit 5 of the mirror read of reg 0xD8 | [`findings-hardware-drivers.md`](../../g2/docs/reference/findings-hardware-drivers.md) | FW High |
| Factory panel data | Panel drive current at NVDB `nvSysDt`+0x2E; canvas x/y offsets at +0x2C/+0x2D; 40 legacy PSNs (ROM `0x006D3358`) change the display offset | `service_nvdb.c` | FW High |
| GPU blend | The Ambiq LVGL draw backend blends ARGB8888 layers with `NEMA_BL_SRC_OVER \| NEMA_BLOP_SRC_PREMULT` (0x04000501) and other layers with `NEMA_BL_SIMPLE`. GPU init `0x0059FAE0` runs in `board_init` | findings-hardware-drivers | FW High |
| Brightness | Per-side adjustment; ALS-driven auto brightness on master temple | `g2/docs/research/g2-als-dependency-boundary.md`; COM g2flash `als_sensor.c` | FW, COM |
| Panel spec | 640×350 visible, FoV 27.5°, 60 Hz, 1200 nits, green, binocular waveguides | https://support.evenrealities.com/hc/en-us/articles/13499229138959-Specs | Official spec |
| Colour | Green monochrome microLED | Official spec (above); firmware confirms only 4-bit grayscale | Official / INF |

Community note: g2flash reports the panels accept full 640×480 while the
EvenHub API exposes 576×288 [COM, https://github.com/jimrandomh/g2flash].

**G1 (for comparison):** JBD 0.13" 640×480 green microLED
[PR, https://www.microled-info.com/even-realities-launch-new-ar-smart-glasses-powered-jbd-monochrome-microled ;
https://kguttag.com/2024/08/18/even-realities-g1-minimalist-ar-glasses-with-integrated-prescription-lenses/].

## 6. Audio pipeline

| Path | Detail | Evidence | Tag |
|---|---|---|---|
| Voice | DMICs → GX8002B (CK804EF; NPU KWS "LVP_KWS", FFT-VAD/EVAD, IMCRA denoise, DRC, beamforming) → I2S 2 ch 16 kHz 16-bit → Apollo I2S DMA (3,200-B buffers) → `service_audio` → SSR + TDOA/angle (`service_algo.c`) → liblc3 v1.1.3 encode → BLE | `g2/docs/research/g2-service-audio-recovery.md`; `g2/docs/research/g2-drv-gx8002b-recovery.md` | FW High |
| Wake | Voice event via GX GPIO + UART `GX8002_GetVoiceEvent` | codec-host doc | FW High |
| Capture to file | Optional PCM to `/audio/*.pcm` on littlefs | `g2/docs/research/g2-service-audio-recovery.md` | FW High |
| Production mic test | Apollo PDM0; listener ID 0x10B; capture mode 1 = PDM, 0 = codec | PDM docs | FW High |
| Output | Buzzer only (PWM). No speaker path | buzzer doc; official spec lists no speaker | FW High |

## 7. Power

### 7.1 Power tree

```mermaid
flowchart TD
  CASE["Case 5 V via pogo"] --> CHG
  subgraph F1["Charger family 1"]
    NPM["nPM1300: charger, VBUS, bucks,<br/>load switches, ADC, ship mode, watchdog"]
  end
  subgraph F2["Charger family 2"]
    BQC["BQ25180 charger @0x6A"]
    BQG["BQ27427 gauge @0x55"]
  end
  CHG{{"board record 3 / board-ID ADC selects family"}} --> NPM
  CHG --> BQC
  BAT[["Temple cell 3.87 V 96 mAh 0.372 Wh"]]
  NPM --- BAT
  BQC --- BAT
  BQG --- BAT
  BAT --> AP["Apollo510B SIMO buck + LDOs<br/>(VDDH 1.71-2.2 V)"]
  AP --> GXR["GX8002 rails via GPIO 6/7/8"]
  AP --> PER["Sensors, panel, NOR"]
```

| Item | Detail | Evidence | Tag |
|---|---|---|---|
| Two charger families in one image | Family 1: nPM1300 (npmx v1.0.1-1-ge1aaec5). Family 2: BQ25180 + BQ27427. Selected by board record 3 (selector `0x0050938E` arg 3 → board-info byte 0 at `0x20074368`) | `g2/docs/research/g2-npmx-main-driver-recovery.md:27`; `pre-consolidation:g2/components/apollo_main/core_overlay/s200_board_config.c` | FW High |
| Family actually selected by 2.2.6.10 | Every hw-ID ADC bin writes family 1 (nPM1300); no code writes 2 | `0x00509134`; §2.1 | FW High; INF (High) that family 2 is unused |
| nPM1300 configuration | Charge 96 mA; discharge limit 1000 mA; termination 4450 mV normal / 4000 mV warm; VBUS limit 500 mA; NTC 100 kΩ β 4250; BUCK2 3.1 V; LDSW1 as LDO 1.8 V; VBUS detect drives case detection | `npmx_main_driver.c` `[0x00511002,0x00512BB1]`; [`findings-hardware-drivers.md`](../../g2/docs/reference/findings-hardware-drivers.md) | FW Medium–High |
| BQ25180 default image | 4.4 V regulation, 91 mA fast charge, 1000 mA input bucket, 2.8 V UVLO; register image `00 00 00 5A 24 24 1F 44 06 00 21 00 F0`. **Conflict:** the reconstruction decodes ICHG 0x24 as 90 mA and ILIM code 6 as 700 mA (argument 1000), plus 6 h safety timer and 160 s watchdog | `g2/docs/research/g2-chg-bq25180-recovery.md`; `drv_bq25180.c` `[0x0053A670,0x0053AF4B]` | FW High |
| BQ27427 data memory | {240, 80, 3100} ⇒ design energy / capacity / terminate-voltage fields; unseal key 0x80008000 | `g2/docs/research/g2-chg-bq27427-recovery.md` | FW High |
| Apollo internal regulation | SIMOBUCK / LDOREG / VREFGEN writes; SPOT manager pcm2_2 | `g2/docs/research/g2-peripheral-register-cluster-audit.md` | FW High |
| Watchdog | nPM1300 timer/watchdog on family 1 | `g2/docs/research/g2-watchdog-recovery.md` | FW High |
| PMIC watchdog | nPM1300 watchdog ≈30.7 s, reset mode, armed by `watchdog_enable` `0x0052F2E0` only when the family byte is 1 | `watchdog.c`; npmx glue | FW High |
| MCU watchdog | Apollo WDT: LFRC/64 (16 Hz), interrupt off (value 12), reset on, reset value 480 ⇒ ≈30 s; started first in `board_init` (`0x004B29D8`); config in initialised data `0x20000950` | `watchdog_start.c`; decoded `.data` | FW High |
| Brown-out policy | A brown-out reset is answered at boot with an immediate software POR (`AM_HAL_RESET_CONTROL_SWPOR`) | `startup_reason_printf` `0x005CDD6C` | FW High |
| SOC aggregation | Charger-common reports min(L, R) SOC with near-full compensation; SOC synced across temples via `0x0105` | `g2/docs/research/g2-charger-common-recovery.md:52` | FW High |
| Supply from case | "DC 3.87V from battery or DC 5V from case" | G2 test report §4 | REG |
| Label input | "Input: 5V 300mAh" (sic, as printed on the label exhibit) | https://fccid.co/fcc/2BFKR-G2 (ID label exhibit) | REG |

### 7.2 Batteries

| Item | Value | Evidence | Tag |
|---|---|---|---|
| Per-temple cell | 3.87 V, 96 mAh, 0.372 Wh | G2 test report N25071003936E §4 | REG |
| Total | 192 mAh / 0.744 Wh | https://support.evenrealities.com/hc/en-us/articles/13499229138959-Specs | Official |
| Vendor / model | Not in public exhibits | — | UNV |
| **G1** | "Glasses capacity 160 mAh 0.616 Wh"; internal photos show 2× ZWD400923H 3.85 V 80 mAh 0.308 Wh | G1 test report CTC20240955E01; G1 internal photos exhibit | REG (G1) |

### 7.3 Reset and boot sequence (main image)

| Step | Detail | Evidence | Tag |
|---|---|---|---|
| Reset | Vector slot 1 = `0x005E4233`. The handler `[0x005E4232,0x005E4241]` sets MSPLIM/PSPLIM = `0x2007D000`, then calls the IAR program entry `0x005E4254` | `startup_handlers.c` | FW High |
| C runtime | IAR scatter decompressor `0x0043A11E`: `.data` 0x4558 B to `0x20000000`; large record `0x0075D400` expands 0xBBE6E B to `0x20080000` | [`findings-hardware-drivers.md`](../../g2/docs/reference/findings-hardware-drivers.md#boot-reset-watchdog-and-power-modes) | FW High |
| `main` | `0x005CE01E`: 200 ms delay, then the auto-init runner `0x005BF0BC`, then the reset-reason report, then the thread-manager kernel start (RAM `0x200040D8`, never returns) | `main_config.c` | FW High |
| Auto-init table | ROM `0x006D1E0C..0x006D1EC3`: 23 × `{fn, priority}`, copied to RAM `0x20066A30` and sorted by ascending priority | `init_table_run.c` | FW High |
| `board_init` (priority 0, row `0x006D1E2C`) | `0x005CDD14`: latch RSTGEN status, start the MCU WDT, FPU and lazy stacking, low-power init, I/D-cache, HIGH_PERFORMANCE MCU mode, heap, NemaGFX GPU init (`0x0059FAE0`), CmBacktrace | `main_config.c` | FW High |
| Board config | `0x005093AC`: pin table, HW-ID detect, UART channels, `HAL_I2CInit`, UART power-on; then `power_init` `0x005093D4` starts the charger family | `board_config.c` | FW High |
| Reset reasons | Reported in this priority: EXT, POR, BOD (then SW POR), SWPOR, SWPOI, DBGR, WDT, AIRCR. An external-pin reset also plays buzzer effect 8 | `0x005CDD6C` | FW High |

## 8. Memory and storage

### 8.1 Apollo510B MRAM (per temple, 4 MiB `0x00400000–0x007FFFFF`)

| Range | Content | Evidence | Tag |
|---|---|---|---|
| `0x00400000–0x0040FFFF` | Ambiq secure bootloader (SBL), 64 KiB, not in EVENOTA (datasheet: "NVM-SBL") | `g2/docs/memory-map.md:27`; Apollo510B datasheet Table 4 | FW, DS |
| `0x00410000–~0x00434477` | Even bootloader `ota/s200_bootloader.bin`, 148,599 B, vectors at base | `g2/docs/memory-map.md:28-301`; `g2/tools/open_cfw.py:737-748` | FW High |
| `0x00437FE0–0x00437FFF` | 32-B OTA staging preamble of the main image | `g2/docs/memory-map.md:303-306` | FW High |
| `0x00438000–0x00794324` | Main application, 3,523,364 B | `g2/docs/memory-map.md:302` | FW High |
| `0x007FE000` | Protected bootloader update flag / record | `g2/tools/open_cfw.py:43`; COM: g2flash OTA flag 0x007FE000 | FW, COM |
| ITCM `0x00000040` | 22-B compressed scatter record (from `0x0079430E`) decompressed into ITCM (delay routine) | `g2/README.md:1345`; `g2/docs/source-coverage.md:1494` | FW High |

Datasheet split of the same MRAM: NVM0-APPL `0x00410000–0x005FFFFF`
(1.94 MB) and NVM1-APPL `0x00600000–0x007FFFFF` (2 MB) [DS]. The main image
crosses that boundary.

SRAM: DTCM `0x20000000–0x2007FFFF` (512 KiB), system SRAM
`0x20080000–0x2037FFFF` (3 MiB), ITCM `0x00000000–0x0003FFFF` (256 KiB) [DS].
Firmware: main SP `0x2007FB00`; IAR initialised-data record decompresses
17,752 B to `0x20000000`; large buffers in system SRAM, e.g. `0x2035EE18`
(8 KiB codec DFU scratch), `0x203795A0` (display config), `0x203799A0` (MSPI1
TCB); WSF pools `[0x2004FAC8,0x200523C8)`; IMU ring `0x200640A0` [FW,
`g2/docs/memory-map.md`, `g2/docs/research/littlefs-g2-mspi-transport-audit.md`].

Information spaces: INFOC `0x400C2000` (0x400 B); INFO0 / INFO1 / OTP info
windows for trims and MAC derivation [FW,
`g2/docs/hardware-validation-2026-08-23.md:158`,
`g2/docs/research/g2-nvdb-mac-recovery.md`]. Datasheet NVM_INFO0 is at
`0x42000000` (2 KiB), NVM_INFO1 at `0x42002000` (6 KiB), OTP2_INFO0 at
`0x42004000`, OTP2_INFO1 at `0x42006000` [DS].

### 8.2 External NOR (MX25U25643G, 32 MiB)

| Range (device offset) | CPU alias | Content | Evidence | Tag |
|---|---|---|---|---|
| `0x00000000–0x013FFFFF` | `0x80000000–` | Not assigned in the repository (20 MiB) | littlefs MSPI audit | FW (gap) |
| `0x01400000–0x01FBFFFF` | `0x81400000–` | littlefs v2.10.1, 3,008 × 4 KiB blocks. Dirs `/firmware`, `/ota`, `/user`, `/log`, `/audio/*.pcm`, `/log/imu_rawdata_*.csv`; `boot_count` | `g2/docs/research/littlefs-g2-mspi-transport-audit.md:260-285`; `g2/docs/memory-map.md:222-224` | FW High |
| `0x01FC0000–0x01FFFFFF` | — | Not assigned (256 KiB). **Superseded** by the two FlashDB rows below | same | FW (gap) |
| `0x01FC0000–0x01FF7FFF` | — | FlashDB FAL partition `kvdb`, database `sysenv` (224 KiB; magic `kvMagic` 0x5A000020) | `g2/docs/reference/memory-map.md` §2; `service_kvdb.c` | FW High |
| `0x01FF8000–0x01FFFFFF` | — | FlashDB FAL partition `NVdb`, database `factory` (32 KiB; `nvMagic` 0x55550022): PSN/BSN, ALS `lux_base`, panel current, IMU/AG calibration, MAC, buzzer, production mode | `g2/docs/reference/memory-map.md` §2; `service_nvdb.c` | FW High |

MX25U25643G driver behaviour (`drv_mx25u25643g.c`, object `[0x0046F4A4,0x00471163]`) [FW High]:
- RDID 0x9F must return 0x2539C2 (packed JEDEC C2 25 39).
- Reset is RSTEN 0x66 → 1 ms → RST 0x99 → 50 ms.
- RDCR 0x15 bit 5 means 4-byte address mode (entered with EN4B 0xB7).
- Quad enable is SR bit 6, written with mask 0xC3, which also clears BP0..3.
- The MSPI timing scan runs 36 base settings × RxDQSDelay 0..31 and keeps the longest matching
  run (stored at RAM `0x20000820`).

The factory OTP PSN copies are in INFOC: 8 × 16 B at `0x400C2340`. A valid slot starts with "S2",
and the last valid slot wins.

Update staging presumably uses littlefs `/ota`; the bootloader reads the
32-B header, checks CRC and programs MRAM in place, single slot, no rollback
[FW, `g2/docs/memory-map.md:1747-1748`].

### 8.3 EVENOTA payloads and targets

| Payload (type) | Size | Target | Evidence |
|---|---:|---|---|
| Main (0) | 3,523,396 | MRAM `0x00438000` (32-B preamble: `0x04<<24 | size`, zlib CRC-32, type 0xCB, run addr) | `g2/tools/open_cfw.py:751-774,2318-2340` |
| Bootloader (1) | 148,599 | MRAM `0x00410000` | `g2/manifests/g2-2.2.6.10.json` |
| Touch (3) | 34,464 | PSoC flash `0x0` (prefix `[0,0x867C)`), FWPK wrapper | touch docs |
| Codec (4) | 326,092 | Seg 1 UART boot container (stage 1 → IRAM `0x10000000`, stage 2 → `0x10002800`); seg 2 → codec NOR offset 0 | codec docs |
| EM9305 (5) | 211,948 | `0x00300000` (224 B), `0x00300400` (656 B), `0x00302000` FHDR, `0x00302400` app (210,888 B; 66-word ARC vector table) | `g2/docs/memory-map.md:1778-1790` |
| Case (6) | 55,784 | STM32 `0x08000000` / inactive alias `0x08040000` | `g2/docs/memory-map.md:1754-1776` |

## 9. RF

| Item | L temple | R temple | Evidence | Tag |
|---|---|---|---|---|
| Band / channels | 2402–2480 MHz, 40 ch, fc = 2402 + 2k MHz | same | G2 test report §5 | REG |
| Modulation tested | GFSK, BLE 1 Mbps only | same | §5 | REG |
| Conducted peak power 2402 / 2440 / 2480 MHz | −1.66 / −1.69 / −1.99 dBm | −1.40 / −1.61 / −2.06 dBm | §8.1.2, §8.2.2 | REG |
| Tune-up | −2 ± 1 dBm (max −1.0 dBm = 0.794 mW) | same | RF exposure exhibit | REG |
| PSD (dBm/3 kHz) | −17.27 / −17.37 / −17.64 | −16.96 / −17.16 / −17.58 | §8.1.5, §8.2.5 | REG |
| −6 dB bandwidth (MHz) | 0.708 / 0.700 / 0.674 | 0.692 / 0.711 / 0.716 | §8.1.3, §8.2.3 | REG |
| 99 % OBW (MHz) | 1.019 / 1.022 / 1.021 | 1.015 / 1.021 / 1.019 | §8.1.4, §8.2.4 | REG |
| Duty cycle (test mode) | 62.4 % | 62.4–62.6 % | §8.1.1, §8.2.1 | REG |
| Antenna | LDS, gain −1.81 dBi | LDS, gain −2.06 dBi | §4, §7.9 | REG |
| Antenna passive efficiency (vendor data, 3 colours) | ≈15–16 % | ≈15–16 % | Top-Link spec PS-24001542… | REG |
| TRP / TIS (vendor active test, 1M 200 B) | ≈ −1.1 to −1.8 dBm / ≈ −87.3 to −88.6 dBm | ≈ −1.1 to −1.7 dBm / ≈ −87.1 to −88.4 dBm | same | REG |

Full regulatory detail, including antenna part numbers and G1 comparison, is
in [regulatory.md](regulatory.md).

Firmware side: BLE 5.4 controller with extended connections, ISO/BIG and
PAwR code present; host Cordio with legacy pairing and LE Secure
Connections; peer MTU floor 247; static-random address derived from Apollo
chip IDs (`service_nvdb_mac.c`) [FW, `g2/docs/functional-capability-ledger.md`,
`g2/docs/research/g2-nvdb-mac-recovery.md`]. Official: BLE 5.4
[Official spec page]. Datasheet capability of the Apollo510B BLEC: −20 to
+6 dBm TX, −97 dBm RX at 1 Mbps [DS]; the FCC test shows the product is
configured near −2 dBm.

Firmware facts from the 2026-10-21 BLE-host reconstruction [FW, `g2/docs/reference/findings-hardware-drivers.md`]:

- Vendor command 0xFCC4 requests the +6 dBm RF power level. The FCC conducted figure is about
  −2 dBm. INF: the level is a controller setting, not the measured antenna-port power. This
  difference is not explained.
- The ring link runs TX on LE Coded PHY S8 and RX on 1M PHY.
- Connection profiles:
  - Slow: interval 72–84 (90–105 ms), latency 4, timeout 6 s. The link switches to it 60 s after
    connecting.
  - iOS and Android fast: interval 12–24, latency 0, timeout 6 s.

## 10. G1 facts that inform G2 (G1 only)

| Fact | Evidence | Tag |
|---|---|---|
| G1 MCU is Nordic nRF5340 (dual Cortex-M33, Zephyr/NCS) | https://github.com/JohnRThomas/even_realities_decomp ; https://github.com/nodesbio/cue/issues/16 | COM (G1) |
| G1 used 2 temple PCBs, one BLE link per arm, and an "NFC RX antenna" for 13.56 MHz inductive charging from the case | G1 internal photos exhibit; G1 case test report | REG (G1) |
| G1 BLE 5.2, 1 and 2 Mbps, 1.25 dBm peak conducted, LDS antenna 8181060001 −3.25 dBi | G1 test report CTC20240955E01; G1 operational description | REG (G1) |
| G2 moved to wired contact charging (pogo) and a wired L/R link; BLE 5.4 | Official blog and spec page | Official (G2) |
