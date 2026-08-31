# G2 first-party retained-path frontier census

> Readiness accounting note: the 885,418 known physical bytes below are
> overlapping complete-object evidence. They are not a disjoint firmware
> bucket and must not be added to Apollo's origin, unanchored, retained, or
> release-blocking totals. See the current
> [Wave-0 reconciliation](g2-wave0-readiness-ledger-reconciliation.md).

Status: reproducible lower-bound census over the authenticated 2.2.6.10 image
and 7,370-function Ghidra corpus. This is analysis only and performs no device
or flash operation.

## Result

The image retains 234 distinct first-party/project `__FILE__` paths. All 234
now have complete linked-object closure records and zero remain open. Of the
234 paths, 200 anchor at least one discovered function and 34 retain no
function reference in the authenticated corpus.

The closed/open split is disjoint at function level: all 1,230 anchored
functions / 485,274 body bytes belong to closed paths, and zero functions
remain on open paths. The 234 complete-object records account for 814,534
body bytes after adding restored non-anchor functions; 232 records also
report 885,418 known physical bytes. The older ULED display-preprocess
manifest and the compact-log core closure deliberately omit physical-byte
metrics.

This means 100% of retained paths, 100% of path-anchored functions, and
100% of path-anchored body bytes are closed. These percentages are not
whole-image source coverage: retained paths are lower-bound ownership
anchors, pathless translation units exist, and object closure does not imply
historical source availability or production ownership.

## Current frontier

The frontier is empty: all 234 retained paths are closed and zero remain
open. The final closure campaign closed the last 53 objects, advancing the
frontier from 181 closed / 53 open to 234 closed / 0 open. Its 32 anchored
closures began with the five former largest open anchors —

| Former rank | Anchored bytes | Functions | Retained path |
|---:|---:|---:|---|
| 1 | 1,428 | 5 | `app\gui\conversate\conversate_pb_msg_handler.c` |
| 2 | 1,350 | 3 | `app\gui\quicklist\quicklist_data_manager.c` |
| 3 | 1,310 | 2 | `app\gui\EvenAI\even_ai_animation.c` |
| 4 | 1,290 | 4 | `app\gui\onboarding\onboarding_animation.c` |
| 5 | 1,238 | 6 | `platform\threads\thread_manager.c` |

— and continued through `app\gui\terminal\terminal_ui.c` (99 functions /
13,200 body bytes). The remaining 21 closures are zero-anchor
linked-unanchored recoveries (for example `app\gui\setting\setting.c`, 18
functions / 5,486 body bytes) plus two zero-additional-byte attestations
(`msg_notif_timer.c` and `translate_data.c`) whose code extents were already
claimed by sibling closures. No new version or commit discriminator was
found in any of the 53 closures. The per-object narrative is in
[`../progress.md`](../progress.md).

Legacy closure metadata now also admits `app_ble.c`, `thread_ble_wsf.c`,
`thread_ble_msgtx.c`, `thread_ble_msgrx.c`, and
`service_nvdb_product_mode.c` without repeating their fail-closed object
audits. `service_codec_host.c`, `service_codec_dfu.c`, `service_touch_dfu.c`,
`terminal_pb_msg_handler.c`, `service_whitelist.c`, and
`teleprompt_page_data.c`, and `imu_icm45608.c` have moved from the open
frontier into the closed set.
The former rank-one `platform\product_test\pt_protocol_procsr.c` object is now
closed as 73 functions / 32,866 body bytes / 35,524 physical bytes. Sixty-nine
path anchors expand through three pathless Ghidra bodies and a hidden handler
at `0x0056F92C`; its sole indirect call is constrained to a 66-entry aligned
Thumb handler table. All 1,526 external direct calls terminate at selected or
bounded providers, so the object contributes no new third-party family or
version discriminator. See
[`g2-pt-protocol-procsr-dependency-boundary.md`](g2-pt-protocol-procsr-dependency-boundary.md).
The zero-Ghidra-anchor `platform\service\callback_mgr\cb_ring_battery.c`
record is also closed from raw source order as five functions / 122 body bytes /
152 physical bytes; its recovered path anchor is therefore absent from the
baseline anchored-function denominator by design.
The same raw source-order method closes the zero-anchor `cb_charge.c` and
`cb_msg_notif.c` siblings as five functions / 190 body bytes / 224 physical
bytes each, again without changing the baseline anchored-function denominator.
Their shared `callback_manager.c` provider is now closed as eight functions /
1,240 body bytes / 1,360 physical bytes, including the restored deinitializer
and bounded registered-callback notification site.
The newly isolated `platform\ble\app_ble_peer_mgr.c` and
`platform\ble\app_ble_discovery.c` objects are also closed as G2-local Cordio
policy: six functions, 3,408 body bytes, and 4,236 physical bytes combined.
Their third-party ancestry ends at already admitted Cordio APIs; the product
state and sequencing are first-party.
The adjacent `platform\ble\app_ble_central.c` object is now closed too. Its
24 path anchors expand to 44 complete functions / 14,288 body bytes / 15,752
physical bytes after admitting the pathless RingLink state helper and 19 other
rooted non-anchor bodies. It owns scan/connect, seven-state RingLink,
dominant-hand, retry, unpair-cleanup, and scene-reconnect product policy over
Cordio APIs. See
[`g2-app-ble-central-recovery.md`](g2-app-ble-central-recovery.md).
The connection-parameter sibling is now closed as 14 functions / 6,336 body
bytes / 6,888 physical bytes. It is G2-local fast/slow scheduling and retry
policy over Cordio DM/WSF providers, with thresholds 25 and 72 BLE units and
five authenticated delay classes. Its two apparent strict-interior BL targets
are second-halfword artifacts inside `sdiv` and `udiv`, not alternate entries.
See [`g2-app-connect-params-recovery.md`](g2-app-connect-params-recovery.md).
The peripheral-role sibling is closed as 31 functions / 5,888 body bytes /
6,560 physical bytes. Seven rooted bodies missed by the baseline sweep complete
advertising-event, unpair/restart, and connection-sync callbacks. Its Cordio
provider seam is already source-identified at the selected AmbiqSuite 2.5.1
commit; the object itself is downstream G2 policy. See
[`g2-app-ble-peripheral-recovery.md`](g2-app-ble-peripheral-recovery.md).
The G2 multipart `platform\protocols\transport_protocol\transport_protocol.c`
object is also closed as 13 functions / 4,134 body bytes / 4,436 physical
bytes. Its checksum is the already source-owned first-party CCITT-FALSE leaf,
not TinyFrame: all 193 body calls and aligned object words contain zero edges
to the authenticated TinyFrame object. The actual third-party relationships
terminate at admitted CMSIS-FreeRTOS v10.5.1, Cordio WSF message, EasyLogger,
and indirect TLSF provider seams. All thirteen bodies are now production
source-owned (2,538 compiled bytes, 55 strict relocations); live peer traffic
qualification is blocked by unavailable authorized responsive hardware. See
[`g2-transport-protocol-recovery.md`](g2-transport-protocol-recovery.md).
The settings-service object is now closed as 31 functions / 5,146 body bytes /
5,712 physical bytes. Eleven recursively recovered bodies complete its version
sync, record persistence, auto-brightness, and head-up paths. Its only
third-party seams are already admitted EasyLogger and CMSIS-FreeRTOS plus the
known family-level IAR DLIB boundary; it embeds no opaque upstream definition
and adds no exact-IAR discriminator. See
[`g2-service-settings-recovery.md`](g2-service-settings-recovery.md).
The tracepoint-settings object is now closed as 21 functions / 5,100 body
bytes / 5,588 physical bytes. Four recursively recovered handlers complete its
file deletion and BLE dispatch paths. Its 252 external calls terminate at
already admitted EasyLogger, nanopb, IAR DLIB, littlefs-backed file wrappers,
and first-party message seams; it embeds no opaque third-party definition. See
[`g2-tracepoint-setting-recovery.md`](g2-tracepoint-setting-recovery.md).
The product `rtos.c` object is closed as 13 functions / 512 body bytes / 548
physical bytes. Its task-vote policy and five FreeRTOS application hooks are
fully bounded. More importantly, the two-WFI stock system-sleep provider
excludes public Apollo510 HAL 5.0.0 and selects 5.1.0-lineage source at public
replay commit `5efc0228…`; the earlier firmware build time proves the actual
generating checkout was a private pre-release snapshot. See
[`g2-product-rtos-recovery.md`](g2-product-rtos-recovery.md).
The small `utils\assert\util_error_check.c` object is now closed as one
178-byte function plus 34 bytes of alignment/literals. Its separately located
43-row / 344-byte table and formatter identify a copied Goodix GR551x SDK 1.7.0
`app_error.c` helper despite the first-party retained path. The source blob is
exact, while the official SDK-release and Even generating commits remain
unavailable. See
[`g2-util-error-check-goodix-recovery.md`](g2-util-error-check-goodix-recovery.md).
The deceptively small `app\gui\logger\logger_setting.c` anchor is now closed
as an eight-function / 5,574-body-byte / 5,992-physical-byte object after
recovering five functions and eight embedded data islands missed by baseline
Ghidra. Its 338 external calls terminate at already admitted EasyLogger,
nanopb, littlefs-backed file, FreeRTOS, IAR DLIB, and first-party seams. No new
dependency family or version discriminator appears. See
[`g2-logger-setting-recovery.md`](g2-logger-setting-recovery.md).
The neighboring single-anchor `app\ux\ux_system\ux_system.c` path is now
closed as eleven functions / 2,668 body bytes / 2,868 physical bytes. Its
2,232-byte stored callback synchronizes OTA, BLE, ring-MAC, and ring-link state
through six message IDs. The only third-party edge is diagnostic logging into
the already admitted EasyLogger baseline; no utility implementation or new
version evidence appears. See
[`g2-ux-system-recovery.md`](g2-ux-system-recovery.md).
The next 94-byte `app\gui\health\health.c` anchor expands to four functions /
504 body bytes / 572 physical bytes after recovering its mutex initializer and
stored common-event callback. Its CMSIS mutex calls land on the exact,
production-source-owned CMSIS-FreeRTOS v10.5.1 wrappers; all other boundaries
are admitted EasyLogger or first-party policy. See
[`g2-health-recovery.md`](g2-health-recovery.md).
The adjacent 94-byte `app\gui\quicklist\quicklist.c` anchor is likewise closed
as four functions / 310 body bytes / 360 physical bytes. Its exact
CMSIS-FreeRTOS mutex seam and stored event callback mirror the health object's
structure and add no hidden utility or version evidence. See
[`g2-quicklist-recovery.md`](g2-quicklist-recovery.md).
The next compact UI anchor,
`app\gui\dashboard\dashboard_watchface_manager.c`, expands from one 98-byte
anchor to 17 functions / 956 body bytes / 1,044 physical bytes. Four pinned
15-slot operation tables close all 15 register-indirect calls into first-party
watchface implementations. The only third-party edge is admitted EasyLogger;
there is no hidden utility or version evidence. See
[`g2-dashboard-watchface-manager-recovery.md`](g2-dashboard-watchface-manager-recovery.md).
The smallest remaining anchor at that point,
`app\gui\EvenAI\text_stream_service.c`, expands from 116 bytes to 26 functions
/ 3,188 body bytes / 3,228 physical bytes. A PC-relative `animate_text`
callback emits complete UTF-8 code points, while all utility edges terminate
at already admitted CMSIS-FreeRTOS, LVGL, nanopb, TLSF, EasyLogger, and IAR
seams. See [`g2-text-stream-service-recovery.md`](g2-text-stream-service-recovery.md).
The next 122-byte `app\gui\terminal\terminal.c` anchor expands to nine
functions / 1,144 body bytes / 1,248 physical bytes, including three stored
callbacks and the terminal command dispatcher. Its utility edges stop at
admitted EasyLogger, CMSIS-FreeRTOS, and IAR seams. See
[`g2-terminal-core-recovery.md`](g2-terminal-core-recovery.md).
The next 130-byte `driver\rtc\drv_rtc.c` anchor is the complete
`DRV_RtcSetTime` wrapper plus a 22-byte pool, for 152 physical bytes. Its two
functional providers are now identified as AmbiqSuite
`am_util_time_computeDayofWeek` and Apollo510 `am_hal_rtc_time_set` at the
selected 5.1.0 public replay `5efc022…`; OpenCFW already production-routes the
body to a tested source replacement. See
[`g2-drv-rtc-recovery.md`](g2-drv-rtc-recovery.md).
The next 144-byte `app\gui\teleprompt\teleprompt_file_list.c` anchor expands
to three functions / 166 body bytes / 200 physical bytes. It owns a single
`0xF52`-byte global record and only calls admitted EasyLogger plus bounded IAR
`memcpy`/`memset`; no nanopb body is embedded. See
[`g2-teleprompt-file-list-recovery.md`](g2-teleprompt-file-list-recovery.md).
The next 152-byte `app\gui\EvenAI\even_ai_timer.c` anchor expands to 13
functions / 856 body bytes / 956 physical bytes. It owns two private
tick/deadline records rather than CMSIS software timers. Its only third-party
edges are exact source-owned `osKernelGetTickCount`, admitted EasyLogger, and
one bounded IAR `memset`; see
[`g2-even-ai-timer-recovery.md`](g2-even-ai-timer-recovery.md).
The next 154-byte `platform\service\callback_mgr\cb_ble_status.c` anchor closes
as three functions / 168 body bytes / 202 physical bytes. Register,
unregister, and notification dispatch reach only admitted EasyLogger and the
first-party generic callback manager; see
[`g2-cb-ble-status-recovery.md`](g2-cb-ble-status-recovery.md).
The next 218-byte `conversate_ui_menu_page.c` anchor expands to eight functions
/ 1,492 body bytes / 1,592 physical bytes with five stored UI callbacks. Its
utility graph closes over admitted LVGL and EasyLogger only; see
[`g2-conversate-ui-menu-page-recovery.md`](g2-conversate-ui-menu-page-recovery.md).
The 234-byte legal/regulatory handler plus its complete regional content pool
is also closed at 428 physical bytes; see
[`g2-legal-regulatory-recovery.md`](g2-legal-regulatory-recovery.md).
The adjacent 238-byte `conversate_ui_tag_page.c` anchor expands to eleven
functions / 2,910 body bytes / 3,056 physical bytes. Its provider graph closes
over admitted EasyLogger, LVGL, exact CMSIS-FreeRTOS tick access, bounded IAR
DLIB, and first-party UI policy; see
[`g2-conversate-ui-tag-page-recovery.md`](g2-conversate-ui-tag-page-recovery.md).
The smallest remaining anchor, `app\gui\anim\exit_prompt.c`, is now closed as
five functions / 782 body bytes / 900 physical bytes. Its utility calls stop
at admitted EasyLogger/LVGL, while three calls enter first-party fade policy;
see [`g2-exit-prompt-recovery.md`](g2-exit-prompt-recovery.md).
The eAT core is now closed as five functions / 666 body bytes / 724 physical
bytes. Its formatter/runtime calls are already bounded or source-owned, and
no public upstream fingerprint was found; see
[`g2-at-core-recovery.md`](g2-at-core-recovery.md).
The HAL I2C wrapper is closed as nine functions / 1,584 body bytes / 1,624
physical bytes. Its Apollo510 IOM/GPIO dependency maps to the selected
AmbiqSuite 5.1.0 source family; see
[`g2-hal-i2c-recovery.md`](g2-hal-i2c-recovery.md).
The ring-battery service is closed as five functions / 352 body bytes / 396
physical bytes. Its two sends terminate at first-party service transport, and
all utility calls are admitted EasyLogger or bounded IAR `memset`; see
[`g2-service-ring-battery-recovery.md`](g2-service-ring-battery-recovery.md).
The OPT3007 register-map initializer is closed as one 340-byte function plus a
20-byte pool. Its 19 descriptor triples exactly reproduce TI datasheet
SBOS864's register fields; see
[`g2-opt3007-registers-recovery.md`](g2-opt3007-registers-recovery.md).
The codec UART-porting seam is closed as two functions / 342 body bytes / 414
physical bytes. Its only reusable call is production-source-owned
AndersKaloer Ring-Buffer initialization; see
[`g2-service-codec-porting-recovery.md`](g2-service-codec-porting-recovery.md).
The notification thread expands to eleven functions / 702 body bytes / 816
physical bytes. Its seven RTOS calls are exact production-source-owned
CMSIS-FreeRTOS v10.5.1 wrappers; see
[`g2-thread-notification-recovery.md`](g2-thread-notification-recovery.md).
The FlashDB service adapter expands from five anchors / 462 bytes to eleven
functions / 908 body bytes / 1,040 physical bytes. Its reusable edges terminate
at authenticated FlashDB 2.1.1, CMSIS-FreeRTOS v10.5.1, and EasyLogger seams;
the stock zero-on-driver-failure FAL behavior is now an explicit OpenCFW
porting constraint. See
[`g2-service-db-api-recovery.md`](g2-service-db-api-recovery.md).
The EvenAI UI object expands from two anchors / 346 bytes to 43 functions /
8,004 body bytes / 8,424 physical bytes. All 413 external calls terminate at
admitted LVGL, EasyLogger, CMSIS-FreeRTOS, bounded IAR DLIB, or first-party
EvenAI/UI providers; see
[`g2-ui-even-ai-recovery.md`](g2-ui-even-ai-recovery.md).
The time-service object expands from two anchors / 438 bytes to eleven primary
functions / 1,308 body bytes / 1,384 physical bytes. Its calendar conversion,
12/24-hour formatting, system-time synchronization, RPC, and registered
callback paths close over bounded IAR DLIB and first-party providers; it makes
no direct CMSIS-FreeRTOS call and embeds no third-party definition. See
[`g2-service-time-recovery.md`](g2-service-time-recovery.md).
The audio-thread object expands from three anchors / 394 bytes to 31 functions /
2,954 body bytes / 3,258 physical bytes. Twenty CMSIS-FreeRTOS calls terminate
at fourteen exact v10.5.1 wrappers, while 19 more calls compose the closed codec
DFU, codec-host, and GX8002B objects. One bounded IAR fill remains; no
NationalChip code or other third-party body is linked. See
[`g2-thread-audio-recovery.md`](g2-thread-audio-recovery.md).
The compact-log core expands from two anchors / 520 bytes to eight functions /
2,300 contiguous executable bytes. Its private 5,718-caller compact-output hook
at `0x0043CE9E` is now separated from the authenticated upstream-derived
EasyLogger `elog_output` at `0x0043D574`; it composes admitted EasyLogger,
CMSIS-FreeRTOS, FreeRTOS, and bounded IAR seams but embeds none of them. The
interleaved post-body literal cells are authenticated without overclaiming one
physical object interval. See
[`g2-compress-log-core-recovery.md`](g2-compress-log-core-recovery.md).
Its port sibling expands from three anchors / 680 bytes to twelve functions /
1,324 body bytes / 1,464 physical bytes. All eighteen file edges already reach
production source-owned wrappers over littlefs v2.10.1-equivalent commit
`0494ce71…`, and all three timeout edges reach production source-owned delayed
callback wrappers. Only two bounded IAR `snprintf` calls remain as a compiler
seam. See
[`g2-compress-log-port-recovery.md`](g2-compress-log-port-recovery.md).
The retained `product\s200\app\config\redirect.c` path is the complete shared
file/directory/synchronized-heap runtime: eighteen functions / 2,266 body
bytes / 2,404 physical bytes. All eighteen entries were already production
source-owned; the closure now formally terminates their providers at selected
CMSIS-FreeRTOS, littlefs, TLSF, EasyLogger, bounded IAR, and first-party seams.
See [`g2-file-runtime-recovery.md`](g2-file-runtime-recovery.md).
The smallest formerly open UI object,
`PdtDistortionTest/pdt_distortion_test.c`, is now closed as four linked
functions / 850 body bytes / 896 physical bytes, including a four-byte
registered predicate missed by the original Ghidra function census.
Its adjacent `PdtGrayScreen/pdt_gray_screen.c` sibling is also closed as three
functions / 340 body bytes / 372 physical bytes. Because its retained path is
loaded by a handler that Ghidra missed, this second closure increases complete
object coverage without changing the path-anchored function lower bound.
The contiguous family endpoint, `ProductionTest/production_test.c`, is closed
as three functions / 286 body bytes / 316 physical bytes and likewise adds no
Ghidra path anchor because all of its linked functions were originally missed.
The copied `platform/ble/profiles/gatt/profile_gatt.c` path is now correctly
classified as Packetcraft Cordio `gatt_main.c`: six functions / 322 body bytes /
356 physical bytes are source-owned at selected r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`.
The neighboring `platform/ble/profiles/ancc/profile_ancc.c` path is also a
hidden upstream copy: its 21-function / 3,712-body-byte / 3,980-physical-byte
object is founded on AmbiqSuite's 17-definition ANCC profile. Twelve stock
functions remain source-derived and nine are bounded G2 message/sync/whitelist
extensions. The selected reproducible baseline is AmbiqSuite 2.5.1 commit
`de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`; the implementation is identical
from authenticated 2.2.0 through 2.5.1 imports, so the private generating
commit remains unobservable. See
[`ambiqsuite-ancc-profile-source-recovery.md`](ambiqsuite-ancc-profile-source-recovery.md).
The contiguous EUS/ESS/EFS/NUS profile group is now closed as four first-party
Cordio adapters: 21 linked functions / 2,374 body bytes / 3,000 physical bytes.
The profiles share the product event/provider ABI but match neither AmbiqSuite
profile sources nor Nordic's `ble_nus_*` implementation. See
[`g2-ble-transport-profiles-recovery.md`](g2-ble-transport-profiles-recovery.md).
The final OTA/Ring pair closes every retained `platform\ble\profiles` path.
OTA retains AmbiqSuite AMOTA ancestry in four of seven functions, with 2.5.1
selected as a source oracle; Ring's seven functions are G2-local. See
[`g2-ble-ota-ring-profiles-recovery.md`](g2-ble-ota-ring-profiles-recovery.md).
The nPMX transplant wrapper is now closed as thirty functions / 6,560 body
bytes / 7,102 physical bytes. Its 72 direct nPMX calls expose adjacent-commit
fingerprints: the February ADC result-register rewrite is present and the
April float-promotion fix is absent. This uniquely selects official public
commit `e1aaec53…` (`v1.0.1-1-ge1aaec5`), whose driver snapshot is now admitted
under `third_party/npmx`. Production routing still requires the nPM1300
ADK/configuration, Apollo510 I2C and interrupt integration, and G2 rail policy.
See [`g2-npmx-main-driver-recovery.md`](g2-npmx-main-driver-recovery.md).
The navigation data handler is now closed as 22 functions / 8,076 reachable
code bytes / 8,556 physical bytes. Control-flow recovery restores the
cross-shard dispatcher and separates its two inline literal pools. All 423
external edges terminate at admitted EasyLogger, nanopb, CMSIS-FreeRTOS,
bounded IAR/runtime, or first-party policy providers; no new third-party
dependency is embedded. See
[`g2-navigation-data-handler-recovery.md`](g2-navigation-data-handler-recovery.md).
The audio service is now closed as 14 functions / 2,676 body bytes / 2,884
physical bytes. Its five Google liblc3 calls terminate at the admitted v1.1.3
tagged baseline, and the only indirect call resolves through three static
registrations to two closed production-microphone callbacks. See
[`g2-service-audio-recovery.md`](g2-service-audio-recovery.md).
The adjacent zero-anchor `driver\pdm\drv_pdm_production.c` record is also
closed as six functions / 610 body bytes / 704 physical bytes. Its 13 HAL calls
map to 12 Apollo510 PDM APIs in the same AmbiqSuite 5.1.0 public replay commit
already selected for the I2S and RTOS seams; its three embedded helper bodies
are CMSIS-Core NVIC definitions. See
[`g2-drv-pdm-production-recovery.md`](g2-drv-pdm-production-recovery.md).
The zero-anchor generic `driver\pdm\drv_pdm.c` object adds seven functions /
794 body bytes / 900 physical bytes, a vector-proven PDM0 IRQ handler, and two
additional public HAL APIs. See
[`g2-drv-pdm-recovery.md`](g2-drv-pdm-recovery.md).
The input manager is now closed as ten functions / 2,242 body bytes / 2,490
physical bytes. Five path anchors expand through five adjacent helpers. Its 103
external calls terminate at admitted EasyLogger, CMSIS-FreeRTOS, nanopb,
bounded memory/runtime leaves, or first-party input/event providers; it calls
neither LVGL nor Cordio and embeds no reusable implementation. See
[`g2-service-input-manager-dependency-boundary.md`](g2-service-input-manager-dependency-boundary.md).
The calendar page is now closed as fifteen functions / 9,690 body bytes /
10,172 physical bytes. Three restored functions complete its page lifecycle
and timers; its utility graph terminates at admitted LVGL, EasyLogger, and
CMSIS-FreeRTOS plus bounded IAR and first-party providers. See
[`g2-ui-calendar-page-dependency-boundary.md`](g2-ui-calendar-page-dependency-boundary.md).
The OTA transport is closed as three functions / 2,004 body bytes / 2,292
physical bytes. Four indirect calls are bounded to two first-party registered
callback slots; every direct edge terminates at admitted/source-owned utility
providers or already closed first-party OTA policy. See
[`g2-ota-transport-dependency-boundary.md`](g2-ota-transport-dependency-boundary.md).
The EFS transport is closed as two functions / 1,990 body bytes / 2,152
physical bytes. Its utility graph mirrors OTA transport and additionally pins
one exact CMSIS-FreeRTOS v10.5.1 tick call. See
[`g2-efs-transport-dependency-boundary.md`](g2-efs-transport-dependency-boundary.md).
The EvenHub loading page is closed as four functions / 2,042 body bytes /
2,328 physical bytes. Its external graph contains only admitted LVGL and
EasyLogger, bounded runtime, and first-party providers; two stored function
pointers close ingress. See
[`g2-evenhub-loading-page-dependency-boundary.md`](g2-evenhub-loading-page-dependency-boundary.md).
Dashboard watchface layout 1 is closed as nineteen functions / 3,500 body
bytes / 3,592 physical bytes. Ten stored-table and source-order routines were
restored beyond Ghidra; both indirect sites bind to recovered local callbacks.
Its provider graph terminates at admitted LVGL, EasyLogger, and mpaland printf,
bounded IAR, or first-party dashboard services. See
[`g2-dashboard-watchface-layout1-recovery.md`](g2-dashboard-watchface-layout1-recovery.md).
The teleprompt FSM is closed as fifteen functions / 2,994 body bytes / 3,302
physical bytes. Eight handlers were restored beyond Ghidra; its single
indirect call is bounded by a nine-entry authenticated local handler table.
Its utility edges terminate at admitted EasyLogger, LVGL, and nanopb, bounded
IAR, or first-party teleprompt providers. See
[`g2-teleprompt-fsm-dependency-boundary.md`](g2-teleprompt-fsm-dependency-boundary.md).
The health data manager is closed as ten functions / 2,644 body bytes / 2,912
physical bytes. One parser was restored beyond Ghidra. Its calls terminate at
admitted EasyLogger, bounded runtime, or already closed health lock wrappers
over exact CMSIS-FreeRTOS; no reusable health algorithm or DSP body appears.
See
[`g2-health-data-manager-dependency-boundary.md`](g2-health-data-manager-dependency-boundary.md).
The EvenHub main controller is closed as five functions / 3,130 body bytes /
3,450 physical bytes. One source-order event routine was restored beyond
Ghidra. Its utility graph reuses admitted EasyLogger, LVGL, CMSIS-FreeRTOS,
nanopb, and TLSF-backed wrappers plus bounded runtime and first-party services;
there is no embedded dependency or new version discriminator. See
[`g2-evenhub-main-dependency-boundary.md`](g2-evenhub-main-dependency-boundary.md).
The translate controller is closed as eleven functions / 2,504 body bytes /
2,862 physical bytes. Two handlers were restored beyond Ghidra; all external
edges terminate at admitted EasyLogger, LVGL, CMSIS-FreeRTOS, and nanopb,
bounded runtime, or first-party translate providers. See
[`g2-translate-dependency-boundary.md`](g2-translate-dependency-boundary.md).
The adjacent translate UI object is closed as 29 functions / 5,288 body bytes /
5,730 physical bytes, including 22 restored bodies and 13 stored entries. Its
provider graph terminates at selected EasyLogger and LVGL, bounded first-party
services, and the source-admitted IAR float-exponent trio; it adds no new
opaque utility. See
[`g2-translate-ui-dependency-boundary.md`](g2-translate-ui-dependency-boundary.md).
The teleprompt controller is closed as ten functions / 2,408 body bytes /
3,900 physical bytes. Two event handlers were restored beyond Ghidra; all
external edges terminate at the same admitted utilities or bounded teleprompt
providers. See
[`g2-teleprompt-controller-dependency-boundary.md`](g2-teleprompt-controller-dependency-boundary.md).
Conversate common data is closed as twelve functions / 2,208 body bytes /
2,560 physical bytes. Its only reusable providers are admitted EasyLogger and
LVGL text measurement plus bounded IAR memory primitives. See
[`g2-conversate-comm-data-dependency-boundary.md`](g2-conversate-comm-data-dependency-boundary.md).
The main conversate controller is closed as twelve functions / 2,250 body
bytes / 2,628 physical bytes. Its vector-referenced fatal entry corroborates
the already bounded CmBacktrace provider and selected compatibility commit
`73714489`; all other reusable edges terminate at admitted providers, with no
new version discriminator. See
[`g2-conversate-controller-dependency-boundary.md`](g2-conversate-controller-dependency-boundary.md).
The EvenHub common image container is closed as three functions / 1,554 body
bytes / 1,834 physical bytes. Its reusable graph terminates at selected
EasyLogger/LVGL, production TLSF-backed free and Apollo510 cache-clean leaves,
one bounded absolute-value helper, and first-party image policy. See
[`g2-common-image-container-dependency-boundary.md`](g2-common-image-container-dependency-boundary.md).
Dashboard watchface layout 2 is closed as nineteen functions / 2,844 body
bytes / 3,076 physical bytes. Its reusable calls terminate at the same selected
EasyLogger, LVGL, mpaland printf, bounded IAR, and first-party providers as the
adjacent layout family. See
[`g2-dashboard-watchface-layout2-recovery.md`](g2-dashboard-watchface-layout2-recovery.md).
With the final campaign the formerly largest remaining surfaces — the broader
GUI modules including dashboard.c, terminal_ui.c, and setting.c — are closed
as well, and no retained-path target selection remains.

## Reproduction and guardrails

Run:

```sh
python3 openCFW/tools/analyze_g2_first_party_frontier.py
python3 -m unittest openCFW.tests.test_analyze_g2_first_party_frontier
```

The analyzer authenticates the official payload and the 64-shard corpus,
normalizes full and relative retained paths, scans two-column and multi-module
three-column `*-closure.tsv` records, and pins the 234-entry closed-manifest
ledger to SHA-256
`aa5eb9142e1033f785771d6c81c5db41abf1d31ef5bb446b0354dca55553efd2`.
It emits all 234 paths in its JSON inventory, so a path cannot disappear,
change status, or silently cross-share a function between open and closed
sets.
