# G2 touch storage adapters (batch 15)

Batch 15 admits four application-owned storage adapters at `0x01D8`, `0x0220`,
`0x02B0`, and `0x02E4` as isolated MIT clean-room source. They cover provider
initialization and accepted-status translation, overflow-safe 256-byte reads,
a context operation, and the application counter increment.

The source injects the three Em_EEPROM operations as typed callbacks. It does
not copy, compile, or claim the Infineon EULA provider bodies at `0x5738`,
`0x5778`, or `0x57E0`; all ten Em_EEPROM provider functions remain external.
Exact canonical bodies, calls, spans, and accepted status `0x093E0004` are
pinned. Host tests exercise both accepted statuses, failures, bounds,
readiness, counter wrap, fail-closed callbacks, and Cortex-M0+ symbol closure.

The concrete source/implementation gap falls from 60 functions / 5,278 bytes
to 56 functions / 5,120 bytes. Application contracts fall from 48 to 44;
twelve external/unavailable functions remain. Resident loaders, system/halt,
and `0x1B6C`/`0x1C54`/`0x2638` remain unadmitted.

This source is isolated and not production-routed. No MMIO or hardware path is
executed.

```sh
python3 g2/tools/analyze_g2_touch_storage_adapters_admission.py --write-manifests
python3 -m unittest \
  g2.tests.test_analyze_g2_touch_storage_adapters_admission \
  g2.tests.test_runtime_touch_storage_adapters
```
