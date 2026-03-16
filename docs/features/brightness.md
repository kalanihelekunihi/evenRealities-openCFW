# Brightness Protocol

Brightness control for the G2 glasses operates through protobuf-encoded commands on the configuration service. The G1-era raw byte format does NOT work on G2.

**Source**: `G2BrightnessSender.swift`, `G2ConfigurationReader.swift`

## 1) G2 Brightness Protocol (Primary Path)

### Service ID

Configuration: `0x0D-0x00` (same service as G1, but G2 expects protobuf payloads, not raw bytes)

### Protobuf Schema (from Even.app RE)

G2 brightness uses `G2SettingPackage` protobuf with `commandId = DEVICE_BRIGHTNESS`:

```
G2SettingPackage {
  commandId: DEVICE_BRIGHTNESS
  payload: DeviceReceive_Brightness {
    brightnessLevel: <int>
  }
}
```

Related methods from Even.app (`ProtoBaseSettings` extension):
- `setBrightness(level)` — set brightness level
- `setBrightnessAuto(enabled)` — toggle auto-brightness
- `setBrightnessCalibration(left, right)` — per-eye calibration (`leftMaxBrightness`, `rightMaxBrightness`)
- `APP_REQUIRE_BRIGHTNESS_INFO` — query current brightness state

### Scale

- **UI scale**: 0-100% (confirmed from Even.app localization keys: `brightness_set_to_80`, `brightness_set_to_2`)
- **Internal scale**: Likely 0-42 DAC steps (our current implementation) or 0-100 percentage — exact field number mapping TBD
- **Per-eye calibration**: `leftMaxBrightness` / `rightMaxBrightness` allow independent brightness limits

### Status

**Protobuf field numbers are still unknown.** We can confirm the service ID (0x0D-00) and the general structure, but the exact protobuf field numbers for `commandId`, `brightnessLevel`, and auto-brightness flag need wire capture of the official Even.app brightness flow.

Our current implementation sends G2SettingPackage-style protobuf to 0x0D-00. The `G2ConfigurationReader` can query settings from 0x0D-00 and decode brightness, autoBrightness, and other config fields.

## 2) EvenAI SKILL Path (Secondary)

Brightness can also be set via the EvenAI SKILL command system on service 0x07-20:

- **Skill ID 0**: `BRIGHTNESS` — set brightness level
- **Skill ID 7**: `AUTO_BRIGHTNESS` — toggle auto-brightness

SKILL type 6 on 0x07-20 is confirmed responsive (testAll-2 2026-03-02: echo + COMM_RSP). This path is used by the Even AI voice assistant ("set brightness to 80%").

## 3) Display Wake Echo (Observation Only)

When brightness data is sent to 0x04-20 (DisplayWake), the response on 0x04-00 includes a COMM_RSP with brightness information:

```
f1=161 (0xA1), f5={f1=brightness_level, f2=8}
```

This is a **response containing the current brightness level**, not a brightness setter. It appears alongside the standard DisplayWake ACK (`f1=1, f3=empty`).

## 4) Deprecated: G1 Raw Byte Format

The original G1-derived protocol sends raw bytes to 0x0D-00:

```
[0x01] [level (0-42)] [auto (0/1)]
```

This does **NOT work on G2**. The G2 expects protobuf-encoded `G2SettingPackage` on the same service ID. Sending raw bytes produces no visible effect and no response.
