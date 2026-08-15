# R1 clean-room functional firmware

Status: active implementation goal; compatibility-core milestone complete.

## How this documentation is arranged

Four documents sit at the top of `r1/docs/` because they orient a reader: this
one, [`SECURITY.md`](SECURITY.md), [`PROVENANCE.md`](PROVENANCE.md), and
[`SOURCE-ADMISSION.md`](SOURCE-ADMISSION.md). Everything else is filed by kind:

| Directory | What it holds |
| --- | --- |
| [`correlation/`](correlation) | one record per subsystem, pinning recovered behavior to the stock image -- exact addresses, byte counts, record layouts, and how this implementation corresponds to them |
| [`boundaries/`](boundaries) | one record per licensed-provider seam -- what the R1-owned adapter implements, and what stays disabled until that provider is supplied |
| [`closures/`](closures) | Nordic SDK closure proofs |
| [`reference/`](reference) | function ownership, coverage, the capability ledger, the remaining frontier, the residual provider and production-readiness audit, and the BSim run summaries under `reference/bsim/` |

To understand what the firmware *does*, read `correlation/`. To understand what
it deliberately refuses to do without a licensed provider, read `boundaries/`.

## Reproducing any claim here

Each correlation document ends with the command that regenerates its numbers.
Those commands run in this repository:

```sh
make -C r1/research/decompilation/rebuild verify   # reconstruct the pinned images
python3 tools/summarize_r1_<subsystem>.py          # from the r1/ directory
make -C r1 verify                                  # the whole evidence gate at once
```

The reconstruction needs the vendor byte arrays, which are supplied locally --
see [`../research/decompilation/rebuild/PROVENANCE.md`](../research/decompilation/rebuild/PROVENANCE.md).
The firmware itself builds and passes its full test suite without them.

## Outcome

The source in [`..`](..) implements the observable R1 application contract. It
uses the recovered application/bootloader decompilation, executable Python models, first-party
controller models, capability ledger, and firmware security audit as specifications. Attributable
platform and library functionality comes from pinned vendor/upstream sources; clean-room C is
limited to R1-specific application behavior, configuration, ports, safety corrections, and
unattributable gaps. It does **not** emit the stock firmware image.

The host build remains an executable protocol/device simulator, and every core translation unit
compiles freestanding for Cortex-M4. A second target links an actual nRF52840 application from
Nordic nRF5 SDK 17.1.0 sources against the S140 7.2.0 ABI. It registers the recovered BAE8 service
and four characteristics through Nordic's service helper and connects channel 2 to the bounded EUS
runtime. Nordic Peer Manager, FDS, fstorage, connection-state, GATT-cache, ATT-MTU/data-length,
timer, and sorted-list providers are linked with the recovered parameters. The authenticated
upstream FreeRTOS-Kernel 10.5.1 core, Nordic SDK 17.1.0 nRF52 port, and Arm's authenticated
CMSIS-FreeRTOS v10.5.1 wrapper now own scheduling, queues, flags, semaphores, timers, and heap
behavior. Armink's authenticated
CmBacktrace 1.4.2-compatible source owns crash unwind and fault diagnosis. The recovered 16-byte
reset-trace record, capture policy, and fault-vector seam are implemented locally, while reset
mechanics remain Nordic/CMSIS-owned. Role-aware advertising control is now bound: the linked
application starts fast advertising while either the phone or glasses role is unoccupied and stops
when both are occupied, driven by runtime role assignment and disconnect; the glasses-role channel
parser remains deliberately unwired, so the both-occupied stop path awaits that binding. Product
identity authorization is resolved as a documented fail-closed policy: stock performs no
cryptographic product challenge, so `authorized` remains false and sensitive mutations stay
withheld until an evidence-backed product identity verifier is a deliberate product decision.
Remaining board pins,
optical/PMIC devices,
and boot/update integration remain HAL work. Official Bosch BMA456 SensorAPI v2.29.0 and
ST LIS2DW12 v2.1.0-compatible sources are pinned for the recovered motion variants; only their R1
configuration/bus/event adapters are implemented locally. The Nordic target now probes the exact
TWIM1 P0.11/P0.14 address-`0x18` bus in stock LIS2DW12-then-BMA456W order, applies the recovered
provider configuration, and retains a bounded normalized FIFO API. The target also compiles
Nordic's exact SPIM2 provider/IRQ path while leaving the proprietary sensor provider behind that
transport unbound. Its P0.15 interrupt worker,
higher-level consumer, NFC/TWIM1 coexistence, and owned-ring validation remain open. QST QMA6100
V1.0 lineage is proven for three provider bodies and ten R1 seams, but stays disabled until
licensed official source and installed-part evidence are available. The GoMore health-algorithm cluster is likewise
hard-gated pending an authenticated licensed SDK; see
[`GOMORE-PROVIDER-BOUNDARY.md`](boundaries/GOMORE-PROVIDER-BOUNDARY.md).
The IQS7211E path now uses pinned MIT provider/settings references, a compiled R1-only
configuration/lifecycle/recovery adapter, and Nordic's TWIM0/GPIOTE drivers for the recovered board
binding. It remains fail-closed pending the shared-power provider, device identity, and hardware
validation:
[`IQS7211E-PROVIDER-BOUNDARY.md`](boundaries/IQS7211E-PROVIDER-BOUNDARY.md).
The R1-owned ATI-error audit cadence and channel summary are separately reconstructed without bus
or logging code in
[`IQS7211E-ATI-AUDIT-CORRELATION.md`](correlation/IQS7211E-ATI-AUDIT-CORRELATION.md).
The separate R1-owned calibration, slider timing, gesture, and event-routing path is documented in
[`TOUCH-SLIDER-CORRELATION.md`](correlation/TOUCH-SLIDER-CORRELATION.md); it consumes normalized samples and
does not reproduce controller/register semantics.
GXCAS GXT310 and YHMICROS YHM2710 marker-bearing functions are provenance-pinned in
[`NAMED-PERIPHERAL-BOUNDARIES.md`](boundaries/NAMED-PERIPHERAL-BOUNDARIES.md).
The expanded Goodix provider/demo gate and clean-room R1 adapter split are documented in
[`GOODIX-PROVIDER-BOUNDARY.md`](boundaries/GOODIX-PROVIDER-BOUNDARY.md); the exact 58-function GH_NADT
provider closure is in
[`GOODIX-NADT-PROVIDER-BOUNDARY.md`](boundaries/GOODIX-NADT-PROVIDER-BOUNDARY.md), and the 31-function GH_HR
processing closure is in
[`GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md`](boundaries/GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md). The
9-function GH_HRV lifecycle closure is in
[`GOODIX-HRV-PROVIDER-BOUNDARY.md`](boundaries/GOODIX-HRV-PROVIDER-BOUNDARY.md). The
85-function GH_SPO2/dlCom processing, diagnostic, generated-model, recurrent-runtime, and dormant-graph boundary is in
[`GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md`](boundaries/GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md).
The recovered NFC driver now compiles and retains ST's pinned BSD-3-Clause ST25DVxxKC component.
Eleven local board/policy adapters supply the recovered TWIM1/GPO topology, exact session/GPO
orchestration, hardened 20-byte receive boundary, and bounded dock heartbeat/field-control
planner; see [`ST25DVXXKC-CORRELATION.md`](correlation/ST25DVXXKC-CORRELATION.md) and
[`NFC-DOCK-POLICY-CORRELATION.md`](correlation/NFC-DOCK-POLICY-CORRELATION.md).
Five additional byte-pinned R1 resource functions now own the P1.10 NFC board lifecycle,
exclusive shared-bus arbitration, and the three-client battery/optical/touch lease. All YHM
register and wire operations are reconstructed behind typed board callbacks; see
[`YHM2710-I2C5-RESOURCE-BOUNDARY.md`](boundaries/YHM2710-I2C5-RESOURCE-BOUNDARY.md).
The Nordic image also compiles the exact `nrfx_saadc` provider and recovered AIN5/AIN3/AIN2
configuration. Four R1 analog adapters and seven product battery routines supply only routes,
filtering, conversion, curves, and charge-state policy. The linked controller can synchronize
provider measurements into protocol-visible runtime state, while live sampling remains fail-closed
until the reconstructed YHM service is bound and validated on owned hardware; see
[`ANALOG-BATTERY-CORRELATION.md`](correlation/ANALOG-BATTERY-CORRELATION.md).
The R1-owned three-hour automatic health-history gate is also implemented as a portable controller
and retained Nordic integration seam. It reproduces the authenticated-phone condition, shared
query/sync timestamp, exact five-leg order, serial-zero output, cooldown boundary, and clock-rewind
recovery without admitting GoMore or Goodix code; see
[`AUTOMATIC-HEALTH-SYNC-CORRELATION.md`](correlation/AUTOMATIC-HEALTH-SYNC-CORRELATION.md).

## Evidence incorporated

The implementation is pinned to these repository-owned evidence sets:

- Raw application-to-reference similarity is treated only as a candidate ranking. Exact tiny-thunk
  false positives and the semantic admission rule are recorded in
  [`SOURCE-CORRELATION-REVIEW.md`](reference/SOURCE-CORRELATION-REVIEW.md).
- The recovered cross-peripheral name registry and nine operation/list functions remain an
  unidentified, non-reimplemented framework boundary; see
  [`GENERIC-DEVICE-REGISTRY-BOUNDARY.md`](boundaries/GENERIC-DEVICE-REGISTRY-BOUNDARY.md).
- The current 685-function / 36,288-byte unclassified frontier, plus nine separately blocked
  generic device-registry candidates, fourteen blocked time/calendar-provider candidates, forty
  software-TWI-provider candidates, seven RTC-device-provider candidates, and thirteen
  sensor-algorithm heap-provider candidates, plus four sensor-stream framework candidates, and
  the next evidence-ranked closure
  are recorded in
  [`REMAINING-FUNCTION-FRONTIER.md`](reference/REMAINING-FUNCTION-FRONTIER.md).
- The five-function 280...308-byte frontier is closed as four bounded R1 behaviors and one
  Goodix provider body. The local APIs add six-byte `pb_tran` framing, delayed-event admission,
  and health-settings transition planning; the BLE-thread body maps to the existing envelope
  encoder. See
  [`FRONTIER-280-308-CORRELATION.md`](correlation/FRONTIER-280-308-CORRELATION.md).
- The five-function 264...274-byte frontier plus one exclusive helper is closed as three bounded
  R1 behaviors and three GoMore provider bodies. The local APIs retain the existing five-byte EUS
  producer and add only battery diagnostic cadence and payload-redacting `ep.bin` cursor recovery.
  See [`FRONTIER-264-274-CORRELATION.md`](correlation/FRONTIER-264-274-CORRELATION.md).
- The five-function 256...262-byte inventory frontier (including one corrected 272-byte extent)
  plus eight exclusive helpers is closed as two R1 policies, one bounded R1/Goodix adapter, and
  ten GoMore provider bodies. See
  [`FRONTIER-256-262-CORRELATION.md`](correlation/FRONTIER-256-262-CORRELATION.md).
- The five-function 230...248-byte inventory frontier plus twelve supporting helpers is closed as
  eleven R1 product/data entries, three GoMore provider bodies, and three blocked shared-runtime
  entries. The local work reuses the bounded `kv.bin` store and adds only `ep.bin` readiness and
  legacy device-info formatting over caller-supplied data. See
  [`FRONTIER-230-248-CORRELATION.md`](correlation/FRONTIER-230-248-CORRELATION.md).
- The seven-function 212...222-byte inventory frontier is closed with three corrected executable
  extents: five bounded R1 product/provider seams, one Goodix provider body, and one blocked
  sensor-stream scheduler. See
  [`FRONTIER-212-222-CORRELATION.md`](correlation/FRONTIER-212-222-CORRELATION.md).
- The five-function / 1,030-byte 204...210-byte frontier is closed as four bounded R1
  policies/adapters and one blocked unattributed shared tensor-arena allocator. Nordic GAP and
  FAL/device access use their admitted provider APIs; the sensor-stream framework is not
  recreated. See
  [`FRONTIER-204-210-CORRELATION.md`](correlation/FRONTIER-204-210-CORRELATION.md).
- The 402-byte PMIC charge-event boundary is implemented as a pure status-template and thermal
  action planner in [`PMIC-CHARGE-EVENT-CORRELATION.md`](correlation/PMIC-CHARGE-EVENT-CORRELATION.md);
  ST25DVxxKC, timers/events, logging, and live transport retain their typed provider seams;
  the YHM2710 closure itself is reconstructed.
- The composite 374-byte PMIC-charged notification boundary is implemented as a pure retry and
  completion planner in
  [`PMIC-CHARGED-NOTIFICATION-CORRELATION.md`](correlation/PMIC-CHARGED-NOTIFICATION-CORRELATION.md);
  Nordic GPIO/CMSIS, ST25DVxxKC, delayed events, touch, and device-registry work remain external.
- The native 406-byte R1 battery runtime entry at `0x00031FD0` is reconciled with the previously
  accepted 412-byte veneer-plus-body extent in
  [`ANALOG-BATTERY-CORRELATION.md`](correlation/ANALOG-BATTERY-CORRELATION.md); the existing clean controller
  is reused and no provider dependency or duplicate algorithm body is introduced.
- The 406-byte GH_HR private-context initializer at `0x0006D204` is reconstructed as a typed,
  failure-clean constructor in
  [`GOODIX-PRIMITIVES-REDUCTION-CORRELATION.md`](correlation/GOODIX-PRIMITIVES-REDUCTION-CORRELATION.md);
  its two stock global owners and copied constructor table are explicit caller bindings.
- The 402-byte HRV FlashDB iterator callback is product-routed in
  [`HRV-FLASH-MERGE-CORRELATION.md`](correlation/HRV-FLASH-MERGE-CORRELATION.md), with only its bounded
  record/day/slot policy admitted and every storage, calendar, logging, transport, and biometric
  provider left external.
- The 380-byte HRV current-RAM merge is product-routed in
  [`HRV-RAM-CACHE-MERGE-CORRELATION.md`](correlation/HRV-RAM-CACHE-MERGE-CORRELATION.md); the clean-room API
  performs only day/timezone refresh, hourly window selection, acknowledgement clamping, and
  typed packet handoff, leaving HRV production and all provider implementations external.
- The twin 364-byte heart-rate and SpO2 current-RAM merges are product-routed in
  [`SCALAR-HEALTH-RAM-CACHE-MERGE-CORRELATION.md`](correlation/SCALAR-HEALTH-RAM-CACHE-MERGE-CORRELATION.md);
  one shared clean-room scalar API performs their hourly selection and packet handoff while both
  biometric producers and every service provider remain external.
- The two-function / 500-byte final phone-response and packet-constructor closure is product-routed in
  [`PROTOCOL-RESPONSE-CORRELATION.md`](correlation/PROTOCOL-RESPONSE-CORRELATION.md); its clean-room API reuses
  the bounded packet encoder, full-model CRC-16/MODBUS, and generated-serial policy, while
  injecting FreeRTOS allocation plus Nordic BLE transport as external seams.
- The 364-byte generic virtual-file export state machine is product-routed in
  [`EXPORT-STATE-MACHINE-CORRELATION.md`](correlation/EXPORT-STATE-MACHINE-CORRELATION.md); only its pure
  control/chunk planner is local, while the composite private-log reader and live sender remain
  excluded.
- The 376-byte firmware-event-loop timer callback is product-routed in
  [`DELAYED-EVENT-TIMER-CORRELATION.md`](correlation/DELAYED-EVENT-TIMER-CORRELATION.md); a pure 64-slot
  countdown/reschedule step exposes due events and both recovered sentinel quirks while CMSIS,
  FreeRTOS, queues, live timers, ticks, and logging remain provider-owned.
- The twin 394-byte heart-rate and SpO2 FlashDB iterator callbacks are product-routed in
  [`SCALAR-HEALTH-FLASH-MERGE-CORRELATION.md`](correlation/SCALAR-HEALTH-FLASH-MERGE-CORRELATION.md).
  Their shared normalized clean-room merge preserves the record/day/slot, first-record-wins, and
  monotonic cursor policy while FlashDB, calendar, logging, transport, and biometric providers
  remain external.
- The 382-byte HRV timed-window start controller is implemented as a pure plan in
  [`HRV-TIMING-START-CORRELATION.md`](correlation/HRV-TIMING-START-CORRELATION.md), including its 120-second
  one-shot delay, catch-up exclusion, stream-registration boundary, and rollback obligation;
  time, timers, sensor streams, logging, and biometric code remain provider-owned.
- The three-function / 550-byte target-glasses peer policy, three-slot lookup, sentinel handling,
  and recovered acceptance behavior are pinned in
  [`PEER-TARGET-POLICY-CORRELATION.md`](correlation/PEER-TARGET-POLICY-CORRELATION.md); Nordic peer data and
  all disconnect/advertising actions remain external.
- The 464-byte legacy command-frame dispatcher, its 36-byte workspace, opcode offset, all 23
  routes, unknown return, and special `0x88` pair-auth route are byte-pinned in
  [`LEGACY-COMMAND-DISPATCH-CORRELATION.md`](correlation/LEGACY-COMMAND-DISPATCH-CORRELATION.md). The local
  implementation is a bounded pure router; every destination handler retains its independent
  ownership and source-admission status.
- The symmetric 430-byte phone and glasses connection-role setters are implemented as a pure,
  fail-closed policy in
  [`CONNECTION-ROLE-ASSIGNMENT-CORRELATION.md`](correlation/CONNECTION-ROLE-ASSIGNMENT-CORRELATION.md);
  Nordic connection state and role-event delivery remain external.
- The four-function / 1,740-byte R1 nonvolatile-recovery closure, exact 116-byte body, fill-only
  merge rules, and withheld identity-bearing transport are documented in
  [`NV-RECOVERY-CORRELATION.md`](correlation/NV-RECOVERY-CORRELATION.md).
- The 494-byte R1 MAC-keyed compiled-default restore and its 59-record identity-table extent are
  pinned in [`NV-COMPILED-RESTORE-CORRELATION.md`](correlation/NV-COMPILED-RESTORE-CORRELATION.md); only an
  abstract deployer-owned policy is eligible locally, and live persistence remains disabled.
- Eight exact Nordic BLE advertising functions, including initialization, event handling, and the
  complete `ble_advertising_start` mode-selection path with its inline `TBB` table, are source-routed in
  [`NORDIC-ADVERTISING-START-CLOSURE.md`](closures/NORDIC-ADVERTISING-START-CLOSURE.md).
- Ten exact Nordic unbonded buttonless-DFU functions, including one function Ghidra omitted and
  two non-contiguous SDK functions, are source/hash-routed in
  [`NORDIC-BUTTONLESS-DFU-CLOSURE.md`](closures/NORDIC-BUTTONLESS-DFU-CLOSURE.md).
- Nordic's exact shutdown request and static shutdown processor are source-routed in
  [`NORDIC-POWER-MANAGEMENT-CLOSURE.md`](closures/NORDIC-POWER-MANAGEMENT-CLOSURE.md).
- The twelve-function retained reset-trace closure, exact 16-byte CRC record, fault-vector path,
  and product/CMSIS split are documented in
  [`RESET-TRACE-CORRELATION.md`](correlation/RESET-TRACE-CORRELATION.md).
- The 16-function / 1,802-byte R1 structured-log record and live-cache closure, including four
  exact manual supplements, is documented in
  [`STRUCTURED-LOG-CACHE-CORRELATION.md`](correlation/STRUCTURED-LOG-CACHE-CORRELATION.md); Nordic logging,
  RTOS/toolchain services, time/device providers, and the `log.bin` writer/export path remain
  separate provider boundaries.
- The adjacent three-function / 876-byte `log.bin` circular-page writer is documented in
  [`LOG-BIN-WRITER-CORRELATION.md`](correlation/LOG-BIN-WRITER-CORRELATION.md); pinned FAL supplies lookup,
  configured flash callbacks supply physical I/O, and private export/transport remains excluded.
- The 602-byte IIR coefficient designer called exclusively by GoMore's already gated sleep
  initializer is retained behind the licensed-provider boundary in
  [`GOMORE-IIR-DESIGNER-PROVIDER-BOUNDARY.md`](boundaries/GOMORE-IIR-DESIGNER-PROVIDER-BOUNDARY.md); no private
  formula or coefficients are reconstructed locally.
- The 528-byte `sdkAuth` authorization parser at `0x0008EA0C` is retained behind the licensed
  GoMore boundary in
  [`GOMORE-AUTH-PARSER-PROVIDER-BOUNDARY.md`](boundaries/GOMORE-AUTH-PARSER-PROVIDER-BOUNDARY.md); its private
  format, tables, validation behavior, and authorization material are not reconstructed.
- The two-function / 616-byte R1 HRV day-packet reset and synchronization-flush behavior is
  documented in [`HRV-SYNC-FLUSH-CORRELATION.md`](correlation/HRV-SYNC-FLUSH-CORRELATION.md); allocation,
  time/calendar, topic selection, transport, and biometric providers remain external.
- The analogous two-function / 578-byte R1 heart-rate day-packet reset and synchronization-flush
  behavior is documented in [`HR-SYNC-FLUSH-CORRELATION.md`](correlation/HR-SYNC-FLUSH-CORRELATION.md);
  only the bounded product packet/reset policy is local, while allocation, time, topic,
  transport, logging, and biometric providers remain external.
- The opcode-`0x91` ATI/touch-calibration handler is closed as a one-function / 416-byte R1
  policy in [`ATI-CALIBRATION-COMMAND-CORRELATION.md`](correlation/ATI-CALIBRATION-COMMAND-CORRELATION.md).
  Its pure planner covers all eleven subcommands while IQS7211E, Nordic/CMSIS, logging, queue,
  and response-transport operations remain external.
- The two-function / 578-byte R1 SpO2 sibling is documented in
  [`SPO2-SYNC-FLUSH-CORRELATION.md`](correlation/SPO2-SYNC-FLUSH-CORRELATION.md), with the same clean-room
  packet-policy boundary and strict exclusion of the Goodix algorithm and shared providers.
- The noncontiguous 578-byte R1 touch-task dispatcher is bounded in
  [`TOUCH-TASK-DISPATCHER-CORRELATION.md`](correlation/TOUCH-TASK-DISPATCHER-CORRELATION.md); its event routing
  may be clean-room implemented only around the pinned IQS7211E, Nordic/CMSIS, and shared-power
  provider seams.
- The 464-byte registration, noncontiguous 422-byte timer dispatch, and noncontiguous 562-byte
  unregistration bodies are isolated as a three-function / 1,448-byte named sensor-stream
  framework boundary in
  [`SENSOR-STREAM-FRAMEWORK-BOUNDARY.md`](boundaries/SENSOR-STREAM-FRAMEWORK-BOUNDARY.md); no attributable
  source or license is known, so openR1 uses typed admitted providers instead of cloning it.
- The two-function / 560-byte R1 BLE transmit-queue producer is documented in
  [`BLE-TX-QUEUE-DISPATCH-CORRELATION.md`](correlation/BLE-TX-QUEUE-DISPATCH-CORRELATION.md); the envelope and
  bounded queue policy are local while FreeRTOS/CMSIS, toolchain, logging, and BLE worker code stay
  external.
- The seven-function / 1,506-byte R1 wear-fusion closure is implemented as a pure policy over
  normalized observations in [`WEAR-FUSION-CORRELATION.md`](correlation/WEAR-FUSION-CORRELATION.md). Motion,
  Goodix optical/living algorithms, CMSIS time, and the unresolved sensor-stream framework remain
  external.
- The four-function / 498-byte R1 BLE connection-parameter observer, role-handle accessors, strict
  fast/slow classifier, and asymmetric retry plan are implemented without BLE or timer side
  effects in
  [`CONNECTION-PARAMETER-POLICY-CORRELATION.md`](correlation/CONNECTION-PARAMETER-POLICY-CORRELATION.md).
- The 472-byte compact-to-wire sleep synchronization packet builder is implemented with bounded
  run merging and legacy-clock correction in
  [`SLEEP-SYNC-PACKET-CORRELATION.md`](correlation/SLEEP-SYNC-PACKET-CORRELATION.md); allocation, transport,
  acknowledgement, flash, and clock providers remain external.
- The three-function / 850-byte validated-sleep delivery, fallback, storage-consumer, and
  two-attempt append chain is closed in
  [`VALIDATED-SLEEP-DELIVERY-CORRELATION.md`](correlation/VALIDATED-SLEEP-DELIVERY-CORRELATION.md). OpenR1
  keeps the event/logging frameworks external and replaces the stock destructive reset with an
  explicit error for deployer-owned recovery.
- Six functions / 1,328 bytes of shared quantized-neural machinery—including the indirect
  signed-int8 pooling executor, float quantizer, int8-add executor, and tensor-arena compactor—are isolated in
  [`QUANTIZED-POOLING-PROVIDER-BOUNDARY.md`](boundaries/QUANTIZED-POOLING-PROVIDER-BOUNDARY.md). No local
  executor or generic library substitution is admitted until an exact source, version, license,
  descriptor ABI, and tensor behavior are authenticated.
- The two-function boot reset-reason decoder and Nordic RESETREAS lifecycle adapter are documented
  in [`RESET-REASON-CORRELATION.md`](correlation/RESET-REASON-CORRELATION.md).
- The R1-owned local time production that replaces the blocked stock `sys rtc`/calendar layer is
  documented in [`CLOCK-PRODUCTION-CORRELATION.md`](correlation/CLOCK-PRODUCTION-CORRELATION.md).
- The 1,736-byte R1 BLE event consumer, `pairAuth` security scheduling, two-target `advStart`
  policy, and strict Nordic/RTOS provider split are documented in
  [`CONNECTION-CONTROL-CORRELATION.md`](correlation/CONNECTION-CONTROL-CORRELATION.md).
- The corrected YHM2710 `device_stacmd` table and complete 36-entry transparent reduction are in
  [`YHM2710-REDUCTION-CORRELATION.md`](correlation/YHM2710-REDUCTION-CORRELATION.md); the adjacent watchdog
  now compiles Nordic `nrfx_wdt.c` with only an R1 configuration/feed adapter, documented in
  [`WATCHDOG-DEVICE-CORRELATION.md`](correlation/WATCHDOG-DEVICE-CORRELATION.md).
- The first source-owned algorithm batches—331 Goodix functions and 198 GoMore primitives/tensor-runtime routines—are
  correlated in [`GOODIX-PRIMITIVES-REDUCTION-CORRELATION.md`](correlation/GOODIX-PRIMITIVES-REDUCTION-CORRELATION.md)
  and [`GOMORE-PRIMITIVES-REDUCTION-CORRELATION.md`](correlation/GOMORE-PRIMITIVES-REDUCTION-CORRELATION.md).
  The tensor subset has its descriptor/allocation seam documented in
  [`GOMORE-TENSOR-RUNTIME-REDUCTION-CORRELATION.md`](correlation/GOMORE-TENSOR-RUNTIME-REDUCTION-CORRELATION.md).
- The complete twelve-function Goodix `goodix_mem`/`GdMem` core, its twenty Goodix call-site
  helpers, and the R1 byte-fill are reconstructed in
  [`GOODIX-HEAP-REDUCTION-CORRELATION.md`](correlation/GOODIX-HEAP-REDUCTION-CORRELATION.md).
- The thirteen-function / 1,202-byte sensor-algorithm private heap, including its five
  scatter-loaded bodies and `sensor_algo_mem_fatal` path, is separately source-gated in
  [`SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md`](boundaries/SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md).
- The 2026-08 attribution re-examination tested all six `investigate_before_implementing`
  platform families (device registry, software TWI, sensor stream, quantized-neural runtime,
  time/calendar, RTC device — 165 functions) against fetched upstream sources and identified
  the interlocked "B210 platform" middleware as Wuxi Bravechip's closed ChipletRing / BCL603M
  platform (firmware string `603MV1.9.3`, byte-exact BAE8 GATT base-UUID match to the public
  `BravechipSpace/ChipletRing-APPSDK`). All six remain NO ATTRIBUTION and implementation-blocked,
  with licensed Bravechip acquisition as the named route; per-family reports are the six
  `boundaries/unknown_*_candidate-ATTRIBUTION-2026-08.md` files.
- The thirteen-function / 2,784-byte product-owned touch-slider closure, including one exact
  Ghidra-omitted IRQ callback, is admitted as clean-room behavior in
  [`TOUCH-SLIDER-CORRELATION.md`](correlation/TOUCH-SLIDER-CORRELATION.md).
- The dormant 1,344-byte R1 health-daily synthetic fixture is byte-pinned and excluded from the
  production image in
  [`HEALTH-DAILY-TEST-CORRELATION.md`](correlation/HEALTH-DAILY-TEST-CORRELATION.md).
- The indirect 1,234-byte GoMore floating-point neural-layer executor is source-gated, not locally
  reimplemented, in
  [`GOMORE-NEURAL-RUNTIME-BOUNDARY.md`](boundaries/GOMORE-NEURAL-RUNTIME-BOUNDARY.md).
- The six-function / 2,188-byte paired GoMore sleep-classifier graph closure is source-gated in
  [`GOMORE-SLEEP-GRAPH-PROVIDER-BOUNDARY.md`](boundaries/GOMORE-SLEEP-GRAPH-PROVIDER-BOUNDARY.md).
- The six-function / 1,890-byte GoMore activity-state window-classifier closure is source-gated in
  [`GOMORE-ACTIVITY-STATE-PROVIDER-BOUNDARY.md`](boundaries/GOMORE-ACTIVITY-STATE-PROVIDER-BOUNDARY.md).
- The seven-function Goodix packed-word integrity census, including five newly classified helpers,
  all direct callers, and three identical constant-table copies, is source-gated in
  [`GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md`](boundaries/GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md).
- The 58-function / 19,274-byte GH_NADT census, including 57 newly routed processing functions,
  exact component identity, 25-sample cadence, composite extents, and direct callgraph closure, is
  source-gated in [`GOODIX-NADT-PROVIDER-BOUNDARY.md`](boundaries/GOODIX-NADT-PROVIDER-BOUNDARY.md).
- The 31-function / 7,144-byte GH_HR processing closure, including the former largest unknown at
  `0x00032808`, is source-gated in
  [`GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md`](boundaries/GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md).
- The 9-function / 1,288-byte GH_HRV lifecycle, including the former largest unknown at
  `0x0006DB5C`, is source-gated in
  [`GOODIX-HRV-PROVIDER-BOUNDARY.md`](boundaries/GOODIX-HRV-PROVIDER-BOUNDARY.md).
- The complete two-function / 856-byte packed-channel decoder/scaler closure is transparent C
  with explicit table and toolchain-math bindings in
  [`GOODIX-CHANNEL-DECODER-PROVIDER-BOUNDARY.md`](boundaries/GOODIX-CHANNEL-DECODER-PROVIDER-BOUNDARY.md).
- The sole-caller 518-byte GH_NADT channel-quality stage is source-admitted with typed
  configuration and explicit exponential binding in
  [`GOODIX-NADT-QUALITY-PROVIDER-BOUNDARY.md`](boundaries/GOODIX-NADT-QUALITY-PROVIDER-BOUNDARY.md).
- The seven-function / 1,098-byte GH_NADT extrema/peak-mask chain is fully source-admitted in
  [`GOODIX-NADT-PEAK-MASK-PROVIDER-BOUNDARY.md`](boundaries/GOODIX-NADT-PEAK-MASK-PROVIDER-BOUNDARY.md).
- The complete 30-function / 5,126-byte GH_NADT accumulation/decision helper graph is
  source-admitted in
  [`GOODIX-NADT-ACCUMULATION-PROVIDER-BOUNDARY.md`](boundaries/GOODIX-NADT-ACCUMULATION-PROVIDER-BOUNDARY.md).
- The 514-byte eight-channel GH3X2X register-profile decoder is source-gated in
  [`GOODIX-REGISTER-PROFILE-PROVIDER-BOUNDARY.md`](boundaries/GOODIX-REGISTER-PROFILE-PROVIDER-BOUNDARY.md);
  no private register-profile format or parser is recreated.
- The 85-function / 19,568-byte GH_SPO2/dlCom closure, including 82 formerly unclassified Ghidra
  functions and three exact dispatcher-table wrappers, is source-gated in
  [`GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md`](boundaries/GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md).
- The two exact FreeRTOS static idle/timer memory callbacks and recovered 256-word stack
  configuration are separated from the upstream kernel in
  [`FREERTOS-STATIC-MEMORY-CORRELATION.md`](correlation/FREERTOS-STATIC-MEMORY-CORRELATION.md).
- The recovered four-word FreeRTOS stack-sentinel configuration and R1 diagnostic/fail-stop hook
  are separated from the upstream kernel in
  [`FREERTOS-STACK-OVERFLOW-CORRELATION.md`](correlation/FREERTOS-STACK-OVERFLOW-CORRELATION.md).
- The decisive 40-byte `prvReloadTimer` body establishes the authenticated upstream
  FreeRTOS-Kernel 10.5.1 core plus Nordic's nRF52 port split in
  [`FREERTOS-KERNEL-VERSION-CORRELATION.md`](correlation/FREERTOS-KERNEL-VERSION-CORRELATION.md).
- The exact application `SystemInit` and inlined-wait `nvmc_config` helper are routed to Nordic,
  with both recovered UICR configuration switches documented in
  [`NORDIC-SYSTEM-INIT-CORRELATION.md`](correlation/NORDIC-SYSTEM-INIT-CORRELATION.md).
- Nordic's exact TWIM transfer-completeness helper and both callsites are source-routed in
  [`NORDIC-TWIM-COMPLETENESS-CORRELATION.md`](correlation/NORDIC-TWIM-COMPLETENESS-CORRELATION.md).
- Ten exact Peer Manager GATT-cache functions are source-routed in
  [`NORDIC-GATT-CACHE-CLOSURE.md`](closures/NORDIC-GATT-CACHE-CLOSURE.md).
- Five exact Nordic BLE/Peer Manager static helpers are source-routed in
  [`NORDIC-BLE-STATIC-HELPERS-CORRELATION.md`](correlation/NORDIC-BLE-STATIC-HELPERS-CORRELATION.md).
- Eight branch-only aliases inherit their already accepted target ownership in
  [`RESOLVED-THUNK-CLOSURE.md`](closures/RESOLVED-THUNK-CLOSURE.md).
- The completed HR, SpO2, and HRV 24-record offline queues, exact 16/20-byte retained layouts,
  merge rules, and acknowledgement policies are documented in
  [`SCALAR-HEALTH-OFFLINE-SYNC-CORRELATION.md`](correlation/SCALAR-HEALTH-OFFLINE-SYNC-CORRELATION.md).
- The nine HR, SpO2, and HRV daily-cache callbacks, bounded UInt8/UInt16 accessors, reset
  preservation, and three-sample legacy-clock recovery are documented in
  [`SCALAR-HEALTH-DAILY-CACHE-CORRELATION.md`](correlation/SCALAR-HEALTH-DAILY-CACHE-CORRELATION.md).
- The fifteen HR, SpO2, and HRV value consumers, latest-point accessors, hourly aggregators,
  timestamp contracts, and notification routes are documented in
  [`SCALAR-HEALTH-SAMPLE-STORAGE-CORRELATION.md`](correlation/SCALAR-HEALTH-SAMPLE-STORAGE-CORRELATION.md).
- The eleven-function retained health crash-record lifecycle, cache snapshot and restore,
  opaque provider-blob seam, and CRC lifecycle are documented in
  [`HEALTH-CRASH-SNAPSHOT-CORRELATION.md`](correlation/HEALTH-CRASH-SNAPSHOT-CORRELATION.md).
- The health database provider binding and startup controller's exact schema gate,
  FlashDB/provider ordering, retained-clock handoff, zeroed recovery query, and allocation-failure behavior are documented in
  [`HEALTH-DATABASE-STARTUP-CORRELATION.md`](correlation/HEALTH-DATABASE-STARTUP-CORRELATION.md).
- The fifteen byte-pinned TWI register-transfer/completion/wait/lifecycle adapters and their strict
  Nordic SDK / authenticated CMSIS-FreeRTOS provider split are documented in
  [`TWI-SYNCHRONIZATION-CORRELATION.md`](correlation/TWI-SYNCHRONIZATION-CORRELATION.md).
- The six exact two-wire record-binding configurations and direct-typed replacement for their
  unidentified registry dependency are documented in
  [`BUS-REGISTRATION-CORRELATION.md`](correlation/BUS-REGISTRATION-CORRELATION.md).
- The forty exact software-TWI engine functions, four recovered state/pin instances, and unresolved
  provider-source gate are documented in
  [`SOFTWARE-TWI-PROVIDER-BOUNDARY.md`](boundaries/SOFTWARE-TWI-PROVIDER-BOUNDARY.md).
- The exact Nordic/R1/unidentified split for the adjacent nine-function RTC-device layer is
  documented in [`RTC-DEVICE-PROVIDER-BOUNDARY.md`](boundaries/RTC-DEVICE-PROVIDER-BOUNDARY.md).
- The retained crash-log sink's bounded R1 buffer/newline policy and its toolchain/SEGGER provider
  split are documented in [`RETAINED-LOG-CORRELATION.md`](correlation/RETAINED-LOG-CORRELATION.md).
- The exact 14-entry health registration lookup, nine event-14 routes, inert search residue, and
  temperature/stress route absence are documented in
  [`HEALTH-HISTORY-ROUTING-CORRELATION.md`](correlation/HEALTH-HISTORY-ROUTING-CORRELATION.md).
- Material time-transition and local-hour rollover planning, exact known-cursor reconciliation,
  and the FlashDB/GoMore provider boundary are documented in
  [`TIME-HEALTH-ROLLOVER-CORRELATION.md`](correlation/TIME-HEALTH-ROLLOVER-CORRELATION.md).
- The product-owned temperature/stress range gates, offset representation, hourly aggregation,
  and daily-cache callbacks—separate from GXCAS and GoMore providers—are documented in
  [`TEMPERATURE-STRESS-DAILY-CACHE-CORRELATION.md`](correlation/TEMPERATURE-STRESS-DAILY-CACHE-CORRELATION.md).
- The five activity daily-cache lifecycle functions and their legacy-clock redaction policy are documented
  in [`ACTIVITY-DAILY-CACHE-CORRELATION.md`](correlation/ACTIVITY-DAILY-CACHE-CORRELATION.md).
- Activity RAM/decoded-flash day merge, context-preserving builder reset, timestamp clamp, and
  packet flush are documented in
  [`ACTIVITY-DAY-MERGE-CORRELATION.md`](correlation/ACTIVITY-DAY-MERGE-CORRELATION.md).
- The provider-facing 24-byte activity accumulator, 600-second publication policy, exact event-11
  record, wear transition handling, and packed cache consumer are documented in
  [`ACTIVITY-ACCUMULATOR-CORRELATION.md`](correlation/ACTIVITY-ACCUMULATOR-CORRELATION.md).
- The exact clock/calendar/backend cluster and its unresolved source-admission gate are documented
  in [`TIME-CALENDAR-PROVIDER-BOUNDARY.md`](boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md).

- [`../research/decompilation/README.md`](../research/decompilation/README.md): the complete
  supplied-image function, address, symbol, call-graph, disassembly, and decompiler corpus.
- [`../r1-bootloader-reconstruction/README.md`](README.md):
  bootloader control-flow and memory reconstruction.
- `../r1-2.2.6.0009-firmware-analysis.md`: subsystem-level
  behavioral findings and exact handlers.
- `../r1-reverse-engineering-feasibility.md`: normal
  EUS wire model, command catalog, device behavior, sensors, and remaining physical gates.
- `../r1-capability-matrix.csv`: 202 evidence and readiness records,
  including R1-193 through R1-202.
- `../r1-firmware-security-follow-up.md`: application,
  bootloader, update, ACL, debug, and malformed-input findings.
- [`generated/application-source-correlation/README.md`](README.md):
  reproducible 31,776-row semantic comparison against the symbol-bearing Nordic SDK reference;
  candidates remain subject to function-local review.
- [`generated/st25dvxxkc-source-correlation/README.md`](README.md):
  reproducible 31,776-row comparison against a symbol-bearing build of ST's pinned ST25DVxxKC
  component, including exact `ReadReg` and `WriteReg` anchors.
- the version-pinned Swift R1 protocol controllers and their tests (external to this repository)
  and `R1ProtocolModels.swift`:
  version-pinned, tested executable specifications.

These are provenance inputs, not linked code. `r1` contains no copied decompiler body. The
separate vendor-source policy and exact dependency inventory are in
[`SOURCE-ADMISSION.md`](SOURCE-ADMISSION.md).

Source admission is also enforced for every recovered function by
[`FUNCTION-OWNERSHIP.csv`](reference/FUNCTION-OWNERSHIP.csv). Unclassified functions are blocked for
ownership research rather than presumed eligible for rewriting; methodology and dispositions are
documented in [`FUNCTION-OWNERSHIP.md`](reference/FUNCTION-OWNERSHIP.md). The exact 756-entry Nordic mapping
(538 application and 218 bootloader entries) and thirteen-entry SDK-bundled SEGGER mapping, plus the R1
log-prefix adapter boundary, are documented in
[`NORDIC-SDK-CORRELATION.md`](correlation/NORDIC-SDK-CORRELATION.md). The standard-C/EABI provider subset is
documented in [`TOOLCHAIN-RUNTIME-CORRELATION.md`](correlation/TOOLCHAIN-RUNTIME-CORRELATION.md).
The current ledger has 269 GoMore-gated entries, three bounded R1/GoMore adapters, three bounded
R1 health-storage provider adapters, fifteen R1 TWI provider adapters, nine R1 direct
record-binding configuration adapters, 394
Goodix-gated provider/demo/closure entries, 18 clean-room R1/Goodix adapters, 12 clean-room
R1/IQS7211E configuration/port/policy adapters, 23 clean-room common motion adapters, 27
ST25DVxxKC provider bodies, eleven R1/ST25DVxxKC adapters, five R1 `i2c_5`/power resource adapters,
ten R1 internal-flash adapters, four R1 analog adapters, nine blocked generic device-registry
functions, fourteen blocked time/calendar-provider functions, forty blocked software-TWI-provider
functions, seven blocked RTC-device-provider functions, thirteen blocked sensor-algorithm
heap-provider functions, seven R1 automatic health-sync
functions, five R1 activity offline-sync functions, and
fifteen R1 scalar-health offline-sync functions, fifteen scalar-health sample-storage functions,
five R1 activity daily-cache lifecycle functions, five
R1 activity day-merge/flush functions, five R1 activity accumulator/storage functions, eleven R1
health crash-record lifecycle functions, one R1/FlashDB handle accessor, one R1 health-database
startup orchestrator, and nine
scalar-health daily-cache callbacks. The ledger
also admits fifteen temperature/stress storage-cache functions while keeping GXCAS and GoMore
providers gated. It now leaves 685 unclassified
application entries. The gated provider bodies and
unclassified entries are not
eligible for local implementation. IQS7211E's admitted adapters are compiled and linked, but cannot
energize hardware until its explicit identity and shared-power boundaries are provisioned. The
ST25DVxxKC path is likewise linked and starts disabled. Nordic startup binds its exact P1.10 board
lifecycle and exclusive `i2c_5` mutex; the reconstructed YHM board binding must take that same mutex.

## Implemented compatibility spine

### Wire protocol

- Twelve-byte normal inner model with version/module/module-version, little-endian serial and
  length, status, command, subcommand, checksum, and payload.
- Phone-to-ring compact CRC-16/CCITT preimage, including the low serial byte, low length byte, and
  single zero checksum placeholder used by the first-party constructor.
- Ring-to-phone CRC-16/MODBUS over the complete model with checksum bytes zeroed.
- Non-reflected Castagnoli checksum with polynomial `0x1EDC6F41`, zero seed, and no final XOR.
- Five-byte EUS fragment header, 239-byte fragment payload, descending sequence, repeated complete
  message checksum, sequence zero completion, 4,062-byte safe output, and 4,063-byte bounded input.
- The exact 424-byte receive reassembler at `0x00032198` and its sole channel-2 event callsite are
  body/callgraph-pinned in
  [`EUS-RX-REASSEMBLY-CORRELATION.md`](correlation/EUS-RX-REASSEMBLY-CORRELATION.md); valid stock behavior is
  retained while malformed duplicate, discontinuous, and inconsistent-checksum trains fail closed.
- The registered 418-byte BAE8 callback and its event `2/3/6...9` product routing are pinned in
  [`BAE8-EVENT-ROUTER-CORRELATION.md`](correlation/BAE8-EVENT-ROUTER-CORRELATION.md); local code exposes a pure
  route plan while Nordic link-context/service providers and unresolved BC/event helpers stay out.
- The stock exact-multiple empty terminal fragment is retained because it is externally observable.
- Reassembly rejects length, sequence, checksum, capacity, and cross-message inconsistencies.

### Device and command behavior

- `deviceStatus` (`01/00/01`): seven-byte requested form.
- `deviceInfo` (`01/00/02`): two fixed 16-byte slots, initialized to the recovered
  `2.2.6.0009` / `603MV1.9.3` compatibility identity.
- `wearStatus` (`01/00/03`): one-byte state.
- `userInfo` (`01/00/04`): canonical 12-byte write, bounded validation, and persistence in the
  device-state model.
- `systemTime` (`01/00/05`): signed-timezone raw bits plus Unix time from the first six payload
  bytes.
- `touchSwitch` (`01/00/07`), pre-security `pairAuth` phone-role selection (`01/00/08`), 12-byte
  health settings (`0E`), 12-byte system settings (`0F`), authorized 15-byte device serial (`10`),
  and heartbeat-family acknowledgements.
- Unsupported or withheld routes receive explicit error/refuse/not-supported results.

### Memory, storage, and scheduling

- S140 application placement constants: flash `0x27000`, RAM `0x200064A8`.
- Recovered RTOS configuration: authenticated upstream FreeRTOS-Kernel 10.5.1 plus Nordic's nRF52
  port with 109 byte-pinned provider functions, 1024 Hz RTC tick, 56
  priorities, 256-word default stack, preemption, tickless idle, static/dynamic allocation, and
  `heap_4`, exposed through authenticated Arm CMSIS-FreeRTOS v10.5.1 source.
- A SoftDevice event-poll task and bounded EUS runtime task use CMSIS thread flags for wakeups.
  `SD_EVT_IRQHandler`, BLE receive, and HVN completion only signal work; Nordic/Arm providers own
  the scheduler and synchronization algorithms.
- Armink's authenticated CmBacktrace provider is compiled into the Nordic image with the recovered
  Cortex-M4, FreeRTOS, English, 20-byte-name, 32-frame, and 16-word-dump configuration. The local
  port uses statically known task stacks and retains a bounded crash log in `NOLOAD` RAM without
  exposing it over BLE. See [`CMBACKTRACE-CORRELATION.md`](correlation/CMBACKTRACE-CORRELATION.md).
- Motion provider ownership is resolved in
  [`MOTION-PROVIDER-CORRELATION.md`](correlation/MOTION-PROVIDER-CORRELATION.md): official Bosch v2.29.0 and
  ST LIS2DW12 v2.1.0-compatible code own their driver bodies; local code may contain only the
  recovered product adapters. The Nordic image probes the recovered TWIM1 P0.11/P0.14 bus at
  address `0x18`, selects LIS2DW12 before BMA456W, and retains the fixed configuration and bounded
  FIFO API. Interrupt-driven ingestion and owned-ring validation remain, and the unauthenticated
  QST path is not implemented.
- Nordic `nrfx_saadc.c` supplies the physical ADC driver. The retained R1 adapter configures
  battery AIN5/P0.29, PMIC current AIN3/P0.05, and NFC rectifier AIN2/P0.04 with the recovered
  gains and acquisition times. Portable R1 code implements only the exact filters, conversions,
  four battery curves, charging cadence/full gate, stalled-charge recovery, and runtime state
  transitions. Battery acquisition is unavailable until reconstructed YHM power and charge-state
  bindings exist; see
  [`ANALOG-BATTERY-CORRELATION.md`](correlation/ANALOG-BATTERY-CORRELATION.md).
- Seven contiguous 4-KiB-aligned partition descriptors spanning 36 pages: `kv.bin`, `health.db`,
  `sleep.db`, `pKey.bin`, `reserve`, `ep.bin`, and `log.bin`.
- The linked Nordic target binds that map to nRF52840 internal flash through official
  `nrf_fstorage_sd` and upstream FAL. The captured layout reserves `0xD1000...0xD3FFF` for Nordic
  FDS and `0xD4000...0xF7FFF` for `device_flash`; the linker stops before both. See
  [`INTERNAL-FLASH-CORRELATION.md`](correlation/INTERNAL-FLASH-CORRELATION.md).
- A bounded NOR flash interface and host NOR emulator that enforces one-to-zero programming,
  page erasure, range checks, operation counts, and deterministic mutation-failure injection.
- The R1-owned `kv.bin` format is implemented as the recovered four 2,048-byte snapshots and seven
  fixed classes with exact headers, names, lengths, defaults, base-131 hashes, and MODBUS CRCs.
  openR1 uses recovered block 7 as a generation commit and alternates sectors so an interrupted
  rollover retains the prior complete snapshot; strict legacy import is supported. See
  [`KV-STORE-CORRELATION.md`](correlation/KV-STORE-CORRELATION.md).
- The R1-specific two-sector `sleep.db` journal: exact headers, eight slots per sector, body-first
  commits, four-byte alignment, MODBUS CRC, synchronization marker, close sequence, oldest-sector
  rollover, 3,888-byte writer ceiling, and 232-byte synchronization-reader ceiling.
- Compact sleep persistence splits runs into six-bit half-minute chunks and merges adjacent types
  during restart recovery. Power-loss tests prove an orphaned body is not counted as a record.
- Restored and newly persisted sessions retain their exact journal-header offset. A matched sleep
  packet ACK writes the timestamp-checked `0x11223344` marker before consuming the pending ACK or
  changing RAM; a flash failure leaves both states retryable.
- `health.db` is not reimplemented: unmodified upstream FlashDB 2.0.0 TSDB and its bundled FAL
  0.5.99 compile and run through the R1 port, producing the recovered `TSL0` layout and reverse-time
  traversal. FlashDB is not used for `kv.bin`. The internal-flash transport is linked;
  destructive policy, migration, power-loss, and owned-ring coexistence validation remain gates.
- Normal 20-record and EUS/eAT 50-record output queues.
- Four notification credits, saturating completion replenishment, and queue/credit reset on
  disconnect.
- A hardware interface for accelerometer, optical, temperature, flash, and time services without
  inventing unverified device behavior.

### Nordic BLE security provider

- Unmodified Nordic Peer Manager modules own bond persistence, security dispatch, connection state,
  local GATT/CCCD cache, and FDS/fstorage transactions. The openR1 source supplies only recovered
  configuration and the adapter into the R1 session policy.
- Security parameters reproduce the recovered static contract: bonding enabled; no MITM, LESC,
  OOB, or keypress; no-input/no-output I/O capability; 7–16-byte keys; encryption and identity keys
  in both directions; repairing allowed; no central role, whitelist, identity-list, or privacy
  configuration.
- Peer Manager observers run before the BAE8 observer. The BAE8 TX adapter reads the per-connection
  CCCD through the SoftDevice so a value restored by Peer Manager is honored without duplicating
  Nordic's cache implementation.
- A bond is transport identity only. Nordic's encrypted/bonded status is copied into the runtime,
  but `authorized` remains false until a separate, evidence-backed product identity verifier exists.
- FDS reserves three 4-KiB pages immediately below the bootloader address reported through UICR (or
  below physical flash when no bootloader is configured). Those pages are outside the application
  linker region; deployment still must validate the actual UICR/bootloader layout on owned hardware.

### Nordic GATT negotiation provider

- Unmodified Nordic `nrf_ble_gatt` owns per-link ATT state, exchange requests/replies, retry state,
  clamping, disconnect reset, and link-layer data-length updates. The R1 adapter supplies only the
  recovered desired values: central and peripheral ATT MTU 247 and data length 251.
- The provider initiates MTU exchange on connection, handles peer-initiated server exchange, and
  requests the 251-byte link-layer length through S140. Until negotiation completes, EUS still
  fragments to the transport limit reported by the peer; the 244-byte characteristic ceiling is
  never treated as an immediately available write size.
- `pairAuth` now follows the recovered ordering: significant byte `01` assigns the sole phone role,
  then the platform callback asks Peer Manager to secure an unencrypted link. Duplicate phone-role
  assignment is rejected without replacing the existing owner. Neither role assignment nor a bond
  sets the independent product-authorization bit.
- The registered R1 Peer Manager callback now delegates Nordic's standard event/error and flash
  recovery handling to SDK 17.1.0, preserves repairing and product connection policy, performs no
  whitelist promotion, and deliberately excludes the stock LTK-printing diagnostic helper; see
  [`PEER-MANAGER-EVENT-POLICY-CORRELATION.md`](correlation/PEER-MANAGER-EVENT-POLICY-CORRELATION.md).

### Nordic advertising provider

- Unmodified Nordic `ble_advertising` and `ble_advdata` own AD encoding, advertising-set
  configuration, timeout transitions, and disconnect restart behavior. The R1 adapter supplies
  only evidence-recovered product data and mode parameters.
- The normal GAP name is `EVEN R1_` plus uppercase bytes 3, 2, and 1 of the SoftDevice address;
  factory mode appends `_FAC`. Appearance is `0x0240` (Generic Keyring), and preferred connection
  parameters are 15–30 ms, latency 4, with a 6-second supervision timeout.
- The legacy advertisement contains flags `0x06`, complete name, and appearance. Its scan response
  contains manufacturer identifier `0x5245`, the six address bytes in SoftDevice order, and an
  optional 15-byte provisioned product serial. It intentionally advertises no service UUID or TX
  power element.
- Normal mode runs at 100 ms for 60 seconds, then 1 second indefinitely. The admitted factory-mode
  configuration runs at 100 ms indefinitely and disables slow mode. Startup currently selects
  normal, unprovisioned mode; durable factory marker/serial restore and the two-role stop/restart
  policy remain pending storage and role integration.

### Health history and synchronization

- Twenty-four hourly aggregate slots for HR and SpO₂ using one-byte average/maximum/minimum
  values, plus HRV using UInt16 values and the recovered wrapping rolling-average behavior.
- Exact daily wire headers, optional latest-point fields, four-byte narrow hourly items, and
  seven-byte wide hourly items.
- A 144-bucket activity day with exact seven-byte bucket encoding and the recovered
  count/UTC-offset/day-start prefix; full days correctly cross the EUS multipart boundary.
- A 144-record activity offline FIFO with exact 16-byte record semantics, drop and full-ring
  behavior, timestamp-bounded prefix consumption, consecutive day/offset grouping, duplicate
  bucket replacement, maximum-timestamp acknowledgement context, and flash/offline/RAM ACK modes;
  see [`ACTIVITY-OFFLINE-SYNC-CORRELATION.md`](correlation/ACTIVITY-OFFLINE-SYNC-CORRELATION.md).
- Distinct 24-record heart-rate, SpO2, and HRV offline FIFOs with exact 16/20-byte retained record
  semantics, full-ring overwrite, FIFO-prefix consumption, consecutive day/offset merge,
  repeated-hour replacement, and metric-specific ACK clock policy; see
  [`SCALAR-HEALTH-OFFLINE-SYNC-CORRELATION.md`](correlation/SCALAR-HEALTH-OFFLINE-SYNC-CORRELATION.md).
- Activity daily-cache reset, bounded hour write, and legacy-clock read/redaction callbacks; see
  [`ACTIVITY-DAILY-CACHE-CORRELATION.md`](correlation/ACTIVITY-DAILY-CACHE-CORRELATION.md).
- Activity day-building from RAM and decoded flash records, exact timestamp/day rollover rules,
  public packet flush, and acknowledgement context; see
  [`ACTIVITY-DAY-MERGE-CORRELATION.md`](correlation/ACTIVITY-DAY-MERGE-CORRELATION.md).
- A provider-facing cumulative activity service with exact 24-byte state, 600-second publication
  window, midnight/rollback/wear rebasing, 12-byte event-11 payload, cross-bucket placement, and
  packed 12/10/10-bit cache addition; see
  [`ACTIVITY-ACCUMULATOR-CORRELATION.md`](correlation/ACTIVITY-ACCUMULATOR-CORRELATION.md). Step detection,
  locomotion classification, and energy calculation remain licensed-provider boundaries.
- Up to 16 sleep sessions, matching the two-sector journal retention ceiling. Each phone payload
  uses the recovered 32-byte header and expanded `[stage, halfMinutes UInt16LE]` tail, with a
  200-run limit derived from the 232-byte stock synchronization-body bound.
- Daily HR, SpO₂, HRV, activity, and sleep queries emit a same-serial empty `0x03` ACK followed by
  ring-serial `0x02` data notifications. Point reads emit the recovered 8/9-byte typed result.
- A 32-entry first-match pending-acknowledgement table models handler `0x842CC` / resolver
  `0x83028`. Sleep packet ACKs use the bound durable-marker callback before marking the session
  synchronized; disconnect clearing is explicit.
- The HRV RMSSD primitive reproduces the recovered validity mask, endpoint invalidation above a
  150 ms adjacent change, 1100/1500 ms modes, index-zero ceiling quirk, sequential Float32 square
  accumulation, population divisor, square root, ordered-positive publication gate, and low-UInt16
  eight-byte event. Cortex-M4F builds use hardware single-precision operations.
- The recovered HRV producer state machine ignores callbacks 1–9, accepts at most four intervals
  per callback, maintains the physical-order 100-entry circular buffer, gates at callback 60 and
  70 nonzero intervals, and reproduces full reset versus timed-window retry transitions.
- Activity `05/02` preserves exact `2.2.6.0009` refresh-only behavior and emits no direct response.
- Automatic synchronization requires an active phone-role link and runs at initial timestamp,
  clock rewind, or at least 10,800 elapsed seconds. It invokes HR, SpO2, HRV, activity, and
  unsynchronized sleep in that order with serial zero, then advances the shared timestamp without
  aggregating leg success. An authorized explicit history query resets the same timestamp before
  query routing.
- The real 120-second timer source, optical RR producer, eligibility inputs, and unproven
  measure-control routes remain pending sensor-HAL integration. The automatic-sync policy is
  retained in the Nordic image, but its periodic wall-clock producer remains pending scheduler
  integration.

The detailed row-by-row state is in [`COVERAGE.csv`](reference/COVERAGE.csv).
Clean source symbols are cross-referenced to recovered stock addresses in
[`PROVENANCE.md`](PROVENANCE.md).

## Intentional security differences

The audit is a design input, so functionally equivalent does not mean vulnerability equivalent.
The following stock behaviors are intentionally changed:

- Every command has an actual backing-length check. The recovered short-frame over-reads are not
  reproduced.
- State-changing ACKs are generated after validation and state update, not before an unchecked or
  failed effect.
- Pair role selection does not authenticate a peer. Mutations require encrypted, bonded, and
  separately authorized session state.
- The channel-1/eAT parser that allowed a 244-byte value to overflow a 36-byte global buffer is not
  present. A future HAL must keep data length-carrying and bounded end to end.
- OTA start, advertising target mutation, algorithm-key provisioning, NV restore, shutdown,
  remove-ring, factory/test commands, and destructive storage operations are withheld from the
  normal dispatcher.
- Device serial reads require authorization. Key material and live restore payloads are never
  logged or exposed through a generic command surface.
- Prepare/Execute writes, raw register buses, NFC mailbox writes, and generic flash writes are not
  exposed over BLE.
- The BAE8 service observes and rejects queued-write authorization operations. Channel 1 remains a
  bounded no-op until its BC/eAT parser and product authorization policy are independently complete.

See [`SECURITY.md`](SECURITY.md) for the integration requirements these choices impose.

## Build and verification

From the repository root:

```sh
make -C openR1 test
make -C openR1 sanitize
make -C openR1 arm-objects
make -C openR1 sim
python3 tools/verify_openr1.py
```

The first command uses strict warnings as errors. The second runs AddressSanitizer and
UndefinedBehaviorSanitizer. The third compiles every core source as freestanding ARM EABI Cortex-M4
code. The fourth builds a request/response simulator; for example,
`r1/build/openr1_sim 01 get` emits a synthetic `deviceStatus` response EUS value. The verifier
reruns all build checks and checks the recovered constants and documented coverage.

With the pinned external sources and Arm GNU 9.3.1 toolchain:

```sh
make -C openR1 vendor-audit SDK_ROOT=/absolute/nRF5_SDK_17.1.0_ddde560 \
  FLASHDB_ROOT=/absolute/FlashDB-4e5677408256f82d47cd56a6b04605dcee35ed9a \
  BMA456_ROOT=/absolute/BMA456_SensorAPI-3266db2c5de15be1a00232b8c0f2fd23e07934e0 \
  LIS2DW12_ROOT=/absolute/lis2dw12-pid-8d4bd522015004a9646102702901ba5a15ec6d39 \
  ST25DVXXKC_ROOT=/absolute/fp-sns-stbox1-e9a35449b777699b5e1dd0f1466de0ead554893a/Drivers/BSP/Components/st25dvxxkc \
  TINY_AES_ROOT=/absolute/tiny-AES-c-e72b6eff0884673997d0ca6385169bbd9b31936d \
  IQS7211E_ROOT=/absolute/flipperone-mcu-firmware-0a88e26bb8fd5b6afcdcc607fd748d7bc3d2b067 \
  AZOTEQ_SETTINGS_ROOT=/absolute/zmk-driver-iqs7211e-436d3c42172abf812ec104521f29384fc02fc50e \
  GOODIX_DEMOCODE_ROOT=/absolute/pebbleos-nonfree-2c0034a23b675a5f9a29e4a47e8b504c7a88e321/gh3x2x
make -C openR1 vendor-storage-test \
  FLASHDB_ROOT=/absolute/FlashDB-4e5677408256f82d47cd56a6b04605dcee35ed9a
make -C openR1 vendor-crypto-test \
  TINY_AES_ROOT=/absolute/tiny-AES-c-e72b6eff0884673997d0ca6385169bbd9b31936d
make -C openR1 vendor-goodix-test \
  GOODIX_DEMOCODE_ROOT=/absolute/pebbleos-nonfree-2c0034a23b675a5f9a29e4a47e8b504c7a88e321/gh3x2x
make -C openR1 sdk-verify SDK_ROOT=/absolute/nRF5_SDK_17.1.0_ddde560 \
  FLASHDB_ROOT=/absolute/FlashDB-4e5677408256f82d47cd56a6b04605dcee35ed9a \
  BMA456_ROOT=/absolute/BMA456_SensorAPI-3266db2c5de15be1a00232b8c0f2fd23e07934e0 \
  LIS2DW12_ROOT=/absolute/lis2dw12-pid-8d4bd522015004a9646102702901ba5a15ec6d39 \
  ST25DVXXKC_ROOT=/absolute/fp-sns-stbox1-e9a35449b777699b5e1dd0f1466de0ead554893a/Drivers/BSP/Components/st25dvxxkc \
  TINY_AES_ROOT=/absolute/tiny-AES-c-e72b6eff0884673997d0ca6385169bbd9b31936d \
  GOODIX_DEMOCODE_ROOT=/absolute/pebbleos-nonfree-2c0034a23b675a5f9a29e4a47e8b504c7a88e321/gh3x2x \
  GNU_INSTALL_ROOT=/absolute/gcc-arm-none-eabi-9-2020-q2-update/bin/
```

The SDK target emits a linked application ELF, HEX, BIN, and map with its vector table at `0x27000`
and initialized RAM at `0x200064A8`. It uses Nordic's startup, CMSIS, SoftDevice handler,
`ble_srv_common`, `nrf_ble_gatt`, Peer Manager, FDS/fstorage, connection state, GATT caches,
FreeRTOS-Kernel 10.5.1, Nordic's nRF52 FreeRTOS port, CMSIS-FreeRTOS v10.5.1, the FreeRTOS
app-timer backend, and S140 SVC declarations
rather than clean-room substitutes. The linked image
contains the exact BAE8 UUID base, `0001` service, `0010...0013` characteristics, per-link EUS
runtime, notification queue, and persistent bond/GATT-cache provider. This is not yet a
hardware-validated complete product: physical CCCD replay,
the glasses-role channel-1 binding that makes both-occupied advertising stop reachable,
owned-hardware RTOS timing, remaining board transports,
the motion interrupt consumer, and owned-ring motion validation are still required. Internal flash
is now linked through Nordic fstorage and upstream FAL with exact FDS/data separation; physical
power-loss and migration validation remain.
Bosch/ST driver bodies are assigned to pinned official sources. Their translation units and the
R1 TWIM1 selector/configuration/FIFO adapters are compiled and retained; startup probes the
recovered P0.11/P0.14 address-`0x18` bus in stock LIS2DW12-then-BMA456W order. The two ST25DVxxKC translation units are hash-verified, compiled, and
retained through the R1 bus/pin/interrupt adapter. NFC remains disabled at startup, while the exact
P1.10 lifecycle and exclusive `i2c_5` mutex are provisioned. The former TWIM1 instance conflict with
motion is resolved by the R1-owned arbiter in `openr1_twim1_arbiter.c`: the dock (NFC) context takes
the bus through a documented handoff, motion never preempts it, and every transfer by a non-owner
fails explicitly. Shared-power dock coexistence and owned-hardware validation remain gates.
QST remains provider-gated. The IQS7211E Nordic transport, GPIO lifecycle, active-low IRQ worker,
restart timer, and `touchSwitch` policy hook are retained in the image, but live touch remains gated
on the unresolved shared-power provider, identity provisioning, wear lease, and physical validation.
Code signing, image combination, and device installation remain separate from this source
reconstruction.

## Definition of complete

The active goal is complete only when all rows marked `deferred` in `COVERAGE.csv` are either:

1. implemented and verified against the recovered executable specification and owned-hardware
   captures; or
2. explicitly classified as a non-goal because reproducing it would restore an audited unsafe or
   destructive behavior.

The current milestone therefore establishes a reproducible compatibility foundation, not a claim
that all optical, health, sleep, touch, power, BLE, persistence, and boot functions are finished.
