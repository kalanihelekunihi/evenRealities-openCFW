# G2 touch selection/update source (batch 13)

Batch 13 admits the three-function `0x15CC`/`0x2794`/`0x28A2`
selection/update family as isolated MIT clean-room source. The family removes
558 shipped instruction bytes while preserving the target's argument-relative
object graph and complete internal call closure.

The source implements the evidenced three-sample peak selection and signed
position correction, lane/counter state update and result copying, and the
small mode dispatcher. Exact canonical bodies, direct-call sets, byte spans,
and the shipped `0x0000FFFF` sentinel at `0x16D0` are pinned. Division and copy
operations use clean-room primitives; no vendor body is copied.

Host tests preserve the target's four-byte pointer slots through the existing
token resolver. They exercise positive and negative corrections, disabled and
empty selection, lane/update result copying, dispatcher behavior, and
Cortex-M0+ compile/symbol closure.

The concrete source/implementation gap falls from 66 functions / 6,190 bytes
to 63 functions / 5,632 bytes. The residual remains 51 clean-room application
contracts and twelve typed external/unavailable providers. The resident
`0xB41C` loader, ten Em_EEPROM EULA functions, system handoff, halt, and the
insufficiently evidenced `0x1B6C`/`0x1C54`/`0x2638` boundaries remain
unadmitted.

This source is isolated and not production-routed. No device or MMIO path is
executed.

```sh
python3 g2/tools/analyze_g2_touch_selection_update_pipeline_admission.py --write-manifests
python3 -m unittest \
  g2.tests.test_analyze_g2_touch_selection_update_pipeline_admission \
  g2.tests.test_runtime_touch_selection_update_pipeline
```
