# Runtime Service Map

This is the clean-room service map to drive `openCFW` implementation work.

Confidence states:

- `Identified`: safe as a direct implementation target.
- `Partial`: the service is real and implementation-relevant, but field ownership or semantics are still incomplete.
- `Unidentified`: do not implement beyond instrumentation or scaffolding.

## Transport Lanes

| Lane / Service | State | Meaning | openCFW Use |
|---|---|---|---|
| `0x5401 / 0x5402` | Identified | Main control/service protobuf lane | Core command/response plane |
| `0x6401 / 0x6402` | Identified | Display/render/sensor lane | Display wake, render feedback, and sensor stream handling |
| `0x7401 / 0x7402` | Identified | File/OTA lane | File transfer, OTA, and possible log export |
| `NUS 6E4000xx` | Identified | Raw low-latency BLE side channel | Gesture events, microphone enable, and LC3 audio stream outside the G2 envelope |
| `0xC4-00` | Identified | File command path | `FILE_CHECK`, send control, export control, and OTA metadata |
| `0xC5-00` | Identified | File data path | Streamed payload transfer for both send and export directions |

## G2 Service IDs

| Service | State | Meaning | Implementation Note |
|---|---|---|---|
| `0x01-20` | Partial | Dashboard widgets / sync | Runtime exists, and adjacent `0x01-01` traffic carries tap/swipe gesture status; widget/menu schema is still incomplete |
| `0x80-00/01/02/20` | Identified | AuthControl/AuthResponse/TransportACK/AuthData | Dedicated application-level auth and time-sync family; keep endpoint-local sequencing |
| `0x02-20` | Identified | Notification metadata | Stable control-plane feature; displayed notifications still depend on the file lane |
| `0x03-20` | Identified | Menu | Good early implementation candidate |
| `0x04-20` | Identified | Display wake | Required before many render features |
| `0x05-20` | Partial | Translate | Service is real, but detailed subtype/field semantics are still incomplete |
| `0x06-20` | Identified | Teleprompter | Init/content/complete path plus ACK/progress flow are known |
| `0x07-20` | Identified | EvenAI | Core assistant path is known; microphone and audio transport remain on separate codec or NUS paths |
| `0x08-20` | Partial but executable | Navigation | Two descriptor-adjacent lanes are anchored; field map still incomplete |
| `0x09-00/20` | Partial but executable | DeviceInfo / DevConfig bridge | Shared settings parser/status bridge, not just read-only info |
| `0x0A-20` | Unidentified | SessionInit? | No confirmed runtime meaning |
| `0x0B-20` | Identified | Conversate | Transcript/session path with known FSM; `use_audio` exists but live audio ownership is separate |
| `0x0C-20` | Identified | Quicklist + Health | Shared service with update, paging, health-data, and highlight families |
| `0x0D-00/20` | Identified | Settings / ProtoBaseSettings | Major early implementation target; wear gating and long-press/compact notify behavior are adjacent on `0x0D-01` |
| `0x0E-20` | Identified | Display config (viewport regions) | Needed for render-mode bring-up |
| `0xE0-20` | Identified | EvenHub (container layout) | Dedicated service — `evenhub_common_data_handler` |
| `0x0F-20` | Identified | Logger | `/log/` management is known; live-stream and export details are still partial |
| `0x10-20` | Partial but executable | Onboarding | First-run lifecycle service is real; startup/start/end flow is anchored, but full state schema is still partial |
| `0x20-20` | Partial | ModuleConfigure + SyncInfo | Needed for calibration/config sync; brightness calibration, language, and module-list behavior are anchored but schema closure is incomplete |
| `0x21-20` | Partial | SystemAlert | Dedicated lifecycle-facing alert lane; event ids and final state effects are still partial |
| `0x22-20` | Partial | SystemClose | Dedicated close/confirm lane; dialog semantics are known but action/result tables are still partial |
| `0x81-20` | Partial | BoxDetect / case relay / display trigger | Case path is important and likely lifecycle-coupled to display trigger/wake behavior; exact command grammar is still partial |
| `0x90-??` | Unidentified | Reserved / unknown | No clean-room implementation yet |
| `0x91-20` | Partial but executable | Ring relay | Handler path is anchored; gesture/health relay exists, but enum tables and tick/type mapping are still unresolved |
| `0xFF-20` | Identified | SystemMonitor | Dedicated monitor and idle-probe lane with scheduler-handoff linkage; deeper payload semantics are still partial |

## Priority for openCFW

1. `0x80` auth family, `0x04`, `0x09`, `0x0D`, `0x0E`, `0xFF`
2. `0x02`, `0x03`, `0x06`, `0x0B`, `0x0C`
3. `0x08`, `0x20`, `0x81`, `0x91`
4. `0x01`, `0x05`, `0x07`, `0x10`, `0x21`, `0x22`
5. Skip `0x0A` and `0x90` until more evidence exists

## Source Documents

- `../firmware/g2-service-handler-index.md`
- `../firmware/firmware-reverse-engineering.md`
- `../firmware/g2-firmware-modules.md`
- `../firmware/modules/file-transfer.md`
- `../firmware/modules/logger.md`
- `../firmware/modules/quicklist-health.md`
- `../firmware/modules/settings-compact-notify.md`
- `../firmware/even-app-reverse-engineering.md`
- `../features/gestures.md`
- `../features/brightness.md`
- `../firmware/modules/settings-sync-module-config.md`
- `../firmware/modules/settings-headup-calibration.md`
- `../firmware/touch-cy8c4046fni.md`
- `../firmware/modules/wear-detection.md`
- `../firmware/modules/ring-relay.md`
- `../protocols/services.md`
- `../protocols/nus-protocol.md`
- `../protocols/authentication.md`
- `../firmware/firmware-communication-topology.md`
- `../features/display-pipeline.md`
- `../firmware/analysis/2026-03-05-g2-nav-devinfo-descriptor-lanes.md`
- `../firmware/analysis/2026-03-05-g2-ring-relay-callchain.md`
- `../firmware/analysis/2026-03-05-g2-system-monitor-callchain.md`
