# Residual provider and production-readiness audit

Snapshot: 2026-08-17, after the source-built Goodix optical-transport/YHM lifecycle binding, the platform-driver
increments, the six Bravechip-attributed middleware reductions, the eight-entry GXT310 reduction,
the complete 17-entry QMA6100 provider/adapter reduction, the complete 44-entry YHM2710
reduction, and the complete 320-entry opaque-Goodix / 360-entry GoMore reductions. This audit tracks what remains outside the R1-owned clean-room
boundary, why it remains there, and what the project does and does not claim today.

## Ledger totals

The generated ownership ledger
([`FUNCTION-OWNERSHIP.csv`](FUNCTION-OWNERSHIP.csv), summary in
[`FUNCTION-OWNERSHIP-SUMMARY.json`](FUNCTION-OWNERSHIP-SUMMARY.json)) covers **3,326
functions**: 3,022 application and 304 bootloader entries, comprising 2,991 Ghidra inventory
records plus 335 exact manual provenance supplements. **Zero entries remain unclassified**;
every recovered function carries an ownership disposition. The separate generated
[`GHIDRA-EXPLICIT-ENTRY-CENSUS.json`](GHIDRA-EXPLICIT-ENTRY-CENSUS.json) closes the omission
boundary: across 28 curated function-entry arrays, it records 666 version-qualified unique
entries. For application 2.2.6.0009, 598 are exact ledger starts and five are interior addresses
within genuinely contiguous ledger extents. Seven are conclusively adjudicated literal/data
operands and explicitly retained as `adjudicated_non_function_data` rather than being turned into
invented functions. One further seed, `0x00042974`, is the second halfword of a 32-bit Thumb
branch and is retained as `adjudicated_non_function_instruction_interior`; one seed is a proven
secondary executable segment. No application seed remains unproven. All 41
bootloader entries are exact. Thirteen additional entries belong to application 2.2.7.0005 and
are explicitly marked `analysis_only_no_ownership_inventory` because that analyzed image and its
function inventory are not preserved in this workspace. They are a real remaining provenance
gap, not treated as covered by same-address 2.2.6 functions.

Disposition totals:

| Disposition | Entries |
| --- | ---: |
| `use_nordic_sdk` | 782 |
| `clean_room_behavior_only` (+ 12 `clean_room_behavior_only_security_preserving`) | 757 |
| `use_pinned_upstream` | 252 |
| `use_toolchain_runtime` | 129 |
| `use_authenticated_upstream_snapshot_and_nordic_port` | 111 |
| `use_authenticated_upstream_snapshot` | 65 |
| `use_nordic_sdk_bundled_upstream` | 43 |
| `use_nordic_supplied_provider` | 41 |
| `clean_room_adapter_only_*` / `clean_room_configuration_only_*` / `clean_room_data_model_only` (all variants) | 200 |
| `vendor_source_required_not_redistributable` | 0 |
| `clean_room_reimplementation_owner_authorized` | 946 |

No `vendor_source_required_not_redistributable` executable entry remains. The 946
`clean_room_reimplementation_owner_authorized`
entries comprise the 169 functions in six Wuxi Bravechip ChipletRing/BCL603M middleware families,
eight GXT310 entries, all 17 QMA6100 provider/adapter entries, all 44 YHM2710 entries,
339 Goodix functions, all 362 GoMore primitives/tensor-runtime routines, and seven R1 GoMore input/time adapters. Under the owner-authorized full reduction
([`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md), 2026-08-14) these are reconstructed
from the decompilation evidence as independently compiled C under `r1/reconstructed/` with
per-function provenance and host tests. The reconstructions are not vendor source; on-target
runtime adoption and hardware validation remain open.

## Per-provider residual boundary table

| Provider family | Entries | Disposition | Boundary documentation | What would unblock it | Fail-closed behavior today |
| --- | ---: | --- | --- | --- | --- |
| GoMore health/sleep algorithms (`gomore_health_algorithm_candidate`) | 0 remaining + 362 reconstructed + 7 reconstructed R1 adapters | `clean_room_reimplementation_owner_authorized` | [`../boundaries/GOMORE-PROVIDER-BOUNDARY.md`](../boundaries/GOMORE-PROVIDER-BOUNDARY.md), the neural-runtime/sleep family boundary docs, [`../correlation/GOMORE-PRIMITIVES-REDUCTION-CORRELATION.md`](../correlation/GOMORE-PRIMITIVES-REDUCTION-CORRELATION.md), [`../correlation/GOMORE-TOPIC-INPUT-CORRELATION.md`](../correlation/GOMORE-TOPIC-INPUT-CORRELATION.md), [`../correlation/TIME-HEALTH-ROLLOVER-CORRELATION.md`](../correlation/TIME-HEALTH-ROLLOVER-CORRELATION.md), and [`../correlation/GOMORE-TENSOR-RUNTIME-REDUCTION-CORRELATION.md`](../correlation/GOMORE-TENSOR-RUNTIME-REDUCTION-CORRELATION.md) | The executable reduction is complete: 343 primitive/shared-runtime routines, nineteen tensor-runtime routines, and seven R1 adapter extents are transparent C. The exact four topic callbacks, readiness barrier, all 16 stages, output copy/lifecycle, activity accumulator, final-sleep builder/persistence, dynamic optical slot, and fresh-engine reset paths are target-composed. Continue only physical input semantics and owned-hardware equivalence work. | Live health/activity/sleep execution remains fail-closed behind the persisted health gate and exact seven-slot authorization. Dormant stock-unreachable stress output is not synthesized. Public activity history independently enforces the shared 50-fragment transport bound and resumes through per-packet ACK state. |
| Wuxi Bravechip ChipletRing / BCL603M closed middleware — six `unknown_*_candidate` families | 169 | `clean_room_reimplementation_owner_authorized` | [`../boundaries/unknown_generic_device_registry_candidate-ATTRIBUTION-2026-08.md`](../boundaries/unknown_generic_device_registry_candidate-ATTRIBUTION-2026-08.md) and the five sibling `unknown_*-ATTRIBUTION-2026-08.md` reports; per-family boundary docs [`../boundaries/GENERIC-DEVICE-REGISTRY-BOUNDARY.md`](../boundaries/GENERIC-DEVICE-REGISTRY-BOUNDARY.md), [`../boundaries/SOFTWARE-TWI-PROVIDER-BOUNDARY.md`](../boundaries/SOFTWARE-TWI-PROVIDER-BOUNDARY.md), [`../boundaries/SENSOR-STREAM-FRAMEWORK-BOUNDARY.md`](../boundaries/SENSOR-STREAM-FRAMEWORK-BOUNDARY.md), [`../boundaries/QUANTIZED-POOLING-PROVIDER-BOUNDARY.md`](../boundaries/QUANTIZED-POOLING-PROVIDER-BOUNDARY.md), [`../boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md`](../boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md), [`../boundaries/RTC-DEVICE-PROVIDER-BOUNDARY.md`](../boundaries/RTC-DEVICE-PROVIDER-BOUNDARY.md) | Licensed acquisition from Bravechip (named commercial route via the byte-exact GATT base-UUID match to the public `BravechipSpace/ChipletRing-APPSDK` and the `603MV1.9.3` module string; contact xiaojian.cui@bravechip.com per the APPSDK README) or the ring ODM, with OTA-hex analysis as forensic fallback; or new attribution evidence for an individual family. All six were re-tested against fetched upstream sources in 2026-08 and remain NO ATTRIBUTION. A 2026-08-14 public-route re-check found Bravechip's only public repository to be phone-side-only (zero firmware identifiers), its official download list to offer app SDKs/datasheets only, and a second Bravechip-based ring product (`thuhci/OpenRing`) shipping no firmware source either — no public firmware-side source exists; see the updated `unknown_*-ATTRIBUTION-2026-08.md` reports. | All 169 functions are reconstructed host-side under the owner-authorized 2026-08 reduction: generic device registry (43), GPIO-driven software-TWI engines (40), sensor-stream framework (32), shared quantized-neural runtime (28), time/calendar provider (16), RTC-device layer (10). The Zephyr target now adopts exact software `i2c_4` for Goodix optical transport and exact software `i2c_2` for the typed dual-GXT310 probe/acquisition adapter; dormant roles remain retained source awaiting typed consumers. OpenR1 continues to substitute typed admitted providers (Nordic TWIM, `nrfx_rtc`, R1-owned clock production) on the other hardware paths. |

Goodix has left the residual table: all 320 formerly opaque provider-candidate entries now map to
owner-authorized transparent C, alongside seventeen public-democode replacements and two R1
product entries. Three additional product-side callback-table supplements preserve the exact
`raw_hr`, `adt`, and living-object topic records. The final admitted algorithm function is the complete 1,370-byte SpO2/dlCom processing root
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

[`COVERAGE.csv`](COVERAGE.csv) holds 97 rows: **52 implemented, 40 partial, 2 withheld,
2 separate, 1 excluded**. The structured-log record/cache/persistence row is now compiled and
target-bound. The exact composite virtual-file source is also compiled and owner-gated; its
undocumented BLE sender is tracked separately as withheld. The recovered remove-ring metadata
route is now a strict owner-phone-authorized two-generation transaction with exhaustive
byte-interruption and retry coverage.

### Partial rows grouped by remaining gate

Every partial row's remaining gate has been audited and classified as external. A row appears
under its primary gate; mixed gates are noted inline.

**Owned-hardware validation (14 rows).** The implementation is source-complete; what remains
is capture or confirmation on a physical ring.

- platform: S140 resource configuration (owned-hardware RAM negotiation); RTOS scheduler and
  task wake topology (the stock nine-group startup census is pinned; physical wake/saturation timing remains); legacy GAP advertising
  (durable factory/serial restore, physical validation); ATT MTU and data-length negotiation
  (negotiated values to be captured).
- protocol: BAE8 raw GATT event mapping (physical validation); 100/200/1000 scheduling and
  retry timing (physical saturation and timing-unit confirmation).
- security: queued-write rejection (owned-hardware ATT validation); crash unwind and retained
  diagnostics (authenticated export, hardware fault validation).
- storage: `kv.bin` and `sleep.db` now exhaust every byte-level program/erase interruption through
  rollover and legacy migration, including a different post-reboot append; FlashDB health storage
  still needs its provider-specific physical power-loss campaign, and every store needs owned-ring
  lifecycle validation.
- sensors: PMIC current and NFC rectifier conversion (physical transfer functions
  capture-gated).
- hardware: ST25DVxxKC source mailbox transport, P1.10 dock lifecycle, dock-session mutex, and
  TWIM1 handoff are linked on the alternate target; explicit activation policy and owned-hardware
  coexistence validation remain.

**Source-admitted algorithm / physical-provider validation (14 rows).** The R1-owned portion and
all inventoried Goodix/GoMore executable bodies are implemented and live target composition is
complete. The remaining work is electrical, physical-semantic, reference, and owned-ring
validation of the source-bound sensor providers.

- sensors: GH3X2X raw acquisition now has source Goodix demo/driver, recovered software-`i2c_4`,
  GPIO/interrupt, motion-feed, and YHM-client lifecycle bindings; the global algorithm frame/result
  ABI is checked and normalized through a provider contract, and validated updated HR/SpO2 records
  now reach recovered planners and scalar storage consumers behind the persisted health gate. The
  provider-independent function IDs are compile-time checked against the pinned democode ABI
  (`HR=1`, `HRV=2`, `SpO2=6`), preventing HR output from being misclassified as an unsupported
  function. Checked adapters reproduce the recovered four-channel HR record and SpO2's mapped
  three-by-four-channel record, including the exact MSB-first enable flags, 24-bit marker, frame
  byte, motion axes, and fail-without-mutation bounds behavior. A retained source composer now
  owns all three outer-wrapper lifecycles, exact HR `0x003F`, HRV `0x007F`, and retail-R1 SpO2
  `0x00FF` masks, their six distinct public words, the zero HRV slot 6, the SpO2 word-0 mirror in
  slot 6 plus zero slot 7, and HR-to-HRV carry;
  a retained reconstructed-root executor now invokes HBA `0x0006C6A8`, HRV `0x0006D51C`, and
  SpO2 `0x0006E838`, routes the exact recovered version builders, and reproduces the HBA and
  noncontiguous SpO2 private-to-public result transformations;
  the public 36-byte HR and 24-byte HRV configuration sources are byte-matched to retail ROM and
  retained beside the existing exact SpO2 configuration. Persistent HBA/HRV/SpO2
  plan/state/workspace initialization, HRV session composition, observer routing, and scalar
  storage are source-bound; electrical calibration, biometric equivalence, and owned-ring
  validation remain.
- health: heart-rate, SpO2, and HRV sample storage (Goodix result and typed GoMore integration);
  heart-rate and SpO2 pipelines (Goodix democode-ABI composition over the bound raw acquisition);
  temperature and stress storage edge (GXT310 transport/acquisition, exact two-byte temperature
  stream, dormant one-shot listener, event 9, and daily-cache producer are now source-bound, while
  the sleep/timing activation policy and stock-unreachable GoMore stress producer remain explicit
  gates); health crash snapshot (the live GoMore exporter reports `0x2E0`, so the stock exact
  `0x380` provider-blob gate is correctly not taken, while Zephyr creates the next retained
  one-shot activity/HR/SpO2/HRV snapshot after recovery); activity/steps and sleep classification
  (transparent algorithms, live sensor topics, all 16 stages, result consumers, and prior-state
  lifecycle are target-composed; physical semantics and owned-ring validation remain).
- sensors: nRF52840 SAADC acquisition and battery voltage/percentage behavior (YHM client-bit-0
  binding, persisted battery type/compensation, live register-6 charge state, and boot/status-access
  production are bound; PMIC event-driven refresh and hardware calibration remain); IQS7211E transport,
  lifecycle, and YHM client-bit-2 binding are linked, with wear-lease identity and hardware
  validation still required for live sampling.
- sensors: BMA456W, LIS2DW12, and the reconstructed QMA6100 third fallback feed the `"acc"` stream
  through the exact 188-byte batch ABI and persisted axis calibration; the exact dormant
  `"gomore"` listener and 25-sample axis transform are source-bound. The companion raw-optical
  producer, exact topic barrier, all 16 GoMore stages, prior state, and proven output consumers are
  live; physical-axis and optical-channel validation remain.
- hardware: shared `i2c_5` and YHM2710 power ownership (battery, touch, and optical clients are
  adopted; hardware electrical validation remains).

**Bravechip-middleware physical adoption (3 rows).** All six families are reconstructed,
host-tested, and adopted where the recovered target has a live consumer. Remaining gates concern
physical channel identity or stock-dormant paths rather than an absent runtime.

- sensors: GXT310/PMIC temperature timing and event consumers (the exact GXT310 software-bus,
  two-address probe, raw conversion, bounded acquisition, read-only persisted `nv_r1`
  calibration, fixed `"temp"` stream vtable, and dormant one-shot event/cache path are adopted;
  sleep/timing scheduling, physical channel semantics, public activation, and owned-hardware
  validation remain).
- health: HRV pipeline (sensor-stream topic transport, Goodix HRV root/result production, scalar
  persistence, and live GoMore topic routing are adopted; electrical/reference validation remains).
- platform: two-wire bus record bindings (software `i2c_2` and `i2c_4` are adopted by the Zephyr
  GXT310 and optical paths; reconstructed global-registry and dormant GPIO-driven software-I2C
  roles remain pending).

**Authorization-policy.** The source-built target now has an independent persisted owner policy:
only a completed bond may enroll the first CRC-protected identity, while encryption, restored bond
state, and `pairAuth` cannot create or replace it. The remaining seams below stay closed where
their destructive, identity-bearing, licensed, or diagnostic policy is still unresolved.

- system: `advStart` two-target connection control is now admitted only for an exact SET from
  the independently owner-authorized phone role and is asynchronously composed through real
  SDK and Zephyr persistence, disconnect, and advertising providers; target byte-order,
  retention, timing, and radio behavior remain owned-hardware validation items. The alternate
  Zephyr target now replaces the system-settings REG1 SVC with the pinned source nRF POWER HAL and binds the separately
  authorized glasses-status channel to immediate-disable/delayed-enable wear automation plus
  the touch lease, immediate `{16,16,2,600}` secondary-mode BLE profile, and exact
  `0x2800`-tick delayed `{72,84,4,600}` slow profile; physical timing, regulator,
  radio, and coexistence validation remains.
- security: Peer Manager bond and GATT-cache provider (source authorization is complete;
  owned-hardware persistence/replay, ATT, and revocation validation remain); NV recovery merge
  (persistent mutation is local-only, atomic, and readback-verified; the identity-bearing BLE
  sender remains refused pending physical service authorization and reboot validation).
- protocol: channel-2 EUS BLE runtime (source authorization is complete; physical timing and
  saturation validation remain).
- storage: pKey and EP stores (sensitive pKey/algorithm state pending licensing and key
  policy); log store (the owner-authorized composite source is internal-only and its live BLE
  sender remains excluded; no raw destructive controls are exposed).

### Withheld, separate, and excluded rows

The 2 **withheld** rows and their reasons: algorithm key provisioning (sensitive cloud/key
lifecycle lacks safe durable verification), the private structured-log BLE sender (the exact
source is implemented, but records can contain identity, health, bonding, and diagnostic material
and physical ATT plus redaction policy remain unvalidated). OTA recovery and power controls are
tracked as partial: the owner-authorized zero-length recovery transition and source loader are
implemented, while advertising and power controls remain policy/physical gates. NV recovery is no
longer withheld: its fill-only three-record
mutation is a local-only readback-verified atomic KV transaction with exhaustive byte-cut rollback
and retry tests. Its exact command-2 merge route is independently owner-authorized and bounded while the identity-bearing local-report sender remains unreachable. GoMore floating-point neural runtime and sleep-stage statistics are no
longer withheld: both are reconstructed and target-composed. The software-TWI, RTC-device, and
shared quantized-neural runtime boundary rows likewise left the withheld set under the
owner-authorized 2026-08 reduction.

The 2 **separate** rows: startup vectors and runtime (the linked Nordic/SDK application owns
placement; a standalone non-SDK bootable image is not a product target) and secure boot
signing, rollback, and recovery (no signing bypass or stock-verifier patch is implemented;
the deployment lifecycle stays separate per [`../SECURITY.md`](../SECURITY.md)).

The 1 **excluded** row: the health-daily synthetic test fixture, a dormant 1,344-byte
product-owned test body with no recovered caller, intentionally excluded from production.

The initial owned-ring BLE evidence is recorded in
[`../closures/AUGUST-18-R1-B56EE2-HARDWARE-VALIDATION.md`](../closures/AUGUST-18-R1-B56EE2-HARDWARE-VALIDATION.md).
The remaining physical, debug-readback, instrumentation, and policy evidence
required to advance the other rows is recorded explicitly in
[`../closures/AUGUST-18-PHYSICAL-VALIDATION-BLOCKER.md`](../closures/AUGUST-18-PHYSICAL-VALIDATION-BLOCKER.md).
That record is a stop condition, not a completeness claim.

## Production-readiness statement

Current buildable and verified deliverables (the Zephyr manifest records this working tree and
hashes all 174 included firmware source files):

- the host protocol/device test suite (`make -C r1 test`);
- the AddressSanitizer/UndefinedBehaviorSanitizer build (`make -C r1 sanitize`);
- freestanding Cortex-M4F objects for every portable core translation unit
  (`make -C r1 arm-objects`);
- the host executable protocol/device simulator (`make -C r1 sim`);
- the linked nRF52840 application built from Nordic nRF5 SDK 17.1.0 sources against the
  S140 7.2.0 ABI, verified by `tools/verify_sdk_image.py` against pinned artifacts:
  BIN 436,648 bytes, BIN SHA-256
  `47e502685da57c1df55aeee6d9d156210f22b427a9c36ac94d72401a4f859729`, HEX SHA-256
  `b3bf1fd534bf588c2cf3186d1f48ac1aa07c1dfcf71e681095e6ae2770cc8b4a`;
- an application-only owner DFU package whose three-member boundary excludes stock application,
  SoftDevice, bootloader, and vendor algorithm blobs; it still declares and requires the
  preinstalled S140 ABI `0x0100`, as documented in
  [`APPLICATION-BUNDLE-BOUNDARY.md`](../closures/APPLICATION-BUNDLE-BOUNDARY.md); the current
  owner-signed ZIP SHA-256 is
  `f2394dd396396edbc5993755559836a1cba3b5e90e5d5ecdbe25ca3ce2797fa6`;
- an alternate source-built Zephyr/MCUboot full-flash bundle whose executable members require no
  S140 or retail bootloader, whose signed application retains all 14 reconstructed modules, and
  whose source revisions, flash ranges, canonical member union, and ECDSA-P256 signature are
  verified as documented in
  [`SOURCE-BUILT-ZEPHYR-BUNDLE.md`](../closures/SOURCE-BUILT-ZEPHYR-BUNDLE.md); the current
  bundle contains a 642,871-byte signed application with SHA-256
  `2e4727fde3817c1494a16bf0c9e93dc8417c513c9cf16fb0d40f830b4c6292e5`, full-flash HEX SHA-256
  `56072380e98c12f2b13a1b44ec4005e49f5ab05165e0bc0291705d9ae6a92aff`, and ZIP SHA-256
  `9d518d0a0a1f748796d591fd561638204e9ac75a59fc7fd98a2b226bd7ccae49`;
- the full evidence gate (`python3 tools/verify_openr1.py`), which reconciles the ownership
  ledger, the explicit Ghidra-script entry census, the coverage ledger, the per-subsystem
  correlation summaries, and the Goodix democode mapping against the recovered images.

Explicitly **not** claimed:

- owned-hardware validation of the live Goodix/GoMore biometric and health algorithms and several
  reconstructed YHMICROS, GXCAS, QST, and Bravechip-attributed closures; their executable bodies,
  generated-model parameters, checked Goodix ABI, persistent roots, live topic path, and complete
  GoMore output lifecycle compile from transparent source;
- complete sensor/health-record/power/product integration on the alternate source-built BLE/boot target;
  its BAE8/core runtime, persistent SMP settings, KV/health/sleep storage, exact SAADC routes,
  phone-synchronized clock with reconstructed exact calendar query/day-boundary conversion,
  reset-reason trace, scheduler watchdog, pinned Bosch/ST plus reconstructed-QMA motion
  acquisition, fail-closed IQS7211E transport/lifecycle, reconstructed YHM shared power, and
  ST25DVxxKC mailbox/P1.10/TWIM1 handoff are linked. Motion production ingestion is live; touch
  identity/wear provisioning, explicit NFC activation policy, destructive health slot-0
  format/retry,
  fatal-trace validation, and retail-layout migration still require owned-ring work. Public
  health-settings are now canonicalized, ACK-ordered, and persisted into the live global gate;
  private event `0x100D` reconciles the exact seven-slot gate, and backward-clock/failure-60 resets
  initialize a fresh engine. HR, SpO2, HRV, and activity
  daily routes now bind their exact three-day FlashDB merges and ACK-driven named-cursor persistence;
  both target clocks drive the exact automatic five-leg gate through a bounded drain-aware
  service that preserves the recovered 50-record queue;
- initial owned-ring BLE validation on later retail `2.2.8.0002`: exact BAE8
  properties/CCCDs, pair-role response, retained macOS relationship, requested
  and unsolicited status models, three sequential status timings, and a
  twenty-request zero-drop burst are captured. Raw HCI/HVN values, exact
  `2.2.6.0009` and source-built behavior, physical scheduler units, sensor
  calibration, and analog transfer functions remain gates; host-tested raw-tick
  constants are not relabeled as physical time.

The project's exact current claim is: **"All inventoried application and bootloader executable
entries are source-routed, all Goodix/GoMore algorithm bodies and model parameters are transparent
source, and an alternate signed full-flash bundle builds its BLE/controller and boot path from
pinned source without S140 or the retail bootloader; remaining gaps are hardware/provider
integration, deployment, instrumented validation, and exact-version/source-built
owned-ring equivalence."**

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
- **Unrecovered cross-context event publishers** — target-owned sensor and platform production
  uses typed stream topics and direct handlers rather than inventing the missing id-to-slot map;
  any future generic cross-context publisher must first recover that mapping.
- **Command/peer byte-order end-to-end reconciliation** — left unbound rather than inventing
  behavior; it is an end-to-end validation concern with the first-party sender
  ([`../correlation/CONNECTION-CONTROL-CORRELATION.md`](../correlation/CONNECTION-CONTROL-CORRELATION.md)).
- **`advStart` physical target semantics** — the source route is authorization-gated and live;
  first-party address byte order, target retention, disconnect timing, and advertising behavior
  still require recoverable owned-hardware validation
  ([`../correlation/CONNECTION-CONTROL-CORRELATION.md`](../correlation/CONNECTION-CONTROL-CORRELATION.md)).

## Reproducing this audit

```sh
make -C r1 test sanitize arm-objects sim
cd r1/platform/nrf52840/sdk && make clean && make SDK_ROOT=... default   # see docs/build.md
make -C r1 sdk-verify SDK_ROOT=...                                       # pinned-hash check
python3 r1/tools/verify_openr1.py
cd r1 && python3 tools/build_r1_source_ownership.py --check
cd r1 && python3 tools/audit_r1_ghidra_explicit_entries.py --check
```

The SDK image verification must pass against the pins corresponding to the current reviewed
source. A future hash mismatch is a build anomaly to investigate; pins change only alongside an
intentional, reviewed source change and a fresh deterministic build.
