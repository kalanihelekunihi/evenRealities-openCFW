# Even bootloader recovery path — where the wired recovery actually ends (2026-11-01)

Written to correct a loose earlier claim ("wired recovery is unreachable") with
the precise mechanism, from the reconstructed bootloader (`docs/firmware/` +
`docs/firmware/decompilation/bootloader/*` in git history, and
`g2/docs/reference/{protocols,memory-map,capabilities}.md`).

## What is true

- The brick is a **software brick**: a CRC-valid openCFW main app that hangs early
  in `board_init` (unbounded ADC-FIFO poll, Fix 51 / RAM Fix 43), before any comms.
- We **have a known-good image** (`build/simota/stock-repack.evenota`, 2.2.6.10).
- There **is** a wired recovery mechanism we own: the **Even bootloader's DFU
  installer** at `0x00410000`, which is untouched by any app flash and works (it
  is how openCFW got installed in the first place).

## Why it nonetheless cannot reach an already-bricked temple

The Even bootloader is an **installer, not a wire receiver**. Boot decision
(reset handler `0x004324CF`):

```
DFU trigger / OTA flag set?  -> DFU install
no valid app?                -> DFU install
valid app present?           -> hand off to 0x00438000   <-- our bricked case
```

- `is_need_updata_image` (`0x0042e170`) reads the **OTA flag** — MRAM record at
  `0x007FE000` (16 B, value `0x55555555`). Set ⇒ `thread_dfu_task` (`0x0042dc60`)
  installs; clear ⇒ jump to app. Our flag is clear and the app is statically
  valid, so the bootloader hands off to the hung app every reset.
- `thread_dfu` installs **from a file**: `ota/s200_firmware_ota.bin` on the
  MX25U25643G norflash (littlefs). It reads header → CRC (`0x0042D890`) → program
  (`0x0042DAE8`) → verify → handoff. **There is no over-the-wire receive in the
  bootloader.** Its only transports are the EasyLogger **debug UART** (output
  only, `redirect.c`), MSPI (to norflash), and I2C (hardware) — none accept a
  firmware stream, and it does not speak the case's `5A A5 FF` app frames (hence
  the case sees "present, no frame").
- `boot_count` (littlefs) is incremented per boot but drives **no anti-brick
  fallback** — there is no "N failures ⇒ DFU" path in the decompiled flow.

So the firmware image is **staged + the flag set by the application** during a
normal OTA (case/BLE → app receiver → norflash + `0x007FE000`), then the
bootloader installs on reset. **The wire's endpoint on the temple is the app.**
openCFW hangs before its OTA receiver (box_uart_mgr / BLE OTA service) starts, so
nothing over pogo or BLE can stage an image or set the flag. Writing `0x007FE000`
(MRAM) or the `/ota` file (norflash) requires on-temple code (dead) or SWD.

**Conclusion for the current bricks:** unchanged — only the Ambiq SBL wired path
(INFO0/INFOC-gated, SWD-only to verify) or SWD/manufacturer service can write the
temple with the app down. The bootloader, which survives, is deaf to the wire.

## The real anti-brick this reveals (protects FUTURE flashes)

The recovery we own can be armed **by on-temple code before the hang**:

1. openCFW keeps a known-good stock `s200_firmware_ota.bin` present in the
   norflash `/ota` (or `/firmware`) directory.
2. A very early boot hook (before the risky HW bring-up) tracks boot health; on
   repeated early-boot failure it writes `0x55555555` to the MRAM update flag at
   `0x007FE000` pointing at that staged good image.
3. Next reset → the Even bootloader (always runs, always works) reinstalls the
   good image → clears the flag → hands off to a healthy app.

This bypasses **both** the Ambiq SBL/INFO0 path and SWD — it uses only the
bootloader installer we already have. Limits:

- It must be armed by code that runs **before** the hang, so it only protects
  temples flashed with openCFW that already carries the arm. It cannot save the
  two temples already bricked with pre-arm openCFW.
- It supersedes the earlier `self_recovery.c` MRAM-recovery arm, which targets the
  Ambiq SBL (INFO0-gated, likely inert). The **Even-bootloader OTA-flag arm is the
  recovery we actually have** and should replace it.
- Requires openCFW to safely program the `0x007FE000` MRAM record and to stage a
  file in its own littlefs — both must be validated in sim and reviewed before any
  flash (and never flashed to the one good temple without BLE-OTA rollback staged).

## Open question for the user

If the intended "wired recovery we have" is a **case- or bootloader-level entry I
have not mapped** — e.g. a case console/jig command that forces the temple
bootloader into a *receive* mode, or a factory protocol distinct from the app's
`5A A5 FF` OTA — that would change this conclusion. The reconstructed bootloader
shows no such receiver, but the decompilation is not a guarantee of completeness.
