# Unidentified Behaviors & Protocol Unknowns

This document catalogs protocol behaviors, magic numbers, and field mappings that are implemented in the codebase but not fully understood. Each entry notes the current assumption, what evidence exists, and what would be needed to confirm or correct it.

**Last updated**: 2026-03-07 (session 39l — handler_map sync, firmware RE cross-reference, item #43 resolved)

---

## 1. Hardcoded Init Sequences

### Conversate Init Packets — PARTIALLY RESOLVED

**File**: `G2ConversateProtocol.swift`

Two hardcoded packets (type=1 init + type=255 marker) must be sent before transcript updates. Protobuf structure fully decoded (2026-02-26) — follows the same init+marker pattern as teleprompter. See `G2ConversateProtocol.swift` for packet bytes.

**Still unknown**: Whether the specific display config values (field2=1, field4=1 vs teleprompter's field2=0, field4=267) are required or can be varied.

**Risk — Fixed Sequence Numbers**: Init packets use hardcoded seq values (42 and 45) that bypass `G2SequenceCounter`. Collision unlikely but possible if prior protocol consumed those seq numbers.

---

### Auth Transaction ID Sentinel — PARTIALLY RESOLVED

**File**: `ProtocolConstants.swift`

The time-sync packet includes a hardcoded varint encoding of signed Int64(-24):
```
E8 FF FF FF FF FF FF FF FF 01
```

This appears in every auth time-sync packet across all known implementations (iOS, Python, i-soxi).

**Resolved**: This is NOT a timezone offset (UTC-24 doesn't exist), NOT ZigZag-encoded (sint64 -24 would be single byte `0x2F`), and NOT related to auth packet count or any other protocol value. The value 24 does not appear elsewhere in the protocol.

**Best hypothesis** (confidence: Medium-High): A hardcoded protocol handshake marker. The distinctive 10-byte pattern (`E8 FF...FF 01`) is easily recognizable in BLE traffic dumps. The proto definition labels it `transaction_id` (field 3 in TimeSyncData). The value -24 appears arbitrary — likely a developer-chosen magic number from early firmware development.

**To confirm**: Test with different sentinel values to determine if the glasses validate or ignore this field.

---

## 2. Speculative Field Mappings

### Heartbeat Response Status Fields — EXISTENCE CONFIRMED

**File**: `G2ResponseDecoder.swift` (lines 175-181)

**Heartbeat echo format confirmed (2026-03-01)**: `f1=type(14), f2=msgId, f13={empty}` on service 0x80-00. The f13 field (empty length-delimited, `6A 00`) is required for the decoder to recognize the response as a heartbeat echo vs other auth-service traffic.

**Dangerous types confirmed (2026-03-01)**: Types 0x0D and 0x0F cause the glasses to **remove the iOS pairing bond** (CBError code 14), not merely disconnect. Only type 14 (0x0E) is safe. The comprehensive probe now skips these types.

Heartbeat echo responses may contain additional protobuf fields beyond the echoed request. Three status fields are provisionally mapped:

| Protobuf Field | Assumed Meaning | Confidence |
|----------------|-----------------|------------|
| Field 3 | isWearing | Medium (confirmed to exist, field number unverified) |
| Field 4 | isCharging | Medium (confirmed to exist, field number unverified) |
| Field 5 | isInCase | Medium-Low (confirmed to exist, field number unverified) |

**Confirmed (2026-02-26)**: The official Even Hub SDK (`even_hub_sdk-0.0.7/dist/index.d.ts`, `DeviceStatus` type) defines exactly these three boolean fields: `isWearing`, `isCharging`, `isInCase`. The community docs (`nickustinov/even-g2-notes`) confirm the same field names under `device.status`. These fields **definitely exist** in the protocol.

**Still unverified**: The specific protobuf field number assignment (3=wearing, 4=charging, 5=inCase). The ordering is plausible (most important status first), but the SDK API surface doesn't expose which protobuf field numbers map to which values.

**To confirm**: Capture heartbeat responses while changing wearing/charging/case state. Compare field values before and after each state change. A single session with known transitions would resolve all three mappings.

---

### EvenHub Container Event Fields — FIELD NAMES CONFIRMED

**File**: `G2ResponseDecoder.swift` (lines 906-971)

When a container with `isEventCapture=1` is active, the glasses send events back on service 0x0E-00. The event field mapping was previously speculative but **field names are now confirmed** by the official Even Hub SDK (`even_hub_sdk-0.0.7/dist/index.d.ts`):

| Outer Field | Assumed Content | Confidence |
|-------------|----------------|------------|
| Field 2 (LD) | ListItemEvent | Medium — inferred from SDK types |
| Field 3 (LD) | TextItemEvent | Medium — inferred from SDK types |

**ListItemEvent nested fields** (SDK-confirmed names):
- Field 1: `Container_ID`
- Field 2: `Container_Name`
- Field 3: `CurrentSelect_ItemIndex`
- Field 4: `CurrentSelect_ItemName`
- Field 5: `Event_Type`

**TextItemEvent nested fields** (SDK-confirmed names):
- Field 1: `Container_ID`
- Field 2: `Container_Name`
- Field 3: `Event_Type`

**Resolved**: The SDK `ContainerEventPayload` type confirms exactly these field names. The protobuf field number assignment (1-5) is still unverified, but the names and structure match our implementation.

**Still unknown**: Whether the outer field numbers (2=list, 3=text) are correct. The SDK API surface doesn't distinguish event transport — it just delivers the parsed `ContainerEventPayload`.

**To confirm**: Create a page with both list and text containers. Tap each, capture response packets, verify outer field numbers.

---

### Configuration Query Response Fields

**File**: `G2ConfigurationReader.swift` (lines 76-90)

The configuration response (service 0x0D-00) is decoded with guessed field numbers:

| Protobuf Field | Assumed Meaning | Confidence |
|----------------|-----------------|------------|
| Field 1 | Brightness level | Unverified |
| Field 2 | Auto-brightness flag | Unverified |

The code has a fallback to interpret values as either varint or raw byte, indicating uncertainty about the wire format.

**To confirm**: Query configuration at known brightness levels. Compare field values.

---

## 3. Unparsed Response Types

Several service response types are received but not decoded into typed structures. They are passed through as raw payloads via `onRawResponse`.

| Service ID | Name | Status |
|-----------|------|--------|
| 0x06-00 | TeleprompterResponse | **DECODED** — per-page ACK (type=166, field2=msg_id echo, field12={f1=1}=replacing active session) |
| 0x06-01 | TeleprompterProgress | **DECODED** — type=164, field10={field1=pagesRendered}. Terminal repeats 3x at ~1.47s |
| 0x09-01 | DeviceInfoResponse | **DECODED** — nested in field4: field5/6=firmware version, field8/12/18 unknown |
| 0x04-00 | DisplayWakeResponse | Received but not parsed |
| 0x20-00 | CommitResponse | Received but not parsed |
| 0x81-00 | DisplayTriggerResponse | Received but not parsed |
| 0x0B-00 | ConversateResponse | **DECODED** — f1=162 (COMM_RSP_ACK), f2=msgId, f9={f1=1}=init2/marker acknowledged (not on final frame) |
| 0x0B-01 | ConversateNotify | **DECODED** — auto-close: f1=161, f2=msgId, f8={f1=2}=timeout |
| 0x07-00 | EvenAIResponse | **DECODED** — f1=1/3/5 echo (CTRL/ASK/REPLY), f1=161 completion, else EvenHub |
| 0x07-01 | EvenAIStatus | **DECODED** — mode-entry confirmation: f1=1, f3={f1=3} |
| 0x08-00 | NavigationResponse | Fields stored raw, no typed accessors |

**To investigate**: Send commands on each service and capture the response payloads. Decode protobuf fields to determine their structure.

---

## 4. CRC Anomalies

### Firmware Heartbeat CRC Mismatch

**File**: `G2ResponseDecoder.swift`

One consistently observed heartbeat packet has a CRC that doesn't match canonical CRC-16/CCITT calculation:

```
AA 21 0E 06 01 01 80 20 08 0E 10 6B 6A 00 E1 74
           ↑↑                                └──┘ captured CRC: 0x74E1
           len=6                                   canonical CRC: 0x5826
```

Despite the mismatch, the glasses accept this packet and respond with a transport ACK (not a heartbeat echo — probe 2026-02-27 confirmed).

**Tested and disproven (2026-03-01)**: The packet has `len=0x06` vs canonical `len=0x08` (a len field discrepancy). The hypothesis that CRC was computed over the shorter 4-byte payload (`08 0E 10 6B`) was tested: CRC16/CCITT of those 4 bytes = `0xC4BC`, not `0xE174`. Exhaustive testing across 7 CRC variants (CCITT-FALSE, XMODEM, CCITT-reflected, KERMIT, ARC, MODBUS, USB) and multiple byte scopes (payload, svc+payload, header+payload, etc.) found **no match**.

**Updated hypothesis**: The firmware recognizes this packet by its CRC signature (`0xE174`) as a pre-stored heartbeat pattern, responding with transport ACK (0x80-02) rather than computing a heartbeat echo. The CRC may have been generated by a different firmware version or a non-standard algorithm internal to Even Realities' tooling.

**To investigate**: Capture the same heartbeat packet from the official Even Realities iOS app to compare CRC computation. Test if glasses reject packets with intentionally wrong CRCs.

---

### Response CRC Echo Behavior

Response packets (0x12 type) appear to echo the CRC from the original command packet rather than calculating a fresh CRC over the response payload. This is handled in the decoder but not explained by any specification.

---

## 5. Display Config Region-3 Unknown Byte — PARTIALLY RESOLVED

**File**: `ProtocolConstants.swift`, `G2TeleprompterProtocol.swift`

The display config blob (sent on 0x0E-20) contains 5 nested regions. Region 3 includes a non-protobuf byte:

```
... 08 03 10 0D 0F 1D ...
                   ↑
                 Flags byte (0x0F)
```

**Analysis (2026-02-26)**: The byte `0x0F` is NOT a valid protobuf tag (it would decode to field 1, wire type 7, which is undefined). The preceding varint terminates at `0x0D` (MSB clear), so `0x0F` is NOT a varint continuation byte. This is a **raw non-protobuf byte** embedded in a region whose type (param1=13) uses a specialized format.

Region 3 is the only region with a non-trivial `param1` value (13), and the only region with this extra byte. Regions 4-6 (param1=0) are 18 bytes each with standard protobuf layout; region 3 is 19 bytes.

**Best hypothesis** (confidence: Medium): The `0x0F` byte (binary `0000_1111`) is a flags/mode byte controlling display properties for this region type. The sweep candidates support a bit-flags interpretation:
- `0x00` = `0000_0000` (all flags off)
- `0x06` = `0000_0110` (bits 1-2 set)
- `0x0F` = `0000_1111` (bits 0-3 set)

**Probe results**: Not yet documented. The teleprompter works with the default 0x0F value.

**To investigate**: Run the display config sweep probe. Compare glasses behavior with 0x0F vs 0x00 vs 0x06. Look for visual differences in region 3's rendering (font, color, visibility).

---

## 6. Arbitrary Thresholds

### Double-Tap Detection Window (400ms)

**File**: `G2ResponseDecoder.swift` (line 411)

```swift
private static let doubleTapWindowMs: UInt64 = 400
```

This value was not derived from device testing or a specification. It was chosen as a typical human double-tap interval. The firmware doesn't report double-taps natively — they are detected in software by observing two single-tap events with different counter values within this window.

**Risk**: Too short → misses intentional double-taps. Too long → false positives from sequential single taps.

---

### Conversate Update ID Start (0x41) — PARTIALLY RESOLVED

**File**: `G2ConversateSender.swift`

```swift
private var updateIdCounter: UInt64 = G2ConversateConstants.initialUpdateId  // 0x41 = 65
```

The update ID starts at 65 and increments. Partially explained by the init packet analysis:

**Resolved**: The init packets use msg_ids 53 and 56. Starting transcript updates at 65 provides 8 slots of clearance (57-64) for any ACK/heartbeat traffic between init and first transcript. This avoids msg_id collisions. The gap is intentional, not arbitrary.

**Still unknown**:
- Maximum value before wraparound
- What happens if the glasses receive a non-monotonic ID

**To investigate**: Test with update IDs starting at 0, 1, or other values. Test wraparound behavior at 255 and 65535.

---

## 7. Even AI Unknowns

### SKILL Command Responses — RESOLVED

**RESOLVED**: SKILL commands (type=6) respond even outside an active EvenAI session with echo + COMM_RSP (testAll-2 2026-03-02). 8 known skills (brightness, translate, notification, teleprompt, navigate, conversate, quicklist, auto_brightness). Still unknown: whether skills take effect and what nested payload format is needed.

---

### Extended Command Types (Unverified)

These Even AI command IDs are documented in third-party sources but never tested on G2 hardware:

| CommandId | Name | Confidence |
|-----------|------|------------|
| 0 | NONE_COMMAND | Low |
| 2 | VAD_INFO | Medium |
| 4 | ANALYSE | Low |
| 7 | PROMPT | Low |
| 8 | EVENT | Low |
| 9 | HEARTBEAT | Low |
| 10 | CONFIG | Medium |
| 161 | COMM_RSP | **High** — f12.f1=7 (EvenAI), f12.f1=8 (EvenHub). New f12.f1=8 code discovered testAll-2 |

Commands verified on G2: 1 (CTRL), 3 (ASK), 5 (REPLY), 6 (SKILL), 161 (COMM_RSP). Unverified: 0, 2, 4, 7, 8, 9, 10.

---

### Magic Random Field — RESOLVED

**RESOLVED**: `magicRandom` (protobuf field 2 in `EvenAIDataPackage`) is a per-command message correlation counter, not random. Sequential increment (100, 101, 102...) is correct. Glasses maintain their own counter independently (captures show phone=53-55, glasses reply=59). Starting value is arbitrary (100 chosen to avoid auth ID collision and stay in single-byte varint range).

---

## 8. Tasks Protocol — RESOLVED

**RESOLVED**: Both Tasks (0x0C-20) and Controller (0x10-20) respond with basic ACK `08011a00` on their respective -00 channels (testAll-2 2026-03-02). Responses arrive with >1s delay. Richer payloads may unlock additional functionality.

---

## 9. Notification Proto vs File Transfer

**File**: `G2NotificationManager.swift`, `G2Protocol.swift`

The notification system uses **two different mechanisms** (confirmed by i-soxi proto):

1. **Metadata proto** (svc `0x02-20` per i-soxi): `NotificationMessage{type, msg_id, notification{app_id, count}}` — sends only app ID and count, no text content.
2. **File transfer** (svc `0xC4-00`/`0xC5-00`): `notify_whitelist.json` — sends the actual notification text and display details as a JSON file.

The codebase currently uses only the file transfer path. The metadata proto is not implemented.

**Service ID confirmed**: Our code correctly uses `0x02-20` for the notification service (in `G2ServiceIDs.notifications`, ProtocolConstants.swift line 123: `G2ServiceID(hi: 0x02, lo: 0x20)`). This matches the i-soxi proto definition. Zero traffic on 0x01-20 in all captures, confirming 0x02-20 is correct.

**Unknown**: Whether the metadata proto must be sent alongside the file transfer, or if either mechanism works independently. The glasses may require both (metadata to trigger display, file for content).

---

## 10. Brightness Protocol — ROOT CAUSE IDENTIFIED (2026-03-01)

**RESOLVED**: G2 uses protobuf-encoded brightness via `G2SettingPackage` on 0x0D-00. Our G1-derived raw bytes `[0x01, level, auto_flag]` are silently ignored. See `brightness.md` and firmware RE for DevConfig protobuf structure. Exact protobuf field numbers within `eDevCfgCommandId`/`eDeviceConfigInfoItem` still TBD -- needs BLE capture from official app.

---

## 11. Device Info Response — PARTIALLY RESOLVED

**File**: `G2ResponseDecoder.swift`

**Resolved (2026-02-26)**: Device info responses arrive on service **0x09-01** (not 0x09-00 as previously expected). The response uses a nested protobuf format:

- Outer: field1=2, field2=7, field4=LD (nested message)
- Nested (in field4): field5/field6 = firmware version strings, field7=1, field8=30, field12=85, field18=1

The decoder now handles both 0x09-00 (flat) and 0x09-01 (nested) formats.

**Updated (2026-03-01, capture testAll)**: Device info responses arrive **unsolicited** approximately every 5-12 seconds during active feature operations (teleprompter, conversate, display rendering). No query on 0x09-00 is needed to trigger these.

**Inner f2 varies within a session**: Observed 60→60→45→70 over a 47-second window. This rapid fluctuation rules out battery level. Most likely candidate: **RSSI signal strength** (as unsigned absolute value: -60dBm, -45dBm, -70dBm). Previous captures showed f2=50 — consistent with RSSI interpretation.

**Subtype counter extends**: Outer f2 (subtype) increments beyond the previously documented maximum of 4. Observed f2=3,4,5,6 in a single session (one per unsolicited response cycle). Counter resets on reconnect.

**Stable fields across session**: f3=6, f4=1, f5="2.0.7.16" (fw), f6="2.0.7.16" (hw), f7=1, f8=30, f12=54, f18=1.

**Still unknown**: The meaning of nested fields 3 (value=6), 8 (value=30, battery?), 12 (value=54, varies between sessions), and 18 (value=1).

**To confirm**: Compare inner f2 values with iOS CoreBluetooth RSSI readings from the same time window. If they correlate, f2 = |RSSI|.

---

## 12. R1 Ring Bonding & Services

Ring may suppress service UUID advertising when bonded to G2 — app uses name-prefix fallback scan. Service discovery confirmed 2 services: BAE80001 (primary, gestures) + 0xFE59 (Nordic DFU). No standard health services (0x180D/0x1822). Health queries (0xFE 0x01/02/03) returned no response. See `r1-ring.md` for details.

**Unknown**: Exact conditions for UUID suppression (connected-only vs bonded-but-disconnected).

---

## 12b. R1 Ring Passive Events — CONFIRMED ABSENT

After init (0xFC, 0x11), ring sends **zero** passive events. Only user gestures produce notifications. Battery/state must be queried (if command exists). Mock firmware correctly mirrors this.

---

## 13. Mic Control Confirmation

**File**: `G2NordicUARTClient.swift`

NUS mic commands (`[0x0E, 0x01]` / `[0x0E, 0x00]`) report success based on whether the BLE write succeeded, not whether the glasses actually enabled/disabled the microphone. There is no ACK or confirmation mechanism.

**Risk**: A successful write does not guarantee the mic state changed. The glasses may silently reject the command if in an incompatible mode.

---

## 14. Pairing Removal Timing — CONFIRMED

Glasses escalate BLE timeout → pairing removal (CBError code=14) within ~60s. Surfaced via `G2ConnectionAlertManager`. Exact timeout and firmware version dependency still unknown.

---

## 15. Heartbeat Echo Multiplicity — Bimodal Echo Pattern

Each heartbeat TX pair (L+R eye) produces **4+ echoes** on 0x80-00 in two bursts: early (~30-630ms) and delayed (~1.3-1.9s). Each eye echoes both its own TX and the TX it overheard via inter-eye link, producing 2 echoes/eye. Right eye consistently precedes left by ~27ms. The ~1.2s gap matches the dangerous-heartbeat timer.

**Impact**: Do not assume 1:1 TX/RX heartbeat correspondence. Extra echoes are harmless (decoder handles duplicates).

---

## 16. NotifyResponse App Info on 0x04-01

After notification file transfer, glasses echo parsed app info on 0x04-01: `f4={f1=bundleID, f2=displayName}`. Disambiguate from device info (same service) by checking f4 content: device info has f5/f6 firmware strings.

---

## 17. Teleprompter Progress Continues After Finalize

Teleprompter progress ticks (0x06-01) continue for 12+ seconds after finalize, including during unrelated feature operations. Final tick uses f1=0xA1 COMM_RSP format with f7={f1=4} instead of f10. Downstream listeners must tolerate stale ticks.

---

## 18. NUS Connect Storm in Degraded Mode — CONFIRMED RISK

3 NUS connects in 3s during single-eye degraded mode → cascade failure (remaining eye disconnected 1.9s later). NUS competes with heartbeat TX and reconnect on same radio.

**Mitigation**: Guard NUS connects when in degraded mode; log warning instead.

---

## 19. Display Frame Flood and Heartbeat Stale Detection — FIXED

**Root cause**: 0x6402 sensor stream (~20 Hz, 205 bytes/pkt) floods MainActor, starving heartbeat watchdog `recordHeartbeat()` callback.

**Fix**: Added TX-side `recordHeartbeat()` in `G2Session.startHeartbeat()`. Watchdog stays fed if BLE can write. See `magic-numbers.md` for 0x6402 frame structure (5×40-byte LFSR-scrambled blocks + 5-byte trailer with head angle + frame counter).

---

## 20. Unsolicited Heartbeat Echoes at Connection Time

Two heartbeat echoes arrive on 0x5402 ~2s after connection, **before any phone TX**. Either glasses-initiated keepalive or stale buffer from prior session. Impact: heartbeat echo count cannot reliably confirm TX — subtract unsolicited echoes when correlating.

---

## 21. Right Eye AuthACK Timing — 1.3-2.0s Delay

Right eye AuthACK arrives 1.3-2.0s after left eye (varies by session). Likely due to inter-eye relay latency or BLE connection parameter differences.

---

## 22. Comprehensive Probe Notification Handler Lifecycle — RESOLVED

**RESOLVED**: Probe handler lifecycle bug caused 0-response false negatives. Fixed with shared `SharedCapture` class that persists across all sub-probes. See `G2ProtocolProbeSender.swift`.

---

## 23. Bidirectional Feature Protocols — RESOLVED

**RESOLVED**: Teleprompter, EvenAI, Conversate, and Display Wake are bidirectional (ACK + progress/status). EvenHub (0xE0-20 TX / 0xE0-00 RX), Navigation, and Brightness are write-only. Config state notifications (0x0D-00) fire during feature transitions. Full service routing table in MEMORY.md "Response Decoder Service Routing".

---

## 24. iOS Background BLE Timeout — Disconnect Pattern

iOS stops delivering BLE callbacks ~8s after backgrounding → supervision timeout → disconnect. Auto-reconnect succeeds in ~5s. Longer background periods (~130s) sometimes survive if the phone was recently responsive. iOS platform limitation — existing auto-reconnect handles it.

---

## 25. NUS CBCentralManager Race — Intermittent

NUS connect occasionally fails in 24ms (before `.poweredOn` transition). Race condition with fresh `CBCentralManager`. Subsequent connects succeed. Low impact — NUS is secondary. Consider reusing `G2Session`'s centralManager.

---

## Investigation Priority

### High Priority (blocks features)
1. Configuration response field mapping

### Medium Priority (improves reliability)
2. Heartbeat status fields — **verify field number assignment** (existence confirmed by SDK, echo format confirmed by probe)
3. Container event **outer field numbers** (2=list, 3=text) — field names now confirmed by SDK
4. CRC anomaly root cause (7 CRC variants tested, all failed — may require capturing from official app)
5. Notification proto (`0x02-20`) — is it required alongside file transfer, or independent? (i-soxi + our code confirm 0x02-20; zero traffic on 0x01-20 in all captures)
6. R1 Ring battery query — does a command exist to request battery level? (passive events confirmed absent)
7. Device info inner f2 — confirm whether it's RSSI by correlating with CoreBluetooth RSSI readings
8. Config 0x0D-00 mode notifications — verify if f3.f2 values map directly to feature IDs
9. Gesture 0x0D-01 f3.f1=11 and f3.f1=16 — confirm these are display events, not user gestures

### Low Priority (edge cases / partially resolved)
10. Display config region-3 byte — **PARTIALLY RESOLVED**: likely flags byte, not protobuf
11. Display Wake field meanings (field3=5, field5=1)
12. R1 ring service UUID suppression conditions
13. Conversate init fixed-seq collision risk
14. Unsolicited heartbeat echoes at connect — determine if glasses-initiated or stale buffer
15. Heartbeat echo delayed burst — confirm ~1.2s second burst timing on multiple sessions
16. Display 0x6402 signed int16 angle — confirm this is head orientation (tilt/pitch) by correlating with physical movement
17. NUS CBCentralManager race — investigate 24ms timeout; consider reusing G2Session's centralManager instead of creating a new one
18. **Display lifecycle for non-teleprompter features** — **PARTIALLY RESOLVED**: EvenHub (0xE0-20) does NOT need displayConfig — it manages its own LVGL container layout; only displayWake needed. DisplayConfig (0x0E-20) added to Conversate and Navigation senders. Needs hardware testing
19. **x450 alternate characteristics** — **PARTIALLY RESOLVED**: x450 are parent service UUIDs. Still unknown: what triggers a pipe switch in practice, and 1001 characteristic role
20. **Glasses case protocol** — **PARTIALLY RESOLVED**: `GlassesCaseDataPackage` protobuf with `eGlassesCaseCommandId`. Service ID and wire format still TBD
21. **Compass/magnetometer** — **PARTIALLY RESOLVED**: Calibration event sequence confirmed. Still unknown: BLE service carrying compass data, calibration trigger command format
22. **Device configuration extended fields** — **PARTIALLY RESOLVED**: 15 configurable module categories documented in firmware RE §14. Wire format (protobuf field numbers within G2SettingPackage) still TBD
23. **LC3 audio codec** — **RESOLVED**: LC3 runs on Apollo510b main SoC (NOT GX8002B codec chip). GX8002B handles DSP preprocessing (beamforming, VAD, wake words). NUS 0xF1 frames are raw PCM. Firmware logs: `[svc.audio]lc3_encode failed at frame %d`
24. **On-device LLM** — RE found llama.cpp + ONNX Runtime + sherpa-onnx. Our app doesn't implement on-device inference
25. **Navigation maps as BMP** — **RESOLVED**: Firmware uses RLE compression for navigation icons (`nav_ui_bmp_decompress_gray4` function). Maps sent via file transfer (0xC4/0xC5) expect RLE-compressed Gray4 BMP data, not raw uncompressed

---

## 26. Device Info f12 is Session-Variable

Device info nested f12 varies between sessions (85, 54, 69). All other fields stable. Not a hardware ID — candidates: session token, uptime, signal quality. Correlate across 5+ sessions to identify.

---

## 27. Long Press Triggers Proactive Device Info

Long press gesture → unsolicited device info on 0x09-01 (in addition to gesture on 0x0D-01). Decoder handles both solicited and unsolicited identically. No change needed.

---

## 28. Display 0x6402 Sensor Stream — PARTIALLY RESOLVED

JBD LFSR-scrambled sensor telemetry at ~20.1 Hz when display active, ~16.3 Hz average (gaps during transitions). Frame structure decoded: 5×[36 scrambled + 4 cleartext status] + 5-byte trailer. Status byte 2 encodes head tilt (r=0.73). See `magic-numbers.md` for full structure.

**Still unknown**: Whether stream starts on BLE subscription or requires feature activation. JBD LFSR polynomial still needed for descrambling.

---

## 29. Notification JSON Key Name — RESOLVED

**RESOLVED**: The JSON key `"android_notification"` is platform-independent — firmware expects this key on both iOS and Android. Our implementation is correct. See `notification.md`.

---

## 30. Notification Service ID Discrepancy — RESOLVED

**RESOLVED**: Code already uses 0x02-20 correctly. Confirmed by i-soxi proto schema.

---

## 31. Auth Keepalive Bidirectional Behavior

Auth keepalive (type=6 on 0x80-01) is bidirectional: glasses send every ~1-2s, Even.app sends back. Our app only listens — does NOT send type=6 keepalive. May contribute to long-idle instability.

**To investigate**: Add phone→glasses type=6 keepalive at ~2s intervals; measure stability over 30+ minute idle sessions.

---

## 32. EvenHub Error Codes (13 codes from RE)

Even.app defines error codes 101-113 for EvenHub: createPage(101), rebuild(102), addText(103), addImage(104), modifyText(105), modifyImage(106), removeText(107), removeImage(108), shutdown(109), audioControl(110), textUpgrade(111), setExposure(112), removeContainer(113). Our decoder only handles 0-4. Same response path, different field values.

---

## 33. Conversate Alternative Format — Field 7 vs Fixed 30-Byte

i-soxi proto defines `ConversateTranscribeData{text: string, is_final: bool}` on field 7 — variable-length protobuf vs our 30-byte fixed format. Our format works (HW confirmed). Field 7 would remove 30-char limit and space padding. **To investigate**: test field 7 format on real hardware.

---

## 34. Auth Time Sync — Field 2 vs Field 3 Transaction ID

Our auth uses field 3 for transaction ID; i-soxi uses field 2. Our auth works on HW. Low impact but suggests possible field numbering offset in auth proto. See also item 37 (i-soxi proto errors).

---

## 35. Display 0x6402 Frame Structure — PARTIALLY RESOLVED

**PARTIALLY RESOLVED**: 205-byte frames = 5×40-byte LFSR-scrambled blocks + 5-byte trailer. Trailer bytes 200-201 are quantized head angle (signed int16 LE), bytes 202-203 are `00 XX` frame counter (wraps 0-255). Byte 204 is sync/final counter. See `magic-numbers.md` for full structure.

**Still unknown**: JBD LFSR polynomial (needed to descramble the 36-byte sensor blocks within each 40-byte block).

---

## 36. NotifyResponse (0x04-01) Contains Real App Content — CONFIRMED

**CONFIRMED**: After notification file transfer, 0x04-01 echoes back parsed content: `f4={f1="com.apple.MobileSMS\0", f2="Messages\0"}`. Confirms glasses parse notification JSON. Null terminators indicate C-style firmware string handling. Could be used for delivery confirmation. See also item 16.

---

## 37. i-soxi Proto Field Number Errors — CONFIRMED

Three confirmed errors in i-soxi proto: (1) TimeSyncRequest field 16 should be 128 (tag `0x82 0x08`), (2) TimeSyncData has duplicate field 2 (real: f1=timestamp, f3=tz offset), (3) AuthData incomplete (1 field vs actual 2). Our implementations are correct. Treat i-soxi as approximate reference.

---

## 38. Even AI Unexplored Commands

We implement 4 of 12: CTRL(1), ASK(3), REPLY(5), SKILL(6). HEARTBEAT(9) and CONFIG(10) tested (both respond with echo + COMM_RSP). Remaining untested: VAD_INFO(2, may need mic), ANALYSE(4), PROMPT(7), EVENT(8). See EvenAI Command Type Coverage table in Probes section.

---

## 39. Brightness — Dual Format Ambiguity — RESOLVED

**RESOLVED**: G2 uses protobuf G2SettingPackage only. Raw byte format `[0x01, level, auto]` is G1 legacy. See `brightness.md`.

---

## 40. Display Wake f2 Echo-Back — Confirmed

Display wake TX with f2 value → glasses echo exact f2 in ACK. Could be used as correlation ID. Not currently used.

---

## 41. Conversate Late ACK After Auto-Close

After auto-close on 0x0B-01, a delayed ACK arrives ~941ms later on 0x0B-00 with glasses-internal msg_id. Queued from internal pipeline. Low impact — decoder handles gracefully.

---

## 42. Heartbeat f2 Static Value — 0x6B

All heartbeat TX uses f2=0x6B (107, non-incrementing). Glasses echo back or substitute own counter. Incrementing would enable RTT measurement. Low priority — current behavior stable.

---

## 43. Onboarding Protocol — RESOLVED

**RESOLVED** (firmware RE session 39l): Service 0x10, fully documented in handler_map.txt section 15:
- APP_PbTxEncodeOnboardingConfig (FUN_004af9d8): TX type=1, field_count=3, 16-byte struct
- APP_PbNotifyEncodeOnboardingConfig (FUN_004afb62): echo with auto-increment msgId at DAT_004b0338
- PB_RxOnboardingHeartbeat (FUN_004afcee): RX handler (simple null check, returns 0 or 2)
- APP_PbTxEncodeOnboardingHeartbeat (FUN_004afd60): heartbeat TX
- Field table at DAT_004b0168. Struct: type(1), msgId, field_count(3), state byte, padding
- G2OnboardingSender and G2OnboardingProtocol already implemented in iOS SDK

---

## Experimental Protocol Probes (TestAll #24-54)

> **Probe methodology**: The iOS app includes an experimental probe runner accessible from the Protocol Probe screen and the Run Even G2 Protocol Probe Shortcuts action. Probes capture inbound notify traffic on both control (0x5402) and file (0x7402) channels while sending test packets with varied parameters.

TestAll includes 31 experimental probes across 4 phases for protocol research. All probes send minimal payloads and log responses. Safety: no OTA, no factory reset, no unpair, no quickRestart.

**Risk levels**: LOW (known services, query-only) | MEDIUM (speculative services/commands) | EXCLUDED (OTA, factory reset, unpair)

### All Probes

| # | Probe | Service | Payload | HW Result |
|---|-------|---------|---------|-----------|
| 24 | Settings Query | 0x0D-00 | cmdId=0 | TBD |
| 25 | Dashboard AutoClose | 0x0D-00 | cmdId=8 | TBD |
| 26 | Glasses Case | 0x0D-00 | cmdId=11 | TBD |
| 27 | Dashboard HB | 0x07-20 | type=9 | TBD |
| 28 | EvenAI Config | 0x07-20 | type=10 | TBD |
| 29 | Session Init | 0x0A-20 | type=1 | TBD |
| 30 | Controller | 0x10-20 | type=1 | **ACK `08011a00`** (confirmed) |
| 31 | Tasks | 0x0C-20 | type=1 | **ACK `08011a00`** (confirmed) |
| 32 | Display Mode | 0x0D-00 | cmdId=13 | TBD |
| 33 | Anti-Shake | 0x0D-00 | cmdId=15 | TBD |
| 34 | Wakeup Angle | 0x0D-00 | cmdId=16 | TBD |
| 35 | Brightness Info | 0x0D-00 | cmdId=1 | TBD |
| 36 | Menu Info | 0x0D-00 | cmdId=4 | TBD |
| 37 | R1 Services | R1 BLE | Service discovery | TBD |
| 38 | R1 Health Query | R1 BLE | Standard health svc | TBD |
| 39 | R1 Raw Commands | R1 BAE80012 | Health queries | TBD |
| 40 | Translate Init | 0x07-20 | type=20 | TBD |
| 41 | Basic Info Query | 0x0D-00 | cmdId=2 | TBD |
| 42 | Error Info | 0x0D-00 | cmdId=9 | TBD |
| 43 | Settings Heartbeat | 0x0D-00 | cmdId=3 | TBD |
| 44 | Work Mode | 0x0D-00 | cmdId=14 | TBD |
| 45 | BLE MAC | 0x0D-00 | cmdId=17 | TBD |
| 46 | Glasses SN | 0x0D-00 | cmdId=18 | TBD |
| 47 | Device SN | 0x0D-00 | cmdId=19 | TBD |
| 48 | EvenAI Skill | 0x07-20 | type=6, skillId=0 | TBD |
| 49 | Type Scan 0x07-20 | 0x07-20 | types 11-19 | TBD |
| 50 | EvenAI Analyse | 0x07-20 | type=4 | TBD |
| 51 | EvenAI Prompt | 0x07-20 | type=7 | TBD |
| 52 | EvenAI Event | 0x07-20 | type=8 | TBD |
| 53 | EvenAI COMM_RSP | 0x07-20 | type=161 | TBD |
| 54 | Settings CmdId Scan | 0x0D-00 | cmdIds 23-40 | TBD |

### g2_settingCommandId Reference (inferred from Even.app Dart enum)

| cmdId | Name | Dir | Probed? |
|-------|------|-----|---------|
| 0 | APP_REQUIRE_BASIC_SETTING | TX | Yes |
| 1 | APP_REQUIRE_BRIGHTNESS_INFO | TX | Yes |
| 2 | APP_SEND_BASIC_INFO | TX | Yes |
| 3 | APP_SEND_HEARTBEAT_CMD | TX | Yes |
| 4 | APP_SEND_MENU_INFO | TX | Yes |
| 5 | APP_SEND_MAX_MAP_FILE | TX | Skip (file) |
| 6 | APP_SNED_MINI_MAP_FILE | TX | Skip (file) |
| 7 | APP_SET_DASHBOARD_AUTO_CLOSE_VALUE | TX | Skip (write) |
| 8 | APP_INQUIRE_DASHBOARD_AUTO_CLOSE_VALUE | TX | Yes |
| 9 | APP_SEND_ERROR_INFO_MSG | TX | Yes |
| 10 | SET_DEVICE_INFO | TX | Skip (write) |
| 11 | GET_DEVICE_INFO | TX | Yes |
| 12 | DEVICE_BRIGHTNESS | RX | — |
| 13 | DEVICE_DISPLAY_MODE | TX/RX | Yes |
| 14 | DEVICE_WORK_MODE | TX/RX | Yes |
| 15 | DEVICE_ANTI_SHAKE_ENABLE | TX | Yes |
| 16 | DEVICE_WAKEUP_ANGLE | TX | Yes |
| 17 | DEVICE_BLE_MAC | RX | Yes |
| 18 | DEVICE_GLASSES_SN | RX | Yes |
| 19 | DEVICE_DEVICE_SN | RX | Yes |
| 20 | DEVICE_SEND_LOGGER_DATA | RX | — |
| 21 | DEVICE_RESPOND_SUCCESS | RX | Meta |
| 22 | DEVICE_RESPOND_PARAMETER_ERROR | RX | Meta |

### EvenAI Command Type Coverage

| Type | Name | Status |
|------|------|--------|
| 0 | NONE | Unused |
| 1 | CTRL | **Implemented** |
| 2 | VAD_INFO | RX-only |
| 3 | ASK | **Implemented** |
| 4 | ANALYSE | Probed |
| 5 | REPLY | **Implemented** |
| 6 | SKILL | Probed |
| 7 | PROMPT | Probed |
| 8 | EVENT | Probed |
| 9 | HEARTBEAT | Probed (echo: f11={f1=8} + COMM_RSP) |
| 10 | CONFIG | Probed (echo: f13={empty} + COMM_RSP) |
| 11-19 | Dashboard/Unknown | Scanned (all respond COMM_RSP f12={f1=8}) |
| 20-23 | Translate | Probed |
| 161 | COMM_RSP | Probed (likely RX-only) |
