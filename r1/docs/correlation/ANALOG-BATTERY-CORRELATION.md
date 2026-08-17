# Analog acquisition and battery-behavior correlation

## Result

The open firmware now compiles Nordic nRF5 SDK 17.1.0's unmodified `nrfx_saadc.c` as the
physical ADC provider and keeps only the recovered R1 channel configuration, filtering,
conversion, percentage, and charging-state behavior in local code. It does not recreate Nordic's
driver or the stock generic device registry. YHM2710 register/wire behavior is separately
reconstructed and source-bound on the alternate Zephyr target.

The portable behavior is implemented in `r1/src/r1_battery.c`. The nRF52840 adapter is
`r1/platform/nrf52840/sdk/openr1_analog.c`. Its retained runtime bridge samples voltage and
updates protocol-visible battery state only when an admitted caller supplies charge state and
elapsed time. The legacy Nordic adapter remains fail-closed without a power provider; the Zephyr
adapter binds the same semantic acquire/release interface to reconstructed YHM client bit 0. No raw
ADC or PMIC diagnostic is exposed over BLE.

The source-built database owner now strictly decodes the exact four-byte persisted `power` class:
battery type is byte 0 and signed Int16LE voltage compensation is at bytes 2...3. Types 1...4 are
adopted into the runtime battery controller; the decoded compensation and its recovered report
validity remain available through a typed read-only accessor. This path neither samples the ADC
nor changes persistent state.

## Recovered SAADC configuration

The decompressed registry contains three 40-byte records. Nordic's driver configuration is
12-bit resolution, no oversampling, normal-power mode, and interrupt priority 6.

| Stock name | Channel | nRF52840 input | Pin | Gain/reference | Acquisition |
| --- | ---: | --- | --- | --- | --- |
| `vbat_adc` | 0 | AIN5 | P0.29 | 1/2, internal 0.6 V | 40 us |
| `vpmic_isns_adc` | 1 | AIN3 | P0.05 | 1/2, internal 0.6 V | 40 us |
| `vnfc_rect_adc` | 2 | AIN2 | P0.04 | 1/6, internal 0.6 V | 10 us |

All three are single-ended, use disabled input resistors, disabled negative input, and disabled
burst. The R1 initialization adapter invokes the recovered raw 64,000-cycle Nordic delay body
twice after channel setup; the clean port expresses those waits through Nordic `nrf_delay_us`.

## Function ownership and byte pins

These complete stock extents are SHA-256 pinned from the recovered 2.2.6.0009 application image.
The hash is evidence integrity, not source to copy.

### Nordic provider bodies

| Extent | SDK symbol | SHA-256 |
| --- | --- | --- |
| `0x0007AEAC..<0x0007AF38` | `nrfx_saadc_channel_init` | `f566b9bdb3566e82779475552d6222438d301d440895159507200c8deac41454` |
| `0x0007AF38..<0x0007AF7C` | `nrfx_saadc_channel_uninit` | `1c3000ad35f6c953143c68af804b71a12078d11a7baf5f25a033f345ca7e31bc` |
| `0x0007AF7C..<0x0007B010` | `nrfx_saadc_init` | `d5dd834663a4bf64fec41da0d5a66e5d06ae7fb143c33533a57b923169bb8d62` |
| `0x0007B010..<0x0007B090` | `nrfx_saadc_limits_set` | `15f87b4e90a39eeb7bd90fd5ec86956b623047e349042ad231f88d9dd0114b91` |
| `0x0007B090..<0x0007B150` | `nrfx_saadc_sample_convert` | `f6b5be2a7ac2024543c8b74d92bc19ec319e64d1486672a9e033c3fef1981aab` |
| `0x0007B150..<0x0007B1C4` | `nrfx_saadc_uninit` | `d1c097f7ef7d2b06624acbf65d5d8b652900352b3efded7a7201df5cfcda1fe2` |

These bodies match `modules/nrfx/drivers/src/nrfx_saadc.c` in the pinned Nordic SDK. Their ledger
disposition is `use_nordic_sdk`.

### R1 adapter bodies

| Extent | Clean-room role | SHA-256 |
| --- | --- | --- |
| `0x00054864..<0x000548F0` | name lookup, driver/channel configuration, settling | `16ec92db60099eff5d5ffb34342fa43c9e0ee79dc4f8af8f180b281097a50385` |
| `0x000548F0..<0x0005493C` | named blocking sample adapter | `cc37f1a092c14c62a440e0b354cc109c5a1a47bbbda76763695e3cedddc6b2b6` |
| `0x0005493C` (46 executable bytes) | record registration | `d78efd269f6b380c47dfe4ad35d3cff6782021b96d3a00f75a8d4c9047cc8483` |
| `0x00091184..<0x0009123A` | five-sample battery filter and conversion | `deaf339da23f60478f08800d1dbea8b56f969f18bdd2d145dd252308863ca80b` |

Their ledger disposition is `clean_room_adapter_only_use_nordic_sdk`. The clean port substitutes a
small fixed route table and direct Nordic calls for the stock generic registry.

### R1 battery behavior

| Extent | Behavior | SHA-256 |
| --- | --- | --- |
| `0x00031FCC..<0x00032168` | runtime voltage/state service | `863f83ebcc66161453cb498ddbef63e81ea83d42424291e15534367fb4cea5fb` |
| `0x0003DB70..<0x0003DC80` | stalled-charge recovery | `c4624ea1b01d6c199e5c5c94f2b9809860c30cf071a8c9fc02fce75b9b226324` |
| `0x0003DD0C..<0x0003DD9C` | charged-state refresh/full gate | `172542219c4cd2b4ec88c1b3c9d22231e42f77bc3d6bf34e36b2d82096a9d9db` |
| `0x0004FE5C..<0x0004FE6A` | charging progress reset | `70abea51fe92f022617bae783fea1cb37223cfc1f9454003ea81b8493c3a7b68` |
| `0x0004FE70..<0x0004FF32` | charging cadence | `29f00e75116b1d16868e25b73f08a01ba21f20828cc22ddcdd4713dfba8710fb` |
| `0x0004FF3C..<0x00050004` | charging initial curve | `9ea86a27b3e2625272a15695213e278f01c7feb31ed0a298ca78491a6afb5364` |
| `0x00050004..<0x000500BA` | discharge curve | `8220077c7133d7d5ce08ed96ba3f2e30d01086dafe1a6f12e259bb709343395b` |
| `0x00096AD0..<0x00096C62` | PMIC charge-event dock-status and thermal policy | `a079977932ae1d297bb451311bc998e001d9b3ae13efe0ff2769f14bc00ef67a` |
| `0x00047F10..<0x00047F9A` + `0x00096CC8..<0x00096DB4` | composite PMIC-charged retry and completion policy | `a00d2417c36d598e48d0372052fabccf0444ea0ced5a0252ba33983ad912a34f` |

Ghidra recorded `0x00031FCC` as a four-byte NOP-only function. All callers enter that address and
fall through the runtime body; the ledger therefore applies the independently verified 412-byte
extent ending before the literal pool at `0x00032168`.

The same service also has a native Ghidra entry at `0x00031FD0..<0x00032166`: 406 bytes with
SHA-256 `81fbdac0326291722319030ab711e90075c000759f03e34c3dbf2c1e3291cfd6` and direct
callsites `0x0009127A` and `0x000913CE`. It is now explicitly product-routed rather than left as
an overlapping unclassified entry. The reconciliation retains the four leading veneer bytes and
two trailing alignment bytes in the existing 412-byte manual extent; it creates no second
algorithm implementation. Reproduce this check with
`python3 tools/evidence/summarize_r1_battery_runtime_service.py`.

## Implemented behavior

- Battery acquisition requires exactly five samples, discards the two lowest, averages the other
  three, and applies `(average * 0xD5154) / 0x79D38` with integer truncation.
- Persisted compensation is applied only in `-299...299`. Charging divides through the exact
  Float32 value with bit pattern `0x3F86C8B4`.
- PMIC current sense clamps three signed samples at zero, averages them, then applies
  `(average * 1200 + 2048) >> 12`.
- NFC rectifier conversion clamps/averages three signed samples and applies
  `(((average * 3600 + 2048) & 0x0FFFFFFF) >> 12) * 331 / 51`.
- All four 20-segment discharge and charging-initial curves are retained, including the anomalous
  type-1 terminal charging word. Inputs at or below 2399 mV return the stock fallback of 50.
- Charging progression uses the recovered 38/60/108/480 or 48/72/144/480-second bands, caps each
  elapsed update at 180 seconds, and keeps reported full state separate from internal progress.
- The charged refresh counter saturates at 8; 4341 mV plus at least five full-state refreshes
  reports 100 percent.
- Stalled-charge recovery is a one-shot per unchanged episode and requires an unchanged value at
  most 98 percent, both samples at least 2400 mV, a 35 mV rise, and 120 seconds.
- A portable controller implements recovered charge-state entry/exit, cadence reset, refresh-count
  saturation, recovery-latch timing, and synchronization into `r1_runtime.device`. The Nordic
  adapter retains a voltage-to-controller bridge but has no autonomous producer until licensed
  PMIC state and power operations are available.
- A pure PMIC charge-event planner builds the exact 24-byte dock working template, maps public
  charge state to the private two-bit encoding, and returns low/mid target or raw high-limit
  actions. It does not execute YHM, ST, timer/event, logging, or transport operations; see
  [`PMIC-CHARGE-EVENT-CORRELATION.md`](PMIC-CHARGE-EVENT-CORRELATION.md).
- A pure PMIC-charged notification planner preserves the strict 50/4,200 mV gates, UInt8 retry
  state, 200/409 ms recovery request, ST mailbox completion decisions, and 5,120 ms post-charge
  schedule without executing vendor or hardware operations; see
  [`PMIC-CHARGED-NOTIFICATION-CORRELATION.md`](PMIC-CHARGED-NOTIFICATION-CORRELATION.md).

Host tests cover normal and boundary behavior, invalid sample counts/types, conversion truncation,
all profile families, elapsed-time carry, the full gate, saturation, the recovery latch, controller
transitions, invalid-state immutability, and runtime-state propagation. The image verifier requires
every battery helper, controller entry point, runtime seam, and analog bridge to have a nonzero
linked address. The verified unsigned Nordic image is 94,804 bytes text, 236 bytes data, and
132,544 bytes BSS.
Its standalone HEX and BIN SHA-256 values are
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf` and
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.

## Remaining gates

- Preserve the completed Zephyr YHM2710 semantic lease binding and keep raw register/transport
  operations outside the analog module; decide separately whether the legacy Nordic target should
  adopt the reconstructed provider.
- Confirm the decoded installed battery type and compensation against an owned ring; startup
  adoption is source-bound and read-only, but physical calibration remains unverified.
- Validate divider/amplifier gain, offsets, noise, temperature behavior, and sample timing against
  calibrated equipment on an owned ring.
- Bind a periodic producer to the retained runtime bridge only after typed PMIC charge-state input
  and physical validation are available. Current/rectifier functions remain
  internal retained APIs.
- Preserve the absence of raw ADC, PMIC write, ship-mode, and unrestricted diagnostic BLE routes.

This work does not alter signing, rollback, boot verification, or deployment policy.
