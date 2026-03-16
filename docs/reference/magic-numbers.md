# Inferred Magic Numbers (G2 Protocol)

This page tracks numeric literals and classifies confidence for each inferred meaning.

## Confidence rubric

- **High**: Observed in multiple flows/captures and behavior is confirmed.
- **Medium**: Consistent with captures/docs but not fully behavior-proven.
- **Low**: Plausible hypothesis or single-context observation; needs more captures.

## Transport and framing

| Value | Meaning | Confidence |
|---|---|---|
| `0xAA` | Packet magic byte | High |
| `0x21` | Command direction (phone -> glasses) | High |
| `0x12` | Response direction (glasses -> phone) | High |
| `8` | Header byte count | High |
| `2` | CRC trailer byte count | High |
| `253` | Max payload bytes per packet (`len` is 1 byte and includes CRC bytes) | High |
| `255` | Max fragment count (`totalPackets` is 1 byte) | High |
| `0xFFFF` | CRC16/CCITT init | High |
| `0x1021` | CRC16/CCITT polynomial | High |
| `0x1EDC6F41` | CRC32C polynomial (Castagnoli), used to generate 256-entry lookup table for FILE_CHECK | High |
| `0x7F` / `0x80` | Protobuf varint boundary and continuation bit | High |

## BLE characteristic endpoints

| Value | Meaning | Confidence |
|---|---|---|
| `0x0001` | Base channel write characteristic | High — probe 2026-02-27 |
| `0x0002` | Base channel notify characteristic (subscribed in connectEye) | High — probe 2026-02-27 |
| `0x1001` | Unknown characteristic (possibly OTA service) | Medium — RE 2026-03-01 |
| `0x5401` | Control channel write characteristic (BleG2PsType=0) | High |
| `0x5402` | Control channel notify characteristic | High |
| `0x5450` | Control alternate characteristic (role unknown) | Medium — RE 2026-03-01 |
| `0x6401` | Display channel write characteristic (204-byte binary commands) | High — probe 2026-02-27 |
| `0x6402` | Display channel notify characteristic — continuous encrypted sensor stream (~18.8 Hz, 205 bytes/pkt) | High — testAll 2026-03-02 (1333 pkts @ ~53ms) |
| `0x6450` | Display alternate characteristic (role unknown) | Medium — RE 2026-03-01 |
| `0x7401` | File channel write characteristic (BleG2PsType=1) | High |
| `0x7402` | File channel notify characteristic | High |
| `0x7450` | File alternate characteristic (role unknown) | Medium — RE 2026-03-01 |
| `FE59` | Nordic DFU service UUID (advertised during firmware update mode) | High |

## Protobuf wire-format field tags

These bytes encode `(field_number << 3 | wire_type)` per the protobuf spec. They appear extensively in protocol payloads.

| Value | Encoding | Confidence |
|---|---|---|
| `0x08` | Field 1, varint (wire type 0) | High |
| `0x10` | Field 2, varint | High |
| `0x18` | Field 3, varint | High |
| `0x20` | Field 4, varint | High |
| `0x28` | Field 5, varint | High |
| `0x30` | Field 6, varint | High |
| `0x38` | Field 7, varint | High |
| `0x40` | Field 8, varint | High |
| `0x48` | Field 9, varint | High |
| `0x12` | Field 2, length-delimited (wire type 2) | High |
| `0x1A` | Field 3, length-delimited | High |
| `0x22` | Field 4, length-delimited | High |
| `0x2A` | Field 5, length-delimited | High |
| `0x3A` | Field 7, length-delimited | High |
| `0x6A` | Field 13, length-delimited | High |
| `0x82 0x08` | Field 128, length-delimited (multi-byte varint tag) | High |
| `0x8000` | CRC16 sign bit test mask | High |

## Service IDs and low-byte semantics

| Value | Meaning | Confidence |
|---|---|---|
| `0x80-00`, `0x80-20` | Auth control/data services | High |
| `0x06-20` | Teleprompter service | High |
| `0x0E-20` | Display-config service | High |
| `0x07-20`, `0x07-00` | Even AI request/response services | High |
| `0xC4-00`, `0xC5-00` | File command/data services | High |
| `0x06-01` | Teleprompter rendering progress (type=164, field10=pages rendered) | High |
| `0x09-01` | Device info response (nested format, data in field4) | High |
| Low-byte `0x00` / `0x20` / `0x01` | Control-or-response / request-data / typed-response | High |

## Auth service (`0x80-00` / `0x80-20`)

| Value | Meaning | Confidence |
|---|---|---|
| Type `0x04` | Capability query | High |
| Type `0x05` | Capability response-request | High |
| Type `0x80` | Time-sync | High |
| Msg IDs `0x0C..0x13` | Full 7-packet auth progression | High |
| Msg IDs `0x0D..0x0F` | Fast 3-packet auth progression | High |
| `E8 FF FF FF FF FF FF FF FF 01` | Time-sync transaction sentinel (int64 -24, NOT sint64; hardcoded handshake marker, value likely arbitrary) | High |
| Sync block key `0x82 0x08` | Field 128 length-delimited block | High |
| Sync block length `0x11` | Current observed time-sync block length | High |
| Capability mode `0x02` | Fast auth (3-packet) mode flag | High |
| Capability mode `0x01` | Final auth (7-packet) mode flag | High |

## Notification file transfer (`0xC4-00` / `0xC5-00`)

| Value | Meaning | Confidence |
|---|---|---|
| `0x100` | FILE_CHECK mode | High |
| `size = len(json) * 256` | Scaled size field | High |
| `checksum = (crc32c << 8)` | Lower 24 bits placed in 32-bit checksum field | High |
| `extra = crc32c >> 24` | CRC32C high byte | High |
| `80` | Fixed filename field width | High |
| `user/notify_whitelist.json` | Target file path on glasses | High |
| START payload `0x01` | Start transfer command | High |
| END payload `0x02` | End transfer command | High |
| `234` | Known safe single-packet JSON data ceiling | High |
| Sequence IDs `0x10`, `0x49`, `0xDA` | Working session sequence IDs (likely session-local, not opcodes) | Medium |
| `msg_id = 10000 + (ts % 10000)` | App-side notification ID generation strategy | Medium |
| `action = 0` | “show notification” action code | Medium |

### File transfer ACK responses (glasses → phone)

File transfer ACKs arrive on the **file channel** (0x7402), not the control channel. They use a simple **non-protobuf** 2-byte little-endian status word — distinct from all other G2 protocol responses which use protobuf encoding.

| Svc | Status Word | Meaning | Confidence |
|---|---|---|---|
| `0xC4-00` | `0x0000` | File opened — ready to receive data | High — capture 20260301-1-testAll.txt |
| `0xC5-00` | `0x0100` | Data chunk received (chunk 1) | High — capture 20260301-1-testAll.txt |
| `0xC4-00` | `0x0200` | Transfer complete | High — capture 20260301-1-testAll.txt |

**Full file transfer sequence** (confirmed):
1. TX `0xC4-00`: File init header (103 bytes, path + size + CRC32C)
2. RX `0xC4-00`: Open ACK `0x0000` (~90ms)
3. TX `0xC4-00`: Start transfer `0x01`
4. TX `0xC5-00`: File data (JSON payload, up to 244 bytes)
5. RX `0xC5-00`: Data ACK `0x0100` (~53ms)
6. TX `0xC4-00`: Complete signal `0x02`
7. RX `0xC4-00`: Complete ACK `0x0200` (~65ms)

Both eyes receive and ACK independently. CRCs are constant per status type (open=0x0f1d, data=0x3e2e, complete=0x6d7b).

## Heartbeat protocol

### Safe and dangerous types

| Value | Meaning | Confidence |
|---|---|---|
| Type `14` (`0x0E`) | **Only valid heartbeat type** — produces echo on 0x80-00 | High — probe 2026-02-27, reconfirmed 2026-03-01 |
| Type `13` (`0x0D`) | **Triggers GestureLongPress** — glasses respond on 0x0D-0x01 with f1=1, f3={empty} (long release event). Both eyes respond. NOT a heartbeat type; the glasses misroute the 0x0D payload field to the gesture subsystem. Leads to pairing removal after ~1.2s. | High — capture 20260301-1-testAll.txt |
| Type `15` (`0x0F`) | **Causes BLE disconnect** — no response at all. Left eye disconnects ~1.2s after TX. If probe continues to right eye, right eye also disconnects ~5s later. Pairing removal (CBError code 14) follows during reconnect. | High — capture 20260301-1-testAll.txt |

**CRITICAL**: Type 0x0D is misinterpreted by the glasses as a gesture command, not a heartbeat. Type 0x0F produces no response and silently crashes the BLE connection. Both ultimately cause pairing removal (CBError code 14) requiring the user to forget the device in iOS Settings and re-pair. The comprehensive probe now skips these types.

**CASCADE FAILURE**: If a probe sends 0x0D/0x0F to the left eye and it disconnects, sending the same sequence to the right eye causes a second disconnect — pairing is removed for both eyes.

### Echo format (confirmed)

| Value | Meaning | Confidence |
|---|---|---|
| Echo format | `f1=type(14), f2=msgId, f13={empty}` on service 0x80-00 | High — probe 2026-03-01 |
| `f13` (field 13) | Empty length-delimited field (`6A 00`), required for decoder to recognize as heartbeat | High |
| Unsolicited echoes | Glasses send 2 heartbeat echo packets ~2s after connection, before phone sends any heartbeat. May be glasses-initiated keepalive or stale buffer. | Medium — comprehensive probe 2026-03-01 |
| Bimodal echo timing | Echoes arrive in two bursts: early (~200-630ms) and delayed (~1300-1900ms). Right eye precedes left by ~27ms within each burst. | Medium — comprehensive probe 2026-03-01 |
| Right eye AuthACK delay | Right eye AuthACK arrives 1.3s–2.0s after left eye, varying by session | Medium — multiple probe sessions 2026-03-01 |
| Msg IDs 106-108 | All produce echoes; 107 is primary | High — probe 2026-02-27 |

### CRC anomaly (captured_raw format)

Known captured frame:

`AA 21 0E 06 01 01 80 20 08 0E 10 6B 6A 00 E1 74`

| Value | Meaning | Confidence |
|---|---|---|
| Payload `08 0E 10 6B 6A 00` | Type 14, msg_id 107, empty field 13 (`6A 00`) | High |
| Type `14` | Sync-trigger-like auth/control message type | High |
| `msg_id = 107` (`0x6B`) | Common working heartbeat/sync message id | Medium |
| CRC `0xE174` in captured frame | Does not match canonical CRC16 for full payload framing | Low |

Notes:
- Canonical packet build for payload `080e106b6a00` yields CRC `0x5826` under standard framing.
- The captured_raw has `len=0x06` vs canonical `len=0x08` — a **len field discrepancy**. However, CRC16/CCITT of the 4-byte scope (`08 0e 10 6b`) yields `0xC4BC`, not `0xE174`. Exhaustive testing (7 CRC variants, multiple scopes) found no match. The CRC origin remains unknown.
- The glasses respond with a transport ACK (0x80-02) for this packet, not a heartbeat echo — suggesting firmware recognizes it by CRC signature, not protocol parsing (probe 2026-02-27 confirmed).

## Teleprompter response protocol

| Value | Meaning | Confidence |
|---|---|---|
| Type `166` (`0xA6`) | Per-page ACK on 0x06-0x00 (field1=166, field2=msg_id echo, field12={f1=1}=replacing session) | High |
| Type `164` (`0xA4`) | Rendering progress on 0x06-0x01 (field1=164, field2=msg_id, field10={f1=count}) | High |
| Type `161` (`0xA1`) | Completion event on 0x06-0x01 (field1=161, field2=last_msg_id, field7={f1=4}) | High — capture 20260301-2-testAll.txt |
| Terminal repeat 3x | Progress packet with pagesRendered=totalPages repeats at ~1.47s intervals | High |
| Content complete field6 | Nested: {field1=startPage, field2=totalPages, field3=140(scaling denominator)} | High |
| Completion f7.f1=4 | Distinct from progress (f10.f1); f7 field signals scroll-complete (different encoding) | High — capture 20260301-2-testAll.txt |

## Teleprompter extended command types (RE 2026-03-01)

| Type | Name | Implemented? | Confidence |
|---|---|---|---|
| `1` | `INIT` | Yes | High |
| `2` | `SCRIPT_LIST` | No | Medium — RE |
| `3` | `CONTENT_PAGE` | Yes | High |
| `4` | `CONTENT_COMPLETE` | Yes | High |
| `5` | `PAUSE` | No | Medium — RE |
| `6` | `RESUME` | No | Medium — RE |
| `9` | `HEARTBEAT` | No | Medium — RE |
| `10` | `AI_SYNC` | No (scroll follows speech) | Medium — RE |
| `255` | `MARKER` | Yes | High |

### Teleprompter type→field mapping (from i-soxi proto schema)

Each teleprompter command type maps to a specific protobuf field number in the packet:

| Command Type | Proto Field | Purpose | Confidence |
|---|---|---|---|
| `1` (INIT) | field 3 | Init/select script settings | High — i-soxi proto |
| `2` (SCRIPT_LIST) | field 4 | Script list data | High — i-soxi proto |
| `3` (CONTENT_PAGE) | field 5 | Page content data | High — i-soxi proto |
| `4` (CONTENT_COMPLETE) | field 6 | Completion/scroll-start signal | High — i-soxi proto |
| `255` (MARKER) | field 13 | Mid-stream boundary marker | High — i-soxi proto |

This means our code should use `field 3` (not a generic payload field) for INIT data, `field 5` for content pages, etc.

### TeleprompterScript message (from i-soxi proto — NEW Phase 3)

The SCRIPT_LIST command (type=2) uses a `TeleprompterScript` message:

| Field | Type | Example | Confidence |
|---|---|---|---|
| `1` | string | `"teleprompter_createdId_1766814694346"` (timestamp-based ID) | High — i-soxi proto |
| `2` | string | `"Teleprompt Title"` | High — i-soxi proto |

This provides the wire format for script list management if we implement type=2.

### TeleprompterStart — explicit scroll start (from i-soxi proto — NEW Phase 3)

In addition to content complete (type=4) triggering auto-scroll, there's an explicit scroll start mechanism:

```
TeleprompterStart {
  type = 1;          // Re-use init type
  msg_id = N;
  state = { f1 = 4 };  // field 3, with inner f1=4 = START
}
```

Our implementation relies on content complete to trigger scrolling (glasses auto-start after type=4). This explicit start may be useful for manual scroll-start control after pausing.

## Teleprompter and display config

| Value | Meaning | Confidence |
|---|---|---|
| `25` | Character wrap width per line | High |
| `10` | Lines per page | High |
| `14` | Minimum page count for stable render | High |
| Type `1` | Teleprompter init/select | High |
| Type `2` | Display-config message type (svc `0x0E-20`) | High |
| Type `3` | Teleprompter content page | High |
| Type `4` | Content complete / scroll-complete signal | High — confirmed by multiple probes + testAll (f1=0xA1, f7={f1=4} on 0x06-01) |
| Type `14` (`0x0E`) | Sync trigger type (svc `0x80-00`) | High |
| Type `255` | Mid-stream marker message | High |
| Marker `6A 04 08 00 10 06` | Marker sub-payload | High |
| Sync trailer `6A 00` | Empty field used as sync trigger payload | High |
| `267` | Display width-like setting | Medium |
| `230` | Line height | High |
| `1294` | Viewport height | High |
| `fontSize = 5` | Font-size-like setting | Medium |
| Scroll mode `0/1` | Manual / AI mode | High |
| `content_height = (lines * 2665) / 140` | Scaling ratio confirmed by glasses echo in content-complete message (field3=140) | High |
| `seq start = 0x08`, `msg_id start = 0x14` | Working teleprompter session seeds | Medium |
| Batch split at pages `0..9`, marker, `10..11`, sync, `12+` | Working send choreography | Medium |

### Teleprompter init display settings (protobuf field map)

| Field | Tag | Meaning | Confidence |
|---|---|---|---|
| 1 | `0x08` | Init/select type (always `1`) | High |
| 2 | `0x10` | Unknown (always `0`) | Medium |
| 3 | `0x18` | Unknown (always `0`) | Medium |
| 4 | `0x20` | Display width (`267`) | Medium |
| 5 | `0x28` | Content height (dynamic, scaled) | High |
| 6 | `0x30` | Line height (`230`) | High |
| 7 | `0x38` | Viewport height (`1294`) | High |
| 8 | `0x40` | Font size (`5`) | Medium |
| 9 | `0x48` | Scroll mode (`0`=manual, `1`=AI) | High |

### Display-config proto structure (from i-soxi)

The display config on svc `0x0E-20` follows this protobuf schema:

```
DisplayConfig {
  uint32 type = 1;              // 2
  uint32 msg_id = 2;
  DisplaySettings settings = 4; // field 4, length-delimited
}

DisplaySettings {
  uint32 enabled = 1;
  repeated DisplayRegion regions = 2;
  uint32 field3 = 3;
}

DisplayRegion {
  uint32 region_id = 1;   // 2, 3, 4, 5, 6
  uint32 param1 = 2;      // varies (0 or 13)
  float param2 = 3;       // IEEE 754 float (geometry)
  float param3 = 4;       // IEEE 754 float (geometry)
  uint32 param4 = 5;      // 0
  uint32 param5 = 6;      // 0
}
```

| Value | Meaning | Confidence |
|---|---|---|
| Region IDs `2,3,4,5,6` | Display region slots | High — confirmed by proto |
| Region float params `1191`, `68`, `73`, `81`, `99`, `98` | Geometry/layout values (IEEE 754) | Medium |
| Region param2/param3 | Float fields (wire type 5, 4 bytes each) | High — confirmed by proto |
| Region-3 `param1=13` | Only region with non-zero param1 | Medium |
| Sequence fragment `...10 0D 0F 1D...` | Region-3 contains unresolved byte (`0x0F` baseline) | Low |

The iOS probe runner now sweeps that unresolved byte (`0x0F`, `0x00`, `0x06`) for empirical comparison.

### Display Wake settings (from i-soxi)

Display Wake on svc `0x04-20` uses this proto structure:

```
DisplayWake {
  uint32 type = 1;        // 1
  uint32 msg_id = 2;
  DisplayWakeSettings settings = 3;
}

DisplayWakeSettings {
  uint32 field1 = 1;      // 1
  uint32 field2 = 2;      // 1
  uint32 field3 = 3;      // 5
  uint32 field5 = 5;      // 1 (field 4 absent)
}
```

| Value | Meaning | Confidence |
|---|---|---|
| Wake field1=1, field2=1 | Likely enable flags | Medium |
| Wake field3=5 | Purpose unknown (timeout? display duration?) | Low |
| Wake field5=1 | Purpose unknown (field 4 absent in proto) | Low |

### Display lifecycle — required for rendering (2026-03-01)

The G2 glasses require explicit display activation before content renders. Two mechanisms exist:

| Feature | displayWake (`0x04-20`) | displayConfig (`0x0E-20`) | Mode Entry | Renders? |
|---|---|---|---|---|
| **Teleprompter** | No | **Yes** | init type=1 | Yes |
| **Even AI** | No | No | **CTRL(enter)** | Yes |
| **EvenHub** | Yes | **Yes** (added 2026-03-01) | None | Pending HW test |
| **Conversate** | No | **Yes** (added 2026-03-01) | None | Pending HW test |
| **Navigation** | **Yes** (added 2026-03-01) | **Yes** (added 2026-03-01) | None | Pending HW test |

**Key finding:** Without `displayConfig`, the glasses ACK content but never draw it. Even AI bypasses this via its CTRL(enter) lifecycle which triggers glasses-internal display setup. EvenHub (0xE0-20) manages its own LVGL container layout and does NOT need displayConfig — only displayWake (0x04-20). The teleprompter's 122-byte displayConfig blob (5 regions, IEEE 754 float coordinates) is shared by Conversate and Navigation pending hardware validation.

## Even AI (`0x07-20` / `0x07-00`)

### Confirmed command/status core

| Value | Meaning | Confidence |
|---|---|---|
| Command `1` | `CTRL` | High |
| Command `3` | `ASK` | High |
| Command `5` | `REPLY` | High |
| Status `2` | Enter AI mode | High |
| Status `3` | Exit AI mode | High |
| `0x2A` | `askInfo` field tag (field 5) | High |
| `0x3A` | `replyInfo` field tag (field 7) | High |
| `08 00 10 00 18 00` | `cmdCnt=0, streamEnable=0, textMode=0` defaults | High |
| Initial `magicRandom = 100` | Per-command correlation counter (not random); 100 avoids auth ID collision range 12-19 | High |
| `seq start = 0x08` | Working Even AI session seed | Medium |
| Echo f1=1/3/5 on 0x07-00 | Glasses echo CTRL/ASK/REPLY commands back (NOT EvenHub error codes) | High — event log 2026-03-01 |
| ASK ACK: f5=empty | Glasses acknowledge ASK but clear text content (don't echo question) | High — capture 20260301-1-testAll.txt |
| REPLY ACK: f7=empty | Glasses acknowledge REPLY but clear text content (don't echo answer) | High — capture 20260301-1-testAll.txt |
| Late response: f1=161, f12={f1=7} | `COMM_RSP` session cleanup ~27ms after exit; f12.f1=7 = session-end status | High — capture 20260301-1-testAll.txt |
| `162` (`0xA2`) | `COMM_RSP_ACK` — conversate ACK (f1=162, f2=msgId). f9={f1=1} on init2/marker ACK only (NOT on final transcript frame) | High — probe 2026-03-02 |
| Status 0x07-01 | EvenAI state notification: f1=1, f2=glasses_counter, f3={f1=state} (state 3=exited). f2 is running counter, NOT fixed 1 | High — probe 2026-03-02 (f2=14 observed on real HW) |
| Config 0x0D-00 on AI enter | Proactive config notification with f3={f1=6, f2=7} on entering EvenAI | High — capture 20260301-2-testAll.txt |

### Extended command enum (not all behavior-confirmed)

| Value | Meaning | Confidence |
|---|---|---|
| `0` | `NONE_COMMAND` | Medium |
| `2` | `VAD_INFO` | Medium |
| `4` | `ANALYSE` | Low |
| `6` | `SKILL` — echo: f1=6, f8={empty}; then COMM_RSP f1=0xA1 | High — testAll-2 2026-03-02 (echo + COMM_RSP confirmed) |
| `7` | `PROMPT` | Low |
| `8` | `EVENT` | Low |
| `9` | `HEARTBEAT` — echo: f1=9, f6=msgId, f11={f1=8}; then COMM_RSP f12={f1=7} | High — testAll 2026-03-02 |
| `10` | `CONFIG` — echo: f1=10, f2=msgId, f13={empty}; then COMM_RSP f12={f1=7} | High — testAll 2026-03-02 |
| `161` | `COMM_RSP` — universal completion marker (confirmed on 0x06-01 teleprompter, 0x07-00 EvenAI, 0x0B-01 conversate) | High — event log 2026-03-01 |

### Related enums and values

| Value | Meaning | Confidence |
|---|---|---|
| VAD `1/2/3` | Start / End / Timeout | Medium |
| Config `streamSpeed = 32` | Typical observed config value | Medium |
| Skill `0..7` | 0=Brightness, 1=Translate, 2=Notification, 3=Teleprompt, 4=Navigate, 5=Conversate, 6=Quicklist, 7=Auto-brightness | Low |

## NotifyResponse (`0x04-0x01`)

After a notification file transfer (via `0xC4-00`/`0xC5-00`), the glasses send back a decoded notification response on service `0x04-0x01`:

```
NotifyResponse {
  uint32 type = 1;              // 2
  uint32 msg_id = 2;
  NotificationAppInfo info = 4; // field 4, length-delimited
}

NotificationAppInfo {
  string app_bundle_id = 1;     // e.g., "com.apple.MobileSMS\0" (null-terminated)
  string app_display_name = 2;  // e.g., "Messages\0" (null-terminated)
}
```

| Value | Meaning | Confidence |
|---|---|---|
| f1 = 2 | Response type | High — capture 20260301-1-testAll.txt |
| f4.f1 | iOS app bundle identifier (null-terminated) | High — capture 20260301-1-testAll.txt |
| f4.f2 | Human-readable app display name (null-terminated) | High — capture 20260301-1-testAll.txt |

Note: Distinct from device info responses also on 0x04-0x01 (Gap 9). Device info has f4 containing firmware strings; NotifyResponse has f4 containing app bundle IDs. Distinguish by f1 value: f1=2 = notify, f1=2 with firmware strings in f5/f6 = device info.

## Service IDs (additional protocols)

| Value | Meaning | Confidence |
|---|---|---|
| `0x02-20` | Notification service — metadata only (app_id + count, no text content) | High |
| `0x0B-20`, `0x0B-00` | Conversate/ASR request/response services | High |
| `0x08-20`, `0x08-00` | Navigation request/response services | High |
| `0x0D-00` | Configuration service (brightness, config query) | High |
| `0x01-01` | Gesture events (tap/swipe) | High |
| `0x0D-01` | Gesture long press OR display mode notification (disambiguated by f3: non-empty f3 = mode change, empty/absent f3 = gesture) | High — event log 2026-03-01 |
| `0x07-01` | EvenAI status (mode-entry confirmation: f1=1, f3={f1=3}) | High — event log 2026-03-01 |
| `0x04-20` | Display wake command | High |
| `0x04-00` | Display wake ACK: f1=1, f2=brightness_level, f3=empty (~11ms latency). Also triggers COMM_RSP f1=161, f5={f1=brightness, f2=8} | High — probe 2026-03-02 (f2 brightness confirmed on real HW) |
| `0xC4-00` | File transfer command (TX on 0x7401) / File transfer ACK (RX on 0x7402) | High — capture 20260301-1-testAll.txt |
| `0xC5-00` | File transfer data (TX) / Data ACK (RX) — both on file channel | High — capture 20260301-1-testAll.txt |
| `0x20-00` | Commit response — tested 3 contexts on real HW, **zero responses** | Low — probe 2026-03-02 (downgraded from Medium) |
| `0x81-00` | Display trigger response: f1=1, f2=glasses_counter, f3={f1=67} — **confirmed active on real HW** | High — probe 2026-03-02 (upgraded from Medium) |
| `0x11-20` | ConversateAlt — tested on real HW, **zero responses** | Low — probe 2026-03-02 |
| `0x0B-01` | Conversate completion: f1=161 (COMM_RSP), f8={f1=2} (timeout auto-close) | High — capture 20260301-1-testAll.txt |

## Response type markers (cross-service pattern)

G2 response packets use high-value f1 markers (≥128) to distinguish asynchronous ACKs from direct echoes:

| f1 Value | Hex | Service(s) | Meaning | Confidence |
|---|---|---|---|---|
| `161` | `0xa1` | 0x06-01, 0x07-00, 0x0B-01 | `COMM_RSP` — universal completion/session-end marker | High |
| `162` | `0xa2` | 0x0B-00 | Conversate ACK (init and transcript) | High |
| `164` | `0xa4` | 0x06-01 | Teleprompter rendering progress | High |
| `166` | `0xa6` | 0x06-00 | Teleprompter page ACK | High |

Low-value f1 (1, 3, 5) in EvenAI responses on 0x07-00 are direct echoes of the TX command type, not asynchronous markers.

## Config mode notifications (`0x0D-00` / `0x0D-01` RX)

During display feature operations, the glasses send **asynchronous** config state notifications. These are NOT responses to config commands — they are proactive mode-change broadcasts. Transitions are **per-page** (not per-session) — each new content page can trigger a mode change.

### Config mode values (f3.f1)

| f3.f1 Value | Name | Meaning | Confidence |
|---|---|---|---|
| `6` | `CONFIG_MODE_RENDER` | Display rendering active (generic) | High — capture 20260301 |
| `11` | `CONFIG_MODE_CONVERSATE` | Conversate/ASR mode active | High — RE 2026-03-01 |
| `16` | `CONFIG_MODE_TELEPROMPTER` | Teleprompter display mode active | High — capture 20260301 |

### Config mode combined patterns (f3.f1 + f3.f2)

| f3 Content | Meaning | Trigger | Confidence |
|---|---|---|---|
| `f3={f1=6, f2=7}` | EvenAI display mode active (f2=7 = EvenAI feature ID) | Immediately after EvenAI CTRL(enter) | High — capture 20260301-1-testAll.txt |
| `f3={f1=6}` | Display active (generic, no feature ID) | During EvenAI exit and other operations | High — capture 20260301-1-testAll.txt |
| `f3={f1=11}` | Conversate mode active | During conversate init | High — RE 2026-03-01 |
| `f3={f2=16}` | Teleprompter display mode (f1 absent) | During teleprompter init | High — capture 20260301-1-testAll.txt |
| `f3={}` (empty) | Simple ACK / mode cleared | Various | High — capture 20260301-1-testAll.txt |

### Config close behavior

Config close always sends **two packets** via `config_state_close()`:
1. First packet: mode=`CONFIG_MODE_RENDER` (f1=6) — transition to render state
2. Second packet: mode cleared (f3=empty) — reset to idle

This two-packet close pattern applies to ALL feature exits (EvenAI, Teleprompter, Conversate).

### Conversate cold vs warm init

| Scenario | Config Notification? | Confidence |
|---|---|---|
| **Cold init** (first type=1, no prior config activity) | May skip config notification | Medium — mock firmware behavior; real HW emitted mode=11 when other features used earlier in session |
| **Warm init** (subsequent type=1 or after other features) | Emits config mode=11 (conversate) | High — probe 2026-03-02 confirmed on real hardware |

## Nordic UART Service (NUS)

| Value | Meaning | Confidence |
|---|---|---|
| `6E400001-B5A3-F393-E0A9-E50E24DCCA9E` | NUS service UUID | High |
| `6E400002-...` | TX characteristic (phone → glasses) | High |
| `6E400003-...` | RX characteristic (glasses → phone) | High |
| `0xF5` | Gesture event prefix byte | High |
| `0x01` | NUS gesture: single tap | High |
| `0x00` | NUS gesture: double tap | High |
| `0x04` | NUS gesture: triple tap (left) | High |
| `0x05` | NUS gesture: triple tap (right) | High |
| `0x17` | NUS gesture: long press | High |
| `0x24` | NUS gesture: release | High |
| `0x02` | NUS gesture: slide forward | High |
| `0x03` | NUS gesture: slide backward | High |
| `0x25` | NUS heartbeat command (single byte) | High |
| `0x0E` | NUS mic control prefix (`0x0E 0x01`=on, `0x0E 0x00`=off) | High |
| `0x4E` | NUS text display prefix + UTF-8 | High |
| `0x15` | NUS BMP image prefix | High |
| `0xF1` | NUS audio PCM prefix (stripped before callback) | High |

## Conversate/ASR (`0x0B-20`)

| Value | Meaning | Confidence |
|---|---|---|
| `0x35` (53) | Init packet 1 msg_id — burned-in from original capture, not a protocol requirement | Medium |
| `0x38` (56) | Init packet 2 msg_id — gap of 3 matches 2 interleaved heartbeat/ACK packets | Medium |
| Type `1` | Init packet 1 type — same as teleprompter init (shared `type=1` convention) | High |
| Type `255` (`0xFF 0x01`) | Init packet 2 type — shared marker convention with teleprompter (`type=255`) | High |
| `0x41` (65) | Update ID counter start — provides clearance above init msg_ids (53, 56) to avoid collision | Medium |
| `30` | Fixed text field length (bytes) | High |
| Type `5` | Transcript update frame type | High |
| `0x52 0x00` | Field 10 LD, empty — conversate marker (teleprompter uses field 13 instead) | Medium |
| `0A 1E` | Inner nested: field 1 LD, length 30 (text content) | High |

### Conversate alternative format (from i-soxi proto)

The i-soxi proto schema reveals a **second conversate data format** using protobuf field 7:

```
ConversateDataPackage {
  uint32 type = 1;
  uint32 msg_id = 2;
  // ... fields 3-6 for control/init/heartbeat ...
  ConversateTranscribeData transcribe_data = 7;  // ALTERNATIVE
}

ConversateTranscribeData {
  string text = 1;
  bool is_final = 2;
}
```

This is fundamentally different from our 30-byte fixed-field implementation (type=5 with space-padded text). The i-soxi format uses variable-length text in a proper protobuf string field with a boolean final flag. Our implementation works (confirmed by hardware probes) but may be a legacy/compat format.

| Our Format | i-soxi Format | Confidence |
|---|---|---|
| Type=5, field with 30-byte fixed text, partial/final byte | Type via field 7, `{text: string, is_final: bool}` | Medium — both may be valid |

### Conversate ACK responses (0x0B-00)

| f1 | f9 | Meaning | Confidence |
|---|---|---|---|
| `162` (`0xA2`) | empty | Simple ACK (init 1, transcript partial/final) | High — capture 20260301-1-testAll.txt |
| `162` (`0xA2`) | `{f1=1}` | Mode activated — sent only for init packet 2 (one-time signal) | High — capture 20260301-1-testAll.txt |

**4 ACKs per TX**: Each conversate TX to both eyes produces 4 RX ACK packets (doubled from the usual 2). Both eyes ACK both TX packets (cross-echo behavior).

### Conversate state notifications (0x0B-01)

| f1 | f8 | Meaning | Confidence |
|---|---|---|---|
| `161` (`0xA1`) | `{f1=2}` | Session ended / feature closed — `COMM_RSP` with state 2 | High — capture 20260301-2-testAll.txt |

## Navigation (`0x08-20`)

| Value | Meaning | Confidence |
|---|---|---|
| State `2` | Dashboard widget mode | High |
| State `7` | Active navigation mode | High |
| Inner type `4` | Turn-by-turn instruction type | High |
| Icon `1` | Turn left | High |
| Icon `2` | Turn right | High |
| Icon `3` | Go straight | High |
| Icon `4` | U-turn | High |
| Icon `5`–`8` | Slight left/right, sharp left/right | Medium — RE 2026-03-01 |
| Icon `9`–`11` | Merge left/right/straight | Medium — RE 2026-03-01 |
| Icon `12`–`16` | Ramp left/right, fork left/right, off ramp | Medium — RE 2026-03-01 |
| Icon `17`–`18` | Keep left/right | Medium — RE 2026-03-01 |
| Icon `19`–`24` | Roundabout variants (enter, exit, left, right, straight, U-turn) | Medium — RE 2026-03-01 |
| Icon `25` | Ferry | Medium — RE 2026-03-01 |
| Icon `26`–`28` | Arrive left/right/straight | Medium — RE 2026-03-01 |
| Icon `29`–`31` | Flag/waypoint, destination, close/cancel | Medium — RE 2026-03-01 |
| Icon `32`–`36` | Additional types from Flutter SVG assets (close-x, flag-outline, navigation-off, roundabout-135°, roundabout-45°) | Medium — framework analysis 2026-03-01 |

**Total confirmed icons**: 36 (from Flutter asset analysis of `ic_navigation_*.svg` files). Our implementation handles 4 (icons 1-4).

### Navigation sub-commands (10 total — RE 2026-03-01)

| ID | Name | Implemented? | Confidence |
|---|---|---|---|
| `1` | `start` | Yes | High |
| `2` | `basicInfo` | Yes | High |
| `3` | `miniMap` | No (BMP via file svc) | Medium — RE |
| `4` | `overviewMap` | No (BMP via file svc) | Medium — RE |
| `5` | `heartbeat` | No | Medium — RE |
| `6` | `recalculating` | No | Medium — RE |
| `7` | `arrive` | No | Medium — RE |
| `8` | `stop` | No | Medium — RE |
| `9` | `startError` | No | Medium — RE |
| `10` | `favoriteList` | No | Medium — RE |

## EvenHub container event types (`0xE0-00` RX)

| Event Type | Name | Description | Confidence |
|---|---|---|---|
| `0` | `CLICK_EVENT` | User tapped container | High — partially implemented |
| `1` | `SCROLL_TOP` | Scrolled to top of list | Medium — RE 2026-03-01 |
| `2` | `SCROLL_BOTTOM` | Scrolled to bottom of list | Medium — RE 2026-03-01 |
| `3` | `DOUBLE_CLICK` | Double-tapped container | Medium — RE 2026-03-01 |
| `4` | `FOREGROUND_ENTER` | Container gained focus | Medium — RE 2026-03-01 |
| `5` | `FOREGROUND_EXIT` | Container lost focus | Medium — RE 2026-03-01 |
| `6` | `ABNORMAL_EXIT` | Container exited abnormally | Medium — RE 2026-03-01 |

## EvenHub image result codes (`0xE0-00` RX)

| Code | Name | Confidence |
|---|---|---|
| `0` | `SUCCESS` | Medium — RE 2026-03-01 |
| `1` | `FAIL` | Medium — RE 2026-03-01 |
| `2` | `imageSizeInvalid` | Medium — RE 2026-03-01 (corrected from BUSY) |
| `3` | `sendFailed` | Medium — RE 2026-03-01 (corrected from NO_RESOURCES) |
| `4` | `INVALID_PARAM` | Medium — RE 2026-03-01 |

## EvenHub / Display containers (`0xE0-20`)

| Value | Meaning | Confidence |
|---|---|---|
| `576` | Display canvas width (pixels) | High |
| `288` | Display canvas height (pixels) | High |
| `204` | Display channel max bytes per write | High |
| `4` | Maximum containers per page | High |
| 4-bit greyscale | Image pixel format (16 shades) | High |
| `isEventCapture = 1` | Required on exactly 1 container per page to receive events | Medium |

## Notification proto (`0x02-20`)

The notification service uses a simple metadata-only format — no text content is transmitted (from i-soxi proto).

```
NotificationMessage {
  uint32 type = 1;
  uint32 msg_id = 2;
  NotificationData notification = 3;
}

NotificationData {
  uint32 app_id = 1;      // e.g., 0x1A = Gmail
  uint32 count = 2;        // Number of notifications
  // NOTE: No text content - only metadata
}
```

Notification text is delivered via file transfer (service `0xC4-00`/`0xC5-00`), not via the notification proto.

## Device status fields

These fields are confirmed by both the official Even Hub SDK (`DeviceStatus` type) and community notes (`nickustinov/even-g2-notes`):

| Field | Type | Range | Source |
|---|---|---|---|
| `batteryLevel` | Integer | 0–100 | SDK + community notes |
| `isWearing` | Boolean | true/false | SDK + community notes |
| `isCharging` | Boolean | true/false | SDK + community notes |
| `isInCase` | Boolean | true/false | SDK + community notes |

`batteryLevel` is available via the EvenHub bridge (SDK API). The standard BLE GATT battery service (`0x180F`/`0x2A19`) does **NOT exist** on G2 (confirmed by probe 2026-02-26). Battery level may be embedded in device info responses (inner f2 candidate) or require a protobuf query on 0x0D-00. Whether the heartbeat echo also includes `batteryLevel` as a protobuf field is **unconfirmed** — the heartbeat status field number assignment (3=wearing, 4=charging, 5=inCase) is still unverified.

## Brightness (`0x0D-00`) — Protobuf G2SettingPackage (Updated 2026-03-03)

G2 brightness uses protobuf `G2SettingPackage` on 0x0D-00. The G1-era raw byte format `[0x01, level, auto]` does NOT work on G2 (expects protobuf, not raw bytes). See [brightness.md](../features/brightness.md) for full protocol details.

| Value | Meaning | Confidence |
|---|---|---|
| `ProtoBaseSettings.setBrightness` | Protobuf brightness setter | High — RE 2026-03-01 |
| `ProtoBaseSettings.setBrightnessAuto` | Protobuf auto-brightness toggle | High — RE 2026-03-01 |
| `ProtoBaseSettings.setBrightnessCalibration` | Per-eye brightness calibration | High — RE 2026-03-01 |
| `APP_REQUIRE_BRIGHTNESS_INFO` | Query current brightness (protobuf) | High — RE 2026-03-01 |
| `leftMaxBrightness` / `rightMaxBrightness` | Per-eye max brightness calibration | Medium — RE 2026-03-01 |
| `isAutoBrightness` | Auto-brightness flag (protobuf field) | Medium — RE 2026-03-01 |
| Skill ID 0 (BRIGHTNESS) | EvenAI SKILL path for brightness | High — testAll-2 2026-03-02 |
| Skill ID 7 (AUTO_BRIGHTNESS) | EvenAI SKILL path for auto-brightness | High — RE 2026-03-01 |
| Level `0`–`42` | Brightness DAC range | High — confirmed in both formats |
| UI `0`–`100%` | Brightness UI percentage | High — Even.app localization keys |

**Resolution status**: Protobuf field numbers for G2SettingPackage brightness commands still TBD. Needs MITM capture of Even.app brightness control flow.

## Gesture detection

| Value | Meaning | Confidence |
|---|---|---|
| `12 04 08 01` | Protobuf pattern: swipe forward (svc 0x01-01) | High |
| `12 04 08 02` | Protobuf pattern: swipe backward (svc 0x01-01) | High |
| `400` ms | Double-tap detection window (software, not firmware) | Medium — arbitrary human-interval guess |
| 0x0D-01 `f1=1, f3={}` | Long press RELEASE event (empty f3 = gesture, not mode notification) | High — probe 2026-03-01 |
| 0x0D-01 `f1=1, f3={f1=6}` | Long press START (gesture type 6) | High — capture 20260301-1-testAll.txt |
| 0x0D-01 `f1=1, f3={f1=6, f2=7}` | Long press with extended info (f2=duration/mode?) | High — capture 20260301-1-testAll.txt |
| 0x0D-01 `f1=1, f3={f1=16}` | Display state change at teleprompter scroll start (NOT a user gesture) | High — capture 20260301-1-testAll.txt |
| 0x0D-01 `f1=1, f3={f1=11}` | Scroll end / content dismiss event at teleprompter completion | High — capture 20260301-1-testAll.txt |
| 0x0D-01 `f1=1, f3={non-empty}` | Display mode notification (NOT a gesture) | High — event log 2026-03-01 |

## Hardware identification

### G2 Main SoC (from OTA firmware — RE 2026-03-03)

| Value | Meaning | Confidence |
|---|---|---|
| **Apollo510b** | **Main SoC** — Ambiq Micro, ARM Cortex-M55, 512KB SRAM | **Confirmed** — OTA firmware build path `s200_ap510b_iar`; `lv_ambiq_display.c`; NemaGFX GPU |
| **EM9305** | **BLE Radio** — EM Microelectronic | **Confirmed** — `ble_em9305.bin` in OTA package; `service_em9305_dfu.c`; Cordio BLE host |
| `B210` | Board/PCB revision identifier | High — DFU name, firmware paths |
| `S200` | Hardware model (GATT Device Info) | High — probe 2026-02-26 |

### DFU Bootloader (from Even.app bundle — RE 2026-03-01, applies to auxiliary update path)

| Value | Meaning | Confidence |
|---|---|---|
| `hw_version = 52` | Nordic nRF52 family (init packet field — does NOT distinguish 52832 vs 52840) | High — all 3 DFU init packets |
| **nRF52840** | DFU bootloader SoC — Cortex-M4F 64MHz, 1MB flash, 256KB RAM. NOT the G2 main processor | High — bootloader at 0xF0000 requires 1MB; FWID 0x0100 = S140 |
| `sd_req = [0x0100, 0x0102]` | S140 v7.0.0 (0x0100) or v7.2.0 (0x0102) compatible | High — corrected from S132 |
| `FWID 0x0100` | S140 v7.0.0 SoftDevice identifier | High — SD info struct at MBR+0x14 |
| `S140 v7.0.0` | SoftDevice version (corrected from S132 v7.2.0) | High — FWID 0x0100 maps to S140, APP_CODE_BASE 0x27000 matches S140 (S132 uses 0x26000) |
| `0x00027000` | APP_CODE_BASE (application start — S140 specific) | High — SD info struct |
| `0x000F8000` | Bootloader start address | High — vector table |
| `0x00100000` | Flash end boundary (1 MB) | High — bootloader constant |
| `153,140` bytes | SoftDevice size (S140 v7.0.0) | High — SD info struct |

## Protobuf service map (from Even.app RE — 2026-03-01)

Services discovered from `package:even_connect` Dart protobuf modules. Service IDs (svc_hi-svc_lo) are TBD — the Dart layer uses symbolic names, not raw bytes. These need wire capture to map.

| Module | Data Package Class | Priority |
|---|---|---|
| `dashboard` | `DashboardDataPackage` | High |
| `transcribe` | — | High |
| `translate` | `TranslateDataPackage` | High |
| `menu` | via `meun_main_msg_ctx` | Medium |
| `quicklist` | `QuicklistDataPackage` | Medium |
| `health` | `HealthDataPackage` | Medium |
| `glasses_case` | `GlassesCaseDataPackage` | Medium |
| `module_configure` | — | Medium |
| `ring` | `RingDataPackage` | Medium |
| `onboarding` | `OnboardingDataPackage` | Low |
| `sync_info` | via `sync_info_main_msg_ctx` | Low |
| `logger` | via `logger_main_msg_ctx` | Low |
| `ota_transmit` | — | Low |
| `efs_transmit` | — | Low |
| `g2_setting` | — | Low |

## Compass / magnetometer (from Even.app RE — 2026-03-01)

| Value | Meaning | Confidence |
|---|---|---|
| `OS_NOTIFY_COMPASS_CHANGED` | Compass heading data notification | Medium — RE, not wire-confirmed |
| `OS_NOTIFY_COMPASS_CALIBRATE_STRAT` | Compass calibration start | Medium — RE |
| `OS_NOTIFY_COMPASS_CALIBRATE_COMPLETE` | Compass calibration complete | Medium — RE |
| `compassIndex` | Compass heading index | Medium — RE |
| `CompassCalibrateStatus` | Calibration status enum | Medium — RE |

## R1 Ring

| Value | Meaning | Confidence |
|---|---|---|
| `BAE80001-4F05-4503-8E65-3AF1F7329D1F` | Ring service UUID | High |
| `BAE80012-4F05-4503-8E65-3AF1F7329D1F` | Ring TX (phone→ring write) | High — confirmed RE 2026-03-01 |
| `BAE80013-4F05-4503-8E65-3AF1F7329D1F` | Ring RX (ring→phone notify) | High — confirmed RE 2026-03-01 |
| `0xFF` | Gesture packet marker byte | High |
| `0x03` | Gesture type: hold | High |
| `0x04` | Gesture type: tap | High |
| `0x05` | Gesture type: swipe | High |
| `0xFC` | Init command (written to 0x0030) | High |
| `0x11` | Mode command (written after 200ms delay) | High |
| `200` ms | Config delay between init and mode commands | Medium |
| Handle `0x0020` | Battery level notify | High |
| Handle `0x0024` | Gesture events notify | High |
| Handle `0x0028` | State/menu toggle notify | High |
| Handle `0x002c` | Config/version read | High |
| Handle `0x0030` | Config commands write | High |
| Passive events | **None** — ring sends no battery, state, or heartbeat events after init sequence; only user-triggered gestures (tap, hold, swipe) | High — probe 2026-03-01 on real hardware |

## Audio PCM

| Value | Meaning | Confidence |
|---|---|---|
| `16000` Hz | Sample rate | High |
| `40` bytes | PCM frame size | High |
| `10000` µs | Frame duration (10ms) | High |
| Little-endian | Byte order | High |

## Display sensor stream (`0x6402`)

Continuous encrypted sensor data stream arriving on the display notify characteristic. Unsolicited — starts immediately on subscription, flows independently of all TX activity.

| Value | Meaning | Confidence |
|---|---|---|
| `205` bytes | Fixed packet size (all packets) | High — 2393/2393 packets in capture 20260301-2 |
| `5 × 40` bytes + `5` trailer | Structure: 5 blocks of (36 encrypted + 4 sync marker) + 5 trailer | High |
| `~18.8 Hz` | Packet rate (~53ms inter-packet interval) — **CORRECTED** from ~7.3 Hz (testAll 2026-03-02: 1333 pkts, mean 53.2ms, mode 50-59ms) | High |
| `~94 Hz` | Effective sample rate (5 blocks/packet × 18.8 pkts/sec) — **CORRECTED** from ~36.5 Hz | High |
| Byte 37 (per block) | **Always odd** — sync marker invariant | High — 11,965/11,965 samples |
| Byte 38 (per block) | **Always even** (range 0x30–0x8A) — sync marker invariant | High — 11,965/11,965 samples |
| Byte 39 (per block) | **Always odd** (range 0x55–0x9F) — sync marker invariant | High — 11,965/11,965 samples |
| Byte 200 | Metadata (0–49 range, bell-curve centered ~7–11) | High |
| Byte 201 | Always `0x00` — separator | High |
| Bytes 202–203 | Signed int16 LE — **quantized head orientation angle** (14 discrete values: ±90, ±49, ±37, ±27, ±17, ±8, 0) | High |
| Byte 204 | Frame counter (0x00–0xFF, strictly incrementing, wrapping) | High |
| Entropy | 36-byte data blocks: 7.989 bits/byte (AES-level encryption) | High |
| Cross-reconnect | Glasses maintain internal counter across phone disconnect/reconnect | High |
| Single source | One eye only (strictly incrementing counter, never interleaved) | High |

## Glasses unified counter (probe 2026-03-02)

Real G2 hardware uses a **single running counter** shared between the packet header `seq` byte and the protobuf `f2` field in RX responses. This was discovered by cross-referencing auth keepalive f2 values with their packet seq bytes.

| Evidence | f2 value | Packet seq | Match? | Confidence |
|---|---|---|---|---|
| Auth keepalive #1 | `130` | `0x82` (130) | Yes | High — probe 2026-03-02 |
| Auth keepalive #2 | `147` | `0x93` (147) | Yes | High — probe 2026-03-02 |
| Auth keepalive #3 | `165` | `0xA5` (165) | Yes | High — probe 2026-03-02 |
| DeviceInfo #1 | `293` | wrapped 8-bit seq | Yes (counter > 255, seq wraps) | High — probe 2026-03-02 |
| DeviceInfo #2 | `294` | wrapped 8-bit seq | Yes | High — probe 2026-03-02 |
| EvenAI status | `14` | early in session | Yes | High — probe 2026-03-02 |

**Implications:**
- DeviceInfo f2 is NOT a "subtype" (3=first, 4=subsequent) — it's the running counter value at time of response
- EvenAI status f2 is NOT fixed at 1 — it's the current counter value
- Mock firmware should use a single `g2_next_seq()` for both packet seq and protobuf f2
- The counter wraps at 8 bits for packet seq but the protobuf f2 can hold larger values (observed 293/294)

## DisplayTrigger response (`0x81-00`) — probe 2026-03-02

| Value | Meaning | Confidence |
|---|---|---|
| f1=1 | Response type | High — probe 2026-03-02 |
| f2=glasses_counter | Running counter (same unified counter as all other responses) | High — probe 2026-03-02 |
| f3={f1=67} | Inner field — 67 may represent current brightness or display state | Medium — single observation |

DisplayTrigger request on 0x81-20 uses the same protobuf payload format as display wake (type=1, msg_id=N, settings=...). The response confirms the service is **active** on real hardware — previously classified as speculative.

## Display Wake ACK variants (`0x04-00`) — probe 2026-03-02

Display Wake ACK format varies depending on what was sent to 0x04-20:

**Standard ACK** (standard display wake, 87% of responses):

| Field | Value | Meaning | Confidence |
|---|---|---|---|
| f1 | `1` | Response type | High |
| f3 | empty | Standard ACK marker | High |

**Variant ACK** (occasionally, ~13% of responses):

| Field | Value | Meaning | Confidence |
|---|---|---|---|
| f1 | `1` | Response type | High |
| f2 | glasses_counter | Running message counter (NOT brightness level) | High — confirmed via DisplayTrigger f2 correlation |
| f3 | empty | Standard ACK marker | High |

**Brightness COMM_RSP** (when brightness data sent to 0x04-20, on **0x04-00**):

| Field | Value | Meaning | Confidence |
|---|---|---|---|
| f1 | `161` (COMM_RSP) | Completion marker | High |
| f5 | `{f1=brightness_level, f2=8}` | f1=brightness value (0-42), f2=8 (unknown — possibly display state or auto-brightness flag) | Medium — probe 2026-03-02 |

The COMM_RSP confirms that 0x04-20 **does process brightness data** and echoes the level back in f5.f1. The f2 field in the variant ACK is the glasses' unified running counter, not the brightness level (confirmed by correlation with DisplayTrigger response at the same timestamp).

## Auth keepalive (`0x80-01`)

The auth service supports bidirectional keepalive after initial authentication:

| Value | Meaning | Confidence |
|---|---|---|
| Type `4` | Auth success / reconfirmation (f1=4, f2=msgId, f3={f1=1}) | High — auth handshake |
| Type `6` | Keepalive heartbeat (f1=6, f5=empty) — distinct from auth success | High — RE 2026-03-01 |
| `~1-2s` interval | Real hardware keepalive cadence (glasses → phone) | High — community capture analysis |
| `~10s` interval | Mock firmware keepalive cadence (conservative) | High — mock firmware |
| Bidirectional | Both glasses→phone and phone→glasses send type=6 keepalives | Medium — RE 2026-03-01 |

**Note**: The initial post-auth burst (4-6 packets within 5s) uses type=4 (reconfirmation). The sustained keepalive uses type=6.

## Teleprompter scroll timing

After teleprompter finalize (type=4, scroll start), the glasses send progress ticks on svc 0x06-01:

| Value | Mock Firmware | Real HW (testAll 2026-03-02) | Confidence |
|---|---|---|---|
| First tick delay | `~480ms` | `~633ms` | High — both sources |
| Subsequent tick interval | `~1500ms` | `~1470ms` (range 1374-1523ms) | High — both sources |
| Tick count | `6` ticks | `7` progress + `1` completion | High — mock; Medium — real HW (may vary with content) |
| Total scroll duration | `~12s` | `~10.5s` (finalize→completion) | High — both sources |
| Sticky completion | Re-sent 2× at ~1500ms intervals | Not observed in testAll | High — mock; needs more real HW captures |
| `msgId = finalize+1` | Ticks use msgId one higher than finalize | Confirmed — ticks use glasses' own counter sequence | High — both sources |

## EvenHub timing

| Value | Meaning | Confidence |
|---|---|---|
| `~80ms` | Deferred completion delay after EvenHub create | High — mock firmware |
| `createStartUpPage` | **Once-only** per session — second call may be rejected | Medium — RE 2026-03-01 |
| `audioControl` | Requires `createStartUpPage` first (prerequisite) | Medium — RE 2026-03-01 |
| Images | Cannot send during container creation (queue until ready) | Medium — RE 2026-03-01 |

## Operational heuristics (implementation, not protocol law)

These values are useful but should not be treated as strict wire-level requirements.

| Value | Meaning | Confidence |
|---|---|---|
| BLE delays (`50ms`, `100ms`, `200ms`, `300ms`, `500ms`, etc.) | Pacing choices for reliability | Medium |
| Keepalive windows (`3s`, `5s`) | UX/connection hold timing | Medium |
| Heartbeat cadence `~3.05s` | Measured interval between heartbeat TX pairs (consistent ±0.15s) | High — capture 20260301-1-testAll.txt |
| Auth 0x80-01 initial burst | NOT periodic; 4-6 type=4 packets within 5s of auth, then transitions to type=6 keepalive | High — capture 20260301-1-testAll.txt |
| Probe seeds (`seq=0x40`, `msg_id=0x30`) | Diagnostic sweep scaffolding | High (for probe tool behavior), Low (as protocol requirement) |
| Probe candidate sets (`msg_id 0x6A/0x6B/0x6C`, type `0x0D/0x0E/0x0F`) | Experimental search space | High (as experiment definition), Low (as protocol meaning) |

### Disconnect risk factors (confirmed)

| Risk | Observed Impact | Mitigation | Confidence |
|---|---|---|---|
| Heartbeat type 0x0D/0x0F | Pairing removal (CBError 14), both eyes | Skip in comprehensive probe; warn in standalone | High |
| NUS connect storm in degraded mode | 3 NUS connects in 3s on sole remaining eye → second eye disconnect | Guard against NUS operations when one eye is disconnected | High — capture 20260301-1-testAll.txt |
| Display frame flood on 0x6402 | ~~Heartbeat echo stale for 36s~~ **ESCALATED**: 6402 flood causes MainActor starvation → onHeartbeatEcho callback stops firing → watchdog false positive → unnecessary disconnect+reconnect (97s and 90s events) | **Fixed**: TX-side recordHeartbeat() call in heartbeat loop prevents false positives | High — capture 20260301-2-testAll.txt |
| Background BLE throttling | Scan timeouts during iOS background state; 82s background = all scans failed | Accept as iOS limitation; queue re-auth for foreground resume | High |
| iOS background BLE timeout | App entering background → iOS stops delivering BLE callbacks after ~8s → supervision timeout → both eyes disconnect | Accept as iOS limitation; auto-reconnect handles recovery (4-5s) | High — capture 20260301-2-testAll.txt |

## Remaining highest-value inference targets

- Heartbeat CRC anomaly (`0xE174` vs canonical `0x5826`) — len field mismatch (0x06 vs 0x08) noted but CRC hypothesis disproven (4-byte CRC = `0xC4BC`). 7 CRC variants tested, no match. Firmware recognizes packet by CRC signature, not protocol parsing.
- Resolve the display-config region-3 `0x0F` byte semantics (likely flags byte, probe sweep needed).
- ~~Confirm behavior for extended Even AI command IDs (`ANALYSE`, `PROMPT`, `EVENT`, `HEARTBEAT`)~~ — PARTIALLY RESOLVED (probe 2026-03-02): Event/heartbeat tested; not specifically profiled in this probe run.
- Confirm Even AI `SKILL` sub-protocol fields beyond enum IDs.
- ~~Identify correct G2 brightness protocol~~ — **ROOT CAUSE IDENTIFIED** (RE 2026-03-01): G2 uses protobuf-encoded brightness via ProtoBaseSettings on DevConfig pathway, not G1 raw bytes. Exact protobuf field numbers still TBD.
- Verify heartbeat status **field number assignment** (3=wearing, 4=charging, 5=inCase — existence confirmed by SDK, mapping unverified).
- ~~Determine Display Wake field meanings~~ — PARTIALLY RESOLVED (probe 2026-03-02): f2 in ACK = current brightness level. COMM_RSP f5={f1=brightness, f2=8} confirms brightness echo. field3=5 and field5=1 in request still TBD.
- Confirm notification proto (`0x02-20`) `app_id` values beyond 0x1A (Gmail).
- ~~Investigate right eye heartbeat silence~~ — Partially resolved (probe 2026-03-01): confirmed 0 responses on right eye standalone; likely pairing/connection state issue.

### Recently resolved (2026-02-26)

- ~~Conversate init packet structure~~ — fully decoded as teleprompter-homolog init+marker pattern.
- ~~Conversate msg_id gap (53→56)~~ — 2 interleaved heartbeat packets consumed IDs 54-55.
- ~~Conversate update ID start (0x41=65)~~ — clearance above init msg_ids to avoid collision.
- ~~Even AI magicRandom~~ — per-command correlation counter, not random. Starting value arbitrary.
- ~~Auth sentinel (-24)~~ — hardcoded handshake marker, int64 encoding, value likely arbitrary.
- ~~Skill enum indexing~~ — confirmed 0-indexed (0..7 in code), not 1-indexed as previously documented.
- ~~Display Config proto~~ — field names confirmed from i-soxi: DisplaySettings{enabled, regions[], field3}, DisplayRegion{region_id, param1, param2(float), param3(float), param4, param5}.
- ~~Display Wake proto~~ — field names confirmed from i-soxi: DisplayWakeSettings{field1=1, field2=1, field3=5, field5=1}.
- ~~Notification proto~~ — confirmed metadata-only (app_id + count, no text) on svc 0x02-20.
- ~~Device status fields~~ — batteryLevel (0-100) confirmed alongside isWearing/isCharging/isInCase by SDK + community.

### Recently resolved (2026-03-01)

- ~~COMM_RSP (161)~~ — upgraded from Low to High confidence; confirmed as universal completion marker across teleprompter (0x06-01), EvenAI (0x07-00), and conversate (0x0B-01).
- ~~EvenAI echo on 0x07-00~~ — f1=1/3/5 are echoed CTRL/ASK/REPLY commands, NOT EvenHub error codes.
- ~~0x0D-01 ambiguity~~ — disambiguated: non-empty f3 = display mode notification, empty/absent f3 = real long-press gesture.
- ~~0x6402 characteristic type~~ — corrected from "write" to "notify"; 0x6401 is the write characteristic.
- ~~Base channel characteristics~~ — 0x0001 (writeNoResp) and 0x0002 (notify) documented from probe discovery.
- ~~Teleprompter ACK f12~~ — field12={f1=1} signals "replacing active session" when a new teleprompter send starts before the first completes.
- ~~G2Error.pairingRemoved dead code~~ — CBError code=14 now surfaces user-friendly message via G2ConnectionAlertManager.
- ~~Display channel (0x6402)~~ — confirmed 205-byte encrypted/compressed rendering frames at ~16-20fps, not protocol data. Silently discarded (expected).
- ~~Conversate auto-close timing~~ — **REVISED**: Variable timeout ~52-60s after last TX (event log: 60s; testAll-2: ~59.9s; testAll-3: ~52.4s). Not a fixed timer.
- ~~Navigation write-only~~ — confirmed 0 RX responses across full session (write-only as documented).
- ~~Brightness write-only~~ — confirmed 0 RX responses across full session (write-only as documented).

### Recently resolved (2026-03-01, hardware probe)

- ~~Heartbeat type candidates~~ — **RESOLVED**: Only type 14 (0x0E) is valid. Types 0x0D and 0x0F cause pairing removal (CBError code 14), not disconnect. Comprehensive probe now skips dangerous types.
- ~~Heartbeat echo format~~ — **CONFIRMED**: f1=type(14), f2=msgId, f13={empty} on 0x80-00. The f13 field is required for decoder recognition.
- ~~GestureLongPress f1=1~~ — **RESOLVED**: f1=1 with empty f3 = long press RELEASE event. f1=1 with non-empty f3 = display mode notification (already known from event log analysis).
- ~~R1 Ring passive events~~ — **RESOLVED**: Ring sends zero passive events (battery, state, heartbeat) after init. Only user-triggered gestures produce notifications.
- ~~Right eye heartbeat silence~~ — **PARTIALLY RESOLVED**: Right eye produces 0 heartbeat responses when tested standalone; may be a pairing/connection state issue rather than a protocol limitation.

### Recently resolved (2026-03-01, deep capture analysis)

- ~~File transfer ACK protocol~~ — **RESOLVED**: 3-step ACK on 0xC4-00/0xC5-00 using non-protobuf 2-byte status words (0=open, 1=data, 2=complete). Uses file channel 0x7402.
- ~~Auth 0x80-01 keepalive~~ — **CORRECTED**: NOT periodic. Burst of 4-6 confirmation packets within 5s of auth, then stops. Previously assumed periodic at ~700ms.
- ~~Response type markers~~ — **RESOLVED**: Cross-service pattern: 0xa1(161)=COMM_RSP, 0xa2(162)=ConversateACK, 0xa4(164)=Progress, 0xa6(166)=PageACK. Low values (1,3,5) are direct echoes.
- ~~Config 0x0D-00 mode notifications~~ — **RESOLVED**: Asynchronous display mode broadcasts during feature operations. f3.f1=6 (display active), f3.f2=7 (EvenAI), f3.f2=16 (teleprompter).
- ~~Gesture 0x0D-01 extended types~~ — **RESOLVED**: f3.f1=6 (long start), f3.f1=11 (scroll end), f3.f1=16 (display state change). Only f3=empty is a user gesture (release).
- ~~Conversate ACK multiplicity~~ — **RESOLVED**: 4 ACKs per TX (not 2). Init2 f9={f1=1} is a one-time "mode activated" signal.
- ~~EvenAI COMM_RSP~~ — **RESOLVED**: Late response f1=161, f12={f1=7} arrives ~27ms after exit confirmation. Session cleanup marker.
- ~~NUS connect storm risk~~ — **CONFIRMED**: 3 NUS connects in 3s on degraded single-eye mode contributed to second eye disconnect.
- ~~Display frame format~~ — **CONFIRMED**: 205 bytes per frame, sequential counter in last byte (wraps 0x00-0xFF), ~18.8fps continuous during active display context.

### Recently resolved (2026-03-02, testAll capture analysis)

- ~~6402 sensor stream rate~~ — **CORRECTED**: Actual rate is ~18.8 Hz (~53ms interval), NOT ~7.3 Hz. Previous measurement was wrong. 1333 packets over ~70.8s with zero dropped frames (sequential counter verified).
- ~~Display Wake brightness echo~~ — **DISPROVED**: Real HW ACK is always `08011a00` (f1=1, f3=empty). No f2 brightness field. No secondary COMM_RSP. All 12 ACKs in testAll are byte-identical.
- ~~Sticky teleprompter completion~~ — **DISPROVED**: Real HW does NOT repeat completion packets. Previous probe mistook dual-eye responses for re-sends.
- ~~Teleprompter page count~~ — **DISCOVERED**: Page rendering count is cumulative across sessions — does NOT reset when a new teleprompter session begins.
- ~~Left/right eye ACK asymmetry~~ — **DISCOVERED**: Left eye echoes exact TX msg_id in teleprompter ACKs (34 ACKs). Right eye uses its own incrementing counter and produces far fewer ACKs (~7 sparse). This is NOT a bug — eyes may have different display processing roles.
- ~~Auth keepalive schema~~ — **CORRECTED**: Uses f5 (tag 0x2A), NOT f13 (tag 0x6A). Different from heartbeat echo format. Interval is ~9.8s. Single-eye only (not paired).
- ~~Glasses-initiated heartbeat~~ — **DISCOVERED**: Glasses proactively send heartbeat (type=14) on 0x80-00 at ~15s intervals per eye, arriving as L/R pairs ~2s apart. Distinct from phone-initiated heartbeat (3s) and auth keepalive (10s).
- ~~Heartbeat echo counter~~ — **CORRECTED**: Glasses do NOT purely echo phone's heartbeat payload. Some responses contain the glasses' own incrementing counter (e.g., `108a01` = varint 138 vs phone's `106b` = 107).
- ~~Conversate f9 finalize flag~~ — **DISCOVERED**: f9={f1=1} alternates between eyes (non-deterministic). Init1 gets f9={f1=1} from one eye, init2/marker from the other. Not reliably predictable.
- ~~Conversate auto-close timing~~ — **REVISED**: Variable ~52-60s after last TX (59.9s testAll-2, 52.4s testAll-3). f2 = last_msg_id + 1. Followed by a stale ACK with glasses' own counter (unrelated msg_id).
- ~~EvenAI echo text~~ — **CONFIRMED**: ASK/REPLY echoes have empty text fields (f5=""/f7="") — bandwidth optimization. Only CTRL echoes retain full nested status.
- ~~EvenAI status only on EXIT~~ — **CONFIRMED**: Only EXIT triggers 0x07-01 status notification. ENTER does NOT produce a 0x07-01 packet (only echo on 0x07-00).
- ~~Config state f2=7 for EvenAI~~ — **CONFIRMED**: 0x0D-01 f3={f1=6, f2=7} occurs on EvenAI enter (f2=7 matches service byte 0x07). Conversate gets f3={f1=11} (=0x0B). Teleprompter gets f3={f1=6} (RENDER only, no f2).
- ~~0x04-01 NotifyResponse~~ — **NOT OBSERVED**: Zero packets on 0x04-01 despite 2 complete notification file transfers. May only trigger with specific notification types or may be mock-only behavior.
- ~~6402 sensor stream pause~~ — **DISCOVERED**: 4.3-second pause during EvenAI exit + display mode transition. Frame counter confirms zero dropped frames — glasses intentionally halted the stream during heavy display processing.
- ~~Head angle quantization~~ — **CONFIRMED**: Byte 202 in 6402 trailer uses discrete values: 0, ±8, ±17, ±27, ±37, ±49, +90 degrees. Bell-curve distribution centered at 0.
- ~~Dual-eye seq counters~~ — **CONFIRMED**: Both eyes maintain independent 8-bit sequence counters. 63 seq value collisions observed (187 unique values out of 255 possible from 382 total packets).
- ~~File transfer pattern~~ — **CONFIRMED**: Exact OPEN→DATA→COMPLETE 3-step sequence. OPEN/COMPLETE on 0xC4-00, DATA on 0xC5-00. ~800-1000ms per transfer per eye.
- ~~DeviceInfo battery level~~ — **DISCOVERED**: f4.f2 = battery level percentage. Observed f4.f2=25 (25% battery) in testAll.

### Recently resolved (2026-03-02, testAll-3 capture analysis)

- ~~EvenAI HEARTBEAT echo~~ — **DISCOVERED**: Type 9 (HEARTBEAT) echo has unique structure: f1=9, f6=msgId, f11={f1=8}. The f11={f1=8} is consistent across all HEARTBEAT echoes. Followed by COMM_RSP f12={f1=7}.
- ~~EvenAI CONFIG echo~~ — **DISCOVERED**: Type 10 (CONFIG) echo has unique structure: f1=10, f2=msgId, f13={empty}. Same f13={empty} pattern as heartbeat echo. Followed by COMM_RSP f12={f1=7}.
- ~~Teleprompter real HW timing~~ — **DISCOVERED**: Real G2 glasses use ~633ms first tick delay (vs mock's ~480ms) and ~1470ms intervals (vs mock's ~1500ms). 7 progress ticks + 1 completion (vs mock's 6 ticks). Total ~10.5s (vs mock's ~12s). BLE scheduling jitter explains variance.
- ~~Conversate auto-close variability~~ — **CONFIRMED VARIABLE**: Third measurement: ~52.4s (vs 60s in event log, 59.9s in testAll-2). Timer is firmware-internal and not a fixed 60s countdown.
- ~~Controller (0x10-20) responds~~ — **CORRECTED**: Responds with `08011a00` (f1=1, f3=empty) on 0x10-00. Response time 53-468ms. Previously documented as "zero responses."
- ~~Tasks (0x0C-20) responds~~ — **CORRECTED**: Responds with `08011a00` (f1=1, f3=empty) on 0x0C-00. Response time 69-103ms. Previously documented as "zero responses."
- ~~Heartbeat static f2~~ — **OBSERVED**: All heartbeat TX payloads use f2=0x6B (107) throughout entire session. Counter does not increment between heartbeats. Glasses echo this value but also occasionally substitute their own running counter in responses.
- ~~Late conversate ACK~~ — **OBSERVED**: After auto-close on 0x0B-01, a stale ACK arrives ~941ms later on 0x0B-00 with msg_id from glasses' own counter (0xCF01=207). This is a queued acknowledgment from the glasses' processing pipeline.

### Recently resolved (2026-03-02, hardware probe)

- ~~DisplayTrigger (0x81-20) speculative~~ — **CONFIRMED ACTIVE**: Responds on 0x81-00 with f1=1, f2=glasses_counter, f3={f1=67}. The f3.f1=67 value may indicate current brightness or display state. Upgraded from Medium to High confidence.
- ~~Display Wake f2 field~~ — **UPDATED (probe 2026-03-02)**: Standard wake ACK is usually `08011a00` (f1=1, f3=empty) — 87% of responses. Variant includes f2=glasses_counter (~13%). When brightness data is sent to 0x04-20, a COMM_RSP also appears on 0x04-00 with f5={f1=brightness_level, f2=8}. f2 in the ACK is the glasses counter, NOT brightness.
- ~~Glasses unified counter~~ — **DISCOVERED**: Real G2 hardware uses a single running counter for both the packet header `seq` byte AND the protobuf `f2` field in responses. Auth keepalive f2 values (130, 147, 165) exactly match their packet seq bytes. DeviceInfo f2=293/294 are high running counter values, NOT fixed "subtype" 3/4 as previously believed. Mock firmware currently uses separate counters (s_devinfo_subtype) — needs correction.
- ~~DeviceInfoResp f2 meaning~~ — **CORRECTED**: f2 is a running message counter shared with packet seq, NOT a "subtype" field. First response f2=293, second f2=294 in probe 2026-03-02 session (previously misidentified as f2=3→4 pattern).
- ~~EvenAI status f2~~ — **CORRECTED**: f2 in 0x07-01 responses is glasses_counter (observed f2=14 on real HW), NOT a fixed value of 1. Mock firmware should emit running counter here.
- ~~ConversateAlt (0x11-20)~~ — **TESTED**: Zero responses on real hardware. Service exists in firmware routing table but produces no ACK. May require undiscovered activation sequence or may be deprecated.
- ~~Commit (0x20-20)~~ — **DOWNGRADED**: Zero responses across 3 test contexts (minimal, after displayConfig, after evenAI) on real hardware. Downgraded from Medium to Low confidence.
- ~~Sticky teleprompter completion~~ — **DISPROVED (testAll 2026-03-02)**: Real G2 glasses do NOT repeat completion packets. Previous probe was misleading (likely captured dual-eye responses mistaken for re-sends). Mock firmware sticky completion removed.
- ~~Config state f2 qualifier~~ — **CONFIRMED**: 0x0D-01 config notifications include f3={f1=mode, f2=qualifier}. Observed f3={f1=6, f2=7} for EvenAI mode on real hardware, matching capture analysis.

### Recently resolved (2026-03-01, post-fix capture analysis)

- ~~Display 0x6402 purpose~~ — **RESOLVED**: Continuous encrypted sensor stream at ~18.8 Hz (corrected from ~7.3 Hz — testAll 2026-03-02). 5×40-byte blocks (36 AES-encrypted + 4 sync marker) + 5-byte trailer with quantized head orientation angle (±90° in 14 steps) and frame counter. Single eye source, survives reconnections. 4.3s pause during EvenAI exit (zero frame drops).
- ~~Teleprompter completion event~~ — **RESOLVED**: Distinct from progress — f1=161 on 0x06-01, f7.f1=4 (not f10 field used for progress). Signals scroll complete.
- ~~EvenAI status channel~~ — **RESOLVED**: 0x07-01 sends f1=1,f2=1,f3={f1=state} on feature exit. State 3 = exited.
- ~~Conversate state notification~~ — **RESOLVED**: 0x0B-01 sends f1=161,f8={f1=2} on session end. COMM_RSP pattern.
- ~~Watchdog false positive~~ — **RESOLVED**: 6402 display flood causes MainActor starvation → onHeartbeatEcho callback chain breaks → watchdog fires despite healthy BLE. Fixed by adding TX-side recordHeartbeat() in heartbeat loop.
- ~~NUS test failure~~ — **IDENTIFIED**: CBCentralManager fresh instantiation races with BLE state machine; 24ms failure too fast for 15s timeout. Intermittent, not a protocol issue.

### Recently resolved (2026-03-01, deep RE session)

- ~~nRF52832 identification~~ — **CORRECTED** to nRF52840: bootloader at 0xF0000 requires 1MB flash (nRF52832 QFAA only has 512KB), FWID 0x0100 = S140 (BLE 5.0, requires nRF52840).
- ~~nRF52840 as G2 main SoC~~ — **CORRECTED** (2026-03-03): G2 main SoC is **Ambiq Micro Apollo510b** with **EM9305 BLE radio** (Cordio host stack). The nRF52840/S140 identification applies only to the DFU bootloader in the Even.app bundle — an auxiliary update path (possibly R1 Ring or EM9305 radio DFU). Evidence: OTA firmware build path `s200_ap510b_iar`, `lv_ambiq_display.c`, NemaGFX GPU, `ble_em9305.bin`.
- ~~S132 v7.2.0 SoftDevice~~ — **CORRECTED** to S140 v7.0.0: FWID 0x0100 maps to S140, APP_CODE_BASE 0x27000 matches S140 (S132 uses 0x26000), SoftDevice size 153,140 bytes.
- ~~EvenHub image result BUSY (2)~~ — **CORRECTED** to `imageSizeInvalid`. BUSY was a guess; RE confirmed the actual enum value.
- ~~EvenHub image result NO_RESOURCES (3)~~ — **CORRECTED** to `sendFailed`. Same — RE confirmed.
- ~~Battery service 0x180F~~ — **CONFIRMED absent** on G2 (probe 2026-02-26). Battery level source is via EvenHub SDK bridge, not GATT.
- ~~Config mode values~~ — **RESOLVED**: CONFIG_MODE_RENDER=6, CONFIG_MODE_CONVERSATE=11, CONFIG_MODE_TELEPROMPTER=16. Transitions are per-page, not per-session.
- ~~Auth keepalive type~~ — **RESOLVED**: Type 6 (not type 4) for sustained keepalive on 0x80-01. Real hardware uses ~1-2s interval; type 4 is initial reconfirmation only.

### Recently resolved (2026-03-01, Phase 2 deep-dive agents)

- ~~Teleprompter proto field mapping~~ — **RESOLVED** via i-soxi proto: type=1→field 3, type=2→field 4, type=3→field 5, type=4→field 6, type=255→field 13.
- ~~Display config proto field~~ — **CONFIRMED**: DisplayConfig uses field 4 (not field 3) for DisplaySettings data. Our implementation already uses field 4 tag `0x22` (correct).
- ~~Notification service ID~~ — **STRENGTHENED**: i-soxi proto uses 0x02-20; BLE captures show zero traffic on 0x01-20 across 3 sessions. 0x02-20 is almost certainly correct.
- ~~Dashboard service ID~~ — **RESOLVED**: Dashboard shares service 0x07-20 with EvenAI, differentiated by type field in protobuf payload.
- ~~Speculative services~~ — **CORRECTED**: 0x0C-20 (Tasks) and 0x10-20 (Controller) DO respond with `08011a00` ACK on 0x0C-00/0x10-00 respectively (testAll 2026-03-02). 0x0A-20 (SessionInitTrigger) still zero responses. 0x81-20 (DisplayTrigger) confirmed active (probe 2026-03-02).
- ~~Navigation icon count~~ — **UPDATED**: 36 confirmed from Flutter SVG assets (previously 31+).
- ~~SMP characteristic UUID~~ — **RESOLVED**: DA2E7828-FBCE-4E01-AE9E-261174997C48 for R1 Ring DFU.
- ~~G2 hardware variants~~ — **CONFIRMED**: Two hardware revisions (g2_a, g2_b) from Flutter asset images, each in Brown/Green/Grey.
- ~~Conversate alternative format~~ — **DISCOVERED**: i-soxi proto shows field 7 `{text: string, is_final: bool}` as alternative to our 30-byte fixed format. Both may be valid.
- ~~Dashboard widget count~~ — **RESOLVED**: 29 widget types confirmed from SVG asset names in Flutter bundle.
- ~~Audio pipeline detail~~ — **RESOLVED**: GTCRN neural noise reduction → AGC → Speech Enhance → VAD (Silero v5), plus SSR Smoother module.

### Recently resolved (2026-03-01, Phase 3 deep-dive agents)

- ~~i-soxi TimeSyncRequest field 16~~ — **CORRECTED**: Tag bytes `0x82 0x08` decode to protobuf field **128**, not 16. Our implementation uses field 128 (correct). The i-soxi proto has a varint decoding error.
- ~~i-soxi TimeSyncData duplicate field 2~~ — **CORRECTED**: Proto lists both `unknown1` and `transaction_id` as field 2 (invalid). Real structure: field 1 = timestamp, field 3 = timezone offset (signed int64). Our implementation is correct.
- ~~i-soxi AuthData single field~~ — **CORRECTED**: Proto shows only `capability = 1` (field 1). Real packets have two sub-fields: f1=0x01 (basic), f2=0x04 (full). Proto is incomplete.
- ~~Even AI command enum completeness~~ — **CONFIRMED**: Full enum from g2_packet_decoder.py: 0=NONE, 1=CTRL, 2=VAD_INFO, 3=ASK, 4=ANALYSE, 5=REPLY, 6=SKILL, 7=PROMPT, 8=EVENT, 9=HEARTBEAT, 10=CONFIG, 161=COMM_RSP.
- ~~Even AI status codes~~ — **CONFIRMED**: 0=STATUS_UNKNOWN, 1=EVEN_AI_WAKE_UP, 2=EVEN_AI_ENTER, 3=EVEN_AI_EXIT (from g2_packet_decoder.py).
- ~~Even AI protobuf field structure~~ — **CONFIRMED**: f1=command, f2=magic, f3=ctrl(f1=status), f5=ask(f4=text), f7=reply(f4=text) (from g2_packet_decoder.py).
- ~~Brightness format~~ — **RESOLVED**: G2 uses protobuf G2SettingPackage on 0x0D-00. The G1-derived raw byte format `[0x01, level, auto]` does NOT work on G2 (silently ignored). Protobuf field numbers still TBD.
- ~~BLE connection state machine~~ — **DISCOVERED** from flutter_ezw_ble: connecting → contactDevice → searchService → searchChars → startBinding → connectFinish.
- ~~API staging endpoint~~ — **DISCOVERED**: `https://pre-g2.evenreal.co` (pre-production/staging).
- ~~File Command 93-byte variant~~ — **CONFIRMED**: mode[4] + size_scaled[4] + checksum[4] + extra[1] + filename[80]. CRC32C reconstruction: `(extra << 24) | (checksum >> 8)`.
- ~~CRC32C implementation~~ — **CONFIRMED**: Non-reflected MSB-first with polynomial 0x1EDC6F41 (from g2_packet_decoder.py).
- ~~Proto module count~~ — **CONFIRMED**: 28+ modules. Additional discovered: `dev_pair_manager`, `onboarding`, `dev_infomation` (sic), `g2_setting`, `module_configure`, `meun_main_msg` (sic — typo for menu).

See also: [unidentified-behaviors.md](unidentified-behaviors.md) for a full catalog of protocol unknowns and investigation priorities.
