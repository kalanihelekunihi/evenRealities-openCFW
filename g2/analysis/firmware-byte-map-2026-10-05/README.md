# Firmware byte map — 2026-10-05, bounded refinement

Authenticated official bundle: 4,301,227 bytes, SHA-256 `f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`. All six payload hashes and outer format verify. No campaign state, firmware, staged work, reference pin, commit or hardware changed.

## Exact stored-byte classification

| Disjoint class | Bytes |
|---|---:|
| Observed original CPU instructions | 1,570 |
| Confirmed typed non-code | 151,707 |
| Metadata | 1,276 |
| Proven alignment padding | 4 |
| Unresolved, including code candidates | 4,146,670 |
| Conflicts | 0 |
| **Total** | **4,301,227** |

`summary.json` groups the four padding bytes with metadata (1,280 total). `classification-breakdown.json` splits them explicitly. Non-code is separate: 120,800 codec weights + 1,792 vector/control words + 40 BLE FHDR fields + 7 referenced version bytes + 4 checksum bytes + 28,872 L8 pixel storage + 168 image descriptor bytes + 24 constructor pointer-literal bytes.

`interval-map.jsonl` partitions the complete bundle, with half-open bundle/payload offsets, individual hashes, claims and evidence. RAM expansion, BSS and runtime-only workspace are excluded from this stored-byte partition. Accelerator command stream codec `[101776,110940)` (9,164 bytes) is code-bearing unresolved, not weights. Compressed initializers and the broad main suffix at `0x600FAA` remain unresolved.

## Fresh scan versus saved baseline

Cutoff 05:34:11 UTC, compared with the 00:13 UTC snapshot using unchanged scoped review repair and 12 regression checks:

| Comparable measure | Previous | Fresh | Change |
|---|---:|---:|---:|
| Authenticated scoped-review union | 197,000 | 197,000 | 0 |
| Receipt-pinned byte-matched JSON instructions | 273,686 | 274,662 | +976 |

Review footprint 4.58% is of stored bundle bytes, not semantic completion. Standalone ARC/app text supplements were not rescanned; 274,662 cannot be compared with the old combined 488,326 figure. New bounded execution proof described below is separate from that snapshot.

## Nonzero code lower bound

`trace_existing_angle.py` replays the existing hash-pinned angle fixture, saving only observed original PCs: **936 unique bytes, 303 instructions, 13 cases, seven body hash checks**. Host `asin` is excluded. `verify_display_family.py` adds **634 unique bytes, eight cases** from registration/header/open/copy/draw-buffer admission. Exact PCs, bytes, hashes and case associations are persisted in the two proof directories. No whole body, unexecuted branch or literal pool is counted merely because it disassembled. The replays use synthetic CPU/PCM/context state and explicitly listed stubs; they are not hardware traces.

The executable stored-byte denominator is now bounded by **[1,570, 4,148,240]**, not a measured complete code census. `code-evidence-intersections.json` intersects this selected observed set with earlier saved evidence:

| Earlier evidence intersected with observed code | Bytes | Fraction of this selected 1,570-byte set |
|---|---:|---:|
| Candidate catalogue bodies | 1,312 | 83.57% |
| Raw pseudocode bodies | 1,312 | 83.57% |
| Receipt-pinned JSON instruction exports | 48 | 3.06% |
| Authenticated scoped reviews | 34 | 2.17% |

These fractions are sample-specific representation/review footprint, **not firmware completion percentages**. New trace exports are deliberately excluded from the earlier-export numerator; counting them would trivially give 100%. No semantic completion interval is asserted.

## Six attributable display assets

Constructor `0x5BF332` loads exact descriptor pointer literals into R1 and directly calls `0x5BF2F8`, whose hash-bound body calls image setter `0x498680`. The setter uses the source classifier/info dispatch. Binary decoder registration `0x4C794C` writes header/open callback entries `0x4C79D1` and `0x4C7B25`. Original variable-source header/open paths and draw-buffer constructor validate six actual descriptors. All have L8 color 6, flags zero, stride=width, data_size=stride×height, and bounded pixel storage.

| Descriptor runtime | Geometry | Pixel payload offsets | Pixel runtime range |
|---|---|---|---|
| `0x00768374` | 34×24 | `[2535592,2536408)` | `[0x006A3088,0x006A33B8)` |
| `0x007682CC` | 68×28 | `[2398616,2400520)` | `[0x00681978,0x006820E8)` |
| `0x007682E8` | 163×52 | `[2072208,2080684)` | `[0x00631E70,0x00633F8C)` |
| `0x00768320` | 44×32 | `[2415048,2416456)` | `[0x006859A8,0x00685F28)` |
| `0x00768358` | 187×64 | `[2051408,2063376)` | `[0x0062CD30,0x0062FBF0)` |
| `0x0076833C` | 86×50 | `[2187848,2192148)` | `[0x0064E228,0x0064F2F4)` |

Header callback reads 12 descriptor bytes. Open callback reads the pixel pointer at descriptor +0x10; original `0x48B762` → `0x48AEF8` transfers dimensions, stride, size and pointer into a draw-buffer descriptor and rejects insufficient storage. The eight cases cover registration, six admissions, and a one-byte-short storage rejection using a RAM copy. The renderer does not execute or read pixels in this fixture. Global live decoder selection/startup order remains untraced. This supports a typed image-storage role, not visual fidelity or complete decoder recovery. Readable reconstructed pseudocode and layout are in `display-proof/pseudocode.md`.

Of 428 structurally valid descriptor candidates, only these six are promoted. The remaining 422 stay unresolved. 214 aligned pointer-word matches are heuristic inventory, not consumer proof. No native font or PCM/sample region is newly admitted. External font storage is not present in this bundle.

## Representative non-display placement

| Region | Payload range | Bundle range | Mapped address evidence |
|---|---|---|---|
| Codec weights | [110940,231740) | [111244,232044) | Loader-staged; no unconditional runtime/flash alias asserted |
| Touch vectors | [32,224) | [538632,538824) | Flash [0x3300,0x33C0) |
| Case core vectors | [32,96) | [573224,573288) | Flash [0x08000000,0x08000040); bank alias 0x08040000 |
| BLE FHDR fields | [1004,1044) | [327528,327568) | Target [0x302000,0x302028) |

BLE `[1044,1060)` entry bytes remain unresolved. No absent resident flash bytes are added to the denominator.

## Reproduction and review

Run from repo root with the installed environment:

```sh
~/.local/share/opencfw/venv/bin/python g2/analysis/firmware-byte-map-2026-10-05/trace_existing_angle.py
~/.local/share/opencfw/venv/bin/python g2/analysis/firmware-byte-map-2026-10-05/verify_display_family.py
python3 g2/analysis/firmware-byte-map-2026-10-05/scan.py
python3 g2/analysis/firmware-byte-map-2026-10-05/intersect_saved_evidence.py
```

Unicorn native execution requires an environment permitting its JIT; this session's restricted sandbox exited SIGILL, while approved offline execution passed. Producers emit trace SHA-256, scan verifies producer/trace/source bytes, and the angle source fixture is hash-pinned. Earlier proof/review files are not modified. Large saved scan ledgers live in `g2/build/audits/2026-10-05T0534Z-byte-map`; `audit-location.json` explains relocation of this new audit only.

Validation: three codec validators; 12 touch checks; EM parser exact round trip; case checksum; three host image round trips; 12 review fixtures; five instruction-measure fixtures; 13 angle execution cases; eight display execution cases; six payload hashes/bundle format; interval coverage and no-double-count assertions. Tests are different evidence units, not a single interchangeable count. Independent review found no coordinate/type conflicts, identified and verified the fix for trace-manifest reproducibility, and confirmed the renderer/live UI limits.

Files: `summary.json`, `classification-breakdown.json`, `interval-map.jsonl`, `display-image-candidates.json`, `code-evidence-intersections.json`, the two comparison JSONs, three initial reviewer JSONs, `independent-review.md`, the four executable analysis scripts, and `execution-proof/` / `display-proof/` evidence. Most firmware remains unresolved. The next relevant boundary is real renderer pixel access and global decoder activation; this bounded refinement stops there.
