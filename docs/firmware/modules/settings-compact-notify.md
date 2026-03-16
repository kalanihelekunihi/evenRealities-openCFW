# Settings Compact Notify Lane (`0x0D-01`)

## Scope
- Firmware-runtime compact settings/status packets on `0x0D-01`.
- Event tuple shape: `f1=1`, `f3={f1=event[,f2=status]}` (or empty `f3`).
- Simulator parity target for iOS automation behavior matching firmware-observed transitions.

## Firmware + Capture Evidence
- Common settings parser/notify lane remains `0x4AACB4` (v2.0.7.16 main OTA image).
- BL-target sweep for `0x4AACB4` still shows 3 callsites:
  - `0x4AAFA0`
  - `0x4AB016`
  - `0x4AB098` (internal callsite inside wrapper `0x4AB02C`, case5/subcase2 path)
- Full capture sweep across local `captures/**/*.txt` finds `214` compact `0x0D-01` packets with 5 payload families:
  - `08011a00` (`event=0`) — 74
  - `08011a020806` (`event=6`) — 72
  - `08011a02080b` (`event=11`) — 28
  - `08011a0408061007` (`event=6,status=7`) — 24
  - `08011a020810` (`event=16`) — 16
- Repro artifacts:
  - `captures/firmware/analysis/2026-03-05-settings-compact-notify-capture-sweep.json`
  - `captures/firmware/analysis/2026-03-05-settings-compact-notify-capture-sweep.md`
  - `captures/firmware/analysis/2026-03-05-settings-notify-wrapper-callgraph-resolution.json`
  - `captures/firmware/analysis/2026-03-05-settings-device-status-wrapper-case4-map.json`

## Direction-Aware Service Correlation
- Additional correlation sweep over direction-aware logs (`TX`/`RX` or `Sent:`/`Response:` records):
  - `5135` packets across 9 local capture files.
  - `115` compact events had a nearest-prior TX candidate in-file.
- Strongest event-to-service correlations:
  - `event=16` -> preceding `0x06-0x20` (`8/8`, 100%)
  - `event=11` -> preceding `0x0B-0x20` (`12/13`, 92.31%)
  - `event=6,status=7` -> preceding `0x07-0x20` (`13/13`, 100%)
  - `event=6` (no status) -> split across `0x06-0x20`, `0x07-0x20`, `0x0B-0x20` (`13/13/13`)
  - `event=0` -> clustered near `0x80-0x20`, `0x0B-0x20`, `0x06-0x20`
- Repro artifacts:
  - `captures/firmware/analysis/2026-03-05-settings-compact-notify-service-correlation.json`
  - `captures/firmware/analysis/2026-03-05-settings-compact-notify-service-correlation.md`

## Simulator Parity (`g2-mock-firmware`)
- Compact `0x0D-01` packets are now modeled as a `config_state` output lane, not a settings-selector-side emitter.
- `config_state` owns compact payload generation and shadow state:
  - `config_state_notify(mode, extended)`
  - `config_state_reset()`
  - `config_state_close()` (render + reset pair)
  - `config_state_get_notify_shadow(...)`
  - `config_state_reset_notify_shadow()`
- `ble_core.cpp` no longer emits speculative compact events from:
  - selector `6`
  - selector `11`
  - legacy wakeup-angle cmd `16`
- Serial observability (`settings status`) now reports compact shadow values from `config_state`, alongside selector/root-case shadows.

## Current Interpretation
- Capture + simulator alignment is strongest when compact events are treated as module/mode transitions:
  - teleprompter lane (`0x06`) contributes `event=16` and `event=6`
  - conversate lane (`0x0B`) contributes `event=11` and `event=6`
  - evenAI lane (`0x07`) contributes `event=6,status=7` and `event=6`
- Callgraph resolution narrows `0x4AB098` to an internal case5/subcase2 wrapper branch; remaining ambiguity for empty packets shifts to when device-status wrapper `0x4AAF04` emits on-wire versus other notify paths.
- Empty companion packets (`event=0`, payload `08011a00`) remain frequent and still require concrete producer mapping in firmware.

## Next Actionable Improvements
1. Resolve exact `0x4AAF04` emission conditions and determine when/if those outputs account for empty companion packets (`08011a00`) versus case5 wrapper traffic.
2. Trace `0x46F6EA(r1=9)` downstream route labels to recover canonical names for compact event IDs (`6/11/16`) and status semantics.
3. Add replay tests that assert compact notify sequences per module transition (`0x06/0x07/0x0B`) and close/reset behavior.
4. Tighten correlation by adding sequence/time-window analysis (not only nearest-prior line) for captures that include mixed multi-eye traffic.
