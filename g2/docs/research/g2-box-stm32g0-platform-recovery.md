# G2 charging-case (box) STM32G0 platform attribution

Component: charging case / box (EVENOTA entry 4, `type 6`).
Image: `blobs/official/g2-2.2.6.10/firmware_box.bin` — 55,784 bytes,
SHA-256 `36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`
(verified against `blobs/official/g2-2.2.6.10/PROVENANCE.md` before use).

- Analyzer: `tools/analyze_g2_box_stm32g0_platform.py` (read-only, deterministic)
- Attribution map: `tools/manifests/g2-box-stm32g0-platform-attribution.tsv`
- Machine summary: `tools/manifests/g2-box-stm32g0-platform-summary.json`
- Fail-closed test: `tests/test_analyze_g2_box_stm32g0_platform.py` (12 tests)

This increment is identification and behavioral reconstruction only. No
source ownership is claimed for the case image; it remains cut-forward.
No hardware action was performed; battery/charging/thermal and
option-byte behaviors are hardware-gated throughout.

## Transport wrapper

The 32-byte EVEN wrapper at file `0x000000` carries magic `EVEN`, case
version **1.2.57**, a big-endian length `0x0000D9C8` (55,752), and a
big-endian additive checksum `0x7367642F` equal to the sum of the
application payload read as big-endian u32 words (recomputed and
verified). The remaining 16 bytes are zero. The application maps to
logical `0x08000000` with the inactive-bank alias `0x08040000`
(manifest `address_status: confirmed_from_vector_and_ota_code`).

## MCU family: STM32G0Bx-class, leading candidate STM32G0B1

Confidence: **high** for G0Bx-class; **medium** for the exact member.

Candidates considered and discriminating evidence:

| Candidate | Verdict | Discriminator |
|---|---|---|
| STM32G030 (8 KB SRAM, 28 IRQs) | **excluded** | USART3/USART4 base literals present (`0x40004800` at file `0x6320`/`0x8d9c`, `0x40004C00` at `0x8da0`); RAM-resident pointers reach `0x2000FC1C`; dual-bank flow below |
| STM32G070/G071 (single-bank ≤128 KB) | **excluded** | IRQ-slot evidence: on the G070 map IRQ12=TIM1_BRK_UP_TRG_COM, IRQ22=I2C1, IRQ27=USART2; the populated handlers instead match ADC1_COMP (ISR/IER flag worker at `0x08004330`, registers `+0x00/+0x04`), TIM17 (TIM SR/DIER capture-compare worker at `0x08005C90`, registers `+0x10/+0x0C`), USART1 (`HAL_UART_IRQHandler` at `0x08005F50`) — the G0Bx map; plus the dual-bank update flow |
| **STM32G0B0/G0B1** | **consistent, leading** | 46-word vector table = 30 populated peripheral IRQs on the `stm32g0b1xx.h` map (official ST CMSIS device header, fetched from the STMicroelectronics `cmsis_device_g0` repository); 512-KB dual-bank flash with `nSWAP_BANK`; Cortex-M0+ (ARMv6-M: zero `movw`/`movt` sites in a full decode sweep; MRS/MSR PSP usage) |
| STM32G0C1 | **not statically separable** | same IRQ map and flash; FDCAN2 unused (no `0x40006800` literal) |
| G0B0 vs G0B1 | **not statically separable** | AES/RNG unused (no `0x40026000`/`0x40025000` literals); DBGMCU IDCODE (`0x40015800`) never read by the image |

Load-bearing dual-bank evidence: bank-2 base `0x08040000` literals at
file `0x2d30`/`0x2ed8`; option-byte programming with FLASH `OPTKEYR`
credentials; strings `Swap bank(2->1) & RESET, cur ob val:%x`,
`Swap bank(1->2) & RESET`, `ob program: %d`, `Option Bytes check fail,
UPDATE & RESET. 0x%x`. This matches `docs/memory-map.md` (two logical
256-KiB banks, 128 × 2-KiB pages, `nSWAP_BANK` toggle).

Memory-model evidence: initial SP `0x20002C88` (deliberately not the
SRAM top; the linker reserves RAM regions), RAM function pointers at
`0x2000A901`/`0x2000F859` and data to `0x2000FC1C` imply ≥ 64 KB used;
STM32G0B1 nominal SRAM is 144 KB. Exact RAM budget is unresolved.

Vector-table facts: 46 words, SP `0x20002C88`, reset trampoline
`0x08000144` → `SystemInit` (`0x080084AE`) then `_start` (`0x080000B8`)
— GNU/newlib-style startup, consistent with the GCC FreeRTOS port
below. NMI/HardFault and most unused slots are individual `b .` loops;
PVD (IRQ1) and TIM2 (IRQ15) slots are zero; CEC (IRQ30) is not
populated (table ends at IRQ29).

## RTOS: FreeRTOS kernel V10 line, GCC ARM_CM0 port

Confidence: **certain** for family and port; **interval** for the point
release.

Exact instruction-sequence evidence:

- `xPortPendSVHandler` at `0x08000102` (62 bytes, SHA-256
  `6093899cb710c7c4528991e47a9fd21cc8e4099f36f51ecaebadcc5f6998309c`)
  matches the upstream `portable/GCC/ARM_CM0/port.c` naked handler
  instruction for instruction, verified against tag **V10.5.1**
  (sequence stable across the V10 line; the vendored
  `g2/third_party/freertos-kernel` V10.5.1 snapshot does not ship the
  CM0 GCC port, so the reference file was fetched from the upstream
  FreeRTOS-Kernel repository). The trailing literal is
  `pxCurrentTCB = 0x20000128`.
- `vPortSVCHandler` is the documented empty stub: the SVC vector
  (`0x08006E18`) is a bare `bx lr`. The GCC port keeps SVC unused; the
  IAR port does not — this independently confirms the GCC port.
- `ulSetInterruptMaskFromISR` (`0x080000F4`) and
  `vClearInterruptMaskFromISR` (`0x080000FC`) match the port's inline
  helpers.
- `xPortSysTickHandler` at `0x0800C5AC`: mask → `xTaskIncrementTick` →
  `PENDSVSET (1<<28)` into `SCB->ICSR` (literal `0xE000ED00`) → unmask.
- The SysTick vector (`0x08008420`) reads `SysTick->CTRL` via SCS
  literal `0xE000E000`, calls `xTaskGetSchedulerState`, and skips the
  kernel tick only when the scheduler has not started — the STM32Cube
  `cmsis_os` v1 `osSystickHandler` guard shape; raw-API use is not
  excluded (wrapper undetermined).
- `xTaskGetSchedulerState` (`0x0800CA4C`) and the `xTaskIncrementTick`
  head (`0x0800CA78`) prove the kernel statics at `0x20000128`:
  `xTickCount @+0x0C`, `xSchedulerRunning @+0x14`, `xPendedTicks
  @+0x18`, `uxSchedulerSuspended @+0x30`, `pxOverflowDelayedTaskList
  @+0x34`, including the suspended-tick pended path and the wrap path.
- Kernel name strings: `IDLE` (`0x0800C2E8`), `Tmr Svc`
  (`0x0800CD74`), `TmrQ` queue-registry name (`0x0800ACDC`).

Version interval with discriminators: **V10.x (V10.0.0–V10.6.x)**. The
port bytes are unchanged across the V10 line; V9.x is not excluded by
port bytes alone; V11.x single-core is not excluded. Leading candidate
**V10.3.1–V10.5.1** per STM32CubeG0 distribution lineage. Narrowing
requires kernel-body function matching against toolchain-identical
reference builds (task-notification form, TCB layout), which is future
work.

Application task/timer set (static descriptor table at file
`0xd2c0`–`0xd3a0`, names at `0xd8b8`–`0xd958`): `ledTask`,
`pwrManagerTask`, `glsDetectTask`, `defaultTask`, timers
`clearLedTimer`, `showErrorLedTimer`, `startLedTimer`, `agingTimer`,
`powerOnTimer`, `setAgingStatusTimer`, and event group `appEvent`.

## STM32 HAL/LL attribution

Lineage: STM32CubeG0 HAL/LL. **No static version evidence exists** (HAL
carries no version strings); module presence is proven by peripheral
constants and handler structure.

- FLASH driver: unique `FLASH_KEYR` credentials `0x45670123`/`0xCDEF89AB`
  (file `0x4c34`/`0x4c38`) and `OPTKEYR` credentials
  `0x08192A3B`/`0x4C5D6E7F` (file `0x4bac`/`0x4bb0`) —
  `HAL_FLASH_Unlock`/`HAL_FLASH_OB_Unlock` lineage. Used by the OTA
  updater (erase 128 × 2-KiB pages, program doublewords, additive-sum
  verify, option-byte swap).
- UART: `HAL_UART_IRQHandler` head at `0x08005F50` (USART `ISR +0x1c`,
  `CR1 +0x0`, `CR3 +0x8`, `ICR +0x20` sequence). USART1 is the only
  USART with a populated interrupt vector (IRQ27); USART2/3/4 base
  literals exist but their IRQ slots are default handlers — polled.
  No DMA peripheral literals: all UART traffic is polled/IRQ, no DMA.
- Modules present by literal census: RCC, FLASH, PWR, RTC, ADC1
  (battery voltage/temperature), TIM1/3/6/14/16/17, USART1–4,
  GPIOA/B/C/D, SYSCFG/EXTI, SCS/SysTick.
- Modules absent (no base literals): I2C1/I2C2, DMA1/DMA2, USB_DRD,
  FDCAN1/2, RNG, AES, LPUART1/2, UCPD1/2, CRC peripheral, IWDG, WWDG,
  DBGMCU, UID, FLASHSIZE.
- The YHM2510 PMIC, `2217` charger, and `4005` watchdog chips are
  **GPIO bit-banged** (GPIOB/C/D literals plus `read_bit_error…` log
  strings), not hardware I2C. External watchdog feed: `%s dog feed`.
- Reset/self-check flow: `B200 %s %08x%08x%08x` banner, per-chip
  self-checks (`2217 self check done`, `2510 self check done,
  adjVal:%d`, `4005 self check done`, `pmic self check done`), wake
  sources (`wake up from HALL/USB/RTC`, `Power up...`).

G2-owned policy (first-party) is separated from HAL by the attribution
map: HAL islands (flash credentials, UART IRQ handler) are
`upstream_stm32_hal`; the charging/battery/aging/LED/OTA policy code,
log strings, packers, and task descriptors are `first_party_g2`.

## UART / update protocol reconstruction

Glasses↔case link (structural + string evidence):

- Frame header `5A A5 FF <cmd>` (log string `header: 5a a5 ff %02x`,
  file `0x229c`), payload, CRC tail (`crc_cal`/`crc_rx` log pair).
  CRC-16/CCITT and CRC-32 lookup tables are **absent** from the image
  (verified); the CRC is computed bit-wise in software — exact
  polynomial/width unresolved.
- Two symmetric **frame packers** at `0x08008FA8` and `0x08009004`
  (left/right glasses channels): critical-section channel write with
  immediate `0x5A`, retried up to **10** times; on exhaustion the
  caller buffer is filled with `0xFF` and zero returned; success bumps
  a frame counter and runs a conditional notify callback.
- RX parsers exist in two variants (plain and `[noctrl]` prefixes) with
  staged timeouts: `receive header timeout`, `no header in first 5
  char`, `receive len timeout`, `receive data timeout` — a
  header/length/data state machine per direction, on two logical ports
  (control vs non-control).
- Command codes from string evidence: `0x13` case→glasses status push
  (sent on battery/hall/USB/charging changes — `send 0x13 soon`),
  `0x58` OTA check, `0x3D`/`0x3E` aging-exit acknowledges. The status
  telemetry is also rendered as JSON (`{"vol":%d,"pct":%d,"open":%d,
  "usb":%d,"cur":%d,"GLS_L":%d,"GLS_R":%d,"temp":%d}`).

OTA-box update state machine (ordered by log-string evidence; 22
pinned step strings):

1. `ota check (0x58)` + version compare (`cur:1.%d.%d, remote:1.%d.%d`)
   — case OTA versions are `1.x.y` (current image: 1.2.57);
2. `Check gls ready` / `GLS not ready` (both temples must be ready);
3. `Get running bank` → `Running bank: %d`;
4. erase inactive bank (`fail to erase %d pages … retry:%d`);
5. **`Copy SN`** (`Copy SN done/fail`) — preserved-window copy-forward;
6. `get bin file` over UART with per-chunk CRC
   (`crc_cal: 0x%x, crc_rx:0x%x`, `total error cnt: %d`);
7. program (`Fail to program.` retry path);
8. `Inform GLS ota result: %d` → `Inform GLS done.`;
9. `check box ota firmware`, then `Swap bank(2->1)` / `Swap bank(1->2)
   & RESET` via option-byte programming (`ob program: %d`); on boot,
   `Option Bytes check fail, UPDATE & RESET` self-heals.

Host-side cross-reference: the glasses-side `box_uart_mgr.c` recovery
(`docs/research/g2-box-uart-mgr-recovery.md`) shows the mirror image of
this protocol — `[box_uart_mgr]crc check failed … tmp_crc`, `box uart
unpack err`, `box uart pack err`, `uart tx flush failed` — matching the
case-side CRC/pack/unpack layer. The glasses-side
`service_box_detect.c` state accessors (`0x004AC726`/`0x004AC73C`/
`0x004AC752`/`0x004ACAD0`) feed the case-state bytes, and
`pb_service_glasses_case.c` defines the BLE-side mirror of the case
status (battery, charging, lid, glasses-present, error at payload
offsets 4–8) — consistent with the case's `0x13` status push.

## Device-specific serial/identity preservation

The updater's preserved windows are referenced by literal from the OTA
code and confirmed against `docs/memory-map.md`:

| Window | Size | Bank | Literal sites (file) |
|---|---:|---:|---|
| `0x0803F000..0x0803F00F` | 16 | 1 | `0x2fe4`, `0x3834` |
| `0x0803F800..0x0803F807` | 8 | 1 | `0x2fa4`, `0x3728` |
| `0x0807F000..0x0807F00F` | 16 | 2 | `0x2c28` |
| `0x0807F800..0x0807F807` | 8 | 2 | `0x2c24` |

These live in bank-end flash far beyond the 55,752-byte application
image (`image_contains_preserved_windows: false`). The per-device SN is
set over the USB/factory UART (`Set SN:`, `Set SN Even done/fail`,
`SN Even length wrong.`) and copied forward across every OTA (`Copy
SN`). The STM32 UID (`0x1FFF7590`) and FLASHSIZE (`0x1FFF75E0`)
registers are never referenced — identity is SN-based, not UID-based.

**Preservation rule: never overwrite these windows; any reconstructed
case image must reproduce the copy-forward behavior.** The attribution
map carries them as `device_specific_preserve` rows with zero image
bytes.

## Region classification (seven ownership categories)

Categories: `generated_transport`, `upstream_cmsis_startup`,
`upstream_freertos_kernel`, `upstream_stm32_hal`, `first_party_g2`,
`device_specific_preserve`, `unresolved`.

14 evidence-anchored islands are classified (exact ranges and SHA-256
in the TSV): wrapper 32 B `generated_transport`; vectors + reset
trampoline 204 B `upstream_cmsis_startup`; CM0 port + SysTick gate +
`xPortSysTickHandler` + `xTaskGetSchedulerState` + `xTaskIncrementTick`
238 B `upstream_freertos_kernel`; FLASH credential island +
`HAL_UART_IRQHandler` head 208 B `upstream_stm32_hal`; packers +
descriptor table + name strings + SN literal island 552 B
`first_party_g2`; 54,550 B remain `unresolved` (bulk kernel body, HAL
drivers, policy, rodata, log corpus — needs a full function map);
4 zero-byte `device_specific_preserve` logical windows.

These are lower-bound, region-level attributions, not function closure.

## Hardware gates (not exercised, not claimed)

- Battery/charging/thermal policy values (98 % cutoff, over-temperature
  stop, fake-standby timers, water-detect thresholds) are log-evidenced
  only.
- PMIC/charger/watchdog register writes are bit-banged and
  hardware-gated.
- The `nSWAP_BANK` option-byte flow is proven from code and strings
  only; no device execution.

## Remaining questions

1. Exact FreeRTOS point release within V10.x (needs kernel-body
   matching against toolchain-identical reference builds).
2. Exact STM32 HAL version (no static version evidence exists).
3. G0B0 vs G0B1 vs G0C1 member split (unused differentiators).
4. GLS UART CRC polynomial/width (bit-wise; no table).
5. Compressed-log scheme: most log strings (including the whole
   `[OTA_BOX]`/`[AGING_*]` corpus) have **no** pointer literals — only
   the `0x0800Dxxx` page (34 pointers) is directly referenced. This is
   consistent with an indexed log-strip scheme in the `compress_log`
   family; the ID encoding is unknown, which currently blocks anchoring
   the parser/state-machine function bodies through their log strings.
6. Full function-level closure of kernel/HAL/policy bodies.

## Highest-value next action

Run the case image through the lorelei Ghidra lane to produce a full
function map, then anchor the GLS RX parser and OTA updater bodies
through the pinned island addresses (`0x08008FA8`/`0x08009004` packers,
`0x08005F50` UART IRQ handler, `0x0800CA78` tick path) and the SN/pack
literal sites. That converts the 54,550-byte `unresolved` remainder
into a per-function attribution and unlocks the CRC and log-ID
questions above.

## Verification

```
cd g2 && PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 \
  -m unittest -v tests.test_analyze_g2_box_stm32g0_platform
# 12 tests, OK

PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 \
  tools/analyze_g2_box_stm32g0_platform.py --write-manifests
```
