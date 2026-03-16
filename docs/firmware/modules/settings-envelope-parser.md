# Settings Envelope Parser (Root Oneof)

## Scope
- Firmware-only reconstruction of the `ProtoBaseSettings` root-envelope parser path.
- Focus on root oneof envelope handling (`case3..7`) and notify wrappers.
- Simulator parity work for inbound root case5 and unresolved case6/7 observability.

## Firmware Evidence (v2.0.7.16, `ota_s200_firmware_ota.bin`)
- Common parser/notify function: `0x4AACB4`.
  - Loads root descriptor pointer `0x727E44` from literal pool (`0x4AB134`).
  - Uses decode destination buffer at `0x20070908`.
  - Increments global magic/random counter at `0x20072948` and stages it into the outgoing parse struct.
  - Decode call sequence:
    - stream staging: `0x4A2298`
    - decode call: `0x4A28D6(..., 0x727E44, 0x20070908)`
  - Success route call:
    - `0x46F6EA(r0=1, r1=9, r2=0x2006E804, r3=[sp+0x18])`
    - `r3` is the staged envelope route/subcase selector used by the shared dispatcher lane.
- BL-target callsite sweep for `0x4AACB4` in v2.0.7.16 found 3 callers:
  - `0x4AAFA0` (inside wrapper `0x4AAF04`, after helper `0x4AA60E`)
  - `0x4AB016` (inside wrapper `0x4AAFB4`, case5/subcase1 path)
  - `0x4AB098` (inside wrapper `0x4AB02C`, case5/subcase2 path; internal callsite, not a standalone wrapper)
- Wrapper callgraph resolution artifact (binary disassembly):
  - `captures/firmware/analysis/2026-03-05-settings-notify-wrapper-callgraph-resolution.json`
  - `captures/firmware/analysis/2026-03-05-settings-notify-wrapper-callgraph-resolution.md`
- Device-status wrapper lane map artifact:
  - `captures/firmware/analysis/2026-03-05-settings-device-status-wrapper-case4-map.json`
  - `captures/firmware/analysis/2026-03-05-settings-device-status-wrapper-case4-map.md`
- Root case5 wrappers feeding this parser:
  - `0x4AAFB4` (`setting_notify_recalibration_status_to_app`)
    - staged fields before `0x4AACB4`:
      - `+0x00 = 3` (command lane)
      - `+0x08 = 5` (root case5)
      - `+0x0C = 1` (case5/subcase1)
      - `+0x10 = status`
  - `0x4AB02C` (`notify_silent_mode_to_app`)
    - staged fields:
      - `+0x00 = 3`
      - `+0x08 = 5`
      - `+0x0C = 2` (case5/subcase2)
      - `+0x10 = status`
- Cross-version wrapper sweep (`v2.0.1.14`, `v2.0.3.20`, `v2.0.5.12`, `v2.0.6.14`, `v2.0.7.16`):
  - Searched staging write patterns for root-case selector at `struct+0x14`.
  - Observed root-case staging with value `5` (case5 wrappers) in every version.
  - No direct root-case staging wrappers with value `6` or `7` were found in these builds.
  - This strengthens the hypothesis that root `case6/7` are descriptor-declared but not actively produced by known notify wrappers in current firmware line.
  - Repro artifacts:
    - `captures/firmware/analysis/2026-03-05-settings-root-case-wrapper-sweep.json`
    - `captures/firmware/analysis/2026-03-05-settings-root-case-wrapper-sweep.md`

## Descriptor Context
- Root descriptor: `0x727E44`.
- Root case table includes:
  - case3 selector payload (`0x727F1C`)
  - case4 local-data payload (`0x727F34`)
  - case5 notify-group payload (`0x727F4C`)
  - case6 scalar payload (`0x727FDC`)
  - case7 scalar payload (`0x727FF4`)

## Simulator Parity Updates
- `g2-mock-firmware/src/ble_core.cpp`:
  - Added inbound root case5 payload decode (`subcase/status`) when selector lane is absent.
  - Applied case5 state effects:
    - subcase1 recalibration status updates calibration UI shadow (`tag17` lane) and gate shadow.
    - subcase2 updates silent-mode shadow (`ctx+0x15`).
  - Added root case6/7 shadow capture (first field, wire type, first scalar, blob length, seen count) for repeatable firmware-wave analysis.
  - Added compact settings-status notify lane on `0x0D-01` (capture-derived payload family):
    - `f1=1`, `f3={f1=event[,f2=status]}`
    - simulator compact packets are sourced from shared `config_state` mode transitions (module lanes), not selector-specific direct emits
  - Added paired selector4/subtype3 transition notify behavior:
    - case5/subcase1 notify (`status=0/1`)
    - followed by case4 local-data status notify (`0x4AAF04` parity path)
  - Kept root case routing non-fallback behavior (`case5..7` do not enter legacy `cmdId` lane).
  - Added runtime observability hook `settings status` in serial console to print selector/context shadow state, root case6/7 capture counters, and compact-notify shadow telemetry.
  - Compact notify capture evidence + simulator mapping details are tracked in [settings-compact-notify.md](settings-compact-notify.md).

## Next Actionable Improvements
1. Recover concrete producer/consumer paths for root case6/7 (`0x727FDC`/`0x727FF4`) and map them to app-visible commands/events.
2. Resolve `0x4AAF04` on-wire emission conditions (ordering, channel reuse, and empty companion behavior) under each caller context after the now-resolved field map.
3. Trace `0x46F6EA` dispatch argument `r3=[sp+0x18]` into downstream settings command handlers and recover canonical route enum names.
4. Add replay fixtures that inject root case5 payloads (`subcase1/2`) and assert shadow/state side effects (`tag17`, `ctx+0x15`) on simulator output lanes.
