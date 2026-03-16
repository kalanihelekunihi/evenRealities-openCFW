# Settings and State Model

This document is the clean-room state-model summary for the `0x0D` settings path. It records the currently identified selector/root structure, the still-inferred state writers, and the unresolved lanes that should not yet be treated as authoritative compatibility behavior.

## Identified Envelope Structure

### Root Cases

| Root Case | State | Meaning |
|---|---|---|
| `case3` | Identified | selector-dispatch receive path |
| `case4` | Identified | local-data/status response lane |
| `case5` | Identified | notify-group/status lane |
| `case6` | Unidentified | captured but not closed |
| `case7` | Unidentified | captured but not closed |

### Selector Space

The selector oneof under root `case3` is strongly anchored for selectors `1..11`.

| Selector | State | Identified Meaning |
|---|---|---|
| `1` | Partial | query/basic snapshot path with subtype/context side effects |
| `2` | Identified | scalar context write |
| `3` | Identified | scalar context write |
| `4` | Partial | head-up and calibration-related subtypes |
| `5` | Identified | wear-detection enable path |
| `6` | Partial | scalar write with notify/log side effects |
| `7` | Identified | no-op branch |
| `8` | Partial | guarded call/gate path |
| `9` | Partial | structured context update block |
| `10` | Partial | record-list/bank update block |
| `11` | Partial | single-byte context update block |

## Identified Runtime State Lanes

### Core State

| Area | State | Notes |
|---|---|---|
| Wear detection enable | Identified | selector `5` calls the wear-enable path |
| Brightness/manual state | Identified | settings own the user-facing brightness state path |
| Calibration notify path | Identified | selector `4` subtype `3` drives recalibration notify behavior |
| Silent-mode notify path | Identified | root `case5` subcase `2` exists and is emitted from settings helpers |
| Local-data response envelope | Identified | root `case4` is a separate response lane, not a selector payload |

### Local-Data Tags

The following `case4` local-data tags are strong enough to carry into clean-room modeling:

| Tag | State | Current Meaning |
|---|---|---|
| `12` | Partial | battery-percent lane |
| `13` | Partial | charge-state/trend lane |
| `17` | Partial | calibration-UI/showing lane |
| `18` | Identified | auto-brightness enable lane |
| `19` | Partial | unread-message-count lane |

## Inferred but Not Fully Closed

| Area | Current Inference | Why It Is Not Fully Closed |
|---|---|---|
| Selector `1` subtype meanings | basic snapshot/query behavior plus context side effects | subtype enum semantics are still incomplete |
| Selector `4` full subtype map | head-up switch, angle, and calibration gating all live here | some side-effect lanes are still unresolved |
| Selector `6` state meaning | writes context and emits notify-side effects | exact user-facing feature ownership is incomplete |
| Selector `8` gate path | guarded feature or mode toggle | exact feature meaning is still unclear |
| Selector `9/10/11` state blocks | structured runtime context and banked writes | exact app-visible side effects after `0x463F0E` are still open |
| Local-data tag `11` | dashboard callback/session or similar event-driven boolean lane | exact meaning is still not closed |
| Notify wrapper relationships | case5 and case4 paired emits are real and stateful | full emission conditions are not fully closed |

## Unidentified / Still Open

| Area | Why It Matters |
|---|---|
| Root `case6` and `case7` | these are still active envelopes but their producer/consumer roles are not authoritative |
| Full tag map for local-data response lane | needed for exact state compatibility |
| Exact meaning of local-data `tag11` | affects app-visible state parity |
| Exact post-write event behavior after selectors `9/10/11` | needed for authoritative async-notify compatibility |
| Exact emission conditions for the paired device-status wrapper path | needed before claiming notify parity |

## Clean-Room Guidance

- Implement the `0x0D` path with explicit separation between selector writes, local-data reads, and notify-group emissions.
- Treat `case6` and `case7` as capture-only until their contracts close.
- Keep unresolved local-data tags and structured selector side effects behind instrumentation.
- Do not flatten all settings traffic into a single `cmdId`-style compatibility layer.

## Source Documents

- `../firmware/modules/settings-dispatch.md`
- `../firmware/modules/settings-selector-schema.md`
- `../firmware/modules/settings-local-data-status.md`
- `../firmware/modules/settings-headup-calibration.md`
- `../firmware/modules/settings-envelope-parser.md`
- `../firmware/modules/settings-compact-notify.md`
- `../firmware/re-gaps-tracker.md`
