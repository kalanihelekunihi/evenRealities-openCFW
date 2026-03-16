# Even R1 Ring — Hardware & Protocol Specification

The Even R1 is a smart ring that serves as both a standalone health tracker and a gesture input device for the G2 glasses. It uses a Nordic nRF5x SoC with MCUboot dual-image firmware, health sensors, and dual BLE connections.

---

## 1. Product Identification

| Property | Value |
|----------|-------|
| **Product Name** | Even R1 Ring / Smart Ring |
| **FCC ID** | 2BFKR-R01 |
| **IC** | 32408-R01 |
| **HVIN** | Even R01 |
| **BLE Names** | `Even Ring`, `R1`, `EVEN_RING`, `EvenRing` (variants) |
| **Communication** | Dual BLE: Ring↔Phone + Ring↔G2 Glasses |

---

## 2. Hardware

| Property | Value | Confidence |
|----------|-------|------------|
| **SoC** | Nordic Semiconductor nRF5x (S140 DFU layout; most consistent with nRF52840-class device; exact part unresolved) | MEDIUM |
| **CPU** | ARM Cortex-M4F | HIGH |
| **BLE Stack** | SoftDevice (Nordic proprietary) | HIGH |
| **Bootloader** | MCUboot (dual-image A/B slots) | HIGH |
| **DFU Protocol** | FE59 Buttonless Secure DFU + SMP/MCUmgr | HIGH |
| **Remaining component map** | Peripheral IC map remains unverified from current firmware artifacts | LOW |

Evidence for Nordic nRF5x:
- **FE59 service**: BLE SIG-registered UUID for Nordic Buttonless Secure DFU. Only present on Nordic SoCs
- **SMP characteristic**: MCUmgr Simple Management Protocol, the standard Nordic firmware transfer mechanism
- **MCUboot**: Dual-image bootloader with A/B slot switching — standard Nordic SDK pattern
- **DFU bundles**: `B210_BL_DFU_NO_v2.0.3.0004` and `B210_SD_ONLY_NO_v2.0.3.0004` in the Even.app bundle reference `softdevice.bin` and `bootloader.bin` with ECDSA P-256 signed init packets

### Nordic-domain caveat

- The DFU artifacts are consistent with Nordic S140 placement (`softdevice.bin` linked to `0x00001000`, bootloader at `0x000F8000`), which is the layout pattern for Nordic 1MB-class parts and makes nRF52840 the leading candidate.
- This is still a map-inference, not a direct silicon ID readout; treat the exact SoC part number as unconfirmed until a direct ID field is found.
- Package naming (`B210_*`) and service/UUID flow match Nordic legacy nRF5 DFU-era tooling rather than a modern nRF Connect DFU bundle.
- Unlike the G2 flow, ring firmware is **not** part of the EVENOTA multi-image update package and is handled by Nordic secure DFU + MCUmgr in its own transport domain.

### Health Sensors

| Sensor | Metric | Protobuf Field |
|--------|--------|----------------|
| **Optical HR** | Heart rate (BPM) | `RingRawData.hr` |
| **Optical SpO2** | Blood oxygen (%) | `RingRawData.spo2` |
| **HRV** | Heart rate variability | `RingRawData.hrv` |
| **Temperature** | Skin temperature | `RingRawData.temp` |
| **Accelerometer** | Steps, calories | `RingRawData.steps`, `actKcal`, `allKcal` |
| **Wear detection** | On-wrist/off-wrist | (inferred from charge states) |

Health data is accessed via `RingRawData` protobuf on the G2 relay path (Ring→G2→Phone). Direct phone-to-ring health queries (`0xFE 0x01/02/03` on BAE80012) are not functional — the proprietary BAE80001 protocol for health data remains undocumented.

---

## 3. Firmware & DFU

| Property | Value |
|----------|-------|
| **Firmware format** | Nordic DFU package (NOT EVENOTA) |
| **Bootloader** | MCUboot with dual-image A/B slots |
| **DFU entry** | FE59 Buttonless Secure DFU service |
| **Firmware transfer** | SMP/MCUmgr Simple Management Protocol |
| **Signing** | ECDSA P-256 init packets |
| **Version boundary** | v2.03.00.01 (MCUmgr capabilities added) |

### DFU Update Path

```
Phone (Even.app)                          R1 Ring
    │                                        │
    │  1. Write to FE59 → enter bootloader   │
    │     ─────────────────────────────▶     │
    │     (ring resets into DFU mode)        │
    │                                        │
    │  2. Reconnect to DFU advertisement     │
    │     ─────────────────────────────▶     │
    │                                        │
    │  3. SMP/MCUmgr: upload firmware image  │
    │     ─────────────────────────────▶     │
    │                                        │
    │  4. SMP/MCUmgr: confirm + reset        │
    │     ─────────────────────────────▶     │
    │     (ring boots new image)             │
```

The R1 uses standard Nordic DFU — completely different from the G2's custom EVENOTA multi-component OTA. The G2 glasses have no role in R1 firmware updates.

### MCUmgr Capabilities (v2.03.00.01+)

| Capability | Detail |
|-----------|--------|
| **Filesystem** | On-device file access |
| **Crash dump** | Core dump retrieval |
| **Stats** | Runtime statistics |
| **Logs** | On-device log access |
| **Bootloader info** | MCUboot slot status |
| **SUIT** | Software Update for IoT (experimental) |
| **XIP** | Execute-in-place support |

---

## 4. Dual BLE Communication Architecture

The R1 ring maintains **two independent BLE connections**:

```
┌───────────────────┐          ┌────────────────┐
│     Phone         │◀── BLE ─▶│    R1 Ring     │
│                   │          │                │
│  Battery level    │          │  Gesture source│
│  Limited gestures │          │  Health sensors│
│  State sync       │          │                │
└───────────────────┘          └───────┬────────┘
                                    │ BLE
                                    ▼
                            ┌────────────────┐
                            │   G2 Glasses   │
                            │  (Right eye)   │
                            │                │
                            │  Full gestures │
                            │  Health relay  │
                            └────────────────┘
```

- **Ring ↔ Phone**: Battery level, hold/double-tap gestures, state sync. Uses BAE80001 service
- **Ring ↔ G2 (right eye)**: Full gesture set including swipes, single taps, scrolls. Not visible in phone BTSnoop captures
- The G2 right eye is the primary ring communication partner

---

## 5. R1 Ring BLE Specification

### Service UUID
```
BAE80001-4F05-4503-8E65-3AF1F7329D1F
```

### Characteristic UUIDs
| UUID | Handle | Purpose |
|------|--------|---------|
| `BAE80012-4F05-4503-8E65-3AF1F7329D1F` | ? | Write characteristic |
| `BAE80013-4F05-4503-8E65-3AF1F7329D1F` | ? | Notify characteristic |

### BLE Handles (from capture)
| Handle | Type | Purpose | Example |
|--------|------|---------|---------|
| 0x0020 | Notify | **Battery Level** | `6400` = 100% |
| 0x0021 | CCCD | Battery notifications | `0100` = enable |
| 0x0024 | Notify | **Gesture Events** | `ff0320` = HOLD |
| 0x0025 | CCCD | Gesture notifications | `0100` = enable |
| 0x0028 | Notify | **State/Menu Toggle** | `01`/`00` |
| 0x0029 | CCCD | State notifications | `0100` = enable |
| 0x002c | Read | Config/Version | `02010101` |
| 0x0030 | Write | Config commands | `fc`, `11` |

---

## Gesture Protocol

### Gesture Packet Format
```
[0xFF] [gesture_type] [parameter]
```

### Gesture Types
| Code | Gesture | Notes |
|------|---------|-------|
| `0x03` | **HOLD** | Long press - shows menu |
| `0x04` | **TAP** | Single/Double tap |
| `0x05` | **SWIPE** | Swipe gestures (up/down) |

### Parameter Values
| Value | Meaning |
|-------|---------|
| `0x01` | Single tap |
| `0x02` | Double tap |
| `0x20` | Hold (duration indicator?) |

### State Values (Handle 0x0028)
| Value | Meaning |
|-------|---------|
| `0x01` | Ready/Active |
| `0x00` | Menu/Selection mode |

---

## Capture Timeline vs Action Script

### Connection Sequence (23.7s - 24.1s)
```
23.74s  Enable battery notifications (0x0021)
23.80s  Battery: 100% (0x64)
23.81s  Enable gesture notifications (0x0025)
23.87s  Read config: 02010101
23.96s  Write config: fc
24.02s  Enable state notifications (0x0029)
24.08s  State: 01 (ready)
24.09s  Write config: 11
```

### Gesture Events

| Time | Packet | Decoded | Script Action |
|------|--------|---------|---------------|
| 24.42s | `ff0320` | **HOLD** (0x20) | Step 4: "Hold (menu appears)" ✓ |
| 25.81s | state=`00` | Menu opened | - |
| 26.27s | state=`01` | Menu closing | - |
| 26.27s | `ff0402` | **TAP** (double) | Step 6: "Double tap (menu disappears)" ✓ |
| [gap] | - | Gestures go R1→G2 | Steps 7-24: Swipes, taps, scrolls |
| 116.18s | state=`00` | Menu active | - |
| 159.55s | state=`01` | Menu closing | - |
| 159.55s | `ff0402` | **TAP** (double) | One of the later double taps |

### Missing Gestures (went R1→G2 directly)
- Steps 5, 8, 11: Swipe down
- Steps 7, 10: Hold
- Steps 13, 17, 20, 22, 24: Single tap
- Steps 14-15, 18: Scroll down/up
- Steps 16, 19, 21, 23: Double tap

---

## Ring Protobuf Messages 

### RingDataPackage (main envelope)
```protobuf
message RingDataPackage {
    eRingCommandId commandId = 1;  // 1=EVENT, 2=RAW_DATA
    int32 magicRandom = 2;
    optional RingEvent event = 3;
    optional RingRawData rawData = 4;
}
```

### RingEvent (gesture events)
```protobuf
message RingEvent {
    bytes ringMac = 1;
    eRingEvent eventId = 2;  // BLE_ADV=1
    int32 eventParam = 3;
    eErrorCode errorCode = 4;
}
```

### RingRawData (health metrics)
```protobuf
message RingRawData {
    int32 battery = 1;
    int32 chargeStates = 2;
    int32 hr = 3;             // Heart rate
    int32 hrTimestamp = 4;
    int32 spo2 = 5;           // Blood oxygen
    int32 spo2Timestamp = 6;
    int32 hrv = 7;            // Heart rate variability
    int32 hrvTimestamp = 8;
    int32 temp = 9;           // Temperature
    int32 tempTimestamp = 10;
    int32 actKcal = 11;       // Active calories
    int32 actKcalTimestamp = 12;
    int32 allKcal = 13;       // Total calories
    int32 allKcalTimestamp = 14;
    int32 steps = 15;
    int32 stepsTimestamp = 16;
    eErrorCode errorCode = 17;
}
```

---

## Config Values (Handle 0x002c, 0x0030)

### Read Config (0x002c)
```
02010101
```
Possibly: [type][major][minor][patch] = v1.1.1

### Write Config (0x0030)
- `fc` - Initialization command?
- `11` - Mode setting?

---

## Assistant/UI Channel Integration

When ring gestures trigger dashboard-like actions, the G2 glasses send state updates to the phone.  
In older notes this channel was called "Dashboard service"; current protocol docs classify `0x0720` as an Even AI/assistant service that may carry multiple UI command types.

```
Assistant/UI Service (0x0720):
- cmd=10 (0x0a): Dashboard navigation
- Contains page state, widget index, scroll position

DashboardMain Service (0x1020):
- cmd=1: Page state update
- field 3: Active widget type (News=1, Stock=2, etc.)
```

---

## iOS Implementation Details

**Source**: `R1Constants.swift`, `R1RingManager.swift`

### Initialization Sequence

After connecting to the ring, the following sequence is required:

1. Write `0xFC` (init command) to the write characteristic
2. Wait **200ms**
3. Write `0x11` (mode command) to the write characteristic

```swift
// R1GestureConstants.Config
initCommand  = 0xFC
modeCommand  = 0x11
configDelayNs = 200_000_000  // 200ms between init and mode
```

### Scanning & Discovery

The ring may not advertise its service UUID when already bonded to G2 glasses. A fallback scan by name prefix is used:

| Prefix | Notes |
|--------|-------|
| `Even Ring` | Primary name |
| `R1` | Short name |
| `EVEN_RING` | Uppercase variant |
| `EvenRing` | CamelCase variant |

Saved ring peripheral UUIDs are persisted in `R1KnownRingStore` for quick reconnection.

### Gesture-to-Glasses Forwarding

When the phone receives a ring gesture, it is decoded and forwarded to the G2 glasses:

| Ring Gesture | Ring Bytes | Forward Action | NUS Command |
|-------------|-----------|---------------|-------------|
| Single Tap | `FF 04 01` | NUS command | `F5 01` |
| Double Tap | `FF 04 02` | NUS command | `F5 00` |
| Swipe (param ≤ 1) | `FF 05 00/01` | Scroll forward | — |
| Swipe (param > 1) | `FF 05 02+` | Scroll backward | — |
| Hold | `FF 03 20` | Custom action | — |

Tap gestures are forwarded as NUS commands that simulate touchbar taps. Swipe gestures trigger scroll events processed by the active display feature. Hold triggers an application-defined custom action.

### Swipe Direction Heuristic

The swipe parameter determines direction:
- `param ≤ 0x01` → forward swipe
- `param > 0x01` → backward swipe

This heuristic was derived from BTSnoop captures; the exact meaning of the parameter value is not fully confirmed.

---

## Summary

| Component | Status |
|-----------|--------|
| Battery reading | Working |
| Gesture detection | Implemented (phone-side decode + forwarding) |
| State sync | Working |
| Health data | Available via RingRawData protobuf (G2 relay), not direct phone query |
| Config commands | Init sequence implemented (0xFC → 0x11) |
| Gesture forwarding | Ring → Phone → G2 via NUS |
| Saved ring store | Peripheral UUID persistence |
| DFU | Nordic FE59 + SMP/MCUmgr (independent from G2 EVENOTA) |

---

## Related Documents

- [../features/gestures.md](../features/gestures.md) — Complete gesture protocol across all input sources
- [../firmware/firmware-files.md](../firmware/firmware-files.md) — EVENOTA format (G2 only; R1 uses Nordic DFU)
- [r1-cradle.md](r1-cradle.md) — R1 Charging Cradle hardware
- [g2-glasses.md](g2-glasses.md) — G2 glasses that relay ring health data
