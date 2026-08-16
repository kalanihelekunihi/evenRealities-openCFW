# Residual provider and production-readiness audit

Snapshot: 2026-08-16, after the source-built Goodix optical-transport/YHM lifecycle binding, the platform-driver
increments, the six Bravechip-attributed middleware reductions, the five-entry GXT310 reduction,
the complete 17-entry QMA6100 provider/adapter reduction, the complete 36-entry YHM2710
reduction, and the complete 320-entry opaque-Goodix / 360-entry GoMore reductions. This audit tracks what remains outside the R1-owned clean-room
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
| `vendor_source_required_not_redistributable` | 0 |
| `clean_room_reimplementation_owner_authorized` | 924 |

No `vendor_source_required_not_redistributable` executable entry remains. The 924
`clean_room_reimplementation_owner_authorized`
entries comprise the 165 functions in six Wuxi Bravechip ChipletRing/BCL603M middleware families,
five GXT310 entries, all 17 QMA6100 provider/adapter entries, all 36 YHM2710 entries,
339 Goodix functions, and all 362 GoMore primitives/tensor-runtime routines. Under the owner-authorized full reduction
([`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md), 2026-08-14) these are reconstructed
from the decompilation evidence as independently compiled C under `r1/reconstructed/` with
per-function provenance and host tests. The reconstructions are not vendor source; on-target
runtime adoption and hardware validation remain open.

## Per-provider residual boundary table

| Provider family | Entries | Disposition | Boundary documentation | What would unblock it | Fail-closed behavior today |
| --- | ---: | --- | --- | --- | --- |
| GoMore health/sleep algorithms (`gomore_health_algorithm_candidate`) | 0 remaining + 362 reconstructed (+ 3 gated R1 adapters) | `clean_room_reimplementation_owner_authorized` | [`../boundaries/GOMORE-PROVIDER-BOUNDARY.md`](../boundaries/GOMORE-PROVIDER-BOUNDARY.md), the neural-runtime/sleep family boundary docs, [`../correlation/GOMORE-PRIMITIVES-REDUCTION-CORRELATION.md`](../correlation/GOMORE-PRIMITIVES-REDUCTION-CORRELATION.md), and [`../correlation/GOMORE-TENSOR-RUNTIME-REDUCTION-CORRELATION.md`](../correlation/GOMORE-TENSOR-RUNTIME-REDUCTION-CORRELATION.md) | The executable reduction is complete: 343 primitive/shared-runtime routines and nineteen tensor-runtime routines are transparent C, including the complete sixteen-stage output orchestrator and every numerical, persistence, activity, locomotion, respiratory, energy, and sleep body it schedules. Continue only the explicit model/data-input and on-target integration audit. | Health-index, sleep-classification, and stress paths remain disabled until their explicit model/data inputs and source bindings are provisioned and hardware-validated. Storage and wire layers do not synthesize values. |
| Wuxi Bravechip ChipletRing / BCL603M closed middleware — six `unknown_*_candidate` families | 165 | `clean_room_reimplementation_owner_authorized` | [`../boundaries/unknown_generic_device_registry_candidate-ATTRIBUTION-2026-08.md`](../boundaries/unknown_generic_device_registry_candidate-ATTRIBUTION-2026-08.md) and the five sibling `unknown_*-ATTRIBUTION-2026-08.md` reports; per-family boundary docs [`../boundaries/GENERIC-DEVICE-REGISTRY-BOUNDARY.md`](../boundaries/GENERIC-DEVICE-REGISTRY-BOUNDARY.md), [`../boundaries/SOFTWARE-TWI-PROVIDER-BOUNDARY.md`](../boundaries/SOFTWARE-TWI-PROVIDER-BOUNDARY.md), [`../boundaries/SENSOR-STREAM-FRAMEWORK-BOUNDARY.md`](../boundaries/SENSOR-STREAM-FRAMEWORK-BOUNDARY.md), [`../boundaries/QUANTIZED-POOLING-PROVIDER-BOUNDARY.md`](../boundaries/QUANTIZED-POOLING-PROVIDER-BOUNDARY.md), [`../boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md`](../boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md), [`../boundaries/RTC-DEVICE-PROVIDER-BOUNDARY.md`](../boundaries/RTC-DEVICE-PROVIDER-BOUNDARY.md) | Licensed acquisition from Bravechip (named commercial route via the byte-exact GATT base-UUID match to the public `BravechipSpace/ChipletRing-APPSDK` and the `603MV1.9.3` module string; contact xiaojian.cui@bravechip.com per the APPSDK README) or the ring ODM, with OTA-hex analysis as forensic fallback; or new attribution evidence for an individual family. All six were re-tested against fetched upstream sources in 2026-08 and remain NO ATTRIBUTION. A 2026-08-14 public-route re-check found Bravechip's only public repository to be phone-side-only (zero firmware identifiers), its official download list to offer app SDKs/datasheets only, and a second Bravechip-based ring product (`thuhci/OpenRing`) shipping no firmware source either — no public firmware-side source exists; see the updated `unknown_*-ATTRIBUTION-2026-08.md` reports. | All 165 functions are reconstructed host-side under the owner-authorized 2026-08 reduction: generic device registry (40), GPIO-driven software-TWI engines (40), sensor-stream framework (32), shared quantized-neural runtime (27), time/calendar provider (16), RTC-device layer (10). The Zephyr target now adopts exact software `i2c_4` for Goodix optical transport; the other families and software-bus roles remain retained source awaiting typed consumers. OpenR1 continues to substitute typed admitted providers (Nordic TWIM, `nrfx_rtc`, R1-owned clock production) on the other hardware paths. |

Goodix has left the residual table: all 320 formerly opaque provider-candidate entries now map to
owner-authorized transparent C, alongside seventeen public-democode replacements and two R1
product entries. The final admitted function is the complete 1,370-byte SpO2/dlCom processing root
at `0x0006C6A8`; the Goodix total is 339 mappings / 66,288 declared bytes.

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

[`COVERAGE.csv`](COVERAGE.csv) holds 92 rows: **41 implemented, 43 partial, 5 withheld,
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
- hardware: ST25DVxxKC source mailbox transport, P1.10 dock lifecycle, dock-session mutex, and
  TWIM1 handoff are linked on the alternate target; explicit activation policy and owned-hardware
  coexistence validation remain.

**Source-admitted algorithm / live-provider adoption (12 rows).** The R1-owned portion and all
inventoried Goodix/GoMore executable bodies are implemented; the remaining work is live typed
composition with sensor, persistence, and hardware providers.

- sensors: GH3X2X raw acquisition now has source Goodix demo/driver, recovered software-`i2c_4`,
  GPIO/interrupt, motion-feed, and YHM-client lifecycle bindings; the global algorithm frame/result
  ABI and hardware validation remain fail-closed.
- health: heart-rate, SpO2, and HRV sample storage (Goodix result and typed GoMore integration);
  heart-rate and SpO2 pipelines (Goodix democode-ABI composition over the bound raw acquisition);
  temperature and stress storage edge (GXCAS acquisition and GoMore output composition); health
  crash snapshot (typed Goodix state lookup); activity/steps and sleep classification (transparent
  algorithms and models are retained, with live sensor/state/result bindings still required).
- sensors: nRF52840 SAADC acquisition and battery voltage/percentage behavior (YHM client-bit-0
  binding is live; periodic production and hardware calibration remain); IQS7211E transport,
  lifecycle, and YHM client-bit-2 binding are linked, with wear-lease identity and hardware
  validation still required for live sampling.
- hardware: shared `i2c_5` and YHM2710 power ownership (battery, touch, and optical clients are
  adopted; hardware electrical validation remains).

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
- platform: two-wire bus record bindings (software `i2c_4` is adopted by the Zephyr optical path;
  reconstructed global-registry and other GPIO-driven software-I2C engines remain pending).

**Authorization-policy (7 rows).** The seam stays closed by product/security policy until a
deliberate, separately authorized decision, independent of source availability.

- system: `advStart` two-target connection control (command refused pending end-to-end
  authorization and owned-hardware validation). The alternate Zephyr target now replaces
  the system-settings REG1 SVC with the pinned source nRF POWER HAL; its separate wear-driven
  automatic policy still awaits typed wear/touch/shared-power integration.
- security: Peer Manager bond and GATT-cache provider (product authorization; secondarily
  hardware persistence/replay validation); NV recovery merge (identity-bearing BLE sender and
  persistent mutation remain refused).
- protocol: channel-2 EUS BLE runtime (product authorization; secondarily physical timing
  validation).
- storage: pKey and EP stores (sensitive pKey/algorithm state pending licensing and key
  policy); log store (composite private reader and live sender excluded; no raw destructive
  controls are exposed).

### Withheld, separate, and excluded rows

The 5 **withheld** rows and their reasons: algorithm key provisioning (sensitive cloud/key
lifecycle lacks safe durable verification); NV recovery (destructive identity/calibration
restore lacks validated rollback); OTA and power controls (separated from the normal protocol
and deployment lifecycle); GoMore floating-point neural runtime;
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
  BIN 347,408 bytes, BIN SHA-256
  `262d60f28facf57bf5bf6c0daf2b8a7434a6b1865913d69ceafa5a1979233d95`, HEX SHA-256
  `f24a06fd32fda2bec45738619d188a55f313fb03dffc73c903a5200df10071d7`;
- an application-only owner DFU package whose three-member boundary excludes stock application,
  SoftDevice, bootloader, and vendor algorithm blobs; it still declares and requires the
  preinstalled S140 ABI `0x0100`, as documented in
  [`APPLICATION-BUNDLE-BOUNDARY.md`](../closures/APPLICATION-BUNDLE-BOUNDARY.md);
- an alternate source-built Zephyr/MCUboot full-flash bundle whose executable members require no
  S140 or retail bootloader, whose signed application retains all 14 reconstructed modules, and
  whose source revisions, flash ranges, canonical member union, and ECDSA-P256 signature are
  verified as documented in
  [`SOURCE-BUILT-ZEPHYR-BUNDLE.md`](../closures/SOURCE-BUILT-ZEPHYR-BUNDLE.md);
- the full evidence gate (`python3 tools/verify_openr1.py`), which reconciles the ownership
  ledger, the coverage ledger, the per-subsystem correlation summaries, and the Goodix
  democode mapping against the recovered images.

Explicitly **not** claimed:

- live runtime adoption of the retained Goodix/GoMore biometric and health algorithms and several
  reconstructed YHMICROS, GXCAS, QST, and Bravechip-attributed closures; their executable bodies
  and generated-model parameters compile from transparent source, but the current Goodix democode
  ABI bridge remains fail-closed and multiple board/provider paths still need typed integration;
- complete sensor/health-record/power/product integration on the alternate source-built BLE/boot target;
  its BAE8/core runtime, persistent SMP settings, KV/health/sleep storage, exact SAADC routes,
  phone-synchronized clock, reset-reason trace, scheduler watchdog, pinned Bosch/ST motion
  acquisition, fail-closed IQS7211E transport/lifecycle, reconstructed YHM shared power, and
  ST25DVxxKC mailbox/P1.10/TWIM1 handoff are linked, but motion production ingestion, touch
  identity/wear provisioning, explicit NFC activation policy, destructive health slot-0
  format/retry and GoMore actions, unresolved cursor persistence, Goodix global algorithm frame/result composition,
  fatal-trace validation, and
  retail-layout migration still require owned-ring work;
- hardware-validated behavior of any kind. No owned-ring validation has been performed;
  physical timing units, negotiated BLE values, sensor calibration, and analog transfer
  functions remain capture gates, and host-tested raw-tick constants are not relabeled as
  physical time.

The project's exact current claim is: **"All inventoried application and bootloader executable
entries are source-routed, all Goodix/GoMore algorithm bodies and model parameters are transparent
source, and an alternate signed full-flash bundle builds its BLE/controller and boot path from
pinned source without S140 or the retail bootloader; remaining gaps are hardware/provider
integration and owned-ring validation."**

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
- **Wear-driven REG1 automation** — direct startup and authorized settings actions are
  source-bound on the alternate Zephyr target, but automatic worn/removal transitions remain
  disabled until the recovered wear and touch-lease lifecycle is integrated and hardware-validated.
  The shared-power provider is bound, but the implementation does not infer CPU frequency or
  physical regulator state.
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
