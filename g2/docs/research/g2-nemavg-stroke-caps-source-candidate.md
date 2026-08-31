# G2 NemaVG stroke-cap production source route

Status: all three authenticated stroke-cap entries are production-routed to
maintained MIT C. No stroke-cap endpoint remains retained or candidate-only.
Physical GPU qualification is blocked by unavailable physical evidence.

## Authenticated boundary

The Apollo image contains three no-argument/global-context functions:

| Entry | Stock interval | Physical bytes | Production source |
|---|---|---:|---|
| `draw_start_cap` | `0x0051B8F0...0x0051BF74` | 1,668 | `runtime_nemavg_stroke_cap_endpoints.c` |
| `draw_end_cap` | `0x0051BF7C...0x0051C5E4` | 1,640 | `runtime_nemavg_stroke_cap_endpoints.c` |
| `draw_caps` | `0x0051C5EC...0x0051D2D6` | 3,306 | `runtime_nemavg_stroke_cap_endpoints.c` |

The 6,614-byte route preserves the stock global context cell at `0x20074F04`,
the start/end style bytes at offsets `0x2E0` and `0x2E1`, the active and error
fields, the line records, stroke widths, and the no-argument entry ABI. Butt,
round, and square policies are emitted through authenticated retained NemaGFX
raster/math providers. Invalid styles return the stock `0x00800000` class.

The endpoint implementation is selector-built into three independent leaves.
The overlay applies exactly three branch patches, and each leaf's retained
provider relocations are checked against the admitted Apple and Linux
Cortex-M55 builds. The coordinator calls the two source-owned endpoint leaves
in order, short-circuits on the first nonzero result, clears the authenticated
context fields, and dispatches the retained error provider.

## Evidence

The exact public Ambiq Apollo5 Nema archive pinned by
`g2-nemagfx-ambiq-provenance.json` retains the DWARF names and declaration
lines for `draw_start_cap`, `draw_end_cap`, and the inlined `draw_caps`
coordinator. Independent stock disassembly authenticates the context offsets,
style values, endpoint symmetry, vector construction, antialias transitions,
and lower-provider call graph used by the clean-room implementation.

The admission summary reports:

- three production-routed functions / 6,614 stock bytes;
- zero unpatched endpoint functions or bytes;
- zero candidate-only stroke-cap bytes;
- Apple component SHA-256
  `898d5efb1430dc0c3e0b8b7e26823a653952114ffeab0d3ae6e89d8925301ef5`;
- Linux component SHA-256
  `45d32718d333b61718d7ebeededf4692760608af01951b98501189f5e809eccd`.

Host geometry/error tests, isolated Cortex-M55 compilation, route admission,
canonical dual-profile observations, component builds, package builds, and
flash-plan verification pass. The production source is
`components/apollo_main/core_overlay/runtime_nemavg_stroke_cap_endpoints.c`.
The earlier shared geometry candidate remains supporting test/evidence source,
not a second production owner.

## Remaining boundary

This route closes the software endpoint gap only. Remaining Nema internals,
the Ambiq bare-metal HAL promotion, live command-list behavior, antialiasing and
winding on the Apollo510 GPU, and display/power integration require an
authorized responsive G2 with traceable GPU/display evidence. That physical
qualification is blocked by unavailable physical evidence; no signing,
flashing, MMIO, or hardware operation was performed.
