# G2 touch evidence-closed startup routines (batch 18)

Batch 18 admits four isolated MIT clean-room routines totaling 150 shipped
instruction bytes: the bounded 80-byte record initializer at `0x0D4C`, the
effect-free passthrough sequence at `0x11B4`, the ordered peripheral-divider
configuration at `0x11D0`, and the divider assignment at `0x1228`.

Every direct call and canonical target body is pinned. The record initializer
expresses exact zero-fill, first-halfword copy, and zero-to-1000 defaulting. The
three passthrough calls have no externally visible effect. Clock operations use
typed callbacks corresponding to the already authenticated Apache-2.0 CAT2 PDL
providers at `0x6CD4`, `0x6D1C`, `0x6DBC`, `0x6E04`, and `0x6E48`; host tests do
not execute their MMIO behavior.

No Em_EEPROM or CapSense EULA body, resident configuration table, direct MMIO,
or product policy is admitted. Host tests cover both timeout paths, exact
divider call order and arguments, fail-closed missing providers, and Cortex-M0+
compile/symbol closure.

The concrete gap falls from 54 functions / 4,872 bytes to 50 / 4,722 bytes;
application contracts fall from 42 to 38. All twelve external/unavailable
functions, resident loaders, EULA provider bodies, system/halt boundaries, and
`0x1B6C`/`0x1C54`/`0x2638` remain unadmitted. This source is isolated and not
production-routed, and hardware validation remains deferred by project
direction. The current Touch readiness summary is regenerated at Batch 18.
