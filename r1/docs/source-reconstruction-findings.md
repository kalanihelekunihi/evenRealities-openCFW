# R1 source-reconstruction findings (distilled)

Scope: what the R1 application 2.2.6.0009 source-candidate campaign established
before the receipt store and per-candidate harnesses were removed. The campaign
ran from 2026-08 to 2026-10. The application image is sha256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Identities, Arm Compiler evidence and the open byte-equality questions are in
[toolchain-and-dependencies.md](toolchain-and-dependencies.md). The full
per-checkpoint narrative stays in [upstream-reuse.md](upstream-reuse.md). This
file does not repeat either.

Citation shorthand:
- `SB:<path>[:line]` means `pre-consolidation:r1/research/source-build/<path>`.
- `T:<file>` means `pre-consolidation:r1/tools/<file>`.
- Line numbers refer to `SB:README.md` at that tag.

## 1. Bottom line

| Question | Answer | Evidence |
|---|---|---|
| Any function proven instruction-identical to stock? | **No.** The value of `exact_instruction_matches_proven` is 0. All 3,326 ledger rows have `instruction_identity_proven=false`. | `SB:function-frontier-summary.json`, `SB:function-frontier.csv` |
| Compiled-C instruction bytes equal to stock | 4 section-local spans of 4, 6, 6 and 10 bytes, all without relocations: `r1_format_unbounded_putc` 0x44a6c, `r1_native_floating_environment_control` 0x2839a, `r1_math_self_add32` 0x3bac8 and `r1_math_add32` 0x3bace. Image placement is unproven. | `SB:function-frontier-summary.json` (`compiled_instruction_byte_spans`) |
| Was the stock compiler (armcc) ever run? | **No.** All 616 compile commands across 499 reports are Clang. The other 48 commands are `arm-none-eabi-ld` partial links. GCC 9-2020-q2 was used only for the historical bootloader reference builds and as the provider of runtime headers and libs. | aggregate of `SB:*/report.json` `units[].command` |
| Image linked? | Application: no. Bootloader: a Clang `-Oz` candidate of 74 units links within the stock bounds, but byte identity is false. | `SB:report.json`, `SB:bootloader/report.json`, `SB:gates.json` (`components`) |
| How was correctness established? | Differential execution: stock Thumb from the authenticated image and the compiled ARM object both run under Unicorn 2.1.4 (`UC_MODE_THUMB\|MCLASS`). Checks cover r0–r3, callee-saved registers, SP, FPSCR, ordered non-stack RAM writes and MMIO traces. 607 verification receipts record about 22.9 M comparisons in total. | `SB:**/*verification*.json` (`comparisons`) |
| Final ledger state | 3,326 rows (3,022 application, 304 bootloader). 1,095 `tested_contract_candidate`, 1,298 `compiled_symbol_hint`, 933 `unresolved_source_route`. `SB:gates.json` holds older counts (700/1,372/1,254), so use the summary file. | `SB:function-frontier-summary.json` (`counts`) |

Verification classes used below:
- **D**: differential under emulation against stock, bounded inputs.
- **L**: linked graph of actual compiled providers with no interception.
- **B**: data, string or table bytes equal to stock. Code bytes are B only where stated.
- **A**: symbolic-asm transliteration. A `naked` function holds stock instructions as mnemonics, and reassembly equals stock bytes at native placement. This is **not C source** and not a compiler match. 96 of the 311 files under `r1/components/*.c` are `naked`, and about 50 of those are bulk transliterations. These are the largest: `native_health_notification_stages.c`, `native_event_callbacks.c`, `native_health_sample_storage.c`, `native_qma_configuration.c`, `native_bma_initialize.c`, `native_flashdb_*`, `native_sleep_*`, `native_lis_call_frames.c`, `native_temperature.c` and `native_calendar_frames.c`.

Two things hold for every family below:
- **Behaviour versus bytes.** A D, L or A result says behaviour or bytes matched for bounded inputs. It does not establish the original compiler, placement or byte-identical firmware, or physical behaviour. Every receipt carries `instruction_identity=false` and `whole_image_complete=false`.
- **The Ghidra tools are not independent.** REA and Ghidra-MCP share one Ghidra backend, so the README treats their readbacks as authentication, not as independent semantic proof (README:663, 716).

## 2. Compiler/flag profiles tested

| Profile | Units | Used for | Outcome |
|---|---|---|---|
| Clang (Apple 21 / LLVM) with `--target=arm-none-eabi -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -ffreestanding -fno-builtin -fshort-enums -ffunction-sections -fdata-sections -std=c11 -Os` | 543 | Default for all candidates | Behaviour matches stock where verified. Instruction identity is never achieved. |
| Same, with `-O2 -Wall -Wextra -Werror` | 16 | `r1/reconstructed/*` and `r1/source/*` providers | Compiles. 27 runtime symbols (`__aeabi_d*`, `expf`, `floorf`, `tanhf`, …) stay unresolved. (`SB:report.json`) |
| Same, with `-O0 -fno-inline` | 27 | FreeRTOS slices: tick, timer, wait, notify, termination, idle. Also `native_task_construction`, `cm_backtrace.c`, the SEGGER RTT init, the log prefix and the log modules. | Needed to keep stock-observable store order and frame behaviour. For CmBacktrace, the 4 range-field stores (README:6253). |
| `-O0` for a single SDK unit | 2 | `fal_partition.c` and `nrfx_clock` | Optimised Clang rejects FAL state byte 2. `-O0` restores stock behaviour (README:1398-1413, 1773-1782). |
| Adds `-fwrapv` | 6 | FreeRTOS tick, wait, mutex, notify | Tick overflow semantics (README:2889-2906) |
| Adds `-fno-inline-functions` | 8 | `ble_advertising.c`, `ble_advdata.c`, `nrf_ble_gatt.c` | Keeps the separately callable SDK bodies |
| Adds `-falign-loops=1` | 8 | STACMD and YHM state units | Delay-loop shape (README:4398) |
| Adds `-fno-strict-bool` | 1 experiment | `nrf_ble_qwr.c` | **Failed.** Stock tests a bool byte for nonzero, while Clang tests bit 0. This remains an open compiler-domain gate (README:904-911). |
| Clang `-Oz -g` plus GNU ld, nano libc | 74 | Bootloader candidate | Links within the original flash region. `-Os` overflowed it. Not byte-identical (README:32-60). |
| `-std=gnu11` with newlib 3.3.0 stdio | 25 | `newlib-stdio/` experiment | **Rejected.** Differs from stock printf in 86 of 225 cases: pointer spelling, hex-float, subnormals (README:5017-5035). |
| LLVM compiler-rt 20.1.8 builtins, unchanged (`87f0227c…`) | several | `__aeabi_uldivmod`/`ldivmod`/`llsl`/`llsr`, `floatdisf`, daily-metadata division | Accepted where D passes: 50,822 comparisons for integer division (README:508-530). LLVM soft-double add is **rejected**: 183 of 2,624 cases differ in NaN and subnormal handling (README:5082-5094). |
| musl 1.2.5 subset, unchanged | several | `memcpy`, `memset`, `strcmp`, `strncmp`, `memmove` | Accepted behind R1 EABI wrappers: 1,985 stock comparisons. The stock mem-move helper at 0x2775c returns a non-ISO pointer, so it is wrapped (README:2364-2371). |
| GCC 9.3.1 (`9-2020-q2`) | bootloader only | Historical reference and overlay builds | Not byte-identical. See toolchain-and-dependencies.md §3. |
| armcc / armlink (AC5) | 0 | — | Never available. This is the root blocker for any byte match. |

## 3. Per-family findings

### 3.1 Compiler runtime, libc and libm (`arm_toolchain_runtime`: 114 tested, 10 unresolved)

**Source.** All of the following are R1-owned C written to stock VFP operation order:
- the stock printf engine, rebuilt natively (parser 0x43080, 1,656 B; decimal 0x3f530; unsigned 0x28334; output helpers 0x43734/0x43758/0x43bbc; `snprintf` 0x38080; `vsnprintf` 0x380dc);
- scanf (core 0x283c4, 810 B);
- `rand`, `qsort`, `strtok`, ctype;
- scatter-load decompression;
- application entry.

**Verification (D).** Dense numeric grids over all binary32 exponents, both signs, all four FPSCR rounding modes, FZ and DN:

| Function | Address | Comparisons | README |
|---|---|---:|---|
| `cosf` | 0x38a5c | 470,752 | 5572 |
| `sinf` | 0x3ae04 | 470,752 | 5602 |
| `tanf` | 0x3b048 | 474,016 | 5639 |
| `atanf` | 0x38774 | 467,488 | 5473 |
| `atan2f` | 0x384c8 | 942,112 | 5498 |
| `expf`/`tanhf` | — | 672,832 | 5411 |
| `logf`/`log10f` | 0x39864/0x396e4 | 694,592 | 5443 |
| `powf` | 0x3a620 | 427,168 | 5850 |
| `pow` | 0x399d0 | 90,708 | 5972 |
| `atan`/`tanh`/`expm1`/`exp`/`log` | 0x381f0/0x3b1c8/0x3b5c0/0x38bb0/0x39320 | about 37k each | 5673-5816 |
| `ceil`/`floor`/`round`/`roundf`, float bits | — | 0.3–0.5 M each | 5177-5393 |
| scatter-load (6,492 RAM bytes expanded, 213,172 zeroed) | — | 127,394 | 6127-6148 |
| application entry | — | 27,648 | 6171 |

**Stock quirks to keep:**
- errno lives at 0x20007dbc.
- In FZ mode, logf compares subnormals as zero.
- The `tanf` jump table is a conditional `POP {PC}`.
- scanf's float and long-long conversions are no-ops that return a preset failure (README:6103-6116).
- `isspace` uses a low-bit table lookup that marks 64 non-ASCII bytes as whitespace (README:6081-6086).
- `qsort` is stable lower-index-first.
- `snprintf` with zero capacity differs in r1 in 24 cases.

**Origin.** No upstream origin is inferred from table or algorithm resemblance (README:6024). That the family is the Arm C library comes from `TOOLCHAIN-RUNTIME-CORRELATION.md`, not from these receipts.

**Test harness defect.** Unicorn 2.1.4 corrupts Thumb IT-block progression when a memory-write hook observes a conditional store. Run with write hooks disabled (README:6069; `T:verify_unicorn_it_memory_hook.py`).

**Open.** Arm C library variant (microlib or standard), original placement, private frames.

### 3.2 FreeRTOS 10.5.1, Nordic port and CMSIS-RTOS2 (`freertos_10_5_1_nordic_nrf52_port`: 94 tested; CMSIS: 24 tested)

**Source.** The pinned kernel `def7d2df…`, CMSIS-FreeRTOS `d213f261…` and the SDK `port_cmsis_systick.c` are used unchanged. They are compiled either whole (`SB:rtos/report.json`, 12/12 units) or as **tracked kernel slices**: `SB:rtos-*/*.c` and `SB:native-task-construction/{ready,stack}.c`. Those slices are upstream text plus `*_contract.h` headers, and `tools/build/source-plan.json` and `source-qualification.json` reference them.

**Stock configuration recovered:**

| Setting | Value | Evidence |
|---|---|---|
| `configMAX_PRIORITIES` | 56 (`uxTopUsedPriority`=55 at 0x2000784c) | README:3006-3010 |
| Max-syscall priority | Raw value 2, masked by 0xe0 to give `ucMaxSysCallPriority` 0 and group 4. BASEPRI is 64 elsewhere. Do not "fix" this to 64. | README:3288-3319 |
| Tickless | mode 1, threshold 2; RTC1 at 0x40011000; maximum sleep 0x00fffffd | README:3203-3246 |
| Timers | task priority 53; queue of 32×16-byte messages at 0x2002b258; timer object 44 B with status at +40 | README:3266-3286, 3416 |
| Heap | **Not upstream heap_4.** 16-byte header (next, size\|alloc, caller LR, pad); request rounded to `req+24-(req&7)`; split only if more than 32 B remain; 51,200 B at 0x2001e588; faults set BASEPRI 64 and write zero | README:2799-2823 |
| TCB | **112 B, not upstream's 92.** Name 32 B at +52; stack depth in words at +84; base priority +96; mutex count +100; notification value/state +104/+108; allocation mode +109; stack fill 0xa5; priority ≥56 faults | README:3040-3047 |
| `osThreadNew` defaults | priority 24, 256 words | README:3099-3109 |
| Kernel objects | queue/semaphore 80 B with type at +76; event group 32 B | README:2694-2745, 3661 |

**Verification.**
- D: tick 40,193; suspend/resume 32,274; semaphores 38,400; `osThreadNew` 42,048; event groups 51,826; message queues about 32k.
- L graphs: scheduler start, timer, notification and sync.
- Static task memory (`SB:rtos/static-memory-verification.json`): 20 comparisons.

**Ledger label corrections:**
- 0x97ba4 is `xQueueGenericReset`.
- 0x96188 is the ordered `vTaskPlaceOnEventList`.
- 0x8569c is the timer-ID getter.

**Open.** Full kernel `FreeRTOSConfig.h` equivalence. The GCC `port.c` is used where an armcc build would use RVDS. Scheduler execution, final placement.

### 3.3 Nordic nRF5 SDK 17.1.0, application side (210 tested, 356 hints, 217 unresolved)

**Source.** `make application-sdk` compiles 64/64 unchanged SDK units, emitting 679 symbols (README:109-130). It adds two Clang-only inline-asm operand patches; one of them, `nrf_svci_clang.h`, is generated and gitignored. Configuration is tracked in `r1/source-config/sdk/`.

**Recovered stock configuration and quirks (each D-verified):**
- **GPIOTE**: 8 low-power slots, not the historical 2, giving a 128 B control block. IRQ priority 6, not 2 (README:283-299).
- **nrfx_clock**: LF source RC=0, not 1. Calibration byte restored. IRQ0 at 0x30ac8 with its vector at 0x27040 (README:1773-1826).
- **Critical regions**: application IRQ mask `0xbdff06fc`/all bits, with `nrf_nvic_state` at 0x2002c2fc. 52,464 comparisons (README:538-566).
- **Logging**:
  - `NRF_LOG_DEFERRED=0`; UART backend off; RTT retry 3 with a 1 ms delay; panic ring 4,096 B at 0x2002d60c.
  - fprintf inserts CR before LF; hexdump packs only 10 length bits.
  - The SEGGER RTT init is R1-typed (512/64 B buffers, reversed ID) because the generic SDK initializer differs (README:1885-2236).
- **WDT log policy**: tracked in `source-config/sdk-wdt/nrfx_log.h`. 87 descriptor bytes are B (README:568-600). The `nrf_strerror` table (37 rows) is D over 139,272 cases.
- **Storage drivers**:
  - fstorage: parameter checks off.
  - `fstorage_sd`: 5×28 B queue slots, 4 KiB chunks, 8 retries.
  - atfifo: 33,548 comparisons (README:1540-1627).
- **SDH**: legacy multi-range section ABI, 4 priorities, 500 B BLE event buffer, 12 observer records (README:857-872).
- **SAADC**: 3 typed ADC records; 124 B are B. The stock "fatal ADC error" is a returning conditional logger, bound as `r1_adc_error` 0x4e5bc (README:299-330).
- **Power and DFU**: GPREGRET2 is set to skip-CRC, then SYSOFF (README:1843-1852).

**Open.**
- About half the SDK rows are unresolved.
- `sdk_config.h` values outside the recovered set.
- The second fstorage instance in 0x20007dc0..0x20007de8.
- The second advertising-instance configuration.
- `nrf_drv_twi` `m_cb` layout.

### 3.4 BLE stack users

| Item | Source | Verified | Stock specifics |
|---|---|---|---|
| Serialized sender, 0x3e7a8..0x3e937 | R1 C | D 71,797 | Flag 0 sends even if the semaphore is not acquired. Otherwise status 19 triggers one retry with timeout 1000. 7 benign statuses (README:649-666). |
| BAE8 HVX send, 0x526cc | R1 C plus an SVC174 asm primitive | D 14,342; 806 string bytes B | Two notify-enable bytes; handles at +6 and +22; 244 B length cap (README:692-715) |
| Link context, `blcm_link_ctx_get` 0x514e0 | SDK, unchanged | D 37,154 | Stock does a byte load where the SDK does a halfword load. The not-found sentinel is 20 (README:735-751). |
| `ble_conn_state` and atflags | SDK, unchanged | L 157,596 | Flags at 0x2002bdb4; reset span 124 B (README:773-791) |
| GATT | SDK `nrf_ble_gatt.c` init plus an **R1 observer** | D 5,376 / 16,923 | MTU 247; data length **251** (the historical 27 was wrong); context 36 B at 0x20007e1c. The R1 observer always sends SVC144 on CONNECTED, sends no MTU exchange and applies no peer DLE cap (README:918-963). |
| QWR | SDK, unchanged | D 10,340 | 3×12 B contexts at 0x20007e40 (README:886-895) |
| Advertising | SDK `ble_advertising.c`/`ble_advdata.c` plus R1 configuration | D 48,585 / 70,050; 88 B B | Flags 6; manufacturer ID 0x5245; fast interval 160 / 6000 timeout unless config byte 0x70==0x55; slow 1600 / 0 (README:985-1082) |
| DFU observer 0x52154 and auth 0x7cdc8 | **R1 C (diverges from `ble_dfu.c`)** | D 34,560 | Disconnect compares against the glasses handle; auth and HVC store the connection early. Open: HVX byte 23 (README:8457-8585). |
| Output worker 0x44f50; veneers 0x4e650/0x4e65e | R1 C | D 5,346 | Channel 1 timeout 200; channel 0 timeout 100 (README:604-634) |

### 3.5 Board drivers: TWI, GPIO, ADC, registry, initcalls

**Software TWI** (`unknown_software_twi_provider_candidate`: 40 tested). Source is `r1/reconstructed/software_twi` plus `components/software-twi`:
- D: 20 primitives over 4,144 cases; 8 transactions over 1,575; adapters over 570.
- 448 B of initial configuration are B.
- Fixes it drove: an extra SDA release in the NACK tail was removed, and reversed SCL/SDA were corrected.
- Quirks: i2c_4 keeps a 16-bit length of 257; the delay callback is `us*64-3`.

**Hardware TWI.** R1 adapters sit on the unchanged `nrfx_twim.c` and `nrf_drv_twi.c`:
- D: 30,720 + 46,080 + 7,200.
- An 80-byte write overruns the low byte of saved r4; this is preserved.
- Configuration tails at 0x9a600/0x9a620 are B (README:8200-8454).

**Shared i2c_5.** D 782, which caught a reversed P1.10 OUTSET/OUTCLR (README:181-197).

**Named GPIO.** 7 IRQ descriptors (308 B B). The output GPIO registrar at 0x54e78 drives pins 10/30/36/9/17 (340 B B); it is not PWM. The dispatcher at 0x54d20 keeps negative command indices with no guard (README:2636-2658, 8008-8153).

**Initcalls.** 13-entry table at 0xc4534. Every entry runs even after a nonzero status, and the wrapper re-enables IRQs instead of restoring the mask (README:2569-2595).

**Delay.** The `nrfx_coredep_delay_us` clones are C with 3 ARM mnemonics; 21 native clone spans are B (README:2169-2187). The STACMD delay is 209×4 NOPs.

**Peripherals:**
- **PMIC (YHM2710).** Raw status must keep the incoming r3: D 55,296. System track D 80,184 (README:4755-4791).
- **STACMD bus.** Read makes 9 attempts and returns 31; write returns 11/27/30. Failure counter at 0x200075c0.
- **Battery.** Discharge and initial curves are D over all 65,536 halfwords. Calibration tables 0x99d16..0x9a0d5 are B.
  - The cap at 4310 mV means the 4340 mV override is unreachable. This is kept.

### 3.6 Sensors

| Device | Pin / lineage | Source | Verified | Stock quirks / open |
|---|---|---|---|---|
| Bosch BMA456 | SensorAPI 2.29.0 `3266db2c` (BSD-3) | Upstream `bma4.c`/`bma456w.c` compile 6/6 with the sensor set. Native frames are **A** (`native_bma_*`) plus small extracted Bosch kernels. | D: FIFO 76,397; setup 262,144 validator cases; init 13,248 | `bus_read`/`bus_write`/`delay_us` at offsets 0x24/0x28/0x2C. The remap block at 0x9a768 ends in unexplained bytes `802e`. Open: register 40 alias (00 vs 11), register 49 partial read (80 vs 00) (README:9366-9659). |
| ST LIS2DW12 | pid 2.1.0 `8d4bd522` | Upstream `lis2dw12_reg.c` plus **A** call frames | D: 17 register bodies 55,767; configuration 51,840 | Ledger corrections: 0x750b8 is BDU bit 3; 0x7581a is tap-X bit 7. Native-only routines 0x7575a and 0x7518a (README:9109-9364). |
| QST QMA6100 | V1.0 lineage, no licensed source | **A** reduction (`native_qma_*`); no QST C compiled | D 17,074 + 5,806 | Open: register 19 FB vs F3 (README:9661-9773) |
| Motion selector 0x50208 | R1 | C | D 27,650; 72 B tables B | Probe order is LIS 0x44, then BMA 0x16, then QMA 0x90. FIFO normalizers are exhaustive over signed16 (README:8966-9107). |
| GXT310 temperature | no source | C plus **A** | D 69,964 | Calibration record at 0x200076f0. Stock ignores write results in the self-check (README:6336-6345, 9775-9872). |
| ST25DVxxKC NFC | fp-sns-stbox1 `e9a35449` | Upstream plus the R1 binding | D 90 | Uses public Write/Read field order and the raw RTC1 counter (README:156-179) |
| Goodix GH3x2x | democode v1.6 / `pebbleos-nonfree@2c0034a2` | 16/16 public units, 354 symbols. No private algorithm archives are used. | B: all 136 configuration bytes | **Stock delta:** HR (36 B) and HRV (24 B) equal upstream. SpO2 calibration words a2/a1/a0 are stock −156022/−42041/1066184 against public −124026/−59505/1043941. The patch is in `r1/patches/goodix/`. HBA/HRV/SpO2/NADT libraries are binary-only (`SB:goodix/configuration-verification.json`; README:135-150). |
| GoMore | unidentified | `r1/reconstructed/gomore_*` compiles | 360 hints, 2 tested | No version, licence or behavioural receipt. The quantized NN runtime has 26 unresolved entries. |

The sensor stream framework (`unknown_sensor_stream_framework_candidate`: 20 tested) has two notable behaviours:
- Drift correction fires at span ≥500, not the old >500.
- Allocation failure sets BASEPRI 64 and stores to 0xffffffff (README:8802-8964).

### 3.7 Storage: FlashDB 2.0.0, FAL 0.5.99, KV

**FAL** (`4e567740…`, Apache-2.0). `fal.c`, `fal_flash.c` and `fal_partition.c` are used unchanged:
- `fal_init` 0x62f40: D 10,512. `fal_init_check` 0x62fe8: D 256.
- 7 partition records at 0x9c250 are B (448 B).
- Quirks: the stock assert line is 144 where Clang gives 145; `fal_partition.c` needs `-O0` (README:1275-1449).

**FlashDB.** The product-level iterator 0x63ad8, log read 0x87e14, sector read 0x87c24, partition read 0x631e8, device lookup 0x64f74 and control 0x63694 are **A**. Together 2,068 B are byte-identical at native placement. Quirk: the query-count adapter returns 0 where upstream returns `FDB_INIT_FAILED` (README:10129-10328).

**KV store** (R1 C):
- **Layout.** The class has size at +20 and payload at +24, and returns 5 on a size mismatch. The port table has 9 entries at 0x20006984.
- **Entry points.** get 0x95168, put 0x95304 (erase granularity 4,096), init 0x94e3c (partition `kv.bin`, minimum 2,048, stride 2,048).
- **Verification.** D 140k–793k (README:1109-1330).

**Internal flash** (R1 C): 80 B descriptor at 0x20006f98; 36 pages; length truncated to 16 bits; the wait loop calls `osDelay(5)`. D 203,735 (README:1465-1535).

**Health and sleep storage.**
- Mostly **A**: sample storage, average 0x5aba0, sleep 0x5b6f4/0x5b890/0x8fe28/0x8fe98/0x901e4, report 0x8dd90.
- Chained runs: 3,694 + 1,536 B match placement. The record chain matches 408 of 412 B; the other 4 B are a memcmp relocation.
- Quirk: average row 5 aliases the stress prefix.

### 3.8 Crash / CmBacktrace / retained state

**CmBacktrace** (`73714489…`, MIT). The unmodified `cm_backtrace.c` provides init only, built at `-O0 -fno-inline` to keep 4 range stores. D 10,240. Ghidra-MCP authenticates 84 code bytes and a 98 B string. The raw void-return r0 differs, which is an ABI gate (README:6250-6265).

**R1 crash path** (C):
- Initializer 0x5a2b8.
- Snapshot 0x5a324 plus 0x3f47c. Restored r2/r3 differ in every case, which is open.
- Payload getter 0x6abe4. The CRC covers 964 B and the copy gate is 896 B, but the getter writes 736 B. This mismatch is kept (README:8630-8800).
- The 15 `r1_cmbacktrace_provider_adapter` rows remain unresolved.

**Reset decoder** (754 B, mask 0x0007000f): D 114,240. Retained getters use the stock CRC16 record at 0x2003ffb0 (README:6536-6593).

### 3.9 Product protocol, health and events (`r1_product_specific`: 308 tested, 451 unresolved)

**Protocol.**
- The encoder 0x82f9c uses a recovered Modbus CRC16.
- The fragmenter 0x32408 uses a non-reflected Castagnoli CRC32. It computes the CRC before the 4,096 limit check, and an exact multiple of 239 emits an extra empty fragment.
- Ingress 0x8316c does no CRC or length check.
- Module lookup underflows on keys below the minimum, reading the previous record (README:4935-4990).
- ACK table: 32×20 B records, unlocked before the callback; the callback re-arms with delay 0x7800 (README:6853-6869).

**Delayed-event scheduler** 0x65b4c/0x659e8/0x65d64/0x65f84: the empty table arms a timer with UINT32_MAX. This is flagged "must not be silently corrected" (README:3742-3761).

**Health.**
- Notification throttle 0x8b138 uses 10,800 s.
- Sync controllers are **A**, byte-identical over 6,313 B.
- 37 event callbacks (1,766 B) are **A**, D 53,280 (README:9874-10104).

**Settings and touch** (C): `SD_POWER_DCDC_MODE_SET`=63; gesture events 1/2/0/4/5/8 (README:7611-8005).

**Open counterexamples:**
- A failed NV read lets compiler-private frame residue into the record. The health-settings failed read is a similar case (README:7254-7306, 7934).
- Serial reporting differs in private-stack bytes 72-123 on the second call.

### 3.10 Crypto

tiny-AES-c `e72b6eff…`, built as an AES-128 inverse core with an R1 two-pass adapter (`r1/components/crypto`):
- D: 116 transforms and 28 XOR comparisons, covering partial blocks up to 4,096 B (`SB:crypto/verification.json`).
- Candidate code size differs from stock.
- Open: CC310/Oberon bootloader libraries are binary-only (32 unresolved and 9 hint rows for `arm_cryptocell_cc310`). The nanopb rows are 3 unresolved and 27 hints.

### 3.11 Checksums

`r1/source/stock_checksums.c` and `r1_crc.c` cover three entries: 0x5d87c, 0x5d8a4 and 0x5d8cc.
- D: 1,056 comparisons.
- Both polynomial-generated tables are B: 0x995a8 (512 B) and 0x997a8 (1,024 B).
- `T:generate_stock_checksum_tables.py` regenerates them (`SB:checksum-verification.json`).

## 4. Open blockers (consolidated)

1. **No armcc or armlink.** Every byte-identity question is still open:
   - the exact AC5 release and C-library variant;
   - the scatter file and link order;
   - bool and narrow-load codegen, for example the QWR bool test and the `blcm` byte-versus-halfword load.
2. **About 50 product, sensor and storage bodies exist only as A transliterations.** They need real C before any compile-and-match attempt.
3. **933 rows are unresolved.** Largest groups: product (451), SDK (217), Goodix democode (48), CC310 (32), the quantized runtime (26), IQS7211E (18) and ST25 adapters (17).
4. **Binary-only inputs.** Goodix algorithm libraries, GoMore, CC310/Oberon, S140/MBR, and the Bravechip B210 platform layer, whose source is absent.
5. **Configuration gaps.** The full `FreeRTOSConfig.h`, `sdk_config.h` defaults outside the recovered set, the second fstorage and advertising instances, and the UICR snapshot (776 B).
6. **Counterexamples kept on record.** Private-frame and residue mismatches in NV, health settings, crash snapshot r2/r3, BMA registers 40 and 49, QMA register 19, the DFU HVX byte, and event dispatch r2/r3.

## 5. Removed evidence and how to recover it

The tag `pre-consolidation` keeps everything below:
- **`r1/research/source-build/`**: 4,450 tracked files. Per candidate it holds `report.json` (compile commands and hashes), `*verification*.json` receipts, REA/Ghidra dossiers, `thumb-*.txt` and `pseudocode-*.c.txt` dumps, and `pre-*`/`initial-*` snapshot subdirectories. At top level: `README.md` (the 10,890-line checkpoint log), `gates.json` and `function-frontier.{csv,json}`.
- **`r1/tools/`**: 476 `build_*`, 507 `verify_*`, 172 `audit_*`, 34 `recover_*` and the `check_*`/`probe_*`/`inspect_*` harnesses. Most import `undefined_symbols` from `build_source_candidates.py`, and `functions`/`section_bytes` from `audit_source_frontier.py`.

Recovery commands:

```sh
git show pre-consolidation:r1/research/source-build/README.md | sed -n 9366,9659p
git show pre-consolidation:r1/research/source-build/native-cosf/verification.json
git ls-tree -r --name-only pre-consolidation r1/research/source-build/native-bma-fifo
git ls-tree --name-only pre-consolidation r1/tools/ | grep '^r1/tools/verify_native_'
git restore --source=pre-consolidation -- r1/tools/verify_native_cosf.py   # rerun one harness
```

Rerunning a harness requires:
- the official image at `r1/blobs/official/r1-2.2.6.0009/application.bin`, with sha256 `0e788d43…`;
- `vendor-cache/r1/` with the SDK 17.1.0 zip and GCC 9-2020-q2 headers;
- `third-party/upstream/*` pins;
- Unicorn 2.1.4, and Clang with ARM target support.
