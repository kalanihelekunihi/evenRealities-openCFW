# Factory sensor-stream control correlation

## Outcome

The factory command family uses one shared object at `0x2000673C` with five listener handles at
offsets `0`, `4`, `8`, `12`, and `16`. The handles bind listener name `"at"` to fixed stream names
`"hr"`, `"spo2"`, `"temp"`, `"hrv"`, and `"acc"`. Seven lifecycle functions that curated
Ghidra scripts created after the main export are now transparent, side-effect-free C plans.

| Recovered extent | Bytes | SHA-256 | Fixed operation |
| --- | ---: | --- | --- |
| `0x0004ED34..<0x0004ED52` | 30 | `299e47e0d51fd6fedaee2a7c5e0c2e6b4d7262eddb10a5e0635511f1a603a01f` | register `acc` when handle `+16` is null |
| `0x0004F2BC..<0x0004F2D2` | 22 | `605dfe1b1560a6ca231124ae45cd27e13a31d25be8a85af0d641a1b05b8ee362` | unregister `hr` when handle `+0` exists, then clear it |
| `0x0004F2DC..<0x0004F2FA` | 30 | `05ec36260c1d669678c30bc6d60eceaf43a0e73ed7d7dde85b46b08d6e1cbcbf` | register `hr` when handle `+0` is null |
| `0x0004F348..<0x0004F366` | 30 | `c60af061e20e5c01eb22278b0c19439e58e092968be37842ec835f986dd3e3e5` | register `hrv` when handle `+12` is null |
| `0x0004F8E0..<0x0004F8FE` | 30 | `bc1dadbf6af4c5dd3fde256d110bbc981b234e0f9a0f919e9f4549b1f7fcdf43` | register `spo2` when handle `+4` is null |
| `0x0004F928..<0x0004F93E` | 22 | `c422ede99f7e52be7ac38be805a2f34b7a1035c35cdad092dcee1d6bfafa1b99` | unregister `temp` when handle `+8` exists, then clear it |
| `0x0004F94C..<0x0004F96A` | 30 | `358847d2abac0e7f86ec0a828ab1b770dd9dd3b55c1a4e404b47742bec85cac8` | register `temp` when handle `+8` is null |

The already-ledgered complementary unregister functions are `0x0004ED14` (`acc`, offset 16),
`0x0004F328` (`hrv`, offset 12), and `0x0004F8BC` (`spo2`, offset 4). Together the ten functions
cover every factory listener handle in this object. Registration passes rate/mode values `1,1`
and the corresponding fixed diagnostic callback; the registration return value becomes the
handle even when it is null.

## Clean implementation and boundary

`r1_factory_stream_control_plan` is represented through seven fixed-metric public wrappers. A
register wrapper requests work only when its handle is absent. An unregister wrapper requests
work only when its handle exists; the caller can then apply the stock clear-after-unregister rule.
Tests cover both handle states, all five metrics, both operations, and null output.

The C plans do not call the sensor-stream framework, retain raw handles or callbacks, access the
stock global, emit factory text, start optical acquisition, or expose a BLE/factory command.
Actual stream registration remains an explicit caller-owned boundary.
