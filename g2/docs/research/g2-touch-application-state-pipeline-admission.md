# G2 touch application-state source (batch 11)

Batch 11 admits eleven MIT clean-room source candidates totaling 952 shipped
instruction bytes. The selected functions form closed argument-relative state
operations: conditional copy and pair blending, record synchronization, packed
field construction, object reset, lane/counter updates, object and record value
caps, enabled-mode wrappers, and a nested status-bit query.

Every canonical target body and direct-call set is pinned. Calls resolve to the
same batch, the previously admitted MIT blend primitive, or exact memcpy/memset
behavior that the new source expresses as bounded MIT loops. The only
PC-relative value admitted is the shipped immediate mask at `0x1FB8`
(`0x0FFF0000`). No MMIO or vendor body is executed or copied.

The superficially attractive 172-byte loader at `0x1FBC` is deliberately not
admitted: it copies configuration tables beginning at resident address
`0xB41C`, outside the shipped prefix. Those tables remain part of the external,
unavailable resident ABI. The uncertain `0x1B6C`, `0x1C54`, and `0x2638`
pointer-table loops also remain unimplemented.

Host tests use explicit 32-bit pointer tokens resolved only by a test fixture,
so adjacent target pointer slots retain their actual four-byte layout on a
64-bit host. Tests cover all recovered branches, state transitions, mode gates,
packing variants, caps, and a Cortex-M0+ compile/symbol-closure check. No device
or MMIO path is used.

The concrete source/implementation gap falls from 79 functions / 7,936 bytes to
68 functions / 6,984 bytes. The remaining census is 56 clean-room application
contracts plus ten Em_EEPROM EULA providers, one unavailable system-handoff
provider, and one unavailable halt provider.

This source is isolated and not production-routed.

```sh
python3 g2/tools/analyze_g2_touch_application_state_pipeline_admission.py --write-manifests
python3 -m unittest \
  g2.tests.test_analyze_g2_touch_application_state_pipeline_admission \
  g2.tests.test_runtime_touch_application_state_pipeline
```
