# G2 self-recovery arming (openCFW, 2026-11-01)

Status: the **gated production policy** (`g2_self_recovery_boot_check`) remains
built-but-unwired (see "crash-loop gate" below). The **recovery experiment**
(unconditional early arm + healthy disarm) is **wired into the boot path**.
As of 2026-11-22 it also disarms when BLE advertising is enabled, so an
out-of-case temple is not left armed. See "Recovery experiment" at the end.
The 2026-11-01 container `opencfw-main-recovery-1101.evenota` predates the
advertising disarm; use a rebuild from current sources (the 22 Nov 2026
Apollo-main image is `build/g2-apollo-recovery-20261122-link/g2-apollo-main/`).

## Why

The right G2 temple is bricked: after an openCFW main-app install it hung
before coming up, so it never advertises and answers neither the BLE OTA
receiver nor the case pogo product-test path (both are application services).
The only documented route into a dead Apollo temple is the secure
bootloader's (SBL) wired-recovery path. The temples are sealed (glue + resin),
so SWD is not available; the case pogo UART is the only physical wire.

The 2026-10-31 probe campaign (`build/hw/probe-bridge/`, custom case firmware)
spoke the Ambiq wired HELLO on the right pogo route under steady-state and
boot-window conditions and got **no genuine reply** — but always on a
*valid-image boot*, where the SBL hands off to the app and does not sample the
wired interface. The campaign never tested the one state that would make the
SBL sample wired: an **armed** application-initiated MRAM recovery. Nothing in
our firmware ever armed it, so the wired path was never actually exercised in
its intended mode. Arming is the untested key — not proven dead.

## The arming primitive (`g2/src/apollo-main/system/self-recovery/self_recovery.c`)

`g2_mram_recovery_arm()` mirrors
`am_hal_mram_recovery_init_app_recovery(0xAFD1363A, bReset=false)` from
`third-party/upstream/ambiqhal-apollo510/.../hal/mcu/am_hal_mram_recovery.c`:

- Write the recovery key `0xAFD1363A` to `MCUCTRL->OTAPOINTER` (`0x40020264`,
  struct offset 0x264; cross-checked against our own MCUCTRL pokes in
  `hal/a-03-sysctrl/am_hal_sysctrl_sleep_variant.c` and the Ambiq CMSIS header).
- No reset is forced (`bReset=false`): a healthy app keeps running; the SBL
  enters wired-load mode only on the **next** reset.
- Chip-rev guard: arm only on `MCUCTRL->CHIPREV` (`0x4002000c`) `[7:0] >= 0x22`
  (B1 = 0x22, B2 = 0x23). The upstream HAL refuses on APOLLO5_B0; we mirror that.

## The crash-loop gate (built, unwired)

`g2_self_recovery_boot_check(wdt_reset, clean_reset)` is a complete gate:

- Persistent counter in SSRAM `.noinit.self_recovery` (verified at
  `0x2037a834`, inside the NOLOAD `.noinit` section the region table never
  zeroes, and outside the DTCM gap cleared by Fix 43 — so it survives warm /
  watchdog reset).
- A clean reset (power-on / external — a user restart) clears the counter.
- A watchdog reset increments it. At `G2_SELF_RECOVERY_THRESHOLD` (5)
  consecutive watchdog resets with no clean reset between them, it arms once.
- `g2_self_recovery_mark_healthy()` clears the counter once the app is
  confirmed up, so normal operation can never accumulate toward the threshold.

## Why it is NOT wired into `board_init_5cdd14()`

1. **Reset-cause signature is unknown.** The gate keys on the watchdog reset,
   but the bricked right temple's actual reset cycle was never captured (the
   case reset it externally at 180 s; the temple may never have driven its own
   WDT). Keying on the wrong cause would either never arm, or — if widened to
   external resets — arm on an ordinary user power-cycle.
2. **The wired path may be unreachable even when armed.** INFO0/INFOC wired
   provisioning is SWD-only to read, and the pogo probe was silent. If arming
   does not open a reachable channel, a device that crosses the threshold is
   left requesting an SBL wired-load that never completes.
3. It is boot-path code on the **only working (left) temple**. A wrong trigger
   endangers the exact device we are protecting.

The left temple's proven rollback stays **BLE OTA** (sim round trip #3,
`sim-test-report.md`): arming is insurance, not the primary safety net.

## Prerequisites to wire + flash

1. Capture the brick's reset-cause signature (via `g2_reset_status` /
   `crash_record`) on a real device so the gate keys on the true crash cause.
2. Confirm an armed SBL actually makes the pogo wired path respond (re-run the
   `probe-bridge` HELLO against a temple that has armed recovery).
3. Choose a reliable `g2_self_recovery_mark_healthy()` call site (BLE
   advertising / OTA receiver ready).
4. Re-link, re-run the Renode boot + OTA round trip, then flash with BLE OTA
   rollback staged.

## Related

- RAM-init Fix 43 (`runtime/g2c-gnu/g2c_gnu_init.c`): zeroes the unowned DTCM
  gap `[0x20071078, 0x2007d000)` and moves the `.noinit`-misplaced
  `dashboard_auto_close` / `ring_config_workspace` cells back to `.bss`, so the
  stock startup zero-init state is reproduced on hardware. This is the most
  likely brick cause and is the primary fix; self-recovery is secondary.

## Recovery experiment (implemented 2026-11-01)

Goal: flash openCFW to a (dev) temple and, if it still hangs early, have the
Apollo SBL come up in **wired-load mode** on the next reset so the temple is
recoverable over the case pogo link — the one recovery route we have never been
able to test (it needs an *armed* SBL, which nothing previously provided).

Wiring (two call sites, both openCFW-original, not stock):
- **Arm** — `g2_recovery_arm_early()` called from `low_level_init_5e4228()`
  (`runtime/C3-startup/iar_cmain.c`), the earliest C hook: it runs *before*
  `iar_data_init3` (RAM-init) and *before* `main`/`board_init`/the ADC hw-id
  poll, so it executes even on a boot that hangs early. It writes the recovery
  key to `MCUCTRL->OTAPOINTER` (pure MMIO, no RAM needed), after saving the
  genuine pre-arm OTAPOINTER in `.noinit.recovery_save` (SSRAM 0x2037a840,
  persists across warm resets). Unconditional (arms every boot). B0 chips are
  skipped, as upstream.
- **Disarm** — `g2_recovery_disarm_healthy()` restores the saved OTAPOINTER
  so the **next** reset boots normally. It is called from two healthy-path
  sites, both openCFW-original:
  - `DEV_BoxRevcMsgProcess_53a0b6()` (`drivers/power/box-detect/box_uart_mgr.c`)
    right after the temple sends a product-test response to the charging case
    (scheduler, device-manager thread and pogo UART are alive).
  - `g2_recovery_disarm_on_advertising()`, added 2026-11-22, immediately after
    `HciLeSetAdvEnableCmd(1)` in `audio_ble_dm_adv_start_4b9e88` and
    `audio_ble_dm_adv_start_directed` (the first-party enable=1 sites; upstream
    Cordio `HciLeSetAdvEnableCmd` was not edited). That helper also calls
    `g2_self_recovery_mark_healthy()` so the still-unwired crash-loop streak
    would be cleared if that gate is later connected.

Resulting behaviour:
- **Hang (expected):** armed early, never reaches advertising enable or a
  case product-test reply → stays armed → next reset (watchdog, or a
  case-driven reset) → SBL wired-load → recover over the pogo link, then
  reflash stock or a fixed build.
- **Healthy, in or out of the case:** armed early, then disarmed when
  legacy advertising is enabled (HCI `010A200101` in the Renode boot path)
  or when the temple answers a charging-case product-test frame → next
  reset boots the app normally. A working temple, including one used
  entirely out of the case, is not left stuck in recovery.
- The key write is MMIO-only, so recovery is armed even if the hang is before
  RAM-init. The crash-loop gate stays unwired until a hardware reset
  signature exists; replacing the early arm with that gate would drop
  recovery for a hang that never increments a watchdog streak.

Verification (2026-11-22): Apollo-main rebuilt 2718/2718 and relinked
(3,818,880 bytes, SHA-256
`9d7bcc5edf64a893c47dc49fb0f124fceea4598bf39aaaaca750df9ce4e3cac2`,
reset PC `0x0059404d`). Version-match NOR paired Renode, 8 virtual seconds,
with a `MCUCTRL.CHIPREV=0x22` fixture (required because the model Reset()
zeroes CHIPREV and the arm is a no-op on `(rev & 0xff) < 0x22`). Stock and
openCFW HCI (56 packets, including `010A200101`) and two display frames
(hash `0c5cc90b079d0d9c1ded1376357d23a9782a704a83e01731f50ccd162e246492`)
were byte-identical to each other and to the CHIPREV=0 5:55 AM CST
baseline. OpenCFW `OTAPOINTER` was `0` before run, `0xAFD1363A` after 0.01
virtual seconds (armed), and `0` after 8 seconds (disarmed). Stock
`OTAPOINTER` stayed `0`. The case-reply disarm path was not the path
observed in this run. The wired-load recovery itself is still unproven
on hardware. Do not flash the primary pair.
Evidence: `g2/evidence/g2-20261122-recovery-advertising-disarm-renode.json`.

Container: `build/simota/opencfw-main-recovery-1101.evenota`
(sha256 aab93fc75ec964ccd94171b90db5cc83f3026d257e008a2bd7fb177e43469af6).
It also carries the ADC poll fix (Fix 51) and RAM Fix 43.


### 2026-11-22 — case-reply disarm + pre-ADV unexpected reset (Renode)

Image: `opencfw-otap-disarm.app.bin` (SHA-256
`7c691d8ce955479f748554628107e977cc723ef945b6509dcd00dae1aac625dd`).

- **Case-reply path proven.** After ADV had already cleared OTAP, re-arm
  `OTAPOINTER=0xAFD1363A`, inject uart2 `24 00 01 00 A7`. Reply TX
  `5A A5 FF 09 24 01 03 05 02 02 06 0A 03 4B`; OTAP→0; next reset is SBL
  application handoff. Wrong frame `01 00 00 00 00 84` does not disarm.
- **Unexpected reset while armed (before ADV) → SBL wired-load.** Intended
  recovery for app-dead / watchdog-class reset with the early arm still set.
  Without a pogo/SBL host the temple still looks dead (no BLE).
- **Remaining risk.** Real Ambiq SBL wired-load + probe-bridge on silicon
  unproven. Do not flash the primary pair. Crash-loop gate still unwired.

Evidence: `g2/evidence/g2-20261122-case-reply-and-early-reset.json`.
