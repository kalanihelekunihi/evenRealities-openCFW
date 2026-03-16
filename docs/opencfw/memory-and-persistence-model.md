# Memory and Persistence Model

This document records the clean-room view of Apollo internal flash, SRAM, external flash, LittleFS namespaces, OTA staging, and the persistent objects that `openCFW` must preserve first.

## Region Matrix

| Region | State | Address / Medium | Known Use | Main Gaps |
|---|---|---|---|---|
| Apollo bootloader flash | Identified | `0x00410000` | Boot decision, LittleFS mount, OTA install, VTOR handoff | Exact metadata and rollback layout |
| Apollo main-app flash | Identified | `0x00438000-0x0074299F` | Main runtime image, vector table, protocol/UI/audio/settings code | Exact safe rewrite envelope around vendor metadata |
| Apollo SRAM | Identified | `0x20000000-0x2007FFFF` | Runtime RAM, task objects, queues, descriptor roots | Full data/BSS allocation map |
| Startup stack / guard markers | Identified | `SP=0x2007FB00`, `MSPLIM/PSPLIM=0x2007D000` | Reset-entry stack and guard setup | Final stack-budget ownership per task |
| Runtime dispatch descriptor | Identified | `0x20003DB4` | Startup callback seed and runtime control object | Full fan-out field semantics |
| External QSPI flash | Identified medium, partial layout | MX25U25643G, 32 MB | LittleFS persistence plus asset/XIP storage | Exact partition split and placement policy |
| External XIP window | Partial | `0x80000000-0x81FFFFFF` | Font and generic external-flash writes | Exact region boundaries and headers |

## Identified Internal Memory Model

### Internal flash

- Bootloader lives at `0x00410000`.
- Main app is loaded at `0x00438000`.
- The bootloader handoff is fixed around `SCB->VTOR = 0x00438000`, `MSP = *(0x00438000)`, then branch to `*(0x00438004)`.
- The current v2.0.7.16 main image executes through roughly `0x0074299F`.

### SRAM anchors

- Apollo SRAM range is `0x20000000-0x2007FFFF`.
- Both bootloader and app vector tables use `0x2007FB00` as the initial stack pointer.
- Reset code programs `MSPLIM` and `PSPLIM` to `0x2007D000`.
- Startup/runtime handoff pivots through the descriptor object rooted at `0x20003DB4`.

These anchors are strong enough to drive the first `openCFW` linker and startup assumptions even though the full RAM allocation map is still incomplete.

## Identified Persistent Namespaces

The bootloader and runtime both treat these namespaces as real storage contracts:

| Path / Namespace | State | Owner | Known Purpose |
|---|---|---|---|
| `/firmware/` | Identified | Main app + bootloader mount path | Staging area for subordinate firmware payloads |
| `/ota/` | Identified | Bootloader | Main app and bootloader OTA staging |
| `/user/` | Identified | Main app | User-facing persistent objects |
| `/log/` | Identified | Main app | Diagnostics and crash artifacts |
| `/ota/s200_firmware_ota.bin` | Identified | Bootloader consumer | Main app install image |
| `/ota/s200_bootloader.bin` | Identified | Bootloader consumer | Bootloader self-update image |
| `/firmware/ble_em9305.bin` | Identified | Main app consumer | EM9305 patch staging |
| `/firmware/touch.bin` | Identified | Main app consumer | Touch-controller update staging |
| `/firmware/codec.bin` | Identified | Main app consumer | Codec update staging |
| `/firmware/box.bin` | Identified | Main app consumer | Case update staging |
| `user/notify_whitelist.json` | Identified | Main app | Notification whitelist payload |
| `/log/compress_log_*.bin` | Identified | Main app | Rotating compressed logs |
| `/log/hardfault.txt` | Identified | Main app | Crash dump / hardfault log |

Additional implementation-visible namespace facts:

- Bootloader startup strings show it mounts LittleFS and creates `/firmware`, `/ota`, `/user`, and `/log` if missing.
- Logger operations are guarded to the `/log/` namespace.
- `hardfault.txt` has an observed 100 KB rotation limit in the recovered firmware notes.
- System-level documentation exposes eye-qualified views such as `L:/log/...` and `R:/log/...` for paired-glass access patterns.

## OTA and Persistence Ownership

### Bootloader-owned persistence

- Reads `otaFlag` and boot metadata before deciding whether to program a new image.
- Consumes `/ota/s200_firmware_ota.bin` and `/ota/s200_bootloader.bin`.
- Performs CRC check, internal-flash programming, verify, and handoff.

### Main-app-owned persistence

- Receives OTA/file transfers over `0xC4/0xC5`.
- Stages subordinate images under `/firmware/`.
- Owns user/config/log objects such as `notify_whitelist.json` and `/log/*`.
- Tracks per-eye OTA state and relays some status to the peer eye.

## Inferred but Not Fully Closed

| Area | Current Inference | Why It Is Not Fully Closed |
|---|---|---|
| LittleFS vs XIP split | The 32 MB MX25U25643G hosts both a file-backed area and an XIP-style asset region | Exact partition boundary is not yet instruction-closed |
| Font and external-flash asset placement | OTA types `FONT` and `EXTERNAL_FLASH` target the XIP address space, with fonts hinted at `0x80100000+` | Exact page layout and packing headers are still unresolved |
| FlashDB / KV persistence | The runtime includes `flashDB` and transaction-log markers beyond plain files | Exact key schema, migration rules, and on-flash layout are not recovered |
| Cross-eye persistence policy | Some OTA status and settings/config state are synchronized or relayed across eyes | Exact mirroring rules per namespace are incomplete |
| Boot counters and flags | `otaFlag` and `boot_count` are persistent control values rather than transient RAM-only state | Their exact storage location and structure remain open |

## Unidentified / Blocked Areas

- Exact external-flash partition map.
- Exact `otaFlag`, `boot_count`, and boot metadata layout.
- Full RAM data/BSS map and per-task stack sizing.
- FlashDB key/value schema and transaction-log format.
- Log compression format beyond the known filenames and hardfault rotation behavior.
- Exact header/layout rules for font and generic XIP asset updates.

## Clean-Room Rules

- Preserve path compatibility for `/firmware`, `/ota`, `/user`, `/log`, `user/notify_whitelist.json`, and `/log/hardfault.txt` in the first implementation.
- Keep bootloader staging and runtime-owned file namespaces separate in code.
- Make the external-flash partition plan configurable until the LittleFS/XIP split closes further.
- Treat eye-qualified namespace views as compatibility behavior, not evidence that the two glasses share one physical flash device.

## Source Documents

- `../firmware/s200-firmware-ota.md`
- `../firmware/s200-bootloader.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/ota-protocol.md`
- `../firmware/modules/logger.md`
- `../firmware/firmware-reverse-engineering.md`
- `../protocols/notification.md`
- `../devices/g2-glasses.md`
