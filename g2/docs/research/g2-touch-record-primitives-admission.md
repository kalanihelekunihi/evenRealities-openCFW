# G2 touch argument-relative record transforms (batch 9)

Batch 9 admits seven call-free MIT clean-room source candidates totaling 200
shipped instruction bytes. Their complete functional behavior is established
by authenticated control/data flow over argument-relative buffers. This
software-only tranche performs no MMIO or hardware execution and is not routed
into production.

The source implements a fixed-offset reset, gated copy, two- and three-value
replication, two/four-sample history transform, three-word bit-mask transform,
and threshold/delta transform. Names describe only raw register and buffer
effects and retain each shipped entry address. They do not assign a product
role, object identity, callback ABI, or volatile/atomic access guarantee.

Admission requires the full canonical target body, no direct call, no
PC-relative literal, argument-relative memory only, MIT source declarations,
symbol presence, and a Cortex-M0+ compile. Host tests cover every branch family,
boundary values, deterministic randomized masks and history inputs, and the
optional-pointer path.

The concrete source/implementation gap falls from 93 functions / 8,524 bytes to
86 functions / 8,324 bytes. The residual remains 74 unimplemented application
contracts plus the ten Em_EEPROM EULA rows, one unavailable system-handoff row,
and one unavailable halt provider. Those provider boundaries remain non-source.

Reproduce the tranche with:

```sh
python3 g2/tools/analyze_g2_touch_record_primitives_admission.py --write-manifests
python3 -m unittest \
  g2.tests.test_analyze_g2_touch_record_primitives_admission \
  g2.tests.test_runtime_touch_record_primitives
```
