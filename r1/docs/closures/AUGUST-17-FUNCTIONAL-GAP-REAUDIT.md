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
| The full-flash target might still rely on S140 or the retail bootloader | Closed: the alternate bundle contains source-built MCUboot, a source-built Zephyr Bluetooth host/controller, and the signed application only | `tools/verify_zephyr_bundle.py`; `SOURCE-BUILT-ZEPHYR-BUNDLE.md` |

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
- Product authorization, identity-bearing NV recovery, and raw diagnostic
  mutation remain withheld where the evidence does not provide a safe trust
  policy.

These constraints explain why rows in `reference/COVERAGE.csv` can remain
`partial` even when their software implementation is complete: that ledger also
tracks physical validation and deployment risk. A `partial` label is not, by
itself, evidence of an opaque object or an uncompiled code path.

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

The final source-integrity audit must also compare every entry under
`openr1_source.files` in the bundle manifest with the current workspace. The
current bundle records 171 source files; all 171 match byte-for-byte.

Current verified artifacts:

- `build/openr1-zephyr/openr1-source-built.zip`:
  `9979d400c568607aeec56ff666cbb90a026f37d35f6f3a3590d9aabb9a4b3667`
- Nordic application BIN:
  `47e502685da57c1df55aeee6d9d156210f22b427a9c36ac94d72401a4f859729`
- Nordic application HEX:
  `b3bf1fd534bf588c2cf3186d1f48ac1aa07c1dfcf71e681095e6ae2770cc8b4a`
- `build/owner-dfu-current/openr1-owner-signed.zip`:
  `f2394dd396396edbc5993755559836a1cba3b5e90e5d5ecdbe25ca3ce2797fa6`

The default transparent MCUboot development key is not a deployment trust
anchor. A deployer must rebuild with an owner-controlled P-256 key and validate
the resulting image on owned hardware.
