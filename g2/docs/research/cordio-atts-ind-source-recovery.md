# Cordio ATT server indication/notification recovery

The G2 stock `atts_ind.c` translation unit occupies
`[0x005338AC, 0x00533EF4)`: 1,552 bytes in 13 linked functions and 56 bytes
of authenticated gaps/literal data. Its retained source path and function
inventory match Packetcraft Cordio r20.05c. The two zero-copy public wrappers
are present in that source lineage but stripped from the stock link.

Maintained production source lives in
`components/shared/cordio/runtime_cordio_atts_ind.c`. All 13 linked entry
points are selector-isolated, compiled as Cortex-M55 C, and reached through
guarded entry redirects. The build emits 1,602 code bytes, 16 alignment bytes,
and 51 strict relocations. Both stripped zero-copy wrappers are also restored
in source, including the Cordio 11-byte value-buffer ownership convention.

The maintained behavior preserves three authenticated G2 differences from the
public implementation family: connection close rejects connection ID zero
before indexing the nine CCBs, HCI disconnect status is mapped through byte
base `0xA0`, and the timeout event decodes its message parameter and performs
the CCB lookup without a retained timeout state transition. Vendor logging is
not part of the functional result and is not reproduced.

`tests/test_runtime_cordio_atts_ind.py` exercises pending-slot saturation and
duplicates, setup and callbacks, all three bearers on disconnect, the invalid
connection guard, API overflow/free behavior, the authenticated timeout path,
flow control, MTU and change-awareness gates, zero-copy ownership, service-
changed confirmation, initialization, ordinary wrappers, and all 15 isolated
Cortex-M55 selectors. `tools/analyze_g2_cordio_atts_ind.py` additionally pins
the stock bodies, live interface/table roots, source hashes, overlay leaves,
strict relocations, guarded routes, component, manifest, package, and flash
plan.

The deterministic package is build-verified, not signed, installed, or
flashed. Live indication/notification timing, controller interaction, EATT
interoperability, disconnect behavior, and zero-copy buffer lifetime remain
hardware-blocked because no authorized responsive G2 pair and ATT peer capture
are available.
