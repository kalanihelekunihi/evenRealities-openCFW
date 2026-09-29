# Ambiq Apollo510B (and Apollo510)

**Used in:** G2 glasses, one per temple, as the application processor.
Tags: [vocabulary](../README.md#confidence-vocabulary).

## Identification

| Evidence | Tag |
|---|---|
| Vendor build tree `D:\01_workspace\s200_ap510b_iar_git\` (S200 + AP510B + IAR) | FW High (`g2/docs/research/g2-s200-board-config-recovery.md:4`) |
| "Apollo510B internal MRAM — each temple"; raw Cortex-M55 Thumb-2 XIP image | FW High (`g2/docs/memory-map.md:23`; `g2/docs/research/cordio-ble-stack-identity-audit.md`) |
| AmbiqSuite 5.1.0 HAL/CMSIS in the main image | FW High (`g2/docs/upstream-inventory.md`) |
| "Even G2 … use the Apollo 510 microprocessor from Ambiq … 4-MB MRAM" | PR (https://www.electronicdesign.com/technologies/embedded/video/55404374/electronic-design-spot-helps-knock-down-edge-ai-noise) |
| `MRAM_END = 0x00800000 # end of Apollo510b 4 MB internal MRAM` | COM (https://github.com/jimrandomh/g2flash) |

## Documents

| Document | URL |
|---|---|
| Apollo510B product page | https://ambiq.com/product/apollo510b/ |
| Apollo510B SoC datasheet (DS-A510B-1p1p0, 266 pages; read for this page) | https://contentportal.ambiq.com/documents/20123/4530417/Apollo510B-SoC-Datasheet.pdf |
| Apollo510 product page / datasheet | https://ambiq.com/product/apollo510/ ; https://contentportal.ambiq.com/documents/20123/2877485/Apollo510-SoC-Datasheet.pdf |
| Apollo510B announcement | https://ambiq.com/news/ambiq-announces-apollo510b/ |
| CNX Software summary | https://www.cnx-software.com/2025/09/01/ambiq-apollo510b-ultra-low-power-cortex-m55-edge-ai-mcu-adds-bluetooth-le-5-4/ |
| Keil CMSIS pack (Apollo_DFP, includes SVD) | https://www.keil.arm.com/packs/apollo_dfp-ambiqmicro/versions/ |
| AmbiqSuite 5.1.0 HAL import into Zephyr `hal_ambiq` (commit 5efc0228…) | https://github.com/zephyrproject-rtos/hal_ambiq/commit/5efc0228528a8adce5eae0d226fac85d2551eb3b |
| Zephyr Apollo510 EVB board page | https://docs.zephyrproject.org/latest/boards/ambiq/apollo510_evb/doc/index.html |

## Key specifications (DS, Apollo510B datasheet)

| Item | Value |
|---|---|
| Core | Arm Cortex-M55 with Helium (MVE), up to 250 MHz (96 MHz low-power mode), FPU (half/single/double), TrustZone, MPU |
| Caches / TCM | 64 kB I-cache, 64 kB D-cache; ITCM 256 kB, DTCM 512 kB |
| Memory | 4 MB MRAM (NVM); 3 MB system SRAM (3.75 MB with TCM); boot ROM 128 kB |
| BLE | Integrated BLE 5.4 controller (BLEC): 48 MHz 32-bit co-processor, 64 kB ROM, 512 kB flash, 64 kB RAM, SPI HCI transport; −20 to +6 dBm TX; −94 / −97 / −103 dBm RX (2M / 1M / 125k) — see [em9305.md](em9305.md) |
| Graphics / display | 2.5D GPU with VG, 96/250 MHz; display controller; MIPI DSI 1.2 up to 768 Mbps; QSPI display interface up to 125 MHz DDR; up to 640×480 at 60 FPS |
| Serial | 7× I2C/SPI managers (IOM6 not pinned out), 1× 2/4/8-bit MSPI, 1× 2/4/8/16-bit MSPI (1.2 V), SPI subordinate, 4× UART, USB 2.0 HS/FS, 2× SDIO/eMMC |
| Audio | 1× PDM stereo DMIC, 2× full-duplex I2S (1 with ASRC), low-power audio ADC with PGA |
| Analog | 12-bit ADC, 11 inputs, up to 2.8 MS/s; temperature sensor; voltage comparator |
| Clocks | 48 MHz XTAL, 32.768 kHz XTAL, HFRC ×2, LFRC, PLL |
| Power | 1.71–2.2 V; SIMO buck; LDOs |
| Security | secureSPOT 3.0: secure boot, OTP keys, PUF, crypto, TRNG |
| Package | AP510BFA-CBR: 5.6 × 5.6 × 0.8 mm BGA, 13 × 13 balls, 153 pins, 96 GPIO, −20 to +70 °C |

Apollo510 (non-B) differs mainly by having no integrated radio, 2× PDM and
a 6.6 × 6.6 mm BGA / 4.9 × 4.7 mm CSP option (per the research summary of the
Apollo510 datasheet).

## CPU memory map (DS, Table 4)

| Range | Region |
|---|---|
| `0x00000000–0x0003FFFF` | ITCM 256 kB (secure alias `0x10000000`) |
| `0x00400000–0x0040FFFF` | NVM reserved for secure bootloader (64 kB) |
| `0x00410000–0x005FFFFF` | NVM0 application (1.94 MB) |
| `0x00600000–0x007FFFFF` | NVM1 application (2 MB) |
| `0x02000000–0x0201FFFF` | Boot-loader ROM (128 kB) |
| `0x20000000–0x2007FFFF` | DTCM 512 kB (secure alias `0x30000000`) |
| `0x20080000–0x2037FFFF` | System SRAM 3 MB |
| `0x40000000–0x4FFFFFFF` | Peripherals |
| `0x60000000–0x6FFFFFFF` | MSPI0 external memory (256 MB) |
| `0x80000000–0x83FFFFFF` | MSPI1 external memory (64 MB) — G2 maps the 32 MiB NOR here |
| `0xE0000000–0xE00FFFFF` | PPB (NVIC, SysTick, SCB, MPU, debug) |

## Peripheral memory map

From Apollo510B datasheet Table 5 (DS). Use these as Ghidra memory blocks
and labels.

| Base | Size | Peripheral | G2 firmware use |
|---|---|---|---|
| `0x40000000` | 1 kB | Reset / BoD | — |
| `0x40004000` | 0.5 kB | Clock generator | CLKGEN writes at `0x40004044/0x40004050` (FW) |
| `0x40004800` | 1 kB | RTC | Wall clock |
| `0x40008000` | 1 kB | Timers | Buzzer PWM |
| `0x40008800` | 0.5 kB | STIMER | — |
| `0x4000C000` | 1 kB | Voltage comparator | — |
| `0x40010000` | 2 kB | GPIO control (PADKEY at `+0x400`, key 0x73 per FW) | Pin configuration |
| `0x40014000` | 4 kB | MRAM / OTP control | Bootloader programming |
| `0x40020000` | 2 kB | MCUCTRL | — |
| `0x40021000` | 1 kB | Power control | SIMO/LDO sequencing |
| `0x40024000` | 1 kB | Watchdog | — |
| `0x40025000` | 4 kB | SSC | — |
| `0x40030000` | 1 kB | Security | — |
| `0x40035000` / `0x40036000` | 1 kB each | IOSFD0 / IOSFD1 SPI subordinate | — |
| `0x40038000` | 1 kB | GPADC | Board-ID ADC |
| `0x40039000`–`0x4003C000` | 1 kB each | UART0–UART3 | UART3 = GX8002 |
| `0x40050000`–`0x40055000`, `0x40057000` | 4 kB each | IOM0–IOM5, IOM7 (IOM6 slot at `0x40056000` listed as reserved) | I2C buses 4, 5, 7, … |
| `0x40060000` | 1 kB | MSPI0 | Display panel |
| `0x40061000` | 1 kB | MSPI1 | MX25U25643G |
| `0x40070000` / `0x40071000` | 1 kB each | SDIO0 / SDIO1 | — |
| `0x40090000` | 64 kB | Graphics (GPU) | NemaGFX |
| `0x400A0000` | 32 kB | Display controller | — |
| `0x400A8000` | 32 kB | Display PHY | — |
| `0x400B0000` / `0x400B4000` | 16 kB each | USB / USB PHY | Not used by G2 |
| `0x400C0000` | 32 kB | Crypto | — |
| `0x40201000` | 1 kB | PDM0 | Production mic path |
| `0x40208000` / `0x40209000` | 1 kB / 4 kB | I2S0 / I2S1 | GX8002 audio |
| `0x40210000` | 1 kB | AUDADC | — |
| `0x42000000` | 2 kB | NVM_INFO0 | Trims, provisioning |
| `0x42002000` | 6 kB | NVM_INFO1 | — |
| `0x42004000` / `0x42006000` | 256 B / 1.375 kB | OTP2_INFO0 / OTP2_INFO1 | — |

IRQ numbers used by G2 (from `g2/third_party/ambiqsuite-apollo510/CMSIS/AmbiqMicro/Include/apollo510.h`):
IOMSTR0–7 = 6–13, UART0–3 = 15–18, ADC = 19, MSPI0 = 20, MSPI1 = 21, GPU = 28,
DC = 29; PDM0 = 48 (FW vector cell `0x00438100`). The Apollo510B datasheet
vector table also lists IRQ 125–131 as GPIO8–14 MCUN1INTn.

## Pads used by G2 (FW + DS)

| GPIO | Ball | Function (DS) | Use (FW) |
|---|---|---|---|
| 49 | J1 | MNCE1_0 (func 2) | MX25U25643G CS |
| 95, 96, 97, 98 | H1, H2, G4, H3 | MSPI1_0..3 (func 0) | NOR D0–D3 |
| 103 | F3 | MSPI1_8 | NOR SCK |
| 104 | C3 | MSPI1_9 | DQS (configured, unused) |
| 93 | E5 | BLE_ENABLE (BLEC enable; needs ~10 MΩ pull-down) | Not recovered in FW |

## Register map / SVD

- Official CMSIS header `apollo510.h` is vendored at
  `g2/third_party/ambiqsuite-apollo510/CMSIS/AmbiqMicro/Include/apollo510.h`
  (AmbiqSuite 5.1.0 via Zephyr `hal_ambiq` 5efc0228).
- SVD: in the Keil Apollo_DFP pack (URL above). The datasheet refers to the
  AmbiqSuite SDK for the full register set.

## Relevance to decompilation

- Load the main image at `0x00438000` (vector table), bootloader at
  `0x00410000`; create RAM blocks for ITCM, DTCM and system SRAM and an
  MSPI1 XIP block at `0x80000000`.
- Import `apollo510.h` or the SVD to name peripheral registers; the table
  above gives the bases.
- The toolchain is IAR EWARM (DLIB); the RTOS is FreeRTOS 10.5.1 + CMSIS-RTOS2
  (`g2/docs/upstream-inventory.md:21-105`).
