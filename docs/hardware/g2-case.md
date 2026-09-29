# Even G2 charging case ("B200"): hardware

> **Citations.** Repository paths cited as `path` or `path:line` refer to the tree at commit `832137ec`. The 2026-09-29 cleanup retires many of those evidence files; after they are removed, `git show 832137ec:<path>` still shows them.


Tags follow the [confidence vocabulary](README.md#confidence-vocabulary).
Primary firmware source: the case payload `firmware/box.bin` (EVENOTA type 6,
55,784 B, version 1.2.57) as analysed in
`g2/docs/research/g2-box-stm32g0-platform-recovery.md` (cited below as
"box platform doc").

## 1. Summary

| Item | Value | Evidence | Tag |
|---|---|---|---|
| Internal name | B200 (`B200 %s %08x%08x%08x` boot banner) | box platform doc | FW High |
| MCU | STM32G0Bx class (G0B0/G0B1/G0C1 not separable statically); leading candidate **STM32G0B1**; Cortex-M0+, 512 KiB dual-bank flash | box platform doc lines 28–52 | FW High (G0Bx) / Medium (G0B1) |
| RTOS | FreeRTOS V10.x, GCC `portable/GCC/ARM_CM0` port (V10.3.1–V10.5.1 likely) + CMSIS-RTOS | box platform doc | FW High |
| HAL | STM32CubeG0 HAL/LL (FLASH, UART, ADC, TIM, RTC, PWR); version not determinable | box platform doc | FW High |
| Power management IC | **YHMICROS YHM2510** ("2510 self check done, adjVal:%d") | box platform doc line 135 | FW High |
| Charger IC | "2217" (log prefix only; full part number unknown) | same | FW Medium |
| External watchdog | "4005" (log prefix only), fed by GPIO (`%s dog feed`) | same | FW Medium |
| Wake sources | Hall (lid), USB, RTC (`wake up from HALL/USB/RTC`) | same | FW High |
| Battery | 3.7 V, **2000 mAh, 7.4 Wh**; two alternate cell sources "112375" and "GSP112375" | G2 test report N25071003936E §4 (https://fccid.co/fcc/2BFKR-G2); official spec page | REG, Official |
| Supply | "DC 3.7V from battery or DC 5V from charge port" | G2 test report §4 | REG |
| Glasses charging | Contact (pogo) pins, 5 V to glasses | G2 test report §4 ("DC 5V from case"); https://support.evenrealities.com/hc/en-us/articles/13754885105295-How-to-Charge | REG, Official |
| Host connector | USB-C (charging); host sees a USB serial device (`/dev/cu.usbserial-*`) | Official charging page; `g2/docs/hardware-validation-2026-08-23.md:20` | Official, FW |
| Radio | None; no FCC ID of its own (`2BFKR-G2CASE` not found); appears only as support unit "AE-3 Case" in the G2 test report | https://fccid.co/fcc/2BFKR-G2 | REG |
| Status LED | Single LED, orange/white patterns; flashing orange = misaligned pins | Official charging page | Official |
| Recharges | About 7 full glasses charges | Official spec page | Official |

## 2. MCU peripheral use

| Peripheral | Use | Evidence | Tag |
|---|---|---|---|
| USART1 | Only USART with a populated IRQ vector (IRQ27); `HAL_UART_IRQHandler` at `0x08005F50` | box platform doc | FW High |
| USART2 / USART3 / USART4 | Base literals present (`0x40004800`, `0x40004C00`); IRQ slots default ⇒ polled | box platform doc | FW High |
| DMA | Not used (no DMA literals) | box platform doc | FW High |
| ADC1 | Battery voltage and temperature; ADC1_COMP ISR worker at `0x08004330` | box platform doc | FW High |
| TIM1/3/6/14/16/17 | Timers; TIM17 capture/compare worker at `0x08005C90` | box platform doc | FW High |
| RTC | Wake source | box platform doc | FW High |
| GPIOA–D | LEDs, Hall, glasses-present detect, bit-banged PMIC/charger/watchdog lines | box platform doc | FW High |
| FLASH | Dual-bank OTA: 128 × 2 KiB page erase per bank, doubleword program, `nSWAP_BANK` option-byte toggle; keys `0x45670123/0xCDEF89AB`, OB keys `0x08192A3B/0x4C5D6E7F` | box platform doc | FW High |
| Absent | I2C1/2, USB_DRD, FDCAN, RNG, AES, LPUART, UCPD, CRC unit, IWDG, WWDG, DBGMCU | box platform doc | FW High |

Consequences:

- The YHM2510, "2217" charger and "4005" watchdog are driven by **GPIO
  bit-banging** (log strings `read_bit_error…`), not hardware I2C [FW].
- The STM32 USB peripheral is unused, yet the host enumerates a USB serial
  port. An external USB-to-UART bridge is therefore likely [INF]; its part
  number is unknown (open question 13 in the [README](README.md)).

## 3. Memory map

| Range | Content | Evidence | Tag |
|---|---|---|---|
| `0x08000000–0x0803FFFF` | Bank 1 (active bank at boot), 128 × 2 KiB pages | `g2/docs/memory-map.md:1754-1776` | FW High |
| `0x08040000–0x0807FFFF` | Bank 2 / inactive-bank install alias | same; bank-2 literals at file `0x2d30`/`0x2ed8` | FW High |
| `0x0803F000–0x0803F00F` | Preserved serial/identity window (16 B), bank 1 | box platform doc | FW High |
| `0x0803F800–0x0803F807` | Preserved window (8 B), bank 1 | box platform doc | FW High |
| `0x0807F000–0x0807F00F` | Preserved window (16 B), bank 2 | box platform doc | FW High |
| `0x0807F800–0x0807F807` | Preserved window (8 B), bank 2 | `g2/docs/memory-map.md:1754-1776` | FW High |
| SRAM | Initial SP `0x20002C88` (not SRAM top); data to `0x2000FC1C` ⇒ ≥64 KiB used; STM32G0B1 has 144 KiB (DS) | box platform doc | FW / DS |
| Vector table | 46 words (IRQ0–IRQ29); reset trampoline `0x08000144` → `SystemInit` `0x080084AE` → `_start` `0x080000B8` | box platform doc | FW High |

Payload wrapper: `"EVEN"` + version (1.2.57) + big-endian length
(`0x0000D9C8` = 55,752) + big-endian additive word sum (`0x7367642F`) + 16
zero bytes [FW, box platform doc].

## 4. Glasses ↔ case UART protocol

Physical: UART over the pogo contacts [FW: "wired UART … mapped to the pogo
UART module/pins", `g2/docs/hardware-validation-2026-08-23.md:165`]. Baud
and logic levels are not recovered.

| Element | Detail | Evidence | Tag |
|---|---|---|---|
| Header | `5A A5 FF <cmd>` (case log string `header: 5a a5 ff %02x`, file `0x229c`) | box platform doc | FW High |
| Frame checksum | 8-bit additive checksum seeded with `length - 2` (glasses side); header search limited to the first four receive offsets | `g2/docs/research/g2-case-uart-update-source-closure.md:9-12` | FW High |
| Case-side checksum strings | `crc_cal: 0x%x, crc_rx:0x%x` used around chunk transfer; no CRC tables in the case image, computed bit-wise | box platform doc | FW High (strings); relation to the frame checksum: open question 14 |
| Packers | Two symmetric packers at `0x08008FA8` and `0x08009004` (left and right channels), up to 10 retries | box platform doc | FW High |
| RX parser | Header / length / data state machine, timeouts `receive header timeout`, `no header in first 5 char`, `receive len timeout`, `receive data timeout`; plain and `[noctrl]` variants | box platform doc | FW High |
| Glasses RX buffering | Five rotating 1,024-B slots; ASCII `T` passthrough for product test | `g2/docs/research/g2-box-uart-mgr-recovery.md:68` | FW High |
| `0x13` | Case → glasses status push on battery/hall/USB/charging change | box platform doc | FW High |
| `0x58` | OTA offer / check (versions `1.x.y`) | box platform doc; update closure doc | FW High |
| `0x5A` | Update chunk with nested chunk checksum; 32-bit additive sum of big-endian words | update closure doc | FW High |
| `0x3D` / `0x3E` | Aging-exit acknowledges | box platform doc | FW High |
| Status JSON | `{"vol":%d,"pct":%d,"open":%d,"usb":%d,"cur":%d,"GLS_L":%d,"GLS_R":%d,"temp":%d}` | box platform doc | FW High |
| Console | Case console command `DEB0` (USB serial) | `g2/docs/hardware-validation-2026-08-23.md:127-145` | FW High |
| Wired SBL bridge | The Ambiq Apollo5 wired-update HELLO `14559de900000800` can be bridged through the case to a temple; requires per-device INFOC/INFO0 provisioning | `g2/docs/hardware-validation-2026-08-23.md:127-170` | FW High |
| Phone mirror | BLE protobuf service `0x81` (glasses_case): battery, charging, lid, glasses-present, error | `g2/docs/research/g2-pb-service-glasses-case-recovery.md` | FW High |

## 5. Dual-bank update sequence

Ordered from 22 pinned log strings [FW, box platform doc]:

1. `ota check (0x58)` + version compare `cur:1.%d.%d, remote:1.%d.%d`.
2. `Check gls ready` / `GLS not ready` (both temples must be ready).
3. `Get running bank` → `Running bank: %d`.
4. Erase the inactive bank (retry on page-erase failure).
5. `Copy SN` — copy the preserved serial windows forward.
6. `get bin file` over UART with per-chunk checksum and error count.
7. Program doublewords (retry path).
8. `Inform GLS ota result: %d` → `Inform GLS done.`
9. `check box ota firmware`, then `Swap bank(2->1)` / `Swap bank(1->2) & RESET`
   via option-byte programming. On boot, `Option Bytes check fail, UPDATE &
   RESET` self-heals.

## 6. Tasks and timers

`ledTask`, `pwrManagerTask`, `glsDetectTask`, `defaultTask`; timers
`clearLedTimer`, `showErrorLedTimer`, `startLedTimer`, `agingTimer`,
`powerOnTimer`, `setAgingStatusTimer`; event group `appEvent` [FW, box
platform doc].

## 7. G1 case (for comparison only)

| Fact | Evidence | Tag |
|---|---|---|
| FCC ID 2BFKR-G1CASE, model "G1 Case", DXX, 13.56 MHz ASK, induction coil antenna SG-B346, 0 dBi | https://fccid.co/fcc/2BFKR-G1CASE (test report CTC20240956E01, operational description) | REG (G1) |
| Case input 5 V 1.5 A; charges glasses at 5 V 120 mA | same test report | REG (G1) |
| Field strength 48.06 dBµV/m @ 3 m (≈1.9×10⁻⁵ mW EIRP) | G1 case RF exposure exhibit | REG (G1) |
| Case MCU has a USB serial port and is updated with a desktop upgrade tool; MCU part not identified | https://support.evenrealities.com/hc/en-us/articles/14309515401743-Even-G1-Case-Upgrade | Official (G1) |

The G2 case does not use 13.56 MHz inductive charging; it charges by
contact pins [Official] and has no FCC grant [REG].
