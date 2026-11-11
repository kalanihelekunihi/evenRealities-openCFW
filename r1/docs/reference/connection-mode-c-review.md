# C BLE connection parameters and shared profile ownership

The existing connection unit now supplies `0x4d4ac` parameter updates, the slow
wrappers at `0x4dd78`/`0x4de44`, and the flag getter/setter at `0x4e9d0`/`0x4e9dc`.
The adjacent setter is an explicitly recorded six-byte manual supplement.
The [C event-consumer review](connection-consumer-c-review.md) now records
their integration through stock `0x45184`.

This also removes a duplicate state owner. The observer previously declared
three flag bytes at `0x200064be`, overlapping the GAP profile already owned at
`0x200064c0`. Its flag array now owns only the first two bytes. The observer's
ff-to-one profile repair, GAP initializer and both mode-one selection reads use
the existing canonical profile. The two preferred parameter records are reused;
only the slow and glasses records are added, with stock-matched bytes.

Mode selection preserves phone/glasses short circuits, setup/update error rules,
and fast-state write timing. Mode one reloads the profile after the SDK setup
and any error callback. Busy status 17 is tolerated only on the native paths;
setup ffff is logged then aborts. The wrappers cancel before scheduling the packed
`connection << 16` argument at raw delays 0/0x2800 or 0x2c00. The existing delayed
callback executes in the replay. These values are not labeled milliseconds.

The [machine-readable review](connection-mode-c-review.json) records 6,232
stock/C comparisons and thirteen rejected compiled defects. It covers every flag
byte, independent role flags, full-word mode/handle edges, SDK status rules,
provider mutations, timer callback encoding, profile sharing and control-byte
round trips. The actual SDK SVC gateways, C handle getters, connection observer,
GAP setter and delayed callback execute. The service results, logs, role query,
scheduler backend and queue encoder are models. Callee saves, stack guards and
interrupt masks are checked; incidental upper register bits above the Nordic
uint16 connection key are excluded.

The normal build still compiles 842 units (760 application, 82 bootloader), with
72 application imports and 22 bootloader linker imports. No imports are added or
removed. All 831 other prior nongenerated objects, including the GAP state/table
owner, remain identical. The observer and resized flag section are the only
changed pre-existing allocated sections of the connection unit; helper, constant
and SDK gateway sections are added. The R1 manifest check passes. The global
check still reports the pre-existing G2 `resident_rom_thumb_set.S` entry.
Final linking, runtime placement, radio timing and device boot remain unverified.
Byte identity and a paid compiler are not required.
