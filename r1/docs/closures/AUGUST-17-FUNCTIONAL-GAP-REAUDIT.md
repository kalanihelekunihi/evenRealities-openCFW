# August 17 functional-gap re-audit

## Result

The August 17 capability assessment was accurate for the source state it
reviewed, but its principal software gaps are closed in the current workspace.
The source-built Zephyr target now composes the recovered Goodix and GoMore
pipelines rather than merely retaining their translation units, and both the
Zephyr and Nordic build products have been regenerated from the current source.

This is a source/build closure, not a claim of physical or clinical equivalence.
No R1 was flashed as part of this work. Electrical behavior, sensor calibration,
biometric accuracy, power endurance, and retail-data migration still require an
owned device and a controlled validation protocol.

## Assessment gaps and current disposition

| August 17 finding | Current disposition | Evidence |
| --- | --- | --- |
| Nordic image and owner DFU were stale | Closed: the Nordic image contains the current retained corpus and the owner DFU is signed over that exact binary | `tools/verify_sdk_image.py`; `build/owner-dfu-current/manifest.json` |
| Goodix global frame/result ABI was only partially known | Closed at the executable ABI boundary: checked 20-row frame routing, exact HR/HRV/SpO2 identities, input records, result layouts, and lifecycle rollback are source-bound | `port/goodix_gh3x2x/r1_gh3x2x_algo_bridge.h`; `r1_gh3x2x_provider_composer.c` |
| HBA, HRV, and SpO2 roots were not live | Closed: reconstructed roots own caller-supplied plans, state, workspaces, model/configuration input, and typed result formatting | `port/goodix_gh3x2x/r1_gh3x2x_reconstructed_roots.c`; `platform/nrf52840/zephyr/src/openr1_optical_zephyr.c` |
| GoMore was retained but incompletely composed | Closed: the target owns the `0x39E0` engine, `0x2E0` previous state, exact profile/filter initialization, all 16 stages, and the 264-byte output snapshot | `platform/nrf52840/zephyr/src/openr1_gomore_zephyr.c` |
| Live topic acquisition was incomplete | Closed: bounded `acc`, `raw_hr`, direct-HR, and HRV topics cross the recovered readiness barrier and host adapter; the adapter's intentionally unread HRV auxiliary lane remains unread | `platform/nrf52840/zephyr/src/openr1_sensor_stream_zephyr.c`; `openr1_gomore_zephyr.c` |
| Algorithm output was not connected to product behavior | Closed for stock-proven consumers: HR/SpO2/HRV storage, cumulative activity, dynamic sleep optical authorization, final-sleep construction, validation, `sleep.db` persistence, and synchronized commit are live | `platform/nrf52840/zephyr/src/openr1_health_results_zephyr.c`; `openr1_databases_zephyr.c` |
| GoMore prior-state and reset behavior was incomplete | Closed: graceful shutdown checkpoints, profile/backward-clock resets discard stale resume state, and failure 60 triggers a fresh engine while transient failures remain retryable | `platform/nrf52840/zephyr/src/openr1_gomore_zephyr.c`; `openr1_databases_zephyr.c` |
| Generated algorithm parameters could conceal binary dependencies | Closed: all consumed Goodix/GoMore/model words are checked-in typed C data and verified; no stock image or binary algorithm library enters the production build | `reconstructed/model_data/`; `tools/verify_openr1.py` |
| QMA6100 existed only as retained reconstructed source | Closed on the source-built target: exact `0x12`/`0x13` probing, 25 Hz setup, typed TWIM/delay/lock/FIFO seams, P0.15 IRQ worker, and common normalized motion ingestion are live | `platform/nrf52840/zephyr/src/openr1_motion_zephyr.c`; `reconstructed/qma6100/` |
| Encryption and bonding were conflated with product authorization | Closed on the source-built target: a completed bonded pairing may enroll the first CRC-protected owner identity; encryption, restored bond state, and `pairAuth` cannot create or replace it; portable reboot reconstruction admits only the exact identity; every truncated record and all 96 single-bit mutations fail closed; malformed reload evicts stale RAM authorization; and revocation is local-only | `platform/nrf52840/zephyr/src/openr1_bae8_zephyr.c`; `src/r1_peer_target.c`; `tests/test_openr1.c`; `docs/SECURITY.md` |
| Battery/charge state was not continuously product-visible | Closed at the source boundary: startup adopts valid persisted compensation, SAADC acquisition owns the YHM battery lease, exact device-status access refreshes voltage, and live PMIC register 6 refreshes charge state | `platform/nrf52840/zephyr/src/openr1_battery_zephyr.c`; `src/r1_battery.c` |
| Hardware RTC adoption was incomplete | Closed at the source boundary: RTC2 runs the recovered 1,024-Hz/8-Hz backend, the phone-synchronized monotonic clock is live, and exact Gregorian query/day-boundary conversion drives storage and health cadence | `platform/nrf52840/zephyr/src/openr1_rtc_zephyr.c`; `src/r1_clock.c`; `reconstructed/time_calendar/` |
| Identity/calibration NV recovery was non-transactional | Closed as an owner-authorized recovery operation: the exact CRC-gated fill-only merge commits `nv_r1`, `power`, and `r_size` in one generation-bearing KV snapshot, verifies complete readback, exhaustively proves old-or-new reboot state at every byte cut, and exposes no identity report | `src/r1_nv_recovery.c`; `src/r1_kv_store.c`; `platform/nrf52840/zephyr/src/openr1_databases_zephyr.c`; `tests/test_openr1.c` |
| Channel 1 had no safe production receiver | Closed narrowly: the 36-byte route admits only opcode `0x89` after encrypted, bonded, independently authorized glasses-role admission; it emits the exact seven-byte response and binds touch, REG1, immediate `{16,16,2,600}` secondary-mode, and exact `0x2800`-tick delayed `{72,84,4,600}` slow BLE actions; every other BC/eAT route remains fail-closed | `platform/nrf52840/zephyr/src/openr1_bae8_zephyr.c`; `src/r1_runtime.c`; `src/r1_protocol.c` |
| Storage power-loss testing stopped at provider-call boundaries | Closed in the portable fault model: `kv.bin` exhausts every byte cut across erase/program and legacy migration; `sleep.db` uses reservation/body/metadata/commit ordering and exhausts normal plus rollover cuts while proving a different recovery append remains iterable | `src/r1_storage.c`; `src/r1_kv_store.c`; `src/r1_sleep_db.c`; `tests/test_openr1.c` |
| The composite diagnostic source remained absent with its private BLE sender | Closed at the safe source boundary: exact EP/log/cache/optional-crash ordering, chronology, eligibility, checksum, and segmented reads are compiled and target-bound to one encrypted, bonded, independently authorized phone-role session; disconnect or security loss releases the writer freeze. The undocumented BLE command remains separately withheld | `src/r1_storage.c`; `platform/nrf52840/zephyr/src/openr1_storage_zephyr.c`; `openr1_bae8_zephyr.c`; `DIAGNOSTIC-EXPORT-CORRELATION.md` |
| Deployment preservation and recovery existed only as prose | Closed offline: the bundle embeds a machine-checked no-mass-erase contract; the preflight requires exact 1-MiB internal-flash and complete 0x308-byte architected nRF52840 UICR backups, accepts only exact two-data/one-swap retail FDS settings or fully erased pages, erases the complete source-built boot/application/settings extent so no opaque retail bytes or incompatible credentials survive, preserves only product data, and emits separate canonical recovery HEX files plus the exact expected full readback; an independent verifier reconstructs the result, byte-compares observed internal-flash and unchanged-UICR install readbacks, and separately requires post-recovery readbacks to equal both original backups byte-for-byte | `tools/prepare_zephyr_deployment.py`; `tools/verify_zephyr_deployment.py`; `tools/verify_zephyr_bundle.py` |
| The full-flash target might still rely on S140 or the retail bootloader | Closed: the alternate bundle contains source-built MCUboot, a source-built Zephyr Bluetooth host/controller, and the signed application only | `tools/verify_zephyr_bundle.py`; `SOURCE-BUILT-ZEPHYR-BUNDLE.md` |
| The manifest could be internally consistent while stale versus the workspace | Closed: verification now rejects unsafe inventory paths and byte-compares every one of the 174 recorded firmware sources to the current source tree | `tools/verify_zephyr_bundle.py` |
| Linked RAM left no credible runtime margin | Closed at the software-layout boundary: dispatch responses retain the exact 32-response, 1,100-byte-model, and 50-fragment limits but share an exact fragment-bounded arena; the owner build falls from 256,690 bytes (97.92%) to 233,586 bytes (89.11%) without removing a provider or protocol response | `include/openr1/r1_dispatch.h`; `src/r1_dispatch.c`; `tests/test_openr1.c`; `SOURCE-BUILT-ZEPHYR-BUNDLE.md` |

## Intentionally unclaimed behavior

The following items are not opaque firmware gaps and must not be filled by
guessing:

- Goodix wavelength/channel meanings, optical transfer functions, biometric
  equivalence, and clinical accuracy need synchronized physical reference data.
- Motion axes and temperature channels are source-routed, but their physical
  orientation, calibration, and final-sleep temperature semantics need an owned
  ring. Until then, final sleep records use a transparent zero temperature.
- Touch remains fail-closed until ring identity and a wear/factory lease are
  known. NFC remains policy-disabled until an evidence-backed activation policy
  is selected.
- The destructive stock `health.db` format-and-retry path is deliberately
  omitted. The source target preserves data and reports failure instead.
- The stock-unreachable stress producer and unlabeled GoMore output fields are
  not exposed or assigned invented semantics.
- Identity-bearing NV recovery now has an owner-phone-gated, readback-verified
  atomic KV transaction with exhaustive byte-cut rollback tests. The local
  report sender and raw diagnostic mutation remain withheld; physical
  persistence/replay, reboot adoption, and ATT behavior remain validation work.

These constraints explain why rows in `reference/COVERAGE.csv` can remain
`partial` even when their software implementation is complete: that ledger also
tracks physical validation and deployment risk. A `partial` label is not, by
itself, evidence of an opaque object or an uncompiled code path.

## Fresh remaining-gap classification

After the source-target and deployment closures above, the authoritative ledger
contains 52 `implemented`, 40 `partial`, two `withheld`, two `separate`, and one
`excluded` row. The 40 partial rows do not identify an opaque executable input.
They retain a partial label because their last acceptance criterion needs an
owned ring, debug probe, radio/electrical/reference instrumentation, retail-data
migration evidence, or a product authorization/licensing decision. Raw EP/log
payload access retains explicit privacy and destructive-control restrictions.
The withheld rows are credential/algorithm-key provisioning and the private
structured-log BLE sender; neither belongs in an unauthenticated general command
surface. The source-built OTA recovery route is implemented while advertising
authorization and power control remain explicit policy and physical-validation
gates on a partial row.

The offline portion of deployment is now executable and independently checked,
including complete install-partition erasure, exact preserved-region modeling,
separate internal-flash and UICR backups/recovery images, unchanged-UICR proof,
and post-recovery comparison. The remaining deployment criteria—actual flash,
boot, rollback, recovery, and power-loss validation—cannot be truthfully closed
without owned hardware and an authorized debug path.

## Reproduction gates

From the repository root:

```sh
make -C r1 verify
python3 r1/tools/verify_sdk_image.py
python3 r1/tools/verify_zephyr_source_boundary.py
python3 r1/tools/verify_zephyr_bundle.py \
  r1/build/openr1-zephyr/openr1-source-built.zip
python3 -m unittest discover -s r1/tests -p 'test_sign_r1_firmware.py'
git diff --check
```

The bundle verifier compares every entry under `openr1_source.files` with the
current workspace. The current bundle records 174 source files; all 174 match
byte-for-byte.

Current verified artifacts:

- `build/openr1-zephyr/openr1-source-built-ble-recovery-owner.zip`:
  `9d518d0a0a1f748796d591fd561638204e9ac75a59fc7fd98a2b226bd7ccae49`
- Nordic application BIN:
  `47e502685da57c1df55aeee6d9d156210f22b427a9c36ac94d72401a4f859729`
- Nordic application HEX:
  `b3bf1fd534bf588c2cf3186d1f48ac1aa07c1dfcf71e681095e6ae2770cc8b4a`
- `build/owner-dfu-current/openr1-owner-signed.zip`:
  `f2394dd396396edbc5993755559836a1cba3b5e90e5d5ecdbe25ca3ce2797fa6`

The default transparent MCUboot development key is not a deployment trust
anchor. A deployer must rebuild with an owner-controlled P-256 key and validate
the resulting image on owned hardware.
