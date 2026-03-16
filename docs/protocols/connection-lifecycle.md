# BLE Connection Lifecycle & Error Handling

This document covers the G2 BLE connection flow, error classification, and reconnection behavior.

**Source**: `G2BluetoothClient.swift`, `G2BLEErrorClassifier.swift`, `G2ConnectionHelper.swift`, `G2KnownGlassesStore.swift`

## Connection Flow

```
┌──────────┐    ┌─────────┐    ┌──────────┐    ┌──────┐    ┌─────────┐
│   Scan   │───▶│ Connect │───▶│ Discover │───▶│ Auth │───▶│ Feature │
│          │    │         │    │ Services │    │      │    │   Use   │
└──────────┘    └─────────┘    └──────────┘    └──────┘    └─────────┘
     │                                                          │
     │  Quick-connect                                           │
     │  (saved UUID)                                            ▼
     └──────────────────────────────────────────────────── Disconnect
```

### 1. Scan

Two paths to find glasses:

**Quick-connect** (preferred): Use a saved peripheral UUID from `G2KnownGlassesStore`. Calls `CBCentralManager.retrievePeripherals(withIdentifiers:)` to get the peripheral directly, skipping BLE scanning.

**Scan-based**: Scan for devices advertising the G2 service. Filter by name prefix `Even G2_`. Minimum scan duration is 1.5 seconds to catch multiple advertising cycles.

**Missing-eye recovery**: If one eye quick-connects and the other eye is still missing, `G2Session` now performs a targeted scan/connect pass for the missing side before auth. This avoids persistent one-eye degraded sessions when only one saved UUID is valid.

| Parameter | Value |
|-----------|-------|
| Quick-connect timeout | 15 seconds |
| Scan timeout | 10 seconds |
| Scan retries | 2 attempts |
| Direct connect retries | 3 attempts |
| Minimum scan duration | 1.5 seconds |
| RSSI warning threshold | -70 dBm |

### 2. Connect

After finding a peripheral, establish the BLE connection. MTU is negotiated to 512 bytes (247 effective after ATT overhead).

### 3. Discover Services

Enumerate characteristics on the control channel:
- 0x5401 (Control Write)
- 0x5402 (Control Notify)
- 0x7401 (File Write)
- 0x7402 (File Notify)
- 0x6402 (Display Write) — optional
- 0x6401 (Display Notify) — optional

Enable notifications on 0x5402, 0x7402, and optionally 0x6402.

### 4. Authenticate

Send 3-packet (fast) or 7-packet (full) auth sequence. See [authentication.md](authentication.md).

### 5. Feature Use

Send commands, receive responses. Connection stays alive with periodic heartbeats. See [heartbeat.md](heartbeat.md).

### 6. Disconnect

Two disconnect paths:

**Transient connection**: `withSingleEye`/`withBothEyes` connects, runs a closure, then disconnects automatically. A post-send keepalive delay (default 3 seconds) keeps the connection open briefly for any pending responses.

**Persistent session**: `G2Session` maintains a long-lived connection with automatic reconnection and periodic heartbeats.

## Session State Machine

```
disconnected ──▶ connecting ──▶ connected ──▶ disconnected
                     │                            ▲
                     └── (error) ─────────────────┘
```

## Error Classification

BLE errors are classified into three severity levels that determine retry behavior:

### Retryable

Transient errors — auto-retry with exponential backoff.

| CBError Code | Max Retries | Initial Delay |
|-------------|------------|---------------|
| `connectionTimeout` | 3 | 500ms |
| `peripheralDisconnected` | 3 | 1000ms |
| `connectionLimitReached` | 2 | 2000ms |

### Fatal

Non-recoverable errors — surface to user, do not retry.

| Error | Domain |
|-------|--------|
| `peerRemovedPairingInformation` | CBError |
| `encryptionTimedOut` | CBError |
| `operationNotSupported` | CBError |
| `insufficientAuthentication` | CBATTError |
| `insufficientEncryption` | CBATTError |

### Degraded

Unknown errors — continue with a warning.

| Condition | Behavior |
|-----------|----------|
| Unknown CBError code | Log warning, attempt reconnect |
| Unknown ATT error | Log warning, continue |
| Non-CoreBluetooth error | Log warning, continue |

## Degraded Single-Eye Recovery

When one eye disconnects but the other remains connected, `G2Session` now:

1. Enters degraded mode (`left-only` or `right-only`)
2. Starts bounded background recovery attempts for the missing eye:
   - quick-connect from saved UUID
   - targeted scan/connect for the missing side if quick-connect fails
   - auth handshake for the newly attached eye before normal feature traffic
3. Exits degraded mode automatically after both eyes are restored

If recovery attempts are exhausted, the session stays active in degraded mode and the existing watchdog/full reconnect path remains available.

## Disconnect Handling

When a peripheral disconnects:

1. **Cancel pending writes** for that specific peripheral (per-peripheral, not global)
2. **Classify the error** using `G2BLEErrorClassifier`
3. **Take action based on severity**:
   - **Retryable**: Attempt background reconnection via `central.connect(peripheral)`
   - **Fatal**: Clear saved peripheral UUID, do not retry
   - **Degraded**: Attempt background reconnection with warning

## Pairing Removal Behavior

When the glasses report `peerRemovedPairingInformation`:

1. The error is classified as **fatal**
2. The saved peripheral UUID is cleared from `G2KnownGlassesStore`
3. No reconnection is attempted
4. The glasses stop advertising — subsequent scan attempts will time out
5. The user must re-pair via the Devices screen

**Observed behavior**: After a timeout disconnect (e.g. app backgrounding), the glasses may escalate to pairing removal within ~1 minute if the device doesn't reconnect. This is firmware behavior and cannot be changed from the app side.

## Saved Peripheral Store

`G2KnownGlassesStore` persists peripheral UUIDs in UserDefaults for quick-connect:

| Method | Purpose |
|--------|---------|
| `save(left:right:)` | Save both eye UUIDs after successful pairing |
| `save(side:peripheral:)` | Save one eye UUID |
| `loadPeripheralIdentifiers()` | Load both saved UUIDs |
| `loadPeripheralIdentifier(side:)` | Load one saved UUID |
| `clear()` | Clear both saved UUIDs |
| `clear(side:)` | Clear one side's UUID |
| `clear(peripheralId:)` | Clear by matching UUID against both sides |

## Test Suite Short-Circuit

The `runAllTests()` test runner short-circuits on connection loss:

- If the **BLE Connection** test (test #1) fails, all remaining tests are skipped
- If **3 consecutive tests** fail, the runner assumes connection is lost and skips the rest
- Skipped tests are recorded as "Skipped (connection lost)" with 0 duration
