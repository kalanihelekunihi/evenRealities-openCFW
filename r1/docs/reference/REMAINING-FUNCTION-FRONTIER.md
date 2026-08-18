# Remaining application-function frontier

Snapshot: 2026-08-13, after the final-53 residue closure.

Terminal explicit-entry update 2026-08-17: every executable entry named by the preserved Ghidra
analysis is now either an exact ledger start or contained in a proven contiguous ledger extent.
The last six functions / 666 bytes are independently compiled C; the audit has 639 exact starts
and zero `within_noncontiguous_bounding_range_unproven` rows. See
[`FINAL-EXPLICIT-ENTRY-CLOSURE.md`](../correlation/FINAL-EXPLICIT-ENTRY-CLOSURE.md). The older
tier narrative below is retained as closure history, not as a list of opaque executable gaps.

Explicit-entry follow-up 2026-08-17: the 364-byte product callback at
`0x0005232C` is now byte-pinned and compiled as a pure buttonless-DFU event
policy. Its event-0 advertising/disconnect intent is separated from Nordic
providers and bootloader/reset effects; see
[`BUTTONLESS-DFU-EVENT-POLICY-CORRELATION.md`](../correlation/BUTTONLESS-DFU-EVENT-POLICY-CORRELATION.md).
The adjacent touch audit now also pins the 72-byte recovery-timer callback at
`0x00046EAC` as a pure clear-latch/event-bit plan and adjudicates the off-by-four
`0x00046908` seed as data; see
[`TOUCH-RECOVERY-TIMER-CORRELATION.md`](../correlation/TOUCH-RECOVERY-TIMER-CORRELATION.md).
The scatter-installed 12-byte `i2c_5` delay callback at `0x00054AF0` is also
closed as an exact argument-ignoring no-op without enabling a live bus; see
[`I2C5-DELAY-CALLBACK-CORRELATION.md`](../correlation/I2C5-DELAY-CALLBACK-CORRELATION.md).
Three additional script seeds at `0x0007902C`, `0x000791E4`, and `0x00079E10`
are now exact manual supplements routed to Nordic SDK 17.1.0 GPIO/SAADC header
inlines; see
[`NORDIC-OMITTED-HAL-INLINES-CORRELATION.md`](../correlation/NORDIC-OMITTED-HAL-INLINES-CORRELATION.md).
The `0x0007A6FC` seed is now part of a complete six-wrapper/six-target Nordic
microsecond-delay closure, including ten exact bodies omitted by Ghidra; see
[`NORDIC-OMITTED-DELAY-CLUSTER-CORRELATION.md`](../correlation/NORDIC-OMITTED-DELAY-CLUSTER-CORRELATION.md).

Attribution re-examination 2026-08-14: all six `investigate_before_implementing` families were
re-tested against fetched upstream sources (CMSIS-NN, RT-Thread, MultiTimer, old newlib, Pebble,
BabyOS, mr-library, μC/Clk, vendor SDKs) and all remain NO ATTRIBUTION; the interlocked "B210
platform" middleware is identified as Wuxi Bravechip Technologies' closed "ChipletRing" /
BCL603M smart-ring platform (firmware string `603MV1.9.3`, byte-exact GATT base-UUID match to
the public `BravechipSpace/ChipletRing-APPSDK`), which names the commercial acquisition route.
Per-family reports: `../boundaries/unknown_*_candidate-ATTRIBUTION-2026-08.md` (six files).

## Current inventory

The generated ownership ledger contains 3,326 application/bootloader functions. All 304
bootloader entries are source-routed. Of 3,022 application entries, including 335 exact manual
provenance supplements, **zero remain `unclassified`**: every recovered function now carries an
ownership disposition. The final 53-entry residue (1,548 declared bytes) is closed by
[`FRONTIER-FINAL53-CORRELATION.md`](../correlation/FRONTIER-FINAL53-CORRELATION.md); earlier
closures are the 128...202-byte tier
([`FRONTIER-128-202-CORRELATION.md`](../correlation/FRONTIER-128-202-CORRELATION.md)), the
64...127-byte tier
([`FRONTIER-64-127-CORRELATION.md`](../correlation/FRONTIER-64-127-CORRELATION.md)), the
32...63-byte tier
([`FRONTIER-32-63-CORRELATION.md`](../correlation/FRONTIER-32-63-CORRELATION.md)), and the
sub-32-byte tier
([`FRONTIER-SUB32-CORRELATION.md`](../correlation/FRONTIER-SUB32-CORRELATION.md)).

The former provider-boundary frontier is no longer opaque executable work: all forty-three
generic device-registry, sixteen time/calendar-provider, forty software-TWI-provider, ten
RTC-device-provider, thirty-two sensor-stream, and twenty-eight shared quantized-runtime entries
have owner-authorized transparent-C reductions under their distinct provenance families.
Thirty-four sensor-algorithm heap functions are provenance-resolved as Goodix's
`goodix_mem`/`GdMem` memory-pool manager from the GH3X2X SDK common DSP support library and now
compile from owner-authorized transparent C; the two integrator-authored glue bodies (the
`Gh3x2xPoolIsNotEnough` fatal handler at `0x0002E952` and the product byte-fill at `0x00092B60`)
remain R1 product behavior. Thirty-two generic sensor-stream functions likewise compile from
their independently reconstructed registry, list, allocator, buffer, and timer implementation.
Twenty-eight shared quantized-neural runtime functions are reconstructed under the
owner-authorized `unknown_shared_quantized_neural_runtime_candidate` reduction, including the
indirect 434-byte signed-int8 pooling executor, float quantizer, parameter helper, descriptor
constructors, int8-add, float tensor-add, softmax and float dense executors, and the
twelve-descriptor tensor-arena alloc/free pair; no exact provider source was authenticated, so
the attribution label remains while the implementation is transparent C.
The completed 264...274-byte tier routes three R1 product functions and three formerly GoMore-private
functions / 1,386 bytes. The existing EUS producer now has its exact 272-byte body pinned; clean
metadata-only policies add the five/30-cycle battery diagnostic cadence and `ep.bin` recovery
cursor. GoMore timestamp expansion, its exclusive fill helper, and fixed-coefficient IIR filtering
were subsequently included in the complete owner-authorized GoMore reduction. See
[`FRONTIER-264-274-CORRELATION.md`](../correlation/FRONTIER-264-274-CORRELATION.md).
The completed 256...262-byte inventory tier routes thirteen more entries / 2,090 ledger bytes.
One Ghidra extent is corrected from 262 to 272 executable bytes, making the immutable executable
census 2,100 bytes. The clean-room side is limited to the system-settings/REG1 action plan,
temperature timed-mode transition plan, and bounded selector over a caller-supplied Goodix
snapshot. Ten pooling and sleep/history functions were subsequently included in the complete
owner-authorized GoMore reduction. See
[`FRONTIER-256-262-CORRELATION.md`](../correlation/FRONTIER-256-262-CORRELATION.md).
The completed 230...248-byte inventory tier routes seventeen entries / 1,928 ledger bytes. One
Ghidra extent is corrected from 234 to 240 executable bytes, making the immutable executable
census 1,934 bytes. The clean-room side reuses the R1 `kv.bin` store and adds only an `ep.bin`
readiness plan, a bounded legacy device-info formatter, and fixed-record data fields. Three
GoMore functions and three shared quantized-runtime functions were subsequently reconstructed
under the owner-authorized transparent-C policy. See
[`FRONTIER-230-248-CORRELATION.md`](../correlation/FRONTIER-230-248-CORRELATION.md).
The completed 224...230-byte tier routes eight entries / 1,458 bytes. Four frontier functions and
two helpers are R1 product behavior: delayed-event cancellation, heart-rate mode transitions,
ring-stability decisions, and the connected-link PHY gate. The PDM IRQ handler is routed to Nordic
SDK 17.1.0, and the int8-add executor expands the blocked shared-runtime boundary. See
[`FRONTIER-224-230-CORRELATION.md`](../correlation/FRONTIER-224-230-CORRELATION.md).
The completed 212...222-byte inventory tier routes seven entries / 1,524 ledger bytes and corrects
three truncated inventory extents, yielding 1,542 executable bytes. Two bodies remain provider-owned
(Goodix signal processing and the unattributed sensor-stream framework); the five bounded R1 seams
cover stored-sleep acknowledgement, CmBacktrace/FreeRTOS task diagnostics, serialized BAE8 HVX,
system-control command `0x37`, and Nordic FDS-event translation. See
[`FRONTIER-212-222-CORRELATION.md`](../correlation/FRONTIER-212-222-CORRELATION.md).
The completed 204...210-byte inventory tier routes five entries / 1,030 bytes. Four bounded R1
seams cover named Goodix-facing stream configuration, six-bucket activity-record expansion,
Nordic GAP connection-profile selection, and newest-valid FAL/device-slot scanning. The shared
twelve-descriptor tensor-arena allocator remains blocked pending exact attribution. See
[`FRONTIER-204-210-CORRELATION.md`](../correlation/FRONTIER-204-210-CORRELATION.md).
Eight composite-initializer functions / 586 bytes are newly routed into the existing GoMore
licensed-provider gate, bringing that boundary to 221 exact functions. The indirect 1,234-byte
floating-point neural-layer executor at `0x00076BDC` is now also routed to that gate, bringing the
GoMore boundary to 222 exact functions.
Six paired sleep-classifier graph-builder/allocator functions / 2,188 bytes are now routed to the
same provider gate, bringing the GoMore boundary to 228 exact functions.
Six activity-state window-classifier functions / 1,890 bytes are now routed to the same provider
gate, bringing the GoMore boundary to 234 exact functions.
Nine energy-model dispatcher/estimator functions / 2,360 bytes are now routed to the same
provider gate, bringing the GoMore boundary to 243 exact functions.
The 602-byte private IIR coefficient designer at `0x000717AC` is now routed to the same provider
gate through its sole caller in the already gated sleep initializer, bringing the GoMore boundary
to 244 exact functions.
The noncontiguous 528-byte `sdkAuth` parser at `0x0008EA0C` is now routed through its sole caller
in the `gomore_setAuthParameters` path, bringing the historical GoMore boundary to 245 exact
functions. It is now source-admitted with explicit decrypt keys and typed dispatch callbacks; no
stock authorization material is copied.
Three sleep-stage statistics functions / 796 bytes are now routed through their exclusive
callgraph into the same licensed-provider gate, bringing the GoMore boundary to 248 exact
functions. The two statistics blocks and their shared timestamp-indexed stage lookup helper remain
provider-only.
Five packed-word integrity helpers / 162 bytes were routed into the existing Goodix
licensed-provider gate, and the resolved branch thunk brought the earlier census to 170. The
GH_NADT closure now adds 57 formerly unclassified processing functions / 19,148 bytes while
retaining the already gated version builder, bringing its complete census to 58 functions /
19,274 bytes.
The GH_HR callgraph closure adds 31 formerly unclassified functions / 7,144 executable bytes,
bringing the complete Goodix-gated census to 231 at that stage.
The GH_HRV lifecycle closure adds seven formerly unclassified functions / 1,154 executable bytes
around the two already gated identity/output functions. Its nine functions / 1,288 bytes precede
the later GH_SPO2/dlCom, supplemental NADT, packed-channel, NADT-quality, register-profile, and
peak-mask, accumulation/decision, and dlCom peak-selector closures; after correcting one shared
quantizer constructor's attribution, the complete Goodix gate is now 394.
The GH_SPO2/dlCom closure adds 82 formerly unclassified Ghidra functions / 19,520 executable bytes
and three exact 16-byte dispatcher-table wrappers omitted by Ghidra, bringing the complete
Goodix-gated census to 316 at that stage / 85 newly bounded entries in this closure.
The packed-channel decoder/scaling closure adds two formerly unclassified functions / 856 bytes,
and the sole-caller GH_NADT quality closure adds another 518-byte function, bringing the current
complete Goodix gate to 352 functions. Their private lookup tables, thresholds,
coefficients, and floating-point formulas remain provider-only.
The sole-thunk 514-byte GH3X2X register-profile decoder adds one provider entry, and the closed
seven-function / 1,098-byte GH_NADT peak-mask chain and the remaining 30-function / 5,126-byte
accumulation/decision graph, GH_HR initializer, quantization helper, dlCom peak selector, and the
channel-decimation/rolling-window body at `0x00029D5C` bring the Goodix gate to 395 functions at
that stage; the later shared-quantizer correction makes the current count 394. Their private
signal-processing behavior remains excluded.
Twelve formerly unclassified Ghidra functions / 1,720 bytes and four exact manual functions / 82
bytes now form a 16-function / 1,802-byte R1 structured-log cache closure. Nordic logging,
toolchain, RTOS, clock/calendar, device-registry, and `log.bin` writer/export implementations stay
outside that product boundary.
Three formerly unclassified functions / 876 bytes now form the adjacent R1 `log.bin` circular-page
writer closure. Pinned FAL lookup, configured flash-device I/O, Nordic logging, and the composite
private-log exporter/transport remain outside that product boundary.
Two formerly unclassified functions / 616 bytes now close the R1 HRV day-packet reset and flush
path around external time, allocation, topic, and transport providers.
The adjacent 380-byte HRV current-RAM merge at `0x00040DE0` is now product-routed. Its clean-room
adapter refreshes day/timezone metadata, selects nonzero hourly aggregates inside the requested
window while retaining the current hour, clamps the acknowledgement cursor, and delegates to the
already bounded UInt16 packet encoder/emitter. HRV production, clock, logging, storage, and
transport remain external.
Two formerly unclassified functions / 578 bytes now close the analogous R1 heart-rate day-packet
reset and flush path. The exact 12-byte prefix, sparse four-byte hourly values, optional
acknowledgement context, future-record rejection, and reset behavior are product policy; time,
allocation, topic, transport, logging, and biometric providers remain external.
Two more formerly unclassified functions / 578 bytes close the equivalent R1 SpO2 day-packet
reset and flush path under the same split. Its metric-specific caller set, cache accessor, and
transport seam are pinned separately; Goodix processing remains licensed-provider-only.
The 578-byte noncontiguous touch-task dispatcher at `0x00046650` is now bounded as R1 lifecycle,
event-routing, diagnostics, and factory-marker glue around the pinned IQS7211E provider. Nordic,
CMSIS-FreeRTOS, shared-power, logging, controller, and unresolved hardware implementations remain
outside the adapter boundary.
The 562-byte noncontiguous named sensor-stream unregister routine at `0x00089B08` and the
422-byte noncontiguous timer callback at `0x0008A1E0` are now isolated
under `unknown_sensor_stream_framework_candidate`. Its source, version, and license remain
unresolved, so neither it nor its list/allocation/timer dependencies are eligible for local
implementation.
Three functions / 572 bytes now close the R1 BLE transmit-queue producer: type-0 and type-2
inventory veneers plus the independently bounded dormant type-1 supplement, a bounded envelope,
90-percent warning, 100-tick put timeout, worker signal, and failure cleanup around separately
owned FreeRTOS/CMSIS/toolchain/transport services.
The R1 touch-slider closure adds twelve formerly unclassified Ghidra functions / 2,776 bytes and
one exact eight-byte IRQ callback omitted by Ghidra. These are product calibration, gesture,
timing, callback, and event-routing behaviors around the separately owned IQS7211E provider.
The dormant R1 health-daily synthetic test fixture / 1,344 bytes is now product-routed but excluded
from production; it has no recovered caller or entry-pointer reference.
Two FreeRTOS static-memory callbacks / 36 bytes are source-routed as R1 provider configuration;
the upstream scheduler and timer implementations remain authenticated FreeRTOS-Kernel 10.5.1.
A FreeRTOS stack-overflow callback / 72 bytes is now source-routed as R1 provider configuration;
the upstream four-word sentinel check remains FreeRTOS-Kernel provider code.
FreeRTOS 10.5.1 `prvReloadTimer` / 40 bytes is source-routed to the authenticated upstream core;
its absence from Nordic's bundled 10.0.0 core establishes the core-version/provider split.
Nine resolved branch-only thunks / 36 bytes now inherit their exact target ownership: one maps to
reconstructed Goodix code, one aliases an R1 Goodix adapter, and six alias R1 daily-cache metadata operations.
The ninth is the revision-confused `0x0007D2A0` script seed, which is a direct
alias to authenticated FreeRTOS `xTaskGetTickCount` in the preserved image.
Application `SystemInit` and `nvmc_config` / 544 bytes are now exact Nordic source routes; the
recovered NFCT-as-GPIO and GPIO pin-reset switches are build configuration only.
Nordic `xfer_completeness_check` / 98 bytes is now routed to `nrfx_twim.c`.
Ten Nordic Peer Manager GATT-cache functions / 784 bytes are now source-routed.
Five Nordic BLE/Peer Manager static helpers / 158 bytes are now source-routed.
Eight Nordic BLE advertising functions / 992 bytes are now source-routed; their complete extents
total 998 bytes because `ble_advertising_start` owns a six-byte inline mode jump table.
Eight newly routed Nordic buttonless-DFU functions / 668 Ghidra bytes are now source-routed. A
ninth exact 128-byte provider function omitted by Ghidra is added as a manual provenance
supplement, while a tenth 162-byte function was already Nordic-routed and is now scatter-pinned.
Two Nordic power-management shutdown functions / 332 bytes are now source-routed with direct
dispatch proving that the SDK scheduler option is disabled.
Fourteen YHM2710 state-command bodies are now separately vendor-gated rather than unclassified;
four Nordic watchdog bodies and two bounded R1 watchdog adapters are source-routed.
Twelve retained reset-trace functions / 598 bytes are now closed: eleven are R1-owned record and
capture behavior, while the fault-reset wrapper delegates reset mechanics to Nordic/CMSIS.
Two reset-reason functions / 834 bytes are now closed as R1 decode/report policy plus a bounded
adapter to Nordic RESETREAS get/clear primitives.
The 1,736-byte BLE-thread event consumer is now closed as product-specific role, target-address,
and advertising orchestration around separately owned Nordic, CMSIS-FreeRTOS, and FreeRTOS calls.

| Address band | Investigation-blocked entries | Recovered body bytes |
| --- | ---: | ---: |
| `0x00020000...0x0002FFFF` | 3 | 254 |
| `0x00030000...0x0003FFFF` | 2 | 470 |
| `0x00040000...0x0004FFFF` | 1 | 434 |
| `0x00050000...0x0005FFFF` | 81 | 5,928 |
| `0x00060000...0x0006FFFF` | 3 | 114 |
| `0x00070000...0x0007FFFF` | 12 | 604 |
| `0x00080000...0x0008FFFF` | 49 | 3,682 |
| `0x00090000...0x0009FFFF` | 13 | 820 |

Body size and proximity are prioritization signals only. They do not establish authorship or
permission to implement a function. Every promotion still requires function-local semantics,
callgraph context, attributable-source comparison where applicable, and an exact provider or
clean-room disposition.

## Largest unresolved bodies

| Entry | Bytes | Current treatment |
| --- | ---: | --- |
| `0x00089B08` | 562 | sensor-stream framework: source/version/license unresolved |
| `0x00089890` | 464 | sensor-stream framework: source/version/license unresolved |
| `0x00041816` | 434 | shared quantized-neural runtime: attribution unresolved |
| `0x0008A1E0` | 422 | sensor-stream framework: source/version/license unresolved |

The former 294-byte `0x0002D460` heap leader left this table with the Goodix
`goodix_mem`/`GdMem` provenance resolution; it is vendor-gated, not unresolved.

The remaining large math/DSP bodies are deliberately not treated as attractive local rewrite
targets. Several lie next to Goodix or GoMore boundaries, where misclassification would recreate
vendor algorithms contrary to the source-admission policy.

## Latest completed closures

The former 280...308-byte tier is closed as four bounded R1 behaviors and one Goodix provider
function. Local code implements the distinct six-byte/238-byte `pb_tran` transport, pure
delayed-event scheduling, and health-settings transition planning; the BLE-thread body maps to the
existing shared envelope encoder. Heap/RTOS/timer/event/storage/live transport stay external, and
Goodix signal processing remains licensed-provider-only. See
[`FRONTIER-280-308-CORRELATION.md`](../correlation/FRONTIER-280-308-CORRELATION.md).

The former 314...328-byte tier is closed as two bounded R1 behaviors, the exact Nordic
`nrfx_saadc_irq_handler`, and two GoMore tensor operators. Local code clears six public cache
families and performs only the deterministic dual-channel trimmed/calibrated reduction. FlashDB,
sleep, GoMore, GXCAS sensor I/O, timing, logging, and persistence remain provider seams. See
[`FRONTIER-314-328-CORRELATION.md`](../correlation/FRONTIER-314-328-CORRELATION.md).

The former 334...342-byte tier is closed as two bounded R1 policies, two transparent GoMore
functions, and one transparent Goodix dlCom function. The local APIs encode the factory-test
thread envelope, periodic peripheral-link/advertising watchdog actions, recurrent tensor cell,
energy estimator update, and Goodix peak selection. See
[`FRONTIER-334-342-CORRELATION.md`](../correlation/FRONTIER-334-342-CORRELATION.md).

The former 348...354-byte tier is closed as four bounded R1 policies and one transparent GoMore
function. The local APIs encode a BLE thread envelope, redact the LTK diagnostic, plan safe
user-profile persistence/reinitialization, plan glasses-status lifecycle actions, and perform the
typed GoMore sensor-update orchestration without opaque code or state. See
[`FRONTIER-35X-CORRELATION.md`](../correlation/FRONTIER-35X-CORRELATION.md).

The former five-way 364-byte tier is closed without admitting vendor code. The twin heart-rate
and SpO2 RAM-cache merges share a clean-room scalar selection API; the final response orchestrator
and its 136-byte packet constructor now pin full-model CRC-16/MODBUS and generated-serial policy;
and the generic virtual-file handler is represented only by a pure export planner, with the
private-log reader and live sender excluded. The remaining `0x00036590` body is a quantized
recurrent-runtime helper reached solely inside the already gated Goodix dlCom graph and therefore
joins that licensed-provider boundary. See
[`SCALAR-HEALTH-RAM-CACHE-MERGE-CORRELATION.md`](../correlation/SCALAR-HEALTH-RAM-CACHE-MERGE-CORRELATION.md),
[`PROTOCOL-RESPONSE-CORRELATION.md`](../correlation/PROTOCOL-RESPONSE-CORRELATION.md),
[`EXPORT-STATE-MACHINE-CORRELATION.md`](../correlation/EXPORT-STATE-MACHINE-CORRELATION.md), and
[`GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md).

The former 372-byte leader at `0x00041A40` is now closed as R1 IQS7211E
ATI-error diagnostic policy. Its UInt32 sequence/cadence, exact 10,000-tick
gate, `0x56:0xE3` 21/24-channel read request, `0xFF` channel exclusion, stable
active-value order, and min/max behavior are implemented as staged pure
planning and summary APIs. Azoteq transport, CMSIS ticks, and logging remain
external. See
[`IQS7211E-ATI-AUDIT-CORRELATION.md`](../correlation/IQS7211E-ATI-AUDIT-CORRELATION.md).

The tied 372-byte leader at `0x00072C48` is now routed into the licensed Goodix
GH_HR provider boundary. Its sole caller is the already gated `pv_v1.1.0`
private-context initializer, immediately after allocation of the exact
0x158-byte subcontext. Under the later owner-authorized reduction, its bounded
buffer layout and defaults are now recreated locally with caller-owned
coefficient metadata; the primary initializer remains gated. See
[`GOODIX-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-PROVIDER-BOUNDARY.md).

The former 374-byte leader at `0x00096CC8` is now closed as the composite R1
PMIC-charged notification policy. Its two noncontiguous executable ranges,
strict 50/4,200 mV gates, UInt8 retry behavior, 200/409 ms recovery sequence,
ST mailbox completion decisions, and 5,120 ms post-charge schedule are pinned
in a pure planner. Nordic GPIO and CMSIS execution, the official ST25DVxxKC
driver, the separately recovered delayed-event loop, touch service, generic
device registry, and logging remain outside this implementation. See
[`PMIC-CHARGED-NOTIFICATION-CORRELATION.md`](../correlation/PMIC-CHARGED-NOTIFICATION-CORRELATION.md).

The former 376-byte leader at `0x00065F84` is now closed as the R1 firmware-event-loop delayed
timer callback. Its 64-slot saturating countdown, direct elapsed tag, due-event order, minimum
delay reschedule, 1,024-Hz tick conversion, and mismatched empty/`INT32_MAX` sentinel behavior are
pinned in a pure step. CMSIS-RTOS2, FreeRTOS critical sections, queues, timers, ticks, and logging
remain provider-owned. See
[`DELAYED-EVENT-TIMER-CORRELATION.md`](../correlation/DELAYED-EVENT-TIMER-CORRELATION.md).

The former 380-byte leader at `0x00040DE0` is now closed as the R1 HRV
current-RAM cache merge. Its sole public-history caller, metadata refresh,
24-hour sparse selection, inclusive window, current-hour exception, fixed
latest-value prefix, acknowledgement clamp, and mode restoration are pinned.
The clean-room adapter delegates encoding and emission and contains no HRV,
clock, storage, logging, or transport provider implementation. See
[`HRV-RAM-CACHE-MERGE-CORRELATION.md`](../correlation/HRV-RAM-CACHE-MERGE-CORRELATION.md).

The former 382-byte leader at `0x00049F0C` is now closed as R1 HRV timed-window
start policy. Its two callers, mode and health gates, exact 120-second delay,
3,450...3,599 catch-up exclusion, 208-byte workspace, one-shot registration,
and registration-failure rollback are pinned. A pure planner performs no live
time, timer, sensor-stream, logging, or biometric operation. See
[`HRV-TIMING-START-CORRELATION.md`](../correlation/HRV-TIMING-START-CORRELATION.md).

The former tied 394-byte leaders at `0x00040508` and `0x000446B4` are now a
two-function / 788-byte R1 heart-rate and SpO2 FlashDB merge closure. Exact
128-byte record gates, future/previous-day filtering, local hour/day mapping,
day/timezone flushes, four-byte scalar slots, first-record-wins duplicate
handling, and monotonic newest timestamps are pinned. One shared normalized
clean-room implementation supplies the product policy; FlashDB, time/calendar,
logging, transport, and biometric providers remain external. See
[`SCALAR-HEALTH-FLASH-MERGE-CORRELATION.md`](../correlation/SCALAR-HEALTH-FLASH-MERGE-CORRELATION.md).

The former 402-byte frontier leader at `0x00096AD0` is now a
one-function / 402-byte R1 PMIC charge-event policy closure. Its three direct callers, 24-byte dock-status template, exact charge
and temperature packing, embedded `2.2.6.0009` identity, `0x5A` event exception, and three thermal
bands are pinned. The local implementation is a pure planner; YHM2710 register access,
ST25DVxxKC mailbox transport, Nordic/CMSIS timers and events, and logging remain external. See
[`PMIC-CHARGE-EVENT-CORRELATION.md`](../correlation/PMIC-CHARGE-EVENT-CORRELATION.md).

The 402-byte FlashDB iterator callback at `0x00041438` is now closed as R1 HRV history merge
policy. Exact record length, future/window rejection, local day/hour mapping, day/timezone flush,
nonzero seven-byte slot insertion, duplicate handling, and newest-timestamp behavior are pinned.
Storage, time/calendar, logging, sending, and biometric providers remain external. See
[`HRV-FLASH-MERGE-CORRELATION.md`](../correlation/HRV-FLASH-MERGE-CORRELATION.md).

The former 406-byte GH_HR private-context initializer at `0x0006D204` is now reconstructed as
`goodix_primitives_hr_primary_context_create`. It validates the exact 36-byte configuration and
`pv_v1.1.0` ABI, owns both logical 0x150/0x158 contexts without stock globals, preserves the
recovered mode/rate/default rules and exact `262144.0f` / `0.0` tails, and replaces selectors
0/1/6 of the copied ROM constructor table with typed graph bindings. Its paired teardown releases
all 31 owner allocations and unwinds partial construction. Reproduce the stock extent and caller
pin with `python3 tools/evidence/summarize_r1_goodix_hr_init_boundary.py`.

The native 406-byte R1 battery runtime entry at `0x00031FD0` is now reconciled with the already
accepted 412-byte `0x00031FCC..<0x00032168` veneer-plus-body extent. Exact body/caller pins show
one runtime service, not a second algorithm. The existing clean battery controller is reused;
SAADC, YHM, clock, shared-power, and publication dependencies retain their independent ownership
gates. See [`ANALOG-BATTERY-CORRELATION.md`](../correlation/ANALOG-BATTERY-CORRELATION.md).

The former 416-byte leader at `0x0006210C` is now closed as a one-function / 416-byte R1 ATI calibration command closure
for opcode `0x91`. Its two executable ranges, 12-byte table, sole
dispatcher caller, eleven
subcommands, event masks, configuration words, provider observations, and response statuses are
pinned. The local pure planner performs no IQS7211E, Nordic/CMSIS, logging, queue, calibration,
or transport operation. See
[`ATI-CALIBRATION-COMMAND-CORRELATION.md`](../correlation/ATI-CALIBRATION-COMMAND-CORRELATION.md).

The 418-byte custom BAE8 service callback at `0x0005D5E0` is now product-routed. Its exact
indirect registration pointer, service configuration chain, event `2/3/6...9` split, EUS
reassembly handoff, and role/link-context planning are pinned. A pure local planner contains no
Nordic, BC, factory-accessor, logging, or unresolved event-helper implementation. See
[`BAE8-EVENT-ROUTER-CORRELATION.md`](../correlation/BAE8-EVENT-ROUTER-CORRELATION.md).

The former explicit seed `0x0007CCB4` is now closed as the 276-byte BAE8
connection-event handler through the next function at `0x0007CDC8`. Its sole
raw-observer event-`0x10` tail call, two CCCD value reads, conditional
notification flags, missing-context continuation, and 24-byte callback record
are pinned. The local planner performs no Nordic link-context operation,
SoftDevice SVC, CCCD helper call, log emission, or live callback dispatch. See
[`BAE8-CONNECTION-EVENT-CORRELATION.md`](../correlation/BAE8-CONNECTION-EVENT-CORRELATION.md).

The former explicit seed `0x00052B9C` is now closed as the noncontiguous R1
GAP observer registered at `0x000C45C0`. Its 3,184-byte envelope contains
1,728 executable bytes in two independently hashed segments plus the handler's
literal/diagnostic islands. The pure local plan covers all six recognized
connected, disconnected, PHY, and GATT-timeout events while leaving Nordic,
SoftDevice, advertising, timer, logging, and live dispatch operations external.
See [`GAP-EVENT-POLICY-CORRELATION.md`](../correlation/GAP-EVENT-POLICY-CORRELATION.md).

The former explicit seed `0x000461CC` is now closed as the R1 NFC charge-task
event policy. Its 1,156-byte envelope through `0x00046650` contains 662
executable bytes followed by exact literal and diagnostic data, and has one
system-task caller at `0x00092556`. The pure planner preserves all nine flag
routes, ST register values, fixed delays, three-attempt temperature-ID reset
decision, battery refresh cadence, and terminal intent without implementing
ST25, touch, battery, RTOS, watchdog, task, or logging providers. See
[`NFC-CHARGE-TASK-POLICY-CORRELATION.md`](../correlation/NFC-CHARGE-TASK-POLICY-CORRELATION.md).

The former explicit seed `0x00046B20` is now closed as the 140-byte R1
task-topology startup envelope, containing 100 executable bytes and ten
state-block literals. Its sole product-startup caller, nine indirect creator
calls, normal/factory group order, and raw priorities `8`/`0x35` are pinned.
The clean plan exposes only logical group intent; CMSIS-FreeRTOS, recovered
creator pointers, state blocks, and live task creation remain external. See
[`TASK-TOPOLOGY-STARTUP-CORRELATION.md`](../correlation/TASK-TOPOLOGY-STARTUP-CORRELATION.md).

The former explicit seed `0x00049B60` is now closed as the 142-byte R1 timing
heart-rate result callback. Its indirect Thumb registration pointer, inclusive
40...220 validity gate, health-gated eight-byte event-6 record, unconditional
`"hr"` stream cleanup, and timing-timer release tail are pinned. The compiled
pure plan accepts provider values, gate state, and firmware clock as bounded
inputs and performs no sampling, live event dispatch, timer operation, or
optical control. The same source also makes the previously classified adjacent
validity and one-shot callback contracts concrete. See
[`HR-TIMING-RESULT-CALLBACK-CORRELATION.md`](../correlation/HR-TIMING-RESULT-CALLBACK-CORRELATION.md).

The former explicit seeds `0x0004ABEC` and `0x0004ADA0` are now closed as the
230-byte one-shot and 252-byte timing SpO2 callbacks. Their indirect Thumb
registrations, lossless six-byte input record, inclusive 70...100 gate,
piecewise adjustment through the already transparent GoMore primitive,
zero-padded event-8 publication, unconditional stream cleanup, and timing-only
timer/completion flags are pinned. The planners perform no sampling, live
event dispatch, timer operation, or optical control. See
[`SPO2-RESULT-CALLBACKS-CORRELATION.md`](../correlation/SPO2-RESULT-CALLBACKS-CORRELATION.md).

The former explicit seeds `0x0004ED64` and `0x0004EE18` are now closed as the
72-byte factory accelerometer result callback and 32-byte `AT^BAT_ADC` handler.
Their indirect callback/command-table Thumb pointers, exact result and format
strings, every local callsite, fixed 30-triplet accelerometer layout, fivefold
decimation, battery accessor order, and fixed return value are pinned. The
compiled plans perform no stream registration, sensor or battery read, text
emission, or live factory command routing. See
[`FACTORY-ACC-BATTERY-DIAGNOSTICS-CORRELATION.md`](../correlation/FACTORY-ACC-BATTERY-DIAGNOSTICS-CORRELATION.md).

The former explicit seeds `0x0004F4A4`, `0x0004F4D4`, and `0x0004F524` are
now closed as the three `AT^PMIC_ISNS`, `AT^PMIC_OFF`, and `AT^PMIC_READ`
factory handlers. Their 162 executable bytes, 244-byte complete envelopes,
fixed command-table pointers, provider call order, power-recovery packing,
and handler returns are pinned. The corrected `PMIC_READ` contract reads only
register 9 and formats it followed by nine zeros. `PMIC_OFF` remains an inert
plan with no persistence/thread executor or live destructive route. See
[`FACTORY-PMIC-HANDLERS-CORRELATION.md`](../correlation/FACTORY-PMIC-HANDLERS-CORRELATION.md).

The former explicit seeds `0x00050614`, `0x000507CC`, and `0x00050804` are
now closed together with the real `0x000350E0` target behind the first seed.
The four manual supplements total 138 executable bytes and pin the register-3
charging-event mask policy, its branch-only veneer, and the complete read/write
dispatch bodies behind the existing public veneers. All are independently
compiled in `reconstructed/yhm2710/`; no opaque transport is admitted. See
[`YHM2710-OMITTED-TRANSPORT-ENTRIES-CORRELATION.md`](../correlation/YHM2710-OMITTED-TRANSPORT-ENTRIES-CORRELATION.md).

The former 424-byte leader at `0x00032198` is now closed as the R1 EUS receive fragment
reassembler and outer Castagnoli-CRC gate. The exact body, sole channel-2 event caller, five-byte
header, 239-byte payload, sequence and logical-size bounds, allocator split, and terminal behavior
are pinned. The existing per-link clean implementation preserves valid trains while deliberately
rejecting stock duplicate/discontinuous/repeated-checksum ambiguities. See
[`EUS-RX-REASSEMBLY-CORRELATION.md`](../correlation/EUS-RX-REASSEMBLY-CORRELATION.md).

The former 430-byte leader at `0x00069128`, the adjacent 326-byte first statistics block, and their
exclusive 40-byte stage lookup helper are now a three-function / 796-byte GoMore sleep-stage
statistics closure. Exact bodies, finalizer calls, helper caller census, 0.5-minute epoch scale,
output-block widths, and denominator behavior are pinned. All three functions are now source-admitted
as bounded transparent C; the interval block preserves leading/middle/trailing awake accounting,
unknown-nonzero sleep behavior, efficiency arithmetic, and the seven-field invalid sentinel. See
[`GOMORE-SLEEP-STAGE-STATISTICS-PROVIDER-BOUNDARY.md`](../boundaries/GOMORE-SLEEP-STAGE-STATISTICS-PROVIDER-BOUNDARY.md).
The finalizer's 580-byte score consumer at `0x0006778C` is now source-admitted as well, with typed
19-float input, exact raw-bit band boundaries, double-tanh duration shaping, wake penalty,
REM/deep weights, final clamp, and the stock exact-540-minute zero-parameter defect.
The 444-byte sleep peak-rate interpolator at `0x00074D60` is likewise source-admitted: its only
algorithm dependency is the already-local valid-anchor finder, and its exact 60-BPM defaults,
invalid-marker handling, spacing rates, and grid interpolation use bounded caller spans.
The 280-byte caller at `0x00088AAC` is now source-admitted too, closing spacing invalidation,
mode-specific 6/9/12-update cadence, 90-float rotation, normalized tail generation, and counter state.
The adjacent 110-byte carryover leaf at `0x00076502` is source-admitted with bounded suffix
compaction, exact above-749 retention, subtraction by 750, and high-bit invalid-marker preservation.
The 112-byte valley-candidate leaf at `0x00064A28` is source-admitted with bounded 256-value input,
zero-filled twelve-index output, asymmetric local-minimum comparison, and strict positive curvature.
The 128-byte history-advance leaf at `0x0008EE3A` is source-admitted over a typed 396-byte state,
closing the one/two-block 25-sample shift and the greater-than-two full-reset lifecycle.

The former tied 430-byte leaders at `0x0004D654` and `0x0004DA28` are now a symmetric
two-function / 860-byte R1 phone/glasses connection-role assignment closure. Both bodies, caller
sets, shared role state, invalid sentinel, empty-slot assignment, repeat and occupied behavior,
and role publication are pinned. The local implementation returns an explicit cross-role conflict
instead of invoking the stock fatal assertion; Nordic state, logging, and event delivery remain
external. See
[`CONNECTION-ROLE-ASSIGNMENT-CORRELATION.md`](../correlation/CONNECTION-ROLE-ASSIGNMENT-CORRELATION.md).

The former 434-byte leader at `0x00041816` is now isolated as a shared quantized-neural provider
boundary. Its complete body, lack of direct callers, constructor, exact Thumb pointer, and ten
constructor calls from two GoMore and two Goodix model-graph builders are pinned. The mixed
topology establishes provider ownership but not which provider or library supplied the code, so
the executor remains blocked under `unknown_shared_quantized_neural_runtime_candidate`; OpenR1
does not recreate it or substitute a merely similar generic pooling implementation. See
[`QUANTIZED-POOLING-PROVIDER-BOUNDARY.md`](../boundaries/QUANTIZED-POOLING-PROVIDER-BOUNDARY.md).

The former tied 434-byte leader at `0x0008DD90` is now part of a three-function / 850-byte R1
validated-sleep delivery and persistence closure. The 3,599/3,600-second boundary, wrapping
duration behavior, private storage event `0x2000`, direct queue-failure fallback, append-success
automatic-sync argument `6`, two write attempts, rollover, and 3,888-byte maximum are pinned.
Local planners and the bounded journal preserve product behavior while keeping the generic event
and logging frameworks external; the stock destructive reset is replaced by an explicit error.
See [`VALIDATED-SLEEP-DELIVERY-CORRELATION.md`](../correlation/VALIDATED-SLEEP-DELIVERY-CORRELATION.md).

The former 464-byte leader at `0x0004E258` is now closed as an R1 legacy command-frame router.
Its complete body, sole caller, 36-byte workspace, byte-2 opcode, all 23 handler destinations,
recognized/unknown return convention, and special `0x88` pair-auth response route are pinned.
The clean-room implementation performs bounded pure route selection only: it invokes no recovered
address, mutates no pairing state, and does not change any destination handler's independent
ownership gate. See
[`LEGACY-COMMAND-DISPATCH-CORRELATION.md`](../correlation/LEGACY-COMMAND-DISPATCH-CORRELATION.md).

The tied 464-byte body at `0x00089890` and noncontiguous 422-byte timer callback at `0x0008A1E0`
are now source-gated with the already blocked sensor-stream unregistration routine. Their
three-function / 1,448-byte generic framework boundary
pins listener registration/removal, shared-buffer resizing, optional provider open/close hooks,
and `1024 / rate` timer policy. No attributable source or license has been identified, so openR1
does not clone the framework and continues to bind typed providers directly. See
[`SENSOR-STREAM-FRAMEWORK-BOUNDARY.md`](../boundaries/SENSOR-STREAM-FRAMEWORK-BOUNDARY.md).

The former 464-byte leader at `0x0004CCCC` now forms a three-function / 550-byte R1 target-glasses
peer-address policy closure with its validity check and three-slot accessor. The pure local policy
rejects all-zero/all-`FF` configured targets, matches either valid side, and preserves the stock
acceptance behavior when no target is configured or peer lookup is unavailable. Nordic peer data,
disconnect/advertising actions, and logging remain external, and this compatibility helper is
explicitly not an authorization boundary. See
[`PEER-TARGET-POLICY-CORRELATION.md`](../correlation/PEER-TARGET-POLICY-CORRELATION.md).

The former 466-byte leader at `0x00077430` now forms a four-function / 620-byte R1 NFC dock
policy closure with its 23-byte advertisement helper and field-seen getter/setter. Exact bodies,
callers, state pointers, identity header, mailbox-control gate, heartbeat counter, cached-delay
threshold, strict ADC comparison, 4/60-second selection, and delayed `55 04` control action are
pinned. The local implementation is a bounded pure planner; ST mailbox status/transport, Nordic
delayed execution, ADC acquisition, and logging remain external. See
[`NFC-DOCK-POLICY-CORRELATION.md`](../correlation/NFC-DOCK-POLICY-CORRELATION.md).

The former 472-byte leader at `0x0008DA24` is now the R1 compact-to-wire sleep synchronization
packet builder. Its sole caller, exact body, compact stage encoding, adjacent-type merge, 32-byte
header, legacy cutoff, timezone policy, and future-end correction are pinned. The local builder is
bounded and pure; allocation, clock, transport, acknowledgement, logging, and flash remain
external. See [`SLEEP-SYNC-PACKET-CORRELATION.md`](../correlation/SLEEP-SYNC-PACKET-CORRELATION.md).

The former tied 472-byte leader at `0x00051AA0` now forms a four-function / 498-byte R1 BLE
connection-parameter policy closure with its strict maximum-interval classifier and phone/glasses
handle accessors. Exact event IDs, literals, caller sets, initial interval pairs, role status
updates, and 4/2,000 ms mismatch retry delays are pinned. The local implementation returns pure
actions; Nordic GAP/SoftDevice behavior, the generic timer loop, logging, and the delayed callback
remain external. See
[`CONNECTION-PARAMETER-POLICY-CORRELATION.md`](../correlation/CONNECTION-PARAMETER-POLICY-CORRELATION.md).

The former 480-byte frontier leader at `0x0003D45C` is now part of an eleven-function / 1,756-byte
R1 wear-fusion closure. Four formerly unproven callback seeds (`0x0003CE1C`, `0x0003D0FC`,
`0x0003D150`, and `0x0003D1B8`) are exact manual supplements. Body hashes, direct callsites,
callback pointers, bounded five-slot history, 3,000/7,000-tick plans, the three internal states,
motion/IR/living thresholds, strict boundaries, counter windows, sleep preservation, and distinct
public mappings are pinned. `r1` implements only bounded observation-to-state/action policy;
Goodix, motion acquisition, CMSIS time, and the unresolved sensor-stream framework remain external.
See [`WEAR-FUSION-CORRELATION.md`](../correlation/WEAR-FUSION-CORRELATION.md).

The former unproven ten-byte callback at `0x0003E00E` is now an exact manual supplement. Its
registered pointer at `0x0003D7C4` and tail call to SDK-bundled `SEGGER_RTT_Write` are pinned;
transparent C returns a channel-0 write plan without performing RTT I/O. See
[`FRONTIER-SUB32-CORRELATION.md`](../correlation/FRONTIER-SUB32-CORRELATION.md).

The former largest unknown at `0x00072DCC` is now included in a 30-function / 5,126-byte Goodix GH_NADT accumulation/decision
closure. Eight remaining direct descendants of provider root `0x0006E838` and all of their
formerly unclassified descendants have no outside non-Goodix caller. Two compiler-shaped entries
have exact composite segment maps; all 30 bodies and direct callsites are pinned. No private
constant or formula is admitted. See
[`GOODIX-NADT-ACCUMULATION-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-ACCUMULATION-PROVIDER-BOUNDARY.md).

The tied 494-byte unknown at `0x00030178` belongs to a seven-function / 1,098-byte Goodix GH_NADT peak-mask
helper closure. The only entry from outside that chain is `0x0006E8E6` in the
still-gated GH_NADT root `0x0006E838`. All seven helper entries now compile transparently: the
five-entry / 918-byte final batch replaces transient allocations with caller-owned scratch while
preserving packed extrema, plateau, row-selection, newest-index, and threshold-history behavior. See
[`GOODIX-NADT-PEAK-MASK-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-PEAK-MASK-PROVIDER-BOUNDARY.md).

The other tied 494-byte unknown at `0x0007C52C` is part of a two-entry / 498-byte R1 compiled-default
restore closure. The formerly unproven four-byte veneer `0x00042BBE` is now an exact manual
supplement and is reached only through internal storage event `0x2005`. Its 59-record table at
`0x0009A0F8..<0x0009A432` contains identity match keys, so the table is hash-pinned but not
redistributed; transparent C accepts caller-owned typed records and returns a plan, while the live
persistent restore remains disabled. See
[`NV-COMPILED-RESTORE-CORRELATION.md`](../correlation/NV-COMPILED-RESTORE-CORRELATION.md).

## Prior completed closures

The former largest unknown at `0x0002B6E0` is now a one-function / 514-byte Goodix register-profile
decoder boundary. Its sole entry is already gated branch thunk `0x0002A810`, reached from the
provider register/configuration parser at its profile terminator. No private eight-channel profile
layout, parser, fatal-loop behavior, or live register I/O is admitted. See
[`GOODIX-REGISTER-PROFILE-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-REGISTER-PROFILE-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x00088E80` was a one-function / 518-byte Goodix GH_NADT
channel-quality boundary. Its sole callsite `0x0006E916` lies in the pinned GH_NADT root
`0x0006E838`, identified as `GH_NADT_pre v1.0.2.0 / 548d894d`; no outside caller exists. Its
six masked flag rules and exact three-component logistic score now compile from bounded C. See
[`GOODIX-NADT-QUALITY-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-QUALITY-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x000335B4` completes the two-function / 856-byte packed-channel
decoder closure. Its sole-caller decoder at `0x00061DA4` is
`goodix_primitives_spo2_channel_records_assemble`; all three calls now reach
`goodix_primitives_spo2_channel_scale_decode`. The stock RAM table banks and `pow` dependency are
explicit bounded bindings, and both direct and width-packed formulas compile locally. See
[`GOODIX-CHANNEL-DECODER-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-CHANNEL-DECODER-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x00037B80` is the 554-byte NADT auxiliary
state classifier called only by the still-bounded window classifier at
`0x000856EC`. It now compiles as
`goodix_primitives_nadt_auxiliary_state_classify`: the final-50 sample span,
five configuration fields, result/mode/latch state, diagnostics, two 25-entry
extrema banks, and square-root dependency are explicit. Tests pin the exact
range/deviation/extrema clustering and consecutive-window transition. See
[`GOODIX-NADT-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x000856EC` is the 1,154-byte compiler-scattered NADT window
classifier. It now compiles as `goodix_primitives_nadt_window_classify` with four bounded metric
lanes, separate tail/range histories, explicit persistent state and diagnostics, the exact
rounded square-root energy and raw-bit ratio gates, and typed primary/auxiliary/alternate
classifier bindings. Tests cover every transition family and extent rejection. See
[`GOODIX-NADT-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-PROVIDER-BOUNDARY.md).

The former largest Goodix residual at `0x00047240` is the 3,240-byte compiler-scattered NADT
primary-signal classifier and sole algorithm dependency of the now-local window classifier. It
now compiles as `goodix_primitives_nadt_primary_signal_classify` with paired bounded Int32 spans,
typed configuration/state/diagnostics, and a fixed workspace replacing every stock allocation.
Tests pin its disabled, near-zero transition, 100-sample quarter-range, and malformed-input paths.
See [`GOODIX-NADT-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-PROVIDER-BOUNDARY.md).

The former 1,162-byte NADT harmonic-candidate selector at `0x00035850` now compiles as
`goodix_primitives_nadt_harmonic_candidates_select`. Its exact three-lane harmonic search uses a
fixed caller workspace in place of six transient allocations and supplies the final local
dependency of `goodix_primitives_nadt_spectral_peak_prepare`. See
[`GOODIX-NADT-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-PROVIDER-BOUNDARY.md).

The former 1,294-byte GH_NADT streaming root at `0x0006E008` now compiles as
`goodix_primitives_nadt_stream_process`. Typed plan/state records replace the private runtime and
configuration globals, fixed caller histories replace the stock RAM banks, and the complete
sample-preparation, optical-transform, rolling-statistics, window-dispatch, compaction, and result
path reaches already-local dependencies. Tests pin cadence, first-window dispatch, history
geometry, result flags, uninitialized state, and malformed-input behavior. See
[`GOODIX-NADT-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-PROVIDER-BOUNDARY.md).

The former 1,240-byte GH_SPO2/dlCom stream helper at `0x0003113C` now compiles as
`goodix_primitives_spo2_stream_accumulate`. It exposes four optical filter lanes, adaptive scale
state, packed histories, decimal-residual/motion processing, percentile histories, and caller
scratch while retaining the first-window cleanup/replay and rolling update paths. Tests cover the
fill boundary, replay geometry, subsequent percentile update, packed lane cadence, and preflight
rejection. See
[`GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md).

The former 1,382-byte HRV root at `0x0006D51C` now compiles as
`goodix_primitives_hrv_process`. It exposes channel geometry, counted signal/motion/quality
histories, feature/extrema state, candidate and quality policy, fallback state, and reference-rate
recovery; `0x00032808` now compiles as the typed `goodix_primitives_hr_decision_update` state machine. Tests cover a full
periodic candidate window, exact rate/quality emission, invalid-input clearing and quality 25,
history updates, and preflight no-mutation. See
[`GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x0008EA0C` now compiles as the bounded
`gomore_primitives_sdk_auth_parse`. Its two exact executable ranges, sole callsite `0x0006B38A`,
`sdkAuth` diagnostics, dispatch-table use, R1 dual-AES seam, and toolchain `strtok` dependency are
pinned. The sole caller at `0x0006B27C` compiles as typed
`gomore_primitives_auth_parameters_setup`; no outside caller exists. Both 32-byte decrypt keys,
message matching, four field parsers, and three validators are explicit caller bindings, so no
stock key or authorization material is admitted. See
[`GOMORE-AUTH-PARSER-PROVIDER-BOUNDARY.md`](../boundaries/GOMORE-AUTH-PARSER-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x000442F4` is closed with its 32-byte builder-reset helper as a
two-function / 578-byte R1 SpO2 synchronization-flush boundary. Five SpO2
RAM/flash/offline/history paths call each routine; already product-routed offline merge
`0x000448B0` and history sync `0x0008CD60` are among them. The flush owns only future-record
rejection, sparse 24-hour packed-value serialization, optional acknowledgement context, and
reset-after-attempt behavior. FreeRTOS allocation, the unresolved time/calendar backend, topic
selector, transport sender, Nordic logging, and Goodix algorithms remain external. See
[`SPO2-SYNC-FLUSH-CORRELATION.md`](../correlation/SPO2-SYNC-FLUSH-CORRELATION.md).

The former co-largest unknown at `0x0004011C` is closed with its 32-byte builder-reset helper as a
two-function / 578-byte R1 heart-rate synchronization-flush boundary. Five heart-rate
RAM/flash/offline/history paths call each routine; already product-routed offline merge
`0x00040700` and history sync `0x0008C150` are among them. The flush owns only future-record
rejection, sparse 24-hour UInt32 packet serialization, optional acknowledgement context, and
reset-after-attempt behavior. FreeRTOS allocation, the unresolved time/calendar backend, topic
selector, transport sender, Nordic logging, and all biometric algorithms remain external. See
[`HR-SYNC-FLUSH-CORRELATION.md`](../correlation/HR-SYNC-FLUSH-CORRELATION.md).

The former largest unknown at `0x00034070` is closed with the adjacent type-0 veneer as a
two-function / 560-byte R1 BLE transmit-queue producer boundary. The envelope layout, dispatch
types, 90-percent queue warning, raw timeout 100, worker flag 1, and failure-free path are pinned.
FreeRTOS heap, CMSIS queue/thread operations, Arm `memmove`, logging, the BLE worker, and unresolved
connection accessors remain external. See
[`BLE-TX-QUEUE-DISPATCH-CORRELATION.md`](../correlation/BLE-TX-QUEUE-DISPATCH-CORRELATION.md).

The registration body at `0x00089890`, timer callback at `0x0008A1E0`, and unregister body at
`0x00089B08` now form a three-function / 1,448-byte unresolved sensor-stream framework boundary.
The contiguous register body, two exact callback ranges, four exact unregister ranges, indirect
callback pointer, and direct caller sets are SHA-pinned. The code adds/removes and dispatches
named listeners, defers removal during dispatch, recomputes rates, resizes a shared buffer,
retimes at `1024 / rate`, and invokes optional provider open/close hooks. Cross-domain callers and
absent source correlation prevent R1 ownership attribution; no local registry implementation is
admitted. See
[`SENSOR-STREAM-FRAMEWORK-BOUNDARY.md`](../boundaries/SENSOR-STREAM-FRAMEWORK-BOUNDARY.md).

The former largest unknown at `0x00046650` is now a one-function / 578-byte R1 touch-task dispatcher boundary.
Its seven exact executable segments, sole direct callsite `0x00092822`,
event-bit map, open/close ordering, diagnostic-only cases, and six factory marker transactions are
SHA-pinned. IQS7211E controller/register behavior stays in the pinned provider references; Nordic
and CMSIS-FreeRTOS primitives, shared power, logging, and unresolved hardware wrappers remain
external. See
[`TOUCH-TASK-DISPATCHER-CORRELATION.md`](../correlation/TOUCH-TASK-DISPATCHER-CORRELATION.md).

The former largest unknown at `0x0004101C` is now closed with its 32-byte builder-reset helper as
a two-function / 616-byte R1 HRV synchronization-flush boundary. Five HRV RAM/flash/offline/history
paths call both routines; already product-routed offline merge `0x00041638` and history sync
`0x0008C750` are among them. The flush owns only future-record rejection, sparse 24-hour packet
serialization, optional acknowledgement context, and reset-after-attempt behavior. FreeRTOS
allocation, the unresolved time/calendar backend, topic selector, transport sender, Nordic
logging, and all biometric algorithms remain external. See
[`HRV-SYNC-FLUSH-CORRELATION.md`](../correlation/HRV-SYNC-FLUSH-CORRELATION.md).

The former largest unknown at `0x000717AC` / 602 bytes is now routed into the licensed GoMore
provider gate. Its sole direct caller is already gated sleep-filter initializer `0x00071D62` at
callsite `0x00071D76`, and it has no outside caller. Its trigonometric coefficient-design behavior
depends only on separately source-routed Arm toolchain `cosf`, `sinf`, and `powf`. The complete
body and caller set are pinned, but no private formula, generated coefficients, or substitute
implementation is admitted. With the later authorization-parser closure, the complete GoMore
gate is now 245 entries. See
[`GOMORE-IIR-DESIGNER-PROVIDER-BOUNDARY.md`](../boundaries/GOMORE-IIR-DESIGNER-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x00059670` is now closed with its initialization and sector-count
helpers as a three-function / 876-byte R1 `log.bin` circular-page writer boundary. The writer's
sole direct caller is periodic-persistence callsite `0x000914D2`. It accepts at most 4,096 bytes,
advances before a cross-page write, wraps over the twelve configured sectors, erases a selected
nonempty page, and pre-erases the following nonempty page. Partition and device lookup remain in
pinned FAL 0.5.99/FlashDB 2.0.0; physical flash operations remain configured-provider callbacks;
Nordic logging, the structured-log encoder/cache, and the composite private-log exporter and
transport remain separate. No raw mutation or private-log sender is exposed. See
[`LOG-BIN-WRITER-CORRELATION.md`](../correlation/LOG-BIN-WRITER-CORRELATION.md).

The former largest unknown at `0x00046FD4` is now closed with fifteen related functions as a
16-function / 1,802-byte R1 structured-log record and live-cache boundary. Twelve formerly
unclassified Ghidra functions / 1,720 bytes and four exact manual functions / 82 bytes cover the
two bounded argument encoders, their public facades, circular-cache operations, mode/threshold
configuration, timestamp seam, and 4,096-byte persistence orchestration. The format-aware encoder
has public facade `0x00091638` as its sole caller; sibling typed encoder `0x00041D30` has
`0x000915A8` as its sole caller, and both converge on the same two-caller cache append routine.
Nordic's separately source-routed logging frontend, Arm runtime, CMSIS-FreeRTOS/FreeRTOS,
unresolved clock/calendar and device-registry providers, and the `log.bin` writer/export sender
remain external. No raw private-log export is exposed. See
[`STRUCTURED-LOG-CACHE-CORRELATION.md`](../correlation/STRUCTURED-LOG-CACHE-CORRELATION.md).

The former largest unknown at `0x00034194` is now closed with six recursive relatives as a
seven-function / 1,964-byte extension of the Goodix GH_NADT boundary. The exact generated-model
chain `0x0006E838 -> 0x000968C4 -> 0x0002907C -> 0x00037890 -> 0x00034194` begins at the
authenticated NADT preprocessing core's sole callsite to the new root. None of the root's private
descendants has an outside caller. The closure also pins the normalization, tensor projection,
tensor-combine, and generated-model executor bodies while keeping the separately gated Goodix
descriptor helper, sensor-algorithm heap, and Arm runtime outside this supplemental census. The
complete NADT boundary is now 58 functions / 19,274 bytes and, with the later packed-channel,
NADT-quality, register-profile, peak-mask, accumulation/decision, GH_HR initializer, dlCom
quantization, peak-selector, and channel-decimation closures, the complete Goodix gate is 395
entries. The outer `0x00037890` seven-stage topology is now reconstructed with typed
node/subgraph bindings. The nested `0x00034194` runtime is now
`goodix_primitives_nadt_generated_subgraph_execute`, with all nineteen
operators, fixed shapes/banks, quantization range, scalar descriptor, and
branch handoff explicit; only the operator/model contents remain typed
bindings. See
[`GOODIX-NADT-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x0007DA30` was closed with eight recursive descendants as a
nine-function / 2,360-byte GoMore energy-model boundary. Dispatcher `0x0002F488` is called at
exactly three sites by now source-admitted energy output producer `0x0005F56C` and has no other caller.
Its private mode families, table-driven estimator, interpolation, projection, scaling, and state
helper are all body- and caller-pinned. Existing GoMore helpers and Arm runtime math remain
excluded from the supplemental census. The complete GoMore gate was 243 entries at that stage.
Under the later owner-authorized reduction, all nine bodies, formulas, and 81 table values plus
the complete 2,102-byte producer are now transparent C; the paragraph above records the historical
frontier classification. See
[`GOMORE-ENERGY-MODEL-PROVIDER-BOUNDARY.md`](../boundaries/GOMORE-ENERGY-MODEL-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x00095828` is now source-admitted as
`goodix_primitives_nadt_signal_confidence_update`; its sole direct caller is authenticated
preprocessing core `0x0006E838` at `0x0006EA88`. The typed entry consumes the already-local
dual-window feature result, replaces the 496-byte stock allocation with a 124-Float32 caller
workspace, and preserves rate selection/blending, variation-mode counters, rolling acceptance,
hold recovery, mean, and Gaussian confidence probability. The historical nineteen-function /
3,246-byte graph remains hash- and caller-pinned; two small statistic/conversion helpers are shared
with adjacent signal routines, so outside-caller exclusivity is not claimed for those helpers. See
[`GOODIX-NADT-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x0004387C` is now closed with three private initialization bridges
as a four-function / 1,128-byte extension of the Goodix GH_SPO2/dlCom boundary. Exact chain
`0x0006EC28 -> 0x0006EB94 -> 0x0002F624 -> 0x00036C26` reaches the graph builder twice through
the scatter-loaded continuation at `0x00099014`. The graph body, all direct caller sets, and the
noncontiguous bridge segments are pinned. Shared descriptor constructors called by both GoMore
and Goodix graphs remain excluded from this provider census. At that stage the complete Goodix
gate contained 323 entries; no graph topology or model behavior is recreated locally. See
[`GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x00036F88` is now source-admitted as
`goodix_primitives_nadt_output_state_select`. Its sole caller is preprocessing core `0x0006E838`
at callsite `0x0006EA7A`; its only direct callees are Arm toolchain floating-point helpers. The
typed entry exposes rate history, thresholds, flags, signal/persistence inputs, retained rate, and
the exact `0/1/2/12/21` state latch while preserving the 65..100 output clamp and kinds 1/2/5.
See
[`GOODIX-NADT-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x0006E838` is now source-admitted as the retail SpO2 root
`goodix_primitives_spo2_calc`. The typed root composes its embedded, already reconstructed NADT
channel assembly, accumulation, spectral, feature, quality, inference, selection,
confidence, and result stages in the exact recovered order. It preserves both failure encoders,
the accumulation-readiness return, the 25-frame cadence, quartic transform, three bit-range
adjustment rules, and inference return status. Five stock heap temporaries are replaced by bounded
caller-owned records, summaries, and one-lane output spans. See
[`GOODIX-NADT-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x0007DD58` is now source-admitted as
`goodix_primitives_nadt_alternate_state_classify`. Its two callsites remain in the byte-pinned
NADT window classifier. The fixed 200-sample entry preserves its range/sample gate, paired
shared-state autocorrelation transforms, signed extrema and 800-amplitude filters, peak-quality
update, alternating interval ordering, regularity thresholds, and consecutive-match transition.
Five stock allocations are replaced by one bounded caller workspace. See
[`GOODIX-NADT-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x00034CBC` is now source-admitted as
`goodix_primitives_hr_extrema_tracker_update`. Its sole caller remains the GH_HR core at
`0x0006D5F2`. The local entry preserves full-buffer and period-boundary behavior, the exact
rise/fall/equality latch, paired extrema positions and values, amplitudes, spans, and optional
four-sample cardinal-spline refinement. Static curve coordinates are explicit bindings and the
41-point interpolation bank is caller-owned. See
[`GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x0006138C` is now source-admitted with five private helpers as a
six-function / 1,890-byte GoMore activity-state window classifier. Its only direct caller is the
now-source-admitted GoMore output orchestrator at `0x0005FF94`; every helper is private to the closure.
Four executable segments, three embedded eight-byte `TBB` tables, the adjacent literal pool, and
all exact caller sets remain pinned. The transparent reconstruction includes the 1,028-byte state,
25/250-sample decision process, statistics, thresholds, transitions, adaptive holds, outputs, and
bounded representation of the stock 26/27-sample metadata overwrite. See
[`GOMORE-ACTIVITY-STATE-PROVIDER-BOUNDARY.md`](../boundaries/GOMORE-ACTIVITY-STATE-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x0002874C` is now closed with paired 892-byte and 884-byte GoMore
sleep-classifier graph builders, their 236-byte family selector, and three allocator wrappers.
All six functions / 2,188 bytes are tied to the pinned indirect floating-point executor, exact
constructor table at `0x000BCF40`, and the two 21,824-byte classifier model regions. The separate
Goodix-rooted builder `0x0004387C` is deliberately excluded from the GoMore closure and is now
separately admitted to the Goodix GH_SPO2/dlCom boundary despite sharing constructors. No local
graph topology, descriptors, model weights, or inference runtime is admitted. See
[`GOMORE-SLEEP-GRAPH-PROVIDER-BOUNDARY.md`](../boundaries/GOMORE-SLEEP-GRAPH-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x0006DB5C` is now closed as the 926-byte Goodix
`GH_HRV_pre` lifecycle initializer. It accepts only the exact 24-byte configuration and private
ABI tag `pv_v1.1.0`, and its sole direct caller is the already gated HRV output wrapper at
`0x0006DF14`. The complete nine-function / 1,288-byte lifecycle includes init, cleanup, two
dispatcher wrappers, configuration/version helpers, and exact identity
`GH_HRV_pre_pv_v1.0.1.0_ed953ff3`. Seven formerly unclassified functions / 1,154 bytes are now
provider-gated; OpenR1 does not recreate the private state, buffer allocator, or calibration
logic. See [`GOODIX-HRV-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-HRV-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x0007BD68` is now closed with the 474-byte report builder and four
manual functions omitted by Ghidra as a six-function / 1,954-byte R1 product closure. The exact
system-`0x11` handler at `0x00084150` and route
`0x000841FA -> 0x0007C450 -> 0x0007BD68` enforce command 2, 116 bytes, and nonzero CRC before
the fill-only merge; report sender `0x0007BBE8` reaches outbound wrapper `0x000839B4` at
`0x0007BC22`. The local implementation is a bounded pure report, outbound-response, envelope-route,
and merge planner;
it performs no BLE send or persistent commit, and the normal dispatcher continues to refuse the
identity-bearing `nvRecover` command. See
[`NV-RECOVERY-CORRELATION.md`](../correlation/NV-RECOVERY-CORRELATION.md).

The formerly unproven curated sleep seed at `0x0008F954` is now closed as an independent 118-byte
stored-sleep report callback manually omitted by Ghidra's function inventory. Exact Thumb pointer
`0x0008F955` at `0x0008B830` registers it with iterator `0x0005B39C`; the callback rejects a null
private context, skips synchronization flag `1`, and otherwise forwards the context UInt8 report
type and UInt16 stage count to packet builder `0x0008DA24`. The local implementation is a pure
typed intent and exposes no live flash, allocation, packet, marker, or BLE operation. See
[`STORED-SLEEP-REPORT-CALLBACK-CORRELATION.md`](../correlation/STORED-SLEEP-REPORT-CALLBACK-CORRELATION.md).

The formerly unproven GATT-cache seeds `0x0008A93C` and `0x0008AA08` are now exact manual
supplements for Nordic SDK 17.1.0 `service_changed_pending_set` and
`service_changed_send_in_evt`. Ghidra had folded each independent body into a noncontiguous
caller; `0x000890CC` is corrected to the distinct `sc_send_pending_handle` callback whose tail
call enters the latter body. OpenR1 already compiles the pinned `gatt_cache_manager.c` and
`gatts_cache_manager.c`; no local Peer Manager implementation is introduced. See
[`NORDIC-GATT-CACHE-CLOSURE.md`](../closures/NORDIC-GATT-CACHE-CLOSURE.md).

The formerly unproven DFU seed `0x00052050` is now the exact 40-byte Nordic
`ble_dfu_buttonless_bootloader_start_finalize` function from `ble_dfu.c`. Ghidra folded it into
the noncontiguous prepare wrapper even though `0x0005207C` tail-calls the independent prologue at
`0x00052050`. The source is already part of the pinned unbonded buttonless-DFU build; see
[`NORDIC-BUTTONLESS-DFU-CLOSURE.md`](../closures/NORDIC-BUTTONLESS-DFU-CLOSURE.md).

The formerly unproven GATT-cache seed `0x000578F4` is now the exact 54-byte Nordic
`car_update_pending_handle` callback. It is registered through Thumb pointer `0x000578F5` at
`0x00094ADC`, which explains the absence of a direct branch caller. The pinned Peer Manager source
already supplies the implementation; see
[`NORDIC-GATT-CACHE-CLOSURE.md`](../closures/NORDIC-GATT-CACHE-CLOSURE.md).

The former largest unknown at `0x0006CCC0` is now closed as a 984-byte Goodix
GH_SPO2/dlCom input diagnostic formatter. Its sole direct caller is the already gated Goodix
wrapper `0x0002C944` at `0x0002CA2C`, immediately after the wrapper invokes processing root
`0x0006C6A8`. The formatter emits provider algorithm configuration and per-sample PPG, enable,
accelerometer, and gyroscope fields through optional callbacks. The complete body, sole caller,
and exact diagnostic strings are pinned. It now compiles as
`goodix_primitives_spo2_input_diagnostics_emit`: bounded typed sinks replace the private variadic
callback ABI while preserving the two output routes and their separately sampled heap diagnostic.
It remains provider support and is not treated as product telemetry. See
[`GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x0007F2B0` is now closed as the 1,052-byte R1 Peer Manager event
policy callback. R1 initializer `0x0004E4B4` registers exact Thumb pointer `0x0007F2B1` through
Nordic `pm_register`; the callback delegates standard event/error and flash-clean behavior to
Nordic SDK 17.1.0 before applying product connection, repairing, and advertising policy. OpenR1
preserves `allow_repairing = true` while keeping bond state separate from product authorization,
performs no whitelist promotion, and excludes the recovered LTK-printing helper. See
[`PEER-MANAGER-EVENT-POLICY-CORRELATION.md`](../correlation/PEER-MANAGER-EVENT-POLICY-CORRELATION.md).

The former largest unknown at `0x000617F8` and its sole 932-byte neural-layer callee at
`0x000876C8` now compile as owner-authorized transparent C. Both bodies use the same generated-model
configuration object at `0x000BD668` as builder `0x000742E4`; the local APIs replace embedded
callbacks and the former heap temporary with typed plans and bounded caller-owned storage. No
executable caller or raw entry pointer reaches the outer executor in the shipped image; the
apparent raw branch at `0x0003007A` is pinned literal-pool data before the real wrapper at
`0x0003007E`. This preserves the dormant topology without asserting a live product route or
fabricating model outputs. See
[`QUANTIZED-RUNTIME-REDUCTION-CORRELATION.md`](../correlation/QUANTIZED-RUNTIME-REDUCTION-CORRELATION.md).

The former largest unknown at `0x000739A8` and its complete six-function helper/constructor
closure are now owner-authorized transparent C. The exact Goodix-rooted initializer chain reaches
constructor `0x00074A20`; stock word `0x00074A98` supplied Thumb callback `0x000739A9`, while the
generated descriptor now binds the local target adapter. The seven functions / 2,264 bytes
implement quantized recurrent gates, matrix products, sigmoid/`tanhf`, state updates, checked
model-region resolution, and exact target scratch layout. The model weights remain explicit
caller-supplied build input rather than copied opaque firmware data. See
[`QUANTIZED-RUNTIME-REDUCTION-CORRELATION.md`](../correlation/QUANTIZED-RUNTIME-REDUCTION-CORRELATION.md).

The former largest unknown at `0x00035850` is pinned with its sole direct caller
`0x000766AC` under the existing Goodix GH_NADT provider boundary. The exact direct chain is
`0x0006E838 -> 0x000766AC -> 0x00035850`: the already pinned GH_NADT preprocessing core calls a
478-byte spectral peak-preparation pipeline, which calls the 1,162-byte harmonic-candidate
selector. Both stages are now transparent C with caller workspaces and explicit math/scale
bindings; the larger maps to `goodix_primitives_nadt_harmonic_candidates_select`. Both
body hashes, the selector's split executable extent, and both callsites remain pinned. See
[`GOODIX-NADT-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-PROVIDER-BOUNDARY.md).

The former largest unknown at `0x00076BDC` is now closed as a 1,234-byte indirect GoMore
floating-point neural-layer executor. The exact pointer `0x00076BDD` at `0x00074B40`, its
24-byte layer constructor, all sixteen constructor callsites, specialized 1/3/5-wide convolution
paths, activation behavior, constants, and body hash are pinned. Two callers build the already
hash-pinned paired GoMore sleep classifier graphs and the third builds another health-model graph.
It now compiles as `quantized_runtime_float_conv1d_execute`: virtual padding replaces the stock
in-place move, overlap uses caller workspace, and the layer constructor stores the local target
adapter. Model weights and biases remain explicit bounded inputs. See
[`GOMORE-NEURAL-RUNTIME-BOUNDARY.md`](../boundaries/GOMORE-NEURAL-RUNTIME-BOUNDARY.md).

The former largest unknown at `0x0008B378` is now closed as a dormant R1 health-daily synthetic
test fixture / 1,344 bytes. Exact diagnostics, type routing, 24-hour bounds, pseudorandom HR/SpO2/
temperature writes, four scattered executable ranges, body hash, and absence of any caller or
entry-pointer reference are pinned. It is eligible only as explicit clean-room test behavior and
is intentionally excluded from production. See
[`HEALTH-DAILY-TEST-CORRELATION.md`](../correlation/HEALTH-DAILY-TEST-CORRELATION.md).

The R1 touch-slider and gesture-event path is now closed as thirteen functions / 2,784 executable
bytes. Twelve formerly unclassified Ghidra functions / 2,776 bytes include the former largest
unknown at `0x00092CBC`; the eight-byte callback at `0x000933FC` is added as a manual provenance
supplement. The indirect Thumb pointer at `0x0008E7CC`, exact noncontiguous state-machine segments,
initial product configuration, calibration formula, timing and movement thresholds, three-sample
velocity filter, event bitset, body hashes, and callers are pinned. This admits only R1 gesture
policy after normalized samples; all IQS7211E register/controller behavior remains in the pinned
provider boundary. See [`TOUCH-SLIDER-CORRELATION.md`](../correlation/TOUCH-SLIDER-CORRELATION.md).

The Goodix GH_SPO2/dlCom component is now extended by 85 functions / 19,568 executable bytes.
The 82 formerly unclassified Ghidra functions / 19,520 executable bytes include former frontier
leaders `0x000742E4`, `0x0006C6A8`, `0x0003113C`, and `0x00034500`; three exact 16-byte Thumb
wrappers referenced by the table at `0x000BCF58` are added as manual provenance supplements. The
already gated Goodix entry `0x0002C944` directly calls processing root `0x0006C6A8` at
`0x0002CA24`. Exact `dlCom_pre2exc_pv_v1.3.0_c00c91c9`, GH_SPO2 v2.1.10.0 / `277e89de`, and
network `1f1cf98b` markers match Goodix primary-source diagnostics. The indirect recurrent
executor at `0x000739A8` and its complete helper/constructor closure are now source-admitted in
the quantized-runtime reconstruction after pointer- and callgraph pinning.
The dormant graph executor at `0x000617F8` and neural-layer executor at `0x000876C8` are now
source-admitted through explicit stage plans, recovered shape records, and caller-owned scratch,
with their shipped-image non-reachability still pinned.
The sole-caller diagnostic formatter at `0x0006CCC0` is likewise body-, callsite-, and
field-string-pinned and source-admitted through bounded typed sinks as provider support rather
than product telemetry.
The final HR/HBA root `0x0006C6A8` is source-admitted as
`goodix_primitives_hba_process`, with fixed caller workspace replacing all three transient
allocations and typed bindings for packed banks, spectra, report state, quantized runtime, and
model dispatch. Every executable segment,
function hash, direct-caller map, marker, and dispatcher word is pinned. Shared runtime helpers are
not claimed by outside-caller exclusivity. The recurrent runtime and graph topology are local;
no executable Goodix closure remains opaque and model inputs are explicit data bindings. See
[`GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md).

The Goodix GH_HR processing component is now extended by 31 formerly unclassified functions /
7,144 executable bytes. The 2,814-byte function at `0x00032808` has the already gated GH_HR core
`0x0006D51C` as its sole direct caller. Recursive direct-call traversal from that provider core
closes all 31 functions within four levels, with no outside direct callers. Exact executable
segments, hashes, and callsites are pinned, including the four-segment `0x00032808` body. All 31
are now source-admitted owner-authorized clean-room C; the original provider attribution and exact
callgraph remain pinned. See
[`GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md).

The Goodix GH_NADT component is now closed as 58 functions / 19,274 executable bytes. Its exact
`GH_NADT_pre_pv_v1.0.2.0_nc_548d894d` version builder was already provider-gated; 57 additional
functions / 19,148 bytes now leave the unclassified frontier. Direct edges close the chain from
existing Goodix candidate `0x0002CDD4` through streaming process `0x0006E008`, window classifier
`0x000856EC`, the now-local primary classifier `0x00047240`, the preprocessing spectral/harmonic pair, and the
now source-admitted state/output selector `0x00036F88`, the source-admitted signal-confidence tracker
at `0x00095828`, and the generated-model inference graph rooted at `0x000968C4`, with processing
every 25 samples. The signal-confidence graph's `0x00029144` dual-window feature/correlation
extractor is now source-admitted with fixed caller workspace, exact packed-5/10 conversion, and
typed tail-window spans. All segments, hashes, and direct callsites are pinned. The remaining
generated-subgraph bodies retain the
non-redistributable provider gate. See
[`GOODIX-NADT-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-PROVIDER-BOUNDARY.md).

The BLE-thread event consumer at `0x00045184` is now closed as one R1 product function / 1,736
Ghidra bytes. Its complete `0x00045184..<0x00045B16` range (including literal/string islands),
SHA-256, sole caller, event IDs, `pairAuth`/Peer Manager transition, two-target address policy,
exclusive persistent-setter caller set, mismatch disconnect, and fast/stop-advertising decisions
are pinned. Exact Nordic log and Peer Manager functions, authenticated CMSIS-FreeRTOS queue
receive, and FreeRTOS release remain provider-owned. Unclassified common logging/timer/role
callees remain gated rather than being absorbed. See
[`CONNECTION-CONTROL-CORRELATION.md`](../correlation/CONNECTION-CONTROL-CORRELATION.md).

The boot reset-reason path is now closed as two functions / 834 bytes. The product decoder maps
the exact reset-pin, watchdog, software, lockup, and three System-OFF wake bits, treats raw zero as
power-on/brownout, and attaches the retained SREQ record with persist-tag-2 reboot-caller gating.
The 80-byte lifecycle wrapper is only an R1 adapter around Nordic `nrf_power_resetreas_get/clear`.
The decoder's two executable extents, both body hashes, callers, register literal, and clear order
are pinned. See [`RESET-REASON-CORRELATION.md`](../correlation/RESET-REASON-CORRELATION.md).

Twelve formerly unclassified functions / 598 bytes now close the retained reset-trace path. The
exact 16-byte record uses a zero validity byte, thirteen logical field bytes, and little-endian
Modbus CRC16 over bytes 0...13. Persist/reboot tags, little-endian return-address and program-
counter fields, corruption repair, clearing policy, all hashes/callers, and the non-contiguous
capture extent are pinned. Eleven bodies are admitted as R1 behavior; the fault wrapper remains a
bounded adapter to Nordic/CMSIS `NVIC_SystemReset`, whose barriers and AIRCR mechanics are not
reimplemented. See [`RESET-TRACE-CORRELATION.md`](../correlation/RESET-TRACE-CORRELATION.md).

The 88-byte `nrf_pwr_mgmt_shutdown` and 244-byte static `shutdown_process` are exact Nordic SDK
17.1.0 provider code. The recovered request mutex/state path directly invokes the processor,
establishing `NRF_PWR_MGMT_CONFIG_USE_SCHEDULER=0`. Handler-section iteration, readiness return,
log flush, DFU/reset events, SoftDevice-aware System OFF, terminal barriers, hashes, and callers
match the pinned source. No local power-manager body is admitted. See
[`NORDIC-POWER-MANAGEMENT-CLOSURE.md`](../closures/NORDIC-POWER-MANAGEMENT-CLOSURE.md).

Ten exact functions / 958 executable bytes now route to Nordic SDK 17.1.0's unbonded buttonless
Secure DFU provider. Eight newly routed Ghidra entries remove 668 bytes from the frontier; the BLE
event handler at `0x00052154` is a newly bounded 128-byte manual supplement, and the already-routed
asynchronous SVCI initializer is now scatter/hash-pinned. The non-contiguous prepare/finalize and
SVCI paths, static authorization handler, open unbonded characteristic permissions, UUIDs, BLE and
SoC event paths, control-point opcodes, 1...20-byte advertising-name validation, SVCI completion,
three-byte response, hashes, and callers all match the pinned `ble_dfu.c` and
`ble_dfu_unbonded.c`. No local provider body is admitted. See
[`NORDIC-BUTTONLESS-DFU-CLOSURE.md`](../closures/NORDIC-BUTTONLESS-DFU-CLOSURE.md).

Eight formerly unclassified functions / 992 Ghidra bytes are exact Nordic SDK 17.1.0
`ble_advertising.c` code: connection-tag configuration, initialization, mode-configuration copy,
BLE event handling, `ble_advertising_start`, `flags_set`, `phy_is_valid`, and `use_whitelist`.
The 998-byte complete extent includes the start routine's six-byte inline Thumb `TBB` mode table.
Configuration validation/copy, buffer encoding, initial configure, connection/disconnection/
termination handling, directed-peer and whitelist requests, PHY checks, advertising parameter
selection, flags update, S140 configure/start calls, event callback, structure offsets, hashes,
and all direct callers agree with the pinned SDK. No local provider body is admitted. See
[`NORDIC-ADVERTISING-START-CLOSURE.md`](../closures/NORDIC-ADVERTISING-START-CLOSURE.md).

Eight formerly unclassified entries / 32 bytes are exact branch-only aliases. Their one
instruction, destination, body hash, and sole caller are pinned; no duplicate C body is needed.
The proprietary destination remains provider-gated, while the admitted targets retain their
existing clean-room adapter or product-behavior disposition. See
[`RESOLVED-THUNK-CLOSURE.md`](../closures/RESOLVED-THUNK-CLOSURE.md).

The formerly unclassified `0x00085440` / 40-byte body is exact FreeRTOS-Kernel 10.5.1
`prvReloadTimer`. Its loop, timer status-byte layout, two direct callers, and absence from Nordic
SDK 17.1.0's bundled 10.0.0 core establish that R1 combines the authenticated upstream 10.5.1 core
with Nordic's nRF52 port. See
[`FREERTOS-KERNEL-VERSION-CORRELATION.md`](../correlation/FREERTOS-KERNEL-VERSION-CORRELATION.md).

Five formerly unclassified functions / 158 ledger bytes now route to Nordic SDK: GATT-link default
initialization, SoftDevice RAM end calculation, the Peer Manager rank event wrapper and rank-state
initializer, and BLE common's security-requirement encoder. Complete extents total 164 bytes because the security encoder owns a
six-byte inline Thumb jump table beyond Ghidra's function end. Source semantics, hashes, and all
direct callers are pinned in
[`NORDIC-BLE-STATIC-HELPERS-CORRELATION.md`](../correlation/NORDIC-BLE-STATIC-HELPERS-CORRELATION.md).

Ten formerly unclassified functions / 784 bytes now route to Nordic Peer Manager: module reset,
database-change completion, cached local GATT database apply, Service Changed need/send handling,
event-context result policy, local-update flagging, Service Changed pending-flag iteration, Central
Address Resolution persistence, and pending-update iteration. Their exact error cases, events, flags, PDS calls, complete bodies, and
caller sets match the pinned SDK. See
[`NORDIC-GATT-CACHE-CLOSURE.md`](../closures/NORDIC-GATT-CACHE-CLOSURE.md).

The 72-byte function at `0x00095BFC` is now admitted as the R1
`vApplicationStackOverflowHook` configuration callback. Its only caller is FreeRTOS
`vTaskSwitchContext`, which contains the provider's four-word `0xA5A5A5A5` sentinel check and
therefore proves `configCHECK_FOR_STACK_OVERFLOW = 2`. openR1 now enables that upstream check and
implements only the recovered task diagnostic and non-returning fail-stop behavior over bundled
SEGGER RTT. See
[`FREERTOS-STACK-OVERFLOW-CORRELATION.md`](../correlation/FREERTOS-STACK-OVERFLOW-CORRELATION.md).

The 98-byte function at `0x00098DC0` is now source-routed to Nordic SDK
`nrfx_twim.c::xfer_completeness_check`. Its TXTX/TXRX/TX/RX descriptor cases, EasyDMA amount
comparisons, SUSPENDED-mask leg choice, and `ENABLE=0` then `ENABLE=6` recovery sequence match
the provider source. Its only two direct callsites are in the already-routed TWIM IRQ and transfer
paths. See
[`NORDIC-TWIM-COMPLETENESS-CORRELATION.md`](../correlation/NORDIC-TWIM-COMPLETENESS-CORRELATION.md).

The 530-byte application function at `0x00033364` is now source-routed to Nordic SDK
`SystemInit`; its only caller is Nordic `Reset_Handler`. Its seven calls reach the 14-byte
`nvmc_config` at `0x0007CA7C`, whose NVMC READY wait is inlined. The complete constants and flow
match nRF52840 errata, FPU, APPROTECT, NFCT-UICR, PSELRESET, NVMC, reset, and 64 MHz clock
initialization. openR1 compiles the pinned Nordic source and supplies the two recovered UICR build
switches; no startup body is local. See
[`NORDIC-SYSTEM-INIT-CORRELATION.md`](../correlation/NORDIC-SYSTEM-INIT-CORRELATION.md).

The duplicate 18-byte functions at `0x00095BB8` and `0x00095BD0` are now identified as the
FreeRTOS static-allocation callbacks for the idle and timer tasks. Each returns a 112-byte
`StaticTask_t` followed by a 256-word stack; their exact consumers are upstream
`vTaskStartScheduler` and `xTimerCreateTimerTask`. openR1 already kept those callbacks separate
from the SDK provider, and its timer stack has now been corrected from 128 to the recovered 256
words. See [`FREERTOS-STATIC-MEMORY-CORRELATION.md`](../correlation/FREERTOS-STATIC-MEMORY-CORRELATION.md).

Five formerly unclassified packed-word integrity helpers at `0x00028E5C`, `0x00028E70`,
`0x000294BC`, `0x000294F8`, and `0x0002950C` are now Goodix-gated. Their caller sets connect two
copies exclusively to the frozen Goodix demo/provider component and the remaining copy to GH_NADT
and another Goodix-rooted algorithm path. Three encoder copies, including the already gated GH_HR
body at `0x0005A5EC`, are byte-identical and use three identical four-word tables. Classification
rests on the callgraph contexts; the identical 54-byte bodies and constants corroborate it. No
private symbol or local implementation is admitted. See
[`GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md`](../boundaries/GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md).

The composite sensor-algorithm initializer at `0x00071A32` and its seven audited helpers form an
exact 586-byte GoMore candidate boundary. Its only caller is the byte-pinned GoMore sleep body
at `0x0006FEA0`; it initializes ten GoMore-attributed substates plus the newly bounded helpers.
The 8-byte reset at `0x00071D96` exactly duplicates the body at `0x0007170A`, but the attribution
rests on exclusive callgraph context, not generic byte identity. All eight entries have since
crossed the owner-authorized source gate: the composite root is transparent C with typed callback
and configuration inputs, and both reset leaves share one checked C body. See
[`GOMORE-PROVIDER-BOUNDARY.md`](../boundaries/GOMORE-PROVIDER-BOUNDARY.md).
The caller at `0x0006FEA0` is now transparent as
`gomore_primitives_sleep_algorithm_initialize`; its authorization, previous-state validation,
profile conversion, and complete child-initializer sequence use explicit typed providers and no
absolute firmware state.

The linked sensor-algorithm heap is now closed as thirteen exact functions and 1,202 executable
bytes. Its 44-byte control prefix, two bitmap-selected size-ordered bins, tagged eight-byte block
headers, boundary-record coalescing, allocation/split policy, control pointer at `0x20007C64`,
direct initialization from Goodix-candidate entry `0x0002A090`, and terminal
`sensor_algo_mem_fatal` path are recovered. Five bodies are scatter-loaded and are hashed over
only their executable spans. Function-local comparison rejects both Nordic FreeRTOS `heap_4` and
the repository's pinned TLSF v3.1 source. Provenance is now resolved: the component is Goodix's
`goodix_mem`/`GdMem` memory-pool manager from the GH3X2X SDK common DSP support library (config
tag `gh3x2x-v2.23_7ecd2a`), matched through the public `goodix_mem.h` -1/-2 error contract and
instruction-level comparison against the Goodix common-DSP library object. The twelve allocator
internals and twenty Goodix consumer call-site glue bodies are vendor-gated with the restrictive
binary-only Goodix SDK license; only the integrator-supplied `Gh3x2xPoolIsNotEnough` fatal
handler and the product byte-fill used for pool clearing are R1 product behavior. The allocator
itself remains implementation-blocked rather than translated or silently substituted. See
[`SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md`](../boundaries/SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md).

The primary/secondary register-read/write and shutdown wrappers at
`0x00054FF8...0x000551E0`, primary and secondary initializers at `0x00055278` and `0x000552E4`, completion callback at
`0x00070778`, and duplicate-state wait adapters at `0x00070820` and `0x0007088C` are now routed
and implemented as R1 framing, bounds, state/status, lifecycle configuration, power-cycle, and
timeout policy over Nordic GPIO/TWI/TWIM/delay/fatal handling plus authenticated CMSIS-FreeRTOS
kernel/tick/semaphore providers. Four adjacent per-instance software-bus shutdown adapters now
delegate pin release to Nordic `nrf_gpio_cfg_default` without admitting the bit-level bus engine.
These fifteen exact bodies remove 1,022 bytes from the unclassified
frontier. See
[`TWI-SYNCHRONIZATION-CORRELATION.md`](../correlation/TWI-SYNCHRONIZATION-CORRELATION.md).

The 26-byte helper at `0x00037530` is byte-identical to the already-routed
`__NVIC_ClearPendingIRQ` instance at `0x00038166`, including the non-negative IRQ guard, indexed
`NVIC->ICPR` write, and negative-exception path. Both now route to the CMSIS Cortex-M4 header
bundled by Nordic; their common body hash is verifier-pinned.
Six adjacent exact-extent bus-record binding wrappers are now separately source-routed as fixed
R1 configuration. They preserve two hardware semaphore/device bindings and four software-bus
records through direct typed provider interfaces without recreating the unidentified registry or
software-I2C engine. See
[`BUS-REGISTRATION-CORRELATION.md`](../correlation/BUS-REGISTRATION-CORRELATION.md).
The four GPIO-driven software-TWI engines omitted by Ghidra are now closed as a 40-function,
3,524-byte exact-extent census. Their ten roles, four state/pin instances, and every body hash are
known, but no attributable source/version/license is established. They are therefore separately
implementation-blocked rather than recreated locally. See
[`SOFTWARE-TWI-PROVIDER-BOUNDARY.md`](../boundaries/SOFTWARE-TWI-PROVIDER-BOUNDARY.md).
The immediately following RTC-device block is independently closed as nine functions and 798
bytes: Nordic `nrfx_rtc_init` routes to SDK 17.1.0, one fixed initcall wrapper is R1
configuration-only, and seven named-record/calendar/callback bodies remain unidentified and
implementation-blocked. Four of those seven were removed from the unclassified frontier. See
[`RTC-DEVICE-PROVIDER-BOUNDARY.md`](../boundaries/RTC-DEVICE-PROVIDER-BOUNDARY.md).

The final Nordic TWIM transfer core at `0x0007B448` is now source-routed as `nrfx_twim_xfer`.
Ghidra's 690-byte size is correct but non-contiguous: a 32-byte veneer at
`0x0007B448..<0x0007B468` branches to a 658-byte body at `0x00093B34..<0x00093DC6`. Exact
descriptor, EasyDMA, event/interrupt, repeated-transfer, and blocking/error semantics match the
pinned SDK source, and the ordered executable bytes are SHA-pinned in the verifier. See
[`TWI-SYNCHRONIZATION-CORRELATION.md`](../correlation/TWI-SYNCHRONIZATION-CORRELATION.md).

The adjacent interrupt veneers at `0x00031A74` and `0x00031A84` are now source-routed as Nordic
`nrfx_twim_0_irq_handler` and `nrfx_twim_1_irq_handler`. The 8-byte TWIM0 veneer supplies base
`0x40003000`; the 10-byte TWIM1 veneer supplies base `0x40004000` and tail-calls the 400-byte
static `nrfx_twim.c::twim_irq_handler` core at `0x000939A0..<0x00093B30`. Ghidra assigns that
shared core only to the 410-byte TWIM1 function. ERROR/STOPPED/SUSPENDED events, EasyDMA
completion checks, repeated-transfer state, anomaly-109 handling, callback ABI, and the SDK/CMSIS
pending-IRQ clear agree with nRF5 SDK 17.1.0. Both executable extents are SHA-pinned.

The following 76-byte body at `0x00031A94` is independently source-routed as Nordic
`nrfx_spim_2_irq_handler`: SPIM2 base `0x40023000`, END event `0x118`, the exact SDK control-block
layout, software slave-select deassertion, completion-event construction, and callback ABI all
match `nrfx_spim.c`. The clean SDK image now compiles that official translation unit with only
SPIM2 enabled; the proprietary sensor provider behind the transport remains separately gated.

## Earlier completed closures

The four-byte health-database provider accessor at `0x00070028` and 526-byte startup controller at
`0x00070030` are routed and implemented as explicit provider binding plus exact schema-size,
FlashDB/provider-ordering, retained-clock, time-subscription, local-day-query,
zeroed-workspace, allocation-failure, and crash-restore policy. FlashDB and RTOS implementations
remain attributable providers, while the unresolved time/calendar provider stays abstract and
blocked. See
[`HEALTH-DATABASE-STARTUP-CORRELATION.md`](../correlation/HEALTH-DATABASE-STARTUP-CORRELATION.md).

The 146-byte retained crash-log sink at `0x0007F030` is product-routed and implemented as bounded
R1 buffer/newline/one-time initialization policy over the attributable toolchain formatter and
SDK-bundled SEGGER RTT transport. The stock oversized-format out-of-bounds edge is capped. See
[`RETAINED-LOG-CORRELATION.md`](../correlation/RETAINED-LOG-CORRELATION.md).

The eleven-function health crash-record lifecycle is now product-routed and implemented over
injected time-provider values, an uninterpreted optional 896-byte provider blob, and the already
admitted activity/HR/SpO2/HRV caches. The exact 966-byte record, 52-byte summary, non-contiguous
builder address set, validated accessors, component clears, one-shot cache restore, status-bit
update, and Modbus CRC lifecycle are pinned without implementing the unknown blob lookup or
time/calendar provider. See
[`HEALTH-CRASH-SNAPSHOT-CORRELATION.md`](../correlation/HEALTH-CRASH-SNAPSHOT-CORRELATION.md).

The 14-function clock-backend/calendar cluster now has exact roles and body hashes, but no
attributable provider source. It is separately implementation-blocked, and the activity consumer
continues to accept an abstract bucket resolver. See
[`TIME-CALENDAR-PROVIDER-BOUNDARY.md`](../boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md).

The activity cumulative-counter accumulator and event-11 storage boundary is now cleanly
implemented and exact-body pinned. It preserves the 24-byte state, 600-second window, wear
transition grace, rollback/day rebasing, cross-bucket placement, and packed-field wrap while
keeping step, locomotion, and energy algorithms provider-gated. See
[`ACTIVITY-ACCUMULATOR-CORRELATION.md`](../correlation/ACTIVITY-ACCUMULATOR-CORRELATION.md).

The health-history registration, binary-search, event-record, and event-consumer boundary preserves
all nine public history routes and proves temperature/stress absence without exposing a private
event sender. See
[`HEALTH-HISTORY-ROUTING-CORRELATION.md`](../correlation/HEALTH-HISTORY-ROUTING-CORRELATION.md).

The fifteen heart-rate, SpO2, and HRV sample-storage functions close range gates, timestamp
selection, dual-hour aggregation, compact latest points, and notification routing without crossing
into Goodix acquisition or GoMore algorithms. See
[`SCALAR-HEALTH-SAMPLE-STORAGE-CORRELATION.md`](../correlation/SCALAR-HEALTH-SAMPLE-STORAGE-CORRELATION.md).

The scalar-health offline synchronization family is now cleanly implemented and source-routed.
First-party executable models and exact recovered bodies pin the queue storage, validation, merge,
and acknowledgement behavior for three metrics; each cluster feeds an admitted public
synchronizer:

| Metric | Capacity / record | Consume | Empty | Enqueue | ACK | Merge | Public sync |
| --- | --- | --- | --- | --- | --- | --- | --- |
| heart rate | 24 × 16 bytes | `0x0003FAA4` | `0x0003FB90` | `0x0003FBA4` | `0x0003FCEC` | `0x00040700` | `0x0008C150` |
| SpO2 | 24 × 16 bytes | `0x00043CA0` | `0x00043D90` | `0x00043DA4` | `0x00043EB0` | `0x000448B0` | `0x0008CD60` |
| HRV | 24 × 20 bytes | `0x00040984` | `0x00040A74` | `0x00040A88` | `0x00040BD4` | `0x00041638` | `0x0008C750` |

All 15 entries are byte-bounded, provider-screened, and pinned by the verifier. The three callbacks
omitted by Ghidra are exact manual inventory supplements. Distinct state instances preserve the
HR/SpO2/HRV storage and cursor boundaries; shared local operations retain the two exact record
widths, timestamp policies, validation rules, duplicate handling, and wire encodings. See
[`SCALAR-HEALTH-OFFLINE-SYNC-CORRELATION.md`](../correlation/SCALAR-HEALTH-OFFLINE-SYNC-CORRELATION.md).

## Next evidence-ranked closure

The activity cache/merge families, all nine HR/SpO2/HRV daily-cache callbacks, the bounded
time/hour rollover planners, and the temperature/stress storage-cache families are now complete;
see [`ACTIVITY-DAILY-CACHE-CORRELATION.md`](../correlation/ACTIVITY-DAILY-CACHE-CORRELATION.md) and
[`ACTIVITY-DAY-MERGE-CORRELATION.md`](../correlation/ACTIVITY-DAY-MERGE-CORRELATION.md), plus
[`SCALAR-HEALTH-DAILY-CACHE-CORRELATION.md`](../correlation/SCALAR-HEALTH-DAILY-CACHE-CORRELATION.md) and
[`TIME-HEALTH-ROLLOVER-CORRELATION.md`](../correlation/TIME-HEALTH-ROLLOVER-CORRELATION.md), plus
[`TEMPERATURE-STRESS-DAILY-CACHE-CORRELATION.md`](../correlation/TEMPERATURE-STRESS-DAILY-CACHE-CORRELATION.md),
the activity accumulator is closed in
[`ACTIVITY-ACCUMULATOR-CORRELATION.md`](../correlation/ACTIVITY-ACCUMULATOR-CORRELATION.md), and the HR/SpO2/HRV
sample-storage consumers are closed in
[`SCALAR-HEALTH-SAMPLE-STORAGE-CORRELATION.md`](../correlation/SCALAR-HEALTH-SAMPLE-STORAGE-CORRELATION.md).
The next unresolved inventory leader is the 222-byte function at `0x0008A45C`,
followed by 220 bytes at `0x0008F780`, 218 bytes at `0x0008EF28`, and 216 bytes at
`0x0003E7A8`. Each must receive the same
function-local evidence, provider screening, behavioral implementation, and exact body pinning
before ownership changes. Nordic- or third-party-looking clusters remain source-correlation tasks,
not clean-room implementation tasks. QMA6100, YHM2710, and Goodix have crossed the owner-authorized
source gate; the remaining GoMore functions stay gated as documented elsewhere.
