# G2 touch application packet source (batch 12)

Batch 12 admits the two-function `0x2248`/`0x23A4` packet/state builder as
isolated MIT clean-room source. Although it contains only two functions, the
pair removes 794 shipped instruction bytes, the largest coherent internally
closed application-state cluster remaining after Batch 11.

The source constructs fixed-layout entries, packs established buffer fields,
selects mode-dependent masks, and applies the already admitted three-word mask,
mode-scale, and record-pack primitives. Exact canonical bodies and direct-call
sets are pinned. The only PC-relative value admitted is the shipped immediate
mask at `0x23A0` (`0x0FFF0000`); it is not a pointer or resident table.

Host tests preserve the target's four-byte pointer slots with the existing
token resolver fixture. They cover both entry formats, mode-one scaling,
non-mode-one return behavior, both group strides, repeated list masks, child
masking, and Cortex-M0+ compile/symbol closure.

The concrete gap falls from 68 functions / 6,984 bytes to 66 functions / 6,190
bytes. The residual remains 54 clean-room application contracts and twelve
typed external/unavailable providers. The resident `0xB41C` table loader,
Em_EEPROM EULA functions, system handoff, halt, and the insufficiently evidenced
`0x1B6C`/`0x1C54`/`0x2638` boundaries remain unadmitted.

This source is isolated and not production-routed. No device or MMIO path is
executed.

```sh
python3 g2/tools/analyze_g2_touch_application_packet_pipeline_admission.py --write-manifests
python3 -m unittest \
  g2.tests.test_analyze_g2_touch_application_packet_pipeline_admission \
  g2.tests.test_runtime_touch_application_packet_pipeline
```
