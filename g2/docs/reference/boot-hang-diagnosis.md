# openCFW apollo-main boot hang — consolidated diagnosis (2026-11-02)

**2026-11-11 update:** The source-linked Apollo startup now copies the
source-defined 24-byte overlay to ITCM `0x40..0x58`; the linked bytes match
the recovered locked overlay. The older “ITCM overlay missing” entries below
describe the 2026-11-02 build. The current source-only image has not been
booted on hardware. See
[`apollo-itcm-overlay-startup-20261111.json`](../../evidence/apollo-itcm-overlay-startup-20261111.json).

Supersedes and extends `sim-hardware-gap.md`. It folds in a full boot-path
blocking-wait audit, the hybrid-build mechanism, and a **hardware-free
confirmation method** (a Unicorn differential boot trace against the stock
image, feasibility proven — see §5). It does not claim to have *found* the
hang: without a recoverable hardware loop or a faithful sim we cannot yet prove
which candidate is the cause. It replaces "flash and pray" with a confirmable
pipeline and a defense-in-depth hardening list.

## 0. In-sim results (2026-11-02) — Renode confirmation workflow is live

Built Renode from source (`~/Repo/g2-firmware-emulator`, Cortex-M55; Unicorn is
ruled out — it cannot run M55 apollo-main: our GNU build emits CSEL and stock
uses an IAR LZ77 self-modifying decompressor, both of which Unicorn's core
rejects). The emulator now runs any build and compares against baselines. What
the runs established:

1. **Baseline:** the project's patched-*stock* image (`g2_2.2.9.22_cfw.bin`)
   boots to BLE in the sim (EM9305 HCI advertising + display frames). NOTE: this
   is a lightly-patched stock binary, **not** the GNU C reconstruction — the
   earlier "the sim boots the reconstruction fine" belief conflated the two.
2. **A real, now-fixed bug the method caught:** an older reconstruction build
   (w18) hangs in the sim at `main`'s post-scheduler `for(;;)` (0x59fad0) —
   `thread_manager_kernel_start` → `osKernelStart`/`vTaskStartScheduler`
   *returns*. Cause: the w18 vector table mis-bound **SVC/PendSV/SysTick to
   `g2c_unhandled_isr`** (an infinite-loop trap) instead of the real FreeRTOS
   handlers (which were compiled but unreferenced). Fatal to the RTOS. Fixed by
   "Wave 21" (`runtime/g2c-gnu/g2c_vectors.c`): current builds (w28i, sim68)
   bind `SVC_Handler`/`PendSV_Handler`/`SysTick_Handler` correctly.
3. **The flashed build was already fixed:** the actually-flashed
   `opencfw-main-adcfix-1101.evenota` has correct vectors (SVC/PendSV/SysTick →
   real 0x5c1xxx handlers). So the vector bug is **not** what bricked the device.
4. **The current build boots in the sim:** w28i reaches BLE advertising
   (HCI `010A2001 01`, device name "Even G2_32_R…"), same as the patched
   baseline. So the sim does **not** reproduce the hardware hang for the current
   reconstruction.

**Conclusion:** the current reconstruction has no gross boot/scheduler defect
the (lenient) sim exposes — the hang genuinely lives in the **sim-faked
hardware layer**. This validates the leads below (the sim fakes STIMER clocking,
ADC analog power, and NOR content) and means the next step is to make the sim
**strict** so it reproduces the hang. Harness/runbook: `build/boot-trace/STATUS.md`.

## 0b. Full sim differential vs stock 2.2.6.10 — nothing diverges (2026-11-02, later)

Oracle: the real same-version stock app (`g2/blobs/official/g2-2.2.6.10/
ota_s200_firmware_ota.bin` has a 0x20-byte preamble; app = file[0x20:], load
0x438000, reset 0x5E4233 = `reset_handler_5e4232`). It boots to BLE in the sim.
Method: `sysbus LogAllPeripheralsAccess`, 4 s, normalised, per-peripheral
first-divergence diff with RAM pointers masked (`build/boot-trace/periph_diff.py`).

- **Writes identical** for pwrctrl, clockgen, mspi1 (NOR controller), adc, uart0/2/3,
  iom2, rtc, mram; gpio identical to 99 %. The only divergences are benign:
  RAM-layout pointers; uninitialised padding in IOM TX words (FIFOPUSH 0x10C upper
  bytes — CMD identical, so not transmitted); one cache-op and one NVIC reorder;
  iom6 skips a redundant DCX=0 write; TIMER14 RTC clock-edge sync done 1× vs 173×
  (an RTC-read-path difference, not a hang); wdt/uart1 tail counts.
- **Reads:** ADC FIFO 638k vs 81 and IOM STATUS ×31/×48 are a sim poll-fast-forward
  artifact — outcomes identical (`hw_version=3`, 595 mV, 384 scans, 3 results);
  stock's ADC wait is the same tight `ubfx #20,#8 / beq` spin on 0x40038038. Our
  IOM waits are bounded `am_hal_delay_us_status_check((STATUS&6)==4)`.
- **Excluded as reconstruction defects (each tested):** STIMER (both CLKSEL=3
  XTAL_32KHZ, clock programming identical, model already gates on CLKSEL);
  ITCM 0x40 (both boot with the overlay absent); ADC (identical outcome);
  MSPLIM (both 0x2007d000; tlib doesn't enforce; watchpoints below the limit never
  fire); watchdog (identical cadence; model can reset); hw_version/board_type (only
  logged; uLED type comes from display mode); OTP consumers (bounded);
  cstartup/handoff (program-start prologues instruction-equivalent, neither touches
  PRIMASK, and the bricked temples run the stock bootloader anyway);
  **flashed builds** (ramfix and adcfix both boot to BLE in the sim with correct
  vectors — the w18 vector bug is not the brick).
- **Lead C (littlefs on real NOR) — largely excluded:** using the emulator's real
  MX25 model, stock 2.2.6.10 formats littlefs at NOR 0x1400000; **ours boots to BLE
  on that stock-written array**, and ours formats a byte-compatible layout (disk
  version 0x20001, 4096×3008, same partitions). Our mount-failure path formats and
  continues (no hang). Residual: an internal `LFS_ASSERT`/FlashDB assert on months of
  real content — low probability, untestable without a real dump.

**Reframed conclusion.** At every interface the sim models, ours ≡ stock through
BLE advertising, and every audit lead is excluded or low-probability. The hang
therefore lives in how ours reacts to **real device responses or timing the sim's
fixtures never produce** — branches both images skip in the sim (the fixtures
return identical canned values to both; real hardware returns real values to
both; only a reconstruction bug in the real-value branch distinguishes them).
Note the symptom: `box_uart_init` runs in the device-manager thread's late init,
but *servicing* pogo requests needs that thread (or a lock it holds) to keep
running — so a device-init stall in that thread after `box_uart_init` also yields
"no pogo frame". Next: (1) static audit of device-response-gated loops/retries;
(2) perturb the sim fixtures (EM9305 version/caps, IMU WHO_AM_I, PMIC status,
panel IDs) and see whether ours hangs where stock copes.

### 0b-ii. Fixture perturbations and the pogo path (2026-11-02, later still)

Every sim-unexercised branch I could reach by perturbing fixtures behaves
identically in ours and stock (metric: 56 HCI packets = BLE advertising, no
errors): EM9305 controller **version mismatch**; **low battery** (3450 mV);
**in-case at boot** (PMIC `SetPowerState true 9` charging and `true 3` complete —
the model defaults to no VBUS, so this branch had never run); **touch-event
burst** and **IMU data-ready IRQ burst** (12 injected events each); and the
**pogo product-test request itself** injected on UART2 (`BOX_UART=2`) — both
images answer `24 00 01 00 A7` byte-identically with
`5A A5 FF 09 24 01 03 05 02 02 06 0A 03 4B`. Boot timeline is identical (all 56
HCI packets within the first virtual second). Recipes in `build/boot-trace/STATUS.md`.

One steady-state tell: after ~6 s virtual, ours costs ~5× more host time per
virtual second than stock, i.e. it executes far more instructions in steady
state — it busy-polls where stock sleeps. Being profiled (t=6–7 s access counts).

### 0b-iii. End of the sim campaign — final exclusions (2026-11-02)

A device-response audit (EM9305 bring-up, PMIC/fuel-gauge, touch/codec DFU,
display, device_mgr topology) plus targeted sim experiments closed every
remaining candidate. Each line below was *tested*, not assumed:

- **ITCM 0x40's real role:** stock `am_hal_delay_us` (0x4807a0) ends in `bl #0x40`
  — the 24-byte overlay is the µs busy-loop. Ours tail-calls an equivalent
  `br_util_delay_cycles` (identical `subs/bne/bx` loop, identical µs→iteration
  math: ×32, ×250/96 in HP mode, overhead 15/24) from MRAM. On silicon that is
  equal-or-marginally-longer, never shorter — not a hang.
- **Non-stock early recovery arm** (`self_recovery.c`, OTAPOINTER=0xAFD1363A): the
  magic is absent from ramfix, adcfix, w28i and stock binaries; it is an untracked
  working-tree experiment added after the flashes. Not the brick. **Do not ship it
  as-is**: it arms unconditionally and only disarms after a pogo reply, so an
  out-of-case temple would never disarm.
- **Ship mode on zero telemetry:** fuel gauge is the stock `nrf_fuel_gauge` blob,
  the gate is stock logic, the PMIC model implements ship mode; both images pass.
- **EM9305:** mode-word decode identical (`((b1&0x1f)<<1)|(b0>>7)`), revision
  compare identical, `acquire` recovers on `check==0` in stock too, SPI-bus
  STATUS reads identical (999/999). Version-mismatch and in-case/low-battery
  perturbations identical.
- **Sleep policy:** per-second deep/normal `am_hal_sysctrl_sleep` profile identical;
  `am_freertos_sleep` is a stock blob.
- **MRAM programming:** the only boot-time MRAM write is the OTA-flag clear
  (4×0xFFFFFFFF at 0x7FE000), executed by the ROM `nv_program_main2` at
  0x0200FF21 — stock reaches the same address through its const helper table
  (0x75d630 slot 1); the emulator HLEs that ROM (`G2Apollo510_BootRom`). Identical.
- **Install path:** app preamble = `{0x04000000|size, crc32(payload[8:]), 0, 0,
  0xCB, 0x438000, 0, 0}`; our packer reproduces it (all four images verified);
  the Even bootloader's `opencfw_boot_verify` CRCs exactly `payload[8:]`, and
  `opencfw_boot_program` erases/programs `size−32` bytes with no cap and per-chunk
  verify. Our image is larger (3,827,816 B, ends 0x7DE868 vs stock 0x794324) but
  no bootloader/app MRAM metadata lives in that band (only the flag page at
  0x7FE000). Install equivalent.
- **Poll-count gaps** (I2C STATUS ×31/×48, ADC FIFO ×7880) are an emulator
  time-accounting effect: no stock-PC fast-forward table exists (only the STIMER
  has `PollFastForward`), and *every other register's* read count is identical.
  Not firmware.

**Where this leaves the brick.** Nothing the simulator can model, perturb, or
inject distinguishes the reconstruction from stock. The residuals that cannot be
tested here are: (i) the EM9305 firmware-update branch, which is live on hardware
(the NOR holds `firmware/ble_em9305.bin` and the real controller trim/revision
words) but never ran in any sim because the sim NOR lacks the file; (ii) months of
real littlefs/FlashDB content (an internal assert); (iii) silicon-level timing of
the GPIO15 pulse trains and I2C settle under MRAM-executed delays. Resolving any of
these needs an observation from a bricked temple (debug UART or SWD boot log), not
more simulation.

## 1. Confirmed facts

- A clean 6/6 BLE install of openCFW main (RAM Fix 43 build, and separately the
  stock-equivalent builds) **hangs early on real hardware**: no BLE advertising,
  no case product-test frame. Both dev temples bricked identically. RAM Fix 43
  did not help, which rules out the uninitialised-RAM defects as the cause.
- The same builds **boot to the BLE stack in the Renode simulator**. So the
  hang is *earlier than anything the sim exercises faithfully* — in early
  bring-up, where the sim fakes (preloaded ITCM 0x40 overlay, blank NOR, lenient
  clocks/ADC/MRAM; see §4).
- Boot chain (traced in source):
  `runtime/C3-startup/iar_cmain.c` (`__cmain` → `__iar_data_init3`) → region
  walk → `system/a-67-main-config/main_config.c` `main_5ce01e` →
  `auto_init_table_run_5bf0bc` (23-entry **pre-scheduler** init table in
  `system/S2-system-rtos-runtime-data/init_table_data.c`) → `vTaskStartScheduler`
  → tasks (storage/littlefs, display/uLED, BLE).
- `board_init_5093ac` runs at init priority 1 and calls, in order:
  `board_gpio_table_init` → `board_config_empty_hook` →
  **`board_hw_version_detect_509134`** → `uart_channels_init` → `HAL_I2CInit` →
  `hal_uart_power_on`.
- A watchdog is started pre-scheduler (`main_config.c` `watchdog_start_4b29d8`
  in `board_init_5cdd14`). A hang before the WDT task first kicks becomes a
  **reset loop**, consistent with the "case resets temple at ~180 s" symptom —
  i.e. the observed state is equally consistent with a static hang *or* an
  early crash/abort that resets.

## 2. The hybrid-build insight (this reframes the ADC lead)

apollo-main is a **hybrid build**: unreconstructed functions are called at their
original stock ROM addresses in the retained image. The ADC HAL
(`am_hal_adc_*`, mapped in `g2/src/sources.json` to the upstream names) is **not
reconstructed and not vendored** — it is stock bytes. The hw-id probe's
configuration in `board_config.c` is also copied verbatim from stock ROM records
(e.g. the IRTT record from ROM 0x78d104, clock/slot fields matching the stock
layout).

Therefore: **the ADC register-write sequence in `board_hw_version_detect` is
byte-for-byte stock behaviour.** The stock firmware boots on this silicon with
exactly those writes. So the ADC FIFO poll can only hang on openCFW-but-not-stock
if the probe is *reached in a different machine state* — i.e. some reconstructed
code that runs **before** it (reconstructed cstartup/region-init, or an earlier
init-table entry) leaves a clock, power domain, or pin in a state stock never
leaves it in. If no such divergence exists, **the ADC is not the hang** and Fix
51 is bounding a non-cause (harmless, but not the fix).

This demotes "ADC bring-up bug" from root cause to *conditional on an earlier
divergence*, and tells us where to look: the reconstructed pre-probe path.

## 3. Ranked hang candidates

Ranked by likelihood of hanging on real silicon while passing the lenient sim.
"Confirmable" = can be settled by the §5 differential trace without hardware.

| # | Locus | Type | Phase | Status |
|---|-------|------|-------|--------|
| 1 | STIMER compare-delta wait — `hal/a-12-stimer/am_hal_stimer_a12.c:120` | **unbounded** HW poll | scheduler start | **not fixed** |
| 2 | littlefs `LFS_ASSERT` → non-returning `__aeabi_assert` — `storage/u-02-littlefs-config/g2_lfs_defines.h:53` | non-returning abort | post-scheduler mount | not fixed (Lead C) |
| 3 | uLED MSPI ISR poll — `drivers/display/display-uled/display_driver_uled_mspi_interrupt_service.c:70` | **unbounded** HW poll | display init, pre-BLE | not fixed |
| 4 | ADC FIFO poll — `app/a-41-board-config/board_config.c:193` | HW poll | pre-scheduler (prio 1) | **bounded by Fix 51**; see §2 |
| 5 | `wait_hp_mode` MCU-perf poll — `hal/a-03-sysctrl/am_hal_sysctrl_sleep_variant.c:132,263` | unbounded HW poll | post-scheduler idle/wake | not fixed (MEDIUM) |
| 6 | uLED MSPI DMA ring walk — `.../display_driver_uled_mspi_dma_queue_snapshot_release.c:33` | RAM-state loop | post-scheduler | not fixed (MEDIUM) |
| 7 | ITCM 0x40 overlay missing — `runtime/g2c-gnu/g2c_gnu_init.c` (4 rows vs stock 5) | reconstruction gap | cstartup | real gap, **no demonstrated boot caller** (Lead A) |

### Mechanisms and the sim leniency that hides each

- **#1 STIMER** (`while (now == last || now == last+1) now = counter_get();`): spins
  until the STIMER free-running counter advances ≥2 ticks. No bound, no timeout.
  Called from the FreeRTOS tickless port (`rtos/a-04-freertos-port/port_stimer_tickless.c`)
  at `vPortSetupTimerInterrupt` (scheduler start) and every tickless idle. If the
  STIMER clock source (HFRC/XTAL/LFRC) is not actually running on silicon, `now`
  never changes → hard hang **right at scheduler start, before any task** — which
  matches "sim reaches BLE, hardware shows nothing." The sim's STIMER model
  advances, so it passes. This is the single most plausible *unbounded* locus the
  earlier doc missed.
- **#2 littlefs assert** (Lead C): `__aeabi_assert` (stock, no in-tree body) does
  not return. The sim's NOR is blank → clean mount. Real NOR holds months of
  stock littlefs/FlashDB with a version skew (2.10.1 / FlashDB 2.0.0 vs stock
  2.1.1); any mount-time invariant failure is an infinite abort. Mount is in the
  storage thread — post-scheduler but before BLE.
- **#3 uLED MSPI ISR** (`while ((*reg(0x104) & 1) != 0) {}`): stock
  `am_hal_mspi_interrupt_service` spins on MSPI reg 0x104 bit 0 with no timeout,
  in the display ISR driven before BLE. The sim's `mspi0.panel` is a fixture (the
  "known benign mspi0.panel warning") so the bit always clears.
- **#4 ADC**: see §2. Bounded defensively by Fix 51 (1e6 spins → default nPM1300
  profile, `board_type 1`, `hw_version 0xff`). No regression in sim (FIFO ready
  on iteration 1).
- **#7 ITCM 0x40**: the GNU region table populates nothing at 0x40; stock's IAR
  scatter places a 24-byte overlay there (a busy-delay leaf + a word-copy leaf;
  exact bytes in `~/Repo/g2-firmware-emulator/generated/boot/itcm.bin`). The audit
  found **no in-tree caller** of the literal 0x40/0x44/0x48, and a binary scan of
  the early HAL found **no immediate branch** to those addresses. It remains a
  real reconstruction gap (worth closing for correctness, §6) but there is no
  evidence it is a boot hang. Earlier sessions over-weighted it; do not.

Bounded loops verified safe (do not touch): IOM power-wake retries
(`board_config.c`, `POWER_RETRIES=1000`), NOR WIP poll (`fal-norflash-wait-*`,
200 + timeout_ticks), XTAL/HFRC-adj wait (`hal/clock/xtal-request/request.c`,
counter decrement), region-table walk (`iar_cmain.c:88`), and the copy/zero init
rows.

## 4. What the simulator fakes (the gap surface)

From `~/Repo/g2-firmware-emulator`:
- **ITCM 0x40 overlay preloaded** (`sysbus LoadBinary @generated/boot/itcm.bin
  0x00000040` in `renode/boot.resc`). Hardware relies on the SBL scatter.
- **No NOR model** for littlefs content (MSPI0 is the JBD display fixture; MX25U
  is lightly stubbed; NOR is blank → littlefs mounts clean).
- **ADC model converts on digital config alone.** `renode/peripherals/G2Apollo510_ADC.cs`
  is otherwise faithful (it validates CLKSEL=HFRC24/LPMODE0, 12-bit slot, a
  provisioned SE3 code) — our digital config matches, so it passes — but its
  comment `case 4: // Power-domain transition timing is not modeled here.` means
  it **ignores whether the ADC analog power domain / reference / IRTT clock is
  actually up.** That is exactly the degree of freedom §2 points at.
- **MRAM/OTP** are synthetic fixtures; the MRAM model "does not fake a successful
  boot operation."
- **STIMER advances** unconditionally (hides #1).

## 5. Hardware-free confirmation method (feasibility proven)

The repo already used this method to debug the **case** firmware:
`build/case-link/boot.py` runs the image from reset under Unicorn with coarse
peripheral models, records every access, and diffs against the stock image as an
oracle. It caught, among 11 boot-stoppers, *"an oscillator-setup loop that never
exited"* and *"a busy-bus read that returned 0"* — the same class of hang we have
here, found with **no hardware**.

The glasses are a Cortex-M55 (Armv8.1-M), which is why the project uses Renode
(not Unicorn) for full-system G2 emulation. **But Unicorn's QEMU core does decode
and run the stock M55 cstartup** — verified this session: `build/boot-trace/trace.py`
loads the stock main app (base 0x438000, SP=0x2007fb00, reset=0x005fb8ab) and
executes cstartup, advancing through the large `.bss` zero-init. So a
**narrow** differential trace — reset → region init → init table →
`board_hw_version_detect` (0x509134) / `vTaskStartScheduler`, comparing stock vs
the reconstructed ELF — is feasible here without Renode.

What this settles, per candidate:
- **#4 ADC / §2**: does the reconstructed path reach the probe in the same clock
  and power-domain state as stock? (Diff the register writes before 0x509134.)
- **#1 STIMER**: is the STIMER clock source enabled by the reconstructed init in
  the same way stock enables it before `vPortSetupTimerInterrupt`?
- **#7 ITCM 0x40**: does stock ever read/call a pointer equal to `0x40|1` during
  boot? (If never, close the gap for correctness only.)

Harness status (`build/boot-trace/trace.py` + `STATUS.md`, git-ignored):
- Done: authoritative Apollo510 memory map (stock `.bss` zero-init of ~3 MB
  SSRAM now completes); milestone/spin/peripheral-read/demand-map + scoped
  instruction-trace instrumentation; two run modes (from-reset, and
  `--start <addr>` function-entry). **Confirmed Unicorn runs the M55 board
  code** — starting at `board_init` (0x5093ac) executes real board code.
- Blocker 1 (from-reset): `UC_ERR_INSN_INVALID` at 0x43a160 inside the stock
  IAR LZ77 region decompressor — a self-modifying-code / TB desync (it writes
  decompressed bytes into already-translated pages). This is the known reason
  the project uses Renode for the glasses. Work around with function-entry
  mode, or move this harness to Renode.
- Blocker 2 (function-entry): cstartup RAM init is skipped, so globals holding
  loop bounds are uninitialised (a `memset` at 0x43c10e runs a ~6 MB garbage
  length). Fix: replay the region-table copy/zero rows from the image first.
- Remaining (see `build/boot-trace/STATUS.md`): add `--init-rams` (walk
  `iar_region_table_base_75d3c8..limit`); model the few pre-ADC peripheral polls
  until `board_hw_version_detect` (0x509134) runs; then load a reconstructed
  `g2/build/g2c-*-final-apollo-main/g2-apollo-main.elf` and diff the
  peripheral-access sequence to the first divergence before 0x509134 and before
  `vTaskStartScheduler`. Multi-iteration (the case harness took ~10), but the
  only way to *confirm* a fix without the bricked temples or the primary pair.

## 6. Defense-in-depth hardening (recommended; gate behind §5/§7)

The goal is "a future flash does not brick," which does **not** require finding
the one true cause — it requires that **whichever** candidate fires, boot
degrades instead of hanging. Fix 51 is the template. Recommended, but each
changes boot behaviour and so must be confirmed in the §5 trace before it is
flashed (an unconfirmed behavioural boot change can itself brick):

1. **Bound #1 STIMER** so a non-ticking STIMER cannot hard-hang scheduler start.
   Care: the fallback must not desync the tickless scheduler — prefer "proceed
   after N spins as if one tick elapsed" plus a logged fault flag, not a silent
   skip. Design and confirm in the trace first.
2. **Make littlefs boot asserts non-fatal (#2):** on a mount-time invariant
   failure, log + reformat-or-degrade rather than `__aeabi_assert` (which never
   returns). Alternatively gate `LFS_ASSERT` off for the boot mount only.
3. **Bound #3 uLED MSPI ISR poll** with a timeout + error return.
4. **Close the ITCM 0x40 gap (#7)** for correctness: add a fifth region row that
   copies the 24-byte overlay to 0x40 (bytes known; matches the stock 5-row
   scatter). Low risk, but still gate behind the trace.

Do **not** apply these blind to the primary pair. They are only as safe as the
confirmation behind them.

## 7. Safe-flash guardrail (unchanged, reaffirmed)

- **Never flash the primary G2 pair** until a build boots clean in the §5
  strict/differential trace (and ideally a strict Renode reproduction).
- Keep SBL + Even bootloader intact; preserve the case serial windows; no BLE
  recovery assumptions — the wired recovery only *resets*, it cannot un-hang a
  crashing app (see `usb-case-recovery-direction.md`).
- Before any future flash, wire the early-arm MRAM wired-recovery **before** the
  earliest hang point so a still-hanging build stays recoverable — but note its
  effectiveness depends on the same pogo path the recovery campaign found silent,
  so it is insurance of uncertain value, not a proven net.
- The two bricked dev temples need SWD (sealed) or Even service; they cannot
  provide the iteration loop. The §5 trace is the substitute.

## 8. Next steps

1. Build out `build/boot-trace/trace.py` to reach `board_init` on stock (memory
   map + minimal CLKGEN/PWRCTRL/STIMER/GPIO/ADC models).
2. Load a reconstructed `g2-apollo-main.elf` and diff to first divergence before
   0x509134 and before `vTaskStartScheduler` — settles §2 and #1.
3. Apply the §6 hardening that the trace confirms, in priority order #1 → #2 →
   #3 → #7, each re-verified in the trace.
4. Only then consider the early-arm + a single recoverable hardware iteration.
