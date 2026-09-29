# G2 on-device observations and safety notes

Condensed from `g2/docs/hardware-validation-2026-08-23.md`,
`g2/docs/hardware-validation-2026-08-30.md` and
`g2/docs/hardware-validation-policy.md`. Only device facts, procedures and
cautions are kept; campaign status is omitted. Nothing in this repository
authorizes signing, flashing, resetting, erasing, or exercising a device; the
qualification phase starts only when the project owner says so.

## Authorized hardware (2026-08-23 record)

| Item | Identity |
|---|---|
| Glasses serial | `S211GBBC180304` |
| Left temple | `EVEN G2_32_L_4FB39E`, `F0:F1:0C:4F:B3:9E` |
| Right temple | `EVEN G2_32_R_1412E0`, `E0:EC:B6:14:12:E0` |
| Case | USB serial `/dev/cu.usbserial-210`, B200 firmware `1.2.57` |

No other nearby glasses may be connected to or written. Another G2 is never a
substitute for the authorized pair.

## How devices were flashed

- **Stock baseline.** Both temples were downgraded over exact-name BLE to the
  official `2.2.6.10` package (hardware revision 5), SHA-256
  `f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`, taken
  from the SybilSight WebFlasher firmware set.
- **Flash transport.** Multiple successful firmware flashes through
  `evenRealities-webflasher` are established; flashing transport itself is not
  a blocker.
- **Full-package BLE install (right temple).** An exact-address BLE install of a
  source-built `2.2.6.0` candidate completed all six components, 1,099 blocks,
  zero resends, and an `UPDATING` acknowledgement at every component END.
- **Case product-test route.** The stock case application/product-test route
  rejected a right-temple START at the zero-byte boundary; the BLE route was
  used instead.
- **Candidate facts observed offline before that install.** Vector table,
  initial SP `0x2007FB00` and reset handler `0x005E4233` were unchanged from
  stock; the candidate changed 145,986 bytes of the stock-sized Apollo image
  through 1,118 patch sites.

## Boot path facts learned

- Startup enters `0x005CE01E`, delays, calls `0x005BF0BC`, and only then emits
  the first startup log. `0x005BF0BC` calls the public IAR `memcpy`
  (`0x00439BE4`) to populate and run an initializer table, so `memcpy` is the
  earliest non-trivial runtime call on the boot path.
- Consequence for any modified image: qualify in stages, never all hooks at
  once. The staged ladder that was prepared:
  1. stock-code control (stock Apollo bytes, only nested CRC and two version
     fields changed: eight bytes in three runs);
  2. one minimal hook (a 412-byte function plus one 4-byte BL for the
     advertised-name suffix, stock vector table);
  3. the earliest critical hook (rung 2 plus a source-built `memcpy`).
  Each rung only after the previous one boots on an authorized temple.

## Case interruption behavior

- The apparent right-temple "application-dead" state after the BLE install was
  caused by the charging case being bumped during an unattended run, which
  interrupted the connection mid-way. It is **not** evidence of a temple fault,
  a failed flash, or a firmware defect, and must not be cited as one.
- Symptoms seen at the time (retain only as chronology): case still reported
  the right physical contact present; the right application UART returned no
  complete frame; `EVEN G2_32_R_1412E0` stopped advertising; a bilateral
  `DEB0` case-console command did not restore liveness. The normal case
  application later returned as B200 `1.2.57` reporting both contacts present.
- Lesson: keep the case physically undisturbed during any link-dependent
  operation; an unattended run through the case is fragile.

## Recovery behavior and read-only experiments

- A hash-pinned case-SRAM bridge was used that accepts only the exact 8-byte
  Ambiq Apollo5 wired-update HELLO `14559de900000800`; it has no data, erase,
  OTA or arbitrary-byte command.
- Attempt 1 stopped before launch: the case reset gate reopened the console and
  sent `DEB0` while the case was rebooting. Fix: presence preflight and `DEB0`
  in one console session.
- Attempt 2 accepted all eight bytes but an inverted validator rejected the
  request; retained SRAM proved zero temple bytes and byte-identical YHM
  (case PMIC) restoration. Fix: validator returns 0 only for the exact HELLO.
- Attempt 3 stopped at bridge setup on an unexpected post-reset YHM state
  `810104ffa603c10522ff`; ten-register baseline read, zero YHM writes, zero
  temple bytes, no UART errors. That transient must not be allowlisted.
- Apollo5 SBL wired update depends on per-device INFOC/INFO0 provisioning,
  which the stock case cannot read from a temple whose application is not
  running. Read-only debugger acquisition would be needed first:
  INFOC `0x400` bytes from `0x400C2000`; active INFO0 at least `0x6C` bytes
  from offset 0. Decode with the WebFlasher `recoveryConfig.js` and continue
  only if it proves wired UART enabled on the pogo pins, exact baud/framing/pin
  words, a nonzero wired receive window, a usable INFOC boot override or real
  SBL boot error, any required MRAM wired-recovery enable, and an authorized
  image format. A dump alone never authorizes a write
  (`firmwareWriteAuthorized: false`); device-identity binding and a live
  CRC-correct SBL STATUS frame are separate requirements.
- Without those, recovery needs manufacturer service or physical debug access.

## Host environment (2026-08-30 inventory)

- `/dev/cu.usbserial-210` and `/dev/tty.usbserial-210` were present; no USB
  records enumerated; no J-Link, nrfjprog, pyOCD, OpenOCD, probe-rs or nrfutil
  on `PATH`. A present serial node is not permission to open it.

## Safety cautions

- No device operation is implied by any build, analysis or source-admission
  result; offline tests and compilation are software evidence only.
- Keep the left temple on stock `2.2.6.10` unless explicitly authorized.
- Never allowlist unexpected case/PMIC register states to get past a gate.
- Preserve the four case serial windows (`0x0803F000..0x0803F00F`,
  `0x0803F800..0x0803F807`, `0x0807F000..0x0807F00F`,
  `0x0807F800..0x0807F807`) before any case write; the raw case image is not a
  whole-flash replacement.
- The Ambiq secure bootloader (`0x00400000..0x00410000`) and the update-flag
  record (`0x007FE000`) are protected and must not be written.
- A future qualification run must bind the target to the authorized identity,
  record the exact artifact and readback, and keep capability-specific captures
  (BLE/controller traces, paired-temple behavior, display, audio, filesystem
  persistence/power loss, sensor timing, stack high-water marks, WCET).
