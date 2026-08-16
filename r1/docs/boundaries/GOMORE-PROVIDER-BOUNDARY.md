# GoMore health-algorithm provider boundary

> Current owner-authorized reduction note: all 362 candidate entries now compile from
> transparent C (343 primitives/shared-runtime routines and nineteen tensor-runtime routines); no executable body remains gated. The attribution and
> callgraph census below remains valid, while source-admitted entries are tracked in the two
> `GOMORE-*-REDUCTION-CORRELATION.md` reports.

## Decision

The recovered application contains GoMore-specific health-index, authorization, persistence,
sensor-allocation, sleep, and update diagnostics. These are direct vendor-origin indicators, but
they do not identify an exact SDK release or establish redistribution rights. Public company
materials describe GoMore as a wearable health/fitness algorithm and licensing provider; no
redistributable source package matching the R1 evidence has been authenticated.

openR1 therefore classifies the complete functions containing these markers, plus exact
functions already covered by the SHA-pinned GoMore algorithm audit, as
`gomore_health_algorithm_candidate` with disposition
`vendor_source_required_not_redistributable`. This is deliberately conservative: a marked
function can combine R1 storage or scheduling glue with provider calls, so the classification is
a hard investigation gate, not a claim that every instruction in the function belongs to GoMore.

## Byte-pinned candidate functions

| Recovered entry | Size | Function-local evidence |
| --- | ---: | --- |
| `0x00049410` | 506 | GoMore idle-timer creation/deletion diagnostics |
| `0x0004BD98` | 768 | `gomore_setAuthParameters`, `gomore_setAuth`, health-index initialization, and initialization-failure diagnostics |
| `0x0006AD80` | 282 | GoMore pKey flash, presence, and CRC diagnostics; now source-admitted as `gomore_primitives_pkey_load` with explicit storage bindings |
| `0x0006AFB0` | 180 | GoMore previous-data restoration diagnostics; now source-admitted as `gomore_primitives_previous_state_restore` |
| `0x0006B27C` | 374 | GoMore pKey and authorization-parameter orchestration; now source-admitted as `gomore_primitives_auth_parameters_setup` with explicit key, UUID, time, and authorization bindings |
| `0x0006B50C` | 318 | GoMore sensor/sleep allocation and forced-wake diagnostics |
| `0x0006C1C0` | 114 | GoMore index-update diagnostics |
| `0x0006C294` | 456 | GoMore sensor-allocation diagnostics |
| `0x000823D8` | 106 | retained `GoMoRe` product/provider label |

The ownership verifier pins all ten bodies by exact size and SHA-256. Address proximity is not
used to classify adjacent functions.

## Audit-scoped algorithm functions

The firmware audit independently pins another 259 exact function entries. These are not inferred
from a broad address interval: each entry begins a code-only range whose bytes, constants, and
direct-call relationships are checked by at least one read-only audit. Overlap between scopes is
expected because an output producer can also participate in the sleep or energy pipeline.

| Audited scope | Exact entries |
| --- | ---: |
| energy pipeline | 14 |
| respiratory/motion/step algorithm domains | 59 |
| complete GoMore output producers | 24 |
| dormant estimator | 42 |
| heart-rate selector | 6 |
| SPS speed selector | 15 |
| sleep algorithm | 75 |
| composite sensor-algorithm initializer boundary | 8 |
| floating-point neural runtime | 1 |
| paired sleep-classifier graphs | 6 |
| activity-state window classifier | 6 |
| energy-model dispatcher/estimators | 9 |
| private IIR coefficient designer | 1 |
| SDK authorization parser | 1 |
| sleep-stage statistics closure | 3 |
| unique additional entries | 259 |

Together with the ten direct diagnostic-marker functions, the original attribution ledger contained
269 GoMore-gated functions. Current per-entry admission is recorded in the generated ownership
ledger and the reduction note above. The newest three additions at that audit stage were private sleep-step orchestrator
`0x00094070`, rolling accumulator `0x000947DE`, and reset helper `0x00071B24`, documented in
[`FRONTIER-230-248-CORRELATION.md`](../correlation/FRONTIER-230-248-CORRELATION.md). The accumulator and reset
helper and orchestration root now have transparent typed reconstructions. The preceding ten additions
are the floating-point pooling executor and
constructor plus the private sleep/history force-wake reducer, wrappers, weighted merge, snapshot
selector, tail reconciliation, timestamp setter, and two-bit extraction/lookup helpers documented
in [`FRONTIER-256-262-CORRELATION.md`](../correlation/FRONTIER-256-262-CORRELATION.md); all ten now have transparent typed reconstructions. The preceding three additions are the 274-byte private timestamp-to-sample
segment expansion at `0x00067C30`, its exclusive 44-byte fill helper at `0x000641C4`, and the
264-byte fixed-coefficient IIR filter at `0x00064274`. The fill helper and IIR filter are source-admitted while the segment expansion remains gated; see
[`FRONTIER-264-274-CORRELATION.md`](../correlation/FRONTIER-264-274-CORRELATION.md). The preceding two additions are the 314-byte private convolution tensor
operator at `0x00091B08` and the 314-byte private batch-normalization tensor operator at
`0x000651CA`. The batch-normalization operator is now transparent as
`gomore_tensor_batch_normalize_half`; the convolution operator is now transparent as
`gomore_tensor_conv1d_half`. The preceding additions were the 336-byte
generated sleep-model tensor graph at `0x000653E6` and the 334-byte energy-estimator state update
at `0x00090ACC`; both are now source-admitted as `gomore_tensor_cell_run` and
`gomore_primitives_energy_mode_rate`. The supplemental 350-byte sensor-update orchestrator at
`0x00094384` is now source-admitted as `gomore_primitives_sensor_update_orchestrate`; its
diagnostics, input application, and snapshot steps are explicit typed providers, while validation,
timestamp normalization, stale rejection, state commit, and update-counter behavior are local. The
352-byte motion-gate accumulator at `0x0005F264` is now source-admitted as
`gomore_primitives_motion_gate_accumulate`; its 30-second circular buckets, short-gap fill,
540-second reset, weighted score, and exact bias predicate are transparent. The
newest three-function / 796-byte closure pins both final
sleep-statistics blocks and their exclusive stage lookup helper; see
[`GOMORE-SLEEP-STAGE-STATISTICS-PROVIDER-BOUNDARY.md`](GOMORE-SLEEP-STAGE-STATISTICS-PROVIDER-BOUNDARY.md).
The earlier one-function / 528-byte closure pins the SDK authorization parser and dispatcher at
`0x0008EA0C`; see
[`GOMORE-AUTH-PARSER-PROVIDER-BOUNDARY.md`](GOMORE-AUTH-PARSER-PROVIDER-BOUNDARY.md). It is now
source-admitted with caller-supplied decrypt keys and typed dispatch callbacks. The earlier
nine-function / 2,360-byte closure pins the energy-model dispatcher and its three estimator
families; all nine are now transparent C, including the 81 table values; see
[`GOMORE-ENERGY-MODEL-PROVIDER-BOUNDARY.md`](GOMORE-ENERGY-MODEL-PROVIDER-BOUNDARY.md).
The prior six-function / 1,890-byte closure pins the activity-state
window classifier, its five private helpers, three embedded dispatch tables, and literal pool;
see
[`GOMORE-ACTIVITY-STATE-PROVIDER-BOUNDARY.md`](GOMORE-ACTIVITY-STATE-PROVIDER-BOUNDARY.md).
All six entries are now source-admitted, including the complete seven-state top-level routine as
`gomore_primitives_activity_window_update`.
The prior six-function / 2,188-byte closure pins the paired sleep-classifier graph builders,
family selector, allocator table, and both model regions; see
[`GOMORE-SLEEP-GRAPH-PROVIDER-BOUNDARY.md`](GOMORE-SLEEP-GRAPH-PROVIDER-BOUNDARY.md). Every exact address and its applicable audit scopes are recorded in
[`FUNCTION-OWNERSHIP.csv`](../reference/FUNCTION-OWNERSHIP.csv); the immutable ranges and hashes remain in the
corresponding `summarize_r1_*` audit scripts. This expansion routes already-proven vendor-algorithm
work away from local implementation without inventing private symbol names.

The newest eight-entry initializer boundary contains the composite initializer at `0x00071A32` and seven
private or already-vendor-rooted helpers. The root is called only at `0x0006FFAE` from the
SHA-pinned GoMore sleep body at `0x0006FEA0`; it initializes ten already gated GoMore substates
plus the newly bounded helpers. The 8-byte reset at `0x00071D96` is byte-identical to the already
gated reset at `0x0007170A`, but the classification relies on this exclusive call context rather
than on generic bytes alone. The complete 586-byte census and caller sets are pinned by
`../../tools/evidence/summarize_r1_gomore_initializer_boundary.py`.
All eight entries in this boundary are now owner-authorized local C. The composite root is
`gomore_primitives_composite_engine_initialize`; it composes the locally reconstructed child
initializers through typed callbacks and explicit configuration/binding inputs without retaining
an absolute firmware address. This changes source disposition without erasing the callgraph
attribution evidence.

The calling sleep body at `0x0006FEA0` has now crossed the same owner-authorized source gate as
`gomore_primitives_sleep_algorithm_initialize`. Its authorization configuration, random providers,
previous-state storage and 32-bit target binding, user profile, time configuration, and initializer
callbacks are all explicit. The local body preserves the exact 736-byte previous-state gate,
status/random/binding offsets, scattered nested profile fields, composite initializer chain, and
default profile-state transition without retaining the stock global pointer table or any firmware
payload.

The earlier audit treated `GH_HRV_pre_pv_v1.0.1.0_ed953ff3` as a GoMore version marker. Goodix's
primary-source developer trace reproduces that exact string and identifies it as a GH3X2X
algorithm version, so `0x0006DF60` is now correctly routed to the Goodix boundary instead.

Four audited algorithm entries and two product adapter entries were absent from Ghidra's function
inventory. The verifier now treats their independently established code extents as manual
provenance supplements:

| Entry | Size | SHA-256 | Ownership |
| --- | ---: | --- | --- |
| `0x00067488` | 196 | `b351faf207bd93a95557dd695eb7e034dfb92bb02be730ae6e118d8372602991` | GoMore dormant-estimator candidate; now source-admitted as `gomore_primitives_dormant_speed_mode1_target_update` |
| `0x0006825C` | 232 | `346de4b3b4a920d11fd3aaf7dd930854b7ce8eb02fc26568f9016c9febe1cf84` | GoMore dormant-estimator candidate; now source-admitted as `gomore_primitives_dormant_speed_mode0_target_update` |
| `0x0007D09C` | 12 | `90e8db1c4218cea4a6d0b8bfb3599ff589e62348c9b0160696c2decc158a8687` | GoMore sleep-score helper candidate |
| `0x0008F49C` | 24 | `4a6d354d9870c5323d26f51a42612488eccd79558d670938dae0574926e17aa2` | GoMore logistic helper candidate |
| `0x0006B114` | 164 | `12d48128ccaab3563434e1020cafeae53af5c37848aa5e7df228776cfd3139e4` | R1 accelerometer-topic adapter |
| `0x0006B228` | 74 | `ab337651b4344af149b261e8c0e733690a02df92bffcb5b79ee4370e7b8b3134` | R1 raw-heart-rate-topic adapter |

The accelerometer adapter clamps the sample count to 25, converts packed signed XYZ samples into
the provider input layout, sets its readiness bit, and enters the common update path. The raw-HR
adapter applies the same 25-sample bound, converts unsigned readings to the provider numeric form,
sets its readiness bit, and enters that path. These bounded input seams may be implemented locally,
but they must remain disabled until a licensed GoMore provider supplies the underlying algorithm.
Nine other audit-range starts omitted by Ghidra are data/table addresses or an instruction inside
an existing function, so they are intentionally not fabricated as functions.

## Admission requirements

Before this path can be enabled, the project requires a lawfully obtained GoMore package whose
version, binary/source hashes, ABI, target architecture, license, and redistribution terms are
recorded in `third-party/fetched/manifest.json`. Function-level comparison must then split provider
implementation from any bounded R1 configuration, storage, transport, or scheduling adapters.

Until that happens, openR1 may document observable input/output behavior and preserve integration
interfaces, but it must not recreate the GoMore health or sleep algorithms locally.

## Attribution re-examination 2026-08

A 2026-08 audit found no public GoMore source: the Bravechip ChipletRing-APPSDK ships only
app-side wrappers over the closed `LmAPI` AAR, and the only located embedded GoMore SDK copy
(an unlicensed Jieli BR28 watch-SDK dump with `GoMoreLib.h` and a DWARF-carrying
`libgomore.a`) is binary-only and unlicensed — retained as ABI/correlation evidence only
(R1 strings `[sdkAuth]=%d`, `gomore healthIndexInitUser failed:%d`,
`gomore updateIndex failed:%d` match verbatim). At that attribution-audit stage all 362 entries
were blocked; the current owner-authorized reductions are tracked in the note above.
Full evidence: [`withheld-providers-ATTRIBUTION-2026-08.md`](withheld-providers-ATTRIBUTION-2026-08.md).
