# First-party source-replacement frontier ranking

Status: active. This document opens the first-party phase now that every
inferable third-party component is identified
(see [`upstream-inventory.md`](../upstream-inventory.md) and the per-library
audits). Wave-1 item 1 (the transport CRC-32) is now a production
`linux-clang` overlay leaf; the remaining ranking below is forward-looking.
Run addresses use `run = file_offset + 0x00437FE0`.

## Scope

The remaining opaque bytes are first-party Even code. The authenticated image
retains 234 distinct first-party/project `.c` paths across these subsystems:

| Subsystem | Files | Character |
|---|---:|---|
| `app/gui` | 93 | LVGL-based UI (EvenHub, dashboard, translate/teleprompt, onboarding, menus) |
| `platform/service` | 41 | efs/ota transport, pb_service_* protobuf services, ring/dashboard/settings/time |
| `platform/protocols` | 23 | transport framing, efs/ota, dashboard data, pb services |
| `platform/ble` | 14 | connection/pairing policy, peer manager over Cordio |
| `threads` | 9 | RTOS thread entries |
| `audio` | 6 | PDM/codec DSP |
| `uled`, `ux`, `sync`, `sensor`, `input`, `chg`, `pdm`, `device_mgr`, … | ~40 | drivers and device control |

The reproducible census in
[`g2-first-party-frontier-census.md`](g2-first-party-frontier-census.md)
now partitions these paths into 234 closed and zero open objects. The
closed paths anchor all 1,230 functions / 485,274 body bytes, with no
function shared across statuses. Complete-object records account for
814,846 body bytes, and 232 records report 885,418 known physical bytes;
the closed-manifest ledger is
`ced59dc4826e54c647d8b948c823eee6dfd1892c029838db4a518cbf1ed2bfde`. This
is retained-path lower-bound coverage, not whole-image or source-ownership
coverage. The parser now consumes legacy multi-module closure records and
standardized retained-path metadata, correctly moving the already closed
`app_ble.c`, BLE WSF/TX/RX threads, and NVDB product-mode object out of the
open queue. The closed `efs_service.c` object contributes 12 linked functions /
9,276 body bytes / 9,934 physical bytes; `ota_service.c` contributes 25 linked
functions / 15,394 body bytes / 16,376 physical bytes; and
`service_codec_host.c` contributes 26 linked functions / 7,318 body bytes /
8,632 physical bytes; and `service_codec_dfu.c` contributes 16 linked
functions / 9,052 body bytes / 9,968 physical bytes. The closed
`service_touch_dfu.c` object contributes 32 linked functions / 6,430 body
bytes / 7,004 physical bytes. The closed `terminal_pb_msg_handler.c` object
contributes 27 linked functions / 7,688 body bytes / 8,364 physical bytes.
The closed `service_whitelist.c` object contributes seven linked functions /
4,310 body bytes / 4,728 physical bytes.
The zero-anchor `drv_pdm_production.c` object contributes six linked functions /
610 body bytes / 704 physical bytes and ties 12 Apollo510 PDM APIs to the
selected AmbiqSuite 5.1.0 public replay.
The neighboring generic `drv_pdm.c` object contributes seven functions / 794
body bytes / 900 physical bytes and adds the IRQ-service/status APIs plus its
vector-table handler proof.
The BLE production thread contributes 14 restored functions / 2,140 body
bytes / 2,368 physical bytes. Its hidden task/init/deinit entries, static task
attributes, exact CMSIS-FreeRTOS and FreeRTOS assertion seams, message
queue/pool contract, and production-frame checks are now pinned in
[`g2-thread-ble-production-dependency-boundary.md`](g2-thread-ble-production-dependency-boundary.md).
The product-test protocol processor contributes 73 complete functions / 32,866
body bytes / 35,524 physical bytes. Its 69 retained-path anchors expand through
three pathless Ghidra bodies and one hidden external handler; a 66-entry aligned
Thumb table bounds its sole indirect dispatch. All reusable edges terminate at
the selected EasyLogger, CMSIS-FreeRTOS, FreeRTOS, mpaland printf, and bounded
IAR seams, with no embedded third-party implementation or new version
discriminator. See
[`g2-pt-protocol-procsr-dependency-boundary.md`](g2-pt-protocol-procsr-dependency-boundary.md).
The EvenHub main controller now contributes five complete functions / 3,130
body bytes / 3,450 physical bytes. Its direct dependency graph closes over the
selected EasyLogger, LVGL, CMSIS-FreeRTOS, nanopb, and TLSF sources plus
bounded runtime and first-party services. See
[`g2-evenhub-main-dependency-boundary.md`](g2-evenhub-main-dependency-boundary.md).
The translate controller contributes eleven complete functions / 2,504 body
bytes / 2,862 physical bytes and reuses the selected EasyLogger, LVGL,
CMSIS-FreeRTOS, and nanopb sources without adding a utility gap. See
[`g2-translate-dependency-boundary.md`](g2-translate-dependency-boundary.md).
The adjacent translate UI object contributes 29 complete functions / 5,288
body bytes / 5,730 physical bytes. Its 22 restored functions and 13 stored
entries close over selected EasyLogger/LVGL, bounded product providers, and
the source-admitted IAR float-exponent trio, with no new opaque utility. See
[`g2-translate-ui-dependency-boundary.md`](g2-translate-ui-dependency-boundary.md).
The teleprompt controller contributes ten functions / 2,408 body bytes / 3,900
physical bytes and adds no new reusable dependency or version discriminator.
See
[`g2-teleprompt-controller-dependency-boundary.md`](g2-teleprompt-controller-dependency-boundary.md).
Conversate common data contributes twelve functions / 2,208 body bytes / 2,560
physical bytes and adds no reusable dependency or commit discriminator. See
[`g2-conversate-comm-data-dependency-boundary.md`](g2-conversate-comm-data-dependency-boundary.md).
The main conversate controller contributes twelve functions / 2,250 body
bytes / 2,628 physical bytes. Its one CmBacktrace edge corroborates the known
compatible interval and selected `73714489` baseline without proving Even's
private checkout; all other reusable edges are already admitted. See
[`g2-conversate-controller-dependency-boundary.md`](g2-conversate-controller-dependency-boundary.md).
The EvenHub common image container contributes three functions / 1,554 body
bytes / 1,834 physical bytes and adds no dependency or commit discriminator.
See
[`g2-common-image-container-dependency-boundary.md`](g2-common-image-container-dependency-boundary.md).
Dashboard watchface layout 2 contributes nineteen functions / 2,844 body bytes
/ 3,076 physical bytes and adds no dependency or commit discriminator. See
[`g2-dashboard-watchface-layout2-recovery.md`](g2-dashboard-watchface-layout2-recovery.md).
The quicklist UI page contributes 80 functions / 21,886 body bytes / 23,594
physical bytes, including seventeen restored functions and fifteen stored
callbacks. Its provider graph closes over selected LVGL and EasyLogger, exact
CMSIS-FreeRTOS tick access, bounded IAR runtime, and first-party UI/protobuf
policy. See
[`g2-ui-quicklist-page-dependency-boundary.md`](g2-ui-quicklist-page-dependency-boundary.md).
The dashboard news page contributes 45 functions / 19,058 body bytes / 20,668
physical bytes, including fourteen restored helpers and twelve stored
callbacks. Its provider graph closes over selected LVGL/EasyLogger, exact
CMSIS-FreeRTOS mutex wrappers, bounded runtime, and first-party policy. See
[`g2-ui-widget-news-page-dependency-boundary.md`](g2-ui-widget-news-page-dependency-boundary.md).
The closed `teleprompt_page_data.c` object contributes 21 linked functions /
4,728 body bytes / 5,120 physical bytes.
The closed `imu_icm45608.c` object contributes 53 linked functions / 11,674
body bytes / 12,436 physical bytes, including the three stored bus/FIFO
callbacks and the complete sample-fusion and raw-CSV pipeline.
The compact `PdtDistortionTest/pdt_distortion_test.c` UI object is also closed:
four linked bodies / 850 body bytes / 896 physical bytes, its screen-ID `0x110`
registration, retained resource IDs, object-tree behavior, and three stored
entries are pinned in
[`g2-pdt-distortion-test-recovery.md`](g2-pdt-distortion-test-recovery.md).
The adjacent gray-screen object adds three restored bodies / 340 bytes and its
eight-band grayscale contract; see
[`g2-pdt-gray-screen-recovery.md`](g2-pdt-gray-screen-recovery.md).
The family endpoint `ProductionTest/production_test.c` adds three bodies / 286
bytes and its exact 3×3 test-dot geometry; see
[`g2-production-test-screen-recovery.md`](g2-production-test-screen-recovery.md).
The apparently first-party `platform/ble/profiles/gatt/profile_gatt.c` entry is
now removed from the opaque queue: all six functions are the selected
Packetcraft `gatt_main.c` source, with only a local `GattDiscover` logging
expansion. See
[`cordio-gatt-profile-source-recovery.md`](cordio-gatt-profile-source-recovery.md).
The adjacent `platform/ble/profiles/ancc/profile_ancc.c` entry is likewise
removed from the opaque queue. Its complete 21-function object preserves the
AmbiqSuite ANCC client's 64-slot queue, command encoders, fragmented parser,
and service discovery; 12 bodies are Ambiq-derived and nine are bounded G2
policy/adapters. See
[`ambiqsuite-ancc-profile-source-recovery.md`](ambiqsuite-ancc-profile-source-recovery.md).
Four more adjacent BLE-profile paths are now removed from the queue. The
EUS/ESS/EFS/NUS group is a 21-function / 2,374-body-byte / 3,000-physical-byte
family of G2-local Cordio adapters, not copied AmbiqSuite or Nordic code. See
[`g2-ble-transport-profiles-recovery.md`](g2-ble-transport-profiles-recovery.md).
The adjacent BLE peer-manager and discovery-policy paths are closed too. The
peer manager has four functions / 446 body bytes / 512 physical bytes and
implements G2 close-before-unpair policy over Cordio. The discovery object has
two callbacks / 2,962 body bytes / 3,724 physical bytes and owns the role-aware
database-hash, GATT, Ring, ANCS, configuration, and completion state machine.
Prior G2 analysis corroborates all six exact names and the discovery function
sizes. See [`g2-app-ble-peer-manager-recovery.md`](g2-app-ble-peer-manager-recovery.md)
and [`g2-app-ble-discovery-recovery.md`](g2-app-ble-discovery-recovery.md).
The central-role sibling is closed as 44 functions / 14,288 body bytes /
15,752 physical bytes. Its 20 restored non-anchor functions complete the
seven-state RingLink machine, scan/RPA path, retry escalation, dominant-hand
switching, unpair cleanup, and scene reconnect policy. It is G2-local code over
Cordio APIs, not another third-party source gap; see
[`g2-app-ble-central-recovery.md`](g2-app-ble-central-recovery.md).
The adjacent `app_connect_params.c` policy is also closed as 14 functions /
6,336 body bytes / 6,888 physical bytes. Its current fast/slow request,
connection-event, retry, ESS, and OTA paths retain all 14 prior-G2 names while
remaining first-party policy above Cordio rather than an undiscovered upstream
copy. See
[`g2-app-connect-params-recovery.md`](g2-app-connect-params-recovery.md).
The peripheral-role object is also closed as 31 functions / 5,888 body bytes /
6,560 physical bytes. Its provider calls terminate at the already admitted
AmbiqSuite 2.5.1 Cordio application framework; its advertising payload, event,
unpair/restart, and role decisions remain G2-local. See
[`g2-app-ble-peripheral-recovery.md`](g2-app-ble-peripheral-recovery.md).
The multipart `transport_protocol.c` object is now closed too: 13 functions /
4,134 body bytes / 4,436 physical bytes, including the recursively recovered
310-byte timeout callback. It is G2-local `0xAA` framing over admitted
providers; its three checksum calls target the source-owned CCITT-FALSE leaf,
and it has no TinyFrame call or stored pointer. Its complete thirteen-function
clean-room graph is now production-routed; only unavailable authorized peer
hardware blocks live traffic validation. See
[`g2-transport-protocol-recovery.md`](g2-transport-protocol-recovery.md).
The compact `platform/service/settings/service_settings.c` frontier item is
also closed: 31 functions / 5,146 body bytes / 5,712 physical bytes. Its
provider graph terminates at exact CMSIS-FreeRTOS and EasyLogger admissions,
family-level IAR DLIB primitives, and already bounded G2 CRC/KV/display/sensor
objects. See
[`g2-service-settings-recovery.md`](g2-service-settings-recovery.md).
The compact `app/gui/tracepoint/tracepoint_setting.c` item is now closed too:
21 functions / 5,100 body bytes / 5,588 physical bytes. It is first-party
file-list and protobuf command policy over already admitted EasyLogger,
nanopb, littlefs-backed wrappers, and family-level IAR DLIB seams; see
[`g2-tracepoint-setting-recovery.md`](g2-tracepoint-setting-recovery.md).
The single-anchor product `rtos.c` path is now a complete 13-function / 512-
body-byte / 548-physical-byte object. Its task-vote policy and FreeRTOS hooks
close the application-hook seam from the earlier port audit. Its complete
two-WFI system-sleep provider also selects Ambiq Apollo510 HAL 5.1.0 lineage
and public replay commit `5efc0228…`, while the earlier stock build timestamp
keeps the actual private commit unobservable. See
[`g2-product-rtos-recovery.md`](g2-product-rtos-recovery.md).
The GX8002B host driver is now closed as 12 functions / 1,028 body bytes /
1,172 physical bytes. Its reusable software boundary is three emitted
CMSIS-Core NVIC helpers, 13 calls to 12 AmbiqSuite 5.1.0 Apollo510 I2S APIs,
four exact CMSIS-FreeRTOS delay calls, and admitted EasyLogger. NationalChip's
GX8002B/LVP package is an external device dependency, not linked software in
the object. See
[`g2-drv-gx8002b-recovery.md`](g2-drv-gx8002b-recovery.md).
The FlashDB service adapter is now closed as eleven functions / 908 body bytes /
1,040 physical bytes. Its provider graph reuses the pinned FlashDB 2.1.1,
CMSIS-FreeRTOS v10.5.1, and EasyLogger sources, while the unsafe zero-on-failure
FAL seam is preserved as an explicit porting constraint. See
[`g2-service-db-api-recovery.md`](g2-service-db-api-recovery.md).
The two-anchor `app/gui/EvenAI/ui_even_ai.c` path is now closed as a much larger
43-function / 8,004-body-byte / 8,424-physical-byte object. Its dependency
graph terminates at already admitted LVGL, EasyLogger, CMSIS-FreeRTOS, and IAR
seams; the text-stream and timer consumers compose earlier first-party
closures. See [`g2-ui-even-ai-recovery.md`](g2-ui-even-ai-recovery.md).
The adjacent `platform/service/time/service_time.c` path is now closed as eleven
primary functions / 1,308 body bytes / 1,384 physical bytes, including the
externally called alternate compiler entry inside the epoch-to-calendar body.
Its only reusable code edges are eight bounded IAR DLIB calls; the remaining
providers are first-party, and there is no direct CMSIS-FreeRTOS call or
embedded third-party implementation. See
[`g2-service-time-recovery.md`](g2-service-time-recovery.md).
The `platform/threads/thread_audio.c` path is now closed as 31 functions /
2,954 body bytes / 3,258 physical bytes. It composes fourteen exact
CMSIS-FreeRTOS v10.5.1 wrappers and the closed codec DFU, codec-host, and
GX8002B objects; its only remaining compiler seam is one bounded four-byte IAR
fill. See [`g2-thread-audio-recovery.md`](g2-thread-audio-recovery.md).
The neighboring compact-log core is now closed as eight functions / 2,300
contiguous executable bytes. This corrects a high-leverage provenance label:
`0x0043CE9E` is a G2-private compact-record hook with 5,718 direct callers, not
upstream EasyLogger `elog_output`; the admitted G2-adapted upstream output body
is still `0x0043D574`. The core terminates at known EasyLogger, FreeRTOS,
CMSIS-FreeRTOS, IAR DLIB, and first-party providers and embeds no reusable
third-party body. See
[`g2-compress-log-core-recovery.md`](g2-compress-log-core-recovery.md).
The compact-log port is closed too: twelve functions / 1,324 body bytes /
1,464 physical bytes implement five-file rotation, a 12-byte manager record,
version headers, and a 120,000-tick export timeout. Its file and delayed-event
providers are already production source-owned, making this first-party policy
an unusually short route to a future compact-log source candidate. See
[`g2-compress-log-port-recovery.md`](g2-compress-log-port-recovery.md).
The file-runtime object behind that port is now path-closed as eighteen
functions / 2,266 body bytes / 2,404 physical bytes. Every entry already has
an exact production source redirect, so downstream objects can treat file,
directory, synchronized heap, and runtime initialization as source-owned
terminal providers. See [`g2-file-runtime-recovery.md`](g2-file-runtime-recovery.md).
The compact `platform/audio/service_algo.c` object is now closed as ten
functions / 1,712 body bytes / 1,848 physical bytes. Its reusable edges are
bounded IAR `memset`, `asin`, signed-64-to-double, and `sqrt` routines plus a
source-owned 64-bit division helper; no NationalChip LVP or other DSP library
body is linked. The recovered first-party estimator consumes 800 interleaved
stereo frames and searches lags -10 through +10. OpenCFW must preserve or
deliberately correct the stock short-buffer hazard: validation accepts some
aligned sizes below 3,200 bytes although the implementation still reads all
3,200 bytes. See [`g2-service-algo-recovery.md`](g2-service-algo-recovery.md).
The bounded `framework/sync/uart_sync.c` object is now closed as five
functions / 758 body bytes / 872 physical bytes after restoring its write,
receive-callback, and reset helpers. It composes exact CMSIS-FreeRTOS and
TinyFrame source admissions, the selected EasyLogger core, and a first-party
UART adapter over the AmbiqSuite SDK 5.1.0 compatibility baseline. No reusable
implementation is embedded; its one RAM-dispatched initializer and the lower
hardware adapter remain explicit first-party/hardware seams. See
[`g2-uart-sync-recovery.md`](g2-uart-sync-recovery.md).
The factory `service_nvdb.c` object is now closed as five functions / 930 body
bytes / 1,052 physical bytes. Reusing the authenticated FlashDB configuration
audit proves that its reusable implementation is exactly FlashDB 2.1.1 commit
`714d6159…`; the local code supplies only database-index-one wrappers, the
nine-node default table/validator, and `factory@NVdb` magic/reset policy. The
wholesale reset and stock zero-on-driver-failure FAL seam remain explicit
production safety gates. See
[`g2-service-nvdb-recovery.md`](g2-service-nvdb-recovery.md).
The production microphone test object is now closed as six functions / 898
body bytes / 1,000 physical bytes. A stored stereo PCM callback missing from
Ghidra is restored alongside the five visible functions. All reusable calls
are bounded IAR memory operations and admitted logging; codec, PDM, channel
extraction, and PCM dispatch remain first-party providers. No NationalChip or
other DSP body is linked. See
[`g2-production-mic-recovery.md`](g2-production-mic-recovery.md).
The adjacent `service_audio_manager.c` object is now closed as seven functions /
1,554 body bytes / 1,728 physical bytes. Two complete functions missing from
Ghidra restore the four-message role-sensitive peer handshake and initialization
path. Its only reusable edges are admitted logging and one bounded IAR `memset`;
audio power, product-role, and common-data transport remain explicit first-party
providers. See
[`g2-service-audio-manager-recovery.md`](g2-service-audio-manager-recovery.md).
The system `service_kvdb.c` object is now closed as seven functions / 1,384
body bytes / 1,540 physical bytes. It composes the exact FlashDB 2.1.1 commit,
the closed database adapters, onboarding record, and eleven-entry first-party
migration table. Its reset-called IAR zero range proves `kvbooCount` starts at
zero, and the initializer proves its persisted read/increment/write lifecycle,
retiring that former FlashDB gap. See
[`g2-service-kvdb-recovery.md`](g2-service-kvdb-recovery.md).
The formerly open `utils\assert\util_error_check.c` path is now closed as a
one-function / 178-body-byte / 212-physical-byte object. Although retained as
project source, its exact 43-row error table and formatter derive from Goodix
GR551x SDK 1.7.0 `app_error.c`; see
[`g2-util-error-check-goodix-recovery.md`](g2-util-error-check-goodix-recovery.md).
The `app\gui\logger\logger_setting.c` path is also removed from the queue. Its
single 84-byte baseline anchor expands to eight linked functions / 5,574 body
bytes / 5,992 physical bytes after recursive recovery of the file helpers,
stored protobuf callback, and filename simplifier. It is first-party logger
protocol/routing policy over already admitted dependencies, not another
third-party source gap; see
[`g2-logger-setting-recovery.md`](g2-logger-setting-recovery.md).
The next single-anchor `app\ux\ux_system\ux_system.c` path is removed from the
queue as well. Its 88-byte visible anchor expands to eleven linked functions /
2,668 body bytes / 2,868 physical bytes after recovering the stored 2,232-byte
status callback. The object is first-party OTA/BLE/ring synchronization policy
over bounded G2 providers and EasyLogger diagnostics, not a hidden upstream
utility; see [`g2-ux-system-recovery.md`](g2-ux-system-recovery.md).
The 94-byte `app\gui\health\health.c` anchor is removed too. Two functions
missed by baseline Ghidra expand it to four functions / 504 body bytes / 572
physical bytes. The object is first-party health mutex and common-event policy
over exact, production-source-owned CMSIS-FreeRTOS v10.5.1 mutex wrappers,
EasyLogger diagnostics, and bounded G2 providers; see
[`g2-health-recovery.md`](g2-health-recovery.md).
The structurally adjacent `app\gui\quicklist\quicklist.c` object is closed as
four functions / 310 body bytes / 360 physical bytes. Its mutex trio reaches
the same exact CMSIS-FreeRTOS v10.5.1 admission, while the stored event handler
terminates at bounded first-party quicklist providers; see
[`g2-quicklist-recovery.md`](g2-quicklist-recovery.md).
The compact `app\gui\dashboard\dashboard_watchface_manager.c` object is also
closed as 17 functions / 956 body bytes / 1,044 physical bytes. Its four
15-word operation tables pin every indirect dispatch into first-party
watchface code; the sole utility boundary is already admitted EasyLogger. See
[`g2-dashboard-watchface-manager-recovery.md`](g2-dashboard-watchface-manager-recovery.md).
The `app\gui\EvenAI\text_stream_service.c` anchor is now closed as a
26-function / 3,188-body-byte / 3,228-physical-byte object. It owns growable
UTF-8 current/pending buffers, one-code-point-per-tick animation, and four
generic-animation presets over admitted providers; see
[`g2-text-stream-service-recovery.md`](g2-text-stream-service-recovery.md).
The compact `app\gui\terminal\terminal.c` core is closed as nine functions /
1,144 body bytes / 1,248 physical bytes. Its mutex, three stored callbacks,
display lifecycle, and 13-ID command policy terminate at admitted providers;
see [`g2-terminal-core-recovery.md`](g2-terminal-core-recovery.md).
The 130-byte `driver\rtc\drv_rtc.c` path is also closed. Its calendar and RTC
calls resolve to exact AmbiqSuite utility/HAL sources at the selected 5.1.0
public replay, and the complete body is already production-routed to the
tested `open_cfw_rtc_time_set` replacement; see
[`g2-drv-rtc-recovery.md`](g2-drv-rtc-recovery.md).
The neighboring `app\gui\teleprompt\teleprompt_file_list.c` path is closed as
three functions / 166 body bytes / 200 physical bytes. Its update/get/reset
contract covers one `0xF52`-byte global record over admitted EasyLogger and
IAR memory primitives; see
[`g2-teleprompt-file-list-recovery.md`](g2-teleprompt-file-list-recovery.md).
The adjacent `app\gui\EvenAI\even_ai_timer.c` object is closed as 13
functions / 856 body bytes / 956 physical bytes. It implements two first-party
wrap-safe tick/deadline records; four calls reach exact source-owned
CMSIS-FreeRTOS `osKernelGetTickCount`, while EasyLogger and one IAR `memset`
complete the utility boundary. See
[`g2-even-ai-timer-recovery.md`](g2-even-ai-timer-recovery.md).
The BLE-status callback facade is closed as three functions / 168 body bytes /
202 physical bytes. It adds a pathless notification dispatcher to the two
register/unregister anchors; all providers are admitted EasyLogger or the
first-party generic callback manager. See
[`g2-cb-ble-status-recovery.md`](g2-cb-ble-status-recovery.md).
The Conversate menu-page object is closed as eight functions / 1,492 body
bytes / 1,592 physical bytes. Five stored callbacks and all rendering calls
terminate at first-party policy or admitted LVGL/EasyLogger providers. See
[`g2-conversate-ui-menu-page-recovery.md`](g2-conversate-ui-menu-page-recovery.md).
The legal/regulatory event handler and its retained country/identifier content
table close as 234 body / 428 physical bytes over admitted providers; see
[`g2-legal-regulatory-recovery.md`](g2-legal-regulatory-recovery.md).
The S200 board-config object is now source-routed after correcting its leading
four zero bytes from code to retained pool. Its sole function is 114 stock
body bytes, has one stored Thumb entry pointer, and routes both canonical
profiles to a 38-byte C leaf implementing selector-3 nPMx/BQ charger-family
dispatch; live electrical qualification remains blocked by unavailable
physical evidence. See
[`g2-s200-board-config-recovery.md`](g2-s200-board-config-recovery.md).
The Conversate tag-page object is closed as eleven functions / 2,910 body
bytes / 3,056 physical bytes. Its 202 external calls terminate at admitted
EasyLogger, LVGL, exact CMSIS-FreeRTOS tick, bounded IAR DLIB, or first-party
UI policy; see
[`g2-conversate-ui-tag-page-recovery.md`](g2-conversate-ui-tag-page-recovery.md).
The exit-prompt object is closed as five functions / 782 body bytes / 900
physical bytes. Three restored callbacks complete the fade sequence, and all
utility edges terminate at admitted EasyLogger/LVGL; see
[`g2-exit-prompt-recovery.md`](g2-exit-prompt-recovery.md).
The eAT core object is closed as five functions / 666 body bytes / 724
physical bytes. Its four indirect callback sites and 85 direct entries are
pinned; all direct utility calls are admitted EasyLogger or bounded/source-
owned IAR DLIB. See [`g2-at-core-recovery.md`](g2-at-core-recovery.md).
The HAL I2C wrapper is closed as nine functions / 1,584 body bytes / 1,624
physical bytes. It provides a high-value shortcut into AmbiqSuite 5.1.0
IOM/GPIO APIs at public replay commit `5efc0228…`; see
[`g2-hal-i2c-recovery.md`](g2-hal-i2c-recovery.md).
The ring-battery service is now closed as five functions / 352 body bytes /
396 physical bytes. It is first-party record/cache policy over admitted
EasyLogger and a bounded IAR clear primitive, not an undiscovered utility; see
[`g2-service-ring-battery-recovery.md`](g2-service-ring-battery-recovery.md).
The OPT3007 register initializer is closed as one 340-byte body / 360 physical
bytes. Its stock store sequence exactly materializes 19 field descriptors from
TI SBOS864, while the implementation remains private G2 code; see
[`g2-opt3007-registers-recovery.md`](g2-opt3007-registers-recovery.md).
The codec UART-porting seam is closed as two functions / 342 body bytes / 414
physical bytes. Its ring initialization reaches the already production-owned
AndersKaloer source interval; UART lifecycle remains first-party. See
[`g2-service-codec-porting-recovery.md`](g2-service-codec-porting-recovery.md).
The notification thread is closed as twelve functions / 730 body bytes / 816
physical bytes. Thread create/terminate, flag, queue, and delay calls all
terminate at exact source-owned CMSIS-FreeRTOS v10.5.1 wrappers. All twelve
routines are production-routed from clean-room C. See
[`g2-thread-notification-recovery.md`](g2-thread-notification-recovery.md).
OTA and Ring complete the retained BLE-profile directory. OTA has seven
functions / 620 body bytes with a four-function AmbiqSuite AMOTA skeleton;
Ring has seven G2-local functions / 1,446 body bytes. See
[`g2-ble-ota-ring-profiles-recovery.md`](g2-ble-ota-ring-profiles-recovery.md).

## What is already source-replaced

First-party replacement is already extensive and proven: a large share of the
591 functions in `components/apollo_main/core_overlay` are first-party Even code
— the UI-module registry event/data dispatch, display-mode and onboarding
policy, the main display-thread loop and its display/BLE senders, the BLE
message-transmit thread and connection state machine, the MRAM
pairing/record database (update/activate/deactivate/query/allocate), the
lens-side status packet reporters, the SARC crash-report helpers, and the
EvenHub RLE/LZ4/IMU layer. The pipeline (disassemble → clean-room source →
overlay leaf → verify) is therefore established for first-party functions, not
only upstream libraries. The new profile-gating mechanism additionally lets an
alternate toolchain take on functions the reviewed apple-clang set has not.

## Ranking of the next first-party waves

Ordered by tractability (self-containment and testability), not importance:

1. **Pure protocol/format computations.** Deterministic, byte-verifiable:
   - the standard reflected CRC-32 (`0xEDB88320`) used by transport-protocol
     packet framing, OTA external-flash verification, and the box-UART manager
     (table at run `0x006987A8`; the table-driven update at run `0x0058FCF0`).
     Distinct from the already-replaced CRC-32C (`efs_crc32c`). **Done —
     production `linux-clang` leaf.** The 40-byte stock update is source-owned
     (`runtime_transport_crc32.c`) and redirected live; see
     [`first-party-transport-crc32-source-boundary-audit.md`](first-party-transport-crc32-source-boundary-audit.md).
   - the CRC-16/CCITT computation (poly `0x1021`, MSB-first), both stock
     variants — XMODEM seed `0x0000` at run `0x0059D350`, and resumable
     CCITT-FALSE seed `*ptr`/`0xFFFF` at run `0x0049ACD4` (48 callers). **Done —
     two production `linux-clang` leaves** (`runtime_crc16_ccitt.c`); see
     [`first-party-crc16-ccitt-source-boundary-audit.md`](first-party-crc16-ccitt-source-boundary-audit.md).
   - the G2 `0xAA` multipart packet layer in `transport_protocol.c`. **Done at
     production source level; hardware validation blocked.** Its 8-byte fragment header, four receive
     contexts, 1,500 ms timeout, send mutex, and complete send/receive graph are
     authenticated. The checksum is CRC-16/CCITT-FALSE through the already
     source-owned `0x0049ACD4` leaf, not CRC-32 and not TinyFrame CRC-16/ARC.
     All thirteen bodies are clean-room compiled and routed; live peer traffic
     remains blocked by unavailable authorized responsive hardware; see
     [`g2-transport-protocol-recovery.md`](g2-transport-protocol-recovery.md).
   These validate against the firmware byte-for-byte and are ideal first leaves.

2. **Fixed-layout serializers / accessors.** The pb_service_* wrappers around
   nanopb (now identified) marshal Even schemas to protobuf; the fixed field
   packing and the small getters/validators are self-contained. The complete
   retained-path census in
   [`g2-pb-service-frontier-ranking.md`](g2-pb-service-frontier-ranking.md)
   originally ranked 15 paths / 119 anchored bodies. `pb_service_translate.c` and
   `pb_service_glasses_case.c`, `pb_service_ring.c`,
   `pb_service_conversate.c`, `pb_service_teleprompt.c`,
   `pb_service_even_ai.c`, `pb_service_terminal.c`, and
   `pb_service_dev_config.c`, `pb_service_health.c`, and
   `pb_service_setting.c`, `pb_service_onboarding.c`, and
   `pb_service_notification.c` and `pb_service_dev_setting.c` are now closed in
   [`g2-pb-service-translate-recovery.md`](g2-pb-service-translate-recovery.md)
   and
   [`g2-pb-service-glasses-case-recovery.md`](g2-pb-service-glasses-case-recovery.md),
   [`g2-pb-service-ring-recovery.md`](g2-pb-service-ring-recovery.md),
   [`g2-pb-service-conversate-recovery.md`](g2-pb-service-conversate-recovery.md),
   and
   [`g2-pb-service-teleprompt-recovery.md`](g2-pb-service-teleprompt-recovery.md),
   [`g2-pb-service-even-ai-recovery.md`](g2-pb-service-even-ai-recovery.md),
   [`g2-pb-service-terminal-recovery.md`](g2-pb-service-terminal-recovery.md),
   [`g2-pb-service-dev-config-recovery.md`](g2-pb-service-dev-config-recovery.md),
   [`g2-pb-service-health-recovery.md`](g2-pb-service-health-recovery.md), and
   [`g2-pb-service-setting-recovery.md`](g2-pb-service-setting-recovery.md), and
   [`g2-pb-service-onboarding-recovery.md`](g2-pb-service-onboarding-recovery.md),
   and
   [`g2-pb-service-notification-recovery.md`](g2-pb-service-notification-recovery.md),
   and
   [`g2-pb-service-dev-setting-recovery.md`](g2-pb-service-dev-setting-recovery.md),
   and
   [`g2-pb-service-quicklist-recovery.md`](g2-pb-service-quicklist-recovery.md),
   and
   [`g2-pb-service-pair-mgr-recovery.md`](g2-pb-service-pair-mgr-recovery.md).
   All 15 retained protobuf-service paths are now closed: 143 linked functions,
   47,644 body bytes, and 51,744 physical bytes. All 15 are production-routed
   for all 47,644 stock body bytes. Pair-manager contributes 21 clean-room
   source leaves, 2,300 compiled bytes plus 22 alignment bytes, and 97 strict
   relocations; its live peer behavior is explicitly hardware-blocked by
   unavailable authorized responsive G2 evidence.

3. **Device-control state helpers.** The NVDB buzzer, product-mode, MAC,
   advertising-magic, sensor-calibration, and system-data record helpers are now fully
   bounded and have
   host/Thumb-qualified clean-room candidates; production routing remains
   deferred. The MAC increment also
   closes the device-specific `CHIPID1 || CHIPID0` address derivation. The
   system-data increment also closes the 172-byte record and OTP PSN journal;
   the adjacent temperature-unit and time-format KVDB helpers are closed too.
   The primary `kvSetting`, adjacent `kvAlsScale`, compact terminal-mode, and
   timestamp/timezone, onboarding-config, ring, and module-configuration
   objects are now closed as well. Those ten objects account for every retained
   `service_kvdb_*.c` path. The five retained ULED objects and all three
   charger objects are likewise bounded, while the RTC initialize/set/get path
   is already production source-owned. The retained
   `driver/buzzer/drv_buzzer.c` object is now bounded too: 17 linked bodies,
   its PWM/voice tables, queued-event contract, timer callback, and complete
   ingress topology are pinned in
   [`g2-drv-buzzer-recovery.md`](g2-drv-buzzer-recovery.md). The compact
   `driver/wdt/watchdog.c` follow-on is also closed in
   [`g2-watchdog-recovery.md`](g2-watchdog-recovery.md): two linked bodies,
   selector-gated enable behavior, and complete ingress closure. The retained
   `platform/service/eAT/at_buzzer.c` consumer is now closed too in
   [`g2-at-buzzer-recovery.md`](g2-at-buzzer-recovery.md): one 1,014-byte
   command handler, its stored `AT^BUZZER` registration, all four subcommands,
   and complete buzzer-driver call topology are pinned. Its adjacent
   `AT^AUDIO`/`at_codec.c` object is also closed in
   [`g2-at-codec-recovery.md`](g2-at-codec-recovery.md): one 118-byte handler,
   stored registration, and both selector-seven audio-provider calls. Retained
   `at_fs.c` is now closed in [`g2-at-fs-recovery.md`](g2-at-fs-recovery.md):
   four bodies, three registered commands, recursive list behavior, and exact
   filesystem gate/provider closure. The next retained eAT census is
   `at_tp.c`, now closed in [`g2-at-tp-recovery.md`](g2-at-tp-recovery.md):
   two bodies, stored registration, diff/debug/baseline operations, and
   verified gesture-configuration persistence. This completes all four
   retained eAT source paths. The pathless registered-command cluster from
   `AT^INFO` through `AT^BRIGHTNESS_READ` is now closed too in
   [`g2-eat-core-sensor-recovery.md`](g2-eat-core-sensor-recovery.md): twelve
   handlers, twelve stored registrations, 49 body calls, and the complete
   product/reset/PSN/IMU/screen/ALS/brightness contract are pinned. A compact
   adjacent standalone `AT^NUS` registration and handler is now closed in
   [`g2-at-nus-recovery.md`](g2-at-nus-recovery.md): its twelve-byte body,
   four-byte pool, sole stored entry, response, and provider call are pinned.
   The pathless `AT^CLEANBOND` / `AT^BLE_KEEPCONNECT` pair is now source-closed too
   in [`g2-eat-bond-connect-recovery.md`](g2-eat-bond-connect-recovery.md):
   both bodies, both command entries, four provider calls, the exact boundary
   before `at_buzzer.c`, and dual-profile production routing are pinned. Live
   bond deletion/re-pairing and keep-connect effects remain explicitly blocked
   by unavailable authorized G2/peer evidence. The aggregate registry audit in
   [`g2-eat-registry-recovery.md`](g2-eat-registry-recovery.md) proves these
   are all 21 valid stock eAT records and assigns every handler to a closed
   analysis. The registered eAT runtime frontier is therefore complete;
   resume the higher-ranked fixed-layout protobuf/accessor wave next.
   See
   [`g2-nvdb-buzzer-recovery.md`](g2-nvdb-buzzer-recovery.md),
   [`g2-nvdb-product-mode-recovery.md`](g2-nvdb-product-mode-recovery.md), and
   [`g2-nvdb-mac-recovery.md`](g2-nvdb-mac-recovery.md), and
   [`g2-nvdb-sensor-caldata-recovery.md`](g2-nvdb-sensor-caldata-recovery.md),
   and [`g2-nvdb-sys-dt-recovery.md`](g2-nvdb-sys-dt-recovery.md).
   The compact KVDB sibling is documented in
   [`g2-kvdb-temperature-unit-recovery.md`](g2-kvdb-temperature-unit-recovery.md)
   and [`g2-kvdb-time-format-recovery.md`](g2-kvdb-time-format-recovery.md).
   The version-3 universal-setting sibling is documented in
   [`g2-kvdb-universal-setting-recovery.md`](g2-kvdb-universal-setting-recovery.md).
   The primary version-4 record is documented in
   [`g2-kvdb-setting-recovery.md`](g2-kvdb-setting-recovery.md).
   The adjacent ALS-scale record is documented in
   [`g2-kvdb-als-scale-recovery.md`](g2-kvdb-als-scale-recovery.md).
   The compact mode record is documented in
   [`g2-kvdb-terminal-mode-recovery.md`](g2-kvdb-terminal-mode-recovery.md).
   The timestamp/timezone record is documented in
   [`g2-kvdb-time-recovery.md`](g2-kvdb-time-recovery.md).
   The one-byte onboarding record is documented in
   [`g2-kvdb-onboarding-config-recovery.md`](g2-kvdb-onboarding-config-recovery.md).
   The MAC/name ring record is documented in
   [`g2-kvdb-ring-recovery.md`](g2-kvdb-ring-recovery.md).
   The packed menu/scalar module configuration is documented in
   [`g2-kvdb-module-configure-recovery.md`](g2-kvdb-module-configure-recovery.md).
   The first ULED leaf is documented in
   [`g2-uled-display-preprocess-recovery.md`](g2-uled-display-preprocess-recovery.md).
   The first charger leaf is documented in
   [`g2-chg-bq25180-recovery.md`](g2-chg-bq25180-recovery.md), and its
   synchronization/aggregation layer is documented in
   [`g2-charger-common-recovery.md`](g2-charger-common-recovery.md). The
   BQ27427 fuel-gauge path is now documented in
   [`g2-chg-bq27427-recovery.md`](g2-chg-bq27427-recovery.md). The common ULED
   MSPI transport and both panel drivers are now bounded and characterized in
   [`g2-uled-mspi-common-recovery.md`](g2-uled-mspi-common-recovery.md) and
   [`g2-uled-jbd4010-recovery.md`](g2-uled-jbd4010-recovery.md) and
   [`g2-uled-a6ng-recovery.md`](g2-uled-a6ng-recovery.md), with the selector and
   full operations ABI closed in
   [`g2-uled-manager-recovery.md`](g2-uled-manager-recovery.md). Every retained
   first-party ULED path is now bounded. The caller/orchestration body at
   `0x00473C44` is already source-owned as the display-manager receive loop, so
   it is not a new pathless attribution frontier. Remaining ULED work is the
   clean-room implementation and provider validation for the five historical
   first-party objects whose source inventories are unavailable. The adjacent
   anonymous key/record closure is documented in
   [`g2-nvdb-adv-magic-recovery.md`](g2-nvdb-adv-magic-recovery.md).

4. **UI glue.** `app/gui` is the largest surface but the most LVGL-coupled.
   The LVGL v9.3 boundary is now vendored and the first compact UI object,
   `PdtDistortionTest/pdt_distortion_test.c`, is fully bounded. The formerly
   deferred large dashboard, terminal, and navigation objects are now closed
   too: with the final campaign, all 234 retained paths — including every
   `app/gui` object — are closed, and no frontier target selection remains.

The retained-path frontier is now fully closed: 234 closed / 0 open, all
1,230 anchored functions and all 485,274 anchored body bytes. The remaining
ranking below is retained for production-routing order, not discovery order.

## Method

Each wave is the established, mechanised pipeline, run on Linux:

1. Focused disassembly to recover the function's exact contract (from the
   memory map, strings, and instruction behaviour).
2. A clean-room `.c` re-expression under `components/apollo_main/core_overlay`.
3. A profile-gated overlay leaf (`"profiles": ["linux-clang"]`) plus a `b_w`
   redirect at the stock address, so the canonical apple-clang overlay stays
   byte-identical while linux-clang carries the replacement.
4. Record the linux-clang pins; `make source verify` reproduces fail-closed.
5. A host/target test validating byte or behavioural equivalence.

Because first-party functions have no upstream oracle, wave 1's pure
computations (which do have a byte-exact firmware oracle — the CRC table and
known check values) are the right place to continue, before moving to
behaviourally-specified Even logic.

This document does not sign, flash, connect to, or mutate hardware.
