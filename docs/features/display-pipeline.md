# Display Pipeline — App to G2 Display

How content flows from the EvenG2Shortcuts app through BLE onto the G2 glasses displays, and how to confirm content is actually visible.

---

## 1. Display Hardware

| Property | Value |
|----------|-------|
| Panel | JBD4010 micro-LED (uLED) |
| Resolution | 576 × 288 pixels |
| Color depth | 4-bit grayscale (Gray4, 16 levels) |
| Rendering | Monoscopic — same content both eyes |
| Refresh rate | ~20 Hz (confirmed via 0x6402 sensor stream) |
| Interface | MSPI from Apollo510b to JBD ASIC |
| GPU | NemaGFX (hardware-accelerated 2D) |
| Font engine | FreeType |
| Layout engine | LVGL v9.3 |
| Brightness | 0–42 internal scale (UI 0–100%), per-eye calibration |

The Apollo510b SoC receives high-level layout commands over BLE and renders them locally with LVGL+NemaGFX. You never send raw framebuffer data for the full display — only container properties, text, and small image patches.

**GPU architecture** (from firmware RE): NemaGFX uses a command list model — `nema_cl_bind()` programs GPU registers 0xEC/0xF0/0xF4/0x148, then commands are submitted via `nema_cl_submit()`. Arc drawing uses IEEE 754 double-precision math (`__aeabi_drem` for angle modulo) with 7+ specialized arc render functions. A static 20-entry pixel format lookup table (`nema_get_format_bpp`) maps NemaGFX texture formats to stride values, optimized for Gray4 display output.

**Compression** (from firmware RE): Navigation icons use RLE compression (Gray4-specialized `nav_ui_bmp_decompress_gray4`), legal/regulatory text screens use zlib (`zlib_uncompress`), and PMIC calibration data uses LZ4. Fonts (FreeType TTF/CFF) are stored uncompressed in flash.

---

## 2. Three Required Steps

Every display feature MUST follow this sequence. Skipping any step causes content to be ACKed but never rendered.

```
Step 1: DisplayWake (0x04-20)     → Powers on the physical JBD4010 micro-LED
Step 2: DisplayConfig (0x0E-20)   → Configures 6 viewport regions (IEEE 754 floats)
Step 3: Content (feature-specific) → Sends text, images, or feature content
```

### Step 1: Display Wake (svc 0x04-20)

Activates the display hardware. Without this, the JBD panel stays off.

- **Payload**: protobuf `{f1=1, f2=msgId, f3={f1=1, f2=1, f3=5, f5=1}}`
- **Response**: ACK on 0x04-00 within ~11ms (`f1=1, f3=empty`)
- **Post-send delay**: 50ms minimum before DisplayConfig

### Step 2: Display Config (svc 0x0E-20)

Configures 6 rendering regions with IEEE 754 float geometry parameters. Shared across Teleprompter, Conversate, and Navigation. EvenHub (0xE0-20) manages its own LVGL container layout and does NOT need displayConfig.

- **Payload**: protobuf `{f1=type, f2=msgId, f4=<configBlob>}`
- **Response**: Write-only — no response (transport ACK may arrive on 0x0E-02)
- **Post-send delay**: 200–300ms before sending content

### Step 3: Feature Content

Sent on feature-specific service IDs. See §4 below.

---

## 3. BLE Characteristics

| Characteristic | Direction | Role |
|---|---|---|
| **0x5401** | Phone → Glasses (write) | Control channel — auth, heartbeat, config state |
| **0x5402** | Glasses → Phone (notify) | Control responses — ACKs, device info, gestures |
| **0x6401** | Phone → Glasses (write) | Display channel — display wake, config, content |
| **0x6402** | Glasses → Phone (notify) | Display sensor stream (~20 Hz, 205 bytes/frame) |
| **0x7401** | Phone → Glasses (write) | File channel — image/BMP transfers |
| **0x7402** | Glasses → Phone (notify) | File transfer ACKs |

---

## 4. Five Content Rendering Paths

| Path | Service | Expected Mode | Key Files |
|------|---------|---------------|-----------|
| **EvenHub** | 0xE0-20 | 6 (Render) | `G2EvenHubSender`, `G2EvenHubProtocol` |
| **Teleprompter** | 0x06-20 | 16 (Teleprompter) | `G2TeleprompterSender`, `G2TeleprompterProtocol` |
| **Conversate** | 0x0B-20 | 11 (Conversate) | `G2ConversateSender`, `G2ConversateProtocol` |
| **Navigation** | 0x08-20 | 6 (Render) | `G2NavigationSender`, `G2NavigationProtocol` |
| **Even AI** | 0x07-20 | 6 (Render) | `G2EvenAISender`, `G2EvenAIProtocol` |

Most paths share DisplayWake + DisplayConfig initialization. EvenHub only needs DisplayWake — it manages its own LVGL container layout via 0xE0-20. The display mode (0x0D-01 notification) changes to match the active feature.

---

## 5. Display Confirmation — Two Signals

### Signal 1: Sensor Stream (0x6402) — Hardware Level

The JBD display controller sends **205-byte LFSR-scrambled sensor frames at ~20 Hz** when the physical display is powered on. This is the **only reliable hardware-level indicator** that the display is active.

```swift
// G2ConnectionMonitor tracks this:
var isDisplayActive: Bool       // true if 0x6402 frames within last 2 seconds
var displayFrameRate: Double    // estimated Hz over rolling 20-frame window
var displayFrameCount: Int      // total frames since connect
```

- **Frames flowing (~20 Hz)** = display physically ON, content visible
- **No frames** = display physically OFF
- **Frame gap >200ms** = brief display sleep/wake

### Signal 2: Display Mode (0x0D-01) — Software Level

The glasses notify the app of rendering mode changes via config state notifications:

| Mode | Value | Meaning |
|------|-------|---------|
| Idle | 0 | Display off or no content |
| Render | 6 | EvenHub/Navigation content active |
| Conversate | 11 | ASR transcript active |
| Teleprompter | 16 | Scrolling text active |

```swift
// G2ConnectionMonitor tracks this:
var displayMode: G2DisplayMode?  // updated on every 0x0D-01 notification
```

### Programmatic Confirmation

```swift
// G2DisplayConfirmation combines both signals:
let confirmation = await G2ConnectionMonitor.shared.awaitDisplayConfirmation(
    expectedMode: 6,            // what mode we expect (nil = any)
    preFrameCount: framesBefore // snapshot before send
)
// confirmation.isConfirmed = true if mode matched OR new frames arrived
// confirmation.summary = "Display confirmed: 20.5 Hz, mode=Render"
```

---

## 6. Display Mode State Machine

```
                    ┌─── Teleprompter send ───► mode=16 (Teleprompter)
                    │
    mode=0 (Idle) ──┼─── EvenHub/Nav/AI send ──► mode=6 (Render)
                    │
                    └─── Conversate init ──────► mode=11 (Conversate)

    Any mode ───────── shutdown/exit/timeout ──► mode=0 (Idle)
```

Mode transitions are reported on 0x0D-01 with `f3={f1=mode}`. Config close always sends 2 packets (render mode + reset) via `config_state_close()`.

---

## 7. Sender Display Pipeline Status

All senders perform DisplayWake + DisplayConfig + Content + Confirmation:

| Sender | DisplayWake | DisplayConfig | Confirmation |
|--------|-------------|---------------|--------------|
| G2EvenHubSender | ✅ | ✅ | ✅ |
| G2TeleprompterSender | ✅ | ✅ | ✅ |
| G2ConversateSender | ✅ | ✅ | ✅ |
| G2NavigationSender | ✅ | ✅ | ✅ |
| G2EvenAISender | ✅ | ✅ | ✅ |

After each send, senders call `awaitDisplayConfirmation()` and report the result via the progress callback, making it visible in both UI and TestAll automation.

---

## 8. Display Constraints

| Constraint | Value |
|---|---|
| Canvas | 576 × 288 pixels, monoscopic |
| Color depth | 4-bit grayscale (16 levels: 0x0 black – 0xF white) |
| Max containers/page | 4 (text, list, or image) |
| Max text (create) | 1000 chars |
| Max text (upgrade) | 2000 chars |
| Image dimensions | 20–200 × 20–100 px |
| Image format | Raw Gray4 nibble-packed (2 pixels/byte) |
| Image fragment max | 174 bytes |
| BLE display MTU | 204 bytes payload |
| DisplayWake post-delay | 50ms minimum |
| DisplayConfig post-delay | 200–300ms |

---

## Related Documents

- [eventhub.md](eventhub.md) — EvenHub container system (text, list, image containers)
- [teleprompter.md](teleprompter.md) — Teleprompter scrolling text protocol
- [conversate.md](conversate.md) — Conversate/ASR transcript protocol
- [navigation.md](navigation.md) — Navigation turn-by-turn protocol
- [even-ai.md](even-ai.md) — Even AI overlay protocol
- [brightness.md](brightness.md) — Brightness control paths
- [../devices/g2-glasses.md](../devices/g2-glasses.md) — G2 hardware BOM, display specs
- [../protocols/services.md](../protocols/services.md) — Service ID routing reference
- [../protocols/ble-uuids.md](../protocols/ble-uuids.md) — BLE characteristic UUIDs
