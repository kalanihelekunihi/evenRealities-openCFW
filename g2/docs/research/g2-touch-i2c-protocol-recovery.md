# G2 touch-controller I2C protocol recovery

Status: complete, device-free static analysis over the authenticated
`firmware_touch.bin` payload (FWPK type 3), building on
`g2-touch-identity-recovery.md` (PSoC 4000T CY8C4046FNI, Cortex-M0+, 64 KiB
flash, 8 KiB SRAM). Analysis only; no device, flash, or hardware access.

This document is the device-side DFU/report protocol specification for the
touch controller. It supersedes one earlier reading: the nine words at
`0x7DC4` are tuning constants, not a switch table (the real dispatch is
described below).

## Executive summary

The shipped payload is the **normal-mode application/driver layer**: an SCB1
I2C-slave runtime with a 9-slot single-byte command protocol, a 16-byte
event-report channel with a GPIO attention line, deferred EEPROM config
persistence, and an enter-DFU handoff that resets into a **resident DFU
engine that is not part of the shipped prefix**. The payload provably
depends on factory-programmed flash above `0x8680` (switch tables, HAL
descriptors, dead log strings), so a touch OTA updates only the prefix
`[0, 0x867C)` of one base-0 linked image.

## Transport layer (confirmed)

| Element | Value | Evidence |
| --- | --- | --- |
| Peripheral | SCB1 `0x40250000`, I2C slave | pools at `0x334/0x3E4/0x5A8/0x990`; init span `[0x378,0x3DA)` |
| Interrupt | IRQ7 `scb_1_interrupt`; ISER/ICPR bit 7 via `0xE000E100`; handler `0x0400` entered indirectly (zero BL callers) | init stores `0x80` to `0xE000E100` and `0xE000E280` |
| HAL linkage | config table `0xB374`, callback registry `0xB0E8` (both resident); payload callback `0x3624` | init calls `0x65F4`/`0x6FA8` |
| Driver state struct | `0x200008EC`: RX descriptor `+0x28/+0x2C/+0x30/+0x34`, TX descriptor `+0x38/+0x3C/+0x40`, `+0x44` const `0x3701` | helpers `0x67D8`/`0x67F0`/`0x6806` |
| RX buffer | `0x200009A0`, 16 B: `[0]` = command (0–8), `[1..]` = arguments | init arms via `0x67F0`; dispatch reads `[0x200009A0]` |
| TX buffer | `0x200009B0`, 16 B; idle fill `0x5A` after each transaction | TX rearm body at `0x580` |
| Frame-length rule | received frame length must be in `[1, 16]` | dispatch sequence `subs r3,r0,#1; cmp r3,#0xF; bhi ret` at `0x42E` |
| Attention line | GPIO PRT4 pin 0, active-low: assert `DR_CLR (0x40040444)=1` on report ready; release `DR_SET (0x40040440)=1` after host read | report builder `0x932`; TX rearm `0x598` |

The RX dispatch (span `[0x400,0x5A0)`, byte-pinned) is:

```
rx_len = rx_desc.position              ; helper 0x6806
if (rx_len - 1) > 0xF: return          ; frame must be 1..16 bytes
cmd = rx_buf[0]                        ; 0x200009A0
if (cmd > 8): return
goto resident_table[0xB0C4][cmd]       ; 9 slots, mov-pc idiom
```

## Command map (bodies confirmed; slot indices inferred)

The 9-entry dispatch table lives at resident `0xB0C4` (not shipped), so
slot→body assignment is inferred from physical layout order and reply-ID
hints. Seven distinct bodies exist in the payload; slots 7–8 have no
distinct body (default/shared path). Reply framing: `[0]` reply ID,
`[1]` status (`0` ok / `0xFF` error), `[2]` `0x17` terminator — matching the
`0x17` frame terminator of the host-side DFU protocol.

| Slot (inferred) | Body | Role | Contract |
| --- | --- | --- | --- |
| 0 | `0x0446` | version/identity query | 16 B reply `{02,02,00,01, 01,00,02,02, …}` = version 2.2.0.1 + protocol word `0x01000202` (equals the FWPK header field@0x04) |
| 1 | `0x0466` | read saved proximity baseline | 16 B reply carrying u16 `config[0x200009D4]` |
| 2 | `0x0480` | read long-press threshold | 16 B reply (zeroed) carrying u16 `config[0x200009D6]` |
| 3 | `0x04A0` | save proximity baseline to EEPROM | sets flag `0x200009CF`; reply `{5,0,0x17}`; save is deferred to the next report cycle |
| 4 | `0x04C8` | write gesture configuration | u16 arg from `rx[1..2]` (memcpy `0x772C`); `arg==0` → error `{7,0xFF,0x17}`; stores `0x200009D6` + mirror `0x200004E8`, dirty flags `0x200009CE/0x200009CD`; reply `{7,0,0x17}`. Matches host `at_tp.c` 1–65535 ms validation |
| 5 | `0x052C` | enter DFU | reply `{2,0,0x17}`; then `0x4B30(0)`: mailbox `[0x20000000]=mode`, DSB, `AIRCR=0x05FA0004`, spin → reset into resident DFU mode |
| 6 | `0x054C` | read current sensor report | 10 B reply from two `sensor_read_mux (0x2F4)` channels (proximity + slider) |
| 7–8 | — | unresolved | no distinct body in the shipped prefix |

Cross-checks: host-side `at_tp.c` closure documents exactly these classes
(proximity-baseline read/save, gesture-config read/write, 1–65535 ms
validation, write/readback); the payload log strings name the same commands
("Received save ProxBsln command", "Gesture cfg cmd: long=%u"). The enter-DFU
function `0x4B30` has exactly one call site (the command case) and validates
`mode ≤ 1` (`bkpt #1` otherwise).

## Event reports, device → host (confirmed)

The report builder `0x0824` (two call sites from the main loop) assembles a
16-byte report at `0x20000990`, copies it to the TX buffer, asserts the
attention line, sets `report_pending 0x200009CC = 1` and timeout
`0x200009C8 = 0x280` (640):

| Bytes | Field |
| --- | --- |
| `[0]` | event type |
| `[1..3]` | event payload (logged as "event report: %d, %d, %d, %d") |
| `[4..5]` | u16 proximity baseline (current) |
| `[6..7]` | u16 channel value |
| `[8..9]` | u16 proximity value |
| `[10..11]` | u16 gesture result (helper `0x71C`) |

Proximity-baseline persistence policy (in the report cycle): when the
save-request flag `0x200009CF` is set, `|current − saved| > 49` triggers the
EEPROM write (`0x738`) and updates `config[0x200009D4]`; smaller changes are
skipped with a log; failures are logged. The EEPROM-emulation module
(`[0x660,0x780)`) guards config with the `UNVE` magic `0x45564E55` and
first-use default initialization.

## Power management (payload-resident, confirmed)

`0x7040` sets the CPUSS power-mode field (`[0x40100030]` bits `[1:0]`, values
0/1/2, plus bit 4) for requests `≤ 0x20`; `0x7074` enters sleep (clears
SLEEPDEEP in `0xE000ED10`, WFI); `0x7088` enters deep sleep (loads SFLASH
trim `[0x0FFFF152]` into `PWR_KEY_DELAY 0x40030004`, sets SLEEPDEEP, WFI).
The ACT/ALR/WOT state names exist only as dead log strings; the power state
machine itself is gated (below).

## The resident-region dependency (major architectural finding)

The payload is the prefix `[0, 0x8680)` of a single base-0 linked image whose
rodata continues to at least `0xBDF8`. The payload **requires** bytes it does
not ship:

- **Switch tables**: `0xB0C4` (RX command dispatch, 9 entries), `0xB4FC`
  (event dispatcher, 8 entries), `0xB51C` (SROM status decoder, 20 entries) —
  all reached via `mov pc, r3`; there are exactly three such sites.
- **HAL descriptors**: `0xB374`, `0xB0E8`, `0xB0F0`, `0xB38C`–`0xB404`,
  `0xB41C`–`0xB4C4` (≈15 tables).
- **Dead log strings**: `0xAA5C`–`0xB09C` (≈40 strings) — harmless because
  the logger `0x0BE0` is a compiled-out stub (`push {r0-r3}; movs r0,#0;
  add sp,#0x10; bx lr`); all 38 call sites are no-ops. Logging is disabled
  in this production build.

Consequences:

1. A touch OTA updates only `[0, 0x867C)`; the device keeps factory bytes at
   `≥ 0x8680`, which must match the shipped `.text` (single-link layout).
   The version gate in `service_touch_dfu.c` (`isTouchNeedUpgrade`) is the
   only host-side guard for this coupling.
2. The **DFU-mode engine** (commands `0x38/0x4C/0x37/0x49/0x31/0x3B` from
   `g2-service-touch-dfu-recovery.md`) has no handler in the shipped prefix:
   no command compares, no DFU strings, and the enter-DFU path hands off via
   mailbox + reset. The engine is therefore resident — it owns the real boot
   path and flash programming above or beside the updatable prefix.
3. Boot-path puzzle, stated honestly: the payload's first 192 bytes have
   exact ARMv6-M vector-table form (proving base-0 linkage) but their
   entries point into a sensor-processing loop and cannot cold-boot the
   device. The real boot vector table and startup are resident; how the DFU
   engine manages flash `[0, 0xC0)` during an update is an open gate.
4. The payload's own rodata strings (color-prefixed EasyLogger strings at
   `0x775C`–`0x7DC4`, incl. ACT/ALR/WOT and gesture logs) are referenced only
   as arguments to the stubbed logger — predominantly by code whose log
   statements point at resident string copies. One suffix-merged payload
   string (`0x79EB`) is referenced from payload code.

## Recovered module inventory (all byte-pinned in the analyzer)

| Span | Interval | Role |
| --- | --- | --- |
| i2c_slave_init | `[0x0378,0x03DA)` | SCB1 slave init, HAL tables, IRQ7 enable |
| i2c_irq_handler_and_cases | `[0x0400,0x05A0)` | IRQ demux, RX validation, dispatch, 7 command bodies, TX rearm |
| report_builder | `[0x0824,0x0960)` | 16 B report, baseline-save policy, attention assert |
| event_dispatcher | `[0x37C0,0x38CA)` | generic device events 0–7, FIFO/register service |
| dfu_handoff_and_reset | `[0x4B14,0x4B44)` | mailbox + `NVIC_SystemReset` |
| fifo_descriptors | `[0x67D8,0x680C)` | RX/TX descriptor arm, position getter |
| power_mgmt | `[0x703A,0x70A4)` | CPUSS mode set, sleep/deep-sleep WFI |
| logger_stub | `[0x0BE0,0x0BE8)` | compiled-out logger |
| eeprom_config_module | `[0x0660,0x0780)` | UNVE-magic config load/save |
| sensor_read_mux | `[0x02F4,0x0324)` | per-channel sensor reads |

## Reproduction

```sh
python3 openCFW/tools/analyze_g2_touch_i2c_protocol.py
python3 -m unittest openCFW.tests.test_analyze_g2_touch_i2c_protocol
```

The analyzer authenticates the blob, all ten protocol spans, 29 state/pool
words, seven resident references, the 13-halfword dispatch sequence, and the
BL call topology (logger stub ×38, enter-DFU ×1, IRQ handler indirect-only,
report builder ×2). Eleven fail-closed tests mutate every span class, pool
class, resident reference, and the dispatch site.

## Confidence and remaining gates

- **Transport, command bodies, report format, config contract, DFU handoff:
  confirmed at byte level.** Command slot **indices** are inferred
  (layout order); readback of the resident table `0xB0C4` would settle them.
- **DFU-mode engine (0x38-family commands): gated** — resident, not shipped
  in the payload. The host-side contract remains
  `g2-service-touch-dfu-recovery.md`; device-side handler recovery requires
  the resident image (not available as a blob).
- **Boot vector management during OTA: gated** (see boot-path puzzle above).
- **Gesture/calibration internals and the ACT/ALR/WOT state machine:
  gated** — strings and helper boundaries are pinned; the MSC sensing loop
  (`0x36C0`–`0x376C`, per-channel maxima/thresholds over a `0x3200`-offset
  SRAM scan buffer) is mapped but not behavior-closed.
- **Resident image provenance** (HAL library build, version coupling with
  the shipped prefix): open; no resident blob is retained in the repo.
