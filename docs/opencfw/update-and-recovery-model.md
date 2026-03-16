# Update and Recovery Model

This document is the clean-room update and recovery model for `openCFW`. It separates G2 runtime staging, bootloader install, subordinate-component updates, case-led recovery behavior, and the ring's independent DFU path.

## Domain Matrix

| Domain | State | Transport / Trigger | Staging / Installer | Identified Today | Main Gaps |
|---|---|---|---|---|---|
| G2 phone-to-runtime OTA staging | Identified | BLE file lane `0x7401/0x7402` | Runtime stages to `/ota` and `/firmware` | Generic FILE_CHECK lifecycle, prerequisites, restart path | Exact native OTA-specific session bytes |
| G2 bootloader install | Identified with bounded unknowns | Reboot after OTA flag | Bootloader programs internal flash and hands off to app | CRC/program/verify/install path, VTOR jump | Exact metadata and rollback layout |
| G2 subordinate component updates | Identified | Runtime-owned local transports | EM9305/HCI, codec/TinyFrame, touch/I2C, case/UART relay | Apply interfaces and handler order | Exact per-component retry/error policy |
| Case-driven glasses update | Partial | Case UART relay | Box firmware banked OTA flow | Version check, chunk fetch, CRC check, bank swap strings | Full box OTA grammar and exact bank metadata |
| Ring DFU | Identified transport, blocked runtime | FE59 + SMP/MCUmgr | Phone-to-ring direct Nordic DFU | Separate from G2 EVENOTA, MCUboot slot model; Nordic bootloader/SoftDevice artifacts are present | Standalone ring application runtime image and package details |

## Identified G2 Update Path

### Runtime staging over BLE

- OTA transfer uses the file lane (`0x7401` write, `0x7402` notify).
- The reusable staging lifecycle is `FILE_CHECK -> START -> DATA -> END`.
- Runtime staging writes main app and bootloader artifacts under `/ota/`.
- Runtime staging writes subordinate artifacts under `/firmware/`.
- Update prerequisites are strong enough to preserve in `openCFW`:
  - device connected,
  - both eyes at or above 50% battery,
  - device on charger.

### Bootloader install ownership

- The runtime does not directly overwrite the running main app in the identified flow.
- Instead, it stages files, sets an OTA boot flag, and reboots.
- The bootloader then performs:
  1. OTA flag check
  2. image CRC validation
  3. internal-flash programming
  4. flash-content verification
  5. app handoff via VTOR/MSP/reset vector

This split is implementation-relevant: `openCFW` needs a coordinator that can stage and reboot without assuming install ownership belongs to the runtime task graph.

## Identified Component Sequencing

Two different ordering concepts are now clearly separated:

### Package distribution order inside EVENOTA

`codec -> BLE -> touch -> box -> bootloader -> main`

### Runtime subordinate apply order recovered from the Apollo main image

`box -> EM9305 -> touch -> codec`

Bootloader and main-app images are handled by the Apollo internal-flash install path rather than the subordinate transport handlers.

Clean-room implication:

- `openCFW` must not assume the order of entries in the distribution package is the same as the order the runtime applies subordinate updates.
- The update coordinator should model package parsing, staging, and apply sequencing as separate phases.

## Partial but Operationally Relevant Paths

### Native OTA-specific session

A richer OTA session exists beyond the reusable generic file client:

- `START`
- `INFORMATION`
- `FILE`
- `RESULT_CHECK`
- `NOTIFY`

Recovered facts:

- OTA file payloads use a 5-byte per-packet header before the data payload.
- OTA file payloads are enforced at 1000 bytes per packet in the native path.
- `RESULT_CHECK` and restart responses are real parts of the firmware vocabulary.
- OTA status is tracked per eye and can be reported as coming from self or peer.

What remains open is the exact byte-level command encoding, especially for the 5-byte file header and the final notify/restart semantics.

### Case-driven glasses update

Case firmware strings show a separate, banked update path for glasses:

- `firmware_check`
- `begin`
- `file_get`
- `result_check`

Known behavior:

- battery must be above 50%,
- timeout is 3 minutes,
- bank swap strings are explicit (`Swap bank(2->1) & RESET`, `Swap bank(1->2) & RESET`).

This is a real recovery-related boundary, but not yet closed strongly enough to implement as anything more than a compatibility relay.

### Ring DFU boundary

- The ring update path is not part of G2 EVENOTA.
- It uses Nordic buttonless DFU (`FE59`) and SMP/MCUmgr upload.
- MCUboot slot-state concepts such as test/confirm are part of the ring path.
- The G2 glasses do not appear to own ring firmware installation.

## Unidentified / Blocked Areas

- Exact OTA-specific command byte IDs.
- Exact 5-byte OTA file-header layout.
- Exact `otaFlag`, `boot_count`, and boot metadata storage schema.
- Exact retry, backoff, peer-arbitration, and rollback triggers during dual-eye OTA.
- Exact subordinate-component error propagation and recovery policy.
- Full case OTA wire grammar and bank metadata.
- Standalone R1 application runtime image and complete ring package contract beyond the already present Nordic bootloader/SoftDevice artifacts.

## Clean-Room Rules

- Keep runtime staging and bootloader install as separate modules.
- Model package parsing order independently from subordinate apply order.
- Keep the generic file-transfer client and the native OTA-specific session as distinct code paths until the native header closes further.
- Treat case-led update and ring DFU as separate compatibility domains, not extensions of one shared G2 updater.

## Source Documents

- `../firmware/ota-protocol.md`
- `../firmware/firmware-files.md`
- `../firmware/firmware-updates.md`
- `../firmware/s200-bootloader.md`
- `../firmware/s200-firmware-ota.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/box-case-mcu.md`
- `../devices/r1-ring.md`
