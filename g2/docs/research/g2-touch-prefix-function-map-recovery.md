# G2 touch-controller shipped-prefix function map

Status: deterministic software-only recovery tranche complete. This document
does not claim hardware validation or complete resident firmware recovery.

## Scope and identity

The mapped input is the authenticated G2 2.2.6.10 touch FWPK record:

- blob SHA-256: `0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d`;
- type-3 payload: `[0x0000,0x8680)`;
- Thumb code plus literal pools: `[0x00C0,0x775C)`;
- unavailable resident flash ABI: `[0x8680,0x10000)`.

The analyzer first runs the existing identity and I2C-protocol audits and then
authenticates the sensing loop `[0x36C4,0x376C)`. A byte change fails before a
map or manifest is written.

## Conservative discovery rule

`tools/analyze_g2_touch_prefix_function_map.py` starts from two evidence
classes only:

1. nonzero in-prefix vector targets; and
2. function entries already established by the identity, I2C, and sensing
   work, including the I2C callback alternate entry and exact FIFO/power
   helpers.

It walks ARMv6-M control flow, records calls without treating them as ordinary
fallthrough, adds direct in-prefix `BL` destinations to a fixed point, and then
recomputes every function with the final entry set. Direct branches into a
different known entry become tail-entry boundaries. Indirect call sites remain
explicitly unresolved.

The raw halfword `BL` census is not used to seed functions. Thumb literal pools
can accidentally resemble valid call encodings, so promoting all 278 raw
targets would overstate the evidence. This tranche therefore prefers a smaller
reproducible map over a speculative whole-span disassembly.

Aggregate audit spans and dispatcher labels are kept distinct from functions.
For example, `[0x0660,0x0780)` authenticates the EEPROM module but begins in a
literal pool, and `0x0446` through `0x054C` are executable command-case entries
inside the `0x0400` IRQ dispatcher. None are emitted as false standalone
functions.

## Result

The evidence/direct-call closure contains:

- 63 callable entries;
- 16 behavior-named evidence entries;
- 3 vector-seeded entries whose exact semantic roles remain unresolved;
- 44 direct-call-reachable helpers with unresolved semantic/source identity;
- 3,171 instruction instances and 6,620 per-function instruction bytes;
- 6,316 unique shipped-prefix instruction bytes;
- 162 unique bytes shared by two or three alternate/shared-tail entries;
- 9 indirect call sites and no unresolved indirect jump exits.

Coverage uses deduplicated instruction addresses. The three vector targets at
`0x465C`, `0x465E`, and `0x4674` converge on the same recovered suffix, so their
per-entry sizes must not be summed as physical coverage. The exact deterministic
row digest is
`335e09b1d61057a49e69d4f58f9e9117f4e8db4f475068f76ba3f544919a5e7a`.

Exact evidence-backed function spans include:

| Entry | Name | Reachable instruction span/bytes |
|---:|---|---:|
| `0x02F4` | `sensor_read_mux` | `[0x02F4,0x031A)`, 38 B |
| `0x0378` | `i2c_slave_init` | `[0x0378,0x03DA)`, 98 B |
| `0x0824` | `report_builder` | `[0x0824,0x0960)`, 316 B |
| `0x0BE0` | `logger_stub` | `[0x0BE0,0x0BE8)`, 8 B |
| `0x36C4` | `msc_sensing_loop` | `[0x36C4,0x376C)`, 168 B |
| `0x4B14` | `NVIC_SystemReset` | `[0x4B14,0x4B26)`, 18 B |
| `0x67D8` | `i2c_tx_descriptor_arm` | `[0x67D8,0x67F0)`, 24 B |
| `0x67F0` | `i2c_rx_descriptor_arm` | `[0x67F0,0x6806)`, 22 B |
| `0x6806` | `i2c_rx_position_get` | `[0x6806,0x680A)`, 4 B |

The full non-contiguous span and instruction digest for every entry is in
`tools/manifests/g2-touch-prefix-function-map.tsv`.

## Resident and DFU boundary

No address at or above `0x8680` is a function row. Exact payload references to
resident switch/HAL tables (`0xB0C4`, `0xB4FC`, `0xB51C`, `0xB374`, and
`0xB0E8`, plus dead logger strings) are recorded only as
`external_unavailable_abi`. The shipped `0x4B30` handoff writes the mailbox and
resets; the resident DFU engine's exact entry and tables are unavailable and no
address is invented for them.

This boundary means the prefix map can support clean-room interface planning,
but cannot establish a complete standalone controller image until the resident
ABI is either independently specified or replaced.

## Artifacts and verification

- `tools/analyze_g2_touch_prefix_function_map.py` — MIT-licensed analyzer;
- `tools/manifests/g2-touch-prefix-function-map.tsv` — per-entry CFG spans;
- `tools/manifests/g2-touch-prefix-evidence-anchors.tsv` — authenticated
  aggregate spans and non-function case entries;
- `tools/manifests/g2-touch-prefix-external-abi.tsv` — resident dependency
  boundary;
- `tools/manifests/g2-touch-prefix-function-map-summary.json` — pinned metrics,
  limitations, licensing, and ABI summary;
- `tests/test_analyze_g2_touch_prefix_function_map.py` — deterministic,
  tamper-fail, shared-tail, anchor, and resident-exclusion tests.

Run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 \
  g2/tools/analyze_g2_touch_prefix_function_map.py --write-manifests
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  g2/tests/test_analyze_g2_touch_prefix_function_map.py -v
```

The analyzer and generated analytical manifests are MIT licensed. The official
blob is provenance evidence and is not relicensed. This map does not infer a
historical license for any recovered function; future clean-room replacements
must retain identified upstream provider licenses where applicable.

No device access, reset, DFU, flash, signing, timing measurement, or electrical
test is performed, and no physical suitability claim is made.
