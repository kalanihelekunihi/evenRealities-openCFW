# Independent gesture speed closure

New [source/header](../../components/touch/gesture_speed_offline/README.md) closes helper `0x3efc..0x4040`, previously a borrowed dependency of the gesture machine. This standalone source does not call retained firmware. Selected native sections can also replace that helper in the offline composed fixture, while leaving the larger original gesture body explicit. No production image, index, device, shared state or commit changed.

## State and computation

The 80-byte gesture state contains three eight-byte samples starting at +48: position byte at +0 and counter u32 at +4. Ring index +72 is 0–2, sample count +73 saturates at 3, filtered speed +74 is a byte and direction +75 is signed −1/0/+1. The helper writes the current sample, advances the ring modulo three, then compares the newest and immediately preceding sample once at least two samples exist.

Position change > 3 establishes direction +1; change < −3 establishes −1; changes within ±3 leave the existing direction. A nonzero direction reversal clears the filter before processing the new speed.

Elapsed counter arithmetic is unsigned modulo 32 bits. For unequal timestamps:

`speed = min(255, floor((abs(position_delta) * 100 + elapsed / 2) / elapsed))`

When the old filter is zero it adopts speed directly. Otherwise:

`filtered = floor((4 * speed + 6 * old_filtered) / 10)`

For equal timestamps it returns the existing filter, or 1 if the filter is zero, **without storing that fallback**. Fewer than two samples or null state returns 0. This behavior matters for stationary/wrapped-time inputs and direction reversals; it is not a physical velocity calibration. Malformed ring indices/counts are outside the bounded source contract.

## Evidence

Standalone ELF SHA `eea51dda7a9968c1c14ab8769ef92de7549b2025ce6f6e5dcfcff93083d6e2d3`:

- **5,042 original/native comparisons PASS**, no function-entry cuts and no MMIO/SROM model. Original memory/division/logger instructions execute; native helper is standalone source.
- **324/324 original instruction bytes visited**.
- Three rejected mutants: retain filter on reversal, change smoothing weights, store the equal-timestamp fallback.
- **336 additional composed report/calibration comparisons PASS** with native speed replacing the old helper in offline guest memory. Original gesture `0x4070` remains borrowed; the prior calibration module itself stays sealed and unchanged.

The standalone matrix crosses three ring indices, four sample counts, four filters, three directions, seven position pairs, five elapsed values including equal timestamps and unsigned wrap, plus two null-state cases. Unrelated state bytes vary deterministically. Compared complete state, return, SP and PRIMASK. This is bounded functional coverage, not malformed-memory safety or physical timing proof.

`fixture.ld` places source-defined speed at the original entry and its division support at `0x110000`; a size assertion limits the helper section to its original 324-byte extent. The composed harness loads only these selected sections. This is an offline source substitution, not byte-identical firmware, and no function-entry hook supplies synthetic returns. SROM responses and sensor structures in the composed report test remain synthetic.

## Cumulative navigation and next closure

- [EEPROM read/history/write](../../components/touch/eeprom_offline/README.md): independent storage control flow, with SROM as an external model.
- [Initialization](../../components/touch/eeprom_init_offline/README.md): factory configuration and library readiness.
- [Bootstrap](../touch-bootstrap-closure-2026-10-08/REPORT.md): record validity, defaults and recovery.
- [Calibration/report](../touch-calibration-closure-2026-10-08/REPORT.md): baseline update ordering, hold threshold and SysTick counter provenance.
- This directory: independent speed helper; larger gesture machine remains the next executable dependency.

No external input blocks independent gesture-machine reconstruction. Actual clock cadence, analog samples and device durability remain separate hardware questions. No source-complete or whole-OTA equality claim; SDK producing revision ambiguity remains.
