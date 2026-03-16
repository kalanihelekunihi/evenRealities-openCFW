# Display Config Module (0x0E)

## Scope
- Command service: `0x0E-20`
- Feedback/response service: `0x0E-00`
- Used alongside display-mode/config transitions before render-heavy modules.

## Firmware Evidence (Binary)
- `CONVERSATE_UI_EVENT_DISPLAY_CONFIG` at `ota_s200_firmware_ota.bin:0x002CE540`
- Indicates display-config integration into UI/event pipeline, not a pure write-only sink.

### v2.0.7.16 Brightness Evolution
- `[display_thread]JBD_CHANGE_BRIGHTNESS no use now` — direct JBD4010 MSPI display brightness path deprecated
- `ALSSyncHandler` — ambient light sensor (OPT3007) auto-brightness sync between eyes via inter-eye UART
- `[sensor_als]ALS polling, als_value:%d, peak_value:%d, brightness_level_converted:%d, current_brightness_level:%d` — ALS polling with peak tracking
- `[sensor_als]ALS start read data success, als value:%d, brightness_level_converted:%d` — ALS read → brightness conversion
- `[sensor_als]ALSSyncHandler, data length error, len:%d` — inter-eye sync validation
- `[sensor_als]ALSSyncHandler, recv brightness_level:%d, notify_app:%d` — right eye receives synced level from left eye master
- Brightness is now exclusively ALS-driven: OPT3007 → left eye computation → inter-eye UART sync → both JBD4010 displays updated in lockstep

## Capture Evidence (2026-03-02)
From `captures/20260302-3-testAll/display-config.txt`:
- `0x0E-20` TX payloads are stable `f1=2` envelopes with region/fixed32 viewport data.
- `0x0E-00` RX emits 14 unique protobuf payloads in this run.

Observed `0x0E-00` pattern families:
- Type A: `f1=4, f2=<counter>, f6={f1={f1=5}}`
- Type B: `f1=2, f2=<counter>, f4={f1=1}`
- Type C: `f1=1, f2=<counter>, f3={f1=(2|3), f2=(10000|2000), f3=float32}`

Examples from capture:
- `080410a80132040a020805...`
- `080210a90122020801...`
- `080110aa011a0a080310d00f1d00208d44...`

## Current Simulator Behavior (`g2-mock-firmware/src/ble_core.cpp`)
- On each `0x0E-20` write:
  - emits one capture-backed feedback packet on `0x0E-00`
  - continues emitting config mode notify (`0x0D-01`, render mode)
- Feedback cycle models the three observed packet families with realistic counters and fixed32 payloads.

## Next Actionable Improvements
1. Correlate `0x0E-00` variant timing with specific caller modules (teleprompter/conversate/evenai/navigation).
2. Validate whether firmware counter source for `f2` is global seq, module-local, or mixed.
3. Add a deterministic profile mode for tests that replays the exact 14-packet `20260302-3` sequence.
4. Trace ALS→brightness pipeline: determine exact conversion curve from OPT3007 raw lux to DAC brightness level (0–42 range), and whether ALSSyncHandler replaces or supplements the existing `0x0D-00` brightness settings path.
