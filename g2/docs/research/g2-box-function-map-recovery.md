# G2 charging-case (box) full function map and per-function attribution

Component: charging case / box (EVENOTA entry 4, `type 6`).
Image: `blobs/official/g2-2.2.6.10/firmware_box.bin`, 55,784 bytes, SHA-256
`36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`
(verified before use). Application payload: 55,752 bytes at `0x08000000`.

This increment converts the previous increment's 54,550-byte region-level
`unresolved` remainder into a per-function attribution and resolves the two
open questions from `g2-box-stm32g0-platform-recovery.md` (CRC polynomial,
log string-reference scheme).

## Lane and artifacts

The lorelei Ghidra lane (`g2/docs/research/lorelei-re-acceleration-benchmark.md`
pattern) ran Ghidra 12.1.2 headless on the 55,752-byte application:

1. import raw at `0x08000000`, processor `ARM:LE:32:Cortex` (the v7-M
   language decodes the ARMv6-M subset identically; the image contains
   zero `movw`/`movt`/IT instructions, proven in the platform audit);
2. `SeedCortexMVectorTable.java` seeds Thumb mode and the 46-word vector
   table (14 unique handler targets, 11 rejected slots);
3. full analysis, then the new
   `tools/ghidra_scripts/BoxExportFunctionMap.java` exports the function
   map, string census, string xrefs, and whole-image decompilation.

Returned artifacts, hash-verified against the lane's SHA256SUMS envelope
and committed under `tools/manifests/`:

| artifact | SHA-256 |
|---|---|
| `g2-box-ghidra-functions.tsv` | `90cae0c846ceca448022fe21d28c4bf1963cedfedb4d718f2574d56083657556` |
| `g2-box-ghidra-strings.tsv` | `517519e993eb27650aba3f46eee5131123b88e2ccaa0c461e139ca7ff989d565` |
| `g2-box-ghidra-string-xrefs.tsv` | `5ae785bae1a938a5de4fd5746fb3dcf16f3e3fdb96a217d5ed4aa6aacdfce1d6` |
| `g2-box-ghidra-decomp.c` | `531c1c8e75ff25deea66d8f0a5fd30d44654a68508b529396b77898c1c247f57` |
| `g2-box-ghidra-meta.tsv` | `3b0e3d3408d17f03ba2a557525eb3489d116562f4feda051649634c16b41255b` |

Result: **428 Ghidra-discovered functions / 40,664 bytes**, 308 strings
(exactly matching the independent platform-analyzer census), plus 7
supplemental RTOS entries the auto-analysis could not reach (no direct
callers). A device-free Thumb control-flow walk now bounds all seven entries:
4,572 reachable instruction bytes, including 2,820 instruction bytes not
covered by any Ghidra-discovered body.

- Analyzer: `tools/analyze_g2_box_function_map.py` (read-only, deterministic)
- Map: `tools/manifests/g2-box-function-map.tsv` (435 rows)
- Summary: `tools/manifests/g2-box-function-map-summary.json`
- Recovered task bodies: `tools/manifests/g2-box-task-entry-bodies.tsv`
- Task direct-callee map: `tools/manifests/g2-box-task-helper-map.tsv`
- Tests: `tests/test_analyze_g2_box_function_map.py` and
  `tests/test_analyze_g2_box_task_entries.py` (16 tests)

## Anchor reconciliation

All ten pinned islands from the platform audit appear in the Ghidra map
with exact expected sizes; the analyzer fails closed on any drift:
`xPortPendSVHandler` 62 B, SysTick gate 20 B, `xPortSysTickHandler` 32 B,
`xTaskGetSchedulerState` 26 B, `xTaskIncrementTick` 184 B (now fully
bounded), `HAL_UART_IRQHandler` 732 B, packers 84/54 B, both port
interrupt-mask helpers, plus the reset trampoline and
`vPortStartFirstTask`.

## Per-category attribution

Byte accounting reconciles to exactly 55,752 app bytes
(functions + inter-function gaps):

| category | functions | function bytes | combined bytes (incl. gaps) |
|---|---:|---:|---:|
| `upstream_cmsis_startup` | 15 | 310 | 502 |
| `upstream_freertos_kernel` | 86 | 5,814 | 5,814 |
| `upstream_stm32_hal` | 15 | 1,324 | 1,324 |
| `first_party_g2` | 97 (+7 entry rows) | 18,330 | 31,042 |
| `unresolved` | 222 | 14,886 | 17,070 |

FreeRTOS membership is proven two ways: direct references into the
kernel statics block `[0x20000128, 0x200001A0)` (46 functions), and a
banded call-graph closure (`[0x0800A800, 0x0800D100)`) from the pinned
port/scheduler anchors that never crosses a G2-string-referencing
function (79 members), plus seven structurally exact CMSIS-RTOS2 wrappers
called by the recovered entries (86 total). Structurally verified names:
`vTaskSwitchContext` `0x0800C390`, `vPortStartFirstTask` `0x080000CC`,
`uxListRemove` `0x0800BF2C` (exact list.c body), `xTaskCreate`
`0x0800C9A8` (six-argument form, stack words → bytes), `pvPortMalloc`
`0x0800B3E8`, `pxPortInitialiseStack` `0x0800B4C0` (exact
`portINITIAL_XPSR`/return-address frame), `prvTimerTask` `0x0800B0FC`
(timer-queue receive + command dispatch), and `osDelay`,
`osEventFlagsClear/Get/Set`, `osThreadTerminate`, and `osTimerStart/Stop`.

**RTOS wrapper verdict: CMSIS-RTOS2.** The creation APIs called by
`app_rtos_init` (`0x08006968`) use `isCurrentModePrivileged` and
`osThreadNew`/`osTimerNew`-shaped signatures — the cmsis_os2.c wrapper
over the FreeRTOS V10-line kernel, not raw-API calls. This tightens the
platform audit's "wrapper undetermined" to proven CMSIS-RTOS2
(CMSIS-FreeRTOS V10.2+ lineage; leading candidate V10.3.1–V10.5.1).

HAL membership stays deliberately conservative: the eight-function
`HAL_UART_IRQHandler` cluster (962 B) and the two FLASH credential
functions `HAL_FLASH_Unlock` `0x08004B6C` / `HAL_FLASH_OB_Unlock`
`0x08004BF4` (56 B), four structurally exact PWR/wakeup APIs, and one
HAL-style peripheral initializer whose exact public symbol remains unknown.
CubeMX-style board init and the G2 OTA updater
embed HAL register operations but are first-party policy code.

First-party includes 67 string-referencing functions, the log sink
`g2_log_printf` `0x08009170`, the GLS RX validator
`gls_frame_validate_dispatch` `0x08001E94`, the OTA image verifier
`ota_image_be32_sum_verify` `0x08002CC0`, the SN-window updater
functions `0x08002F60/0x08002F88/0x0800373C`, both frame packers, both
channel writers, `app_rtos_init`, four descriptor-table consumers, and
ten RTOS entry functions from the init literal pool (seven of them —
`0x08009D70`, `0x0800B7EC`, `0x0800BB90`, `0x08006E1C`, `0x08007F2C`,
`0x08007200`, `0x080082EC` — outside the discovered map; listed as
zero-byte supplemental rows to prevent overlapping byte counts). Their bodies
are now bounded and hashed in the task-body manifest.

The 222 unresolved functions are helper code without
kernel-statics/HAL/string/descriptor evidence (bit-bang chip drivers,
protocol helpers, math, board init). Naming them is future work; none
is claimed upstream.

## Seven previously undiscovered RTOS entry bodies

The recovery starts only from the authenticated pointer cells used by
`app_rtos_init` at `0x08006968`. It follows direct Thumb branches, records but
does not follow calls, rejects indirect control flow, and fails closed against
the concatenated instruction-byte digest for every entry. No hardware or live
device state is involved.

| entry | role | instructions | bytes | newly mapped bytes | code spans |
|---|---|---:|---:|---:|---|
| `0x08009D70` | timer callback | 28 | 66 | 66 | `0x08009D70-0x08009DB2` |
| `0x0800B7EC` | timer callback | 153 | 342 | 342 | `0x0800B7EC-0x0800B942` |
| `0x0800BB90` | timer callback | 170 | 374 | 374 | two spans through `0x0800BD08` |
| `0x08006E1C` | thread entry | 344 | 790 | 790 | `0x08006E1C-0x08007132` |
| `0x08007F2C` | thread entry | 269 | 616 | 616 | `0x08007F2C-0x08008194` |
| `0x08007200` | thread entry | 974 | 2,184 | 432 | four spans through `0x08007EE4` |
| `0x080082EC` | thread entry | 93 | 200 | 200 | `0x080082EC-0x080083B4` |

The split `0x08007200` thread crosses embedded literal/string pools, producing
four executable islands rather than one monolithic range. The `0x0800BB90`
callback has an unreachable two-byte branch island at `0x0800BC88`, excluded
from its reachable-body digest.

The recovered bodies call 59 distinct helpers. This increment resolves 39
formerly unresolved direct helpers: the seven CMSIS-RTOS2 wrappers above,
`NVIC_SystemReset`, five STM32G0 HAL functions, and 26 G2
GPIO/charge/protocol/sensor policy adapters. All 59 direct task helpers now
have an evidence-backed ownership category. The exact public symbol for the
HAL peripheral initializer at `0x0800598C` remains unresolved and is stated as
such in its evidence instead of being assigned a speculative API name.

## CRC verdict: no polynomial CRC exists in the case image

Both integrity checks are additive sums, verified in decompilation:

1. **GLS frame check** (`gls_frame_validate_dispatch` `0x08001E94`):
   scan first four RX bytes for header `5A A5 FF`; byte 3 is the length
   `len`; the check is an **8-bit additive sum seeded with `(len-2)`**
   over the `len` payload bytes, compared against the byte at
   `payload[len]`. Mismatch logs `GLS_RX error: CRC wrong.` /
   `CRC_Cal: %02x, CRC_Rx: %02x` and returns `0xff`. This is the exact
   mirror of the glasses-side `box_uart_mgr` "crc check failed …
   tmp_crc" path (`g2-box-uart-mgr-recovery.md`).
2. **OTA image check** (`ota_image_be32_sum_verify` `0x08002CC0`):
   **32-bit additive sum of big-endian u32 words** over the received
   image — the same algorithm as the EVEN wrapper checksum pinned in
   the platform audit — compared against the CRC field delivered with
   the image. This matches `docs/memory-map.md` ("verifies a 32-bit
   additive sum").

CRC-16/CCITT and CRC-32 lookup tables are provably absent (platform
analyzer) and no bit-wise polynomial loop exists in the decompilation.

## Log string-reference verdict: no ID/strip scheme

The previous increment hypothesized a compressed/indexed logging scheme
because most log strings had no literal-pool pointers. That hypothesis
is **refuted and corrected**: the log sink `g2_log_printf`
(`0x08009170`) takes a direct format-string pointer, and the address is
materialized by the **ARMv6-M `ADR` instruction (PC-relative, ±1 KiB)**
for nearby strings — invisible to a little-endian-word census — and by
LDR literals for distant ones. Ghidra resolves 153 of 308 strings as
referenced, each by exactly one call site (the rest are cold-path or
dead formats). Consequence for future recovery: every log call site is
recoverable by ADR-target computation, and the platform analyzer's
"unreferenced string" reasoning is superseded.

## Hardware gates (unchanged)

Battery/charging/thermal policy, bit-banged PMIC/charger/watchdog
register writes, and the `nSWAP_BANK` option-byte flow remain
code-evidence only. No hardware was touched.

## Remaining gates

1. Exact FreeRTOS point release (kernel-body matching against
   toolchain-identical V10.3.1/V10.5.1 reference builds; the decomp.c
   corpus is now in place for that comparison).
2. Exact STM32 HAL version (no static evidence).
3. Semantic task-name ↔ entry-function pairing (six create calls consume
   descriptor-table names; the descriptor entry-function fields are
   runtime-patched, so static pairing remains partial). Entry boundaries are
   now closed independently of those runtime names.
4. Naming/ownership of the remaining unresolved functions. None is a direct
   callee of a recovered task body.
5. `device_specific_preserve` windows remain external and untouched;
   no function rows exist at that category, by design.

## Verification

```
cd g2 && PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 \
  -m unittest -v tests.test_analyze_g2_box_function_map \
  tests.test_analyze_g2_box_task_entries
# 16 tests, OK

PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 \
  tools/analyze_g2_box_function_map.py --write-manifests
```
