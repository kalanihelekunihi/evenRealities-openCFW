# Hardware C provider qualification

Four existing C wrappers in `r1/src/application/board/native_peripheral_line_power.c` now enter the canonical exact-build plan. Each complete six-byte function matches its locked stock span after linking with the frontier's native Thumb target:

| Function | Stock entry | Operation |
| --- | --- | --- |
| `r1_goodix_transport_release` | `0x5036c` | Release line selector 0 |
| `r1_goodix_transport_prepare` | `0x50372` | Acquire line selector 0 |
| `r1_touch_bus_enable_on` | `0x50378` | Release line selector 1 |
| `r1_touch_bus_acquire_on` | `0x5037e` | Acquire line selector 1 |

The historical touch labels do not describe the actual operation; the table follows the linked release/acquire targets. No firmware C, manifest unit, inline assembly or stock reference changed. Only the official qualifier's newly selected regions were added to `tools/build/source-plan.json`, with overlap checks against every existing region. The release/acquire provider bodies themselves do not receive new qualification credit.

The sweep covers 78 anchored board/software-TWI/Goodix units whose source files contain no explicit assembly. Clang's recorded/O2/Os/Og profiles compile all 312 candidates and select nine regions, all already covered. Converting 77 Clang units to GCC9 initially compiles 242 of 308 candidates and selects eight regions, including these four new wrappers. One native GCC unit is not a converted Clang candidate. Recorded flags can include a GCC9-unsupported optimization; compilation failures remain explicit.

That conversion exposed a generated-input mount omission. The R1 GCC profile now mounts `build/generated/r1` read-only, matching the generated forced-header inputs. The rerun compiles 250 of 308 candidates: eight recovered compilations, all 242 previously compiled objects byte unchanged, and unchanged selected regions. No missing generated-header errors remain. The 58 remaining failures include Clang-only musttail syntax, GCC warnings promoted to errors in SDK/board code, and unsupported recorded optimization flags; they are not successful validations. See the detailed qualification report and mount audit in the receipt.

The canonical rebuild at `build/hybrid-goal-r1-hardware-c-canonical` reconstructs the locked 646,408-byte application with SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`. It contains 3,905 source-built bytes, 642,255 stock fallback bytes and 248 resource bytes. This adds 24 C executable bytes; it does not establish a complete C firmware build or physical power-control behavior. The normal source build remains the 575-unit flash-write-frame report with unresolved imports 175/34; no firmware source changed during this sweep. G2 gates remain unchanged.

[Machine-readable evidence and hashes](hardware-c-qualification-review.json). Probes and candidate reports live under ignored `build/goal-r1-hardware-c-qualification/`. Existing bounded policy evidence is [peripheral-line-c-power-review.md](peripheral-line-c-power-review.md).
