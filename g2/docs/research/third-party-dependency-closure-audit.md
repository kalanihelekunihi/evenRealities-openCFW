# G2 third-party dependency closure audit

## Outcome

The current Apollo-main third-party ledger contains 26 dependency families.
Every family has an identified origin and version or defensible compatibility
interval, an explicit selected source commit where a redistribution-safe
baseline exists, and at least one fail-closed evidence record. There are **zero
remaining bounded third-party executable functions that are both behaviorally
opaque and locally actionable**.

This does not mean all retained third-party bytes have been replaced. The
origin-aware ledger still counts 130,000 opaque-base bytes inside retained
third-party-path function envelopes. Those bytes include authenticated
upstream/compatible algorithms retained for compatibility, qualified
production-excluded candidates, and hardware-facing code whose admission is
gated. “Opaque in the emitted image” is therefore not equivalent to “unknown
functionality.”

## Machine-readable disposition

The authoritative ledger is
`tools/manifests/g2-third-party-dependency-closure.json`. It records, per
family:

- origin and recovered version/interval;
- the selected OpenCFW source commit or `null` when no defensible public pin
  exists;
- the historical G2 producing commit separately;
- functional status; and
- the exact external, hardware, proprietary-input, or admission gate that
  remains.

Across the 26 families, 25 have a selected public source commit or
compatibility baseline. IAR DLIB is the sole exception: all ten bounded linked
runtime units are already source-recreated, but a release-matched proprietary
archive is unavailable. The 26th family, DaveGamble cJSON, is now admitted as
an authenticated snapshot: the parser shared by service_android_notify.c and
service_whitelist.c is identified to version interval v1.7.9--v1.7.12 from four
binary discriminators, and a pristine MIT three-file snapshot selects the
interval-ceiling tag v1.7.12 (`3c8935676a97c7c97bf006db8312875b4f292f6c`) as
the reproducible OpenCFW baseline. All 21 linked parse-side functions were
re-verified byte-identical C text across the interval during admission; the
whole-file tag diff is confined to dead-stripped print/create/edit/utils code.
The snapshot is **production-excluded by explicit decision**: its
21 functions / 2,572 body bytes at
`[0x004D798C,0x004D83D8)` remain cut-forward pending a compiler/ABI readiness
matrix and a reviewed production-overlay admission decision. See
[`g2-json-parser-source-candidate-audit.md`](g2-json-parser-source-candidate-audit.md)
and [`third_party/cJSON/README.openCFW.md`](../../third_party/cJSON/README.openCFW.md).
No exact historical *producing* commit is asserted.
That is deliberate: source-identical commit intervals, mixed vendor trees, and
private patches make those historical object identities unobservable from the
linked binary. The selected source commit is the reproducible OpenCFW baseline,
not a rewritten claim about Even's private checkout.

The Apollo510 HAL row now has a stronger version boundary. The complete stock
system-sleep provider contains two `WFI` operations and the internal-timer
wake/re-entry path: official SDK 5.0.0 commit `392042e3…` has only one, while
SDK 5.1.0 public replay `5efc0228…` has two. The firmware build predates that
public import, so this proves 5.1.0 lineage while also proving that the public
commit itself was not the private generating checkout. The associated product
RTOS object, CMSIS current-thread calls, watchdog restart, and application
hooks are closed in
[`g2-product-rtos-recovery.md`](g2-product-rtos-recovery.md).

The latest census correction adds a copied Goodix utility hidden under the
first-party path `utils\assert\util_error_check.c`. Its 43-row error table,
512-byte automatic buffer, strings, and control flow select the byte-exact
GR551x SDK 1.7.0 `app_error.c` snapshot and exclude V1.00 and 2.0.1+. The
selected commit is the earliest located public carrier of the exact blob, not
an official Goodix release commit or Even's generating checkout. This is a
copied diagnostic helper, not evidence of a linked Goodix BLE stack. See
[`g2-util-error-check-goodix-recovery.md`](g2-util-error-check-goodix-recovery.md).
The complete SDK 1.7.0 C/header sweep finds only three other multi-string
collisions: the already identified CmBacktrace ancestry and nanopb 0.4.2
decoder/encoder diagnostics. Stock's modern CmBacktrace identity and nanopb
0.4.7 `pb_read` lower bound exclude those exact SDK files, so the sweep adds no
second hidden family.

The subsequent full recovery of the deceptively small retained
`app\gui\logger\logger_setting.c` anchor is another negative dependency
cross-check. Five functions missed by baseline Ghidra expand the object to
eight functions / 5,574 body bytes, but all 338 external calls terminate at
the already admitted EasyLogger, nanopb, littlefs-backed file, FreeRTOS, IAR
DLIB, and first-party message seams. No upstream definition is embedded, and
the object adds neither a dependency family nor a version discriminator. See
[`g2-logger-setting-recovery.md`](g2-logger-setting-recovery.md).

The following `app\ux\ux_system\ux_system.c` closure supplies the same kind
of negative cross-check. Its single 88-byte anchor expands to eleven functions
and a stored 2,232-byte system-status callback, but 95 of 147 external calls
are diagnostics at the admitted EasyLogger seam and the other 52 are bounded
G2 providers. It has no direct CMSIS-FreeRTOS, Cordio, nanopb, littlefs, DLIB,
or other utility edge and embeds no upstream definition. See
[`g2-ux-system-recovery.md`](g2-ux-system-recovery.md).

The next `app\gui\health\health.c` closure explicitly exercises the RTOS seam:
its lazy create, forever-acquire, and release calls land on the already
source-owned CMSIS-FreeRTOS v10.5.1 wrappers at exact commit `d213f261…`.
EasyLogger supplies diagnostics, while the health protobuf and role/display
calls stop at first-party providers. The four-function object embeds no
upstream definition and adds no version discriminator. See
[`g2-health-recovery.md`](g2-health-recovery.md).

The adjacent quicklist object repeats the same exact CMSIS-FreeRTOS mutex trio
and adds only EasyLogger diagnostics plus first-party quicklist providers. Its
four functions embed no upstream implementation and add no version evidence.
See [`g2-quicklist-recovery.md`](g2-quicklist-recovery.md).

The subsequent dashboard watchface-manager object provides a distinct
indirect-dispatch cross-check. Its 30 utility calls terminate at the admitted
EasyLogger 2.2.99-equivalent seam, its one other direct external call is a
bounded first-party state getter, and all 15 register-indirect calls resolve
through four authenticated first-party watchface operation tables. It embeds
no upstream definition and adds no dependency or version evidence. See
[`g2-dashboard-watchface-manager-recovery.md`](g2-dashboard-watchface-manager-recovery.md).

The EvenAI text-stream service exercises six admitted utility seams in one
object without exposing another implementation gap. Its 113 direct external
calls terminate at exact CMSIS-FreeRTOS v10.5.1 timer/mutex wrappers, the
LVGL 9.3-compatible interval, nanopb's admitted input-stream helper, TLSF
through synchronized G2 wrappers, EasyLogger, and bounded IAR DLIB routines.
The recovered UTF-8 timer callback and animation-preset policy are first-party.
See [`g2-text-stream-service-recovery.md`](g2-text-stream-service-recovery.md).

The terminal core repeats the exact CMSIS-FreeRTOS v10.5.1 mutex trio and
EasyLogger seam, with three bounded IAR memory calls. Its remaining providers
are first-party terminal protobuf/UI routers; the object has no direct nanopb
or LVGL definition and supplies no new version evidence. See
[`g2-terminal-core-recovery.md`](g2-terminal-core-recovery.md).

The RTC-driver closure converts a previously generic Ambiq boundary into two
exact source identities. Stock `0x004D3CF8` is
`utils/am_util_time.c::am_util_time_computeDayofWeek`, including the distinctive
month-offset table and shipped `% 400 != 0` leap predicate; `0x004D3ADC` is
`am_hal_rtc.c::am_hal_rtc_time_set`. Both are selected from the 5.1.0 public
replay `5efc022…`, and OpenCFW already source-owns their combined behavior in
the production `open_cfw_rtc_time_set` replacement. Their executable logic is
also present in public 5.0.0, so they corroborate identity but do not replace
the independent two-WFI 5.1.0 discriminator. See
[`g2-drv-rtc-recovery.md`](g2-drv-rtc-recovery.md).

The teleprompt file-list object is a negative provider cross-check. Its three
functions only copy, return, or zero a `0xF52`-byte first-party record. Ten
calls reach admitted EasyLogger and two reach bounded/source-recreated IAR
memory primitives. Nanopb decoding remains in the caller object, so no hidden
schema/runtime definition or new version evidence appears. See
[`g2-teleprompt-file-list-recovery.md`](g2-teleprompt-file-list-recovery.md).

The EvenAI timer object resolves a potentially misleading RTOS seam. Its 13
functions implement two private tick/deadline state machines, not CMSIS or
FreeRTOS software timers. Four calls terminate at the exact source-owned
CMSIS-FreeRTOS v10.5.1 `osKernelGetTickCount` wrapper, 30 at admitted
EasyLogger, and one at bounded IAR `memset`; the remaining ten calls are
first-party EvenAI policy. No opaque upstream timer definition or new version
discriminator remains. See
[`g2-even-ai-timer-recovery.md`](g2-even-ai-timer-recovery.md).

The BLE-status callback facade adds another negative utility check. Ten calls
reach admitted EasyLogger and three reach the private generic callback manager
for registration, removal, and dispatch. It has no direct CMSIS-FreeRTOS,
Cordio, IAR, allocator, or protobuf edge and embeds no upstream definition.
See [`g2-cb-ble-status-recovery.md`](g2-cb-ble-status-recovery.md).

The Conversate menu page closes 101 external calls as 35 admitted EasyLogger,
34 selected LVGL 9.3-compatible primitives, and 32 first-party page/animation
providers. Its five stored callbacks are all local page functions; no hidden
upstream definition or new commit discriminator appears. See
[`g2-conversate-ui-menu-page-recovery.md`](g2-conversate-ui-menu-page-recovery.md).

The Conversate tag page independently closes 202 external calls as 40 admitted
EasyLogger, 113 selected LVGL primitives, two exact source-owned
CMSIS-FreeRTOS `osKernelGetTickCount` calls, four bounded IAR DLIB operations,
and 43 first-party UI-policy calls. It embeds no upstream definition and adds
no version discriminator. See
[`g2-conversate-ui-tag-page-recovery.md`](g2-conversate-ui-tag-page-recovery.md).

The exit-prompt object closes 53 external calls as 35 admitted EasyLogger,
15 selected LVGL 9.3-compatible animation/object primitives, and three
first-party fade-animation calls. It has no RTOS, allocator, nanopb, IAR, or
embedded upstream definition and adds no version discriminator. See
[`g2-exit-prompt-recovery.md`](g2-exit-prompt-recovery.md).

The eAT core closes 20 direct external calls as 10 admitted EasyLogger, six
bounded/source-owned IAR DLIB operations, and four private parser calls. Exact
`AT_CoreInit` / `AT_Handler` fingerprint searches found no indexed public
source, so eAT is not promoted to a third-party dependency. See
[`g2-at-core-recovery.md`](g2-at-core-recovery.md).

The HAL I2C wrapper maps 21 calls to the Apollo510 GPIO/IOM API family in the
authenticated AmbiqSuite 5.1.0 replay at `5efc0228…`, plus 15 exact
CMSIS-FreeRTOS wrappers and admitted EasyLogger/nanopb/IAR seams. This closes a
real dependency shortcut without claiming the later public import was the
private generating commit. See
[`g2-hal-i2c-recovery.md`](g2-hal-i2c-recovery.md).

The ring-battery service closes another small first-party boundary. Its 15
logging calls reach the admitted EasyLogger core, two clears are bounded IAR
DLIB `memset`, and the remaining two calls are private G2 record transport.
Exact public symbol/path searches returned no source, and no new dependency or
version discriminator appears. See
[`g2-service-ring-battery-recovery.md`](g2-service-ring-battery-recovery.md).

The nominally first-party OPT3007 register initializer has a precise external
data origin rather than a hidden code origin: its 19 reconstructed field
triples exactly match Texas Instruments datasheet SBOS864 (August 2017). Exact
symbol/source searches found no public implementation, and its only calls are
admitted EasyLogger. See
[`g2-opt3007-registers-recovery.md`](g2-opt3007-registers-recovery.md).

The codec UART-porting seam confirms one already identified source shortcut:
its receive buffer calls the exact production-source-owned AndersKaloer
`ring_buffer_init`, compatible from `cda00e1…` through selected `190e30b…`.
The other 23 calls are admitted EasyLogger or first-party UART service, so no
codec-vendor body is hidden here. See
[`g2-service-codec-porting-recovery.md`](g2-service-codec-porting-recovery.md).

The notification-thread object composes seven exact CMSIS-FreeRTOS v10.5.1
wrappers—thread creation, flags set/wait, delay, and queue new/get/delete—at
selected commit `d213f261…`. The wrappers and their kernel chains are already
production source-owned; no new RTOS gap or discriminator appears. See
[`g2-thread-notification-recovery.md`](g2-thread-notification-recovery.md).

The GX8002B host-driver object adds three linked CMSIS-Core NVIC helper bodies
and 13 calls to 12 Apollo510 I2S HAL APIs. The latter match AmbiqSuite 5.1.0
`am_hal_i2s.c`, file revision `release_sdk5p1p0-366b80e084`, at selected public
replay `5efc0228…`. NationalChip's LVP SDK is not linked into the object, so it
is recorded as unavailable external device firmware/tooling rather than a new
Apollo-main software family. See
[`g2-drv-gx8002b-recovery.md`](g2-drv-gx8002b-recovery.md).

The production PDM wrapper independently reinforces that Apollo510 selection.
Its 13 direct HAL calls cover 12 functions in public `am_hal_pdm.c` at replay
`5efc0228…` (Git blob `23a440bf…`), while its only embedded third-party bodies
are three admitted CMSIS-Core NVIC helpers. The stock image predates the public
import, so the private generating commit remains unrecoverable; no additional
dependency family is introduced. See
[`g2-drv-pdm-production-recovery.md`](g2-drv-pdm-production-recovery.md).
The generic PDM object then adds `am_hal_pdm_interrupt_service` and
`am_hal_pdm_interrupt_status_get`, bringing the independently exercised source
surface to 14 APIs and proving the IRQ handler through the startup vector. See
[`g2-drv-pdm-recovery.md`](g2-drv-pdm-recovery.md).

The complete ANCC-facing service closure establishes a negative dependency result:
all 129 external calls from the 12-function object terminate at
admitted EasyLogger, CMSIS-FreeRTOS, bounded IAR, or closed G2 providers. It
contains no Ambiq ANCC implementation body, so the admitted profile snapshot
remains the complete reusable-code boundary. See
[`g2-service-ancc-dependency-boundary.md`](g2-service-ancc-dependency-boundary.md).

The next ALS scope similarly composes an already understood specification
boundary. Its complete 38-function object makes six calls to the private G2
OPT3007 field/register adapter, including the fully recovered 19-triple TI
SBOS864 register map, plus admitted EasyLogger, exact CMSIS-FreeRTOS delay,
bounded IAR, and closed first-party edges. There is no public OPT3007 software
checkout or additional dependency commit to recover. See
[`g2-als-dependency-boundary.md`](g2-als-dependency-boundary.md).

The complete BLE production-thread scope adds a dense RTOS consumer check:
fifteen exact CMSIS-FreeRTOS v10.5.1 calls exercise thread creation/termination,
flags, delay, queues, and memory pools, while three assertion calls reach the
exact admitted FreeRTOS `ulSetInterruptMask` port leaf. Its 14 functions,
stored task entry, static attributes, and whole-image ingress are pinned. No
Cordio body is embedded and no new Cordio version discriminator appears. See
[`g2-thread-ble-production-dependency-boundary.md`](g2-thread-ble-production-dependency-boundary.md).

The complete product-test protocol processor provides the largest consumer
cross-check added in this pass. Its 73 functions contain 1,526 external direct
calls: 1,280 EasyLogger calls, seven exact CMSIS-FreeRTOS v10.5.1 calls, one
exact FreeRTOS `xTaskGetTickCount` call, one mpaland printf call, 41 bounded
IAR/runtime/fail-stop calls, and 196 first-party calls. One hidden handler and
the 66-entry stored Thumb dispatch table close all entry paths. No reusable
body, additional dependency family, or version discriminator is embedded. See
[`g2-pt-protocol-procsr-dependency-boundary.md`](g2-pt-protocol-procsr-dependency-boundary.md).

The quicklist UI page closes another dense consumer: 415 LVGL, 465
EasyLogger, five exact CMSIS-FreeRTOS tick, 24 bounded IAR runtime, and 81
first-party calls. Seventeen restored functions and fifteen stored callbacks
complete the 80-function object; no reusable implementation or new version
discriminator is embedded. See
[`g2-ui-quicklist-page-dependency-boundary.md`](g2-ui-quicklist-page-dependency-boundary.md).

The dashboard news page closes 508 LVGL, 565 EasyLogger, eight exact
CMSIS-FreeRTOS mutex, 36 bounded runtime, and 79 first-party calls. Its 45
functions include fourteen restored helpers and twelve stored callbacks; no
reusable body or new version discriminator is embedded. See
[`g2-ui-widget-news-page-dependency-boundary.md`](g2-ui-widget-news-page-dependency-boundary.md).

The FlashDB service-adapter closure provides a direct consumer-side
cross-check of the pinned database and RTOS sources. Its two KVDB calls are
exact `fdb_kv_get_blob` / `fdb_kv_set_blob` from FlashDB 2.1.1 commit
`714d6159…`, and its seven synchronization/tick calls terminate at exact
CMSIS-FreeRTOS v10.5.1 wrappers from `d213f261…`. The object contains zero
third-party definitions. It also proves that the unsafe zero-on-driver-failure
behavior belongs to Even's FAL adapter, not to upstream FlashDB. See
[`g2-service-db-api-recovery.md`](g2-service-db-api-recovery.md).

The 43-function EvenAI UI object supplies a broader LVGL consumer cross-check:
182 calls terminate at 44 admitted LVGL object/style/label/image/bar/scroll/
event/animation targets, one call reaches exact CMSIS-FreeRTOS tick access,
and the object embeds zero third-party definitions. Its text-stream and timer
providers compose earlier closed first-party objects. See
[`g2-ui-even-ai-recovery.md`](g2-ui-even-ai-recovery.md).

The time-service object provides a useful negative RTOS boundary check. Its
eight reusable calls terminate at bounded IAR DLIB copy/set helpers, while all
other external edges are first-party time, RTC, transport, logging, or
configuration providers. It makes zero direct CMSIS-FreeRTOS calls and embeds
zero third-party definitions; the two-byte alignment gap after the closed
CMSIS object therefore remains a sharp ownership boundary. See
[`g2-service-time-recovery.md`](g2-service-time-recovery.md).

The 31-function audio-thread object is a broad consumer-side confirmation of
the admitted RTOS and codec stack. Twenty calls terminate at fourteen exact
CMSIS-FreeRTOS v10.5.1 wrappers, one at bounded IAR `memset`, and nineteen at
already closed codec DFU, codec-host, and GX8002B providers. It embeds no
third-party definition and links no NationalChip LVP code. See
[`g2-thread-audio-recovery.md`](g2-thread-audio-recovery.md).

The compact-log core supplies a provenance correction rather than a new
dependency family. Its private compact-output entry at `0x0043CE9E` and
private record encoder are first-party G2 code; the upstream-derived
EasyLogger `elog_output` is the separately authenticated body at `0x0043D574`.
The core makes 30 calls to EasyLogger controls/output, 14 to FreeRTOS
kernel/port seams, two to the exact CMSIS-FreeRTOS tick wrapper, and 13 to
bounded IAR DLIB primitives, while embedding zero third-party definitions.
See [`g2-compress-log-core-recovery.md`](g2-compress-log-core-recovery.md).

The companion port completes the transitive storage check. Eighteen calls
reach production source-owned shared-file wrappers over littlefs
v2.10.1-equivalent commit `0494ce71…`; three reach production source-owned
delayed-callback wrappers; and two bounded calls reach IAR `snprintf`. The
five-file rotation and 12-byte manager record are private G2 policy, with no
littlefs or other third-party definition embedded. See
[`g2-compress-log-port-recovery.md`](g2-compress-log-port-recovery.md).

The retained shared file-runtime object is now closed independently as eighteen
functions, all eighteen already production source-owned. Its provider graph
contains 36 exact CMSIS-FreeRTOS mutex calls, fourteen first-party backend
adapter calls over littlefs, three exact TLSF allocation-family calls, six
bounded IAR string calls, and no embedded third-party definition. This turns a
previously implementation-only shortcut into a fail-closed dependency
guarantee. See [`g2-file-runtime-recovery.md`](g2-file-runtime-recovery.md).

The adjacent `service_algo.c` object supplies another negative DSP-boundary
result. Its ten first-party functions call bounded IAR `memset`, `asin`,
signed-64-to-double, and `sqrt` bodies and a source-owned 64-bit division
helper; no NationalChip LVP or other reusable DSP definition is embedded. The
IAR body hashes are pinned as executable identities, while their archive
release remains binary-unobservable. See
[`g2-service-algo-recovery.md`](g2-service-algo-recovery.md).

The five-function UART-sync object closes the transport-side composition of
CMSIS-FreeRTOS, TinyFrame, EasyLogger, IAR DLIB, and the AmbiqSuite-backed UART
adapter. It embeds none of those implementations. TinyFrame remains pinned to
the `eb75483e…a29167a` core-identical interval; the lower UART adapter is
first-party code against the AmbiqSuite SDK 5.1.0 compatibility source
`5efc0228…`, not proof of a private historical checkout. One call through RAM
slot `0x20000658` is bounded as first-party initialization policy. See
[`g2-uart-sync-recovery.md`](g2-uart-sync-recovery.md).

The factory NV service is now closed by composing the existing authenticated
FlashDB 2.1.1 configuration result rather than duplicating it. Four calls reach
the selected `714d6159…` KVDB core, nine reach first-party database adapters,
and no FlashDB definition is embedded. The path owns the nine-node
`factory@NVdb` table and magic policy: missing or mismatched `0x55550022`
performs wholesale `fdb_kv_set_default`. The stock zero-on-driver-failure FAL
hazard remains a production gate. See
[`g2-service-nvdb-recovery.md`](g2-service-nvdb-recovery.md).

The production microphone test object supplies a second negative DSP boundary.
Its restored stereo callback plus five visible codec/PDM lifecycle functions
make five bounded IAR memory calls and 24 calls to first-party audio providers.
There are no direct CMSIS-FreeRTOS calls, no NationalChip LVP code, and no
embedded reusable definition. See
[`g2-production-mic-recovery.md`](g2-production-mic-recovery.md).

The audio-manager object extends that negative result through the shared-device
ownership layer. Seven functions, including two restored complete bodies,
contain no CMSIS-FreeRTOS or DSP implementation. Eighty calls terminate at the
admitted logging seams and one at bounded IAR `memset`; product-role, audio
power, and common-data frame `0x010C` calls are first-party providers. See
[`g2-service-audio-manager-recovery.md`](g2-service-audio-manager-recovery.md).

The system KVDB object closes the remaining locally recoverable FlashDB default
detail. Its exact 2.1.1 core calls still select commit `714d6159…`; the local
initializer proves the zero `kvbooCount` default, persisted increment lifecycle,
and eleven closed first-party record migrations. Golden-media, schema, and
non-destructive mount policy remain external or design gates, not an opaque
utility function. See
[`g2-service-kvdb-recovery.md`](g2-service-kvdb-recovery.md).

The battery-sync/callback chain provides a further negative utility closure.
`UX_BatterySyncHandler` dispatches record `0x105` through closed charger and
ring-battery services. The recovered ring, charge, and message callback
facades all terminate at the now-complete eight-function generic callback
manager. That manager's 72 external direct calls are 70 admitted EasyLogger
operations plus two production-source-owned synchronized TLSF wrappers; its
sole dynamic call is bounded to nodes created by registration. Across the five
new retained paths there is no direct CMSIS-FreeRTOS call, embedded third-party
definition, or new version discriminator. See
[`g2-ux-battery-sync-recovery.md`](g2-ux-battery-sync-recovery.md),
[`g2-cb-ring-battery-recovery.md`](g2-cb-ring-battery-recovery.md),
[`g2-callback-facades-recovery.md`](g2-callback-facades-recovery.md), and
[`g2-callback-manager-recovery.md`](g2-callback-manager-recovery.md).

The onboarding data-manager cross-check closes another first-party composition
seam rather than discovering a new library. All 52 external calls terminate at
admitted EasyLogger and CMSIS-FreeRTOS, bounded IAR `memset`, closed
FlashDB-backed KVDB and nanopb-backed protobuf objects, or private G2 policy.
The exact selected dependency commits are asserted by the focused analyzer; see
[`g2-onboarding-data-manager-recovery.md`](g2-onboarding-data-manager-recovery.md).

The adjacent controller strengthens that result across its full twelve-function
physical object. Its 253 external calls contain no new reusable definition:
EasyLogger, LVGL, CMSIS-FreeRTOS, IAR DLIB, and the closed first-party
onboarding/KVDB/protobuf/callback graph account for every edge. See
[`g2-onboarding-controller-recovery.md`](g2-onboarding-controller-recovery.md).

The onboarding main-page audit extends the same negative utility result over a
9,776-byte physical object with 52 functions. Its selected LVGL, EasyLogger,
CMSIS-FreeRTOS, mpaland, bounded IAR, and closed protobuf edges are all pinned;
no reusable definition or version discriminator remains hidden. See
[`g2-onboarding-main-page-recovery.md`](g2-onboarding-main-page-recovery.md).

## Aggregate cross-checks

The aggregate analyzer composes rather than replaces the focused audits:

| Cross-check | Result |
|---|---:|
| Dependency families | 26 |
| Retained third-party-path opaque lower bound | 130,000 bytes |
| Cordio reusable retained paths without focused classification | 0 |
| Copied Cordio GATT-profile functions now source-owned | 6 |
| Copied AmbiqSuite ANCC-profile stock functions source-derived | 12 / 21 |
| AmbiqSuite AMOTA-skeleton-derived OTA functions | 4 / 7 |
| Apollo510 stock / SDK 5.0.0 / SDK 5.1.0 system-sleep WFI count | 2 / 1 / 2 |
| Apollo510 exact private pre-release generating commit recoverable | no |
| GX8002B host-object CMSIS-Core linked definitions | 3 |
| GX8002B host-object AmbiqSuite I2S calls / APIs | 13 / 12 |
| NationalChip LVP code linked in GX8002B host object | no |
| FlashDB service-adapter FlashDB / CMSIS-FreeRTOS calls | 2 / 7 |
| FlashDB service-adapter embedded third-party definitions | 0 |
| FlashDB service-adapter zero-on-driver-failure seam present | yes |
| EvenAI UI LVGL / CMSIS-FreeRTOS calls | 182 / 1 |
| EvenAI UI embedded third-party definitions | 0 |
| Time-service IAR DLIB / direct CMSIS-FreeRTOS calls | 8 / 0 |
| Time-service embedded third-party definitions | 0 |
| Audio-thread CMSIS-FreeRTOS calls / wrappers | 20 / 14 |
| Audio-thread IAR DLIB / closed codec-GX8002B calls | 1 / 19 |
| Audio-thread embedded third-party definitions | 0 |
| NationalChip LVP code linked in audio thread | no |
| Compact-log IAR / EasyLogger / FreeRTOS / CMSIS calls | 13 / 30 / 14 / 2 |
| Compact-output entry `0x0043CE9E` is upstream EasyLogger | no |
| Compact-log embedded third-party definitions | 0 |
| Compact-log port source-owned file / delayed-callback calls | 18 / 3 |
| Compact-log port IAR DLIB calls / embedded third-party definitions | 2 / 0 |
| File-runtime CMSIS / littlefs-adapter / TLSF / IAR calls | 36 / 14 / 3 / 6 |
| File-runtime production source-owned functions | 18 / 18 |
| File-runtime embedded third-party definitions | 0 |
| Audio estimator IAR DLIB/math / source-owned division calls | 10 / 6 |
| NationalChip LVP or other DSP definitions in audio estimator | 0 |
| UART-sync CMSIS-FreeRTOS / TinyFrame-framework / UART-adapter calls | 8 / 4 / 5 |
| UART-sync bounded indirect initializers / embedded third-party definitions | 1 / 0 |
| Factory NV service FlashDB / G2 database-adapter / IAR calls | 4 / 9 / 2 |
| Factory NV service embedded third-party definitions | 0 |
| Factory magic mismatch resets all defaults / stock FAL zero-failure hazard | yes / yes |
| Production-mic IAR / first-party audio / direct CMSIS calls | 5 / 24 / 0 |
| Production-mic restored stereo callbacks / NationalChip definitions | 1 / 0 |
| Audio-manager IAR memset / direct CMSIS-FreeRTOS calls | 1 / 0 |
| Audio-manager first-party audio-power / common-data transport calls | 11 / 1 |
| Audio-manager restored functions / embedded third-party definitions | 2 / 0 |
| System-KVDB FlashDB / G2 database-adapter calls | 4 / 12 |
| System-KVDB closed migration targets / embedded third-party definitions | 11 / 0 |
| `kvbooCount` startup default / persisted lifecycle | 0 / resolved |
| UX battery-sync EasyLogger / direct CMSIS calls | 45 / 0 |
| Ring callback facade restored functions / embedded third-party definitions | 4 / 0 |
| Charge/message callback facades restored functions / embedded definitions | 6 / 0 |
| Generic callback manager EasyLogger / source-owned heap-wrapper calls | 70 / 2 |
| Generic callback manager bounded dynamic callback sites / embedded definitions | 1 / 0 |
| Silent-mode LVGL / EasyLogger / exact `vTaskDelay` calls | 70 / 70 / 1 |
| Silent-mode restored callbacks / embedded third-party definitions | 3 / 0 |
| Onboarding stock-page LVGL / EasyLogger calls | 447 / 110 |
| Onboarding stock-page CMSIS-FreeRTOS / IAR DLIB calls | 2 / 5 |
| Onboarding stock-page embedded third-party definitions | 0 |
| Onboarding news-page LVGL / EasyLogger calls | 232 / 160 |
| Onboarding news-page CMSIS-FreeRTOS / IAR DLIB calls | 16 / 15 |
| Onboarding news-page embedded third-party definitions | 0 |
| LVGL font-manager FreeType adapter calls / embedded definitions | 2 / 0 |
| LVGL font-manager exact FreeType source | 2.9.1 / `86bc8a950…` |
| EvenHub common-list LVGL / EasyLogger calls | 91 / 310 |
| EvenHub common-list bounded indirect targets / embedded definitions | 1 / 0 |
| EvenHub common-text LVGL / EasyLogger calls | 78 / 325 |
| EvenHub common-text bounded indirect targets / restored functions / embedded definitions | 1 / 3 / 0 |
| EvenHub UI EasyLogger / LVGL / nanopb calls | 690 / 37 / 7 |
| EvenHub UI bounded indirect targets / restored functions / embedded definitions | 3 / 16 / 0 |
| EvenHub data-parser nanopb / CMSIS-FreeRTOS / LVGL calls | 25 / 3 / 14 |
| EvenHub data-parser indirect calls / restored functions / embedded definitions | 0 / 2 / 0 |
| Sync framework CMSIS-FreeRTOS / FreeRTOS / TinyFrame calls | 35 / 4 / 26 |
| Sync framework AmbiqSuite / nanopb / EasyLogger calls | 2 / 1 / 825 |
| Sync framework indirect calls / restored functions / embedded definitions | 14 / 20 / 0 |
| Sync-interface API CMSIS-FreeRTOS / FreeRTOS-assert / EasyLogger calls | 17 / 9 / 255 |
| Sync-interface API indirect calls / embedded definitions | 0 / 0 |
| Display thread CMSIS-FreeRTOS / FreeRTOS / LVGL calls | 21 / 11 / 12 |
| Display thread restored / indirect / production-routed functions | 13 / 12 / 2 |
| Display thread embedded third-party definitions | 0 |
| MX25 driver AmbiqSuite / CMSIS-FreeRTOS calls | 31 / 5 |
| MX25 driver shared nanopb-initializer calls | 3 |
| MX25 driver restored / indirect / embedded definitions | 19 / 0 / 0 |
| Notification-list LVGL / CMSIS-FreeRTOS / TLSF-wrapper calls | 304 / 6 / 8 |
| Notification-list restored / indirect / embedded definitions | 13 / 0 / 0 |
| Dashboard main EasyLogger / LVGL / CMSIS-FreeRTOS calls | 255 / 146 / 2 |
| Dashboard main restored / interior callbacks / embedded definitions | 17 / 7 / 0 |
| Teleprompt UI EasyLogger / LVGL / IAR calls | 330 / 252 / 10 |
| Teleprompt UI restored / bounded indirect / embedded definitions | 38 / 1 / 0 |
| EM9305 DFU-service direct EM9305/Packetcraft calls | 0 |
| EM9305 DFU-service file/TLSF / shared-initializer calls | 18 / 1 |
| Conversate tag-data nanopb / JSON calls | 0 / 0 |
| Conversate tag-data EasyLogger / TLSF-wrapper / IAR calls | 140 / 8 / 7 |
| Goodix copied application-error source snapshot | GR551x SDK 1.7.0 / 43 rows |
| Goodix exact generating commit recoverable | no |
| Linked Goodix BLE stack proven | no |
| Logger-settings embedded third-party definitions | 0 |
| UX-system embedded third-party definitions | 0 |
| Health-object embedded third-party definitions | 0 |
| Quicklist-object embedded third-party definitions | 0 |
| Dashboard watchface-manager embedded third-party definitions | 0 |
| EvenAI text-stream-service embedded third-party definitions | 0 |
| Terminal-core embedded third-party definitions | 0 |
| RTC driver exact Ambiq utility/HAL source identities | 2 / 2 |
| RTC setter production source-routed | yes |
| Teleprompt file-list embedded third-party definitions | 0 |
| EvenAI timer embedded third-party definitions | 0 |
| BLE-status callback facade embedded third-party definitions | 0 |
| Conversate menu-page embedded third-party definitions | 0 |
| Legal/regulatory UI embedded third-party definitions | 0 |
| AmbiqSuite Cordio application-framework paths identified | 9 / 9 |
| Cordio application-framework anchored stock surface | 50 functions / 29,110 bytes |
| LVGL private display-port source-owned functions | 7 / 7 |
| LVGL private display-port stock surface | 638 / 638 bytes |
| Retained third-party Ambiq input-port paths | 0 |
| Conventional recoverable `FT_Done_FreeType` entry | no |
| Locally actionable bounded third-party functional gaps | **0** |

The FreeType negative result is important. The only direct reference to
`FT_Done_Memory` is `FT_Init_FreeType` failure cleanup, and neither the even
nor Thumb address is stored. A normal linked `FT_Done_FreeType` body cannot be
assigned without guessing, so it is not treated as an unfinished function.

The dashboard layout-4 cross-check now closes 23 functions and all 230 external
edges. It reuses the selected EasyLogger, LVGL, and AmbiqSuite Apollo510 source
commits, while the remaining IAR and G2 provider seams are bounded. The
corrected `0x005BBD48` callback boundary also removes a false indirect-call
artifact caused by decoding object data at `0x005BBD10` as Thumb code.

The adjacent dashboard extension cross-check closes sixteen functions and all
291 external edges. Its reusable boundaries are the selected EasyLogger,
littlefs, nanopb, and FreeRTOS sources. Ten recovered routines contain only G2
dashboard file-transfer, schema, and resource policy and add no new dependency
or commit discriminator.

The dashboard data-process cross-check closes fourteen functions and all 255
external edges. It reuses the selected EasyLogger, nanopb, CMSIS-FreeRTOS, and
FreeRTOS source commits; the remaining IAR and first-party provider seams are
bounded. No embedded third-party definition or new discriminator appears.

The display-driver manager cross-check closes nineteen functions and all 178
external edges. Its only direct reusable sources are selected EasyLogger and
CMSIS-FreeRTOS; the ULED/MSPI and LVGL-port calls terminate at first-party
providers. Zero direct LVGL or AmbiqSuite edge is present, so the object adds
no vendor-version discriminator.

The nPMX main-driver cross-check closes thirty wrapper functions and all 403
external edges, including 72 calls to 42 linked Nordic nPMX entries. Its paired
ADC and floating-point fingerprints uniquely select public commit
`e1aaec53…` and exclude its adjacent successor `53de7af4…`. The compact driver
snapshot is admitted; PMIC production routing remains gated on the nPM1300 ADK
and configuration, Apollo510 I2C/interrupt integration, G2 power policy, and
hardware validation.

The LC3 source cross-check adds the dependency family exposed by the adjacent
audio object. Four public entries receive five direct calls; `lc3_encode`
retains its complete 18-direct-call algorithm graph and one bounded format
loader. Stock's SNS `FLT_MAX` constant proves `bb85f7d…` or later, while the
encoder's byte-0/1/2 `dt`/`sr`/`sr_pcm` layout excludes `9f1e206…` and later.
The complete 38-file Google liblc3 v1.1.3 tree at `96a3af0…` is admitted as the
tagged compatibility baseline. A spelling-only change to a dead-stripped API
prevents recovery of one exact public/private producing checkout.

The completed `service_audio.c` consumer cross-check then closes fourteen
functions and all 104 external direct calls. Five edges terminate at the
admitted liblc3 baseline; EasyLogger, CMSIS-FreeRTOS, IAR, littlefs/file
runtime, and the closed `service_algo.c` account for every other reusable
provider. Its sole indirect call resolves to the two authenticated
production-microphone callbacks selected by three static registration sites.
No embedded codec or other reusable definition remains in the first-party
adapter.

The dashboard stock-page cross-check closes 34 functions and all 852 external
direct calls. Its reusable providers are 454 selected LVGL calls, 355 admitted
EasyLogger calls, and ten bounded IAR runtime calls; the remaining 33 calls are
first-party seams. It has zero CMSIS-FreeRTOS/FreeRTOS calls, no indirect call,
no embedded third-party definition, and no new version or producing-commit
discriminator. See
[`g2-ui-stock-page-dependency-boundary.md`](g2-ui-stock-page-dependency-boundary.md).

The complete navigation UI cross-check closes 61 functions and all 2,237
external calls. It reuses selected LVGL, EasyLogger, CMSIS-FreeRTOS, nanopb,
and mpaland printf sources, plus bounded IAR and first-party policy seams.
Fourteen stored function starts and five shared-tail callback pointers close
ingress; no indirect call or embedded reusable definition remains, and no new
version or producing-commit discriminator appears. See
[`g2-navigation-ui-dependency-boundary.md`](g2-navigation-ui-dependency-boundary.md).

The menu-page cross-check closes 34 functions and all 746 external calls. It
reuses selected LVGL, EasyLogger, CMSIS-FreeRTOS, and nanopb sources, plus
bounded IAR and first-party providers. Eight stored function starts and one
shared interior entry close ingress; no embedded dependency or new version or
producing-commit discriminator appears. See
[`g2-menu-page-dependency-boundary.md`](g2-menu-page-dependency-boundary.md).

The health-page cross-check closes twelve functions and 666 external calls.
It reuses selected LVGL, EasyLogger, and mpaland printf sources plus bounded
IAR and first-party providers; it has zero direct CMSIS-FreeRTOS calls, no
embedded reusable body, and no new commit discriminator. See
[`g2-ui-health-page-dependency-boundary.md`](g2-ui-health-page-dependency-boundary.md).

The Ring-service cross-check closes eighteen functions and 121 external calls.
It reuses admitted EasyLogger, CMSIS-FreeRTOS, and nanopb sources or bounded
IAR/first-party providers, with zero direct Cordio calls. No vendor body or
discriminator appears.

The dashboard watchface layout-1 cross-check closes nineteen functions, all
215 external direct calls, and both indirect sites. It reuses selected LVGL,
EasyLogger, and mpaland printf sources plus bounded IAR and first-party
providers. Two PC-relative constants bind the indirect calls to recovered
local callbacks; no reusable definition or producing-commit discriminator
appears.

The teleprompt-FSM cross-check closes fifteen functions, all 172 external
direct calls, and its nine-entry indirect handler table. It reuses admitted
EasyLogger, LVGL, and nanopb sources plus bounded runtime and first-party
providers. No reusable definition or producing-commit discriminator appears.

The health-data-manager cross-check closes ten functions and all 136 external
calls. It reuses admitted EasyLogger and bounded runtime or terminates at the
closed health mutex wrappers over exact CMSIS-FreeRTOS. No reusable health/DSP
definition or producing-commit discriminator appears.

The input-manager cross-check closes ten functions and 103 external calls.
It reuses admitted EasyLogger, CMSIS-FreeRTOS, and nanopb, plus bounded
memory/runtime and first-party providers. It calls neither LVGL nor Cordio and
embeds no reusable body or new version/commit discriminator.

The calendar-page cross-check closes fifteen functions and 722 external calls.
It reuses admitted LVGL, EasyLogger, and CMSIS-FreeRTOS plus bounded IAR and
first-party providers. No reusable body or new version/commit discriminator
appears.

The OTA-transport cross-check closes three functions, 86 direct calls, and
four registered callback dispatches. Direct dependencies terminate at admitted
EasyLogger, bounded IAR memory, source-owned CRC/TLSF wrappers, or closed
first-party OTA providers. No reusable body or new discriminator appears.

The EFS-transport cross-check closes two functions, 87 direct calls, and four
registered callback dispatches. It adds one exact CMSIS-FreeRTOS v10.5.1 tick
edge and otherwise reuses the same admitted/source-owned provider classes as
OTA transport. No reusable body or new discriminator appears.

The EvenHub loading-page cross-check closes four functions and all 137
external calls. It reuses 36 selected LVGL and 85 admitted EasyLogger calls,
plus two bounded runtime and fourteen first-party calls. Two stored function
pointers close ingress; no embedded reusable definition or producing-commit
discriminator appears.

## What remains and why work stops at this boundary

The residual third-party work falls into four non-local or decision-gated
classes:

1. hardware evidence: Apollo scheduler/tickless timing, GPU/cache/display
   behavior, flash contents/mount policy, BLE controller interaction, and wire
   captures;
2. unavailable inputs: private Ambiq/Even commits, original IAR archives,
   external font/flash assets, and licensed modern Packetcraft/EM sources;
3. historical ambiguity: source-identical commits or mixed forks whose exact
   producing checkout cannot survive in the binary; and
4. material production choices: atomic admission of boot-critical FreeRTOS,
   Nema/GPU/HAL, nPMX, liblc3, EasyLogger, FlashDB, FreeType, cJSON, or Cordio candidates before
   device validation.

The qualified FreeRTOS scheduler, port-start, STIMER setup/IRQ/tickless, and
task-switch candidates illustrate the boundary. Their algorithms, fixed state,
call topology, objects, and host behavior are closed. Redirecting the live
boot-critical scheduler without the required device timing/sleep/preemption
validation would be a production decision, not additional reverse engineering.

The next useful locally actionable firmware frontier is therefore first-party
ownership recovery among the 675,636 bytes of unanchored discovered functions
and conservative refinement of the 2,157,676-byte mixed outside-envelope
bucket. That work is not another third-party dependency/version gap.

The current first-party frontier audit also closes `conversate.c`. Its only
notable utility edge is one vector-referenced call into the already classified
CmBacktrace fault provider. This confirms provider reuse but adds no version or
commit discriminator beyond the existing `4abadfa0…73714489` interval; the
selected `73714489` snapshot remains a compatibility choice.

## Reproduction

```sh
make third-party-dependency-closure
```

The target rebuilds and verifies the source package, authenticates the
64-shard Ghidra corpus, composes Cordio, LVGL-display, FreeType, and origin-byte
audits, validates every ledger evidence path, and runs mutation/contract tests.
It performs no signing, flashing, erase, or hardware operation.
