# Reference cross-check notes (for firmware sim testing)

Sources (read-only):
- even-realities/everything-evenhub, `plugins/everything-evenhub/skills/{sdk-reference,glasses-ui,handle-input}` (GitHub, main).
- ~/Repo/SybilSight, `Vendor/SybilSightBluetoothSDK/ios/Source/sgcs/G2.swift`.
- g2/src (read-only), stock 2.2.6.10 addresses.

## 1. Why rebuild / text update often give "no reply"
- The parser (a-26 `evenhub_data_parser.c`) answers **only failures** itself: rebuild with a bad which / >1 capture / app not running → 8/7, and text with the app not running → 6/9. On the success path it forwards the raw packet with `audio_uart_master_display_refresh(EVENHUB_APP_ID, …)` and returns 0, sending nothing.
- The success reply comes later from the **UI thread** handler (a-14 `evenhub_ui_page.c`):
  - rebuild: decode → `container_list_rebuild_from_pb 0x493ab6` → build widgets → `evenhub_send_reply(8, seq, 8, 6)`.
  - text: find the container by ID → copy ≤0x7ff bytes → `evenhub_send_reply(6, seq, 10, 8)`. If no container has that ID, 6/9.
- The reply also needs `Thread_MsgPbTxByBle`, which goes out only over the master's phone link.
- So a sim gets no reply if it has any of these gaps:
  - it doesn't run the display-refresh → UI event pipeline (the `master_display_refresh` body is not reconstructed in g2/src);
  - it runs only one arm or role;
  - the EvenHub app isn't "running" (`quicklist_refresh_enabled`).
- Heartbeat (cmd 12) and audio control (cmd 15) get **no reply at all** when the app isn't running. Every reply echoes the request magicRandom.
- SDK change: `softAcks` (default on). rebuildPage, updateText, heartbeat and audio now resolve on timeout and call `onWarning`. An explicit failure code still throws. Pass `softAcks: false` for strict sim tests.
- Docs: "mismatched containerID/containerName silently fails". In firmware the lookup is by ID only, and a missing ID replies 6/9.

## 2. How touch reaches list containers
1. Create/rebuild binds the single `isEventCapture` container (`evenhub_bind_event_container 0x4942a4`) with `evenhub_list_event_inject_adapter 0x495f9a` (text: `0x4961e4`).
2. A touchpad gesture on the **master** goes to the bound adapter. The slave role returns 0, and input is ignored while the list/text scroll animation runs (handle+0x57c / +0x13).
   - List: up, down and click pass through.
   - Text: only up and down.
3. The adapter calls `evenhub_send_input_event 0x4da382` → PrivateDeviceEvent (cmd 0x0B, tag 16) to both arms.
4. The UI handler on each arm finds the container by ID and calls `common_list_container_inject_event 0x4de354`: scroll-up = 0 and scroll-down = 1 move focus, click = 2.
5. The list widget's select callback `common_list_event_callback 0x4949c0` sends `SendDeviceEvent.listEvent` {containerID, name, index}. Text edges send textEvent with 1 = top, 2 = bottom (`0x494a78`).

Phone-visible result (matches the docs):
- Swipes on a list move focus internally and send **no phone event**.
- A click sends listEvent with `currentSelectItemIndex`. Index 0 and CLICK (0) are omitted by proto3, so decode them as 0.
- A double press is a sysEvent (3).
- On a text capture, a click is a sysEvent, not a textEvent.

To test this in the sim, inject the gesture through the bound adapter on the master, not straight into the widget, or the events skip the cmd 0x0B relay.

## 3. Settings-write formats (service 0x09)
- Root: G2SettingPackage {1 commandId, 2 magicRandom u32, …}. commandId values: 1 = write, 2 = request, 3 = device→app, 4 = respond. The firmware only requires commandId != 0 and **drops a repeated magic** (`0x49b198`).
- **Write:** `{1:1, 2:m, 3: DeviceReceiveInfoFromAPP{ <tag>: {...} }}`. The firmware handles it as kind 3: dispatch `0x466abc` on the inner tag, then `setting_respond_to_app 0x49b900` replies `{1:1, 2:m}`, right arm only.

| Inner tag | Message | Fields |
|---|---|---|
| 1 | Brightness | `{1 type (1 = auto, 2 = level), 2 value}`, or calibration `{3 left, 4 right}` (0..10) |
| 2 | Y coordinate (screen height) | `{1 level 0..12}` |
| 3 | X coordinate (screen depth) | `{1 level 0..2}` |
| 4 | Head-up | `{1 switch, 2 angle 0..60}`. Send both fields in one message. |
| 6 | Silent mode | `{1 switch}` |

  Other inner tags (5, 8–12) are dispatched but their formats aren't verified. Send every field: per SybilSight's hardware tests, an omitted field is applied as 0.
- **Request:** `{1:2, 2:m, 4:{1:1}}`, handled as kind 4. The reply is the full status `{1:2, 2:m, 4:{…, 5 left version, 6 right version}}` (`0x49b4da`).
- SDK: `encodeSettingWrite`, `connection.writeSetting()`.

## 4. Other cross-check results
- Container property ranges (from SybilSight): borderWidth 0–5, borderColor 0–15, borderRadius 0–10, padding 0–32, and geometry inside 576×288. One violation fails the whole page with code 1. The SDK now validates these.
- zOrderIndex is text tag 13 and image tag 7 (SDK 0.0.12). It is all-or-nothing per page, unique, and larger means in front. The SDK validates this and sends 0 explicitly.
- Text limits: create ≤999 bytes and upgrade ≤1999 bytes (firmware char[1000]/char[2000]); the docs say 1000 and 2000 characters. Note this is a byte count, not a character count.
- Event capture: the docs require exactly one capture container. The firmware rejects ≥2 but accepts 0, so the SDK enforces ≤1.
- Menus: the in-EvenHub `menu` field (create tag 6 / rebuild tag 5) exists only in 2.3, and the SDK rejects it on 2.2. The dashboard app menu SybilSight uses is a separate service, id 3 (`menu.proto`, 5–10 items, not modelled here). `widgetId` (create tag 5) links a page to a menu appId and enables cmd 17 menu-start events.
- Create can only be sent once per app session; use rebuild after that (docs). The firmware starts the app only if it isn't already running.
