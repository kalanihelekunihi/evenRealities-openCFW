# G2 untagged upstream dependencies and easy wins

Scan date 2026-10-29. Scope: what the stock G2 payloads contain that a pinned
or locally available upstream already provides, but that `g2/src` still
re-implements by hand or lifts from assembly. Each row says how strong the
attribution is. Name matches are leads; only rows marked *verified* have been
compared against stock behaviour.

Method: every named row of `g2/symbols/*.tsv` was matched against an index of
function definitions in `third-party/upstream`, `third-party/reference`,
`third-party/local-vendor/sources` and `vendor-cache/g2/source-discovery-acquisitions`,
then classified per payload as built from upstream, hand-written under the
same name, hand-written under a stock-address name, or not found in the build.
Unnamed (`FUN_`) rows are not covered by this method.

## State of the tree at the scan

| Payload | Units | `.S` units | C units containing `__asm` (occurrences; includes symbol labels) | Notes |
| --- | ---: | ---: | --- | --- |
| apollo-main | 2,870 | 1 | 291 (2,093) | 8,453 / 8,844 stock functions strongly attributed (wave 25); 17 residual |
| apollo-bootloader | 381 | 33 | 172 (260) | links with 0 unresolved; built **no** upstream HAL file before this scan |
| case | 408 | 0 | 106 (181) | |
| touch | 105 | 1 | 11 (20) | PDL/CapSense mostly from upstream |
| codec-a / codec-b | 340 / 331 | 6 / 1 | 30 / 28 | |
| em9305 | 778 | 0 | 418 (765) | 611 files under `qpc-scheduler/` are lowered ARC assembly in `__asm__` blocks (73,771 lines, about 18,100 instruction lines) |

## Findings, ranked for hardware support

### 1. Bootloader: AmbiqSuite SDK 5.0.0/5.1.0 HAL (SYSPLL, queue, CMDQ, CLKGEN, MSPI, UART, status polls done)

The Even bootloader (`0x410000`) links the AmbiqSuite HAL, but `g2/src/apollo-bootloader`
re-implemented it by hand under invented names; only 3 bootloader symbol rows
were tagged as Ambiq code. The HAL release is **SDK 5.0.0 RTM**
(`release_sdk5p0p0-5f68a8286b`, ambiqhal_ambiq `392042e`), not the 5.1.0 tree
apollo-main pins: stock `am_hal_mspi_device_configure` takes the 5.0.0
`bNewDDR` branch, stock `am_hal_mspi_control` uses the 5.0.0 request enum,
and the image lacks the aperture table that the post-RTM fix `9df2220` added.
5.0.0 is now pinned as `third-party/upstream/ambiqhal-apollo510-sdk5.0.0`.

The snapshot is not a single public release. `am_hal_uart.c` matches 5.1.0,
not 5.0.0 RTM: stock keeps the TX/RX queues at state `+0x34`/`+0x4c` and the
active write at `+0xa0`, the 5.1.0 order (RTM has them at `+0xac`/`+0xc4`
and `+0x70`), with the same 0x11c size and `bDMABusy` at `+0x11b`. MSPI is
RTM, UART is ≥ 5.1.0, and the code-identical modules fit either. Pick the
revision per file by differential test, not by release.

- Map: [`coverage-2.2.6.10/bootloader-ambiq-hal-map.tsv`](coverage-2.2.6.10/bootloader-ambiq-hal-map.tsv),
  113 functions, 103 Verified.
- **Built from upstream:** 5.0.0 `am_hal_interrupt.c`, `am_hal_queue.c`,
  `am_hal_mspi.c` (verbatim, including control) and `am_hal_pwrctrl.c`
  (verbatim, all 25 stock functions 0x41b8f8..0x41cae8), generated 5.0.0 copies of
  `am_hal_syspll.c`, `am_hal_cmdq.c`, `am_hal_clkgen.c` and `am_hal_utils.c`
  (status polls only) that compile out what stock does not link, and the
  5.1.0 `am_hal_uart.c` (verbatim). `g_MSPIState` (0x2001caa0), `gAmHalCmdq`
  (0x200262f0), `g_SysPLLState` (0x20027010) and the PWRCTRL state (trim
  version, memory config, MCU/GPU/ROM modes, INFO1 cache, trim snapshots) are
  pinned at their stock addresses. About 70 hand files went, including the
  seven-file hand split of "stock-variant" `am_hal_mspi_control` and the
  register-carry startup root that stood in for `am_hal_pwrctrl_low_power_init`.
- Float ABI: the stock HAL is hard-float (`am_hal_pwrctrl_temp_update` takes
  its temperature in `s0`) while the bootloader builds softfp. A generated
  `am_hal_pwrctrl.h` gives that one function `pcs("aapcs-vfp")`.
- Bindings: the hand clock manager, SPOT dispatcher wrappers, INFO1 read,
  debug trace release and clock-mux reset also carry their upstream names
  (`am_hal_clkmgr_clock_*`, `am_hal_spotmgr_*`, `am_hal_info1_read`,
  `am_hal_debug_trace_disable`, `am_hal_sysctrl_clkmuxrst_low_power_init`).
- Verification: stock bytes against the linked image, 0 mismatches in queue
  (500), CMDQ (800), CLKGEN (4,000) and MSPI (1,500 operation sequences over all
  13 public functions), UART (400), status polls (3,000), PWRCTRL (1,500),
  SYSPLL (3,036, re-run on the final image); mutants caught. The emulator harness once skipped
  instructions after an IT block that wrote MMIO; it now maps MMIO with
  callbacks, and every module was re-run with the fix
  ([`g2/evidence/bootloader-hal-upstream-review.json`](../../evidence/bootloader-hal-upstream-review.json),
  [`bootloader-syspll-upstream-review.json`](../../evidence/bootloader-syspll-upstream-review.json)).
- Remaining hand code that is this SDK: the clock providers under
  `clock-manager/` and `startup_clock_config.c` (`am_hal_clkmgr.c`),
  `am_hal_sysctrl.c` (sleep, clock-mux reset), `am_hal_debug.c` (stock
  `am_hal_debug_disable` is 0x423dd0 with its counters at 0x200271c2/3, and
  0x422468 is `am_hal_debug_power`, mapped as debug_disable in the table), and
  `am_hal_delay_us` (a ROM-loop variant of the SDK function, kept by design).

**SPOTMGR is an unpublished revision.** The stock SPOTMGR is dispatcher
0x41cc04..0x41d1c0, PCM2.2 0x427e0c..0x42ac54, PCM2.1 ..0x42c034, PCM2.0
0x42cdf8..0x42d890 and PCM0.7 0x42f1c8..0x42f700, with its RAM laid out per
object in file-name order (0x2002708c..0x200270c8, 0x200271a9..0x200271be,
initialized cells 0x20000144..0x200001c8 and 0x20000553..0x2000055a). It is
none of the public texts:
- the init computes six trim flags and powers the ACRG for PCM1.0/1.1 too,
  which is AmbiqSuite patch `66185cb` ("patches for apollo510 sdk5.0.0 known
  defects", between 5.0.0 and 5.1.0 in `ambiqhal_ambiq`);
- PCM2.0 records the tempco range unconditionally, guards its
  `g_bFrcBuckAct` writes with `g_bIsPCM2p0`, and has the PCM2.0
  `spotmgr_buck_deepsleep_state_determine`, all 5.1.0 hunks, but no
  `STIM_INIT_STATE` (5.1.0 enum);
- PCM2.2's `SWITCH_TO_HP` forces HFRC2 on and waits for it, as in 5.1.0, yet
  the transition sequences stay `void` and keep the 5.0.0 VDDF double boost.

**The bootloader now builds SPOTMGR from upstream (2026-10-30).** The source is
5.0.0 + `66185cb`, with PCM2.0's three 5.1.0 hunks and two more 5.1.0 hunks
that stock also has. First, `SWITCH_TO_HP` forces HFRC2 on and waits for it
before requesting HP mode, keeping the void 5.0.0 sequences as stock does.
Second, PCM2.1's deep-sleep VDDCAOR/VDDCPU override no longer depends on
TIMER A running. Every global is pinned, and
the PCM2.2 transition table is copied from its load image at startup.

The earlier "the other differences" in the direct sequence calls were a
harness error: it compared `r0` after the void sequences. Once that was fixed,
only sequences 5, 11 and 13 (the three that call `SWITCH_TO_HP`) differed, and
the HFRC2 hunk closes them. All 27 sequences match, and so do 1,500 random
sequences, both in the linked image and as a standalone overlay.

The project goal is a working firmware rather than stock identity (2026-10-30).
So where stock and a newer SDK text differ, the newer text is preferred
unless it changes how the hardware is driven. This SPOTMGR is the older
upstream text plus the newer hardware fixes stock also carries. The 78 hand
files of the old reconstruction are gone (`build/snap-stage2/stage2_removed.json`;
evidence in `g2/evidence/bootloader-hal-upstream-review.json`, `spotmgr`).

**Apollo-main MSPI is SDK 5.0.0 RTM too (2026-10-30).** Its 27 shared MSPI
functions are instruction-for-instruction the bootloader's 5.0.0 RTM text
(branch targets and literal pools aside), plus `build_dma_cmdlist`,
`mspi_cq_add_transaction` and `am_hal_mspi_nonblocking_transfer`, which the
bootloader does not link. The "post-RTM aperture table" seen in the main image
is not used by this code. apollo-main now builds the 5.0.0 file unchanged; the
hand `am_hal_mspi_control` split (`drivers/flash/mspi/`) and the generated 5.1.0
copy are gone, and a standalone link matched stock on 1,500 sequences
(`g2/evidence/main-hal-upstream-review.json`).

**Apollo-main PWRCTRL is now SDK 5.0.0 (2026-10-30).** The block at
0x47ef18..0x4800e4 is the bootloader's 5.0.0 `am_hal_pwrctrl.c` in source
order with equal function sizes and the same callee at every call site.
apollo-main now builds that file unchanged (profile `g2-apollo-main-108`),
and the hand variants (`hal/x-03-pwrctrl/`, `hal/final-r1-pwrctrl/`,
`runtime/info-memory/memory.c`, `ble/ble-flash/display_ble_flash_mode.c`,
`drivers/power/power-vendor/`) and the 27 replacements in the generated
5.1.0 copy are gone. A standalone link of the object against the stock OTA
image matched stock on 1,500 random sequences
(`g2/evidence/main-hal-upstream-review.json`).

apollo-main SPOTMGR now uses the same upstream source (2026-10-30). Stock
main's SPOTMGR is the same text as the bootloader's: SDK 5.0.0, patch
`66185cb` and the same five 5.1.0 hunks. apollo-main now builds the
bootloader's generated `{gen}/ambiqhal-apollo510-boot/am_hal_spotmgr*.c`
(profile `g2-apollo-main-108`), and the hand files under `hal/p-06-spotmgr/`,
`hal/p-14-spotmgr/`, `audio/pcm21/` and early-pcm are retired. The
alternatives were scored against stock over 300 cases: plain `66185cb` gave
50 mismatches, and 5.1.0, `48793d7` and 5.2.0 gave 237 each. Those three
change init register writes, simobuck waits and INFO1 reads, so they were
rejected. Test: `build/dedup2/spot/diff_main_spotmgr.py`, run inside the
stock image, 1,500 cases, 0 mismatches.

### 2. EM9305: Packetcraft Link Layer from open Cordio r20.05c

Of 1,835 EM9305 stock rows (201,992 B), 1,182 named functions (132,240 B)
exist by name in the open Packetcraft Cordio controller, wsf and platform
sources (`third-party/upstream/cordio`, r20.05c, Apache-2.0). The symbol
table's module column names the EM SDK archives they came from
(`lib_emb_peripheral_advext.a:lctr_main_adv_slave_ae.c.obj` and so on). 251
further LL-style names (23,368 B: PAwR, subrating, ECU, `Pal*`) are newer than
r20.05c and have no open source.

About 810 of those functions exist in `g2/src` only under stock-address
names, mostly as lowered assembly that is converted to C one function at a
time from the assembly. The Apache-2.0 r20.05c `.c` bodies are a better
starting text for each lift; the QEMU ARC harness then decides equivalence, as
it does now. `g2/src/em9305` does not use them today.

Licence boundary: `third-party/local-vendor/sources/em9305-v4.6/.../packetcraft`
holds 438 headers for the newer LL (every `lctr_int*.h`, `LL_VER_NUM 31714`),
but they are marked "Packetcraft, Inc. confidential and proprietary" and "EM
Microelectronic, Inc. confidential and proprietary". They must not be copied
into `g2/src` or the build. Whether they may be consulted locally to confirm
structure offsets falls under the open `blocked-map.tsv` decision for the
EM9305 SDK. The `.a` archives have the same status. Where r20.05c and stock
disagree, derive layouts from stock field accesses (for example
`lctrSlvBigBeginOp`, already lifted).

### 3. Codec (GX8002): NationalChip lvp_kws utilities

30 codec functions (1,996 B) are hand-written under stock-address names but
exist in `third-party/upstream/nationalchip-lvp-kws`, and 10 more (680 B) are
absent by name: `tfp_format`, `ui2a`, `putf`, `LvpQueue*`, `LvpKwsDone`,
`LvpAudioInDone`, `wait_bus_ready`, `trap_c`. The `drivers_lib/*.o` objects
named in `codec.tsv` (audio_in v2.0, dw_uart, gx_dcache, flash_spi, clock v2.0)
match `vendor-cache/.../nationalchip-lvp-aiot/lib/libdriver_release_v1.0.5.a`
and its `include/driver/*.h`. That archive is a binary, so use it as a layout
and API reference only.

### 4. Apollo-main: Cordio host remainder

About 390 Cordio host functions (about 46 KB) are still hand-written under
`ble/` (`hci_evt.c` 6.7 KB, `smp_*_act.c`, `hci_core.c`, `l2c_*.c`,
`dm_adv_leg.c`, `attc_main.c`, `atts_csf.c`, `wsf_*`). Thirty other Cordio
files already build from AmbiqSuite R3.2.0 or r20.05c through `generated`
copies. Extending that pattern is mechanical, though it is BLE protocol code
rather than hardware support. The HCI transport (`hci_drv_apollo3.c` derived,
SPI to the EM9305) is the hardware-facing part.

### 5. Smaller leads

- Touch: `Cy_SCB_{Read,Write}Array{,NoCheck}` and
  `Cy_SCB_WriteDefaultArray{,NoCheck}` (6 functions, 254 B) are absent from the
  build, and the upstream PDL is pinned. Check whether anything references them
  before adding them.
- Case: stock names show FreeRTOS kernel (`vTaskSwitchContext`,
  `xPortPendSVHandler`, `prvTimerTask`, `pvPortMalloc`) and STM32G0 HAL
  (`HAL_FLASH_Unlock`, `HAL_PWR_Enter*`) functions that the build has under
  neither name nor address. The `freertos-kernel` and `stm32g0xx-hal-driver`
  submodules are pinned but not compiled for the case.
- Bootloader: `elog_output` (1 KB) is hand-written by address; EasyLogger is
  pinned and already built for apollo-main.
- Empty submodules worth initialising before more Ambiq work:
  `third-party/upstream/ambiqhal-nema` (NemaGFX; apollo-main has 26
  hand-written `nema_*` units), `third-party/reference/ambiq-neuralspot` and
  `ambiq-nsx-sdk` (AmbiqSuite R4/R5 `am_devices_*` and EM9305 HCI driver
  candidates). These are leads, not established sources.

## Hazard found during the scan

The bootloader linker script places `.bss` at `0x20000000`. Its only object,
`opencfw_boot_iom_contexts` (0x4540 B), overlaps 89 distinct hard-coded stock
RAM addresses used elsewhere in `g2/src/apollo-bootloader`, for example
`0x20000080` and `0x2000008c` (reference clock words read by
`startup_clock_config.c`). Any write to an IOM context, and `.bss` clearing
if startup performs it, lands on those cells. The fix
belongs in the link layout (place the contexts where stock has them, or
reserve the stock-cell window), and it needs checking against the stock RAM
map first.

Resolved 2026-10-29: the link script pins the IOM contexts at stock
0x2001455c and `g_SysPLLState` at 0x20027010, and keeps generic `.data`/`.bss`
out of the stock RAM window (see `C-RECONSTRUCTION-PROGRESS.md`).
