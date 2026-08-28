# G2 touch closed record-processing source (batch 10)

Batch 10 admits seven MIT clean-room source candidates totaling 388 shipped
instruction bytes. Each target body is canonical and complete, and every direct
call terminates in either this batch or the previously admitted MIT leaf and
record primitives. No vendor body, literal-backed global, MMIO access, or
hardware execution is included.

The source covers a three-level reset cascade, a median-and-history shift, a
bounded counter/reset/update operation, integer/fractional blending, and an
ordered three-stage filter chain. Names describe only observed buffer effects
and retain shipped entry addresses. They do not assign product roles.

The reset cascade deliberately models the observed pointer graph as raw
little-endian buffers with native-width pointer slots. This matches offsets on
the 32-bit Cortex-M0+ target while allowing device-free host fixtures to store
host-native pointers. Tests cover the mode gate, each reset level, all median
orderings, every update branch, both blend formats, all eight filter-stage
combinations, and Cortex-M0+ compile/symbol closure.

The concrete source/implementation gap falls from 86 functions / 8,324 bytes to
79 functions / 7,936 bytes. The remaining census is 67 clean-room application
contracts plus ten Em_EEPROM EULA providers, one unavailable system-handoff
provider, and one unavailable halt provider. The larger loops at `0x1B6C`,
`0x1C54`, and `0x2638` remain unimplemented because their pointer-table and
iteration semantics are not yet sufficiently established.

This is isolated source admission only; it is not production-routed.

Reproduce the tranche with:

```sh
python3 g2/tools/analyze_g2_touch_closed_record_pipeline_admission.py --write-manifests
python3 -m unittest \
  g2.tests.test_analyze_g2_touch_closed_record_pipeline_admission \
  g2.tests.test_runtime_touch_closed_record_pipeline
```
