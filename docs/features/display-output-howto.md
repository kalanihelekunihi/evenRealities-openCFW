# Display Output How-To

How to get user-visible content onto the Even Realities G2 displays, based on the current `openCFW` reverse-engineering work and the working `EvenG2Shortcuts` sender implementations.

This document focuses on:

- Teleprompter
- Images
- Notifications
- General app/community-app data

It also separates what is confirmed by firmware source from what is inferred from host behavior.

## 1. Core Model

The G2 does not appear to accept a generic full-screen framebuffer stream for normal app features. The dominant model is:

1. Authenticate over the control lane.
2. Wake or initialize the display subsystem.
3. Send high-level feature data:
   - teleprompter pages
   - EvenHub page/container layouts
   - notification JSON over the file lane
4. Let firmware render the final display locally.

This matches:

- `openCFW/docs/transport-and-packet-formats.md`
- `openCFW/docs/feature-and-presentation-model.md`
- `docs/features/display-pipeline.md`

The cleanest current summary is in `docs/features/display-pipeline.md`: the phone sends layout, text, config, and small image fragments; the Apollo510b firmware renders the display on-device with LVGL, FreeType, and NemaGFX.

## 2. BLE Lanes

All of the relevant traffic sits on three characteristic pairs:

| Lane | Write | Notify | Purpose |
|---|---|---|---|
| Control | `0x5401` | `0x5402` | Auth, control services, protobuf-style feature traffic |
| Display | `0x6401` | `0x6402` | Display wake/config, display-facing feature traffic, display feedback |
| File | `0x7401` | `0x7402` | File transfer, notifications, OTA/export paths |

Base UUID family:

`00002760-08c2-11e1-9073-0e8ac72e{suffix}`

## 3. Common Packet Envelope

For the normal G2 transport, the packet envelope is:

| Offset | Size | Field | Meaning |
|---|---:|---|---|
| `0x00` | 1 | magic | `0xAA` |
| `0x01` | 1 | type | `0x21` command, `0x12` response |
| `0x02` | 1 | seq | per-endpoint sequence |
| `0x03` | 1 | len | payload length + CRC bytes |
| `0x04` | 1 | packetTotalNum | fragment count |
| `0x05` | 1 | packetSerialNum | fragment index |
| `0x06` | 1 | serviceHi | service ID high byte |
| `0x07` | 1 | serviceLo | service ID low byte |
| `0x08..` | var | payload | protobuf or lane-specific payload |
| trailer | 2 | CRC16 | CRC-16/CCITT over payload only, little-endian |

This is confirmed in `openCFW/docs/transport-and-packet-formats.md` and is the same shape used by the Swift senders in `Sources/EvenG2Shortcuts`.

## 4. The Concrete Protocol Map

The table below is the current best operator-facing map for getting content onto the displays.

| Feature | Main Service | Lane | Minimum Bring-Up | Content Model | Main Responses | Best Host Reference |
|---|---|---|---|---|---|---|
| Teleprompter | `0x06-20` | Control/EUS | auth, then display config | stateful page/session protocol | `0x06-00` ACK, `0x06-01` progress | `G2TeleprompterSender.swift` |
| EvenHub text/image/apps | `0xE0-20` | Display/content path | auth, display wake | page/container layout engine | EvenHub status responses, async reflash path | `G2EvenHubSender.swift` |
| Notifications | `0x02-20` plus `0xC4/0xC5` | Control + File | auth, display wake, display config | JSON file transfer + internal notification dispatch | file-lane status words, internal ANCC display dispatch | `G2NotificationSender.swift`, `G2FileTransferClient.swift` |
| Community apps | `0xE0-20` | Display/content path | auth, display wake | EvenHub app state rendered as pages/containers | same as EvenHub | `G2EvenHubApps.swift`, `G2EvenHubRenderCoordinator.swift` |

## 5. Display Bring-Up Rules

### 5.1 Standard render-family path

For most display features, the stable activation pattern is:

1. `DisplayWake` on `0x04-20`
2. `DisplayConfig` on `0x0E-20`
3. feature content on its own service

This is explicitly documented in:

- `docs/features/display-pipeline.md`
- `openCFW/docs/feature-and-presentation-model.md`

### 5.2 EvenHub exception

EvenHub is different. It uses its own page/container layout system and does not need the generic `0x0E-20` display-config step. The working host path is:

1. auth
2. display wake
3. EvenHub startup/rebuild/content commands on `0xE0-20`

This matches:

- `docs/features/eventhub.md`
- `openCFW/src/platform/apollo510b/main_firmware/app/gui/EvenHub/evenhub_data_parser.c`
- `Sources/EvenG2Shortcuts/G2EvenHubSender.swift`

### 5.3 Teleprompter exception

Teleprompter is also special. The current working sender does not call display wake first. It sends:

1. auth
2. display config
3. teleprompter init/content packets

The firmware-side code clearly starts a display session for teleprompter through `AsyncRequestDisplayStartUp(0x06, ...)` and later uses `RequestDisplayReflash(0x06, ...)`, but the explicit requirement for a separate `0x04-20` wake is not proven inside the teleprompter path itself.

Relevant files:

- `openCFW/src/platform/apollo510b/main_firmware/app/gui/teleprompt/teleprompt.c`
- `Sources/EvenG2Shortcuts/G2TeleprompterSender.swift`

## 6. Teleprompter

### 6.1 Main service and role

- Service: `0x06-20`
- Transport: normal G2 packet envelope over the control/EUS path
- Rendering model: stateful teleprompter session, not stateless text blits

### 6.2 Working host sequence

The current working sequence is:

1. auth
2. display config `0x0E-20`
3. teleprompter init type `1`
4. content pages `0..9` as type `3`
5. mid-stream marker type `255`
6. content pages `10..11`
7. sync trigger on auth-control `0x80-00` type `14`
8. remaining content pages

This matches `docs/features/teleprompter.md` and the implementation in `Sources/EvenG2Shortcuts/G2TeleprompterSender.swift`.

### 6.3 Firmware behavior

`openCFW` confirms the display/session behavior:

- Teleprompter start goes through `AsyncRequestDisplayStartUp(0x06, ..., 500)` when idle.
- Display refreshes go through `RequestDisplayReflash(0x06, ...)`.
- Close uses `RequestDisplayStop(0x06, ...)`.
- The phone must keep heartbeat traffic flowing; a timeout of roughly 20 seconds forces heartbeat-fail behavior.

Confirmed in:

- `openCFW/src/platform/apollo510b/main_firmware/app/gui/teleprompt/teleprompt.c`
- `openCFW/src/platform/apollo510b/main_firmware/app/gui/teleprompt/teleprompt_fsm.c`
- `openCFW/src/platform/apollo510b/main_firmware/app/gui/teleprompt/teleprompt_ui.c`

### 6.4 Content model

The glasses store incoming page data and render once enough data is buffered. The protocol is page-driven:

- page number
- line count
- UTF-8 text block

Practical formatting rules recovered so far:

- about 25 chars per line
- 10 lines per page
- roughly 7 visible lines at once

### 6.5 Responses

Observed reply flow:

- `0x06-00`: per-page ACK, with response type `0xA6` and echoed message ID
- `0x06-01`: rendering progress, with response type `0xA4`

### 6.6 Best current conclusion

If the goal is to show long-form scrolling text, use the teleprompter protocol directly. Do not try to emulate teleprompter by pushing raw image frames.

## 7. Images and General App Output

### 7.1 Use EvenHub

The clearest path for images, text layouts, and “community app” style output is EvenHub:

- Service: `0xE0-20`
- Response family: `0xE0-00`
- Model: page/container composition on the glasses

This is the best fit for:

- text panels
- list UIs
- static or updated images
- app-like layouts

### 7.2 Supported operations

The stable EvenHub operations are:

- `CreateStartUpPageContainer`
- `RebuildPageContainer`
- `TextContainerUpgrade`
- `ImageRawDataUpdate`
- `ShutDownPageContainer`

These are documented in `docs/features/eventhub.md` and implemented in `Sources/EvenG2Shortcuts/G2EvenHubSender.swift`.

### 7.3 Firmware-side constraints

The startup and rebuild path in `evenhub_data_parser.c` validates:

- max 4 containers per page
- max 1 scrollable or event-capture container per page

The image-content path only assembles content for image containers. When the final fragment arrives, firmware emits a private event `0x4C`, which then becomes an async display reflash.

Confirmed in:

- `openCFW/src/platform/apollo510b/main_firmware/app/gui/EvenHub/evenhub_data_parser.c`
- `openCFW/src/platform/apollo510b/main_firmware/app/gui/EvenHub/evenhub_main.c`
- `openCFW/src/platform/apollo510b/main_firmware/app/gui/EvenHub/evenhub_ui.c`

### 7.4 Image transport model

Images are not sent as a screen dump. They are sent as image-container content:

- 4-bit grayscale
- width 20-200
- height 20-100
- sequential fragments for larger payloads

The Swift sender already fragments image updates sequentially in `G2EvenHubSender.updateImageRawData(...)`.

### 7.5 Community apps

The iOS “community apps” in this repo are not installed onto the glasses as native binaries. They are modeled as EvenHub applications whose state is rendered remotely into EvenHub pages and containers.

Relevant host files:

- `Sources/EvenG2Shortcuts/G2EvenHubApps.swift`
- `Sources/EvenG2Shortcuts/G2EvenHubRenderCoordinator.swift`
- `Sources/EvenG2Shortcuts/EvenHubAppsView.swift`

Best current conclusion:

- for app-like display output, use EvenHub
- for a single image, create an image container then send `ImageRawDataUpdate`
- for dynamic text/list UIs, rebuild or upgrade containers rather than trying to stream pixels

## 8. Notifications

### 8.1 The important split

Notifications are not just a single protobuf command on `0x02-20`.

There are at least three layers involved:

1. notification control and whitelist state on `0x02-20`
2. notification payload transfer on the file lane `0xC4/0xC5`
3. display dispatch inside the notification/ANCC subsystem

### 8.2 Working host sequence

The current sender path is:

1. auth
2. display wake `0x04-20`
3. display config `0x0E-20`
4. file transfer on `0x7401`:
   - `FILE_CHECK` on `0xC4-00`
   - `START` on `0xC4-00`
   - `DATA` on `0xC5-00`
   - `END` on `0xC4-00`
5. heartbeat or sync on the control lane

This is implemented in:

- `Sources/EvenG2Shortcuts/G2NotificationSender.swift`
- `Sources/EvenG2Shortcuts/G2FileTransferClient.swift`

### 8.3 FILE_CHECK header

The reusable file-transfer contract is:

- mode: `0x00000100`
- size: `len(data) * 256`
- checksum: `(CRC32C << 8) & 0xFFFFFFFF`
- extra byte: `CRC32C >> 24`
- filename: 80-byte null-padded UTF-8 string

This 93-byte header is now consistent across:

- `openCFW/docs/transport-and-packet-formats.md`
- `docs/protocols/notification.md`
- `Sources/EvenG2Shortcuts/G2FileTransferClient.swift`

### 8.4 JSON payload

The payload is JSON, and the root key is still:

`"android_notification"`

That name is used even when the host is an iOS app. The payload includes fields such as:

- `msg_id`
- `action`
- `app_identifier`
- `title`
- `subtitle`
- `message`
- `time_s`
- `date`
- `display_name`

The usual filename is:

`user/notify_whitelist.json`

### 8.5 What `0x02-20` actually does

The `pb_service_notification.c` path is primarily settings/control state, not the full notification-body rendering path. It stores values like:

- notification enabled
- display mode
- priority
- extra flags
- whitelist enabled/disabled state

So the right mental model is:

- `0x02-20` configures notification behavior
- the file lane carries the actual notification payload

### 8.6 What actually triggers display

The strongest current firmware-side evidence is that notification display dispatch happens in the ANCC-related path, not directly in `PB_RxNotifCtrl`.

In `service_ancc.c`, valid notifications eventually trigger either:

- `RequestDisplayReflash(...)` if the codec is already ready
- `RequestDisplayStartUp(...)` for cold/not-ready cases

That means notification display is coupled to internal notification handling, not just to receipt of the file transfer.

### 8.7 Best current conclusion

If you want notifications to appear on the glasses, the practical path is:

1. ensure the relevant notification settings and whitelist behavior are acceptable
2. send the JSON notification file using the `FILE_CHECK -> START -> DATA -> END` sequence
3. keep the control-side heartbeat/sync behavior intact

## 9. General App Data and the iOS Community Apps

For “general app data such as the iOS community apps,” the best current answer is:

- use EvenHub as the display runtime
- treat the phone app as the logic owner
- send page/container descriptions and incremental updates to the glasses

In other words, the glasses are acting as a remote presentation device with firmware-managed UI primitives, not as a native app platform for arbitrary iOS app binaries.

Practical mapping:

- long-form reading text: teleprompter
- dashboard or app-like UI: EvenHub
- small images/icons: EvenHub image container
- OS-style popup alerts: notification path

## 10. Display Confirmation

Two useful signals exist when verifying display output:

### 10.1 `0x6402` activity stream

`docs/features/display-pipeline.md` and repo instrumentation indicate that `0x6402` emits a roughly 205-byte stream at about 20 Hz when the display is physically active. This is the best hardware-facing “display is on” signal.

### 10.2 Compact mode notifications

Feature-mode notifications correlate with:

- `0` idle
- `6` render
- `11` conversate
- `16` teleprompter

This is useful as a software-facing confirmation that the intended feature path became active.

## 11. Secondary / Non-Primary Path: NUS

There is also a Nordic UART Service side channel in `Sources/EvenG2Shortcuts/G2Protocol.swift`. It appears useful for some raw or experimental operations such as text or BMP display, but it does not currently look like the main path for Teleprompter, EvenHub/community-app content, or notifications.

Best current guidance: treat NUS as auxiliary or experimental, not as the primary solution for the display tasks covered here.

## 12. Confirmed vs Inferred vs Unknown

### 12.1 Confirmed

- The three main BLE lanes are `0x54xx`, `0x64xx`, and `0x74xx`.
- The common G2 packet envelope is stable and uses CRC16 over payload only.
- Teleprompter is a dedicated service on `0x06-20` with a session/page model.
- EvenHub is a dedicated page/container layout system on `0xE0-20`.
- Notifications use the file lane with `0xC4/0xC5` and JSON payloads.
- Notification control and whitelist state live under `0x02-20`.
- Image updates in EvenHub are fragment-assembled and then trigger a reflash path.
- Community apps in this repo are implemented as EvenHub applications.

### 12.2 Inferred but strong

- The phone-side minimum for teleprompter visibility is: send start/config, answer page needs promptly, keep heartbeat flowing, then send further control commands as needed.
- Notifications likely depend on both payload transfer and the internal notification queue/dispatch state to become visible.
- The practical display abstraction for most custom output is “send high-level structures and let firmware render locally,” not “push raw pixels.”

### 12.3 Still open

- Exact wire-level field ownership for all of `0x0E-20` display config.
- Exact teleprompter type `255` and sync-trigger semantics.
- Full formal schema for all EvenHub container payloads and result codes.
- Exact wire-level EFS mode/type semantics beyond the already-recovered generic file-transfer contract.
- Full `0x6402` stream decoding.
- Exact ownership split among dashboard/widgets/EvenAI around `0x01-20` and `0x07-20`.

## 13. Practical Recommendations

If the goal is to get content onto the G2 displays today, use these routes:

| Goal | Recommended Path |
|---|---|
| Show long reading text | Teleprompter `0x06-20` |
| Show a custom app UI | EvenHub `0xE0-20` |
| Show an image | EvenHub image container + `ImageRawDataUpdate` |
| Show a popup-style notification | notification JSON over `0xC4/0xC5` plus control-side sync |
| Recreate community apps | EvenHub app/runtime model |

The repo already contains working or near-working host implementations for all of those paths under `Sources/EvenG2Shortcuts`.

## 14. Primary Source Files

### Repo docs

- `docs/features/display-pipeline.md`
- `docs/features/teleprompter.md`
- `docs/features/eventhub.md`
- `docs/protocols/notification.md`
- `openCFW/docs/transport-and-packet-formats.md`
- `openCFW/docs/service-map.md`
- `openCFW/docs/feature-and-presentation-model.md`

### Host-side senders

- `Sources/EvenG2Shortcuts/G2TeleprompterSender.swift`
- `Sources/EvenG2Shortcuts/G2EvenHubSender.swift`
- `Sources/EvenG2Shortcuts/G2NotificationSender.swift`
- `Sources/EvenG2Shortcuts/G2FileTransferClient.swift`
- `Sources/EvenG2Shortcuts/G2EvenHubApps.swift`
- `Sources/EvenG2Shortcuts/G2EvenHubRenderCoordinator.swift`
- `Sources/EvenG2Shortcuts/G2Protocol.swift`

### `openCFW` firmware-side evidence

- `openCFW/src/platform/apollo510b/main_firmware/app/gui/teleprompt/teleprompt.c`
- `openCFW/src/platform/apollo510b/main_firmware/app/gui/teleprompt/teleprompt_fsm.c`
- `openCFW/src/platform/apollo510b/main_firmware/app/gui/teleprompt/teleprompt_ui.c`
- `openCFW/src/platform/apollo510b/main_firmware/app/gui/EvenHub/evenhub_data_parser.c`
- `openCFW/src/platform/apollo510b/main_firmware/app/gui/EvenHub/evenhub_main.c`
- `openCFW/src/platform/apollo510b/main_firmware/app/gui/EvenHub/evenhub_ui.c`
- `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_service_notification.c`
- `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/efs_service/efs_service.c`
- `openCFW/src/platform/apollo510b/main_firmware/platform/service/message_notify/service_ancc.c`
