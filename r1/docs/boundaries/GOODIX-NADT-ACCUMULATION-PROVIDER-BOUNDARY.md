# Goodix GH_NADT accumulation/decision provider boundary

## Decision

Thirty formerly unclassified functions / 5,126 executable bytes form the remaining closed private
helper graph beneath the already pinned Goodix `GH_NADT_pre` root at `0x0006E838`. They are routed
to `goodix_gh3x2x_candidate` with disposition `vendor_source_required_not_redistributable` and
must not be reconstructed as local OpenR1 code.

The closure includes the former largest unresolved function at `0x00072DCC` / 490 bytes. It also
includes seven other direct root descendants and all of their formerly unclassified descendants,
covering batch accumulation, intermediate reduction, threshold/decision, and output preparation.
Those descriptions are ownership labels only, not private Goodix symbol claims or a clean-room
algorithm specification.

## Exact call-graph boundary

The new direct entry callsites in `0x0006E838` are `0x0006E892`, `0x0006E8A8`, `0x0006E8C0`,
`0x0006E908`, `0x0006E926`, `0x0006E996`, `0x0006EA56`, `0x0006EAA8`, and `0x0006EAD8` (the two
last-mentioned calls to one shared helper account for eight direct descendants). Every direct
caller of the 30 functions is either inside this closure or already Goodix-gated. There are zero outside non-Goodix callers.

Two compiler-shaped functions have noncontiguous executable extents:

| Entry | Ghidra bytes | Exact executable segments |
| --- | ---: | --- |
| `0x0002FEE2` | 114 | `0x0002FEE2..<0x0002FF0E`, `0x0002F2AC..<0x0002F2F2` |
| `0x00066458` | 52 | `0x00066458..<0x00066470`, `0x0009293E..<0x0009295A` |

The other 28 entries use their contiguous Ghidra extents. The static summarizer pins all 30 body
SHA-256 values, both composite segment maps, and every direct callsite. The provider identity
remains `GH_NADT_pre v1.0.2.0 / 548d894d`.

## Provider rule

Use a matching, lawfully licensed Goodix GH3X2X SDK with recorded version, hashes, ABI, license,
and redistribution terms. Sensor-algorithm heap operations and Arm/toolchain runtime helpers are
separately source-routed and excluded from this census. OpenR1 may retain R1-owned transport and
lifecycle adapters, but it may not reproduce this signal-processing closure, its constants, or
its formulas.

```sh
python3 tools/summarize_r1_goodix_nadt_accumulation.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
