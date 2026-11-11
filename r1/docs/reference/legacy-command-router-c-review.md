# BLE and factory legacy command routers in C, 2026-11-11

Stock `0x4e258..0x4e427` clears the fixed 36-byte scratch at `0x2001a174`,
copies the caller's full length into it, dispatches on byte 2, and returns
`0xffffffff` for unknown commands. Known commands return zero after ignoring
the child return. The special `0x88` command logs the pair-authentication
message and sends BLE event 2 with a one-byte payload of 2. The C owner is
`r1/src/application/board/native_legacy_command_router.c`; the receive task
now declares its actual return type.

Stock `0x625c0..0x627cd` is the factory record router. It uses the same
scratch and 22-child command map. Its ordinary child branches return the
child's result; unknown commands return their command byte. Command `0x88`
returns the BLE encode result. Its extra `0x8b` command writes the low byte
of the charge state and a zero byte, then sends a six-byte legacy reply.
The factory task now declares this return type accurately.

The stock switch maps 22 command bytes to child functions: `0x11`, `0x12`,
`0x21`–`0x24`, `0x34`, `0x37`, `0x40`, `0x52`–`0x57`, `0x85`, `0x89`, `0x8a`,
`0x91`, `0x94`, `0x95`, and `0xf2`. The separate `0x88` branch is counted
apart from those child calls. The ignored
`build/r1-legacy-router-c-20261111/probe.c` checks all 256 command bytes
for each router,
the copy and zeroed tail, the 64-byte stock copy span, both logging sinks,
the event payload, the factory child-return behavior, and the charge reply
under sanitizers. All cases pass.

`build/sources-r1-f2-dispatch-c-20261111/report.json` records 938/938
application and 82/82 bootloader units compiled, with no known failures or
duplicate strong symbols. The strict bootloader link passes. The strict
application receipt at `build/r1-link-f2-dispatch-c-20261111/report.json`
resolves both router roots and all their child imports. It reports 13
undefined references elsewhere in the application, 644,016 of 696,320 flash
bytes used, and no flash overflow. The 72-slot subdispatch table has 15
stock-initialized callbacks, now implemented in the
[0xf2 dispatch](legacy-f2-dispatch-c-review.md).

Both C routes remain unverified on physical R1 hardware and have not been
shown byte-identical to the locked image.
