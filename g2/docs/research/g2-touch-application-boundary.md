# G2 touch application/startup boundary (batch 7)

This software-only admission resolves the 99-function
`application_startup_clean_room` classification without assigning speculative
behavior. It performs no hardware access and is not routed into production.

Two target bodies are exact matches for the public Apache-2.0 CAT2 PDL
critical-section assembly at commit
`35f1714623cfea682d5e285af80d50416b4c7bbc`:

- `0x1192`: `Cy_SysLib_EnterCriticalSection`
- `0x119A`: `Cy_SysLib_ExitCriticalSection`

The namespaced isolated adaptation is
`runtime_touch_critical_adapters.S`. The analyzer pins both the upstream file
digest and each target instruction-body digest and requires a Cortex-M0+
compile.

The other 97 rows have no authenticated public body or established behavior.
They are therefore exhaustive, non-source clean-room reimplementation
contracts: 46 platform/startup/configuration rows below `0x156C` and 51 touch
application-processing rows at or above it. These coarse labels are an address
partition for work planning, not behavior claims. The MIT provider contract
fails closed when absent and carries the shipped entry explicitly so later
implementations can be admitted one at a time.

This changes application-family ambiguity from 99 to zero, but it only reduces
the concrete source/implementation gap from 111 to 109. The 97 contracts remain
unimplemented and are not counted as OpenCFW source. CAPSENSE and Em_EEPROM
EULA implementations remain separate external providers.

Reproduce the evidence and manifests with:

```sh
python3 g2/tools/analyze_g2_touch_application_boundary.py --write-manifests
python3 -m unittest \
  g2.tests.test_analyze_g2_touch_application_boundary \
  g2.tests.test_runtime_touch_application_boundary
```
