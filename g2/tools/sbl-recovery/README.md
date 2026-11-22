# G2 host-side SBL stock recovery tool

Emulator-verified host tool that speaks the stock Apollo510 wired-update
protocol (AmbiqSuite 5.2.0 `uart_wired_update.py` layout, transcribed in
`SybilSight-webflasher/scripts/g2_sbl_{protocol,wire,image,writer}.py`)
to reflash official G2 2.2.6.10 main (`ota_s200_firmware_ota.bin`).

**Do not run this against hardware from the campaign agent.** The default
mode is `sim`. The hardware path is fail-closed.

## What the sim proves

If a temple is in SBL wired-load (`MCUCTRL->OTAPOINTER == 0xAFD1363A` after
reset), the host can:

1. send HELLO `14 55 9D E9 00 00 08 00` and receive a 96-byte CRC-valid STATUS
2. send OTA descriptor `0x007FE000`, UPDATE, DATA, RESET (POI)
3. have the endpoint program the image payload (bytes after the 32-byte
   Ambiq header) at `0x00438000` and hand off to stock vectors
   `SP=0x2007FB00`, `PC=0x005E4233`

The Renode endpoint is a high-level model of that protocol, started from
`wdt.HandoffAfterSystemReset` when the recovery key is still set. It is
**not** the protected Ambiq SBL ROM. UART timing, INFO0 provisioning, and
retail cryptographic policy remain unexecuted.

## Are the current dev temples in SBL wired-load?

Probably **not**, if they still run the pre-arm bricked builds: that flash
never executed `g2_recovery_arm_early`, so a hang leaves the application
dead without the sticky OTAP key, and SBL will not stay in wired-load on
reset. This tool cannot recover those temples until they actually enter
SBL (for example after a later recovery-arm image hangs before disarm,
then a watchdog or power-on reset).

## Hardware hookup (when a temple *is* in wired-load)

Stock recovery is **USB → Smart Case → YHM2510 pogo UART**, not a bare
USB-UART soldered to the temple and not SWD (pads are sealed).

1. Connect the Even Realities Smart Case to the Mac by USB (the same CDC
   console the WebFlasher / `g2_case_pogo_flasher.py` uses).
2. Seat **one** temple on its pogo (left or right). Keep the primary pair
   untouched.
3. Select that YHM route with the reviewed stock values: right `reg7=5`,
   left `reg7=3` (plus the reviewed reg3/4/5/6 sequence in
   `build/hw/probe-bridge/RECOVERY-PLAN.md`). Restore the YHM baseline
   after the session.
4. Baud: start at **1 000 000**; **115200** is the documented fallback.
   Case-bridge DATA chunks must stay at **997 payload bytes**
   (`CASE_BRIDGE_MAX_DATA_BYTES`) because of the USB/case packet limit.
   Direct UART (no case) may use 8180-byte SBL frames.
5. The temple must actually be in SBL wired-load at the moment HELLO is
   sent. For an OTAP-armed hang that is a reset or a genuine cold boot
   (battery UVLO then VBUS / rail restore) with HELLO flooded immediately.
   A charger/pogo pulse is **not** a proven Apollo reset
   (`reference/wired-recovery-charger-reset-boundaries.md`).
6. First command is HELLO only. A 96-byte CRC-valid STATUS must be
   captured and qualified (`qualify_stock_update`) before any UPDATE.
   If there is no STATUS, **stop**. Do not send DATA, do not guess
   bootloader commands, do not touch the primary pair, do not open SWD.
7. Image: official
   `g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`
   SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
   After RESET, confirm stock BLE / case product-test
   (`24 00 01 00 A7` → `5A A5 FF 09 24 01 03 05 02 02 06 0A 03 4B`).

Hardware execution additionally requires both exact operator tokens
`I_ACCEPT_DEVICE_WRITE_RISK` and `I_ACCEPT_FIRMWARE_LANE_RISK` plus
`--hardware`. This tree's CLI still refuses to open a device.

## Running the sim verification

```
python3 g2/tools/sbl-recovery/sim_verify.py
```

Report: `build/em9305-nor-20261122/sbl-recovery-sim/report.json`.
