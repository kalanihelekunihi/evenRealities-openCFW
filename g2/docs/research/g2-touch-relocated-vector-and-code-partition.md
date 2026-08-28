# G2 touch relocation correction and code/pool partition

This device-free analysis corrects the address model used by the first shipped
prefix function map and conservatively partitions the mixed code/pool span. It
does not run firmware, access hardware, or claim recovered source.

## Relocation correction

The touch payload is linked at flash address `0x3300`. Two independent shipped
address correspondences establish the same base:

| Linked address | Payload offset | Difference | Shipped object |
|---:|---:|---:|---|
| `0xaa5c` | `0x775c` | `0x3300` | authenticated diagnostic/version string region |
| `0xb0c4` | `0x7dc4` | `0x3300` | authenticated nine-entry command jump table |

Consequently, vector words and flash pointers are absolute linked addresses,
not payload offsets. The three distinct vector targets are:

| Raw vector | Payload entry | Classification | Bounded bytes |
|---:|---:|---|---:|
| `0x465d` | `0x135c` | shared default-handler self-loop | 2 |
| `0x465f` | `0x135e` | HardFault path to the pinned halt loop | 8 |
| `0x4675` | `0x1374` | reset/startup path, bounded before the `0x13dc` literal pool | 104 |

This replaces the earlier interpretation of payload offsets `0x465c`,
`0x465e`, and `0x4674` as vector entries. Those offsets are ordinary interior
instructions reached only because the raw linked addresses had not been
rebased.

The same correction applies to references previously described as resident:

| Linked address | Shipped payload offset | Object |
|---:|---:|---|
| `0xaa5c` | `0x775c` | log string region |
| `0xb0c4` | `0x7dc4` | command dispatch table |
| `0xb0e8` | `0x7de8` | callback registry table |
| `0xb374` | `0x8074` | SCB configuration table |
| `0xb4fc` | `0x81fc` | event dispatch table |
| `0xb51c` | `0x821c` | SROM status table |

These objects are present in the authenticated payload and are not an external
resident ABI. This correction does not locate or establish the separate DFU
implementation entered after the mailbox/reset handoff; that remains
unavailable.

## Conservative discovery

Discovery begins with the 16 prior evidence entries and the three correctly
relocated vector entries. Direct in-span `BL` targets are followed to a fixed
point. PC-relative literal-load targets are then examined for odd linked flash
pointers; only pointers to an address outside an already decoded body become
additional entry seeds. A second direct-call closure produces:

| Entry origin | Functions |
|---|---:|
| Authenticated evidence | 16 |
| Relocated vectors | 3 |
| Linked flash-pointer seeds | 15 |
| Direct-`BL` closure | 252 |
| **Total** | **286** |

This is an entry/CFG candidate map, not semantic or source closure. Of the 286
entries, 223 remain semantic/source-unclassified. Ten retain evidence-backed
project source candidates. Fifty-two typed startup/upstream/EULA/fail-closed
functions are explicitly not counted as concrete project source.

## Exhaustive mixed-span partition

The `0x00c0..0x775b` mixed code/pool span contains 30,364 physical bytes. Each
byte is assigned once:

| Category | Physical bytes | Interpretation |
|---|---:|---|
| CFG instruction candidate | 26,892 | Reached from relocated vector/evidence/call/pointer seeds and not a literal target |
| CFG/literal overlap | 72 | Decoded as instructions but also directly targeted by PC-relative literal loads; intentionally ambiguous |
| Referenced literal data | 1,816 | Direct four-byte PC-relative literal targets outside CFG bytes |
| Still unclassified | 1,584 | Neither CFG-reached nor a direct literal target |
| **Total** | **30,364** | Exhaustive deduplicated partition |

The first readiness ledger reported 24,048 bytes outside its conservative map.
That exact physical set now partitions as:

| New disposition of prior remainder | Bytes |
|---|---:|
| New CFG instruction candidate | 20,580 |
| New CFG/literal overlap | 68 |
| New referenced literal data | 1,816 |
| Still unclassified | 1,584 |
| **Total** | **24,048** |

“CFG instruction candidate” is deliberately weaker than “code with source.” A
linear fallthrough can enter unreferenced embedded data when a call never
returns or when code and pools abut. The 72 directly detected conflicts are
separated, but other candidates still require boundary/semantic confirmation.
The final 1,584 bytes can mix padding, unreferenced tables, unreachable code,
and indirectly reachable functions; no behavior is invented for them.

## Source and licensing boundary

The analyzer and generated manifests are MIT-licensed. The official blob is
authenticated evidence and is not relicensed. Existing Apache-2.0, Infineon
EULA, toolchain-runtime, MIT, and MIT dispositions are carried forward
only for entries already supported by the source/provider evidence. Newly
discovered entries receive no provider or behavior name merely from their
instruction shape.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 g2/tools/analyze_g2_touch_relocated_partition.py --write-manifests --json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest g2.tests.test_analyze_g2_touch_relocated_partition
```
