# Residual provider and production-readiness audit

Snapshot: 2026-08-14, after the Goodix democode residual re-audit, the platform-driver
increments, the six Bravechip-attributed middleware reductions, the five-entry GXT310 reduction,
the complete 17-entry QMA6100 provider/adapter reduction, the complete 36-entry YHM2710
reduction, and the 310-entry opaque Goodix / 198-entry GoMore reductions. This audit tracks what remains outside the R1-owned clean-room
boundary, why it remains there, and what the project does and does not claim today.

## Ledger totals

The generated ownership ledger
([`FUNCTION-OWNERSHIP.csv`](FUNCTION-OWNERSHIP.csv), summary in
[`FUNCTION-OWNERSHIP-SUMMARY.json`](FUNCTION-OWNERSHIP-SUMMARY.json)) covers **3,167
functions**: 2,863 application and 304 bootloader entries, comprising 2,991 Ghidra inventory
records plus 176 exact manual provenance supplements. **Zero entries remain unclassified**;
every recovered function carries an ownership disposition.

Disposition totals:

| Disposition | Entries |
| --- | ---: |
| `use_nordic_sdk` | 765 |
| `clean_room_behavior_only` (+ 9 `clean_room_behavior_only_security_preserving`) | 666 |
| `use_pinned_upstream` | 252 |
| `use_toolchain_runtime` | 129 |
| `use_authenticated_upstream_snapshot_and_nordic_port` | 110 |
| `use_authenticated_upstream_snapshot` | 63 |
| `use_nordic_sdk_bundled_upstream` | 43 |
| `use_nordic_supplied_provider` | 41 |
| `clean_room_adapter_only_*` / `clean_room_configuration_only_*` / `clean_room_data_model_only` (all variants) | 174 |
| `vendor_source_required_not_redistributable` | 172 |
| `clean_room_reimplementation_owner_authorized` | 752 |

The 172 `vendor_source_required_not_redistributable` entries are exactly the two
licensed-provider families below (164 + 8) and account for every remaining
implementation-blocking boundary. The 752 `clean_room_reimplementation_owner_authorized`
entries comprise the 165 functions in six Wuxi Bravechip ChipletRing/BCL603M middleware families,
five GXT310 entries, all 17 QMA6100 provider/adapter entries, all 36 YHM2710 entries,
331 Goodix functions, and 198 GoMore primitives/tensor-runtime routines. Under the owner-authorized full reduction
([`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md), 2026-08-14) these are reconstructed
from the decompilation evidence as independently compiled C under `r1/reconstructed/` with
per-function provenance and host tests. The reconstructions are not vendor source; on-target
runtime adoption and hardware validation remain open.

## Per-provider residual boundary table

| Provider family | Entries | Disposition | Boundary documentation | What would unblock it | Fail-closed behavior today |
| --- | ---: | --- | --- | --- | --- |
| Goodix GH3X2X closed algorithm libraries and allocator (`goodix_gh3x2x_candidate`) | 8 remaining (312 reconstructed) | `vendor_source_required_not_redistributable` / `clean_room_reimplementation_owner_authorized` | [`../boundaries/GOODIX-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-PROVIDER-BOUNDARY.md), [`../boundaries/GOODIX-DEMO-DRIVER-MAPPING-2026-08.md`](../boundaries/GOODIX-DEMO-DRIVER-MAPPING-2026-08.md), [`../correlation/GOODIX-PRIMITIVES-REDUCTION-CORRELATION.md`](../correlation/GOODIX-PRIMITIVES-REDUCTION-CORRELATION.md), [`../correlation/GOODIX-HEAP-REDUCTION-CORRELATION.md`](../correlation/GOODIX-HEAP-REDUCTION-CORRELATION.md), [`../correlation/QUANTIZED-RUNTIME-REDUCTION-CORRELATION.md`](../correlation/QUANTIZED-RUNTIME-REDUCTION-CORRELATION.md) | Continue the owner-authorized reduction. The local modules reconstruct 331 Goodix-family/public-democode/product entries in total, including 312 that were opaque. The complete heap core and call-site layer plus descriptor, record, channel, aggregate, outer-session, buffer-record, both generated graph builders, generated layer-block builder, first generated-model owner/graph/instance lifecycles, both complete generated graph executors and their three direct veneers, the complete signed-int8 grouped convolution executor, complete quantized layer executor, complete quantized recurrent executor/helper closure with both byte-equivalent range adjusters, four reusable generated-model stage pipelines, all five GH_HR integrity encoder/validator instantiations, packed-float conversion/vector closure, its shared float-vector scaling alternate entry, explicit NADT result and HRV configuration bindings, the complete nine-entry GH_HRV initialization/teardown/version lifecycle, strided incremental sample deviation and its float-buffer wrapper, the six-entry rolling-buffer family, the five-entry numerical post-processing family, the complete thirty-entry NADT accumulation/decision family, the complete seven-entry NADT peak-mask family, the four-entry NADT feature/statistics family, the four-entry feature-preparation/state family, the three-entry array-transformation/history/mask-row family, the three-entry counted-history/running-mean/Int16-deviation family, the single-record transition veneer, the four-entry sort/top-selection/extrema-index/reverse-packed-float family, the two-entry grouped-weighted-sum/event-pair-alignment family, the two-entry GH_HR cardinal-spline evaluator/sampler family, the GH_HR event-pair rebalancing leaf, the caller-scratch quartile-band median replacement leaf, the gated packed-6/9 triplicate workspace-expansion leaf, the GH_HR clamped-deviation mean-outlier counter, the exact GH_HR composite identity builder, the three-stage UInt8 tensor workspace pipeline, the three-entry 256-sample FFT magnitude closure, the capped NADT inference-input normalizer, the SpO2 running-mean/periodic-scale helper, the exact GH_SPO2/dlCom typed input-diagnostic emitter, the complete 36-byte SpO2 report analyzer, the complete NADT default/context initializer pair and selective state reset, the NADT peak dispersion/phase-quality estimator and Gaussian interval integrator, the GH_HR median-absolute-deviation inlier mask, the NADT reflected-boundary signed-int FIR kernel, the scattered SpO2/dlCom biquad cascade, the seven-bank packed-6/9 workspace expansion, the fixed five-channel normalized spectrum preparation, the seven-stage NADT generated-graph orchestrator and its fixed nineteen-operator subgraph with typed bindings, the one-record NADT flag/weighted-logistic quality updater, the fixed-125 dual-window autocorrelation/peak-feature extractor with exact Float16 quantization, the five-state NADT output selector with typed history and flags, the signal-confidence/state tracker with caller-owned 124-float interval workspace and rolling Gaussian probability, the complete GH_NADT preprocessing orchestrator with caller-owned replacements for all five transient allocations, the 50-sample NADT auxiliary state classifier, the SpO2 scaled decimal-residual extractor and rolling percentile selector, the two-stage NADT optical sample transform, the transient-history SpO2 indexed dispatch/logistic scorer, the five-history GH_HR weighted-feature pipeline, its local 25-phase periodic resampler, and the complete GH_HR secondary-context constructor plus typed primary/private-context constructor, the NADT three-lane direct/calibrated sample preparer and fixed-125 spectral peak-preparation pipeline, the GH_HR four-candidate position-band selector, the one-lane NADT generated-model inference bridge, the eleven-boundary plus uniform 23-tap NADT window filter, the NADT periodic-peak rate estimator, the strict spectral-peak/local-energy concentration estimator, the report candidate/three-phase event-latch wrapper, the four-channel packed population-deviation adapter, the packed three-group channel-record assembler and its explicit direct/width scaling implementation with typed table and pow bindings, the three-entry UInt8-deviation/positive-cosine/extrema-index family, the two-entry gated-triplet/threshold-crossing family, the two-entry local-peak/six-float-merge family, the masked sign-run zeroing leaf, the signed running-statistics leaf, the two-entry difference-equation/command-poller family, exact context and 25-slot record-family teardown, the caller-scratch median helper, typed seven-way dispatch and fixed-AA-payload adapters, the bounded NADT peak-quality leaf, paired modular autocorrelation transforms, the ordered register-reset wrapper, the input-word copy/typed-dispatch wrapper, the elapsed-gated dispatch/scaled-output wrapper, the Float32 half-away rounding leaf, the processing-context teardown, the two-entry default/configured in-place quantizer family, the exact GH_NADT identity builder, the fixed-bank NADT tensor projection, conditional float-buffer mean and standard-deviation wrappers, strict sample variance plus zero-safe sample/population variance and standard-deviation chains, the exact `0x0003754A` float-sort branch alias and `0x00037574` target, the mode-one three-buffer clear at `0x00036BFA` and its `0x0002F65C` thunk, selected-slot elapsed accounting at `0x00043B30` and its `0x00099010` thunk, adjacent quartic/peak-selector helpers, and SpO2 version report are now transparent C. Of the 174 public-democode entries, 17 compile locally and 157 still use pinned source. Closed algorithms, remaining graph builders, and private weight tables remain the principal work. | Live biometric paths still fail closed until their complete source closure is reconstructed and bound; the reconstructed heap operates only on caller-supplied memory and does not fabricate sensor output. |
| GoMore health/sleep algorithms (`gomore_health_algorithm_candidate`) | 164 remaining + 198 reconstructed (+ 3 gated R1 adapters) | `vendor_source_required_not_redistributable` / `clean_room_reimplementation_owner_authorized` | [`../boundaries/GOMORE-PROVIDER-BOUNDARY.md`](../boundaries/GOMORE-PROVIDER-BOUNDARY.md), the neural-runtime/sleep family boundary docs, [`../correlation/GOMORE-PRIMITIVES-REDUCTION-CORRELATION.md`](../correlation/GOMORE-PRIMITIVES-REDUCTION-CORRELATION.md), and [`../correlation/GOMORE-TENSOR-RUNTIME-REDUCTION-CORRELATION.md`](../correlation/GOMORE-TENSOR-RUNTIME-REDUCTION-CORRELATION.md) | Continue the owner-authorized reduction from the byte-pinned analysis. One hundred eighty-five record/vector/statistical/state/parser/preprocessing primitives and thirteen tensor-runtime routines are now transparent C; full classifiers, remaining formulas, state machines, graphs, and model data remain. | Health-index, sleep-classification, stress, and energy algorithm paths remain disabled until their complete closures are source-owned. Storage and wire layers do not synthesize values. |
| Wuxi Bravechip ChipletRing / BCL603M closed middleware — six `unknown_*_candidate` families | 165 | `clean_room_reimplementation_owner_authorized` | [`../boundaries/unknown_generic_device_registry_candidate-ATTRIBUTION-2026-08.md`](../boundaries/unknown_generic_device_registry_candidate-ATTRIBUTION-2026-08.md) and the five sibling `unknown_*-ATTRIBUTION-2026-08.md` reports; per-family boundary docs [`../boundaries/GENERIC-DEVICE-REGISTRY-BOUNDARY.md`](../boundaries/GENERIC-DEVICE-REGISTRY-BOUNDARY.md), [`../boundaries/SOFTWARE-TWI-PROVIDER-BOUNDARY.md`](../boundaries/SOFTWARE-TWI-PROVIDER-BOUNDARY.md), [`../boundaries/SENSOR-STREAM-FRAMEWORK-BOUNDARY.md`](../boundaries/SENSOR-STREAM-FRAMEWORK-BOUNDARY.md), [`../boundaries/QUANTIZED-POOLING-PROVIDER-BOUNDARY.md`](../boundaries/QUANTIZED-POOLING-PROVIDER-BOUNDARY.md), [`../boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md`](../boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md), [`../boundaries/RTC-DEVICE-PROVIDER-BOUNDARY.md`](../boundaries/RTC-DEVICE-PROVIDER-BOUNDARY.md) | Licensed acquisition from Bravechip (named commercial route via the byte-exact GATT base-UUID match to the public `BravechipSpace/ChipletRing-APPSDK` and the `603MV1.9.3` module string; contact xiaojian.cui@bravechip.com per the APPSDK README) or the ring ODM, with OTA-hex analysis as forensic fallback; or new attribution evidence for an individual family. All six were re-tested against fetched upstream sources in 2026-08 and remain NO ATTRIBUTION. A 2026-08-14 public-route re-check found Bravechip's only public repository to be phone-side-only (zero firmware identifiers), its official download list to offer app SDKs/datasheets only, and a second Bravechip-based ring product (`thuhci/OpenRing`) shipping no firmware source either — no public firmware-side source exists; see the updated `unknown_*-ATTRIBUTION-2026-08.md` reports. | All 165 functions are reconstructed host-side under the owner-authorized 2026-08 reduction: generic device registry (40), GPIO-driven software-TWI engines (40), sensor-stream framework (32), shared quantized-neural runtime (27), time/calendar provider (16), RTC-device layer (10). The modules compile into the SDK image but are not referenced by the runtime (the image stays byte-identical under `--gc-sections`); on-target adoption is a separate wave. OpenR1 continues to substitute typed admitted providers (Nordic TWIM, `nrfx_rtc`, R1-owned clock production) on hardware paths. |

The GXT310, QMA6100, and YHM2710 rows left the residual table in this reduction. Their exact stock hashes,
typed provider seams, safety divergences, and tests are recorded in
[`../correlation/GXT310-REDUCTION-CORRELATION.md`](../correlation/GXT310-REDUCTION-CORRELATION.md)
[`../correlation/QMA6100-REDUCTION-CORRELATION.md`](../correlation/QMA6100-REDUCTION-CORRELATION.md),
and [`../correlation/YHM2710-REDUCTION-CORRELATION.md`](../correlation/YHM2710-REDUCTION-CORRELATION.md).
The two algorithm primitive batches are recorded separately in
[`../correlation/GOODIX-PRIMITIVES-REDUCTION-CORRELATION.md`](../correlation/GOODIX-PRIMITIVES-REDUCTION-CORRELATION.md)
and [`../correlation/GOMORE-PRIMITIVES-REDUCTION-CORRELATION.md`](../correlation/GOMORE-PRIMITIVES-REDUCTION-CORRELATION.md).

No residual boundary is softened by proximity, naming, or behavioral similarity: absence of a
symbol is never treated as proof that code is eligible for rewriting
([`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md)).

## Coverage-row residual summary

[`COVERAGE.csv`](COVERAGE.csv) holds 92 rows: **41 implemented, 42 partial, 6 withheld,
2 separate, 1 excluded**.

### Partial rows grouped by remaining gate

Every partial row's remaining gate has been audited and classified as external. A row appears
under its primary gate; mixed gates are noted inline.

**Owned-hardware validation (14 rows).** The implementation is source-complete; what remains
is capture or confirmation on a physical ring.

- platform: S140 resource configuration (owned-hardware RAM negotiation); RTOS scheduler and
  task wake topology (physical timing, complete stock task census); legacy GAP advertising
  (durable factory/serial restore, physical validation); ATT MTU and data-length negotiation
  (negotiated values to be captured).
- protocol: BAE8 raw GATT event mapping (physical validation); 100/200/1000 scheduling and
  retry timing (physical saturation and timing-unit confirmation).
- security: queued-write rejection (owned-hardware ATT validation); crash unwind and retained
  diagnostics (authenticated export, hardware fault validation).
- storage: `kv.bin` four-snapshot class store, health database, sleep database (owned-ring
  migration/power-loss/lifecycle validation in each case).
- sensors: PMIC current and NFC rectifier conversion (physical transfer functions
  capture-gated).
- hardware: ST25DVxxKC dynamic NFC tag (mailbox transport, shared-power dock coexistence, and
  owned-hardware validation; secondarily reconstructed YHM board adoption).

**Licensed-provider acquisition (11 rows).** The R1-owned portion is implemented; the
remaining producer is a named absent licensed provider.

- health: heart-rate, SpO2, and HRV sample storage (Goodix optical, GoMore algorithms);
  heart-rate and SpO2 pipelines (Goodix optical acquisition/calculation); temperature and
  stress storage edge (GXCAS acquisition, GoMore stress generation); health crash snapshot
  (Goodix opaque blob lookup); activity and steps (step/locomotion/energy algorithms); sleep
  classification (only the GoMore classifier remains).
- sensors: nRF52840 SAADC acquisition and battery voltage/percentage behavior (reconstructed YHM
  power binding; secondarily hardware calibration); IQS7211E touch controller (reconstructed YHM
  shared power plus wear-lease identity; secondarily hardware validation).
- hardware: shared `i2c_5` and YHM2710 power ownership (reconstructed YHM board adoption and
  hardware validation).

**Bravechip-middleware runtime adoption (5 rows).** The remaining consumer or engine
belonged to a Bravechip-attributed family above; all five families are now reconstructed and
host-tested under the owner-authorized 2026-08 reduction, so the remaining gates are
on-target runtime adoption plus the secondarily named licensed providers.

- sensors: BMA456W and LIS2DW12 accelerometers (higher-level ingestion through the
  reconstructed sensor-stream framework, runtime adoption pending; secondarily owned-ring
  validation); GXT310 and PMIC temperature (reconstructed stream/timer providers, adoption
  pending; secondarily licensed GXCAS acquisition).
- health: HRV pipeline (sensor-stream topic transport reconstructed, adoption pending;
  secondarily Goodix optical RR production).
- platform: two-wire bus record bindings (reconstructed global registry and GPIO-driven
  software-I2C engines, adoption pending).

**Authorization-policy (7 rows).** The seam stays closed by product/security policy until a
deliberate, separately authorized decision, independent of source availability.

- system: `advStart` two-target connection control (command refused pending end-to-end
  authorization and owned-hardware validation); system settings REG1 policy (the regulator
  SVC `sd_power_dcdc_mode_set` is deliberately scoped out).
- security: Peer Manager bond and GATT-cache provider (product authorization; secondarily
  hardware persistence/replay validation); NV recovery merge (identity-bearing BLE sender and
  persistent mutation remain refused).
- protocol: channel-2 EUS BLE runtime (product authorization; secondarily physical timing
  validation).
- storage: pKey and EP stores (sensitive pKey/algorithm state pending licensing and key
  policy); log store (composite private reader and live sender excluded; no raw destructive
  controls are exposed).

### Withheld, separate, and excluded rows

The 6 **withheld** rows and their reasons: algorithm key provisioning (sensitive cloud/key
lifecycle lacks safe durable verification); NV recovery (destructive identity/calibration
restore lacks validated rollback); OTA and power controls (separated from the normal protocol
and deployment lifecycle); GH3X2X optical stack (licensed-provider gate; 499 provider entries);
GoMore floating-point neural runtime;
GoMore sleep-stage statistics. The software-TWI, RTC-device, and shared quantized-neural
runtime boundary rows left the withheld set under the owner-authorized 2026-08 reduction
(reconstructed with host tests; on-target runtime adoption pending).

The 2 **separate** rows: startup vectors and runtime (the linked Nordic/SDK application owns
placement; a standalone non-SDK bootable image is not a product target) and secure boot
signing, rollback, and recovery (no signing bypass or stock-verifier patch is implemented;
the deployment lifecycle stays separate per [`../SECURITY.md`](../SECURITY.md)).

The 1 **excluded** row: the health-daily synthetic test fixture, a dormant 1,344-byte
product-owned test body with no recovered caller, intentionally excluded from production.

## Production-readiness statement

Buildable and verified today, from a clean tree:

- the host protocol/device test suite (`make -C r1 test`);
- the AddressSanitizer/UndefinedBehaviorSanitizer build (`make -C r1 sanitize`);
- freestanding Cortex-M4F objects for every portable core translation unit
  (`make -C r1 arm-objects`);
- the host executable protocol/device simulator (`make -C r1 sim`);
- the linked nRF52840 application built from Nordic nRF5 SDK 17.1.0 sources against the
  S140 7.2.0 ABI, verified by `tools/verify_sdk_image.py` against pinned artifacts:
  BIN 127,400 bytes, BIN SHA-256
  `4bb7ad7cc81ab6030d027c495327719612ea7a32139ba757c06a6c8d3d2d0c36`, HEX SHA-256
  `b93d632817043161e138e97987d4f595520f87b3849e7126922b4e8d4c1eacbb`;
- the full evidence gate (`python3 tools/verify_openr1.py`), which reconciles the ownership
  ledger, the coverage ledger, the per-subsystem correlation summaries, and the Goodix
  democode mapping against the recovered images.

Explicitly **not** claimed:

- biometric, health-algorithm, power-management, temperature, touch-power, or neural-runtime
  functionality behind the absent licensed providers (Goodix and GoMore); the YHMICROS, GXCAS,
  QST, and Bravechip-attributed closures are reconstructed but still require board/runtime adoption;
  the Bravechip-attributed middleware families are reconstructed and host-tested but not yet
  adopted by the on-target runtime;
- hardware-validated behavior of any kind. No owned-ring validation has been performed;
  physical timing units, negotiated BLE values, sensor calibration, and analog transfer
  functions remain capture gates, and host-tested raw-tick constants are not relabeled as
  physical time.

The project's exact claim is: **"Source-complete for the R1-owned application contract above
declared licensed-provider boundaries."**

## Hardware-validation prerequisites

Closing the hardware-validation gates is a separately authorized lifecycle, not a build step.
Per [`../SECURITY.md`](../SECURITY.md), the portable sources contain no signing keys, no
UICR/MBR redirect logic, no APPROTECT manipulation, and no DFU validation toggles; producing
an unsigned development ELF is a build operation, while installing it on hardware requires
explicit authorization. The build system itself fails closed on any verification mismatch
(see the repository build documentation, `docs/build.md`). Any flashing, signing, UICR or
APPROTECT access, or MBR operation requires both explicit authorization and a written test
plan covering the validation target, the recovery path, and the fail-closed expectations
above; withheld commands additionally require the narrow API, state verification, and
interruption recovery that [`../SECURITY.md`](../SECURITY.md) enumerates.

## Unbound-by-design seams

These seams are deliberately left unbound rather than reconstructed from insufficient
evidence; each is a documented divergence, not an oversight.

- **Event-bus cross-context routing table** — it depends on RTOS task identity and mutable
  target state that the recovered evidence does not pin
  ([`../correlation/EVENT-BUS-CORRELATION.md`](../correlation/EVENT-BUS-CORRELATION.md)).
- **Stock per-id consumer dispatch `0x0008D888`** — the id-to-slot mapping is not recovered,
  so the consumer delivers same-context to every populated slot in ascending slot order
  instead of republishing cross-context.
- **Production event publishers** — none exist yet; a future publisher with class-specific
  listeners must first recover the id-to-slot mapping above.
- **Command/peer byte-order end-to-end reconciliation** — left unbound rather than inventing
  behavior; it is an end-to-end validation concern with the first-party sender
  ([`../correlation/CONNECTION-CONTROL-CORRELATION.md`](../correlation/CONNECTION-CONTROL-CORRELATION.md)).
- **REG1 regulator SVC `sd_power_dcdc_mode_set`** — deliberately scoped out of the system
  settings policy; regulator lifecycle is a deployment power decision, not an evidence gap.
- **`advStart` dispatch refusal** — the normal command remains refused until end-to-end
  authorization and owned-hardware validation, per the withheld-commands policy in
  [`../SECURITY.md`](../SECURITY.md).

## Reproducing this audit

```sh
make -C r1 test sanitize arm-objects sim
cd r1/platform/nrf52840/sdk && make clean && make SDK_ROOT=... default   # see docs/build.md
make -C r1 sdk-verify SDK_ROOT=...                                       # pinned-hash check
python3 r1/tools/verify_openr1.py
cd r1 && python3 tools/build_r1_source_ownership.py --check
```

The SDK image verification must pass against the existing pins without re-pinning; a hash
mismatch is a build anomaly to investigate, not an invitation to update the pin.
