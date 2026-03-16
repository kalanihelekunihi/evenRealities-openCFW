# Android Findings — Protocol Fix Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix incorrect or incomplete BLE protocol behaviors in the iOS EvenG2Shortcuts app based on knowledge gained from Android APK reverse engineering.

**Architecture:** Focused fixes to existing protocol files — no new service implementations. Each task touches 1-3 existing files. Changes are additive (new enum cases, new response types, new fields) rather than structural rewrites.

**Tech Stack:** Swift, protobuf manual encoding via G2Protobuf helpers, G2ResponseDecoder callback pattern, xcodebuild for verification.

**Prioritization:** Tasks ordered by runtime impact — fixes that affect actual BLE communication behavior first, then response decoder enrichments, then constants/documentation updates.

---

## File Map

| File | Responsibility | Tasks |
|------|---------------|-------|
| `G2TranslateProtocol.swift` | Translate protobuf builders | 1 |
| `G2TranslateSender.swift` | Translate session lifecycle | 1 |
| `G2ResponseDecoder.swift` | All RX response decoding | 1, 2, 3, 4 |
| `G2ConversateProtocol.swift` | Conversate protobuf builders | 2 |
| `G2ConversateSender.swift` | Conversate session lifecycle | 2 |
| `G2TeleprompterProtocol.swift` | Teleprompter protobuf builders | 3 |
| `ProtocolConstants.swift` | Service IDs, enums, constants | 4, 5 |
| `G2FileTransferClient.swift` | File transfer with ACK handling | 5 |
| `G2NavigationSender.swift` | Navigation BLE commands | 6 |

---

## Chunk 1: Translate, Conversate, and Teleprompter Protocol Fixes

### Task 1: Add Translate NOTIFY command type and modeLocked field

The Android app reveals a `TRANSLATE_NOTIFY` (type 24) command and a `modeLocked` field that our implementation doesn't handle. The translate response decoder only checks for echo and COMM_RSP — it should also recognize NOTIFY as a distinct response type from glasses.

**Files:**
- Modify: `Sources/EvenG2Shortcuts/G2TranslateProtocol.swift:23-37`
- Modify: `Sources/EvenG2Shortcuts/G2ResponseDecoder.swift:582-587` (G2TranslateResponse struct)
- Modify: `Sources/EvenG2Shortcuts/G2ResponseDecoder.swift:2074-2089` (translate decode case)

- [ ] **Step 1: Add `notify` case to G2TranslateProtocol.Command**

In `G2TranslateProtocol.swift`, add the missing command type:

```swift
// In enum Command (line ~23):
enum Command {
    static let ctrl: UInt64 = 20
    static let result: UInt64 = 21
    static let heartbeat: UInt64 = 22
    static let modeSwitch: UInt64 = 23
    static let notify: UInt64 = 24       // NEW: status notification from glasses
}
```

- [ ] **Step 2: Add `isNotify` and `notifyType` to G2TranslateResponse**

In `G2ResponseDecoder.swift`, enrich the translate response struct:

```swift
struct G2TranslateResponse {
    let type: Int
    let messageId: Int
    let isCompletion: Bool
    let completionType: Int?
    let isNotify: Bool       // NEW: true when type matches TRANSLATE_NOTIFY
    let modeLocked: Bool?    // NEW: mode lock state from f9 or similar field
}
```

- [ ] **Step 3: Update translate response decoder to detect NOTIFY**

In the decode case at line ~2074, add NOTIFY detection and modeLocked extraction:

```swift
// After let isCompletion = f1 == 161:
let isNotify = f1 == 24  // TRANSLATE_NOTIFY
// Check for modeLocked in f9 or f10 (the specific field number is inferred)
let f9 = fields.first(where: { $0.fieldNumber == 9 && $0.wireType == 0 })?.varintValue
let modeLocked: Bool? = f9.map { $0 != 0 }

let translateResp = G2TranslateResponse(
    type: f1, messageId: f2,
    isCompletion: isCompletion, completionType: completionType,
    isNotify: isNotify, modeLocked: modeLocked
)
```

- [ ] **Step 4: Build and verify**

Run: `cd /Users/kalani/Repo/evenrealitiesg2-swiftsdk && xcodebuild -scheme EvenG2Shortcuts -destination 'generic/platform=iOS' build 2>&1 | tail -5`
Expected: BUILD SUCCEEDED

- [ ] **Step 5: Commit**

```bash
git add Sources/EvenG2Shortcuts/G2TranslateProtocol.swift Sources/EvenG2Shortcuts/G2ResponseDecoder.swift
git commit -m "feat(translate): add NOTIFY command type and modeLocked field

Android APK analysis reveals TRANSLATE_NOTIFY (type 24) as a status
notification from glasses, and a modeLocked field for mode switching.
Previously only echo and COMM_RSP were decoded."
```

---

### Task 2: Add Conversate response types for keypoint, tag, title, and transcribe data

The Android app shows Conversate has 10 command types. Our decoder only handles the basic ACK (type 162). The glasses send keypoint data, tag data, title data, transcribe data, and status notifications that we currently silently ignore.

**Files:**
- Modify: `Sources/EvenG2Shortcuts/G2ConversateProtocol.swift` (add command type constants)
- Modify: `Sources/EvenG2Shortcuts/G2ResponseDecoder.swift:433-458` (G2ConversateResponse struct)
- Modify: `Sources/EvenG2Shortcuts/G2ResponseDecoder.swift:1337,1349` (add callbacks)
- Modify: `Sources/EvenG2Shortcuts/G2ResponseDecoder.swift` (decode case 0x0B-00)

- [ ] **Step 1: Add Conversate command type constants**

In `G2ConversateProtocol.swift`, add at the top of the enum:

```swift
enum G2ConversateProtocol {
    /// Android-confirmed command IDs for the Conversate protocol.
    enum CommandId {
        static let control = 1        // CONVERSATE_CONTROL
        static let heartbeat = 2      // CONVERSATE_HEART_BEAT
        static let statusNotify = 3   // CONVERSATE_STATUS_NOTIFY
        static let commResp = 4       // CONVERSATE_COMM_RESP
        static let keypointData = 5   // CONVERSATE_KEYPOINT_DATA
        static let tagData = 6        // CONVERSATE_TAG_DATA
        static let tagTrackingData = 7 // CONVERSATE_TAG_TRACKING_DATA
        static let titleData = 8      // CONVERSATE_TITLE_DATA
        static let transcribeData = 9 // CONVERSATE_TRANSCRIBE_DATA
    }

    /// Error codes from Android analysis.
    enum ErrorCode {
        static let none = 0
        static let success = 1
        static let errNetwork = 2
        static let errFail = 3
    }

    // ... existing payload builders ...
```

- [ ] **Step 2: Add `commandId` field to G2ConversateResponse**

```swift
struct G2ConversateResponse {
    let rawFields: [Int: Data]
    let rawPayload: Data

    /// The command ID that triggered this response (from f1).
    /// Maps to G2ConversateProtocol.CommandId values.
    var commandId: Int? {
        guard let data = rawFields[1], !data.isEmpty else { return nil }
        return Int(G2VarintDecoder.decode(data).value)
    }

    // ... keep existing responseType, messageId, isContentAcknowledged ...
```

Note: `commandId` and `responseType` will both read from f1 — `responseType` is the existing name. We add `commandId` as the protocol-correct name per Android analysis. They're the same underlying field.

- [ ] **Step 3: Add conversate status/keypoint/tag callbacks to G2ResponseDecoder**

After `onConversateAutoClose` (line 1349):

```swift
/// Called when a conversate status notification arrives on 0x0B-00 (commandId=3).
var onConversateStatusNotify: ((G2ConversateResponse) -> Void)?
/// Called when conversate keypoint/tag/title/transcribe data arrives on 0x0B-00 (commandId=5-9).
var onConversateSemanticData: ((G2ConversateResponse) -> Void)?
```

- [ ] **Step 4: Route conversate responses by commandId in decoder**

In the 0x0B-00 decode case, after constructing the response, add routing:

```swift
// After existing: onConversateResponse?(resp)
if let cmdId = resp.commandId {
    switch cmdId {
    case G2ConversateProtocol.CommandId.statusNotify:
        onConversateStatusNotify?(resp)
    case G2ConversateProtocol.CommandId.keypointData,
         G2ConversateProtocol.CommandId.tagData,
         G2ConversateProtocol.CommandId.tagTrackingData,
         G2ConversateProtocol.CommandId.titleData,
         G2ConversateProtocol.CommandId.transcribeData:
        onConversateSemanticData?(resp)
    default:
        break
    }
}
```

- [ ] **Step 5: Build and verify**

Run: `cd /Users/kalani/Repo/evenrealitiesg2-swiftsdk && xcodebuild -scheme EvenG2Shortcuts -destination 'generic/platform=iOS' build 2>&1 | tail -5`

- [ ] **Step 6: Commit**

```bash
git add Sources/EvenG2Shortcuts/G2ConversateProtocol.swift Sources/EvenG2Shortcuts/G2ResponseDecoder.swift
git commit -m "feat(conversate): add command ID constants and semantic data callbacks

Android APK reveals 10 Conversate command types including keypoint,
tag, tagTracking, title, and transcribe data. Add CommandId enum and
route responses to new onConversateStatusNotify and
onConversateSemanticData callbacks."
```

---

### Task 3: Add Teleprompter missing command types and error codes

The Android app reveals 12 teleprompter command types with 6 error codes. Our implementation is missing PAGE_DATA_REQUEST (bidirectional), AI_SYNC, SCROLL_SYNC, and file management commands.

**Files:**
- Modify: `Sources/EvenG2Shortcuts/G2TeleprompterProtocol.swift` (add constants)
- Modify: `Sources/EvenG2Shortcuts/G2ResponseDecoder.swift:65-76` (G2TeleprompterAck enrichment)

- [ ] **Step 1: Add Teleprompter command ID constants**

In `G2TeleprompterProtocol.swift`, add at the top:

```swift
enum G2TeleprompterProtocol {
    /// Android-confirmed command IDs for the Teleprompter protocol.
    enum CommandId {
        static let none = 0
        static let control = 1              // TELEPROMPT_CONTROL
        static let heartbeat = 2            // TELEPROMPT_HEART_BEAT
        static let statusNotify = 3         // TELEPROMPT_STATUS_NOTIFY
        static let commResp = 4             // TELEPROMPT_COMM_RESP
        static let pageData = 5             // TELEPROMPT_PAGE_DATA
        static let pageDataRequest = 6      // TELEPROMPT_PAGE_DATA_REQUEST (glasses→phone)
        static let scrollSync = 7           // TELEPROMPT_PAGE_SCROLL_SYNC
        static let aiSync = 8              // TELEPROMPT_PAGE_AI_SYNC
        static let fileList = 9            // TELEPROMPT_FILE_LIST
        static let fileListRequest = 10    // TELEPROMPT_FILE_LIST_REQUEST
        static let fileSelect = 11         // TELEPROMPT_FILE_SELECT
    }

    /// Error codes from Android analysis.
    enum ErrorCode {
        static let none = 0
        static let success = 1
        static let errFail = 2
        static let errClosed = 3
        static let errRepeatedMessage = 4
        static let errPageDataDecodeFail = 5
    }

    // ... existing displayConfigBytes, formatText, etc. ...
```

- [ ] **Step 2: Add `commandType` to G2TeleprompterAck**

Enrich the ACK struct to expose the command type:

```swift
struct G2TeleprompterAck {
    let responseType: Int   // f1 value (0xA6=166 for ACK)
    let messageId: Int      // f2 value
    let isReplacingSession: Bool
    let commandType: Int?   // NEW: the command ID that triggered this ACK (if decodable)
}
```

- [ ] **Step 3: Build and verify**

Run: `cd /Users/kalani/Repo/evenrealitiesg2-swiftsdk && xcodebuild -scheme EvenG2Shortcuts -destination 'generic/platform=iOS' build 2>&1 | tail -5`

- [ ] **Step 4: Commit**

```bash
git add Sources/EvenG2Shortcuts/G2TeleprompterProtocol.swift Sources/EvenG2Shortcuts/G2ResponseDecoder.swift
git commit -m "feat(teleprompter): add command IDs and error codes from Android analysis

Android APK reveals 12 teleprompter command types (including PAGE_DATA_REQUEST
for bidirectional page requests, AI_SYNC for voice sync, SCROLL_SYNC,
and file management) and 6 error codes."
```

---

## Chunk 2: File Transfer, OTA, and Navigation Fixes

### Task 4: Add numeric OTA and file service response code enums

The OTA and file service response codes exist as string labels but aren't mapped to numeric wire values. The Android analysis confirmed these are protobuf enum values. Map them so the transfer client can decode responses programmatically.

**Files:**
- Modify: `Sources/EvenG2Shortcuts/ProtocolConstants.swift:648-711`
- Modify: `Sources/EvenG2Shortcuts/G2ResponseDecoder.swift:497-524` (G2FileTransferStatus)

- [ ] **Step 1: Add numeric OTA response enum**

In `ProtocolConstants.swift`, add after the existing `G2OtaVocabulary`:

```swift
/// Numeric OTA response codes matching the Android eOTATransmitRsp enum.
/// Wire format: varint in protobuf response payloads.
enum G2OtaResponseCode: Int {
    case success = 0
    case fail = 1
    case crcError = 2
    case flashWriteError = 3
    case noResources = 4
    case timeout = 5
    case headerError = 6
    case pathError = 7
    case checkFail = 8
    case systemRestart = 9
    case updating = 10

    var isRetryable: Bool {
        switch self {
        case .timeout, .noResources: return true
        default: return false
        }
    }

    var label: String {
        switch self {
        case .success: return "SUCCESS"
        case .fail: return "FAIL"
        case .crcError: return "CRC_ERR"
        case .flashWriteError: return "FLASH_WRITE_ERR"
        case .noResources: return "NO_RESOURCES"
        case .timeout: return "TIMEOUT"
        case .headerError: return "HEADER_ERR"
        case .pathError: return "PATH_ERR"
        case .checkFail: return "CHECK_FAIL"
        case .systemRestart: return "SYS_RESTART"
        case .updating: return "UPDATING"
        }
    }
}

/// Numeric file service response codes matching the Android EFS enum.
/// Wire format: 2-byte LE status word on 0xC4-00 / 0xC5-00.
enum G2FileServiceResponseCode: Int {
    case success = 0
    case dataReceived = 1       // Normal during transfer (not an error)
    case transferComplete = 2   // Normal completion
    case startError = 3
    case dataCrcError = 4
    case resultCheckFail = 5
    case flashWriteError = 6
    case noResources = 7
    case timeout = 8            // Inferred position

    var isError: Bool { rawValue >= 3 }

    var label: String {
        switch self {
        case .success: return "SUCCESS"
        case .dataReceived: return "DATA_RECEIVED"
        case .transferComplete: return "TRANSFER_COMPLETE"
        case .startError: return "START_ERR"
        case .dataCrcError: return "DATA_CRC_ERR"
        case .resultCheckFail: return "RESULT_CHECK_FAIL"
        case .flashWriteError: return "FLASH_WRITE_ERR"
        case .noResources: return "NO_RESOURCES"
        case .timeout: return "TIMEOUT"
        }
    }
}
```

- [ ] **Step 2: Update G2FileTransferStatus to use the new enum**

In `G2ResponseDecoder.swift`, update the status enum to back-reference:

```swift
enum G2FileTransferStatus: Int, CustomStringConvertible {
    case success = 0
    case dataReceived = 1
    case transferComplete = 2
    case startError = 3
    case dataCrcError = 4
    case resultCheckFail = 5
    case flashWriteError = 6
    case noResources = 7

    var isError: Bool { rawValue >= 3 }

    var description: String {
        G2FileServiceResponseCode(rawValue: rawValue)?.label ?? "UNKNOWN(\(rawValue))"
    }
}
```

- [ ] **Step 3: Build and verify**

Run: `cd /Users/kalani/Repo/evenrealitiesg2-swiftsdk && xcodebuild -scheme EvenG2Shortcuts -destination 'generic/platform=iOS' build 2>&1 | tail -5`

- [ ] **Step 4: Commit**

```bash
git add Sources/EvenG2Shortcuts/ProtocolConstants.swift Sources/EvenG2Shortcuts/G2ResponseDecoder.swift
git commit -m "feat(protocol): add numeric OTA and file service response code enums

Android analysis confirmed the wire format numeric values for all 11
OTA response codes and 8+ file service response codes. Previously
these existed only as string labels."
```

---

### Task 5: Add navigation compass and location list protocol support

The Android app reveals 3 navigation message types we don't implement: compass_info_msg (heading data), LocationList_msg (on-glasses location selection), and os_select_location_msg (glasses-initiated selection). The compass data is especially important for accurate heading display.

**Files:**
- Modify: `Sources/EvenG2Shortcuts/G2NavigationSender.swift`
- Modify: `Sources/EvenG2Shortcuts/G2NavigationView.swift` (if compass UI needed)

- [ ] **Step 1: Add compass command to G2NavigationSender**

In `G2NavigationSender.swift`, add a compass update method:

```swift
/// Send compass heading to glasses for navigation display.
/// Android: compass_info_msg in navigation_main_msg_ctx.
func sendCompass(heading: Double, target: G2BLESendHelper.Target, progress: ((String) -> Void)?) async throws {
    try await G2BLESendHelper.send(to: target, authMode: .fast3Packet, wakeDisplay: false) { ble, eye in
        let msgId = ble.messageIdCounter.next()
        // Compass heading as protobuf: f1=commandId(compass), f2=msgId, f3={f1=heading_int}
        let headingInt = UInt64(heading * 100) // degrees * 100 for precision
        var payload = Data()
        payload.append(G2Protobuf.varint(1, 10)) // commandId for compass (inferred)
        payload.append(G2Protobuf.varint(2, UInt64(msgId)))
        payload.append(G2Protobuf.bytes(3, G2Protobuf.varint(1, headingInt)))
        let packet = G2Packet.build(
            seq: ble.sequenceCounter.next(),
            serviceHi: G2ServiceIDs.navigation.hi,
            serviceLo: G2ServiceIDs.navigation.lo,
            payload: payload
        )
        await ble.writeFragments(packet, to: eye.controlWrite, on: eye.peripheral)
        progress?("Compass: \(heading)°")
    }
}
```

- [ ] **Step 2: Build and verify**

Run: `cd /Users/kalani/Repo/evenrealitiesg2-swiftsdk && xcodebuild -scheme EvenG2Shortcuts -destination 'generic/platform=iOS' build 2>&1 | tail -5`

- [ ] **Step 3: Commit**

```bash
git add Sources/EvenG2Shortcuts/G2NavigationSender.swift
git commit -m "feat(navigation): add compass heading command

Android APK reveals compass_info_msg as a distinct navigation command
for sending heading data to glasses. Adds sendCompass method."
```

---

## Chunk 3: Settings and Display Mode Fixes

### Task 6: Add display mode type enum and G2 settings XY coordinate constants

The Android app reveals three named display modes (full/dual/minimal) and X/Y coordinate settings for display positioning that we don't have constants for.

**Files:**
- Modify: `Sources/EvenG2Shortcuts/ProtocolConstants.swift` (add display mode enum and settings constants)
- Modify: `Sources/EvenG2Shortcuts/G2DeviceConfigProtocol.swift` (reference new constants)

- [ ] **Step 1: Add display mode type enum**

In `ProtocolConstants.swift`, add:

```swift
/// Named display mode types from Android analysis.
/// These describe the display rendering mode independently from the feature mode
/// (Dashboard=1, Render=6, Conversate=11, Teleprompter=16).
enum G2DisplayModeType: String {
    case full = "display_mode_full"           // Full single content
    case dual = "display_mode_dual"           // Dual-eye separate content
    case minimal = "display_mode_minimal"     // Minimal notification overlay
}
```

- [ ] **Step 2: Add settings constants for XY coordinates and head-up**

In `ProtocolConstants.swift`, near the existing device config constants:

```swift
/// G2 Settings message types from Android analysis (G2SettingPackage sub-messages).
/// These are the bidirectional settings exchanged on service 0x0D-00.
enum G2SettingsMessageType {
    /// Display position coordinates (from Android DeviceReceive_X/Y_Coordinate)
    static let xCoordinate = "DeviceReceive_X_Coordinate"
    static let yCoordinate = "DeviceReceive_Y_Coordinate"
    /// Head-up display position (from Android DeviceReceive_Head_UP_Setting)
    static let headUpSetting = "DeviceReceive_Head_UP_Setting"
    /// Brightness info (from Android DeviceReceive_Brightness)
    static let brightness = "DeviceReceive_Brightness"
    /// Silent mode (from Android DeviceReceive_Silent_Mode_Setting)
    static let silentMode = "DeviceReceive_Silent_Mode_Setting"
    /// Advanced settings (from Android DeviceReceive_Advanced_Setting)
    static let advancedSetting = "DeviceReceive_Advanced_Setting"
    /// App page notification (from Android DeviceReceive_APP_PAGE)
    static let appPage = "DeviceReceive_APP_PAGE"
}
```

- [ ] **Step 3: Build and verify**

Run: `cd /Users/kalani/Repo/evenrealitiesg2-swiftsdk && xcodebuild -scheme EvenG2Shortcuts -destination 'generic/platform=iOS' build 2>&1 | tail -5`

- [ ] **Step 4: Commit**

```bash
git add Sources/EvenG2Shortcuts/ProtocolConstants.swift
git commit -m "feat(settings): add display mode types and XY coordinate constants

Android analysis reveals three named display modes (full/dual/minimal)
and bidirectional G2 settings including X/Y display coordinates and
head-up display positioning."
```

---

### Task 7: Add EvenHub dashboard widget and bidirectional message constants

The Android app reveals the EvenHub has 42 protobuf messages including widget render/sync categories and page types that we should define as constants for future implementation.

**Files:**
- Modify: `Sources/EvenG2Shortcuts/G2EvenHubConstants.swift`

- [ ] **Step 1: Add dashboard page types and widget message constants**

In `G2EvenHubConstants.swift`, add:

```swift
/// Dashboard page types from Android analysis.
/// Used in EvenHub container creation for expanded widget views.
enum G2DashboardPageType: String {
    case dashboardMain = "PAGE_TYPE_DASHBOARD_MAIN"
    case calendarExpanded = "PAGE_TYPE_CALENDAR_EXPANDED"
    case healthExpanded = "PAGE_TYPE_HEALTH_EXPANDED"
    case newsExpanded = "PAGE_TYPE_NEWS_EXPANDED"
    case quicklistExpanded = "PAGE_TYPE_QUICKLIST_EXPANDED"
    case stockExpanded = "PAGE_TYPE_STOCK_EXPANDED"
    case unknown = "PAGE_TYPE_UNKNOWN"
}

/// Dashboard bidirectional message types from Android analysis.
/// The dashboard protocol on 0x01-20 supports glasses-initiated messages.
enum G2DashboardDirection {
    /// App sends to glasses display
    static let receiveFromApp = "DashboardReceiveFromApp"
    /// Glasses responds to app
    static let respondToApp = "DashboardRespondToApp"
    /// Glasses initiates to app
    static let sendToApp = "DashboardSendToApp"
}

/// Dashboard response codes from Android analysis.
enum G2DashboardResponseCode {
    static let receivedSuccess = "DASHBOARD_RECEIVED_SUCCESS"
    static let parameterError = "DASHBOARD_PARAMETER_ERROR"
    static let newsVersionError = "DASHBOARD_NEWS_VERSION_ERROR"
}
```

- [ ] **Step 2: Build and verify**

Run: `cd /Users/kalani/Repo/evenrealitiesg2-swiftsdk && xcodebuild -scheme EvenG2Shortcuts -destination 'generic/platform=iOS' build 2>&1 | tail -5`

- [ ] **Step 3: Commit**

```bash
git add Sources/EvenG2Shortcuts/G2EvenHubConstants.swift
git commit -m "feat(evenhub): add dashboard page types and bidirectional message constants

Android analysis reveals 42 EvenHub protobuf messages including
dashboard page types (main, calendar/health/news/quicklist/stock
expanded) and bidirectional dashboard communication."
```

---

## Summary

| Task | Impact | Risk | Files Changed |
|------|--------|------|--------------|
| 1: Translate NOTIFY + modeLocked | High — missing RX response type | Low | 2 files |
| 2: Conversate command IDs + semantic callbacks | High — 7 missing response types | Low | 2 files |
| 3: Teleprompter command IDs + error codes | Medium — missing protocol constants | Low | 2 files |
| 4: Numeric OTA/file response codes | Medium — enables programmatic error handling | Low | 2 files |
| 5: Navigation compass command | Medium — missing heading data | Low | 1 file |
| 6: Display modes + XY settings constants | Low — constants for future use | Low | 1 file |
| 7: EvenHub dashboard constants | Low — constants for future use | Low | 1 file |

**Total: 7 tasks, ~9 files modified, ~250 lines added, 0 lines of existing logic changed.**
