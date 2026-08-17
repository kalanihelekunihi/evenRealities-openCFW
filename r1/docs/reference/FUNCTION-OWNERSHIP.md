# Function-level source ownership gate

The machine-readable [`FUNCTION-OWNERSHIP.csv`](FUNCTION-OWNERSHIP.csv) covers every Ghidra-recovered
function in the R1 application and bootloader inventories, plus exact function entries recovered
manually by the audit where Ghidra left executable bytes undefined. It determines whether the open firmware
may use a pinned provider implementation, may independently implement product behavior, or must
pause for ownership research. Regenerate it with:

```sh
python3 tools/build_r1_source_ownership.py
```

## Interpretation

- `use_nordic_sdk`, `use_nordic_supplied_provider`, `use_nordic_sdk_bundled_upstream`,
  `use_authenticated_upstream_snapshot`, `use_pinned_upstream`, and `use_toolchain_runtime` mean the implementation must link or compile
  the identified provider code. The decompilation is compatibility evidence, not source material.
- `clean_room_behavior_only` means an R1-specific behavior has accepted address-level evidence and
  no third-party implementation has been identified. New code may implement the documented public
  behavior without copying decompiler expression or structure.
- `clean_room_configuration_only_use_pinned_provider` means only the recovered R1 parameters and
  provider adapter may be written locally. The algorithm, state machine, encoder, or driver behind
  that boundary must come from the named pinned provider.
- `clean_room_adapter_only_use_authenticated_provider` applies to a mixed function whose upstream
  core is identifiable but whose exception, logging, task-access, or formatting seam is R1-owned.
  Only that bounded seam may be local; the underlying provider remains compiled upstream source.
- `clean_room_adapter_only_use_nordic_sdk` applies the same rule to an SDK function with a bounded
  R1 hook; these include the wall-clock log-prefix seam, four-characteristic BAE8 write-event seam,
  and four byte-pinned analog naming/configuration/filtering adapters around Nordic `nrfx_saadc`.
- `clean_room_adapter_only_use_nordic_sdk_and_cmsis` permits only byte-pinned R1 state/status and
  timeout policy at a mixed provider boundary. Nordic owns TWI and delay behavior; authenticated
  CMSIS-FreeRTOS owns kernel, tick, and semaphore behavior.
- `clean_room_adapter_only_use_nordic_sdk_and_fal` applies to the ten byte-pinned internal-flash
  seams. Local code may own only R1 geometry, bounds, serialization, and direct provider binding;
  Nordic fstorage and upstream FAL supply their implementations, and the unresolved generic stock
  registry is not recreated.
- `clean_room_adapter_only_use_pinned_provider` is the corresponding rule for Bosch and ST motion
  drivers: local code is limited to R1 configuration, board I/O, bounds, identity, logging, and
  event glue, while official provider source owns the driver.
- `clean_room_adapter_only_use_licensed_provider` bounds the same product seams where provider
  lineage is proven but no redistributable source is admitted. The adapter and provider path remain
  disabled until a licensed provider is supplied.
- `clean_room_adapter_only_vendor_io_abstract` permits only byte-pinned R1 resource ownership and
  board lifecycle. Device-register, transport, and electrical transitions stay behind an abstract
  licensed provider.
- `resolve_provider_before_implementation` and `vendor_source_required_not_redistributable` are
  hard gates. A provider version, license, and source/binary integration decision is required first.
- `investigate_before_implementing` is the default. An unknown function is **not** presumed to be
  Even Realities code and is not eligible for clean-room implementation merely because it lacks a
  recognizable symbol.
- `clean_room_reimplementation_owner_authorized` marks the six Bravechip-attributed middleware
  families, the GXT310 closure, the complete QMA6100 provider/adapter closure, and the complete
  YHM2710 closure plus the 339 Goodix, 362 GoMore algorithm reductions, and seven
  owner-authorized R1 GoMore adapters (939 entries)
  reconstructed from decompilation evidence under the owner-authorized
  full reduction (2026-08-14, [`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md)). The
  reconstruction is independently compiled C with per-function provenance; it is not vendor
  source, and on-target runtime adoption remains a separate gate.

Provider references inside an R1 wrapper do not prove that the wrapper came from that provider.
For this reason, marker matches alone remain candidates. Bosch BMA456 and the R1-labelled
`LIS2DOC` path have now crossed the gate through function-local correlation: 18 Bosch and 26 ST
functions route to official sources, while eight Bosch and seven ST functions are explicitly
bounded as R1 adapters. The ST part is LIS2DW12 (WHO_AM_I `0x44`). QMA6100 now has three
QST-lineage provider bodies and fourteen adapters reconstructed together under the owner-authorized
reduction; no Goodix-candidate or GoMore health-algorithm entries remain to be reduced. IQS7211E has crossed the source gate through
pinned MIT provider/settings references: eighteen exact recovered entries are now bounded as R1
configuration, Nordic/provider port, task dispatch, lifecycle, IRQ, and recovery adapters. The
former GoMore algorithm gate is closed by all 362 transparent reductions. Three additional
byte-pinned R1 adapters are also reconstructed: the four topic inputs, their readiness and
successful-update bookkeeping, and the backward-clock reset dispatcher. Live engine composition
remains a separate typed-input and owned-hardware validation task.
The 2,360-byte energy-model dispatcher/estimator closure rooted at `0x0002F488` is now fully
source-admitted. Its complete private descendant graph, exact bodies, all caller sets, formulas,
three 27-float mode tables, interpolation, and state logic are represented in transparent C.
The 2,102-byte top-level producer at `0x0005F56C` is also source-admitted as a typed 92-byte
state transition producing all eleven energy floats without the stock internal reference pointer.
The adjacent 272-byte daily activity accumulator at `0x00061274` is source-admitted with typed
52-byte state and 44-byte output records, exact local-day reset, truncation, and distance behavior.
The 436-byte profile converter at `0x00071E34` is source-admitted with all seven validation/default
paths, status precedence, duplicated output fields, and the two-value persistent-cache behavior.
The 430-byte sleep-stage statistics block at `0x00069128` is source-admitted over the existing
bounded modulo stage lookup, producing all twelve recovered fractions, ratios, and durations.
The adjacent 326-byte interval-statistics block at `0x00068FD4` is also source-admitted, producing
the seven recovered interval, leading/middle/trailing-awake, sleep, and efficiency fields.
Its sole-caller score leaf at `0x0006778C` is source-admitted with the exact duration bands,
double-tanh shape, `powf(1.1, ...)` wake penalty, REM/deep weights, clamp, and 540-minute branch hole.
The 444-byte peak-rate interpolator at `0x00074D60` is source-admitted with bounded peak/output
spans, invalid-anchor skipping, exact 60-BPM defaults, spacing rates, and grid interpolation.
Its 280-byte caller at `0x00088AAC` is source-admitted with exact spacing invalidation, mode cadence,
90-float rotation, tail normalization, and an explicit wrapping update counter.
The 110-byte peak carryover leaf at `0x00076502` is source-admitted with bounded suffix compaction,
the exact above-749 retention rule, 750-position rebasing, and invalid-marker preservation.
The 112-byte valley extractor at `0x00064A28` is source-admitted with exact asymmetric local-minimum,
positive-curvature, twelve-candidate, and zero-filled output behavior.
The 128-byte history advance at `0x0008EE3A` is source-admitted over a typed 396-byte state, with
exact 25-sample shifts, position rebasing/compaction, and the greater-than-two full-reset path.
The latest supplemental entry is the 602-byte private IIR coefficient designer at `0x000717AC`.
Its only caller is the already gated sleep-filter initializer `0x00071D62`; Arm toolchain
trigonometric/power routines remain separately source-routed, and no GoMore formula or generated
coefficients are admitted locally.
The prior six entries are the 1,890-byte activity-state window classifier at `0x0006138C` and
five private statistical/decision helpers. Their sole-provider caller chain, noncontiguous body,
three inline dispatch tables, literal pool, and exact callsites remain pinned; all six now have
typed local reconstructions, including the complete seven-state top-level state machine.
The newest eight-entry audit scope is a 586-byte composite initializer boundary rooted at
`0x00071A32`. Its sole caller is an already-gated GoMore sleep body, ten direct child initializers
were already GoMore-attributed, and each helper has a pinned body and caller set. This context—not
an 8-byte collision by itself—supports the attribution of `0x00071D96` with its duplicate at
`0x0007170A`. All eight entries have now crossed the owner-authorized source gate; the root maps to
`gomore_primitives_composite_engine_initialize` and both reset twins map to
`gomore_primitives_clear_first_byte`.
The NFC cluster has separately crossed the gate: 27 ST25DVxxKC bodies route to ST's pinned
BSD-3-Clause component and seven product/board wrappers are bounded as R1 adapters. The raw
ST-specific BSim corpus includes exact `ReadReg` and `WriteReg` anchors; the remaining mappings
require matching register constants and complete function semantics, not address proximity.
Five adjacent R1 resource functions separately cover the P1.10 NFC lifecycle, exclusive `i2c_5`
ownership, and three-client battery/optical/touch lease. The YHM register sender is independently
reconstructed behind that typed resource boundary.
CmBacktrace likewise has five exact core functions and fifteen bounded adapters. Five hundred seventeen
application entries now route directly to Nordic SDK 17.1.0, thirteen route to SDK-bundled SEGGER
sources, and the mixed log-prefix and BAE8 write functions are bounded as R1/Nordic adapters. The
exact map is in
[`NORDIC-SDK-CORRELATION.md`](../correlation/NORDIC-SDK-CORRELATION.md).

Goodix's primary-source traces additionally correlate the exact R1 `GH_HR`, `GH_HRV`, `GH_SPO2`,
`GH_NADT`, DSP, `dlCom`, driver-version, component-hash, demo-initialization, and SPI-registration
topology. The conservative boundary now contains 53 individually reviewed provider/demo functions,
116 byte-pinned call-graph closure candidates, and 16 separately pinned R1 adapters. The exact
`GH_HRV` version builder was consequently moved out of the GoMore set. Three corrected GH_HR
functions at `0x0005A5EC`, `0x0006D51C`, and `0x000759F4` are also byte-pinned. Five duplicate
packed-word integrity helpers are additionally callgraph-attributed and pinned in
[`GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md`](../boundaries/GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md). Thirteen bounded
motion call-table functions, eight newly bounded internal-flash functions, two R1 analog adapters,
and six Nordic SAADC functions repair omissions in the Ghidra inventory. The current ledger covers
3,165 application/bootloader entries. The R1-owned structured-log closure covers sixteen
record/cache functions / 1,802 bytes, including four exact manual supplements / 82 bytes. It admits
only bounded product record, cache, mode, and persistence-orchestration behavior; Nordic logging,
Arm runtime, RTOS, clock/calendar, device-registry, and `log.bin` writer/export implementations
remain provider-owned or unresolved. The adjacent three-function / 876-byte R1 `log.bin` writer
closure now admits only partition geometry, initialization scan, cursor, and page policy; pinned
FAL and configured flash I/O remain external, as does the composite exporter/transport. The
two-function / 616-byte R1 HRV synchronization-flush closure admits only builder reset, bounded
sparse-day serialization, future rejection, acknowledgement context, and reset-after-attempt
behavior; allocation, time, topic, and transport providers remain external. The one-function /
578-byte R1 touch-task dispatcher closure admits only event routing, lifecycle orchestration,
diagnostics, and factory-marker glue around pinned provider seams. The 562-byte named
sensor-stream unregistration routine is separately blocked as an unresolved shared framework;
cross-domain use does not make it R1-owned. Nine generic
device-registry/list/dispatch functions,
fourteen clock/backend/calendar functions, forty GPIO-driven software-TWI functions, and seven
generic RTC-device functions are now
isolated as unidentified and still-blocked provider candidates rather than being attributed to R1
or a provider. The software-TWI set supplies exact extents, hashes, and behavior for four
compiler-instantiated engines but no attributable source/version/license; see
[`SOFTWARE-TWI-PROVIDER-BOUNDARY.md`](../boundaries/SOFTWARE-TWI-PROVIDER-BOUNDARY.md). The adjacent RTC split
routes `nrfx_rtc_init` to Nordic source and admits one fixed R1 configuration wrapper without
claiming the unidentified named-record/calendar/callback layer; see
[`RTC-DEVICE-PROVIDER-BOUNDARY.md`](../boundaries/RTC-DEVICE-PROVIDER-BOUNDARY.md).
The two-function / 560-byte BLE transmit-queue producer is product-owned only at its envelope,
dispatch-type, warning, timeout, worker-signal, and cleanup policy. Authenticated FreeRTOS/CMSIS,
Arm runtime, logging, and the transport worker remain separate providers.
The two-function / 578-byte heart-rate synchronization flush is likewise product-owned only at
its bounded 24-slot packet/reset and acknowledgement-context policy. Authenticated FreeRTOS,
time/calendar, topic selection, transport, logging, and biometric implementations remain
separate providers; see
[`HR-SYNC-FLUSH-CORRELATION.md`](../correlation/HR-SYNC-FLUSH-CORRELATION.md).
The corresponding two-function / 578-byte SpO2 flush has the same ownership split and separately
pinned metric-specific callgraph and sender seam; see
[`SPO2-SYNC-FLUSH-CORRELATION.md`](../correlation/SPO2-SYNC-FLUSH-CORRELATION.md).
Eleven complete R1 wear-fusion entries / 1,756 executable bytes are now admitted as clean-room
behavior: seven Ghidra functions plus four manually recovered callback extents covering bounded
history ingestion, raw-HR/ADT lifecycle planning, and the sleep edge, alongside the motion/living
callbacks, statistics/range helpers, teardown, and wear-on/off decisions. Their
sensor-stream, Goodix, motion-provider, timer, logging, and transport dependencies remain external;
see [`WEAR-FUSION-CORRELATION.md`](../correlation/WEAR-FUSION-CORRELATION.md).
Four R1 BLE connection-parameter functions / 498 bytes are likewise admitted for the product's
role-handle access, strict fast/slow classification, state update, and retry planning only. Nordic
owns BLE/GAP operations and the unresolved generic event-loop timer remains external; see
[`CONNECTION-PARAMETER-POLICY-CORRELATION.md`](../correlation/CONNECTION-PARAMETER-POLICY-CORRELATION.md).
The 472-byte R1 sleep synchronization packet builder is admitted for header construction, compact
stage merging, and legacy-clock correction only. Allocation, clock, transport, acknowledgement,
logging, and flash remain external; see
[`SLEEP-SYNC-PACKET-CORRELATION.md`](../correlation/SLEEP-SYNC-PACKET-CORRELATION.md).
The complete two-function / 856-byte packed-channel decoder/scaler closure is source-admitted as
transparent C with explicit table and toolchain-math bindings; see
[`GOODIX-CHANNEL-DECODER-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-CHANNEL-DECODER-PROVIDER-BOUNDARY.md).
The 518-byte GH_NADT channel-quality stage is likewise source-admitted with typed thresholds and
an explicit exponential binding; see
[`GOODIX-NADT-QUALITY-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-QUALITY-PROVIDER-BOUNDARY.md).
The seven-function / 1,098-byte GH_NADT extrema/peak-mask helper chain is also fully
source-admitted with caller-owned scratch; see
[`GOODIX-NADT-PEAK-MASK-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-PEAK-MASK-PROVIDER-BOUNDARY.md).
The remaining 30-function / 5,126-byte GH_NADT accumulation/decision graph has no non-Goodix
caller and is likewise provider-owned; see
[`GOODIX-NADT-ACCUMULATION-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-ACCUMULATION-PROVIDER-BOUNDARY.md).
The 514-byte GH3X2X register-profile decoder is also provider-owned; see
[`GOODIX-REGISTER-PROFILE-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-REGISTER-PROFILE-PROVIDER-BOUNDARY.md).
The two-entry / 498-byte MAC-keyed compiled-default restore closure at `0x0007C52C` includes the
exact four-byte storage-event veneer at `0x00042BBE`. It is R1-owned but security-preserving: the
typed C planner accepts only caller-owned records, its identity table is not redistributed, and
live persistence remains disabled; see
[`NV-COMPILED-RESTORE-CORRELATION.md`](../correlation/NV-COMPILED-RESTORE-CORRELATION.md).
The next initcall pair is also split. The `device_stacmd` table routes fourteen exact functions /
1,000 bytes to the owner-authorized YHM2710 reconstruction and admits its 18-byte direct binding
as configuration. The other 22 coupled device/register bodies are reconstructed in the same
module. The adjacent watchdog routes four exact bodies
to Nordic `nrfx_wdt.c` and admits only two R1 lifecycle/feed adapters plus the fixed binding; see
[`YHM2710-I2C5-RESOURCE-BOUNDARY.md`](../boundaries/YHM2710-I2C5-RESOURCE-BOUNDARY.md),
[`YHM2710-REDUCTION-CORRELATION.md`](../correlation/YHM2710-REDUCTION-CORRELATION.md), and
[`WATCHDOG-DEVICE-CORRELATION.md`](../correlation/WATCHDOG-DEVICE-CORRELATION.md).
The linked sensor-algorithm private heap is now independently closed as thirteen exact functions
and 1,202 executable bytes. Its two-bin structure, tagged headers, coalescing, split policy,
Goodix-candidate initialization edge, and `sensor_algo_mem_fatal` path are pinned, while its
source/version/license remain unresolved. All thirteen entries therefore move from unclassified
to `unknown_sensor_algorithm_heap_provider_candidate` without becoming eligible for local
implementation; see
[`SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md`](../boundaries/SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md).

The GH_NADT processing component is now closed separately as 58 functions / 19,274 executable
bytes. Its exact `GH_NADT_pre_pv_v1.0.2.0_nc_548d894d` builder was already Goodix-gated; 57
additional functions / 19,148 bytes are now routed from the unclassified frontier through the
closed Goodix-rooted callgraph. All remain `vendor_source_required_not_redistributable`; no NADT
classifier or signal-processing body is eligible for local reconstruction. The newly closed
`0x0006E838 -> 0x000766AC -> 0x00035850` chain pins the spectral preparation and harmonic-candidate
selection path to that same provider boundary. The same preprocessing core is the sole caller of
the later closed 744-byte state/output selector at `0x00036F88`. The same root also exclusively
reaches the nineteen-function / 3,246-byte signal-confidence,
correlation, peak, and statistic graph at `0x00095828`; two small helpers shared with adjacent
unclassified signal routines are admitted without claiming outside-caller exclusivity. The same
preprocessing core also exclusively reaches a seven-function / 1,964-byte generated-model
inference graph along `0x0006E838 -> 0x000968C4 -> 0x0002907C -> 0x00037890 -> 0x00034194`.
Its outer `0x00037890` topology is now a local bounded seven-stage orchestrator; private weights
and the nested `0x00034194` inference runtime are both source-admitted typed
orchestrators; private operator/model contents remain explicit bindings. See
[`GOODIX-NADT-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-NADT-PROVIDER-BOUNDARY.md).

The GH_HR processing callgraph now routes another 31 functions / 7,144 executable bytes to that
same provider attribution. The former largest unknown at `0x00032808` is called only by the already
byte-pinned GH_HR core, and the recursive four-level descendant set has no outside direct callers.
All 31 functions now have owner-authorized clean-room C while retaining their pinned attribution;
see
[`GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md).

Seven R1-owned automatic
health-sync functions are separately admitted from
address-level decompilation and first-party behavioral evidence; they cover the authenticated-phone
gate, shared three-hour scheduler, and five public-history legs without admitting any GoMore or
Goodix provider code. Five product-owned activity offline-sync functions now cover the exact
144-record queue, merge, and acknowledgement semantics; one is a manually recovered callback that
Ghidra omitted. Fifteen product-owned scalar-health offline-sync functions cover distinct HR,
SpO2, and HRV 24-record queues, exact retained record bytes, consecutive day/offset merge,
FIFO-prefix acknowledgement, and the HRV callback's distinct clock-sampling policy; three are
manually recovered callbacks omitted by Ghidra. Five activity daily-cache lifecycle functions are
also admitted for accessor/metadata refresh, reset, legacy-clock read/redaction, and bounded hour
write. Five activity day-builder,
RAM/decoded-flash merge, and packet-flush functions are separately admitted without absorbing
storage, allocation, calendar, or transport providers. Nine scalar-health daily-cache callbacks
now cover bounded HR, SpO2, and HRV slot reset/read/write plus the recovered invalid-clock path.
Two time/hour storage orchestrators are admitted only as adapters around pinned FlashDB and metric
providers, while the manually recovered backward-clock adapter now compiles and is source-bound to
the transparent GoMore reset seam with on-target execution intentionally suppressed.
Fifteen product-owned temperature/stress storage functions now cover bounded event acceptance,
replacement timestamps, one-byte temperature offsets, shared hourly averaging, and daily-cache
callbacks without admitting GXCAS acquisition or GoMore stress generation. Five of these functions
are exact manual inventory supplements omitted by Ghidra.
Fifteen product-owned HR/SpO2/HRV sample-storage functions now cover range gates, metric-specific
timestamp selection, compact latest points, dual-hour aggregation, and notification routing without
admitting Goodix optical or GoMore algorithm code. Two SpO2 bodies are exact manual supplements.
The exact health-registration binary search is now product-routed alongside the already admitted
dispatcher, nine event-producing handlers, and event-14 consumer. This closes the typed routing
boundary without making internal event publication public.
Five activity cumulative-counter functions are now product-routed for the provider-facing 24-byte
accumulator, periodic and explicit-refresh policy, exact event-11 storage, and automatic-sync
trigger wrapper. Motion classification, step detection, and energy production remain outside the
clean-room boundary.
Eleven product-owned health crash-record functions now compose, validate, access, clear, and
one-shot restore the exact retained record over injected time values, an uninterpreted provider
blob, and admitted health/activity caches. The blob lookup and time/calendar implementations
remain source-gated.
One bounded health-database accessor and one product-owned startup orchestrator now own only the
explicit provider binding and exact six-schema size gate,
FlashDB/provider call order, time-listener registration, retained-clock handoff, zeroed recovery
workspace, allocation-failure behavior, and crash-snapshot restore. FlashDB, RTOS, event-listener,
and time/calendar implementations remain in their attributable or blocked provider families.
One product-owned retained crash-log sink now owns only the recovered buffer, first-use, newline,
and bounded append policy; toolchain formatting and bundled SEGGER RTT transport remain their
attributable providers.
Fifteen TWI register-transfer, synchronization, and lifecycle functions are separately admitted as R1
adapters around Nordic and CMSIS providers. They own only framing/bounds, event/status mapping,
the kernel-state semaphore gate, timeout conversion, recovered polling policy, bus configuration,
hardware shutdown power-cycle policy, and four Nordic-default software-bus pin-release paths. The
GPIO-driven bit engines are not admitted.
Zero entries remain unclassified. The former generic registry, time/calendar, software-TWI,
RTC-device, sensor-stream, quantized-runtime, GXT310, QMA6100, and YHM2710 families are
owner-authorized reconstructions. Four exact Nordic watchdog bodies and two R1/Nordic watchdog
adapters are source-routed. No bootloader provider entry remains unclassified.

Eight branch-only thunks / 32 bytes now inherit the already accepted ownership and disposition of
their exact destinations. One maps to reconstructed Goodix code, one aliases an R1 Goodix board adapter, and six
alias product-owned daily-cache metadata operations. See
[`RESOLVED-THUNK-CLOSURE.md`](../closures/RESOLVED-THUNK-CLOSURE.md).

Eight formerly unclassified functions / 992 Ghidra bytes now route directly to Nordic SDK 17.1.0
`ble_advertising.c`: connection-tag configuration, initialization, mode-configuration copy, BLE
event handling, `ble_advertising_start`, `flags_set`, `phy_is_valid`, and `use_whitelist`. Their
complete extents total 998 bytes because the start routine owns a six-byte inline Thumb `TBB`
table. The source route, body/extent hashes, structure offsets, SoftDevice calls, and direct caller
sets are pinned in
[`NORDIC-ADVERTISING-START-CLOSURE.md`](../closures/NORDIC-ADVERTISING-START-CLOSURE.md).

Ten exact unbonded buttonless-DFU provider functions / 958 executable bytes now route directly to
Nordic SDK 17.1.0. Eight newly routed Ghidra entries account for 668 frontier bytes; the 128-byte
BLE event handler at `0x00052154` is an independently bounded manual provenance supplement, and
the already-routed 162-byte asynchronous SVCI initializer is now scatter/hash-pinned. The prepare
wrapper/finalize body and SVCI initializer are hashed as ordered segments. UUIDs, permissions,
event/authorization handling, opcode and advertising-name policy, SVCI completion, response
packet, source variant, hashes, and caller evidence are pinned in
[`NORDIC-BUTTONLESS-DFU-CLOSURE.md`](../closures/NORDIC-BUTTONLESS-DFU-CLOSURE.md).

The 88-byte Nordic `nrf_pwr_mgmt_shutdown` and 244-byte static `shutdown_process` now route to
SDK 17.1.0. Their exact mutex/state transitions, direct no-scheduler dispatch, handler-section
iteration, log flush, reset/System-OFF selection, SoftDevice check, terminal barriers, hashes, and
callers are pinned in
[`NORDIC-POWER-MANAGEMENT-CLOSURE.md`](../closures/NORDIC-POWER-MANAGEMENT-CLOSURE.md).

Twelve formerly unclassified reset-trace functions / 598 bytes are now closed. Eleven own the
R1-specific 16-byte retained record, Modbus-CRC lifecycle, tag/field clearing, address packing,
and capture policy. The fault wrapper at `0x0007A5E0` is separately bounded as an R1 adapter to
Nordic/CMSIS `NVIC_SystemReset`; no barrier, AIRCR, or reset-provider body is local. The composite
capture extent, exact body hashes, and complete direct caller sets are pinned in
[`RESET-TRACE-CORRELATION.md`](../correlation/RESET-TRACE-CORRELATION.md).

The adjacent boot reset-reason path closes two formerly unclassified functions / 834 bytes. The
754-byte decoder is R1 product behavior; the 80-byte boot lifecycle is bounded as an R1 adapter to
Nordic `nrf_power_resetreas_get/clear`. Exact reset masks, retained-SREQ gating, executable extents,
hashes, and callers are pinned in
[`RESET-REASON-CORRELATION.md`](../correlation/RESET-REASON-CORRELATION.md).

The 1,736-byte BLE-thread event consumer at `0x00045184` is now admitted as R1 product
orchestration. Its complete 2,450-byte range/hash, sole caller, product event switch, `pairAuth`
security request, two-target `advStart` policy, persistent-address call set, and advertising
decisions are pinned. Nordic Peer Manager/logging, CMSIS-FreeRTOS queue receive, and FreeRTOS heap
release remain provider-owned; unresolved logging/timer/role callees remain unclassified and are
not absorbed by this classification. See
[`CONNECTION-CONTROL-CORRELATION.md`](../correlation/CONNECTION-CONTROL-CORRELATION.md).

Five further static BLE helpers route directly to Nordic: `link_init`, `ram_end_address_get`,
`rank_highest`, `rank_vars_update`, and `set_security_req`. The last owns a six-byte inline jump table outside
Ghidra's counted function size; both ledger size and complete extent are pinned in
[`NORDIC-BLE-STATIC-HELPERS-CORRELATION.md`](../correlation/NORDIC-BLE-STATIC-HELPERS-CORRELATION.md).

Two exact FreeRTOS static-allocation callbacks are now separately admitted as R1 provider
configuration. They supply only the fixed idle/timer control blocks and 256-word stacks; all
scheduler and timer behavior remains in the authenticated FreeRTOS-Kernel 10.5.1 provider. See
[`FREERTOS-STATIC-MEMORY-CORRELATION.md`](../correlation/FREERTOS-STATIC-MEMORY-CORRELATION.md).
The adjacent 72-byte stack-overflow hook is likewise admitted only as R1 provider configuration:
FreeRTOS owns the four-word `0xA5A5A5A5` check, while the local callback owns the task diagnostic
and non-returning fail-stop policy. See
[`FREERTOS-STACK-OVERFLOW-CORRELATION.md`](../correlation/FREERTOS-STACK-OVERFLOW-CORRELATION.md).

The application `SystemInit` and its inlined-wait `nvmc_config` helper are now admitted as exact
Nordic SDK startup provider functions. Their 544 bytes remain entirely Nordic-owned; openR1 adds
only the recovered NFCT-as-GPIO and GPIO pin-reset build configuration. See
[`NORDIC-SYSTEM-INIT-CORRELATION.md`](../correlation/NORDIC-SYSTEM-INIT-CORRELATION.md).

The 98-byte `xfer_completeness_check` helper is also admitted as exact Nordic `nrfx_twim.c`
provider code. Its descriptor/EasyDMA checks, incomplete-transfer TWIM reset, and only two
callsites are body-pinned in
[`NORDIC-TWIM-COMPLETENESS-CORRELATION.md`](../correlation/NORDIC-TWIM-COMPLETENESS-CORRELATION.md).
Four further local-GATT, Service Changed, event-policy, and CAR-persistence functions are exact
Nordic Peer Manager provider routes; see
[`NORDIC-GATT-CACHE-CLOSURE.md`](../closures/NORDIC-GATT-CACHE-CLOSURE.md).

Under the owner-authorized full reduction (2026-08-14,
[`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md)), the six Bravechip-attributed
`unknown_*_candidate` families — 169 entries: generic device registry (43), GPIO-driven
software-TWI engines (40), sensor-stream framework (32), shared quantized-neural runtime (28),
time/calendar provider (16), and RTC-device layer (10) — are reconstructed from the recovered
decompilation evidence as independently compiled C under `r1/reconstructed/` with per-function
provenance banners and host tests. Their disposition is now
`clean_room_reimplementation_owner_authorized`; the family names are unchanged, no entry remains
`investigate_before_implementing`, and the reconstructions are not vendor source. The boundary
docs keep the attribution record; contract, divergences, and test mapping live in the
`../correlation/*-REDUCTION-CORRELATION.md` documents. On-target runtime adoption is a separate
wave; the SDK image stays byte-identical because the modules are unreferenced under
`--gc-sections`. The five GXT310 functions and all 17 QMA6100 provider/adapter functions are
separately reconstructed and host-tested under the same disposition; see the GXT310 and QMA6100
reduction correlation documents.

## Evidence quality

The bootloader ledger consumes the existing manually reviewed `function-names.csv`. Recovered
Nordic SDK, bundled nanopb, CryptoCell, and compiler-runtime symbols are routed to their providers.
The closing source-correlation pass resolved all 304 bootloader entries, so no synthetic bootloader
name remains. Qualified names distinguish duplicate static SDK symbols without treating the local
qualifier as an original binary identifier.

The application ledger accepts twenty-six kinds of evidence:

1. exact addresses already established in `PROVENANCE.md` for product-specific behavior;
2. function-local FlashDB/FAL control flow and release discriminators matched to pinned FlashDB
   2.0.0 with bundled FAL 0.5.99;
3. function-local vendor markers that create a candidate gate, the 203-entry SHA-pinned GoMore
   algorithm audit boundary, plus QST-authored QMA6100 V1.0 lineage evidence used to separate and
   validate the owner-authorized provider bodies and R1 adapters;
4. exact and function-local semantic correlation against ST's authenticated ST25DVxxKC component,
   including two BSim `1.0` anchors plus register, IO-table, chunking, and mailbox discriminators;
5. exact recovered R1 configuration wrappers whose underlying operation is delegated to a pinned
   provider, including GAP identity, advertising, GATT/bootstrap, BAE8, and Peer Manager adapters;
6. exact Nordic SDK literals or other function-local fingerprints together with matching event
   switches, constants, field behavior, and callees; generic template text is not sufficient;
7. exact standard C and Arm EABI runtime semantics and calling conventions, routed to the selected
   compiler runtime rather than locally reimplemented;
8. exact function-level control-flow correlations to the authenticated CMSIS-FreeRTOS v10.5.1
   wrapper, including its revision-distinguishing ISR event-flag behavior;
9. exact FreeRTOS-Kernel 10.5.1 function bodies whose list/queue/TCB/timer/`heap_4` control flow,
   `prvReloadTimer` discriminator, and authenticated CMSIS wrapper call sites identify specific
   upstream core symbols, together with Nordic SDK 17.1.0's exact nRF52 port bodies; address-range
   membership is explicitly rejected because product, Nordic storage, Bosch, FlashDB, DSP, and
   other code are interleaved in the apparent kernel interval;
10. exact CmBacktrace core control flow plus two revision-distinguishing fault-path features that
   bound the compatible upstream interval; mixed R1 hooks are recorded separately;
11. exact Bosch BMA456 SensorAPI bodies plus the v2.29.0 `delay_us` null-check discriminator, with
   product wrappers split into a separate adapter family; and
12. exact LIS2DW12 register/bit/control-flow bodies, with the `mdelay` context layout, pre-v2.2
   guarded interrupt routing, and valued reset setter bounding the compatible ST interval; and
13. the complete eight-function tiny-AES-c AES-128 inverse topology, including the 176-byte key
   schedule and exact `AddRoundKey`/inverse-transform/`Multiply`/`xtime` call graph; and
14. 52 compiler-emitted `nrf_gpio.h` inline instances whose P0/P1 decode, `PIN_CNF` packing,
   `IN`/`OUTSET`/`OUTCLR` offsets, sense masking, and latch read/clear bodies match the pinned SDK,
   plus adjacent exact `nrf_gpiote_event_clear` and `nrf_gpiote_event_is_set` instances; and
15. exact NFCT, PDM, PWM, RTC, SAADC, TIMER, and SPIM event/buffer inline helpers, including
   the NFCT DSB event clear and SAADC `RESULT.PTR`/`MAXCNT` register pair, plus the complete NFCT
   IRQ/field-event path with nRF52840 anomaly 190/218 behavior; and
16. the Nordic clock initialization/request cluster: legacy `nrf_drv_clock_init`, request-list
   enqueue/LF request, the two static legacy clock notification/IRQ functions missed by Ghidra,
   nrfx initialization/enable/LF-start, watchdog-running helper, and the exact S140 nested
   critical-region pair used around request state; and
17. exact Nordic millisecond/microsecond delay helpers, the complete legacy TWI bus-recovery and
   initialization path, two emitted legacy TX wrappers, five nrfx TWIM lifecycle/convenience APIs,
   both TWIM interrupt veneers and their shared static IRQ core, the SPIM2 interrupt/provider path,
   RAM validation, and the exact
   PRS acquire/release/box helpers, including the recovery routine's nine SCL pulses and STOP
   sequence; and
18. the complete nrfx GPIOTE input initialization, event enable/disable, and teardown API bodies
   plus their exact channel, configured-bitmask, pin-assignment, and polarity helpers, including
   high-accuracy channel events, low-power sense polarity, watcher/skip-setup flags, and conditional
   interrupt enablement; and
19. exact nrfx RTC enable/tick-enable and TIMER clear/enable driver APIs, plus the retained RTC2,
   TIMER2, and TIMER4 interrupt veneers and their shared static dispatchers, with control-block
   strides, state transitions, channel counts, callback ABI, and hardware task/event offsets pinned; and
20. the complete Nordic `nrfx_saadc` initialize, channel initialize/uninitialize, limits, blocking
   sample-convert, and uninitialize bodies, correlated to the pinned driver by state transitions,
   register setup, event polling, error paths, and callback ABI; and
21. fifteen SHA-pinned R1 TWI register-transfer/synchronization/lifecycle adapters whose framing,
   bounds, Nordic event values, CMSIS kernel-state gate, semaphore calls, tick conversion,
   64-microsecond delay calls, GPIO/TWI configuration, disable/uninitialize/power-cycle sequence,
   and Nordic-default pin release bound local policy without absorbing either provider
   implementation or the GPIO-driven bus engines.
22. six exact-extent R1 two-wire record-binding configurations whose fixed device-record and
   hardware semaphore setup is retained through direct typed providers without absorbing the
   unidentified global registry or software-I2C engines; and
23. forty exact-extent, SHA-pinned software-TWI bodies grouped into ten roles across four compiler
   instances, retained only as an unidentified-provider gate because semantic and byte-family
   evidence does not establish source/version/license; and
24. the adjacent RTC-device split: one exact Nordic `nrfx_rtc_init`, one R1 configuration-only
   record wrapper, and seven exact unidentified named-record/epoch/calendar/callback bodies; and
25. thirteen exact, SHA-pinned sensor-algorithm heap bodies, including five scatter-loaded
   functions, a two-bin tagged-block layout, the direct Goodix-candidate initialization edge, and
   `sensor_algo_mem_fatal`; retained only as an unidentified-provider gate after excluding both
   Nordic FreeRTOS `heap_4` and the pinned TLSF v3.1 implementation.
26. eight exact GoMore-linked composite initializer functions, including an exclusive edge from
   the already-gated sleep body, ten already-gated direct substate initializers, exact caller sets,
   and the context-resolved duplicate reset at `0x00071D96`.
   The initializer boundary remains GoMore-attributed, while the two byte-reset leaves are now
   source-admitted as one tested C body.

`inventory_source=manual_provenance_supplement` identifies audit- or instruction-confirmed entry
points absent from Ghidra's `functions.csv`. Their `end` and `size` remain blank unless exact extents
are independently proven; the ledger does not turn a nearest-address estimate into a false function
boundary. The recovered CLOCK statics, FlashDB helpers, motion call-table wrappers,
internal-flash adapters, and SAADC provider/adapters are current exceptions: their complete
return/tail-call, indirect-target, callback, or operation-table boundaries are proven and
byte-pinned. Ghidra's four-byte `0x00031FCC` NOP entry is also overridden with the independently
proven 412-byte battery-service extent ending before its literal pool.

[`FUNCTION-OWNERSHIP-SUMMARY.json`](FUNCTION-OWNERSHIP-SUMMARY.json) records provider/disposition
counts and hashes of the inventories used to create the ledger. The project verifier regenerates
the outputs and checks one-to-one coverage, so newly recovered functions cannot silently bypass
source admission.

This ledger does not authorize redistribution. Component licenses and version pins remain governed
by [`SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md) and `third-party/fetched/manifest.json`. It also does not
authorize changing boot verification, signing, rollback, ACL, or protection behavior.
