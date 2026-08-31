# G2 app\gui\SystemAlert\systemAlert.c zero-anchor recovery

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

- Retained path: `app\gui\SystemAlert\systemAlert.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\app\gui\SystemAlert\systemAlert.c`
- Disposition: **production-routed clean-room source; hardware validation blocked**
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-system-alert-closure.tsv` (sha256 `bacaa90329b3b7f19a0df054263d30089812189cc1eede82aa1ac72df27b6294`)
- Function map: `tools/manifests/g2-system-alert-function-map.tsv` (sha256 `70bfe0ac4ea1d67fdc4aac21423d4c52f4b578a86d3610dd7a74e6a11a6ddb41`)
- Candidate: `components/apollo_main/core_overlay/system_alert.c`
- Audit: `tools/analyze_g2_system_alert.py`; tests: `tests/test_system_alert_candidate.py`, `tests/test_analyze_g2_system_alert.py`

## Identity evidence

- Path string at 0x006FD85C; pointer cell(s) 0x004D3424; 12 literal reference(s), all inside the mapped blocks.
- 12 module log-tag strings loaded by the mapped blocks, including:
- `0x00723B60` `[system_alert]PAGE_EVENT_FOREGROUND_ENTER_ANIM_COMPLETE`
- `0x00723B98` `[system_alert]send system alert auto exit event to self`
- `0x00723BD0` `[system_alert]PAGE_EVENT_FOREGROUND_EXIT_ANIM_COMPLETE`
- `0x0072E38C` `[system_alert]unknown system alert event type: %d`
- `0x00738F54` `[system_alert]MessageNotify recv data len = %d`
- `0x00738F84` `[system_alert]system_alert_ReflashEventHandler`
- `0x00744388` `[system_alert]system_alert_MainPage_init`
- `0x0075A9BC` `[system_alert]IMU Reflash Event.`

## Linked extents

Physical interval `[0x004D2B9A, 0x004D34C4)` = 2346 bytes (2176 body + 170 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x4d2b9a-0x4d2bce | 52 | 0 | 22 | `6215de2ee5c2a1b0...` |
| 0x4d2bce-0x4d2c42 | 116 | 1 | 43 | `6189a4e959fc4a0b...` |
| 0x4d2c42-0x4d2f48 | 774 | 7 | 283 | `801b96e90bc4eb30...` |
| 0x4d2f48-0x4d306c | 292 | 0 | 110 | `aea35e0460a4feb4...` |
| 0x4d306c-0x4d30ba | 78 | 0 | 33 | `0f20bbf47ca9dded...` |
| 0x4d30ba-0x4d3354 | 666 | 2 | 255 | `a3457b5a5d777194...` |
| 0x4d3354-0x4d341a | 198 | 2 | 83 | `282ceb27872c7463...` |

## Ingress (whole-image scans)

- direct BL entry sites: 7; strict-interior BL targets: 1
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 2
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

Seven blocks in gap [0x4D2B9A, 0x4D34C4). Identity: 12 path references across 4 blocks and 12 `[system_alert]` tags. Registration: descriptor cells 0x6A4684 (entry 0x4D2BCE) and 0x6A4688 (entry 0x4D3354); helper 0x4D306C is called externally (0x47D40C, 0x47D42E, 0x47D6E0, 0x47D70E, 0x58186C); entry 0x4D2B9A is reached by a strict-interior BL from inside block 0x4D2C42 (pinned). The trailing 170-byte pool carries the path cell 0x4D3424.

## Verification

```
make system-alert-closure
```

The seven selector-isolated clean-room leaves compile to 1,138 Thumb text
bytes, 51 read-only-data bytes, and nine alignment bytes. Seven guarded
`B.W` redirects replace all 2,174 callable stock body bytes. The two-byte
alignment NOP at `0x004D2B9A` and the authenticated 170-byte object pool stay
official. Eighty-five strict relocations bind only to reviewed LVGL, event,
timer, display, message-notification, IMU, and sibling-source interfaces.

Host tests cover box-padding geometry, common-data dispatch, page lifecycle,
auto-exit throttling, main-page construction, reflash events, IMU refresh, and
UI-event routing. The canonical overlay, Apollo component, and complete
package are 225,396 / 3,748,792 / 4,527,286 bytes with SHA-256 values
`29555fb742e82c4a2076eb3b508211faf1d7b2777faa16a43f060edbf5f7c285`,
`a6a78d0b9c38462ddfac7779775537ad4dc9b147975f5fd2263a44873b0ba8c5`,
and `3f09f5ee3eb0752c54267810cc2b9d22c57b57dbe444a81c6b237b2d88da6d0c`.
The 2,464,744-byte flash plan has 3,531 placed, two unresolved, five
container-only, and six protected regions; its SHA-256 is
`cf79b4d7272431805cc19d3cb8acd685d7bb447464976ee884d797acc4304f15`.

No package was signed or flashed. Live display rendering, event timing,
message-notification interaction, IMU reflash behavior, and paired-temple
interoperability remain explicitly blocked: the authorized right temple is
nonresponsive and the left temple must remain stock. This closes only the
SystemAlert software gap and is not a firmware-completeness claim.
