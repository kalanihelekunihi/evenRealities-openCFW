# Goodix GH_NADT accumulation/decision provider boundary

## Decision

Thirty formerly unclassified functions / 5,126 executable bytes formed the original pinned
boundary beneath the already pinned Goodix `GH_NADT_pre` root at `0x0006E838`. Under the subsequent
owner-authorized clean-room reduction, all 30 entries / 5,126 bytes now compile as transparent C.
The last admitted batch is `0x00036974`, `0x00044A78`, `0x00072DCC`, `0x00076A68`, and
`0x00077D2C`. No function in this historical boundary remains provider-gated.
The boundary's former disposition was `vendor_source_required_not_redistributable`.

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

This historical boundary no longer requires a Goodix binary provider. Sensor-algorithm heap
operations and Arm/toolchain runtime helpers are separately source-routed and excluded from this
census. The admitted entries use only the SHA-pinned owner-authorized reconstruction documented
in `GOODIX-PRIMITIVES-REDUCTION-CORRELATION.md`; no bytes or absolute pointers from the stock image
are linked into the bundle.

```sh
python3 tools/evidence/summarize_r1_goodix_nadt_accumulation.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
