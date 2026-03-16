# Lifecycle and Orchestration Model

This document is the clean-room model for the runtime lifecycle plane that sits between startup/state handling and feature-specific payload services in the G2 firmware. It covers idle monitoring, compact mode transitions, onboarding, head-up dashboard wake behavior, timeout/auto-close policy, and alert/close orchestration.

## Lifecycle Matrix

| Domain | State | Main Evidence | Identified Constraints | Remaining Gaps |
|---|---|---|---|---|
| Idle monitor and scheduler handoff | Partial but executable | device boot call trees, system monitor call-chain recovery, service map | `0xFF` is a real lifecycle-facing monitor lane and the scheduler idle handoff is executable | exact `0xFF` payload schema and full monitor event vocabulary |
| Compact feature-mode transition lane | Identified with bounded unknowns | display pipeline, compact-notify module, service correlation | modes `0`, `6`, `11`, and `16` are real runtime modes rather than guessed app labels | exact producer of empty companion packets and final status-field semantics |
| Onboarding first-run flow | Partial but executable | service map, module index, app RE | `0x10` is a real dedicated service with staged onboarding behavior | exact command ids, field grammar, and notify timing |
| Head-up dashboard wake path | Partial | head-up calibration notes, app RE, firmware RE | head-up angle, dashboard trigger, and head-up calibration are distinct lifecycle surfaces | exact wire contract and final ownership split with settings/calibration |
| Auto-close and timeout policy | Partial | display pipeline, settings sync/module-config notes, service docs, firmware module summaries | timeout/exit paths return runtime mode to idle and dashboard auto-close is persisted separately | exact per-feature timer ownership and full timeout table |
| Alert and close-confirmation services | Partial | services docs, firmware module summaries, app RE | `0x21` and `0x22` are dedicated lifecycle-facing services, not generic feature aliases | exact event ids, action enums, and side effects |
| DisplayTrigger / case-coupled wake adjunct | Partial | services docs, firmware RE, module summaries | `0x81` is active and participates in both case-state and display-trigger-adjacent behavior | exact meaning of `f3.f1=67` and final lifecycle role |

## Identified Lifecycle Contracts

### Idle Versus Active Is an Explicit Runtime Plane

- The runtime has a dedicated monitor path on `0xFF`.
- The recovered monitor handler is tied to an idle-command handoff into the scheduler rather than to a generic feature ACK path.
- Runtime display-facing activity is also exposed on `0x0D-01`, which means feature visibility and idle state are explicit state surfaces, not something `openCFW` should infer only from the last packet written.

### Compact Mode Changes Are Real Runtime Transitions

- Current local evidence closes these compact-mode values:
  - `0` = idle/reset
  - `6` = render-family active
  - `11` = conversate active
  - `16` = teleprompter active
- Direction-aware capture correlation ties these events to `0x06`, `0x07`, and `0x0B` activity rather than to direct selector writes.
- Clean-room implication: mode transitions belong in an orchestration layer, not inside individual payload encoders.

### Onboarding Is a Dedicated Staged Lifecycle

- `0x10-20` is a real service with delayed ACK behavior.
- Local app and firmware evidence close a staged onboarding flow with steps for:
  - gesture/video guidance
  - wear check
  - head-up calibration
  - notification setup
  - reconnect/disconnect handling
  - completion
- `setOnBoardingStartUp`, `setOnBoardingStart`, and `setOnBoardingEnd` are real app-facing operations.
- Clean-room implication: onboarding should remain a dedicated lifecycle state machine instead of being flattened into generic settings writes.

### Head-Up Dashboard Wake Is Separate From Standard Display Wake

- Head-up behavior is a distinct product feature, not just a different value on normal display wake.
- `setHeadUpAngle` and `setHeadUpTriggerDashboard` exist separately in app evidence.
- Head-up calibration is tied to onboarding and to the calibration-state surfaces recovered in settings and sensor docs.
- Clean-room implication: preserve a separate motion-triggered dashboard wake policy instead of merging it into ordinary `0x04` display activation.

### Timeout and Auto-Close Policy Are First-Class Inputs

- Dashboard auto-close is persisted through the settings/module-config family and supports a disable sentinel `0xFF55`.
- Conversate emits an explicit timeout-style close notification on `0x0B-01`.
- Display-facing runtime docs close the broader rule that shutdown, exit, or timeout transitions return the runtime to idle mode.
- Clean-room implication: feature close policy should be modeled as explicit timers/configuration, not as implicit client-side cleanup.

### Alert, Close, and DisplayTrigger Services Are Separate Orchestration Lanes

- `0x21` (SystemAlert), `0x22` (SystemClose), `0x81` (BoxDetect/DisplayTrigger), and `0xFF` (SystemMonitor) are all real runtime services.
- These lanes participate in user-visible state changes, close/confirm flows, case/display triggers, or scheduler lifecycle behavior.
- Clean-room implication: keep them separate from feature-content handlers even before every field table is fully closed.

## Inferred Lifecycle Behavior

### A Shared Orchestration Owner Likely Sits Above Feature Services

- Compact mode changes, timeout-driven exits, onboarding stages, and alert/close flows likely converge on one shared orchestration owner rather than being isolated logic inside each feature service.
- The exact owning module name is still open, but the architectural boundary is strong enough to preserve in `openCFW`.

### Head-Up, Calibration, and Dashboard Wake Likely Share One Policy Family

- Head-up calibration state, head-up dashboard trigger settings, and dashboard auto-close behavior likely feed one broader motion/display lifecycle policy.
- The clean-room architecture should preserve these inputs separately until the exact wire schema closes.

### Empty `0x0D-01` Companion Packets Likely Mark Close or Reset Fences

- Capture correlation puts `event=0` packets near feature-close and reset-adjacent traffic.
- They are therefore better modeled as lifecycle fences than as a standalone user feature mode.

### DisplayTrigger Likely Bridges Case, Wake, and Display Policy

- `0x81` is not just passive case telemetry.
- The lane likely participates in display-trigger or wake-adjacent policy as well, but the exact bridge is not closed enough yet to freeze one interpretation.

### Voice Wakeup Response Likely Enters the Same Lifecycle Plane

- App and firmware notes expose a `sendWakeupResp` path and wakeup/head-up adjacencies around EvenAI-style behavior.
- The owning service and exact payload schema remain unresolved, but `openCFW` should expect voice wakeup to integrate with lifecycle orchestration rather than with raw text/render protocols alone.

## Unidentified Areas

- Exact `0x10` onboarding command ids, field schema, delayed-ACK payloads, and state notifications.
- Exact wire schema for head-up angle and `setHeadUpTriggerDashboard`, plus the final relationship to selector `4`, case4 `tag17`, and `0x20073004`.
- Exact producer path and semantic meaning of empty `0x0D-01` companion packets, plus final semantics of `event=6,status=7`.
- Exact `0x21` SystemAlert event ids and `0x22` SystemClose action/result enums.
- Exact timeout tables and close-policy ownership for dashboard, EvenAI-adjacent flows, teleprompter, and other user-facing services beyond the currently anchored cases.
- Exact `0x81` DisplayTrigger/BoxDetect field meaning, including the lifecycle role of `f3.f1=67`.
- Exact wakeup-response payload schema and owning runtime service.

## Clean-Room Rules

- Keep startup/idle orchestration separate from feature-content service handlers.
- Model compact modes and timeout-driven returns to idle explicitly in code.
- Keep onboarding, head-up trigger, alert, and close-confirmation flows as dedicated lifecycle services rather than generic settings bits.
- Keep dashboard auto-close and other timeout policies as explicit configuration/state inputs.
- Keep `0xFF` monitor handling available early for lifecycle tracing and observability.
- Treat `0x81` and wakeup-response behavior as instrumented lifecycle hooks until their schemas close further.

## Source Documents

- `../features/display-pipeline.md`
- `../firmware/modules/settings-compact-notify.md`
- `../firmware/modules/settings-sync-module-config.md`
- `../firmware/modules/settings-headup-calibration.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/firmware-reverse-engineering.md`
- `../firmware/g2-firmware-modules.md`
- `../firmware/even-app-reverse-engineering.md`
- `../protocols/services.md`
- `../firmware/analysis/2026-03-05-g2-system-monitor-callchain.md`
