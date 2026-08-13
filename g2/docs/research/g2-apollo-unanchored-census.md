# G2 Apollo unanchored-function provenance census

Status: authenticated provider-family triage map for official G2 `2.2.6.10`
Analysis mode: read-only; no signing, flashing, erase, or hardware operation

## Result

The [embedded source-path census](apollo-embedded-source-path-census.md)
leaves 5,610 of the 7,370 Ghidra-discovered Apollo-main functions without a
retained `__FILE__` anchor.  This census converts that flat remainder into
quantified provider-family buckets with explicit evidence classes and
confidence levels:

- **3,691 functions (375,900 official opaque bytes)** are assigned to a named
  provider family — 1,533 at high, 906 at medium, and 1,252 at low
  confidence.
- **8 functions** are the oversized Ghidra envelopes already rejected by the
  origin accounting's 16,384-byte trust cap; they are analyzer artifacts over
  mixed data regions, not trustworthy functions.
- **1,911 functions (299,736 official opaque bytes)** remain
  `investigation required`: 38 with mutually inconsistent call evidence and
  1,873 with no corroborating evidence.

The unanchored set and its byte total are re-derived from the authenticated
image, the 64-shard Lorelei corpus, and the checked-in manifests on every
run — nothing is hardcoded from this report.  The census reconciles exactly
with the [origin accounting](../source-coverage.md): the per-function
official-byte attribution sums to the accounting's
`unanchored_discovered_function` bucket of **675,636 bytes** with zero drift,
and the 8 rejected envelopes are the same 8 entries
(`0x0047CC60`, `0x0048949C`, `0x00509708`, `0x00513E2E`, `0x00514F3C`,
`0x00541B74`, `0x0055F994`, `0x005FA120`), whose bytes stay in the
outside-trustworthy-envelope bucket.

## Method

Evidence tiers are evaluated in strict priority order; every function gets
exactly one bucket, one evidence class, and one confidence level.

| Tier | Evidence class | Confidence | Basis |
|---|---|---|---|
| 1 | `analyzer-artifact` | high (definitional) | envelope exceeds the 16,384-byte trust cap |
| 2 | `closed-module-manifest` | high | entry named by one of the 301 ingested per-module `*-function-map.tsv` manifests (prior reviewed audits) |
| 3 | `documented-family-evidence` | high/medium | curated span or exact entry authenticated by a cited project record (nanopb runtime span, LZ4 decoder trio, exact `FT_Done_Face`, liblc3 public entry map) |
| 4 | `library-string-signature` | high | references an IAR DLIB `printf_s`/`scanf_s`/constraint-handler diagnostic string or its pointer cell |
| 5 | `call-topology-single-family` | medium | every closed-world call target (path anchor, manifest, documented, or DLIB-signature function) collapses to one provider family |
| 6 | `link-order-sandwich` | low | nearest labelled functions on both sides in address order share one family; labels propagate only from curated seeds, never from tier-5/6 assignments |
| 7 | `call-topology-mixed` | none | call targets span multiple families |
| 8 | `none` | none | no corroborating evidence |

Byte accounting mirrors the origin accounting: official bytes are counted
through the canonical flash plan's `official_blob` regions after removing the
1,592 builder-controlled patch bytes, anchored envelopes claim shared bytes
first, and the 15 known overlapping unanchored envelope pairs (all in the
early IAR-runtime island and two wrapper clusters) are attributed once in
address order.

Confidence semantics: **high** is a reviewed per-module or exact-span
classification; **medium** is a single-family structural inference; **low** is
a link-order adjacency hypothesis — useful for queue ordering, never proof of
ownership.  Buckets are provider-family triage, not per-function source
ownership, behavioral reconstruction, or candidate-readiness claims.

## Bucket census

| Bucket | Functions | Official bytes | Evidence (functions) | Ownership category |
|---|---:|---:|---|---|
| first-party (Even application/platform) | 1,782 | 216,564 | manifest 1,035; topology 96; sandwich 651 | clean-room G2 implementation target |
| LVGL 9.3.0-development vendor fork | 1,054 | 97,430 | topology 613; sandwich 441 | authenticated upstream source (vendor-fork interval) |
| littlefs v2.10.1 | 99 | 7,042 | topology 27; sandwich 72 | authenticated upstream source |
| IAR DLIB compiler runtime | 12 | 7,462 | string-signature 5; topology 6; sandwich 1 | licensed or proprietary dependency |
| Packetcraft/Ambiq Cordio | 383 | 27,356 | manifest 276; topology 52; sandwich 55 | authenticated upstream source (r20.05–r20.05c interval) |
| AmbiqSuite proprietary ports | 141 | 10,154 | manifest 134; topology 5; sandwich 2 | licensed or proprietary dependency |
| CMSIS-FreeRTOS v10.5.1 wrapper | 60 | 816 | manifest 43; topology 17 | authenticated upstream source |
| nanopb 0.4.7–0.4.9.1 runtime | 72 | 816 | documented 64; topology 8 | authenticated upstream source (compatibility interval) |
| cJSON v1.7.9–v1.7.12 | 21 | 2,572 | manifest 21 | authenticated upstream source (interval) |
| liblc3 v1.1.3-era encoder | 10 | 1,694 | documented 4; sandwich 6 | authenticated upstream source (interval) |
| LZ4 v1.10.0 decoder | 3 | 1,190 | documented 3 | authenticated upstream source (selection) |
| FreeType 2.9.1 (LVGL-bundled) | 2 | 946 | documented 1; topology 1 | authenticated upstream source (exact snapshot) |
| AmbiqSuite ANCC profile | 11 | 888 | manifest 11 | licensed or proprietary dependency |
| TLSF v3.1 | 23 | 632 | topology 12; sandwich 11 | authenticated upstream source |
| TinyFrame | 11 | 338 | topology 2; sandwich 9 | authenticated upstream source |
| EasyLogger 2.2.99-compatible | 7 | 0 | topology 3; sandwich 4 | authenticated upstream source (interval) |
| rejected oversized envelope | 8 | 0 | artifact 8 | generated or non-executable content |
| investigation required — mixed | 38 | 9,032 | mixed 38 | investigation required |
| investigation required — no evidence | 1,873 | 290,704 | none 1,873 | investigation required |
| **Total** | **5,610** | **675,636** | | |

Manifest family coverage is itself fail-closed: all 302 `*-function-map.tsv`
files are censused, the non-Apollo `g2-box` charging-case map is explicitly
skipped, every ingested stem has an explicit provider-family rule, and any
schema or count drift raises `CensusError`.

## Notable findings

1. **Most "unanchored" functions were already reviewed.** 1,520 of the 5,610
   (27.1%) are named by the existing per-module function-map manifests — the
   flat "5,610 unanchored" figure substantially overstated the unexplored
   frontier.  The genuinely unreviewed core is the 1,911-function
   investigation set.
2. **IAR DLIB formatted-I/O cluster identified.** Five unanchored functions
   reference the Annex-K diagnostic strings only IAR DLIB emits: the
   3,256-byte `printf` core at `0x00481836`, the 2,778-byte `scanf` core at
   `0x004D1638`, a 420-byte `scanf_s` helper at `0x004D2158`, the 28-byte
   constraint-handler at `0x004D40A0`, and a 466-byte wrapper at
   `0x00585410`.  With six single-family topology neighbours this extends the
   bounded IAR runtime census (previously 13 code units) with the
   printf/scanf/constraint-handler family — identification only, not yet a
   bounded source candidate.
3. **Link order alone mislabels known upstream objects.** Without the
   documented-evidence tier, the nanopb runtime (64 functions at
   `0x0048F000`–`0x00491400`), the LZ4 decoder trio, and the liblc3 public
   entries all landed in `first-party` via the sandwich tier because they are
   linked between Even objects.  The curated spans correct this; the sandwich
   tier's low-confidence label remains appropriate only where no better
   record exists.
4. **`FT_Done_Face` envelope cross-validates to the byte.** The Ghidra
   envelope for `0x00526814` is `[0x00526814,0x0052687E)` — exactly the
   106-byte span the FreeType recovery audit proved independently.  The
   surrounding 0x51/0x52xxxx sea of 342 no-evidence functions (75,016 bytes)
   is the FreeType engine frontier.
5. **LVGL dwarfs its path anchor count.** The vendor fork contributes 1,054
   unanchored functions / 97,430 official bytes against only 344
   path-anchored functions — consistent with most LVGL objects not retaining
   `__FILE__` in release paths.  Call-graph community analysis corroborates:
   the mega-component containing most no-evidence functions references LVGL
   seeds 925 times against 146 for the next family.
6. **EasyLogger's unanchored remainder is already byte-free.** All seven
   EasyLogger-family candidate envelopes have zero official bytes — the
   production overlay already source-owns every byte; the bucket exists only
   as stock-side identification.
7. **The 38 mixed-evidence functions are boundary objects**, dominated by
   `first-party|lvgl` glue (20), AmbiqSuite↔Cordio port seams (7), and
   nanopb↔schema glue (6) — precisely the adapter layers the ownership model
   expects to be mixed.

## Investigation-required frontier (1,911 functions / 299,736 bytes)

Address concentration of the 1,873 no-evidence functions:

| Region | Functions | Official bytes | Leading hypothesis |
|---|---:|---:|---|
| `0x5Dxxxx` | 300 | 52,866 | LVGL vendor-fork draw/Nema internals (largest single: `0x005D4ED0`, 7,880 B) |
| `0x52xxxx` | 255 | 38,204 | FreeType 2.9.1 engine around the proven `FT_Done_Face` anchor |
| `0x51xxxx` | 87 | 36,812 | FreeType engine / font pipeline |
| `0x5Axxxx` | 130 | 37,058 | LVGL/first-party draw pipeline |
| `0x59xxxx` | 62 | 17,874 | liblc3 encoder internals below the 4 public entries |
| `0x55xxxx` | 129 | 13,714 | TinyFrame/CLI-adjacent first-party |
| `0x44xxxx` | 153 | 6,550 | early-island runtime/startup |
| `0x4Cxxxx` | 87 | 15,584 | mid-image first-party |

Thirty no-evidence functions carry hardware hints: 22 reference peripheral
registers (`0x40000000` range — Ambiq HAL/driver candidates; largest
`0x005202EC`, 8,374 bytes) and 11 reference SRAM globals only.  Three are
linker veneers.

## Highest-value follow-up frontiers

1. **FreeType engine census** (`0x51`/`0x52xxxx`, ~342 functions, 75 KB):
   binary-match against the authenticated 2.9.1 snapshot using the
   byte-exact `FT_Done_Face` anchor and the recovered ten-module order.
2. **LVGL vendor-fork object census** for the 613 medium-confidence topology
   members and the `0x5Dxxxx` sea: compare against the authenticated LVGL
   snapshot trees and the Ambiq backend subtree.
3. **IAR DLIB formatted-I/O bounded audit**: close the printf/scanf cores,
   constraint handler, and six topology neighbours to the same standard as
   the existing 13 runtime units.
4. **liblc3 encoder internals** (`0x59xxxx`): extend the authenticated
   four-entry public map inward through `lc3_encode`'s dispatch graph.
5. **Peripheral-register cluster** (22 functions): AmbiqSuite HAL/driver
   attribution, starting with `0x005202EC` and `0x004C0F78`.
6. **Mixed-evidence boundary objects** (38): resolve the LVGL↔first-party
   and AmbiqSuite↔Cordio seams to complete provider boundaries.
7. **Oversized envelopes** (8): classify the underlying data regions
   (assets/literals) so the outside-envelope bucket shrinks deliberately.

## Reproduction

```sh
python3 tools/analyze_g2_apollo_unanchored_census.py \
  --ghidra-corpus /path/to/full64-j64-auth \
  --write-manifests tools/manifests
```

The analyzer authenticates the official image
(`36c5b0e4…78a27863`), the corpus `SHA256SUMS`
(`3ff8aa90…a0aa832f`), and the canonical flash plan
(`97230c89…1d9e`), and fails closed on any drift in the 5,610-function set,
the 675,636-byte reconciliation, the 8 oversized envelopes, the manifest
census, or the curated documented spans.

Machine-readable output:

- `tools/manifests/g2-apollo-unanchored-census-buckets.tsv` — the bucket
  table above.
- `tools/manifests/g2-apollo-unanchored-census-functions.tsv` — all 5,610
  per-function assignments (entry, body range, envelope and official bytes,
  bucket, evidence, confidence, detail).

The fail-closed guard is
[`../../tests/test_analyze_g2_apollo_unanchored_census.py`](../../tests/test_analyze_g2_apollo_unanchored_census.py):
18 tests covering rule totality, fail-closed mutation rejection, the exact
bucket census, byte reconciliation, documented-family pins, and byte-for-byte
manifest regeneration.

## Limitations

- Bucket membership is triage evidence, not source ownership, behavioral
  reconstruction, or production-candidate readiness; `low`-confidence
  sandwich labels in particular are hypotheses for queue ordering.
- Ghidra envelope shape is an analyzer artifact; official-byte attribution is
  conservative but inherits envelope boundaries.
- Functions whose bytes are fully production source-owned show zero official
  bytes yet remain in the stock-side census (EasyLogger is the extreme case).
- The 8 rejected envelopes and the 2,157,676 outside-envelope bytes are not
  per-byte classified here; data-versus-code separation of that space is a
  separate work item.
