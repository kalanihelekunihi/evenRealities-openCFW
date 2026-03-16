# Feature and Presentation Model

This document is the clean-room model for the user-visible display and feature layer that sits above the transport, settings, and state surfaces already documented elsewhere in `openCFW`.

## Feature Matrix

| Domain | State | Main Evidence | Identified Constraints | Remaining Gaps |
|---|---|---|---|---|
| Display bring-up and mode tracking | Identified | display pipeline, display-config, compact-notify captures | wake -> config -> content sequencing is real; `0x6402` is the hardware-facing activity lane; compact `0x0D-01` mode events are part of feature activation. EvenHub (`0xE0`) skips displayConfig — only needs displayWake | exact `0x0E` display-config field ownership, full `0x6402` decode, `event=0` producer |
| EvenHub containers and page layout | Identified | EvenHub app docs, display pipeline | container/page model, size limits, image fragmentation, and result codes are implementation-relevant. EvenHub uses dedicated service `0xE0-20` (not `0x0E-20` displayConfig) | EvenHub response decode on `0xE0-00` |
| Teleprompter | Identified with bounded unknowns | teleprompter protocol, compact-notify correlation | init, content, marker, completion, ACK, and progress packets are real | exact type `255` and sync-trigger semantics |
| Conversate | Partial | conversate protocol, compact-notify correlation | two-step init and fixed-width transcript updates are stable enough to model | exact init-field meaning, timeout and close-side effects |
| EvenAI | Partial | EvenAI protocol, brightness skill notes, compact-notify correlation | `CTRL(ENTER)` before `ASK/REPLY` is a hard requirement; minimal status flow is real | full command surface, widget/skill multiplex, stream semantics |
| Navigation presentation | Partial | navigation notes, descriptor-lane recovery, compact-notify correlation | navigation has compact and active states and is definitely a first-class UI feature | full `0x08` field and enum closure |
| Quicklist and health | Partial | quicklist-health module | update, paging, save, query, and highlight families are real | exact command-to-payload routing and notify behavior |
| Notifications and alerts | Partial | notification protocol, logger and file-transfer modules | notification display depends on file-backed transfer and whitelist storage, not only a control ACK | exact split between `0x02` metadata and file-backed display trigger |
| Brightness and ALS-driven display policy | Partial | brightness docs, display-config module, settings docs | manual brightness, auto-brightness, and per-eye calibration all exist | exact protobuf fields and ALS curve |
| Dashboard, widgets, and secondary user services | Partial | eventhub, service map, firmware module summaries | dashboard/widget OS, onboarding, translate, and alert-style services are real | canonical service ownership and schema split across `0x01`, `0x05`, `0x07`, `0x10`, `0x21`, `0x22` |

## Identified Presentation Contracts

### Display Activation Is Multi-Step

- User-visible rendering is not a single write. The stable activation pattern is:
  1. display wake (`0x04`)
  2. display config (`0x0E`)
  3. feature content (`0x06`, `0x07`, `0x08`, `0x0B`, or `0xE0` EvenHub container traffic)
- `0x6402` activity is the hardware-facing confirmation lane that the display is active.
- Compact `0x0D-01` mode packets track at least:
  - `0` idle or reset
  - `6` render-family mode
  - `11` conversate
  - `16` teleprompter

### EvenHub Is a Layout System, Not Just One Feature Packet

- The G2 render surface is a local-layout system built around page and container operations.
- Text, list, and image containers are first-class objects with size limits and event-capture constraints.
- Image payloads are fragmented separately from page creation.
- `0x0E` therefore carries at least two implementation-relevant concepts:
  - display-config and mode setup
  - container or page operations

### Teleprompter Has a Stateful Session, Not Just Text Blits

- Teleprompter uses an init flow, repeated page content packets, a mid-stream marker, and a completion packet.
- The glasses send:
  - `0x06-00` page ACKs
  - `0x06-01` render-progress updates
- Clean-room parity therefore needs session state, page counters, and tolerant pacing rather than a stateless text writer.

### EvenAI, Conversate, Quicklist, and Notifications All Carry Different Contracts

- EvenAI requires an explicit enter transition before displayable ask or reply content is accepted.
- Conversate is a transcript session with a small fixed-width text cadence rather than a generic free-form render channel.
- Quicklist and health share one service family but expose different command groups and payload shapes.
- Notifications are file-backed and whitelist-aware. They are not just small control messages on one feature lane.

## Inferred Feature Behavior

### Compact Feature Mode Correlation

- Direction-aware capture correlation strongly suggests:
  - `event=16` is teleprompter-facing
  - `event=11` is conversate-facing
  - `event=6` covers render-family transitions shared by EvenAI and other display features
- Empty companion packets with `event=0` likely participate in feature close, reset, or paired status transitions, but the exact producer path is not closed.

### Brightness Is ALS-Driven and Cross-Eye Coordinated

- Current evidence points to direct JBD brightness writes being deprecated in favor of:
  - ALS sampling on one eye
  - local conversion to a brightness level
  - peer synchronization to the opposite eye
- The clean-room implication is that manual brightness and auto-brightness should be modeled as separate policy inputs to a shared display-level brightness owner.

### Dashboard and Widget Ownership Is Real but Not Fully Partitioned

- App evidence and service-level notes show a dashboard or widget family that is not identical to EvenAI, teleprompter, or navigation.
- Some evidence points at `0x01`; some app-facing feature notes point at shared or adjacent `0x07` traffic.
- That is implementation-relevant because `openCFW` should not freeze one generic widget API until the lane ownership is clearer.

### Notification Display Is Coupled to Storage and Display State

- Notifications depend on JSON file transfer and the whitelist object under `user/notify_whitelist.json`.
- Case, wake, and feature-mode state likely affect whether that transferred payload becomes visible immediately.
- This implies the notification implementation boundary crosses transport, storage, and presentation layers.

## Unidentified Areas

- Exact `0x0E-20` display-config field ownership and counters. EvenHub is separate on `0xE0-20`.
- Exact `0x6402` display-sensor stream decode, descrambling, and per-frame semantic fields.
- Exact source and meaning of compact empty `0x0D-01` packets (`event=0`).
- Exact `0x07` multiplex between EvenAI, brightness skill commands, and dashboard or widget families.
- Exact teleprompter mid-stream marker and sync-trigger semantics.
- Exact conversate init field meaning and any separate transcribe-service ownership.
- Exact notification split between `0x02` metadata, file-lane transfer, and display-trigger behavior.
- Exact navigation `0x08` field map beyond the currently known compact and active presentation states.
- Exact quicklist and health command tables, notify timing, and payload selection rules.
- Exact brightness protobuf field numbers, range normalization, and ALS smoothing curve.

## Clean-Room Rules

- Keep display wake, display config, and feature content as separate steps in code.
- Model feature mode state explicitly instead of inferring it from the last packet written.
- Keep EvenHub container layout separate from feature-specific text or voice protocols.
- Preserve lane-specific feature adapters for teleprompter, conversate, EvenAI, navigation, quicklist/health, and notifications.
- Keep notification rendering file-backed and whitelist-aware until stronger evidence closes a simpler contract.
- Put partial feature schemas behind instrumentation instead of freezing speculative protobuf layouts.

## Source Documents

- `../features/display-pipeline.md`
- `../features/eventhub.md`
- `../features/teleprompter.md`
- `../features/even-ai.md`
- `../features/navigation.md`
- `../features/conversate.md`
- `../features/brightness.md`
- `../firmware/modules/display-config.md`
- `../firmware/modules/quicklist-health.md`
- `../firmware/modules/settings-compact-notify.md`
- `../firmware/modules/logger.md`
- `../firmware/modules/settings-dispatch.md`
- `../firmware/modules/settings-local-data-status.md`
- `../protocols/notification.md`
- `../firmware/g2-service-handler-index.md`
- `../firmware/g2-firmware-modules.md`
- `../firmware/even-app-reverse-engineering.md`
- `../firmware/analysis/2026-03-05-g2-nav-devinfo-descriptor-lanes.md`
