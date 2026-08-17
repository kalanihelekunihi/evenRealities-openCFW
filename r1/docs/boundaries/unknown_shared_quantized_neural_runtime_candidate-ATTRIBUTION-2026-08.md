# Attribution re-examination 2026-08: shared quantized neural runtime and interlocked platform families

Date: 2026-08-14. Scope: `unknown_shared_quantized_neural_runtime_candidate` (primary), plus the
interlocked `unknown_time_calendar_provider_candidate`, `unknown_software_twi_provider_candidate`,
`unknown_generic_device_registry_candidate`, `unknown_sensor_stream_framework_candidate`, and
`unknown_rtc_device_provider_candidate` families, per the provenance tasking. Read-only analysis;
no ledger, generator, or source files were modified.

## Family under test (primary)

`unknown_shared_quantized_neural_runtime_candidate`: 28 functions / 2,746 executable bytes,
spanning `0x000290FE..0x000294B6`, `0x00035E34..0x00035F26`, `0x00036C7C..0x00036D60`,
`0x00041816..0x000419C8`, `0x00058D4A..0x00058D52`, `0x0005A3D4..0x0005A40E`, `0x0005D244..0x0005D2DC`,
`0x00065680..0x000656AA`, `0x0006FE20..0x0006FE56`, `0x00074A9C..0x00074D02`,
`0x00085B9C..0x00085C98`, `0x00091C48..0x00093744`, and
`0x00098EDC..0x00098F80`. The `0x00085B9C` float dense executor is a later
manual-provenance supplement: Ghidra missed the function, but constructor
`0x00074BE0` installs its `0x00085B9D` Thumb entry and disassembly pins the
complete body before its literal pool.
The later callback-entry reconciliation adds the eight-byte qsort comparator at `0x00058D4A`:
the arena compactor installs its odd Thumb pointer and the local static `compare_live_entries`
reproduces its three loads/subtract/return instructions.

## Methods

1. Line-level review of the decompiled bodies in
   `r1/research/decompilation/application/decompiler-output.c`.
2. Constant extraction from `r1/research/decompilation/rebuild/rebuilt-application.bin`
   (load base `0x27000`, SHA-pinned by the evidence tools).
3. Independent Capstone (5.0.7) disassembly of the regions Ghidra omitted (the software-TWI
   engines at `0x00055330..0x00056274`, a 4,102-byte gap `0x000552DA..0x000562E0` in
   `disassembly.s`), to verify the boundary docs' structural claims first-hand.
4. Authenticated GitHub code search (`gh api search/code`) for distinctive strings, constants,
   and idioms across all public repositories.
5. Direct fetch of candidate upstream sources (CMSIS_5 5.9.0, CMSIS-NN v4.0.0, newlib) and
   line-by-line comparison.
6. Web search for vendor fingerprints (`dlCom`, `603M`, `B210`).

## Hypothesis H1 (primary): CMSIS-NN — REJECTED, decisively

The tasking hypothesized that `round_half_away_from_zero` and
`shared_float_to_signed_int8_quantizer` resemble CMSIS-NN requantization helpers (`NN_ROUND`,
`arm_nn_float_to_s8`, `arm_pool_q7_HWC_q15`, `arm_softmax_q7`). Fetched and compared the actual
sources:

- CMSIS_5 5.9.0 `CMSIS/NN/Include/arm_nnsupportfunctions.h`:
  `#define NN_ROUND(out_shift) ((0x1 << out_shift) >> 1)` — an integer shift-offset macro, not a
  float function. Requantization is `arm_nn_requantize()` =
  `arm_nn_divide_by_power_of_two(arm_nn_doubling_high_mult_no_sat(...))` — pure integer
  multiplier/shift fixed-point.
- CMSIS_5 5.9.0 `arm_softmax_q7.c`: base-2 softmax (`y_i = 2^(x_i) / sum(2^x_j)`) using
  `__USAT`/`__SSAT` shifts — no float, no expf.
- CMSIS-NN v4.0.0 `arm_softmax_s8.c`: fixed-point `EXP_ON_NEG` polynomial (`1895147668`,
  `715827883`, ...) on quantized integers — no float.
- Authenticated repo-wide code search: `float_to_s8` in `ARM-software/CMSIS-NN` → 0 files;
  `float path:CMSIS/NN` in `ARM-software/CMSIS_5` → 0 files. CMSIS-NN contains no
  floating-point code at all, in any era.

The firmware bodies are the opposite arithmetic regime. `FUN_000290fe`/`FUN_00029120`
(decompiler-output.c:3904-3939), the two byte-identical 34-byte round helpers:

```c
int FUN_000290fe(float param_1) {
  float fVar1;
  if (param_1 <= 0.0) fVar1 = -0.5; else fVar1 = 0.5;
  return (int)(fVar1 + param_1);   /* truncate(x ± 0.5): round half away from zero, in float */
}
```

`FUN_000293fc` (float→int8 quantizer, decompiler-output.c:4181-4236) computes
`(x - min) * (255.0f / range)` in float, rounds via the ±0.5 helper, clamps to `[0, 255]`, and
stores `q - 0x80` as int8 with float `{min, max}` metadata written back to the output tensor.
`FUN_0005d244` (decompiler-output.c:53902-53943) is a *float* softmax: max-reduce from
`-FLT_MAX` (`0xFF7FFFFF`), `expf` via `FUN_00038f08` with the exponent input capped at `88.0f`
(`DAT_0005d2e4 = 0x42B00000`), floating sum, floating divide. Constants recovered from the
image: quantization domain `255.0f` (`0x437F0000`), range epsilon `1e-4f` (`0x38D1B717`),
nudge bounds `253.0f`/`254.0f`, exp cap `88.0f` — none of which exist anywhere in CMSIS-NN.

Beyond arithmetic, CMSIS-NN kernels are stateless functions taking explicit dimension/offset
arguments; the firmware runtime is a descriptor-driven static graph: 24-byte layer records,
eight packed parameter bytes, function pointer at `+0x14`, a 12-slot tensor pool with `0x14`
stride, and a `0x6A4`-word compacting arena (`FUN_00093628`). No CMSIS-NN version has such an
ABI.

Verdict: **no match** — CMSIS-NN is eliminated at the arithmetic-regime level (integer-only vs
float requantization), the kernel-behavior level (pooling executor supports only window-2 max
unrolled ×4 / window-4 max / window-3 average, nothing like `arm_pool_q7_HWC_q15`), and the ABI
level. The prior boundary doc's rejection stands, now with quoted upstream evidence.

## Hypothesis H2: other public NN runtimes — REJECTED (confirmation of prior rejections)

- TFLM (tflite-micro): **eliminated at four independent levels** against the actual
  decompiled bodies in `decompiler-output.c`.
  1. Language/ABI: TFLM is a C++ flatbuffer interpreter whose kernels take
     `RuntimeShape`-driven `reference_ops` calls; the firmware runtime is plain C with
     3-byte layer descriptors and 24-byte layer records — no C++ ABI, no flatbuffer
     schema anywhere in the runtime path.
  2. Quantization regime: TFLM's quantized add is integer fixed-point
     (`ArithmeticParams` multipliers/shifts); the firmware int8-add dequantizes to
     float, adds, and requantizes through the round-half-away-from-zero helper
     (`FUN_000290fe`) — opposite arithmetic regimes, as with CMSIS-NN above.
  3. Kernel behavior: TFLM's float softmax has no exponent cap (the firmware caps the
     `expf` input at `88.0f`, `DAT_0005d2e4 = 0x42B00000`); TFLM average-pool rounds
     unsigned half-up while the firmware pooling rounding is sign-aware; and the
     firmware pooling executor supports only window-2/4 max plus window-3 average —
     nothing like TFLM's general pooling kernels.
  4. Memory model: TFLM's `MicroAllocator` is an offline-planned bump arena; the
     firmware has a 12-slot tensor pool with `0x14` stride and a qsort+memmove
     compacting arena (`FUN_00093628`). No match at any level.
- tinyMaix (Sipeed, 2022): its int8 path does use float scales, but it is *symmetric*
  (`scale = max(|min|,|max|) / 127`); the firmware uses asymmetric min/max over a 0..255 quant
  domain with a −128 storage bias and endpoint-preserving range nudging. No match.
- NNoM (Qm.n q7 fixed point, dynamic allocation, HWC 3-D tensors), uTensor (C++), TinyEngine,
  emlearn, X-CUBE-AI: prior rejections re-confirmed as structurally incompatible with the
  recovered ABI/math. No match.

## Hypothesis H3: TensorFlow quantization "nudge" lineage — algorithm family only, NO source match

`FUN_00035e34` (decompiler-output.c:20004-20044) derives scale/zero-point as
`scale = 255.0f / max(1e-4f, max - min)` and, for `min < 0`, nudges the range so that 0.0 is
exactly representable: with `zpf = floor(-min * 255 / range)` and fraction `frac`, it either
keeps `max` fixed and solves `min' = (zpf+1)*max / (zpf-254)`, or keeps `min` fixed with
`range' = min*255 / zpf`, choosing by the error comparison `(frac-1)*min < frac*max`. This is
the TFLite-uint8-era quantization idiom (0..255 domain, round-half-away-from-zero, int8 storage
via −128 bias). Compared against TensorFlow's public nudge implementations
(`tensorflow/core/kernels/fake_quant_ops_functor.h`, `lite/kernels/internal/quantization_util.cc`
`NudgeQuantizationRange`): both recompute *both* endpoints from a nudged zero point at unchanged
scale — a different formula from the firmware's fixed-endpoint variant. The firmware's variant
matches no public source found. Verdict: **no match**; the math identifies an algorithm family
(TF-uint8-style asymmetric quantization), not an attributable library.

## Hypothesis H4: private "dlCom" toolchain — CONFIRMED as private; owner narrowed to the ring platform vendor

Embedded model provenance triples `{name, version, git hash}` assembled at `0x0006EC90`:
`dlCom_pre2exc` / `v1.3.0` / `c00c91c9`, `pv_v1.1.0` / `v2.0.3.0` / `21d2063d`,
`GH_SPO2_pre_pv_v2.1.10.0` / `277e89de` / `1f1cf98b`. Authenticated GitHub code search
(2026-08-14): `dlCom_pre2exc` → 7 hits, all inside this repository and its known mirror
(`AM-Guru/SybilSight`); `GH_SPO2_pre_pv` → same two repositories only; `pre2exc` → 19 hits, all
unrelated substring collisions. The `dlCom` (deep-learning compiler) toolchain has zero public
footprint, as previously recorded.

New this round: the runtime serves both the GoMore sleep-classifier graphs and the Goodix
GH_SPO2/dlCom graphs through one descriptor ABI, and its float-softmax exp cap (`88.0f`) is
shared with the GoMore float neural executor at `0x00076BDC` (same cap documented in
`GOMORE-NEURAL-RUNTIME-BOUNDARY.md`). One vendor's math-runtime conventions span both model
families. Combined with the platform-vendor identification below, the most probable owner of
`dlCom` and this runtime is the smart-ring platform vendor (Wuxi Bravechip) — which publicly
states its ring SDK "encapsulates BraveChip's physiological algorithms" — with Goodix as the
alternative owner of at least the GH_SPO2 model side. This cannot be resolved to an open-source
library. Verdict: **no open-source attribution; proprietary runtime, implementation stays
blocked.**

## Platform-vendor identification (NEW, high confidence): Wuxi Bravechip "ChipletRing" / BCL603M platform

Evidence chain:

1. The firmware's compatibility identity string `603MV1.9.3` (decompiler-output.c:80342, passed
   with `product B210_app, build B210_App` and the R1 app version `2.2.6.0009`) matches the
   **BCL603M3** "full-featured module for wearable smart rings" by **Wuxi Bravechip
   Technologies Co., Ltd. (勇芯科技)** — public datasheet (DS60313, rev V1.3 2025-03-11):
   PPG + temperature + accelerometer sensors, NFC, touch interaction, sleep monitoring, "Provides
   a standard APP and SDK, supports secondary development and OTA upgrades".
2. Byte-exact GATT UUID match. Bravechip's public app SDK
   (`BravechipSpace/ChipletRing-APPSDK`, `Android/.../ChipletRing-1.6.2-release.aar`,
   `com/lm/sdk/BLEService.class`) defines the ring service UUIDs
   `BAE80001-4F05-4503-8E65-3AF1F7329D1F` / `BAE80010-...` / `BAE80011-...`. The R1 image
   stores at flash `0x000991A0` the 128-bit base
   `1F 9D 32 F7 F1 3A 65 8E 03 45 05 4F 00 00 E8 BA` — the identical base with the Nordic
   `ble_uuid128` zeroed 16-bit alias field and 16-bit UUID `0xBAE8`. This is the "BAE8 custom
   GATT service" of `BAE8-EVENT-ROUTER-CORRELATION.md`. A 128-bit UUID base collision by chance
   is not plausible.
3. Bravechip's SDK example app contains `GoMoreSleepActivity.java` (GoMore sleep integration)
   and bundles `st25sdk-1.13.0.jar` (ST25 NFC) — matching the R1 firmware's GoMore sleep
   classifier, Goodix GH3x2x demo code, and ST25DVxxKC NFC tag stack.
4. Bravechip's OTA firmware files in the same repo are named `2.4.4.81.hex16`,
   `2.3.7.511S.hex16`, `2.4.8.6Z3K.hex16` — the same `x.y.z.w` version scheme as the R1's
   `2.2.6.0009`.

Interpretation: the R1 (Even Realities board codename `B210`, build path
`product/B210/app/_build/B210_Application` per leaked `__FILE__` strings) is built on
Bravechip's proprietary BCL603M/ChipletRing ring platform; the `platform\...` source tree
(`platform\threads\thread_manager.c`, `platform\services\eAT\at_system.c`) is the vendor's
platform middleware. This identifies the *owner* of the interlocked families. It does not
provide source or license: Bravechip distributes only an app-side SDK; the firmware platform is
closed. Authenticated GitHub searches for `eAT_core_init`, `B210_Application`, `device_stacmd`,
`sys rtc` (quoted) return no leaked platform source.

## Interlocked family test results

### `unknown_time_calendar_provider_candidate` — NO ATTRIBUTION (new negative tests added)

Bodies reviewed first-hand (decompiler-output.c:51231-51323): secs→tm fills POSIX `struct tm`
order (sec, min, hour, mday, mon, year-1900, wday, yday, 0-tail) with `wday = (days + 4) % 7`,
an iterative year loop from 1970, and a per-TU `static const uint8_t` dual month table
(24 bytes, `1f 1c 1f 1e ...`, verified in the image at `0x00099C5C`/`0x00099C74`); the reverse
converter hard-fails outside `tm_year ∈ [70, 129]`. New tests this round beyond the doc's
existing rejections (U-Boot, musl, modern newlib/Hinnant, Zephyr, Mynewt, NuttX, BES,
avr/picolibc):

- Old (pre-2014 tzcode-derived) newlib `gmtime_r`/`__tm_from_epoch`: same era and same
  `EPOCH_WDAY = 4` idiom, but it uses a shared `static const int __month_lengths[2][12]`
  (int, not byte), handles negative days, and never validates `tm_year ≤ 129`. Not a
  function-local match.
- Authenticated GitHub code search: `"tm_year > 129"` (C) → 0; `"tm_year < 70" "tm_year > 129"`
  → 0; `"year < 1970" "year > 2029" mktime` (C) → 0. The 1970..2029 validated range remains
  unique to this firmware.

Verdict: custom code inside the proprietary platform layer (now identified as Bravechip's);
no public source. Blocked.

### `unknown_software_twi_provider_candidate` — NO ATTRIBUTION (structure verified first-hand)

Capstone disassembly of the Ghidra-omitted region confirms the boundary doc: `i2c_2 open`
(`0x00055330`) loads a per-bus ops table and calls `op[0x1C](scl)`, `op[0x1C](sda)`,
`op[0x18](scl)`, `op[0x18](sda)`; `i2c_2 start` (`0x00055A18`) sequences
`op14/op14/op10/op10/udelay/op8/udelay/op0C/udelay` over the six-callback vtable {drive-low,
release-high, set-output, set-input(pin,pull), udelay(ctx), read-pin}. Comparison: Linux
`i2c-algo-bit` uses a five-callback struct {setsda, setscl, getsda, getscl, udelay} with
per-line set/get semantics — different decomposition, already rejected; Nordic
`twi_sw_master` and RT-Thread `i2c-bit-ops` rejections re-confirmed as structurally
incompatible. The engine drives sensors from four different vendors (GXT310, Goodix, ST25DV,
YHM2710) — platform middleware, not a sensor-vendor SDK. Verdict: proprietary platform code
(Bravechip); blocked.

### `unknown_generic_device_registry_candidate` / `unknown_sensor_stream_framework_candidate` / `unknown_rtc_device_provider_candidate` — NO ATTRIBUTION; owner identified

No new public-source match (prior rejections of RT-Thread, Zephyr, Nordic, Goodix demo SDK
stand; the `register not find obj:%s` / `lisent register fail` / `only support 1 ord` strings
still have zero external footprint). The cross-family interlock (positive status enum 0..12,
`sys rtc` / `i2c_n` naming, runtime registration) now resolves to the identified Bravechip
platform layer rather than an anonymous codebase. Blocked pending vendor source.

## Final verdicts

| Family | Verdict |
| --- | --- |
| `unknown_shared_quantized_neural_runtime_candidate` | **(c) NO ATTRIBUTION.** CMSIS-NN eliminated with quoted evidence (integer-only library vs float-requantizing descriptor runtime); TFLM eliminated at four independent levels (language/ABI, quantization regime, kernel behavior, memory model); NNoM/tinyMaix/uTensor/etc. re-confirmed incompatible; `dlCom` toolchain private with zero public footprint. Probable owner: ring platform vendor (Bravechip) or Goodix. Remains proprietary/blocked. |
| `unknown_time_calendar_provider_candidate` | **(c) NO ATTRIBUTION.** Old newlib additionally eliminated; [70,129] validation bound unique (zero code-search hits). Part of the Bravechip platform layer. Blocked. |
| `unknown_software_twi_provider_candidate` | **(c) NO ATTRIBUTION.** Structure independently re-verified by disassembly; no public bit-bang library matches the six-op vtable. Bravechip platform middleware. Blocked. |
| `unknown_generic_device_registry_candidate` | **(c) NO ATTRIBUTION.** Owner identified as the Bravechip BCL603M/ChipletRing platform (byte-exact BAE8 UUID base at `0x000991A0`; `603MV1.9.3`; GoMore + ST25 SDK bundling). Blocked. |
| `unknown_sensor_stream_framework_candidate` | **(c) NO ATTRIBUTION.** Same platform layer. Blocked. |
| `unknown_rtc_device_provider_candidate` | **(c) NO ATTRIBUTION.** Same platform layer (Nordic `nrfx_rtc_init` body already separately admitted). Blocked. |

## Recommended next evidence step

The attribution route is now commercial, not forensic: request the platform SDK/source (or a
license statement) from Wuxi Bravechip Technologies (public business contact in
`BravechipSpace/ChipletRing-APPSDK` README: xiaojian.cui@bravechip.com) or through the ODM,
covering the `platform/` tree, the software-TWI engine, the device registry, the sensor-stream
framework, the calendar converters, and the `dlCom` toolchain/runtime. A secondary forensic
route: acquire another Bravechip-based ring's firmware (the app SDK ships OTA hex files such as
`2.4.4.81.hex16`, apparently obfuscated/encrypted) and check for shared platform code with
richer `__FILE__` strings.

Reproduce the key new evidence:

```sh
# BAE8 base UUID in the R1 image (expect 1f9d32f7f13a658e0345054f0000e8ba at 0x991A0)
python3 - <<'EOF'
data = open('r1/research/decompilation/rebuild/rebuilt-application.bin','rb').read()
print(data[0x991A0-0x27000:0x991B0-0x27000].hex())
EOF
# Bravechip UUIDs
# gh api repos/BravechipSpace/ChipletRing-APPSDK/contents/Android/example/ringDemo/app/libs/ChipletRing-1.6.2-release.aar \
#   -H "Accept: application/vnd.github.raw"  ->  classes.jar: com/lm/sdk/BLEService.class
```
