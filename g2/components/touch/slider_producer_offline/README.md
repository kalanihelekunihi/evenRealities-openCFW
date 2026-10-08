# CapSense slider CPU producer — independent offline source

Selected widget-1 CPU path: acquired raw counts → maximum clamp → fractional
baseline update → noise-qualified difference → activity/debounce → linear
centroid → position IIR → public position/count. `slider.h` records the10-byte
sensor ABI and helpers; configuration pointers/layout remain the observed ARM32
144-byte widget/60-byte context ABI.

This module is bounded to the actual four-sensor slider with CPU raw-filter
bits disabled (`0x6000`). Hardware IIR/common-mode/acquisition are external.
Synthetic direct tests vary coefficients, thresholds, declared counts and
unsupported/disabled guards, with at least three allocated sensor records.
Widget2's proximity/raw-filter producer is not implemented by this module.

Defined X/count/status/baseline/debounce behavior is validated. Stock slider
locals leave non-X position fields uninitialized; native initializes those
fields to zero and excludes them from whole-record equality claims. Direct
position-filter tests use initialized records and compare all their fields.
No production integration, source-complete, analog or physical-time claim.

[Evidence and boundaries](../../../analysis/touch-slider-producer-closure-2026-10-08/REPORT.md).
