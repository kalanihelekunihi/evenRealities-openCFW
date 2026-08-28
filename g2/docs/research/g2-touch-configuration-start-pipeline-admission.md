# G2 touch configuration/start source (batch 14)

Batch 14 admits the `0x1944`/`0x1972`/`0x197C` configuration/start family as
isolated MIT clean-room source. The three functions remove 354 shipped
instruction bytes while preserving complete argument-relative control/data
flow and explicit provider injection.

`0x1944` checks the capture state, invokes the already authenticated
Apache-2.0 CAT2 `0x5CA0` capture boundary, and routes the resulting application
event through the typed `0x37C0` provider. `0x1972` is the exact start wrapper.
`0x197C` reconstructs the fixed-layout state and record configuration before
routing initialization and start events. Exact canonical bodies, direct-call
sets, byte spans, and shipped literals `0x28F`, `0x084C`, and `0xF424` are
pinned. No provider body is copied into the MIT source.

Host tests use the existing four-byte pointer-token resolver and injected
callbacks. They cover busy and capture failures, event propagation, every
configuration field family, record flag construction, fail-closed null
contracts, and Cortex-M0+ compile/symbol closure. They do not execute MMIO.

The concrete source/implementation gap falls from 63 functions / 5,632 bytes
to 60 functions / 5,278 bytes. The residual remains 48 clean-room application
contracts and twelve typed external/unavailable providers. Resident tables at
`0xB41C`/`0xB4C4`, ten Em_EEPROM EULA functions, system handoff, halt, and the
insufficiently evidenced `0x1B6C`/`0x1C54`/`0x2638` boundaries remain
unadmitted.

This source is isolated and not production-routed. No device or MMIO path is
executed.

```sh
python3 g2/tools/analyze_g2_touch_configuration_start_pipeline_admission.py --write-manifests
python3 -m unittest \
  g2.tests.test_analyze_g2_touch_configuration_start_pipeline_admission \
  g2.tests.test_runtime_touch_configuration_start_pipeline
```
