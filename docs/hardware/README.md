# Even Realities hardware reference

> **Citations.** Repository paths cited as `path` or `path:line` refer to the tree at commit `832137ec`. The 2026-09-29 cleanup retires many of those evidence files; after they are removed, `git show 832137ec:<path>` still shows them.


This directory records what is known about the hardware of the Even Realities
G2 glasses, the G2 charging case and the R1 ring, and where each fact comes
from. It is a reference for decompilation and reconstruction work: part
identities, buses, addresses, pins, memory windows and radio parameters.

Scope and date: compiled 2026-09-29 against the locked G2 artifact
`s200_v2.2.6.10` (EVENOTA, 4,301,227 B, SHA-256 `f4dfb0b4…1b9afa`, hardware
revision 5) and the R1 retail application `2.2.6.0009`. G1 (2024) facts appear
only where they inform G2 and are always labelled **G1**.

## Index

| Page | Contents |
|---|---|
| [g2-glasses.md](g2-glasses.md) | G2 system overview, block diagram, per-IC table, buses and pads, inter-processor links, display, audio, power, memory, RF, batteries |
| [g2-case.md](g2-case.md) | G2 charging case ("B200"): MCU, power ICs, UART framing, dual-bank update, preserved serial windows |
| [r1-ring.md](r1-ring.md) | R1 ring: nRF52840 pin and bus map, sensors, PMIC single-wire protocol, NFC charging, BLE, flash map summary |
| [regulatory.md](regulatory.md) | FCC IDs, grants, exhibits and URLs, extracted RF data, antennas, ISED/Japan numbers, withheld and missing records |
| [sources.md](sources.md) | Bibliography of every external URL used |
| [components/](components/) | One page per identified IC (datasheets, key specs, register-map/SVD availability, decompilation relevance) |

### Component pages

| Device | Parts |
|---|---|
| G2 glasses (per temple) | [Apollo510B](components/apollo510b.md), [EM9305 / BLEC](components/em9305.md), [GX8002](components/gx8002.md), [MX25U25643G](components/mx25u25643g.md), [JBD4010](components/jbd4010.md), [Hongshi A6N-G](components/hongshi-a6n-g.md), [PSoC 4000T CY8C4046FNI](components/cy8c4046fni.md), [ICM-45608](components/icm-45608.md), [OPT3007](components/opt3007.md), [nPM1300](components/npm1300.md), [BQ25180](components/bq25180.md), [BQ27427](components/bq27427.md) |
| G2 case | [STM32G0B1](components/stm32g0b1.md), [YHM2510](components/yhm2510.md) |
| R1 ring | [nRF52840](components/nrf52840.md), [BMA456(W)](components/bma456.md), [LIS2DW12](components/lis2dw12.md), [QMA6100](components/qma6100.md), [IQS7211E](components/iqs7211e.md), [ST25DVxxKC](components/st25dvxxkc.md), [Goodix GH3x2x](components/gh3x2x.md), [GXT310](components/gxt310.md), [YHM2710](components/yhm2710.md) |

## Confidence vocabulary

Every fact carries one evidence class. Where it helps, a strength is added
(High / Medium / Low).

| Tag | Name | Meaning |
|---|---|---|
| **FW** | Proven by firmware evidence | Recovered from the stock firmware (strings, literals, register sequences, vector tables, recovered driver paths) and documented in this repository with a file citation. |
| **REG** | Regulatory filing | Stated in an FCC exhibit (test report, RF exposure, antenna specification, label, confidentiality letter). |
| **DS** | Datasheet | Stated in a vendor datasheet, reference manual or official product page. Used for part properties, not for the claim that Even uses the part. |
| **PR** | Press | Reported by a press, trade or teardown article. |
| **COM** | Community | Stated by an independent community project (custom firmware, BLE protocol work). Sources that only restate this repository are not counted. |
| **INF** | Inferred | Derived by reasoning from the above; the reasoning is stated next to the fact. |
| **UNV** | Unverified | A candidate with no supporting evidence found. Listed so it is not repeated as fact. |

Rules:

- A part is "identified" only with FW, REG, or two independent COM/PR sources.
  Everything else stays INF or UNV.
- Datasheet properties (DS) describe the part, not the board. A board-level
  statement (for example "MSPI1 runs at 96 MHz") needs FW or a measurement.
- Repository paths are relative to the repository root. Addresses inside the
  Apollo main image are run addresses (`run = file_offset + 0x00437FE0`).
- Versioned firmware mirrors are in the checkout
  (`g2/blobs/official/g2-2.2.6.10/PROVENANCE.md`); FW facts here cite the
  analysis documents and analyzers that were run against the locked bytes.

## How to add a fact

1. Put it on the page for its device, or on the component page if it is a
   property of the part.
2. Give it exactly one tag from the table above and a citation: a repository
   path (with line numbers if stable), an FCC exhibit URL, or a vendor URL
   that you opened. Do not cite a URL you have not read.
3. If it contradicts an existing row, keep both rows, mark the conflict, and
   add an entry to the open-questions list below. Do not silently overwrite.
4. Add any new external URL to [sources.md](sources.md).
5. Keep G1 facts under a **G1** heading; never merge them into G2 tables.
6. Measurements on hardware go in with the tag FW only when a firmware
   artifact confirms them; otherwise record them as "Measured" in the note
   column with date, unit serial suffix withheld, and method.

## Open questions / measure on hardware

These are the gaps that block complete pin-level or part-level documentation.
Items marked (M) need a physical measurement or debugger read; items marked
(D) can probably be closed by further static analysis of the locked artifact.

| # | Question | Device | Why it matters | Current best evidence |
|---|---|---|---|---|
| 1 | Is the "EM9305" controller the in-package BLE controller (BLEC) of the Apollo510B, or a separate chip? (D/M) | G2 | Determines whether a separate IC and bus exist on the board | Apollo510B datasheet BLEC = 48 MHz MCU, 64 kB ROM, 512 kB flash, 64 kB RAM, SPI HCI; EM9305 has the same memory figures; firmware ships an ARC EM image named `ble_em9305.bin`. INF: BLEC is an EM9305-class core. See [em9305](components/em9305.md). |
| 2 | Which IOM (or dedicated port) carries the SPI HCI to the BLE controller? (D) | G2 | Needed to label the HCI transport in the disassembly | Datasheet: IOM6 is not pinned out on Apollo510B; firmware initialises eight IOM slots. INF (Low): IOM6 is the internal BLEC link. |
| 3 | MSPI0 pads, panel reset/enable GPIOs, TE line (D/M) | G2 | Display bring-up | Undecoded 586-B board config at `[0x005093D0,0x0050968C)` (`g2/docs/research/g2-s200-board-config-recovery.md`). Datasheet lists DISP_QSPI / DISP_SPI_RST functions on GPIO100–104 alternates. |
| 4 | IOM numbers and SDA/SCL pads for "I2C bus 4/5/7", and bus speed (D/M) | G2 | Sensor and charger drivers | Bus 4 = IMU (IOM4 IRQ used), bus 5 = touch, bus 7 = BQ25180/BQ27427. Pads not recovered. |
| 5 | Bus and address of OPT3007 and nPM1300 (D) | G2 | ALS / PMIC | OPT3007 has a fixed 7-bit address 0x45 (DS); community reports 0x45 on 2.3.0.24. nPM1300 bus not recovered. |
| 6 | Which I2S instance receives GX8002 audio; UART3 pads (D/M) | G2 | Audio path | Clock helper touches I2S0 and I2S1. |
| 7 | Physical medium of the temple-to-temple TinyFrame link (M) | G2 | Master/slave sync | Official blog: a 0.1 mm "dual-sided communication FPC" runs through the frame. INF: wired UART over that FPC. |
| 8 | Magnetometer part (D/M) | G2 | Compass | Aux I2C 0x1E behind the IMU, chip-ID reg 0x01 = 0x45, which equals `ICT1531X_WHOAMI` in the vendored TDK driver; stock use of that driver not proven (INF Medium). |
| 9 | Codec (GX8002) external SPI NOR size (M) | G2 | Codec image layout | Image B ends at `0x46440` (≈281 KiB); public GX8002 SiP flash is 256 or 512 KiB. |
| 10 | Which charger family (nPM1300 vs BQ25180+BQ27427) retail revision-5 boards use (M) | G2 | Power driver path | Both families are in the image, selected by board record 3 / board-ID ADC. |
| 11 | Case charger "2217" and watchdog "4005" full part numbers (M) | Case | Case power | Only log-string prefixes. |
| 12 | Case glasses-link UART baud, voltage levels, which USART per temple (D/M) | Case | Wired update and status | USART1 IRQ-driven, USART2/3/4 polled. |
| 13 | Case USB path: external USB-UART bridge part (M) | Case | Console/update | Host sees `/dev/cu.usbserial-*`; STM32 USB peripheral literals absent. |
| 14 | Frame checksum: glasses side is an 8-bit additive sum seeded with `len-2`; case strings mention `crc_cal`/`crc_rx` (D) | Case | Protocol correctness | Both documented; see [g2-case.md](g2-case.md). |
| 15 | Which accelerometer is fitted in retail R1 (LIS2DW12, BMA456W, or QMA6100) (M) | R1 | Motion driver | Stock probes all three at 0x18. |
| 16 | R1 i2c_5 SDA/SCL orientation: P1.11/P1.14 are reported in both orders (D) | R1 | NFC / PMIC bus | Two repo docs disagree; see [r1-ring.md](r1-ring.md). |
| 17 | R1 NFC charging receiver: is ST25DVxxKC energy harvesting the only charge path, or is there a separate wireless-charging receiver? (M) | R1 | Power tree | NFC-rectifier ADC on P0.04, ST25DV EH reset in init, YHM2710 charger. |
| 18 | R1 BLE (DTS) FCC test report | R1 | RF data | Only the NFC report is mirrored; the RF-exposure exhibit covers BLE. |
| 19 | G2/R1 short-term-confidential FCC exhibits (internal photos, manual) may now be public | G2, R1 | IC markings | 180 days after 2025-11-23 is about 2026-05-22; primary FCC site was not reachable. |
| 20 | G2 battery cell vendor/model | G2 | Power | Only "3.87 V, 96 mAh, 0.372 Wh" per arm in filings. |
| 21 | INFOC `0x400C2000` (0x400 B) and INFO0 wired-update provisioning per temple (M, debugger read) | G2 | Wired SBL recovery over pogo | `g2/docs/hardware-validation-2026-08-23.md:151-170`. |
