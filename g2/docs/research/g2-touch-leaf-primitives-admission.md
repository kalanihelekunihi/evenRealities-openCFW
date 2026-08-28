# G2 touch call-free leaf primitives (batch 8)

Batch 8 admits sixteen MIT clean-room source candidates whose complete raw
AAPCS register behavior is established by their shipped call-free Thumb bodies.
This is an isolated software-only tranche: it performs no MMIO or hardware
execution and is not routed into production.

The admitted family contains six `bx lr` register pass-through bodies, six
constant-return bodies, and four pure `uint32_t` algorithms: a bounded modular
sum predicate, unsigned median-of-three, modulo-32-bit 8-bit blend, and a
mode/flag-dependent right-shift selector. The implementation uses descriptive
register-level names suffixed by shipped entry address. It does not assign
product behavior, object layouts, or callback roles.

No upstream body is claimed for these sixteen rows and no vendor source was
copied. Admission requires the complete canonical target body, no direct call,
MIT source declarations, symbol presence, and a Cortex-M0+ compile. Host tests
exercise boundary values, deterministic randomized arithmetic vectors, and all
selector partitions.

The concrete source/implementation gap falls from 109 to 93. The residual is
listed exhaustively as 81 unimplemented application contracts, ten Em_EEPROM
EULA-provider rows, one unavailable system-handoff boundary, and one unavailable
legacy halt provider. External/provider rows and typed contracts remain
non-source.

Reproduce the tranche with:

```sh
python3 g2/tools/analyze_g2_touch_leaf_primitives_admission.py --write-manifests
python3 -m unittest \
  g2.tests.test_analyze_g2_touch_leaf_primitives_admission \
  g2.tests.test_runtime_touch_leaf_primitives
```
