# G2 hardware test plan (openCFW, from 2026-10-31)

This plan follows the simulator checks recorded in
[sim-test-report.md](sim-test-report.md) ("2026-10-31 — jimrandomh emulator").
The simulator runs only the Apollo510 main application and bootloader. The
EM9305, codec (GX8002B), touch (PSoC 4000T) and case (STM32G0B1) are modeled
peripherals or are absent, so their rebuilt images have no simulator evidence.

## Safety rules

1. **The OTA receiver is the only known recovery path.** No SWD/debug access is
   documented for the G2 (`docs/hardware/g2-glasses.md`). A main application
   that crashes before it can accept an OTA leaves that temple unrecoverable
   without opening it. g2flash says the same about early-boot changes.
2. **Keep the stock bootloader.** Install only the MAIN component (TOC index 5)
   at first. The rebuilt bootloader, EM9305, codec, touch and case images stay
   off hardware until a wired recovery path exists or the user accepts the risk
   for that component.
3. **One temple at a time.** Flash the right temple first, then the left only
   after the right passes every step below. Mixed stock/openCFW temples talk
   over the TinyFrame UART link, which the simulator exercises only in the
   paired profile.
4. **Prove the way back before anything else.** The first test after the
   openCFW boot is reinstalling stock from openCFW itself.
5. Have these files ready before starting: the stock 2.2.6.10 container
   (`g2/blobs/official/g2-2.2.6.10/e28738432d7b612d625331b00383149b.bin`), the
   container the glasses currently run, and the openCFW container.

## Package

`build/simota/pack_main.py <stock 2.2.6.10 container> <apollo-main.bin> <out>`
replaces only the MAIN payload. It rebuilds the MAIN preamble (flags 0x04 |
size, zlib CRC-32 over payload[8:], type 0xCB, run address 0x438000) and every
CRC32C. Repacking stock's own application reproduces the stock container byte
for byte. The other five components stay stock 2.2.6.10, which matches the
2.2.6.10 coprocessor interfaces the rebuilt app expects.

## Steps

| # | Step | Pass condition | If it fails |
|---|---|---|---|
| 0 | `g2flash.py -c … -f <stock 2.2.6.10> --stop-before flash` | Both temples connect and authenticate | Fix connectivity first |
| 1 | Flash stock 2.2.6.10 (full container) to both temples | Boots, pairs with the Even app, dashboard shows | Stock path problem; stop |
| 2 | Flash the openCFW container to the **right** temple (`--lens right`) | Transfer completes; END accepted (no status 7) | Package or CRC problem; the temple still runs stock |
| 3 | Watch the right temple boot | Advertises `Even G2_32_R_xxxxxx`; display wakes; no reboot loop for 2 minutes | Note the symptom; go to step 4 if it still advertises |
| 4 | **Recovery check:** flash stock 2.2.6.10 back to the right temple from openCFW | Transfer completes, stock boots | Stop all hardware work; investigate in the simulator |
| 5 | Reflash openCFW (right), then pair with the Even app | Pairing, settings sync, battery reading | Compare with the simulator's paired run |
| 6 | Dashboard, touch gestures (tap, double tap, slides, long press), wear detection | Same behavior as stock | Record which gesture differs |
| 7 | Notifications, teleprompter, translate/conversate text, EvenHub page with a list | Same text and layout as stock (locale tables now load) | Check `.data` init first |
| 8 | Deep sleep and wake, 30 minutes idle, charging in the case | Wakes; no watchdog reset; charge level sane | SPOTMGR/power path (upstream SDK) |
| 9 | Audio: microphone and wake word through the codec | Audio reaches the phone | Codec host path |
| 10 | Repeat 2–9 on the left temple, then run both temples together | Paired sync works; both lenses render | TinyFrame/UART0 path |

Record the firmware version string, the date, and any reboot or watchdog event
for every step. A failure at step 2 or later goes back into the simulator first.

## Simulator pre-checks before step 2

- Done, 2026-10-31: `build/simota/opencfw-main-1031.evenota` passes the simulated stock 2.2.6.10 → openCFW → stock round trip on one device with the stock bootloader. The retained phone bond, our OTA receiver, the stock bootloader's CRC check and reinstall all work. See `sim-test-report.md` (round trip #3).
- Rebuild the container and repeat this round trip after any apollo-main change before it goes to hardware.

## Not covered here

- Rebuilt bootloader on hardware. The simulator boots it and it hands off to
  the app, but a bad bootloader cannot be recovered over OTA.
- EM9305, codec, touch and case images: no simulator model executes them.
- The vendor fuel-gauge library question, still open with the owner.

## Log

### 2026-10-31 — first hardware session (case USB only)

- Case on `/dev/cu.usbserial-210`: B200 1.2.57, both temples seated. Both
  temples ran official **2.3.0.24** (hardware 5), not 2.2.6.10.
- This case's YHM2510 register-8 byte is 0x33. The Python case tool only knows
  the 0x22 profile and stopped at setup (status 3, zero writes). The browser
  WebFlasher's pinned `observed-33` profile was applied through
  `build/hw/g2case.py` (bridge SHA-256 `b341adc4…`); read-only version queries
  then worked on both temples.
- Two case-USB installs of the official 2.2.6.10 main to the right temple
  (`build/hw/audit-0{1,2}-stock2210-right.json`) stopped at START (0x52): the
  temple sent 14 bytes but no complete frame. 0 bytes accepted; the right
  temple still runs 2.3.0.24 and answers version queries. A DEB0 reset between
  the attempts did not help. This is the WebFlasher's
  `wired_start_no_frame_zero_byte_boundary`; its documented next step is a
  Bluetooth full-package install. No further wired START attempts.
- Bluetooth from this session failed: macOS killed the process (no Bluetooth
  permission), and in the Terminal panel CoreBluetooth never became ready.
- openCFW has not been written to either temple.

### 2026-10-31 — Bluetooth installs; openCFW on the right temple does not come up

- Bluetooth works from the app's Terminal panel (not from the agent's own
  shell, which macOS aborts). `SybilSight Debug.app` held both temples'
  connections and was quit so they would advertise. Pair in use: left
  `Even G2_32_L_ACD458` (E0:9B:50:AC:D4:58), right `Even G2_32_R_8D6E3C`
  (EC:F1:B6:8D:6E:3C); both appeared together right after a case DEB0 reset.
- g2flash dry run (to FILE_CHECK) passed on both. Full official 2.2.6.10 install
  on both temples: 6/6 components verified each, 0 resends
  (`build/hw/ble-stock2210-both.log`). Both then read 2.2.6.10 through the case.
- Stock 2.2.6.10 baseline over Bluetooth on the right temple
  (`build/hw/hwhub.py`, the simulator's EvenHub/settings plan): 20
  notifications, results identical in kind to the simulator's stock run
  (create 0, image LZ4 accepted, rebuild 6, text 8, heartbeat 12, IMU 1/0).
- openCFW (`build/simota/opencfw-main-1031.evenota`, only the main app differs
  from stock 2.2.6.10) installed on the right temple: 6/6 components verified,
  0 resends (`build/hw/ble-opencfw-R-01.log`).
- **Result: the right temple did not come back.** No advertising, no reply to
  case-bridge version queries, no battery telemetry to the case. The case
  logged "No reply from GLS_R" every 15 s, reset the temple at 180 s, and
  showed its error LED at 210 s. The left temple (stock) is unaffected.
- Ruled out: the simulator runs preloaded stock's 24-byte ITCM overlay at 0x40;
  ours and stock both still boot in the simulator with it zeroed.
- With no running application there is no known way back: both the BLE OTA
  receiver and the case pogo product-test path are application services. A
  wired route needs SWD or a proven Ambiq SBL UART recovery
  (see `g2/docs/reference/hardware-validation-notes.md`).
- WebFlasher USB recovery, no-flash step ("Diagnose & recover without
  flashing": bounded DEB0 bilateral reset plus liveness, up to two resets),
  run through the Python equivalent: both resets confirmed by the case; the
  right temple still returned no frame and no telemetry for 60 s afterwards.
  The left temple kept reporting normally. The WebFlasher's other USB action
  (Restore) needs a running temple application, so the USB route is exhausted
  for the right temple.

### 2026-10-31 — looking for a cause and a non-invasive way back

- The temples are sealed (glue and resin), so SWD is not an option.
- Simulator variants of our image all still boot to the same idle state with the
  same 60 HCI/frame lines as stock: ITCM 0x40 overlay zeroed, and all of DTCM
  and SSRAM filled with random bytes before reset. Uninitialised RAM alone does
  not reproduce the hardware failure in the simulator.
- Real defects found while looking (not yet fixed, not proven to be the cause):
  - `.noinit` (0x20374800, 29 KB) is never zeroed. It holds
    `audio_dashboard_auto_close_{current,default}` (stock 0x200743d0/d4, inside
    the stock DTCM zero range, so zero at stock boot) and the 20 KB
    `audio_uart_ring_config_workspace` (stock 0x20324600, inside the stock SSRAM
    zero range).
  - Our image holds literal stock RAM addresses that fall in our unzeroed,
    unowned DTCM gap 0x20071078..0x2007D000 but inside the stock zero range
    (for example 0x200742d4, 0x20073704, 0x20073ff0, 0x20074603..0x200747a0).
    Code that reads them sees zero in the simulator and random data on hardware.
- What the simulator cannot show and real hardware differs in: the real NOR
  contents (littlefs and FlashDB written over months by stock; our FlashDB
  source is 2.0.0 against stock 2.1.1), the display panel's replies, PMIC and
  charger state in the case, and codec/touch timing.

### 2026-11-01 — RAM-init fix (Fix 43) + self-recovery arming unit

Software only; nothing written to either temple. Target of the brick: the
hardware-only uninitialised-RAM defects recorded in the 2026-10-31 entry
above (zero in the Renode simulator, random on hardware).

- **Fix 43 (RAM-init), the primary fix.** Reproduces the stock cstartup
  zero-init state on hardware:
  - `runtime/g2c-gnu/g2c_gnu_init.c`: added one region-table zero row over the
    unowned DTCM gap `[__dtcm_bss_end, _sstack)` = `[0x20071078, 0x2007d000)`
    (resolved from the linked ELF). Covers the stock DTCM literals the hand
    copies read (0x200742d4, 0x20073704, 0x20073ff0, 0x20074603..0x200747a0).
    The live MSP stack sits above 0x2007d000, so the zero never touches it.
  - `drivers/peripherals/ring-config/ring_config_storage.c` and
    `app/dashboard-auto/dashboard_auto_close_reset_49c0dc.c`: moved the
    `.noinit`-misplaced cells (native 0x20324600, 0x200743d0/d4 — all inside
    stock's zero range) back to `.bss` so the region table zeroes them, as
    stock does. `ring_persist` and `crash_record` stay `.noinit` (genuinely
    past the stock zero range; must survive a warm reset).
  - Verified: `make -C g2 sources-check` ok; payload compiles 2717/2717, 0
    duplicate strong symbols; full link 0 undefined/unresolved; Renode 20 s
    boot clean (PC 0x542a60, ~85 M instructions, no HardFault, only the known
    benign mspi0.panel fixture warning). The simulator cannot *prove* the HW
    fix (those cells are already zero in the sim); it proves no regression.
- **Self-recovery arming unit** (`system/self-recovery/self_recovery.c`, new
  openCFW unit, registered in `g2/src/sources.json`). Arming primitive
  (`MCUCTRL->OTAPOINTER = 0xAFD1363A` at 0x40020264, chip-rev >= B1 guard) +
  crash-loop gate + persistent `.noinit.self_recovery` counter (verified at
  SSRAM 0x2037a834, outside the Fix-43 gap and `.bss`). **Not wired into the
  boot path** — see `reference/self-recovery-arming.md` for the reset-signature
  and wired-reachability prerequisites. Compiles (2718/2718) and links clean;
  combined-image 20 s boot clean (PC 0x542b00, same signature).
- **Flash-ready container** (not flashed): `build/simota/opencfw-main-ramfix-1101.evenota`
  (6 components, MAIN = this build; sha256 247924103703796e25a87b10d38f67ccab020fe63575153367f4495bd3bbb8a0).
- **Still gated on an explicit decision:** flashing the healthy **left** temple.
  BLE OTA remains the proven rollback (sim round trip #3). A full stock->ours->stock
  OTA round trip in Renode (~3 h) has not been re-run on this build.

### 2026-11-01 — hardware flash of the RAM-fixed build: NEGATIVE

Flashed `build/simota/opencfw-main-ramfix-1101.evenota` (MAIN = RAM-fix build,
other 5 components stock 2.2.6.10) to the **dev pair's healthy left temple**
`Even G2_32_L_ACD458` (00:00:00:AC:D4:58) over BLE with g2flash (user authorized
destructive testing on a development-only pair). Log `build/hw/ble-opencfw-L-ramfix-01.log`.

- Flash itself was clean: all 6 components verified, 935/935 MAIN blocks, 0
  resends, END verify OK; "glasses should reboot into the new firmware."
- **The left temple did not come back up.** ~2.5 minutes of BLE scans
  (08:01:46–08:04:20, build/hw/.venv blescan) showed no `Even G2_32_L_*`
  advertising at all. Case-side read-only pogo version query on `-210`: "left
  presence confirmed" but "no complete temple frame through case bridge" — i.e.
  seated/powered, application dead. Identical for the right temple.
- **Both dev-pair temples are now bricked identically** (present, app dead, no
  BLE, no case frame). The RAM-init Fix 43, though correct and necessary, is
  **not** the (sole) cause of the brick. openCFW main does not boot on this
  hardware even with the stock startup zero-init reproduced.
- The simulator still boots this exact build cleanly, so the failure is in
  something Renode does not model (real NOR/littlefs/FlashDB contents, display
  panel replies, PMIC/charger/codec/touch timing, or a hardware-only early
  init). The hang is early — before BLE advertising and before the case-bridge
  responder.
- Recovery: unchanged dead-end. No BLE (app down), no case-bridge frame, SWD
  sealed. The self-recovery arming hook could not have helped — it was unwired,
  and arming requires the app to run far enough to execute it.
- **No healthy G2 test temple remains on the dev pair.** Do NOT flash the
  primary pair: the current build is disproven on hardware. Next work is
  diagnostic (close the sim/hardware gap), not another flash.

### 2026-11-01 — sim/hardware gap investigation + ADC poll fix (Fix 51)

Investigated why openCFW hangs early on hardware but boots in Renode. Full
analysis in `reference/sim-hardware-gap.md`. The sim fakes early bring-up
(preloads the ITCM 0x40 overlay, no real NOR model, lenient clocks/ADC), so a
reconstruction bug that spins on a real peripheral passes in the sim.

- **Root-cause candidate + fix:** `app/a-41-board-config/board_config.c`
  `board_hw_version_detect_509134` (via board_init_5093ac, init priority 1,
  pre-scheduler) spun in `while (((ADC_FIFO_REG>>20)&0xff)==0){}` with no
  timeout. On real silicon a non-converting hw-id ADC leaves FIFO COUNT at zero
  forever → whole boot hangs before any service. The sim satisfies the FIFO on
  the first read. This is the only unbounded hardware poll in the reconstructed
  pre-scheduler path. **Fix 51** bounds the poll (HWID_ADC_POLL_LIMIT) and
  defaults to the nPM1300 board profile on timeout so boot proceeds.
- Verified: sources-check ok; payload 2718/2718, 0 dup symbols; link 0
  undefined; Renode 20 s boot clean (PC 0x542be8, ~85M instructions, no
  HardFault) — behaviour unchanged in the sim (timeout never fires there).
- Flash-ready container: `build/simota/opencfw-main-adcfix-1101.evenota`
  (sha256 e8b9eb7491c127334d55e12a5d8ce9599d0bb7fd4d753b89a00e7eb2b4f12305).
- Secondary leads NOT yet fixed (see sim-hardware-gap.md): littlefs asserts-on +
  real-NOR content / MSPI XIP request-number + 4QOR dummy-cycle divergences
  (post-scheduler storage thread); and the missing ITCM 0x40 overlay copy row
  (low confidence — no caller found).
- **Cannot be confirmed without hardware** (the sim boots regardless). Next step
  is the self-recovery / early-arm experiment to get a recoverable hardware
  iteration loop, then boot this build and read whether the ADC timed out or the
  hang moved to storage.

### 2026-11-01 — recovery experiment wired (early arm + healthy disarm)

Built the MRAM wired-recovery experiment into openCFW so a flash that still
hangs early leaves the temple recoverable. Details in
`reference/self-recovery-arming.md` ("Recovery experiment").

- **Arm** `g2_recovery_arm_early()` in `low_level_init_5e4228` (earliest C,
  before RAM-init / board_init / the ADC poll): unconditional
  `MCUCTRL->OTAPOINTER = 0xAFD1363A` (MMIO-only; B0 skipped), original OTAPOINTER
  saved in `.noinit.recovery_save` (SSRAM 0x2037a840).
- **Disarm** `g2_recovery_disarm_healthy()` in `DEV_BoxRevcMsgProcess_53a0b6`
  after answering a charging-case product-test frame: restores OTAPOINTER so a
  healthy temple reboots normally. A hung temple never answers → stays armed →
  SBL wired-load on next reset → recoverable over the pogo link (then reflash
  with the probe-bridge / stock).
- Verified: sources-check ok; 2718/2718 compiled, 0 dup symbols; link 0
  undefined; Renode 20 s boot clean (PC 0x542c80, no HardFault) — the arm is a
  harmless MMIO write in the sim; the disarm path needs a real case, so it is
  exercised only on hardware.
- Container: `build/simota/opencfw-main-recovery-1101.evenota`
  (sha256 aab93fc75ec964ccd94171b90db5cc83f3026d257e008a2bd7fb177e43469af6);
  bundles RAM Fix 43 + ADC Fix 51 + the arm/disarm.
- **Testing needs a flashable healthy temple, which we do not have** (both dev
  temples are bricked, and they run the pre-arm build so cannot be armed
  retroactively). The wired-load recovery path itself is still unproven — the
  point of this build is to test it on the next flash. The full toolchain is
  ready: flash this build → if it hangs, reset → run `build/hw/probe-bridge`
  (case wired HELLO) against the now-armed SBL.
