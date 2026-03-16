# Device State and Role Model

This document is the clean-room model for peer roles, battery and charging state, wear state, case state, and ring state in the G2 system.

## Domain Matrix

| Domain | State | Main Surfaces | Identified Today | Main Gaps |
|---|---|---|---|---|
| Left/right identity and peer roles | Partial | BLE identity, `uart_sync`, peer sync, role branches | Shared firmware image, runtime-selected identity, explicit master/slave branches | Exact per-feature authority split |
| Battery and charging state | Partial | proprietary status paths, settings local-data, case relay | No standard Battery Service, battery and charging state are first-class runtime concepts | Exact field ownership across services |
| Wear state | Identified with bounded unknowns | settings `0x0D`, onboarding `0x10`, wear module | enable/status query path and gating behavior are real | Exact selector wire contract and side effects |
| Case state | Partial | `glasses_case`, `0x81` BoxDetect, `0x0D` case status | case battery, charging, and in-case state are relayed through glasses | Final field grammar and notify coupling |
| Ring state | Partial | `0x91` relay, `BAE80001` runtime, ring raw-data protobufs | ring battery/state/health concepts are real | Exact command vocabulary and ownership split |

## Identified State Surfaces

### Peer-role and identity framework

- Left and right eyes run the same firmware image.
- Runtime identity is selected by role and BLE naming rather than by build.
- The runtime contains explicit master/slave branches for the peer-sync path.
- Current evidence supports left-eye master and right-eye slave behavior at the transport/synchronization level.
- Dominant hand is a separate user preference and should not be confused with physical eye role.

### Power and charging model

- G2 does not have a confirmed standard BLE Battery Service (`0x180F`) contract.
- Battery and charging state are carried through proprietary status surfaces.
- Power state is real enough to gate OTA prerequisites and user-facing state.
- Settings/runtime evidence shows dedicated state lanes for battery- and charge-adjacent values.

### Wear state

- Wear detection has an enable switch and a current wear/unwear status.
- Wear state is queryable through settings behavior and also reported into onboarding flows.
- Wear state gates at least input acceptance and display-related control behavior.
- Touch/proximity hardware and wear state are coupled, but the logic is Apollo-visible rather than hidden entirely inside the touch controller.

### Case state

- The case has no direct BLE link to the phone.
- Case battery, charging, and in-case state are relayed through the glasses.
- `GlassesCaseInfo` and BoxDetect/state paths make case state implementation-relevant even before the full UART grammar is closed.

## Inferred but Not Fully Closed

### Peer-role authority

- Right-eye primacy for microphone and ring-facing work is strongly suggested.
- Some master-side coordination still appears around ring and peer state.
- Exact role/authority split per feature remains mixed in local evidence.

### Power/status field mapping

- Settings local-data lanes strongly suggest:
  - `tag12` -> battery percent
  - `tag13` -> charge-state or charge-trend
  - `tag11` -> dashboard/session-related boolean
  - `tag17` -> calibration-UI state
- These are good implementation hints, but not yet final authoritative field truth.

### Pipe-role and alternate-pipe semantics

- `PIPE_ROLE_CHANGE` and alternate UUID anchors (`5450/6450/7450`) clearly participate in stateful channel selection or coordination.
- The exact behavior is not yet closed enough to treat as a stable runtime contract.

### Ring and case state coupling

- Ring direct BLE plus `0x91` relay likely expose overlapping but not identical state.
- Case relay and BoxDetect likely share some power/display-trigger coupling beyond the minimal case-info story.

## Unidentified / Blocked Areas

- Exact per-feature left/right/master/slave ownership.
- Exact mapping between proprietary battery/charging fields across `0x09`, `0x0D`, `0x81`, and app callbacks.
- Exact `PIPE_ROLE_CHANGE` and alternate-pipe semantics.
- Exact case4 `tag11` meaning and authoritative producer ownership for `tag12/13/17`.
- Exact ring connect-state, timeout, and health-readiness semantics.
- Exact boundary between case state, peer state, and local state when the glasses are docked or charging.

## Clean-Room Rules

- Keep peer-role management separate from user preferences such as dominant hand.
- Preserve proprietary battery, charging, wear, and case-state paths first instead of inventing generic BLE service mappings.
- Treat state producers as multi-source: local runtime, peer eye, case relay, and ring relay/direct BLE may all contribute.
- Keep unresolved field maps behind instrumentation rather than hard-coding one guessed status schema.

## Source Documents

- `../firmware/modules/ble-multi-connection.md`
- `../firmware/modules/settings-local-data-status.md`
- `../firmware/modules/settings-runtime-context.md`
- `../firmware/modules/wear-detection.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/firmware-communication-topology.md`
- `../firmware/even-app-reverse-engineering.md`
- `../devices/g2-glasses.md`
- `../devices/g2-case.md`
- `../devices/r1-ring.md`
