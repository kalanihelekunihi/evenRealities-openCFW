# G2 distortion-test screen recovery

Status: complete linked-object census, clean-room C implementation, and
dual-profile production route. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`app\gui\PdtDistortionTest\pdt_distortion_test.c` owns four linked bodies and
one literal pool in `[0x005CF2B4,0x005CF634)`. The 850 body bytes have SHA-256
`adfd25e063b29828689ce9ce4eb77eef9452eb391de280a64b2dbd904df0f2d5`;
the 46-byte pool has SHA-256
`8f588fad13260784069bb2bf8a61db63461c5bf091237e5a25bb14b82990345f`.
The full 896-byte object has SHA-256
`9b2057f67369aade287e9a2e4f52a58e3862bd2b609d6dd730bc32004870e583`.

Ghidra discovered three of the bodies. The fourth is the four-byte leaf at
`0x005CF32C` (`movs r0,#1; bx lr`). It is not padding: a Thumb pointer at
`0x00793734` targets it, and the adjacent gray-screen object has an identical
leaf at the corresponding position, targeted at `0x0079373C`. The next
object starts at `0x005CF634`; its 74-byte handler/predicate prefix, retained
`PdtGrayScreen` path, and adjacent registration record independently close
the distortion object's end boundary.

The four distortion-test bodies are:

| Run interval | Bytes | Recovered role |
|---|---:|---|
| `0x005CF2B4..0x005CF2E6` | 50 | forward one object/style tuple to four LVGL style setters |
| `0x005CF2E6..0x005CF32C` | 70 | exact retained `PdtDistortionTest_common_data_handler`; log length and return zero |
| `0x005CF32C..0x005CF330` | 4 | registered predicate returning one |
| `0x005CF330..0x005CF606` | 726 | screen event handler and LVGL object-tree construction |

The object has four direct BL entry sites, all internal calls to the style
helper, and 83 direct calls across its bodies. Its external ingress is
entirely pointer-based: the registration record at `0x006A45C0` stores screen
ID `0x110`, data handler `0x005CF2E7`, UI handler `0x005CF331`, and state
address `0x20003064`; the separate table at `0x00793734` stores predicate
`0x005CF32D`. There are no direct or stored strict-interior targets and no
wide-branch entry targets.

## Behavior

The common-data handler preserves no payload data. It emits the retained
length diagnostic when logging is enabled and returns zero. The four-byte
predicate returns one for every input.

The UI handler constructs the screen only for event `2`; event `3` is
recognized but remains a no-op. Construction creates a 640 by 480 root at
`0x2007487C`, a 574 by 206 frame at `(0,50)`, and nested column/row flex
containers. It reproduces the root style group, all six distinct frame style
clears, two additional complete frame style groups, and the style group on
each flex container. The row contains the retained image asset and two
localized labels using
`ID_DASHBOARD_CALENDAR_BLUETOOTH_DISCONNECTED_1` and `_2`. The root is also
published to the registration state field at `0x20003068`. Every other event
returns zero without changing the tree.

No authenticated historical source or license is available. The clean-room MIT
implementation in `components/apollo_main/core_overlay/pdt_distortion_test.c`
replaces all 850 executable stock bytes through four guarded redirects in both
admitted compiler profiles while retaining the authenticated 46-byte literal
pool. `tools/analyze_g2_pdt_distortion_test.py` pins the official image, source
and header, four function bodies, literal pool, physical object, registration
record, retained strings and resource IDs, adjacent-object boundary evidence,
direct calls, stored entries, strict-interior absence, 86 strict relocations,
compiled leaves and routed text, component identities, manifest ownership, and
exact dual-profile routes. Live rendering remains blocked by unavailable
physical evidence: the missing evidence is an authorized G2 panel trace
confirming the recovered 640x480 root, 574x206 frame at `(0,50)`, nested flex
layout, image asset, and both localized resource labels.
