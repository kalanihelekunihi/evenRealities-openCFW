# CapSense slider sample-to-position CPU closure

New [independent offline source](../../components/touch/slider_producer_offline/README.md) reconstructs the selected CPU slider producer from acquired raw counts through clamp, baseline, difference, debounce, centroid and position IIR. It composes with the preserved native gesture/speed/report/storage code. No production firmware, index, shared state, device or commit changed.

## Locked configuration, not fixture defaults

The reset-copy table maps source `0xb58c` to RAM `0x200004c0`. Global CapSense context `0x200004ec` points to immutable widget configurations starting `0xb0f8`, stride144. Widget1 at `0xb188` is type2, method1, four sensors, resolution200, centroid config1, position filter config `0x00800102`, raw-filter flags `0x6000`. Its widget context starts `0x20000584`, sensors `0x20000624`, debounce `0x200009f8`, position-filter history header `0x20000848`.

| Factory field | Proven value |
| --- | --- |
| Finger threshold |480|
| Hysteresis |55|
| Noise / negative-noise thresholds |300 /200|
| Negative-baseline reset count |30|
| Baseline IIR coefficient |1 /256|
| On-debounce |1|
| Position IIR coefficient |128 /256|
| Software sensor auto-reset |Disabled|
| Initial maximum raw count |0; populated by runtime setup/calibration|

The pinned [Infineon6.10 processing source](https://github.com/Infineon/capsense/blob/247a9a0f79eb976f144f5fbeb29488c1c2606517/cy_capsense_processing.c), [centroid](https://github.com/Infineon/capsense/blob/247a9a0f79eb976f144f5fbeb29488c1c2606517/cy_capsense_centroid.c) and [filter](https://github.com/Infineon/capsense/blob/247a9a0f79eb976f144f5fbeb29488c1c2606517/cy_capsense_filter.c) corroborate this algorithm family and field meanings. This is not a unique producing-version or exact compiled-byte claim. Comparator sources/license remain cached in `/tmp`; new repository C is instruction-derived reconstruction. Download receipt records pin and content hashes.

## Producer order and interfaces

Original main path calls process-all `0x4c04`, visiting widgets2,1,0 and skipping disabled/type7 entries. Its selected widget processor `0x4ba8` rejects index>2 or type7 with1, unready runtime bits `(status &6)!=6` with8. It then clamps raw values `0x5bc0`, processes sensor raw/baseline/difference `0x5938`, and runs slider status/centroid `0x5a94` through type dispatcher `0x5ba2`. Method!=1 returns status1 **after** raw processing. Native scope is slider types2/3 and type7/out-of-range guards; proximity type6 remains separate.

Sensor layout is10 bytes: `raw u16+0`, `baseline u16+2`, `difference u16+4`, status byte+6, negative-reset count+7, baseline fraction+8, compensation+9. SDK structure labels agree with these instruction offsets. Acquired raw values are inputs here; hardware scan/IIR/common-mode are not replaced. Actual slider `0x6000` has optional CPU median/IIR/average bits disabled, so original filter dispatcher `0x50a0` makes no filter calls on this path.

Baseline updater `0x4fee` first clears the negative counter when raw>=baseline. If baseline>raw+negative-noise, it increments the counter while below its limit, then resets baseline to raw and clears fractional/counter state. With limit30 and initial counter0, reset is on the31st qualifying sample. Otherwise, baseline updates only inside the positive-noise window or when software auto-reset is enabled. It preserves an8-bit fraction:

`history = (baseline <<8) | fraction`

`history = (raw_shifted * coefficient + history * (256-coefficient)) >>8`

Difference `0x5920` becomes raw−baseline only when raw>baseline+noise; otherwise0. Thus baseline updates **before** difference/activity/position. The selected baseline-integrity helper `0x4db4` is an actual return-zero leaf; no invented integrity rejection.

Slider threshold is finger+hysteresis while inactive, finger−hysteresis while active: **535 /425** for locked startup values. Each sensor is active only when difference strictly exceeds threshold. Debounce decrements before the decision; an inactive scan reloads the configured count and clears widget activity. Activity during unexpired debounce clears sensor statuses. With factory count1 the first qualifying processing invocation can activate. Configuration count0 has unusual zero-counter behavior; synthetic tests do not imply that configuration is deployed.

## Centroid and position filtering

Centroid `0x48cc` forces its scan count to at least3, so declared count0–2 is not memory safety: tests still allocate four records. With centroid-number bits1, it finds the maximum difference, then chooses the candidate with greatest three-sensor neighborhood sum. Strict comparison retains the **first** tie. Equal positive signals on all four sensors therefore choose the first interior candidate (index1), producing67 at resolution200; it does not average every active sensor.

Neighbor interpolation uses a signed fractional correction, fixed-point multiplier and +127 rounding before shifting8. Alternate config bit256 changes multiplier/offset. Explicit modulo32 multiplication preserves stock arithmetic. No signal publishes count0; unsupported centroid-number settings leave the incoming count unchanged.

Position filter `0x4a2a` uses history count and configured stride. First/new positions seed history without smoothing; continuing positions use IIR. Actual coefficient128 gives half current/half previous with truncation. Inactive output updates count0 but leaves public coordinates untouched. Reactivation seeds history again. Direct filter sentinel255 and initialized multi-position records are tested separately.

Stock local centroid positions initialize X/count but leave Y/Z/padding stack bytes undefined. Native local non-X fields are zeroed deliberately; **those bytes are excluded from slider equality claims**. Direct initialized filter records have full-record comparisons. The report consumer uses activity and X; its position argument is the low8 bits of X (actual configured resolution200 fits).

## Validation

Final standalone ELF SHA `e5603b1ed181537b6ff9bcf7e3f094a73a54956a386cec68efc1cb04117080bc`.

| Suite | Result | Boundary |
| --- | --- | --- |
| Slider/debounce/centroid/IIR |368 PASS|Defined X/count/status/context/history fields; synthetic differences|
| Selected full CPU raw-to-position |483 PASS|Synthetic acquired raw, clamp/baseline/difference and guards; no ADC|
| Direct initialized position filters |64 PASS|Full initialized X/Y/padding/history records; at most2 positions|
| Negative controls |4 rejected|Inclusive threshold, publish during debounce, last centroid tie, wrong IIR weights|
| Native producer→gesture/calibration/report |5 sequences /48 steps PASS|Native source chain; synthetic SROM and widget2 samples|

No function-entry return stubs. Original checksum/storage/gesture bodies execute for the original side; native side uses independently linked producer/gesture/speed/report/storage sections. Selected producer source sits at `0x112000` alongside preserved native gesture support at `0x110000`, loaded by section rather than ELF segment padding. This is an offline fixture, not firmware integration. Raw acquisition, timing, IRQ scheduling and physical durability remain external.

Composed sequences use locked thresholds/coefficients and an explicitly synthetic calibrated maximum raw count3000. They establish: position200→166→116→58 under motion/IIR; stale58 after release with count0; inactivity at difference535, activation536, persistence426 and release425; hold at callback threshold1000; negative-baseline reset; and raw clamp before processing. All event frames and record/storage effects compare. Pending calibration still waits for a report, and that report carries the **prior saved baseline**, as in the preserved calibration batch. No-event TX retains the previous frame.

## Remaining actionable gaps

Maximum raw count runtime initialization and hardware IIR/common-mode/scan acquisition remain unreconstructed; do not assume the synthetic3000 value. Widget2 type6 uses a different CPU raw-filter configuration `0x3696` and proximity thresholds/debounce, with median/fractional-IIR/average helpers: this is the next bounded producer closure. SDK6.10 is a pinned semantic comparator, not uniquely attributed source. Physical sample/cadence/interrupt behavior requires additional static closure or captures; there is no external-input blocker for continuing the proximity software path. No whole-image source-completeness or byte-equality claim.
