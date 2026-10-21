# G2 touch (PSoC 4000T) and case (STM32G0) findings from analysis experiments

Distilled on 2026-10-21 from the removed experiment directories `g2/analysis/touch-*`, `case-*`,
`component-goal-20261013` and `dependency-*`. Process narrative, per-run case counts, intermediate
hashes and status ledgers were dropped. Originals: `git show pre-consolidation:g2/analysis/<dir>/<file>`.
Citation `[dir]` = `pre-consolidation:g2/analysis/<dir>/REPORT.md`; `[dir/file]` names another file.

Conventions. All evidence was offline (Unicorn/QEMU emulation of the locked bytes against independently
compiled C, plus compiler/linker comparisons). Synthetic MMIO/SROM/FIFO never proves physical timing,
analog response or IRQ delivery; "count", "budget" and "ticks" below are software counts, not ms unless stated.
This file supersedes conflicting statements in `protocols.md` §7/§9, `toolchains.md` §5/§6 and
`libraries.md` §5/§6 where noted.

---

## 1. Touch controller (PSoC 4000T, CY8C4046FNI-T412)

### 1.1 Image identity and coordinates

| Fact | Value | Source |
|---|---|---|
| Locked `firmware_touch` SHA-256 (with 32-B FWPK wrapper) | `0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d`, 34,464 B | [touch-crt-array-binding-2026-10-09] |
| Decoded image (wrapper stripped) SHA-256 | `371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87` | [touch-mmio-cycle-2026-10-05/next-fifo/README.md] |
| Address mapping | runtime VA = decoded offset + `0x3300`; payload offset = VA − `0x3300` + `0x20`. All touch addresses below are VAs | [touch-scb14-holdouts-2026-10-09] |
| OTA runtime extent | `0x3300..0xB980` | [touch-init-closure-2026-10-08] |
| Vectors | SP `0x20002000`, reset `0x4675`; IRQ8 (MSCLP, prio 3) and IRQ7 (SCB1 I2C) used | [touch-reset-layout-candidate-20261010], [touch-scan-isr-closure-2026-10-08] |
| Peripheral bases | SCB0 `0x40240000`, SCB1 `0x40250000` (host I2C), MSCLP `0x40290000`, CPUSS SYSREQ/SYSARG `0x40100004/0x40100008`, SRSS `0x400300xx`, GPIO P4 `0x40040400` | [touch-mmio-cycle-2026-10-05/upstream/REPORT.md], [touch-flash-provider-2026-10-08] |

### 1.2 Toolchain and library identification (supersedes `toolchains.md` §5 / `libraries.md` §5)

The touch image is a ModusToolbox-style GCC build: Infineon PDL + CAPSENSE (MSCLP/LP), Emulated EEPROM + block-storage, newlib-nano, libgcc, GCC crtbegin/crti/crtn.

**Compiler: Arm GNU Toolchain 14.2.Rel1 (GCC 14.2.1 20241119, build arm-14.52)**, flags
`-mcpu=cortex-m0plus -mthumb -Og -ffreestanding -fno-builtin -DCY8C4046FNI_T412 -ffunction-sections`
(+ `-fdata-sections` needed for some units; small enums are the arm-none-eabi default). Matrix on unchanged
PDL `cy_msclp.c` (SHA `2613ec6f…`) [touch-compiler-matrix-2026-10-09], [touch-compiler14-successor-2026-10-09]:

| GCC | `Cy_MSCLP_Configure` 0x8FD0 (424 B) | `Cy_MSCLP_Capture` 0x8FA0 (48 B) | `Cy_MSCLP_ConfigureScan` 0x9178 (160 B) |
|---|---|---|---|
| 10.3-2021.10 | 173 bytes differ | exact | 30 differ |
| 11.3.Rel1 / 12.2.Rel1 | 125 differ | exact | exact |
| 13.3.Rel1 | 24 differ (one loop layout; `-fno-tree-ch`/`-fno-thread-jumps` don't fix) | exact | exact |
| **14.2.Rel1** | **exact** | exact | exact |

Preprocessed Configure text and all 27 non-compiler inputs are identical across versions, so the difference is compiler lowering, not source [touch-compiler-matrix-2026-10-09/ENVIRONMENT.md], [touch-compiler-matrix-2026-10-09/HYPOTHESIS-CLOSURE.md]. Not proven unique producer.

| Component | Identified source/pin | Evidence |
|---|---|---|
| Infineon PDL (`mtb-pdl-cat2`) | `35f1714623cfea682d5e285af80d50416b4c7bbc` (release-v2.21.0) for MSCLP/SCB/GPIO/SysClk/SysInt/SysLib/SysPm/SysTick | many exact sections, below |
| PDL flash driver | **PDL 2.16 pin `16aaf1d3d764ca3c426234c90cdeb6f19cb2d091`**: stock keeps a `c046` NOP before the SROM-status call; PDL 2.17 removed it and changed status processing; stock has no `WaitForSysCallFinish` retry loop | [touch-pdl14-history-layout-2026-10-09], [touch-pdl14-residual-boundary-2026-10-09] |
| System header | `system_cat2.h` from TARGET_CY8CKIT-040T `d1bf634023bf92d083ad0e32083987f67b4a64e6` (byte-identical in CY8CPROTO-040T) supplies `cy_israddress`, delay globals, `__RAM_VECTOR_TABLE` | [touch-pdl14-system-interface-2026-10-09] |
| CAPSENSE | repo gitlink is 3.0.1 (no LP sources); **6.10.0 `247a9a0f79eb976f144f5fbeb29488c1c2606517`** is the matching semantic comparator; exact bodies listed below | [touch-msclp-attribution-2026-10-08] |
| Emulated EEPROM | **emeeprom 2.60 `6cacf37b5cfec2dc9acf1a2c222c1e3038d03bd9`** (2.70/2.70.1 emit the same selected bytes; 2.40/2.50 lack sector-size field +4) | [touch-read-closure-2026-10-08], [touch-init-closure-2026-10-08] |
| Block storage | **block-storage 1.3.0 `0a9781309e0e1832d12e99cdf1d0f75843396a76`** `mtb_block_storage_pdl.c` (null nonblocking callbacks; 1.1/1.2.1 install non-null ones) — all 10 provider bodies exact; vendored at `third-party/upstream/infineon-block-storage-1.3.0` | [touch-init-closure-2026-10-08] |
| newlib | **nano** libc at revision `7923059bff6c120c6fb74b63c7553ea345c0a8f3` (from Arm 14.2 metadata), `-Os`; regular libc does not match; `__libc_init_array` needs `_HAVE_INIT_FINI` (newlib configure default) | [touch-newlib-init-array-discriminator-20261009-implementation], [touch-startup-provider-successor-2026-10-09] |
| libgcc / crt | GCC source `a05ea1e5ee0867191bb432a84c055be99dbdbc16`; `lib1funcs.S` (L_udivsi3, L_divsi3, L_dvmd_tls), `crtstuff.c` built with libgcc `CRTSTUFF_CFLAGS` (-O2), crti/crtn; libnosys `_exit` at default -O2 | [touch-libgcc14-source-rebuild-2026-10-09], [touch-crtstuff-source-rebuild-2026-10-09] |
| Generated CAPSENSE config (`cycfg_capsense.c/.h`, `.cycapsense`, final `.map`) | **absent**; not public (targeted search 2026-10-10) | [touch-reset-ownership-audit-20261010] |

Exact (byte-identical) library sections at stock VAs (all GCC 14.2 unless noted; "13.3" = also matched with 13.3):

| VA | Function | B | VA | Function | B |
|---|---|---|---|---|---|
| 0x33C0 | deregister_tm_clones | 32 | 0x9218 | Cy_SCB_ReadArrayNoCheck | 56 |
| 0x33E0 | register_tm_clones | 40 | 0x9250 | Cy_SCB_ReadArray | 30 |
| 0x3408 | __do_global_dtors_aux | 44 | 0x926E | Cy_SCB_WriteArrayNoCheck | 56 |
| 0x3434 | frame_dummy | 36 | 0x92A6 | Cy_SCB_WriteArray | 48 |
| 0x4480 | Cy_SysLib_DelayCycles (asm) | 18 | 0x92D6 | Cy_SCB_WriteDefaultArrayNoCheck | 16 |
| 0x4492 | Cy_SysLib_EnterCriticalSection | 8 | 0x92E6 | Cy_SCB_WriteDefaultArray | 48 |
| 0x449A | Cy_SysLib_ExitCriticalSection | 6 | 0x9316 | Cy_SCB_SetRxFifoLevel (header inline) | 44 |
| 0x5FBA | Cy_CapSense_InterruptHandler_V3Lp (13.3) | 12 | 0x9344.. | I2C slave HsMode 128, Stop 0x93C4 332, Ack 0x9510 168, Address 0x95B8 400, DataReceive 0x9748 180, DataTransmit 0x97FC 248 | |
| 0x614C | Cy_CapSense_ClrBusyFlags (13.3) | 36 | 0x9B0C | Cy_SCB_I2C_SlaveInterrupt | 300 |
| 0x6220 | GetPolySize (13.3) | 28 | 0x9C38 | Cy_SysClk_ExtClkGetFrequency | 12 |
| 0x6262 | GetLfsrDitherVal (13.3) | 14 | 0x9C80 | Cy_SysClk_ImoSetFrequency | 272 |
| 0x7050 | Cy_CapSense_ScanAllLpSlots (13.3) | 20 | 0x9D90/0x9DDC/0x9E18 | ILO Start/StopMeasurement, Compensate (`-fdata-sections`) | 76/60/284 |
| 0x7E04 | Cy_CapSense_TuInitialize (13.3) | 16 | 0x9F34 | Cy_SysClk_ClkHfGetSource | 16 |
| 0x8BF4 | Cy_Flash ProcessStatusCode + 20-entry table at 0xB51C (80 B) | 128 | 0x9F44 | Cy_SysClk_ClkHfSetSource | 88 |
| 0x8CC4/0x8D00/0x8D20 | Flash ClockBackup/Config/Restore (PDL 2.16) | 60/32/48 | 0x9F9C | Cy_SysClk_ClkHfGetFrequency | 56 |
| 0x8D50 | Cy_Flash_WriteRow (PDL 2.16) | 216 | 0xA188 | Cy_SysClk_ClkPumpSetSource | 56 |
| 0x8E28 | Cy_GPIO_SetHSIOM (incl. 8-B pool) | 60 | 0xA214 | __NVIC_SetPriority | 96 |
| 0x8E64 | Cy_GPIO_Write | 32 | 0xA274 / 0xA2A8 | Cy_SysInt_SetVector / Cy_SysInt_Init | 52/72 |
| 0x8E84 | Cy_GPIO_SetDrivemode | 58 | 0xA2F0 / 0xA324 | Cy_SysLib_Delay / DelayUs | 52/20 |
| 0x8EBE | Cy_GPIO_SetInterruptEdge | 36 | 0xA3B0 | Cy_SysPm_RegisterCallback | 148 |
| 0x8EE4 | Cy_GPIO_Pin_Init (174 code + 2 align + 12 lit) | 188 | 0xA444 | Cy_SysPm_ExecuteCallback (`-fdata-sections`) | 228 |
| 0x8FA0 | Cy_MSCLP_Capture | 48 | 0xA528 / 0xA58C | Cy_SysPm_CpuEnterSleep / CpuEnterDeepSleep | 100/104 |
| 0x8FD0 | Cy_MSCLP_Configure | 424 | 0xA5F4 / 0xA620 / 0xA638 | SysTick ServiceCallbacks / Enable / SetClockSource | 44/24/24 |
| 0x9178 | Cy_MSCLP_ConfigureScan | 160 | 0xA650 / 0xA6A8 | SysTick Init / SetCallback | 88/24 |
| 0xA6C0 | __aeabi_uidiv (+0xA7CC uidivmod 8 B) | 276 | 0xA7D4 / 0xA9A0 | __aeabi_idiv 460 / idivmod 8 | |
| 0xA9A8 | __aeabi_idiv0 (weak, + align) | 4 | 0xA9AC | exit (nano) | 40 |
| 0xA9D4 | memset (nano) | 16 | 0xA9E4 | __libc_init_array (+16 B literals) | 72 |
| 0xAA2C | memcpy (nano, byte loop) | 18 | 0xAA40 / 0xAA44 / 0xAA50 | _exit halt `fee7c046` / _init / _fini | 4/12/12 |

EEPROM 2.60 exact (32 functions/2,864 B), incl. ReadSimpleMode, WriteRow 100, CalculateRowChecksum, CheckRowChecksum, DefineLastWrittenRow 180, CheckLastWrittenRowIntegrity 180, GetNextRowPointer, CopyHistoricData 180, ReadExtendedMode 628, Cy_Em_EEPROM_Read 52, GetPhysicalSize 30, CheckRanges 108, ComputeEEPROMProgramSize 84, Init_BD 172, Init 64, EraseRow 100, WriteSimpleMode 172, Write dispatcher 52, Erase API 276. Not exact: CalcChecksum (60 B), CopyHeadersData (392), extended write (252), two 124-B row wrappers [touch-read-closure-2026-10-08], [touch-init-closure-2026-10-08]. Public `Cy_CapSense_ConfigureMsclpTimer` (0x5D90, 70 B) differs in 5 bytes under 13.3 (not retried with 14.2) [touch-active-timer-closure-2026-10-08]; `Cy_SysPm_CpuEnterDeepSleepNoCallbacks` public 36 B vs stock 40 B [touch-lp-application-closure-2026-10-08].

**Historical symbol corrections** (`g2/symbols/touch.tsv` was not edited): 0x9F34/0x9F44 are ClkHfGet/SetSource, not divider functions; 0xA188 is ClkPumpSetSource; 0x8AAC is `Cy_Em_EEPROM_Write` dispatcher (true read dispatcher 0x8A78); 0x85D4/0x8808 are WriteSimpleMode/WriteExtendedMode; 0x3A38 (`touch_config_load_from_eeprom`) and 0x3568 (`touch_config_read_adapter`) are on the **write** path; 0x7EA4 ("CheckRanges") is the program gate; 0x7D36 returns sensor status byte +6, not raw count; ProcessStatusCode is 128 B (old row 58 B); uidivmod is 8 B at 0xA7CC; idivmod 8 B at 0xA9A0; SetHSIOM/Pin_Init extents include literal pools [touch-pdl14-inline-emission-2026-10-09], [touch-clkpump14-attribution-2026-10-09], [touch-eeprom-dispatch-2026-10-08], [touch-calibration-closure-2026-10-08], [touch-libgcc14-division-2026-10-09], [touch-gpio14-linkage-2026-10-09].

### 1.3 Reset, startup and RAM layout

- Reset 0x4674: call no-op 0x4670, write `0xACED8865` to `0x40030038` (effect unknown), `cpsid i`; copy 192 vector bytes 0x3300→0x20000400 and set VTOR; copy descriptor at **0xB578** {src 0xB58C, dst 0x200004C0, 241 words = 964 B}; zero descriptor at **0xB584** {0x200008A8, 428 words → 0x20000F58} (descriptor grammar = Infineon GCC `linker.ld` copy/zero records); then call 0x3464 [touch-reset-layout-candidate-20261010].
- Reset body 0x3464..0x34B6: constructors (`__libc_init_array`) at 0x34A6, application **0x3CB4** at 0x34AE (normally does not return), `exit` at 0x34B2; weak `atexit` = 0 at 0x34D0. preinit array empty (bounds both 0x2000087C), init array = 1 entry at 0x2000087C → frame_dummy (flash 0xB948), fini at 0x20000880 → `__do_global_dtors_aux` (flash 0xB94C). Exit skips undefined weak `__call_exitprocs`, calls stdio handler 0x20000F54 if nonzero (BSS-zeroed), then `_exit` infinite loop [touch-crt-array-binding-2026-10-09], [touch-startup-provider-successor-2026-10-09].
- Reset-copied values: EEPROM library config 12 B at 0x200004C0 = `00 01 00 00 00 02 01 01 00 00 00 00`; `cy_delay32kMs` 0x2000086C = 786,432,000; `cy_delayFreqMhz` 0x20000870 = 24; `cy_delayFreqKhz` 0x20000874 = 24,000; `SystemCoreClock` 0x20000878 = 24,000,000. Only 25/964 copied bytes are source-owned; **939 B (mostly CAPSENSE configuration/context pointers) need the product `cycfg_capsense`** [touch-source-candidate-round2-20261010], [touch-reset-ownership-audit-20261010].
- Startup 0x3638: SysTick source 0 (`clk_lf`), reload 40, callback 0x35E5 in slot 0 increments u32 **0x200008E8** (gesture timebase) [touch-calibration-closure-2026-10-08].

Key RAM/ROM objects:

| Address | Object | Address | Object |
|---|---|---|---|
| 0x200004EC | global CAPSENSE context (`cy_capsense_context`) | 0x200009A0 / 0x200009B0 | I2C RX buf 16 B / TX buf 16 B (idle fill 0x5A) |
| 0xB2A8 | common config | 0x200008EC | I2C (SCB) context, event callback at +68 |
| 0x20000528 | common runtime (status u16, `lpDataSt` u16+22, LP history bytes +24..28) | 0x20000990 | 16-B report buffer |
| 0x20000C50 | internal runtime (ISR ptr +16, EOI cb +20, timers +28..+44) | 0x20000940 | 80-B gesture state |
| 0xB0F8 / 0xB188 / 0xB218 | widget 0/1/2 configs (stride 144) | 0x200009D0 | 8-B app record {magic u32, baseline u16, hold u16} |
| 0x20000548 | widget runtime (stride 60; widget1 ctx 0x20000584) | 0x200009C8 / 0x200009CC | budget u32 / app state byte |
| 0x20000624 | widget1 sensors (stride 10) | 0x200009CE/CD/CF | deferred-restart / deferred-save / calibration-pending flags |
| 0x20000AAC / 0x200009FC | active frame buf (5×28 B) / LP frame buf (4×44 B) | 0x200009D8 | last proximity code |
| 0x20000818 / 0x20000808 | active / LP slot descriptors | 0x200004E8 | active hold parameter |
| 0x2000065E | LP history (≤426 B window) | 0x200008C4 / 0x200008C8 | EEPROM ready flag / EEPROM context (32 B) |
| 0x200005C0 | widget2 (proximity) context | 0x20000ED4 | block-storage provider table |
| 0x20000CD4 | EEPROM row scratch (128 B) | 0x20000F04 | flash clock-backup state |
| 0x20000F1C/1D/1E | ILO compRunStat / preventMeasurement / measuring | 0x20000F20 | ext-clock frequency word |
| 0x20000F24 / F28 / F34 | SysPm lastExecuted / failed / callback roots | 0x20000F40 | SysTick callback array (5 ptrs) |
| 0x20000850 | DeepSleep PM descriptor (from ROM 0xB91C → cb 0xA1C1, params 0x20000CCC) | 0x20000F54 | stdio handler slot |

### 1.4 Host I2C protocol (supersedes the inferred slot order in `protocols.md` §9)

- Init 0x3678: registers event callback **0x3701** at I2C context +68, enables SCB1 and IRQ7; static borrowed 16-B RX/TX buffers [touch-callback-ownership-2026-10-08].
- Callback 0x3700: on write-complete (event bit 0x20) **without** error 0x40 and RX count 1..16, `cmd = rx[0]` (0..8) branches via a nine-entry in-frame table at **0xB0C4** (`mov pc,r3`, not calls). All write paths rearm RX16. Read-complete (0x10): fill TX with 0x5A, rearm, release attention (P4 DR_SET 0x40040440 ← 1). Both bits: write handling first, so a simultaneous read-complete overwrites a write ACK [touch-commands-2026-10-08].

| cmd | Handler | Behavior (instruction-proven) |
|---|---|---|
| 0, 3 | 0x370E | no-op; rearm RX only |
| 1 | 0x3746 | TX prefix `02 02 00 01` (= protocol/version word 0x01000202); other 12 bytes stale |
| 2 | 0x382C | ACK `02 00 17`, write mailbox byte at 0x20000000, jump to reset entry 0x7E14 (DFU); ACK delivery not guaranteed |
| 4 | 0x384C | 10 B: widget1 sensor `difference` u16 ×(≤4) at 0..7, widget2 difference at 8; LE; last 6 TX bytes stale |
| 5 | 0x37A0 | set calibration-pending 0x200009CF; ACK `05 00 17` (calibration happens at next report) |
| 6 | 0x3766 | first 2 TX bytes = saved baseline u16 (RAM 0x200009D4); 14 bytes stale |
| 7 | 0x37C8 | if RX count ≤2 or u16LE payload == 0: `07 FF 17`; else store hold threshold (0x200009D6, 0x200004E8), set deferred flags 0x200009CE/CD, ACK `07 00 17` |
| 8 | 0x3780 | TX zeroed, hold threshold u16LE at 0 |

- Report (16 B at 0x20000990, copied to TX): bytes 0–3 event (gesture flag/payload, proximity), +4 sensor baseline, +6 raw, +8 difference, **+10 saved baseline as it was *before* this report's calibration**, last 4 bytes stale. Publish slice 0x3C18..0x3C36 copies to TX, arms TX (0x9AD8), asserts attention P4.0 (DR_CLR +0x44 ← 1); sets state 1 / budget 640. Attention rearm 0x3AFC: GPIO +0x44 ← 2, delay(200), +0x40 ← 2 [touch-calibration-closure-2026-10-08], [touch-gesture-machine-closure-2026-10-08].
- No-event processing leaves the previous report in TX; repeated host reads return stale frames.
- PDL I2C ABI (small enums): config 24 B (mode +0, RX/TX FIFO flags +1/+2, addr +3, mask +4, accept +5, general-ACK +6, HS +7, wake +8, filter +9, low/high phase +12/+16, addr delay +20); context 84 B (state +4, master status +8, slave status +32, event/address/HS callbacks +68/+72/+76) [dependency-followup-2026-10-08].
- `Cy_SCB_I2C_SlaveInterrupt` order: wake; bus/arbitration error (0x101 → slave status 0x100/0x80, mask RX, force STOP path); pending RX on STOP; HS; RX (skipped if address-accept 0x10000 and address-match 0x40, so the address byte isn't consumed as payload); STOP then status reload; address; TX (0x41) [dependency-followup-2026-10-08].
- SCB FIFO: RX status +0x308 (used, mask 0x1FF), RX_CTRL +0x300 (width), RX_FIFO_RD +0x340; TX status +0x208, TX_CTRL +0x200, TX_FIFO_WR +0x240; depth 16 if `CTRL & 0xC000 == 0` else 8; counts are elements; `SetRxFifoLevel` executes `BKPT #1` on level ≥ depth [touch-mmio-cycle-2026-10-05].

### 1.5 Application loop (0x3CB4) and timers

- State byte 0x200009CC dispatched at 0x3D5E; budget u32 0x200009C8 [touch-lp-application-closure-2026-10-08], [touch-active-timer-closure-2026-10-08]:
  - **State 1** (active, interval 7773 µs ≈128 Hz): after each successful processing pass budget−1 (wrapping); on reaching 0 → state 2, budget 160, interval 31211 µs. A report sets state 1, budget 640.
  - **State 2** (active, 31211 µs ≈32 Hz): activity → state 1 / 7773; budget not decremented here.
  - **State 3** (LP): `Cy_CapSense_ScanAllLpSlots` (0x7050 → 0x6D74, slots 0–3); **return value discarded**; loop deep-sleep while status bit 0x80 (busy); then signal bit 0x400 → state 1/640/7773 else state 2/160/31211.
  - Literals 7773/31211 at 0x3EC0/0x3ECC.
- Active timer setter **0x5D90** (`ConfigureMsclpTimer`): stores µs at internal+28, cycles at +32; updates live AOS_CTL+0x70 low16 only if common status has 0x10 (active scanning). Converter **0x5D70**: `c = (us*factor mod 2^32) >> 14; if c: c-1; min(c, 65535)`; factor internal+44 initial 655 (= 40 kHz·2^14/10^6). 7773 → 309, 31211 → 1246. LP/WOT interval +36, cache +40 [touch-active-timer-closure-2026-10-08], [touch-clock-selection-closure-2026-10-08].
- Gesture timebase: SysTick on `clk_lf` reload 40. **Inferred**: with nominal 40 kHz ILO this is ≈1 kHz, so hold default 1000 ≈ 1 s and tap window 300 ≈ 0.3 s (unmeasured).
- Software delay `Cy_SysLib_Delay(ms)`: loops of `cy_delay32kMs` for >32768 ms, else `ms*cy_delayFreqKhz` cycles; `DelayUs(us) = us*cy_delayFreqMhz`; DelayCycles: `(n+2)>>2` iterations [touch-syslib14-delay-linkage-2026-10-09], [touch-syslib14-assembly-2026-10-09]. EEPROM default write uses delay arg 10 (×24000 scale).

### 1.6 Gesture engine (0x4070, 874 B; speed helper 0x3EFC, 324 B)

80-B state at 0x20000940: hold threshold u16 +0; previous/current/press samples +4/+12/+20 (position byte + u32 counter); elapsed +28; tap count/pending +32/+33; release/motion counters +36/+40; motion anchor +44; 3 speed samples +48 (stride 8); ring index/count/filtered speed/direction +72..+75; mode +76 (2 = hold); output 3 bytes +77. Zero threshold → 1000 [touch-gesture-machine-closure-2026-10-08].

| Flag | Trigger |
|---|---|
| 0x01 | new press (resets speed history, anchors) |
| 0x02 | release (also after hold/drag; hold release emits only 0x02) |
| 0x04 | pending tap after idle **>300** counts; payload = tap count (counts 1 and >9; counts 2–4 emit nothing; 5–9 clear and call attention rearm) |
| 0x08 | second short release → `0A 02 00` (double tap) |
| 0x10 | stationary hold: elapsed **≥** threshold and displacement ≤24 (emitted exactly at threshold) |
| 0x20 / 0x40 | negative / positive motion; payload distance + filtered speed; drag starts at displacement >24, needs >99 counts since anchor, later updates >14; on drag release may emit 0x22/0x42 |

Short release = elapsed <300; press joins tap sequence if gap ≤300; tap count saturates at 255. Speed: direction set when |Δpos|>3; reversal clears filter; `speed = min(255, (|Δpos|*100 + dt/2)/dt)`; `filtered = (4*speed + 6*old)/10` (adopt directly when old = 0); equal timestamps return old filter or 1 (not stored) [touch-gesture-speed-closure-2026-10-08].

### 1.7 CAPSENSE configuration (locked factory values)

| Widget | Config VA | Type / method | Sensors | Key parameters |
|---|---|---|---|---|
| 0 | 0xB0F8 | type 7 (LP), method 1 | 4 electrodes, LP slots (0,0)…(0,3) | LP processing words below; drives LP wake |
| 1 | 0xB188 | type 2 linear slider, CSD (method 1) | 4 | resolution 200, centroid cfg 1, position IIR 128/256 (cfg 0x00800102), raw filters 0x6000 (CPU median/IIR/avg off), finger 480, hysteresis 55 (on 535 / off 425), noise 300 / neg-noise 200, neg-reset 30, baseline IIR 1/256, on-debounce 1, auto-reset off |
| 2 | 0xB218 | type 6 proximity, method 1 | 1 | flags 0x3696: CPU median(3) → IIR 64/256 → avg(4); proximity threshold 160 (on >170, hold >150), finger 1000 (1010/990), hysteresis 10, on-debounce 3, noise/neg 40, baseline IIR 1/256, neg-reset 30 |

[touch-slider-producer-closure-2026-10-08], [touch-proximity-producer-closure-2026-10-08], [touch-lp-history-closure-2026-10-08]. Each widget record 144 B: ctx ptr +0, method +122, dither % +135, auto-select +136, saturated-scan selector +138, chop cycles +132; runtime 60 B: divider u16+14, source byte +33 (low2: direct/SSC/PRS; bit4 SSC-auto, bit8 PRS-auto), status +35 (enabled = bits 2|4), conversions u16+44, LFSR range +56; sensor 10 B: raw +0, baseline +2, diff +4, status +6 (bit1 prox, bit2 touch, bit4 overflow), neg-reset count +7, fraction +8, compensation +9 [touch-clock-selection-closure-2026-10-08].

LP processing frame (first 5 of 11 words per LP slot), stock: w0 `0x0A1E0461` (raw coef 1, slow baseline 6, fast 4, low-baseline reset 30, update delay 10), w1 `0x001E001E` (noise thresholds 30/30), w2 `0x00010096` (signal threshold 150, debounce 1, CSD), w3/w4 0. Launch writes `CE_CTL` (HW+0x74) = `0x80000100`: channel engine + baseline/signal detection on, **LP raw IIR (RCF) off** [touch-lp-filter-closure-2026-10-08].

Slots: 5 active (stride 28 B: six scan words + IIR word at +24) and 4 LP (stride 44 B: 5 processing + 6 scan words). Base config 256 B at context+36's pointer; three mode records at +144 (7 words each: senseDutyCtl, swSelCdacFl, swSelTop, swSelComp, swSelSh, swSelCmod1, swSelCmod2); defaults ROM 0xB41C, dither variants 0xB470/0xB48C/0xB4A8, pin-function words ROM 0xB4C4 → base+112; offset 52 never written [touch-base-frame-closure-2026-10-08], [touch-frame-generation-closure-2026-10-08], [touch-all-slot-closure-2026-10-08].

### 1.8 Scan engine

- IRQ: startup 0x38E0 passes config ROM 0xB0F0 (IRQ8, prio 3) + handler 0x3949 to `Cy_SysInt_Init`; wrapper 0x3948 → 0x5C98(hw unused, ctx 0x200004EC) → 0x5FBA (`InterruptHandler_V3Lp`: `ctx->internal->ISR(ctx)`, **no null check**) → ISR **0x6780** [touch-scan-isr-closure-2026-10-08], [touch-public-dispatch-attribution-2026-10-08].
- ISR 0x6780: reads INTR_LP (HW+0x120) & mask (+0x128); bit 0x10000 → active path, else LP path. Active: ack, transfer 0x6462, currentSlot (+52) += numSlots (+70); continue if ≤ endSlot (+54) else disable CTL, MRSS_STOP 0x100, active scan counter u16+4++, complete. LP: signal bit0 → status 0x400; if `lpDataSt` bit0, history transfer 0x6530 and counter byte 27++; disable, MRSS_STOP, complete. Completion 0x614C clears status 0x01 then 0x80 and calls EOS callback with NULL.
- Active transfer 0x6462: descriptors (widgetId, sensorId) u16 pairs stride 4; for enabled widgets read FIFO HW+0x3200 → raw low16, overflow from FIFO bit16 → status bit 0x04; frame word6 low24 ← raw<<8 or HW+0x2000 sensor-data word (if internal byte 118).
- LP history 0x6530: used = HW+0x3410 low11; HW+0x3414 bit31 → state 1 (reset) or 3 (reset|valid) at common byte 28; first/count/frames at bytes 24/25/26 (frames = used/count truncated to 8 bit); history is **positional** u16 per slot (disabled slots skipped, not compacted); CSD stores raw, CSX/ISX store max(maxRaw−raw,0). No CPU consumer found; gate bit cleared at reset by TuInitialize 0x7E04. Result-window start `256 − (floor(256/count) − 11)*count` (4 slots → word 44, 212 results = 53 frames = 424 B) [touch-lp-history-closure-2026-10-08], [touch-lp-filter-closure-2026-10-08].
- Slot loader 0x664C: numSlots = min(count, 21); 11 HW words per slot; MRSS wait (441) result discarded; SS callback gets active-scan-context; FRAME_CMD 1.
- LP launch 0x6D74: guards count 1..8, last ≤3; **clears status 0x400 before busy test**; busy → 0x40; switch mode 2; set busy 0x81, repeat flag; copy frames to HW+0x2000, LAST bit, SENSOR_INIT HW+0x3C00, bridge-ready HW+0x341C (fail → 4, busy/0x20 retained). Same-range relaunch skips frame copy/SENSOR_INIT (**edited coefficients not reloaded**).
- Active launch 0x6BD4: first ≤4; busy 0x40; sets busy **before** mode-switch errors; reuse needs prior cfg 2/4, same start/count, count ≤21, no 0x2000, status 0x10; full setup writes CE_CTL `0x80000000|byte118`, masks FRAME 0x10000.
- Mode switch 0x6AC0 (mode byte internal+85, repeat flag +115): same mode returns 0 without clearing repeat; valid prior 0,1,2,5,6,7; requests 0/1 state, 2 regular pins+base, 3 BIST, 5 saturation, 6 CPU, 7 auto-dither (0x68EC, return discarded); 4/>7 fail; PDL Configure failure → 0x40 with no rollback [touch-mode-closure-2026-10-08], [touch-regular-mode-composition-2026-10-08], [touch-auto-dither-closure-2026-10-08].
- CPU setup 0x685C: MRSS status HW+0x180 bit0, MRSS cmd 1, wait up to 315 (0x6608 waits for masked value to *change*, returns 4 on exhaustion) — **status discarded**; 0x6A80 saturation config writes HW+0x608/0x60C stride 64.
- Preparation **0x71C8**: clock init 0x6384 → base 0x5378 → both slot arrays (even on clock error) → ISR ptr 0x6781 at internal+16, wake timer → EOI callback → (status 0 only) mode 1, mode 2, dither scale 0x7064 → max-raw init 0x5CAC for all widgets. Dither scale: per sensor saturated measurement (poll arg 1753), max → scale byte runtime+51: ≤32→6, ≤55→5, ≤111→4, ≤337→3, ≤563→2, ≤1127→1, else 0 [touch-scan-preparation-closure-2026-10-08].
- Saturated scan 0x7BC0: mode 5, temp frame, `ConfigureScan` 0x9178 (mode 5: zero HW+0x3020 then 5 words at 0x3024; mode 11: 11 words; default 6 words at 0x3020), trigger 0x6928 (HWCTL bit31, HW+0x120 ← 0x01110011, ack +0x100 ← 0xC1011111, start +0x3800 ← 1), watchdog 0x7288 / poll 0x6980 (returns remaining budget, acks all interrupt classes). Always reads FIFO and writes output even on timeout (status bit 4). Max-raw correction: `div=(ctl>>16)&0xFFF; epi=(src==2?96:2)*((div+4)>>2)` (−1 for even div+1 or PRS method 1/10); `(fifo−epi)*chop` unsigned, ≥65536 → 65535, 0 → 1 [touch-saturated-scan-closure-2026-10-08], [touch-max-raw-closure-2026-10-08], [touch-scan-watchdog-closure-2026-10-08], [touch-scan-frame-closure-2026-10-08].
- Clock init 0x6384 (3 widgets): SSC/PRS/LFSR auto-selection (0x6294/0x623C/0x6352), polynomial period `2^N−1`; dither amplitude `1 << ((range&3)+scale+1)`; mutates fields before validating divider; bad divider → 0x800 and stop. PRS divider helper 0x5528 has **no minimum clamp** (div <4 encodes 4095) [touch-clock-selection-closure-2026-10-08], [touch-frame-generation-closure-2026-10-08].
- Pins 0x5FC6/0x6044/0x6078/0x60EA: HSIOM 4 bits/pin, drive 3 bits/pin at GPIO+8, input-disable +0x18, analog ownership +0x24, all in a critical section; regular mode drive 9, mux 0, AMUX 1, out 0; electrode desc stride 8 (port ptr, pin) [touch-pin-control-closure-2026-10-08].
- Initialization 0x7278 / 0x4C84..0x4D8E: enable widgets, request max-count bits 8/16 for zero maxima, switch mode 0; capture wrapper returns 0x80 if driver locked (key 2 = CAPSENSE) [touch-cap-initialization-closure-2026-10-08].

### 1.9 Sensor processing → report

- Process-all 0x4C04 visits widgets 2,1,0 (skips type 7); per-widget 0x4BA8; clamp 0x5BC0; raw/baseline/diff 0x5938; slider centroid 0x5A94 via 0x5BA2. Baseline 0x4FEE: `hist=(base<<8)|frac; hist=(raw<<8*coef + hist*(256−coef))>>8`; negative reset on 31st sample with limit 30; difference 0x5920 = raw−baseline only above noise. Centroid 0x48CC (forces ≥3 sensors; first max-neighbourhood tie wins); position IIR 0x4A2A (seed on new touch); inactive output leaves stale X — consumers must check active/count [touch-slider-producer-closure-2026-10-08].
- Proximity debounce: two counters per sensor (bits 1, 2), decrement-then-test, 3 qualifying calls to activate; producer preserves overflow bit 4 [touch-proximity-producer-closure-2026-10-08].
- Classifier 0x441C (saved baseline B): code 2 if widget2 status nonzero (**any** bit, incl. overflow) else 1; override to 2 if sensor baseline > B+500; to 1 if baseline < B and raw ≤ B+49; B = 0 bypasses overrides; returns change vs 0x200009D8.
- Report builder 0x3B24: obtain widget1 activity/position, proximity, gesture; **no gesture and no proximity change → early return** (calibration stays pending). Calibration: |sensor baseline − saved| ≥ **50** updates (49 skipped), RAM first, then persist, then clear flag; flash failure doesn't roll back RAM [touch-calibration-closure-2026-10-08].

### 1.10 Persistent configuration (Emulated EEPROM)

- Factory config: capacity 256 B, **extended mode**, wear 2, redundancy 1, blocking 1; base patched to **0xE400**; row = sector = 128 B (getters 0x4784/0x4788); historic 64, payload 48, 4 logical rows; main 0xE400–0xE800, mirror 0xE800–0xEC00 (outside OTA) [touch-init-closure-2026-10-08].
- App record (8 B, at EEPROM address 0, RAM 0x200009D0): magic `0x45564E55` ("UNVE"), baseline u16, hold u16. Bootstrap 0x395C: init 0x34D8 → read 0x3520; needs read success **and** magic; hold 0 → 1000 in RAM only (never written back). Failure: log, erase 0x35B0, delay(10), write defaults `{UNVE,0,1000}` via 0x3568 [touch-bootstrap-closure-2026-10-08].
- Adapters: null buffer / `(addr+size)>256` → 4; not ready → 1; read success statuses 0 and 0x093E0004 → 0, else 2 (write/erase → 3).
- Deferred worker 0x3A80 (critical section snapshots/clears flags CE/CD): CE → reinit gesture state with new threshold; CD → set UNVE, write 8 B via 0x3A38→0x3568→0x8AAC [touch-commands-2026-10-08].
- Write dispatcher 0x8AAC: reject size 0, `(addr+size) mod 2^32 > capacity`, null; simple (context byte 13) vs extended; reject 0x093E0000. EEPROM context (32 B): logical rows u16+0, physical row u16+2, sector u32+4, capacity +8, wear +12, simple +13, redundant +14, program mode +15, base +16, historic cap u16+20, payload cap u16+22, last row +24, provider +28 [touch-extended-rows-2026-10-08], [touch-read-closure-2026-10-08].
- Row: checksum u32+0, sequence +4, logical address +8, length +12, payload +16, historic half +64. Row CRC **0x7F6C: CRC-8 (seed 0xFF, poly 0x31, MSB-first) over bytes 1..124** (excludes byte 0 and 125..127). DefineLast picks strictly greater unsigned sequence with valid CRC (main wins ties; 0xFFFFFFFF outranks wrapped small). Redundant copy at +rows·wear·rowsize. Erase API writes a versioned empty row into every main/mirror row (not all-zero) [touch-history-closure-2026-10-08].
- Provider 0x20000ED4 (creator 0x486C): slot5 copy 0x4861 (returns 0), slot6 program rows 0x4811, slot7 zero rows 0x47B1, slot11 is-erase-required 0x47AB → 0. Row adapters iterate 128-B rows and **discard every `Cy_Flash_WriteRow` status, returning 0** [touch-flash-provider-2026-10-08].
- `Cy_Flash_WriteRow` 0x8D50: main <0x10000 or SFLASH 0x0FFFF200..0x0FFFF3FF, 128-B aligned; SROM load opcode 4, then with IRQs off backup 0x16, config 0x15, program 5 (main) or 0x18 (SFLASH), restore 0x17; program error precedes restore error. Status decoder 0x8BF4 reads SYSARG once: 0xA… → 0; F0000001 → 0x00520001; F0000003/4 → 0x00520004; F0000005 → 0x00520005; F0000007 → 0; F0000008/9 → 0x00500008/9; F0000011/13/14 → 0x00520021; other F → 0x005200FF; else 0x00500023.

### 1.11 Power management, clocks, ILO

- SysPm descriptor 28 B (cb +0, type +4, skip mask +8, params +12, prev/next +16/+20, order +24); roots 0x20000F34 by type; sorted by order, stable. Phases: CHECK_READY(1)/BEFORE(4) forward, stop only on exact FAIL `0x4200FF`; CHECK_FAIL(2) backward from predecessor of shared last-executed (0x20000F24); AFTER(8) backward from tail. Only registered callback: ILO clock callback 0xA1C0 (type DeepSleep, order 0xFF): CHECK_READY fails if measuring else sets prevent; CHECK_FAIL/AFTER clear prevent. Init 0x4650 → 0x4634 registers it; app calls 0x4650 at 0x3CB6. DeepSleep path copies SFLASH u16 0x0FFFF152 → SRSS_PWR_KEY_DELAY 0x40030004, SCR |= 4, WFI [touch-pm-callbacks-closure-2026-10-08], [touch-ilo-pm-closure-2026-10-08].
- ILO compensation 0x5DD8: start measurement (COUNTER1 0x4003001C ← SystemCoreClock>>10), poll Compensate(500 µs) **retrying every nonzero status with no timeout**, factor = `((COUNTER2<<24) mod 2^32)/10^6`, recompute both active and LP caches, update live AOS_CTL from the selected one. Statuses: 0x4A0001 bad args (range 100..2,000,000 µs), 0x4A0003 bad config/zero count, 0x490004 in progress [touch-ilo-compensation-closure-2026-10-08].
- HF source: GetSource reads bits 0–1; SetSource rejects >1 (0x4A0001), checks IMO ready / ext freq nonzero (0x4A0003) [touch-clkhf14-attribution-2026-10-09]. `SysInt_SetVector` only replaces handler when VTOR == `__RAM_VECTOR_TABLE` 0x20000400 (else returns ROM `__Vectors` 0x3300 entry) [touch-sysint14-linkage-2026-10-09]. SysTick service invokes callbacks only when COUNTFLAG set [touch-systick14-linkage-2026-10-09].

### 1.12 Touch stock quirks / latent bugs (software-level; none hardware-confirmed)

1. Command 7 ACK (`07 00 17`) is prepared before persistence; flash errors are discarded by adapters, so ACK/status 0 never certifies storage. Commands 6/8 read RAM, not flash.
2. Calibration (cmd 5) stays pending until a report event; the report that performs it carries the old saved baseline.
3. Simultaneous read-complete overwrites a write ACK; TX buffer is shared by the main-loop report producer and IRQ callback; descriptor updates are multi-store and not IRQ-atomic.
4. LP launch return ignored by the app; launch failures leave busy set → app can sleep-loop with no transition.
5. MRSS start/stop wait results discarded (CPU setup, slot loader, reuse); saturated scan writes output on failure; max-raw underflow yields 65535; preparation keeps mutating after errors (no rollback anywhere).
6. LP history writer has no bound check; window before LP descriptors is 426 B (FIFO used ≥216 with 4 slots would overwrite descriptors — synthetic only).
7. `Cy_SysPm_ExecuteCallback` phase 8 dereferences NULL on an empty list (wrapper guards it); shared last-executed pointer across callback types.
8. ILO compensation retry loop has no timeout; `Stop` doesn't clear running byte.
9. PRS divider no min clamp; clock init mutates before validating.
10. `Init_BD` discards last-row scan status; bootstrap stores hold 0 as 1000 only in RAM.
11. Classifier treats overflow-only status as proximity.

### 1.13 Touch open blockers

- Product `cycfg_capsense.c/.h` / `.cycapsense` / final `.map`: 939 of 964 reset-copy bytes, LP-history allocation size, and widget-record halfword at offset 142 (nonzero `0x1AA`, `0x1A1`, `0x115` in the three 144-B records 0xB0F8/0xB188/0xB218; CAPSENSE 6.10 schema ends at `iirCoeffHw` +140) are unexplained [component-goal-20261013/touch-blocked-frontier-003/receipt.json].
- Startup composition 0x3464, absolute link map, whole-payload equality, and all physical timing/analog/SROM behavior.
- Resident bootloader/DFU engine (cmd 2 jumps to 0x7E14 after mailbox) is not in the OTA payload.

---

## 2. Charging case (STM32G0B1, "B200", fw 1.2.57)

### 2.1 Image identity and toolchain (supersedes GCC claim in `toolchains.md` §6)

- Locked `firmware_box.bin` SHA-256 `36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374` (55,784 B incl. 32-B `EVEN` header); raw image SHA `773b6d4cfdaf0a5a74a557e3babe8222a0ae813436b76a7437c1096d2c60d677`, **55,752 B**, load 0x08000000 [case-ack-source-candidate-20261010], [component-goal-20261013/case-frontier-012/REPORT.md].
- **Producer = Arm Compiler 6 (armclang) + armlink, Keil MDK project ("TC-ARMCLANG6")**: Keil reset trampoline/scatter-loading runtime, Arm C-library division helpers (unsigned 0x08000160 44 B, signed 0x0800018C), Arm compact switch helper 0x08009190 (table follows the BL inline, index from LR−1, clamps to last entry), FreeRTOS `uxListRemove` register allocation. A 432-build GCC matrix and LLVM runs don't match the whole image. No armclang/armlink executable is available (only a Windows MDK 5.43a installer); per-file flags/scatter not recovered [case-flash-compiler-recipe-boundary-2026-10-09], [component-goal-20261013/case-frontier-012/REPORT.md], [dependency-followup-2026-10-08].
- An open Clang LTO source build of 401 C units produces **63,122 B** (7,370 B over stock); it fits the active bank below the reserved page 0x0803F000 with 194,920 B headroom [component-goal-20261013/case-current-frontier-020/REPORT.md].
- STM32CubeG0 HAL lineage: RX helpers match **v1.4.5** (`ba4210f57d3c863d31ace271219a12f43ab59847`) behavior; 1.4.0/1.4.3/1.4.4 rejected (non-atomic clear / RxEventType unchanged); 1.4.6/1.4.7 rejected (clear CR1.RTOIE on completion when CR2.RTOEN). Repo pin 1.4.7 (`a0cf8a8b…`) is only a comparator. Stock TOIDLE circular-DMA branch returns on full count (differs from retained HAL source) [case-uart-receive-closure-2026-10-08], [case-uart-start-closure-2026-10-08], [case-uart-toidle-branch-20261010].
- FreeRTOS: FromISR queue send increments `cTxLock` directly (matches **V10.4.3** `9c048e0c…`; V10.5.1 caps via task count). CMSIS-RTOS2 `osEventFlagsSet` ISR return = requested flags (matches CMSIS-FreeRTOS **v10.3.1/v10.4.6**, not v10.5.1) [case-queue-version-closure-2026-10-08], [case-event-flags-closure-2026-10-08].

### 2.2 Function map (case VAs)

| Area | Addresses |
|---|---|
| Mask save/restore (PRIMASK) | 0x080000F4 / 0x080000FC (byte-exact from source) |
| Copy helper (forward/dispatch copy) | 0x080001B4 |
| Legacy cmd / binary cmd / record router | 0x08000928 / 0x08000E1C / 0x08001E94 |
| Frame dispatcher / hex digit | 0x0800085C / 0x08009B94 |
| Flash fill (SN windows) | 0x08002F60 (8 B from 0x0803F800), 0x08002F88 (16 B from 0x0803F000) |
| HAL_DMA_Abort / _IT | 0x0800487A / 0x080048E6 (IT: no null guard; non-busy path doesn't unlock) |
| GPIO write leaf / wrappers | 0x08004E9E (+0x18 BSRR set / +0x28 BRR reset), 0x08004E94; 0x08006B80 (GPIOA mask 0x40), 0x08006B98 (mask 0x80) |
| HAL tick getter | 0x08004EAC (u32 0x20000120) |
| FLASH unlock (corrected) | **0x08004BF4 = HAL_FLASH_Unlock** (KEYR +0x08, 0x45670123/0xCDEF89AB); **0x08004B6C = HAL_FLASH_OB_Unlock** (OPTKEYR +0x0C, 0x08192A3B/0x4C5D6E7F) — historical labels swapped [case-flash-unlock-label-correction-2026-10-09] |
| PWR | 0x08005048 = HAL_PWREx_ControlVoltageScaling (not clock poll); 0x080050E8 = **STOP entry** (mislabeled EnterSLEEPMode); 0x080050A8 / 0x08005094 wake-pin enable/disable; 0x0800502C system reset (AIRCR ← 0x05FA0004) |
| UART | IRQ wrapper 0x08008F98 → HAL_UART_IRQHandler 0x08005F50..0x08006230; ErrorCallback 0x08005F42, RxEventCallback 0x08005E6A, TxCplt 0x08006776, Wakeup 0x08005EFE, TXFE 0x08005EFC, RXFF 0x08005E6C (all `bx lr`); EndRxTransfer 0x080086F4; DMA abort cb 0x080086E0; RxISR 8/16-bit 0x08008998/0x08008758, FIFO 0x08008A48/0x08008808; Receive_IT 0x080064EC → 0x08008D98; blocking read 0x080063EC; blocking write 0x080066AC; flag wait 0x08008EC4 |
| Frame callback (RxCplt) / resync / DE predicate | 0x08006544 / 0x0800A358 / 0x0800BE74 |
| Send / ack / hex log / printf / formatter / out cb | 0x0800680C / 0x080068D0 / 0x080067C8 / 0x08009170 / 0x08009210 / 0x0800A380 |
| App init / consumer task / policy / hall / USB | 0x08006968 / 0x08006E1C / 0x08007214 / 0x08003C2C / 0x08003D24 |
| Board peripheral init (VOS → sysclk → clock path) | 0x0800B600 |
| CMSIS event flags new/set/clear | 0x0800A836 / 0x0800A888 / 0x0800A7D2 |
| Event group | create 0x0800C48C (32 B), ClearBits 0x0800C44C, ClearBitsFromISR 0x0800C478, GetBitsFromISR 0x0800C4CC, SetBits 0x0800C4DE, SetBitsFromISR 0x0800C568, clear/set callbacks 0x0800BF84/0x0800BF8C |
| Timer/queue | xTimerPendFunctionCallFromISR 0x0800CE0C, timer daemon cmd drain 0x0800B0FC, xQueueGenericSendFromISR 0x0800C7A8, receive (nonblocking) 0x0800C83A, create 0x0800C5D0, copy-to/from 0x0800AD48/0x0800AD24, queue init 0x0800AC84 |
| Kernel | enter/exit critical 0x0800BFFC/0x0800C014 (nesting 0x2000019C), suspend 0x0800C380, resume 0x0800CC0C, scheduler state 0x0800CA4C, increment tick 0x0800CA78, disinherit 0x0800CB38, remove-from-event-list 0x0800CBA0, remove-from-unordered (event unblock) 0x0800C1CC, uxListRemove 0x0800BF2C, list insert end 0x0800BFE2, reset next unblock 0x0800B260, yield 0x0800C0A0 (ICSR ← 0x10000000), heap insert 0x0800AFCC (free head 0x20000194) |
| Sensor/charger bit-bang | transaction 0x080028B4 (start 0x0800A4B4, byte out 0x0800A46C, ack 0x0800A4FA, byte in 0x0800A436, pulses 0x0800A3D2/0x0800A414, stop 0x0800A4DC; lines 0x0800A550/0x0800A574 on GPIOB 0x50000400, pin select 0x20000114, delay 0x0800A408/0x0800A148), guarded wrapper 0x080035B8 (recursion flag 0x20000029), byte read 0x0800A124, counted 0x0800A130, word read 0x0800A074 (read twice, delay, third read on mismatch; BE u16) |
| Output bus (0x3F) | program 0x08009108 (bus 0x08000610 cmd 0x42, 9 retries, counter 0x20000080), shadowed setter 0x080099E8 (shadow 0x20000090+idx), enable 0x0800D154 (setter (3,0xAE),(4,0xAE),(5,3),(6,0x81)) |
| Flash apply (SN write) | 0x0800373C → mode 0x08002F46/status 0x08004A00, unlock 0x08004BF4, read 0x0800497C retry wait 0x08004958, write 0x08004B94 at 0x0803F000/0x0803F008, finalize 0x08004B20; config words 0x200001A4..B0 |

RAM: FreeRTOS kernel block 0x20000128 (+0x14 running, +0x30 suspended; task count 0x20000130), SystemCoreClock 0x20000124, event group ptr **0x200000F0** (app base 0x200000B8+0x38, created at 0x08006A06, attrs 0x0800D35C, name 0x0800D930), deferred timer queue handle 0x20000164 (storage 0x20001508, control 0x200014B8, len 10 × 16 B), UART1 handle **0x20000E24**, frame buffer **0x20000974** (1200 B, ends at handle), frame count u16 0x2000010A, scratch/last byte 0x20000108/0x20000109, forward buffer 0x200001B4, log context 0x200001A0, **log-quiet byte 0x200000BF** (nonzero suppresses logs; written by cmd 0x68 / legacy 0xAF), record buffer 0x20000664 (0x118 B, cleared per record), OTA chunk buffer 0x2000077C [case-frame-callback-closure-2026-10-08], [case-multiwaiter-closure-2026-10-08], [case-deferred-event-closure-2026-10-08].

### 2.3 UART framing and RX path (USART1 0x40013800, no DMA in normal RX)

- RX is one byte at a time (`HAL_UART_Receive_IT` into 0x20000108) then **0x08006544**: accepted starters at count 0: `0x5A`, `D`, `d`. Binary `5A A5 7F <len8>` (body requested at count 4 with timeout 10, complete at len+5) or `5A A5 CF <len16 LE>` (count 5, timeout 20, complete at len+6) — the bulk read 0x080063EC is blocking. ASCII `DE…` lines (case-insensitive) complete on newline, ≤60 chars. Completion posts event **0x08**; rearm failure posts **0x40**. Ignores non-USART1 handles. Resync keeps a trailing 0x5A only if old count ≥2 [case-frame-callback-closure-2026-10-08].
- Consumer task 0x08006E1C snapshots flags, clears 0x08, calls dispatcher 0x0800085C, resets count. Dispatcher: count <2 ignored; raw `0xDE` → legacy(frame+1, count−1); ASCII `DE` → in-place hex decode (invalid digits → 0, odd char dropped) → legacy(frame+1, count/2−1); `5A A5 7F` checks frame[3]==count−5 → binary(frame+4, count−4, mode 0); `5A A5 CF` checks u16==count−6 → binary(frame+5, count−5, mode 1). Forwarded length = advertised+1 (trailing byte unchecked here). State byte 0x20000893 <30 reset to 0 [case-frame-dispatch-closure-2026-10-08].
- Case→glasses replies (`case_send` 0x0800680C): `5A A5 FF <len8> <payload> <sum8>`, sum seeded with `len−2`, byte-at-a-time HAL transmit timeout 0xFFFF; 16-bit loop index. Ack 0x080068D0: 5 bytes `<cmd> 01 03 01 00` [case-send-candidate-20261010], [case-ack-source-candidate-20261010]. Data replies use `<cmd> 01 03 <n> <n bytes>`.
- HAL UART handle offsets: pRxBuffPtr +0x58, RxXferSize +0x5C, RxXferCount +0x5E, Mask +0x60, FifoMode +0x64, NbRxDataToProcess +0x68, ReceptionType +0x6C, RxEventType +0x70, RxISR +0x74, TxISR +0x78, hdmarx +0x80, RxState +0x8C (busy 0x22, ready 0x20), ErrorCode +0x90 (PE 1, NE 2, FE 4, ORE 8, RTO 0x20 — hardware ISR bit order differs: PE 1/FE 2/NE 4). Error mask 0x80F; ORE/RTO with RX enabled are blocking (EndRxTransfer + ErrorCallback, error retained); PE/FE/NE non-blocking (error cleared). EndRxTransfer clears CR1 0x120, CR3 0x10000001, IDLEIE if TOIDLE; keeps buffer pointer. RX-complete does **not** clear CR3.RXFTIE. Mask table 9-bit/no-parity 0x1FF … 7-bit/parity 0x3F [case-uart-error-closure-2026-10-08], [case-uart-start-closure-2026-10-08].
- Formatter 0x08009210: `%c %s %n %d %i %o %p %u %x %X`, flags/width/precision incl. `*`, lengths `h hh j l ll L t z`; 328 BL sites to 0x08009170 [case-vformat-frontier-20261010].

### 2.4 Command protocol (extends `protocols.md` §7 and `docs/hardware/g2-case.md` §4)

**Binary handler 0x08000E1C** (payload: [0] cmd, [1] reserved/direction, [2] destination, [3..] fields). Destination ≠2 → forwarding: cmd `0x3D` first ORs event 0x80 (aging-exit, logs `[AGING_NOT]: exit aging status(0x3D).`); all others via 0x08000F22→0x08001128: require len ≥5, byte1 = 0, dest ≤1, mode 0: byte3+5 == len → event **0x20**; mode≠0: u16LE(+3)+6 == len → event **0x400**; then copy frame to 0x200001B4 (event posted *before* copy). Destination 2 → local opcodes [case-legacy-default-candidate-20261010], [case-binary-forward-closure-2026-10-08], [case-local-commands-closure-2026-10-08]:

| Op | Behavior (dest 2) |
|---|---|
| 0x06 / 0x41 | ack, then legacy handoff of 1-byte cmd 0xEE (standby/ship) / 0xFF (reset) |
| 0x14 | 11-B reply `14 01 03 07 …`: readers A 0x08009FF0 (byte code 6 → 5·b−400), B 0x08009F18 (code 0xAB byte / code 14 word, mode/sign scaled), C 0x0800A01E (word code 2 → (w·5)>>4); A divided by 10; state byte 0x2000087D |
| 0x3E | len ≥5; byte4 vs aging state 0x200000F4; on change store, clear 0x200000FC; if now 0 and 0x200000F5 set: event 0x80, log `exit aging status(0x3E)`; ack |
| 0x3F | len ≥5; output enable byte4 → 0x20000891, log `%s output, reason: cmd`, if set run enable 0x0800D154 and clear 0x2000088C/8D; ack |
| 0x50 | reply `50 01 03 03 01 02 39` (inferred: firmware version 1.2.57) |
| 0x51 | 12-B reply `51 01 03 08` + 8 B from flash 0x0803F800 (byte order reversed per 8-B block) |
| 0x56 | len ≥6; byte4≠0: `Exit GLS_OTA Status`, clear 0x20000895, exit 0x080012E4 (cancel task cell 0x200000D0, two GPIO clears, clear LED 0x2000087E), ack; byte4 = 0: byte5 → GLS_OTA side state 1/2 in 0x20000895, clear 0x20000896, no ack |
| 0x5C | reply `5C 01 03 01 <!byte 0x20000880>` |
| 0x5D | len ≥6; byte4≠0 → GPIO wrapper 0x08006B80 (PA6) else 0x08006B98 (PA7), level = !byte5; ack |
| 0x5E | Set SN Even: requires len 20; apply 0x0800373C(cmd+4) writing 16 B to 0x0803F000; success → ack, failure → `5E 01 03 01 01`; hex-logs payload |
| 0x5F | 20-B reply `5F 01 03 10` + 16 B from 0x0803F000 (per-8-B reversed) |
| 0x68 | len ≥5; log-quiet byte 0x200000BF ← byte4≠0; ack |
| other | log `dst(box) cannot parse cmd: %02x` |

**Legacy handler 0x08000928** (cmd byte, length; reached from DE frames and binary 0x06/0x41). Table 0xA0..0xAF at 0x08000944 [case-command-switch-frontier-20261010], [case-legacy-default-candidate-20261010]:

| Op | Behavior |
|---|---|
| 0xA0 | log `B200 %s, %d` with "1.2.57" and counter 0x20000884 |
| 0xA1 | len ≥2: GPIO 0x08006B98 ← byte1&0x10, 0x08006B80 ← byte1&1 |
| 0xA2 | fill 8 B via 0x08002F60 (SN window) and hex-log |
| 0xA3 | status report: readers 0x08009FF0/0x08009F18/0x0800A01E + config bytes; prefixed and JSON formats (strings 0x0800D5A8/0x0800D5F8) |
| 0xA4 | log word 0x20000888 |
| 0xA5 | len ≥8: `Set SN:` hex-log, set SN child 0x08003664 |
| 0xAA / 0xAB | 0x0800D1BC→0x0800D218 / 0x08003558 |
| 0xAE | len ≥2: reset-GLS flag 0x200000C0, log `%s reset GLS` |
| 0xAF | (pre-table) len ≥2: log-quiet 0x200000BF ← byte1≠0 |
| 0xB0 | osEventFlagsSet(group, 0x100) |
| 0xD0 | len ≥2: watchdog "4005" enable via 0x08002C8E |
| 0xD1 | len ≥4: simulation flags full/empty/timeout at 0x200000C1..C3 |
| 0xD2 / 0xD3 | one-side charging flag 0x20000105 set / report |
| 0xD4 | `Set PMIC chip id to 0x08`: 0x080039E4(20, 8) |
| 0xDD | flag 0x200000BD ← byte1 (no length check) |
| 0xDF | dog-feed flag 0x200000BE |
| 0xEE | if USB present (0x2000087F) log `usb in, cannot enter shipmode.`; else `Standby, reason: cmd.` → 0x080035D4(16, resp, 1) → 0x0800292C standby chain |
| 0xFF | `Reset, reason: cmd.` → NVIC_SystemReset 0x0800502C |
| others (incl. 0xA6–A9, AC, AD) | no action |

**Glasses→case record router 0x08001E94** (`side` 0/1 per temple; payload p; cleared 0x118 B after use) [component-goal-20261013/case-wave014-record-router/after.c]:

| Cmd | Behavior / return |
|---|---|
| 0x07, 0x08 | return cmd |
| 0x13 | charging status: subtype p[3]==6 → parse BE u16 voltage p[5..6], direction p[4]&1, current sign p[8]/magnitude p[9], level p[7] (≥0x62 threshold; inferred battery %), per-side 3-sample permit history (0x200000B4), state in 0x2000089C block; return 0x13. Subtype 1 with p[4]==1 → log, return 0x13. **Any other subtype returns 0xFF** |
| 0x3E | return 0x3E if p[4] ∈ {0,4} |
| 0x46 | per-side flag ← p[4]≠0 (0x200000F6/F7); return 0x46 |
| 0x58 | OTA offer: p[3]==0x20 and p[9]==2 and p[10]>0x39 (remote 1.2.x newer than 57) → store size/sum BE words p+12/p+16, state 3; else log |
| 0x59 / 0x5B | return cmd if p[3]==1 and p[4]==0 |
| 0x5A | chunk: (p[3]&7)==1, 8-bit sum over p[3]−1 bytes vs trailer; copy to 0x2000077C |
| other | forward |

**cmd 0x13 bug (reconstruction, fixed 2026-10-13 wave 014):** earlier recovered source returned 0x13 for every 0x13 record; stock returns 0xFF unless subtype 6 or subtype 1 + confirmation 1 [component-goal-20261013/case-current-frontier-020/REPORT.md].

Event flags on group 0x200000F0: 0x01/0x200/0x1000 USB, 0x02 hall, 0x08 frame ready, 0x20/0x400 forward (mode 0/1), 0x40 RX rearm failure, 0x80 aging exit, 0x100 legacy 0xB0 [case-multiwaiter-closure-2026-10-08].

### 2.5 RTOS / event semantics

- `osEventFlagsSet` 0x0800A888: null or top-8-bit flags → 0xFFFFFFFC; IPSR thread → `xEventGroupSetBits`; ISR → `SetBitsFromISR` (deferred via timer queue, message `{−2, cb 0x0800BF8D, group, bits}`), failure 0xFFFFFFFD, success returns requested flags; nonzero yield → PendSV. `osEventFlagsClear` 0x0800A7D2 analog (ISR snapshots then queues clear) [case-event-flags-closure-2026-10-08], [case-source-candidate-round2-20261010/ROUND3-CLEAR.md].
- ISR success means queued only; bits change when timer daemon 0x0800B0FC drains (callback(arg1=group in R0, arg2=bits in R1)). Flags coalesce; final bits are not a notification count. Queue full → 0, wrapper −3 [case-deferred-consumer-closure-2026-10-08], [case-deferred-event-closure-2026-10-08].
- Queue ABI prefix: head +0, write +4, tail +8, read +12, send-wait list +16, recv-wait list +36, messages +56, length +60, item size +64, RxLock +68, TxLock +69. Event group: bits +0, list +4 (sentinel +12). Waiter item 20 B; TCB state item +4, event item +24, priority +44; wait flags clear-on-exit 0x01000000, wait-all 0x04000000; unblocked value |0x02000000 (stored |0x82000000). All satisfied waiters get the **pre-clear** snapshot; clears applied after traversal [case-event-waiters-closure-2026-10-08], [case-multiwaiter-closure-2026-10-08].
- Critical exit with nesting 0, remove-waiter null owner, resume with zero suspension, tick wrap with nonempty delayed list, disinherit wrong holder → `cpsid i` + infinite loop (configASSERT) [case-critical-source-candidate-20261010], [case-scheduler-list-candidate-20261010].
- No stock event-group delete / queue drain path was found [case-event-waiters-closure-2026-10-08].
- Logger 0x08009170: va words + context 0x200001A0 + byte callback 0x0800A381 (UART writer) → formatter 0x08009210 [case-log-wrapper-candidate-20261010].

### 2.6 Power and clocks

- STOP 0x080050E8: PWR CR1 low3 cleared, LPMS 0 (regulator 0) or 1; SCR.SLEEPDEEP; entry 1 → WFI else SEV/WFE/WFE; clear SLEEPDEEP. Policy 0x08007214 disables wake mask 0x2B, configures wake, STOP0/WFI, then 0x0800B600 (VOS 0x200 → sysclk → clock path; failure fail-stops) [case-stop-mode-2026-10-08].
- VOS 0x08005048: CR1 = (CR1 & ~0x600)|scale; for scale 0x200 poll SR2 VOSF (0x400) for `SystemCoreClock*6/10^6+1` iterations, return 3 on timeout [case-clock-poll-2026-10-08].
- Wake pins 0x080050A8: `CR4 = (CR4 & ~(arg&0x3F)) | (arg>>8); CR3 |= arg&0x3F`; disable clears CR3 bits [dependency-followup-2026-10-08].

### 2.7 Case stock quirks / latent bugs

1. Binary forward reads byte +2 before its length check; posts the event before copying into the shared 0x200001B4 buffer; ignores post errors.
2. Legacy 0xDD reads byte 1 without length check; ASCII `de` frame of 2 chars passes length 0 with stale FRAME+1; hex decoder accepts invalid digits as 0.
3. Bulk read for 0xCF frames has no clamp against the 1200-B frame buffer.
4. RX helper with count 0 wraps to 65535; `UART_Start_Receive_IT` internal helper has no guards; `case_send` loops forever for length >65535.
5. Legacy 0xAF is handled before the jump table (table slot is a no-op).
6. HAL_DMA_Abort_IT: no null check; non-busy path returns without unlock.
7. Queue TxLock overflow uncapped (V10.4.3 behavior).
8. Source-level only (not stock bugs): callback function-pointer type mismatches fixed in the reconstruction (timer callbacks take `uint32_t`; event callbacks `void(*)(void*,uint32_t)`; DMA +0x38 cb takes `uint8_t*`; sensor cancel slot p+56 returns `uint32_t`) [component-goal-20261013/case-wave061..069 reviews].

### 2.8 Case open blockers

Exact armclang/armlink release and project/scatter recipe; standby chain 0x0800292C; physical reset/standby; flash-apply success path 0x0800373C; bit-bang transaction/output-bus physical timing; runtime contents of 0x0803F000/0x0803F800; formatter source; unresolved computed callback roots/ambient stack; hardware validation of clocks/IRQ/FIFO/flash persistence [component-goal-20261013/case-current-frontier-020/REPORT.md].

---

## 3. Other payload facts found in the `dependency-*` directories

**Apollo bootloader** (148,599 B @0x410000, SHA `f89a4c46…`) [dependency-closure-2026-10-08/KNOWLEDGE.md]:
- Image header (32 B): +0 low 24 bits = total size, bit 26 = CRC/install flag; +4 CRC; +16 low byte `magicNum`; +20 run address; others uninterpreted. CRC skips 8 B (`size−8`); programming skips 32 B (`size−32`); progress % uses size incl. header.
- `osDelay` 0x416378 (−6 if rejected, 0 ticks no yield; `UINT32_MAX` is a finite delay); task-return 0x41B390 (critical word 0x200004C4); malloc-failure 0x41B5F6 prints and spins; stack overflow 0x41B600 BKPT 0; exit 0x41B298 semihosting op 0x18 reason 0x20026; DFU terminal 0x42E1DA loops `osDelay(UINT32_MAX)` (no reset); EasyLogger reports library version 2.2.99; elog time buffer 0x20026F18, tick 0x20027148; IAR fill 0x41560C (writes backward), aligned copy 0x4156AC (returns out+(n&~1)). Resident ROM entries 0x40, 0x48, 0x0200FF20 (nv_program_main2 0x0200FF21) are outside OTA.

**Apollo main** (raw SHA `19044a72…`, base 0x438000):
- Audio dispatcher table **0x20003FBC** (literal 0x53CEB4, dispatcher 0x53C5AC; older 0x20073FBC wrong); TLSF `malloc(680)` min block 696, `malloc(8)` 24 [dependency-followup-audio-lifecycle-2026-10-08/INDEX.md], [dependency-followup-audio-providers-2026-10-08/INDEX.md].
- IOM I2C config 0x55CA94–0x55CC10 writes MI2CCFG (0x400502C0 + module·0x1000) = 0x0003F070/0x0003F270/0x00023040 for 100k/400k/1M — **AmbiqSuite 5.1 values** (5.2 sets STRDIS bit 24) [dependency-gap-audit-fresh-2026-10-09T192823Z/next-sdk-audit/IOM-CMSIS-FINAL-INDEPENDENT-REVIEW.md].
- SPI: IOM service 0x55C558 has no FDNB dispatch (pre-FDNB or TX-DMA lineage); blocking full-duplex 0x55CF40, validator 0x55C1E0; transaction pause/status at +36/+40 [dependency-gap-audit-fresh-2026-10-09T192823Z/next-sdk-audit/QUEUE-FINAL-INDEPENDENT-REVIEW.md, FDNB-LINEAGE-INDEPENDENT-REVIEW.md].
- LZ4 (1.9.4–1.10.0 lineage): read_variable_length 0x54EE90, LZ4_decompress_generic 0x54EF08 (1072 B), LZ4_decompress_safe 0x54F338; caller returns max(ret,0); tolerates zero-offset matches; empty input −1 [dependency-gap-audit-fresh-2026-10-09T192823Z/next-lz4-triage/LZ4-FINAL-INDEPENDENT-REVIEW.md].
- Nema `nema_cl_bind_sectored_circular` 0x5143D4 (230 B) ≠ SDK 5.2 IAR 9.70.1 archive (stock has an extra block clearing bit 0x20 of obj+24) [dependency-gap-audit-fresh-2026-10-09T192823Z/next-lz4-triage/NEMA-FINAL-INDEPENDENT-REVIEW.md].
- HCI `LE Read Supported States` emitter 0x52B37C (opcode 0x201C); reset-sequence consumer 0x569B56–0x569D26 copies 8 B from event+6 to 0x200714D8 without status/length check [dependency-gap-audit-fresh-2026-10-09T192823Z/PIGWEED-REVIEW.md].
- Third-party path strings in main: LVGL, Cordio, EasyLogger, littlefs, TLSF, RingBuffer, TinyFrame only; no CMSIS-DSP hits [dependency-gap-audit-fresh-2026-10-09T192823Z].

**GX8002 codec**: nine NationalChip DSP assembly sections are byte-exact (1,606 B in BINH B stage 2: split_rfft 0x47914, split_rifft 0x479A8, shift 0x47A00, abs_max 0x47A74, copy 0x47AC0, fill 0x47AEC, radix4 butterfly 0x47D3C / inverse 0x47F50, bitreversal_16 0x48164); DWARF: GNU C11 6.3.0, ck804ef, hard-float, -O2; C-SKY Tools V3.10.15 (Minilibc abiv2 B20190929) compiles the C variants but none match (SDK Makefile selects asm kernels) [dependency-gap-audit-fresh-2026-10-09T192823Z/DSP-INDEPENDENT-REVIEW.md, DSP-C-COMPILER-INDEPENDENT-REVIEW.md, DSP-KERNEL-LINEAGE-CORRECTION.md].

Payload sizes used for coverage (with wrappers): main 3,523,396; bootloader 148,599; touch 34,464; case 55,784; codec 326,092; EM9305 211,948 [dependency-gap-audit-fresh-2026-10-09T192823Z/COMPONENT-COVERAGE-REFRESH.md].
