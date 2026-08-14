# Residual provider and production-readiness audit

Snapshot: 2026-08-14, after the Goodix democode residual re-audit and the platform-driver
increments. This is the closing audit of what remains outside the R1-owned clean-room
boundary, why it remains there, and what the project does and does not claim today.

## Ledger totals

The generated ownership ledger
([`FUNCTION-OWNERSHIP.csv`](FUNCTION-OWNERSHIP.csv), summary in
[`FUNCTION-OWNERSHIP-SUMMARY.json`](FUNCTION-OWNERSHIP-SUMMARY.json)) covers **3,165
functions**: 2,861 application and 304 bootloader entries, comprising 2,991 Ghidra inventory
records plus 174 exact manual provenance supplements. **Zero entries remain unclassified**;
every recovered function carries an ownership disposition.

Disposition totals:

| Disposition | Entries |
| --- | ---: |
| `use_nordic_sdk` | 765 |
| `clean_room_behavior_only` (+ 9 `clean_room_behavior_only_security_preserving`) | 667 |
| `use_pinned_upstream` | 269 |
| `use_toolchain_runtime` | 129 |
| `use_authenticated_upstream_snapshot_and_nordic_port` | 110 |
| `use_authenticated_upstream_snapshot` | 63 |
| `use_nordic_sdk_bundled_upstream` | 43 |
| `use_nordic_supplied_provider` | 41 |
| `clean_room_adapter_only_*` / `clean_room_configuration_only_*` / `clean_room_data_model_only` (all variants) | 189 |
| `vendor_source_required_not_redistributable` | 725 |
| `investigate_before_implementing` | 164 |

The two implementation-blocking dispositions account for every residual boundary. The 725
`vendor_source_required_not_redistributable` entries are exactly the five licensed-provider
families below (362 + 319 + 36 + 5 + 3). The 164 `investigate_before_implementing` entries
are exactly the six unidentified-provider families attributed in 2026-08 to Wuxi Bravechip's
closed ChipletRing / BCL603M platform middleware.

## Per-provider residual boundary table

| Provider family | Entries | Disposition | Boundary documentation | What would unblock it | Fail-closed behavior today |
| --- | ---: | --- | --- | --- | --- |
| Goodix GH3X2X closed algorithm libraries and allocator (`goodix_gh3x2x_candidate`) | 319 | `vendor_source_required_not_redistributable` | [`../boundaries/GOODIX-PROVIDER-BOUNDARY.md`](../boundaries/GOODIX-PROVIDER-BOUNDARY.md), [`../boundaries/GOODIX-DEMO-DRIVER-MAPPING-2026-08.md`](../boundaries/GOODIX-DEMO-DRIVER-MAPPING-2026-08.md), [`../boundaries/goodix_gh3x2x_candidate-ATTRIBUTION-2026-08.md`](../boundaries/goodix_gh3x2x_candidate-ATTRIBUTION-2026-08.md), [`../boundaries/SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md`](../boundaries/SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md) | A licensed Goodix GH3X2X SDK whose algorithm libraries may lawfully be integrated. The public democode snapshot (democode v1.6 / DrvLib v4.3.0.0, exact version-marker match) maps 174 demo-kernel/driver/AGC/algo-call entries now routed to `use_pinned_upstream`, but its clause 5 forbids reverse engineering the binary-only algorithm archives, those archives target STAR-MC1 Armv8-M and are unlinkable on the Cortex-M4F, and 23 entries remain documented-unprovable after three mapping passes. | The retained R1 selector operates only over caller-supplied provider snapshots. No live optical-sensor access, no biometric synthesis, no algorithm, model, graph, weight, or allocator reconstruction. Unsupported without a bound licensed provider; no fabricated data. |
| GoMore health/sleep algorithms (`gomore_health_algorithm_candidate`) | 362 (+ 3 gated R1 adapters) | `vendor_source_required_not_redistributable` | [`../boundaries/GOMORE-PROVIDER-BOUNDARY.md`](../boundaries/GOMORE-PROVIDER-BOUNDARY.md) and the neural-runtime, sleep-graph, sleep-stage-statistics, energy-model, IIR-designer, auth-parser, and activity-state boundary docs; [`../boundaries/withheld-providers-ATTRIBUTION-2026-08.md`](../boundaries/withheld-providers-ATTRIBUTION-2026-08.md) | An authenticated licensed GoMore embedded SDK. The 2026-08 audit found no public GoMore source; the only located embedded copy is an unlicensed binary-only Jieli SDK dump, retained as ABI/correlation evidence only. | Health-index, sleep-classification, stress, and energy algorithm paths disabled. Storage and wire layers accept only provider-produced values; nothing synthesizes them. |
| YHMICROS YHM2710 PMIC (`yhmicros_yhm2710_candidate`) | 36 (+ 5 R1 resource adapters) | `vendor_source_required_not_redistributable` | [`../boundaries/YHM2710-I2C5-RESOURCE-BOUNDARY.md`](../boundaries/YHM2710-I2C5-RESOURCE-BOUNDARY.md), [`../boundaries/NAMED-PERIPHERAL-BOUNDARIES.md`](../boundaries/NAMED-PERIPHERAL-BOUNDARIES.md), [`../boundaries/withheld-providers-ATTRIBUTION-2026-08.md`](../boundaries/withheld-providers-ATTRIBUTION-2026-08.md) | Lawfully obtained licensed YHM2710 driver source matching the recovered single-wire transport. | The three-client battery/optical/touch lease calls one abstract semantic provider. No raw YHM register constants, no wire sender, and the SAADC battery path stays fail-closed. |
| GXCAS GXT310 temperature (`gxcas_gxt310_candidate`) | 5 | `vendor_source_required_not_redistributable` | [`../boundaries/NAMED-PERIPHERAL-BOUNDARIES.md`](../boundaries/NAMED-PERIPHERAL-BOUNDARIES.md), [`../boundaries/withheld-providers-ATTRIBUTION-2026-08.md`](../boundaries/withheld-providers-ATTRIBUTION-2026-08.md) | Hash, license-review, and comparison of the official 2025 GXT310 STM32 driver V1.0 archive (retrieved in 2026-08; a license-free demo usable as a documentation pointer only), or a proven clean product-port boundary. | Dual temperature-sensor acquisition gated; product-owned range/offset/aggregation policy is implemented but consumes only provider-produced samples. |
| QST QMA6100 accelerometer (`qst_qma6100_v1_0_lineage_unlicensed`) | 3 (+ 14 bounded R1 adapters) | `vendor_source_required_not_redistributable` | [`../boundaries/NAMED-PERIPHERAL-BOUNDARIES.md`](../boundaries/NAMED-PERIPHERAL-BOUNDARIES.md), [`../boundaries/withheld-providers-ATTRIBUTION-2026-08.md`](../boundaries/withheld-providers-ATTRIBUTION-2026-08.md) | Licensed official QST source plus installed-part confirmation. The 2026-08 audit identified licensed public QMA6100P drivers (RIOT LGPL-2.1, Espressif Apache-2.0) that document the register map for any future datasheet-based rewrite. | Omitted from the motion probe order (stock order LIS2DW12, BMA456W, then unavailable QMA6100). No local driver reconstruction. |
| Wuxi Bravechip ChipletRing / BCL603M closed middleware — six `unknown_*_candidate` families | 164 | `investigate_before_implementing` | [`../boundaries/unknown_generic_device_registry_candidate-ATTRIBUTION-2026-08.md`](../boundaries/unknown_generic_device_registry_candidate-ATTRIBUTION-2026-08.md) and the five sibling `unknown_*-ATTRIBUTION-2026-08.md` reports; per-family boundary docs [`../boundaries/GENERIC-DEVICE-REGISTRY-BOUNDARY.md`](../boundaries/GENERIC-DEVICE-REGISTRY-BOUNDARY.md), [`../boundaries/SOFTWARE-TWI-PROVIDER-BOUNDARY.md`](../boundaries/SOFTWARE-TWI-PROVIDER-BOUNDARY.md), [`../boundaries/SENSOR-STREAM-FRAMEWORK-BOUNDARY.md`](../boundaries/SENSOR-STREAM-FRAMEWORK-BOUNDARY.md), [`../boundaries/QUANTIZED-POOLING-PROVIDER-BOUNDARY.md`](../boundaries/QUANTIZED-POOLING-PROVIDER-BOUNDARY.md), [`../boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md`](../boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md), [`../boundaries/RTC-DEVICE-PROVIDER-BOUNDARY.md`](../boundaries/RTC-DEVICE-PROVIDER-BOUNDARY.md) | Licensed acquisition from Bravechip (named commercial route via the byte-exact GATT base-UUID match to the public `BravechipSpace/ChipletRing-APPSDK` and the `603MV1.9.3` module string), or new attribution evidence for an individual family. All six were re-tested against fetched upstream sources in 2026-08 and remain NO ATTRIBUTION. | All 164 functions stay implementation-blocked: generic device registry (40), GPIO-driven software-TWI engines (40), sensor-stream framework (32), shared quantized-neural runtime (26), time/calendar provider (16), RTC-device layer (10). OpenR1 substitutes typed admitted providers (Nordic TWIM, `nrfx_rtc`, R1-owned clock production) where validated and otherwise leaves the seams unsupported. |

No residual boundary is softened by proximity, naming, or behavioral similarity: absence of a
symbol is never treated as proof that code is eligible for rewriting
([`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md)).

## Coverage-row residual summary

[`COVERAGE.csv`](COVERAGE.csv) holds 92 rows: **41 implemented, 37 partial, 11 withheld,
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
  owned-hardware validation; secondarily the licensed YHM shared-power gate).

**Licensed-provider acquisition (11 rows).** The R1-owned portion is implemented; the
remaining producer is a named absent licensed provider.

- health: heart-rate, SpO2, and HRV sample storage (Goodix optical, GoMore algorithms);
  heart-rate and SpO2 pipelines (Goodix optical acquisition/calculation); temperature and
  stress storage edge (GXCAS acquisition, GoMore stress generation); health crash snapshot
  (Goodix opaque blob lookup); activity and steps (step/locomotion/energy algorithms); sleep
  classification (only the GoMore classifier remains).
- sensors: nRF52840 SAADC acquisition and battery voltage/percentage behavior (licensed YHM
  power binding; secondarily hardware calibration); IQS7211E touch controller (licensed YHM
  shared power plus wear-lease identity; secondarily hardware validation).
- hardware: shared `i2c_5` and YHM2710 power ownership (licensed YHM source; secondarily
  hardware validation).

**Unidentified-provider-blocked (5 rows).** The remaining consumer or engine belongs to a
Bravechip-attributed family above.

- sensors: BMA456W and LIS2DW12 accelerometers (higher-level ingestion through the blocked
  sensor-stream framework; secondarily owned-ring validation); GXT310 and PMIC temperature
  (unidentified stream/timer providers; secondarily licensed GXCAS acquisition).
- health: HRV pipeline (sensor-stream topic transport; secondarily Goodix optical RR
  production).
- platform: two-wire bus record bindings (unidentified global registry and GPIO-driven
  software-I2C engines).

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

The 11 **withheld** rows and their reasons: algorithm key provisioning (sensitive cloud/key
lifecycle lacks safe durable verification); NV recovery (destructive identity/calibration
restore lacks validated rollback); OTA and power controls (separated from the normal protocol
and deployment lifecycle); QMA6100 accelerometer (lineage proven but evidence unlicensed);
GH3X2X optical stack (licensed-provider gate; 499 provider entries); software-TWI provider
boundary (40 SHA-pinned functions, no attributable source/version/license); RTC-device
provider boundary (seven unidentified bodies); YHM2710 state-command provider boundary
(1,000 bytes of vendor transport); GoMore floating-point neural runtime; GoMore sleep-stage
statistics; shared quantized neural runtime (unidentified source/version/license/ABI).

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
  functionality behind the absent licensed providers (Goodix, GoMore, YHMICROS, GXCAS, QST)
  or the Bravechip-attributed middleware families;
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
