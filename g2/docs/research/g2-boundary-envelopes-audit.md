# G2 Apollo boundary-role and oversized-envelope audit

Status: authenticated follow-up closure of census frontiers 6 and 7 for
official G2 `2.2.6.10`
Analysis mode: read-only; no signing, flashing, erase, or hardware operation

## Result

This audit closes follow-up frontiers 6 and 7 of the
[unanchored-function provenance census](g2-apollo-unanchored-census.md):

- **All 38 mixed-evidence boundary functions (9,032 official opaque bytes /
  9,380 envelope bytes)** resolve to declared boundary roles from a closed
  role table keyed by the seam family pair.  Every seam family is
  corroborated by at least one direct call edge per function, and 15 of the
  38 additionally have inbound seed-labelled caller evidence
  (medium confidence); the remaining 23 are outbound-only (low confidence).
  No function stays investigation-required.
- **All 8 rejected oversized envelopes** are partitioned byte-exactly:
  73–99% of each span is code already covered by accepted (trustworthy)
  corpus envelopes; the interstitial remainder is classified by structural
  rules.  The dominant interstitial class in seven envelopes is
  `thumb-code-candidate` (undiscovered Thumb-2 code reached through switch
  jump tables — the mechanism that produced the analyzer artifacts), and the
  eighth (`0x00513E2E`, FreeType region) is 98.7% accepted-envelope code
  with only 774 interstitial bytes.

The analyzer re-runs the unanchored census from the authenticated image
(`36c5b0e4…78a27863`), the 64-shard Lorelei corpus
(`3ff8aa90…a0aa832f`), the canonical flash plan (`97230c89…1d9e`), and the
checked-in census manifest on every run, and fails closed on any drift in
the 38-function mixed set, the 8-envelope set, the 9,380/9,032-byte
reconciliation, the seam census, the role table, or the pinned per-envelope
region partitions.

## Method — mixed-evidence boundary objects

The census assigns tier 7 (`call-topology-mixed`) when a function's
closed-world call tokens span more than one seed-labelled provider family.
This audit re-derives the census's seed labels with the census analyzer's
own helpers (path anchors, function-map manifests, curated documented
evidence, liblc3 public entries, IAR DLIB string signatures) and then, for
each of the 38 mixed functions:

1. **Span cross-check (fail closed).**  The token-derived family set must
   reproduce the census record's `call targets span …` detail exactly.
2. **Edge enumeration.**  Direct call edges are extracted from the
   decompiled corpus (`FUN_<address>(...)` call sites; data references
   without a call parenthesis are ignored).  Every spanned family must have
   at least one direct outbound call edge or the audit fails closed.
3. **Direction.**  Inbound callers that carry seed labels are counted per
   family; they establish which side of the seam drives the adaptation.
4. **Role assignment.**  The sorted seam family pair selects exactly one
   declared boundary role from a closed table; an unknown seam raises
   `BoundaryError`.  Confidence is `medium` when inbound seed-labelled
   caller evidence exists, else `low`.  Roles are boundary declarations
   (which families meet, which direction adaptation flows), not
   source-ownership claims.

### Boundary roles by seam

| Seam (families meet) | Role | Functions | Envelope bytes | Official bytes | Confidence |
|---|---|---:|---:|---:|---|
| `first-party\|lvgl` | `g2-lvgl-ui-adapter` — first-party UI adapter over the LVGL vendor fork | 20 | 6,108 | 5,966 | 8 medium, 12 low |
| `ambiqsuite\|cordio` | `ambiq-cordio-port-shim` — AmbiqSuite port shim around the Cordio host | 7 | 614 | 614 | 4 medium, 3 low |
| `first-party\|nanopb` | `g2-nanopb-schema-glue` — first-party protobuf schema glue over nanopb | 5 | 830 | 672 | 5 low |
| `first-party\|littlefs` | `g2-littlefs-volume-glue` — first-party filesystem glue over littlefs | 2 | 1,174 | 1,174 | 2 low |
| `cmsis-freertos\|first-party` | `g2-rtos-service-glue` — first-party glue over the CMSIS-FreeRTOS os2 wrapper | 2 | 104 | 56 | 1 medium, 1 low |
| `cmsis-freertos\|nanopb` | `g2-nanopb-rtos-glue` — nanopb glue adjacent to the RTOS wrapper | 1 | 286 | 286 | 1 medium |
| `cordio\|first-party` | `g2-cordio-application-callback` — application callback into the Cordio host | 1 | 264 | 264 | 1 medium |
| **Total** | | **38** | **9,380** | **9,032** | 15 medium, 23 low |

The seam census matches the census's qualitative finding 7 exactly:
LVGL↔first-party glue dominates (20), then AmbiqSuite↔Cordio port seams (7)
and nanopb↔schema glue (6 across the two nanopb seams).  The full
per-function edge map (every outbound edge with its family, inbound
seed-caller counts, adaptation flow) is
[`g2-mixed-boundary-map.tsv`](../../tools/manifests/g2-mixed-boundary-map.tsv).

### Notable per-function evidence

- **`0x004736F4` is the LVGL display-port synchronization callback.**
  The [LVGL display-port closure audit](lvgl-ambiq-display-port-closure-audit.md)
  closed this exact 142-byte function as `open_cfw_lv_display_sync`; it has
  zero official opaque bytes because the production overlay already
  source-owns every byte.  Its mixed span (calls LVGL display-lock entries
  and the first-party `0x00474066`) is the expected signature of a port
  adapter, and it is registered by stored pointer rather than called — hence
  no inbound seed caller (low confidence, but independently closed).
- **Three mixed functions are already fully source-owned** in production
  (`0x004736F4`, `0x0047DCB4`, `0x0055E7FA`; 348 envelope bytes, 0 official
  bytes), mirroring the EasyLogger pattern from the census: the bucket
  records stock-side topology, not a source gap.
- **AmbiqSuite↔Cordio direction is bidirectional.**  `0x00536426`,
  `0x0053673E`, and `0x00536774` are called *by* Cordio seed functions and
  call both Cordio and AmbiqSuite — Cordio-invoked port callbacks.
  `0x00503C32` is called by a first-party seed function — application-initiated
  use of the port layer.
- **`0x004B42F0`** is called by an AmbiqSuite seed function and calls three
  Cordio entries plus first-party code — an application callback reached
  from the port layer, hence the `g2-cordio-application-callback` role.
- Edges into the rejected oversized envelopes (for example
  `first-party:0x0048949C`) reference those envelopes' reviewed function-map
  manifest labels, exactly as the census's seed-label model defines; the
  envelope rejection does not invalidate the manifest label at its entry.

## Method — oversized-envelope region classification

Each rejected envelope span `[body_start, body_end)` is partitioned
byte-exactly; every span byte gets exactly one class:

1. `accepted-function-code` — bytes covered by any of the 7,362 accepted
   corpus envelopes (overlaps attributed once, in address order).
2. The interstitial remainder is split into maximal gap segments; inside
   each segment, maximal runs of ≥3 consecutive 4-byte-aligned pointer words
   (image, image|Thumb-bit, SRAM `0x20000000`–`0x2007FFFF`, or peripheral
   `0x40000000`–`0x5FFFFFFF`) are carved as `thumb-jump-table` (majority odd
   words) or `pointer-table`.
3. Each remaining piece is classified:
   `alignment-gap` (<16 bytes), `zero-fill` (≥90% NUL), `ascii-strings`
   (≥80% printable), `thumb-code-candidate` (Thumb-2 `BL` instructions with
   sign-extended in-image targets at ≥4/KB; high confidence at ≥10/KB and
   ≥256 bytes), `mixed-code-data` (some in-image `BL` evidence below the
   code threshold), `opaque-blob` (≥128 distinct byte values, no `BL`
   evidence), else `rodata-table` (low confidence).

The `BL`-topology discriminator was calibrated on known accepted envelopes
(≥9.7 validated `BL`s per KB, including literal-pool-heavy cores) against
the asset tail beyond the last discovered function (≤0.5/KB).  Carved jump
tables were spot-verified as switch tables (odd Thumb targets into nearby
code, for example `0x00570120`) and IAR/peripheral pointer tables (for
example `0x004806F8`).

### Per-envelope composition

| Entry | Span bytes | Accepted code | Interstitial | Dominant interstitial class | Confidence |
|---|---:|---:|---:|---|---|
| `0x005FA120` | 1,802,238 | 1,322,324 (73%) | 479,914 | `thumb-code-candidate` (366,436) | high |
| `0x0047CC60` | 352,058 | 264,458 (75%) | 87,600 | `thumb-code-candidate` (65,788) | high |
| `0x0048949C` | 311,538 | 230,772 (74%) | 80,766 | `thumb-code-candidate` (60,796) | high |
| `0x00509708` | 348,926 | 262,730 (75%) | 86,196 | `thumb-code-candidate` (67,198) | high |
| `0x00513E2E` | 60,220 | 59,446 (99%) | 774 | `rodata-table` (512) | low |
| `0x00514F3C` | 322,072 | 238,236 (74%) | 83,836 | `thumb-code-candidate` (62,578) | high |
| `0x00541B74` | 275,900 | 179,648 (65%) | 96,252 | `thumb-code-candidate` (72,410) | high |
| `0x0055F994` | 192,814 | 135,916 (70%) | 56,898 | `thumb-code-candidate` (38,394) | high |

Full per-class byte maps are in
[`g2-oversized-envelope-regions.tsv`](../../tools/manifests/g2-oversized-envelope-regions.tsv).
The spans overlap heavily and the `0x005FA120` span alone covers the union
`[0x00442134,0x005FA132)`, so per-envelope rows are independent views, not
additive.  The union partition (equal to the `0x005FA120` row) is:
accepted-function-code 1,322,324; thumb-code-candidate 366,436 (303,858
high / 62,578 medium confidence); pointer-table 83,428; rodata-table 11,966;
mixed-code-data 8,466; alignment-gap 7,370; thumb-jump-table 2,052;
ascii-strings 196.

### Interpretation

- **The artifacts are switch-table code+data mixtures.**  The interstitial
  code carries dense in-image `BL` topology but has no direct caller
  anywhere in the decompiled corpus; the only structured references into it
  are function pointers and switch jump tables.  The 92 carved
  `thumb-jump-table` runs (2,052 bytes, 254 case targets) point 65% into
  accepted envelopes and 35% into interstitial code: switch tables whose
  targets Ghidra only partially discovered, which is how the surrounding
  code+table mixtures got glued into mega-envelopes the trust cap correctly
  rejected.  The 1,659 carved even-pointer table runs point overwhelmingly
  (99.8%) outside every accepted envelope — data and asset references, not
  code.
- **The outside-envelope bucket shrinks deliberately.**  479,914 of the
  origin accounting's 2,157,676 outside-trustworthy-envelope bytes are the
  interstitial bytes classified here: ~76% structurally code-evident
  (`thumb-code-candidate`), ~18% pointer/jump tables, ~2.5% rodata tables,
  ~2% mixed code+data, the rest strings and alignment gaps.  The remaining
  ~1.68 MB stays unclassified by this audit and is dominated by the asset
  tail beyond the last discovered function (`0x005FA132`); per-byte work
  there is a separate item.
- **`0x00513E2E` is effectively closed.**  98.7% of its span is
  accepted-envelope code in the FreeType `0x51xxxx` frontier; its 774
  interstitial bytes are small rodata tables and gaps.
- **`0x005FA120` is a degenerate envelope**: its entry sits near the end of
  its own body, which begins at `0x00442134` and swallows the entire image
  head — definitional proof the envelope is an analyzer artifact, not a
  function.

## Reproduction

```sh
python3 tools/analyze_g2_boundary_envelopes.py \
  --ghidra-corpus /path/to/full64-j64-auth \
  --write-manifests tools/manifests
```

The fail-closed guard is
[`../../tests/test_analyze_g2_boundary_envelopes.py`](../../tests/test_analyze_g2_boundary_envelopes.py):
corpus-independent tests cover role-table totality, classifier rules on
synthetic buffers, and validator mutation rejection; the corpus-backed tests
pin the exact 38-function/9,032-byte reconciliation, the seam census, the
per-envelope region partitions, byte-exact partition totality, and
byte-for-byte manifest regeneration.

## Limitations

- Boundary roles are declared adapter roles from closed-world call
  topology, not source ownership, behavioral reconstruction, or
  production-candidate readiness; `low`-confidence rows lack inbound
  seed-labelled callers and rest on outbound edges alone.
- Inbound direction uses only seed-labelled callers; unlabeled callers
  (mostly the no-evidence sea) stay unclaimed, so some `low` rows are
  likely registered callbacks whose registration is data-side.
- `thumb-code-candidate` is structural code evidence, not a discovered
  function set; those bytes remain outside the trustworthy-envelope corpus
  until a per-function discovery pass proves them.
- `BL`-free code (leaf functions, functions reached only via jump tables
  that make no direct calls) lands in the data classes; `rodata-table` in
  particular is low confidence by construction and may contain
  unreached-code fragments.
- Region classes describe span bytes, not official opaque bytes; patch-site
  and source-owned attribution remains the origin accounting's model.
- The eight envelope spans overlap; only the union partition is a
  disjoint coverage statement.
