# G2 FreeType engine census — 0x51xxxx/0x52xxxx frontier

Status: authenticated module-attribution triage for official G2 `2.2.6.10`
Analysis mode: read-only; no signing, flashing, erase, or hardware operation

## Result

This census closes follow-up frontier 1 of the
[unanchored-function provenance census](g2-apollo-unanchored-census.md): the
342 no-evidence functions (75,016 official opaque bytes) in the
`0x51xxxx`/`0x52xxxx` regions hypothesized as the FreeType 2.9.1 engine,
plus the 2 functions (946 bytes) the parent census already bucketed as
FreeType — the byte-exact `FT_Done_Face` envelope at `0x00526814` and its
call-topology neighbour.  Scope is exactly **344 functions / 75,962 official
bytes**.

- **83 functions (7,874 official bytes)** attribute to the FreeType 2.9.1
  **base** module (`src/base`: ftobjs.c / ftinit.c / ftutil.c / ftpsprop.c
  code): 10 at high, 17 at medium, 56 at low confidence.
- **261 functions (68,088 official bytes)** remain `investigation-required`
  with deterministic per-function hypotheses.  No in-scope function carries
  evidence for any other FreeType module: the evidenced FreeType code in
  this frontier is exactly the base-module cluster at
  `0x005242FC`–`0x005293C2`; **no `0x51xxxx` function attributes at all**.

The analyzer re-runs the parent census from the authenticated image
(`36c5b0e4…78a27863`), the 64-shard Lorelei corpus
(`3ff8aa90…a0aa832f`), the canonical flash plan, the checked-in manifests,
and the hash-verified VER-2-9-1 snapshot on every run, and fails closed on
any drift in the 342/75,016 frontier, the 2/946 bucket, the anchor set, the
string/table censuses, the closure inputs, or the pinned 83-row attribution
map.

## Method

Evidence tiers in strict priority order; every in-scope function gets
exactly one status, module, evidence class, and confidence level.

| Tier | Evidence class | Confidence | Basis |
|---|---|---|---|
| 1 | `documented-api-anchor` | high | entry named by address in the reviewed [recovery audit](freetype-recovery-audit.md); re-verified structurally (exact body span for `FT_Done_Face`, pinned interior sites for `FT_Open_Face`/`FT_New_Library`, exact callee sets for `FT_Init_FreeType`/`FT_Add_Default_Modules`, caller pins for `FT_Add_Module`/`destroy_face`) |
| 2 | `documented-interior-pin` | high | `open_face` (static, ftobjs.c): body contains the audit-pinned face-internal `0x44`-byte allocation at `0x00525A0C` and references the `incr` tag literal cell `0x005262A8`, whose image word is re-read as `0x696E6372` |
| 3 | `ps-property-string-signature` | high | function references the pointer cells of exactly the property-name set parsed from the hash-verified snapshot `ftpsprop.c`: four names for `ps_property_set`, three for `ps_property_get` |
| 4 | `base-call-graph-direct` | medium | member of the closed static call-graph community grown from the tier-1/2/3 anchors, with a direct static edge to an anchor and all outbound targets inside the community or the 14-entry external allowlist |
| 5 | `base-call-graph-indirect` | low | remaining community members, reachable only through other members or neutral leaf/runtime-passthrough helpers |
| 6 | `none` | none | no admissible FreeType evidence; deterministic hypothesis recorded |

The community closure (tiers 4/5) admits an outbound static call target only
when it is already in the community, is one of **14 curated externals** (the
three documented vendor ftsystem functions `FT_Stream_Open`/`FT_New_Memory`/
`FT_Done_Memory`, plus eleven body-verified C runtime routines:
memcpy/memmove/memset/strlen/strcmp/strncpy/strstr/memcmp/strchr and two
tails), or bottoms out in allowlisted/leaf functions within one further hop
(neutral passthrough).  The rule is deliberately conservative: the
vendor-grafted fallback loader called directly by `FT_Open_Face`
(`0x00526452` subtree) does **not** satisfy it, because its callees reach
non-community, non-runtime code (the vendor resource-container reader).

Corroborating, non-attributing pins:

- Eight flat constant tables parse from the hash-verified snapshot sources
  `cffload.c`, `t1decode.c`, `psmodule.c`; exactly seven byte-match
  uniquely in the official image (`cff_expert_encoding` 0x006C0150,
  `cff_isoadobe_charset` 0x006C1C60, `cff_expert_charset` 0x006C93B0,
  `cff_expertsubset_charset` 0x006D22FC, `t1_args_count` 0x006D7C60,
  `ft_extra_glyph_unicodes` 0x0074D214, `ft_extra_glyph_name_offsets`
  0x0074D23C), and **no in-scope function references any of them**.  The
  CFF/psaux/psnames constant data is linked but its code lives outside this
  frontier — consistent with the config audit's CFF initializer at
  `0x005B004A`, smooth renderer at `0x005E22E0`, and `tt_driver_init` at
  `0x005F903C`.  The authenticated ten-entry `ft_default_modules[]` table
  already proves those modules are in the build; this census only bounds
  *where*.

## Bucket table

| Status / evidence | Module | Functions | Official bytes | Meaning |
|---|---|---:|---:|---|
| `documented-api-anchor` | base | 7 | 1,518 | `FT_Init_FreeType`, `FT_Add_Default_Modules`, `FT_Add_Module`, `FT_New_Library`, `destroy_face`, `FT_Open_Face`, `FT_Done_Face` |
| `documented-interior-pin` | base | 1 | 288 | `open_face` (static, ftobjs.c) |
| `ps-property-string-signature` | base | 2 | 346 | `ps_property_set`, `ps_property_get` (ftpsprop.c) |
| `base-call-graph-direct` | base | 17 | 1,294 | direct anchor neighbours; includes the `FT_List_Find`/`Add`/`Remove`/`Finalize` and `ft_mem_alloc`/`ft_mem_free` body-shape hypotheses |
| `base-call-graph-indirect` | base | 56 | 4,428 | wider ftobjs/ftutil community |
| `investigation-required` | — | 261 | 68,088 | no admissible FreeType evidence |
| **Total attributed** | base | **83** | **7,874** | |

## Reconciliation against the parent census

| Quantity | Parent figure | This census |
|---|---:|---:|
| `0x51xxxx` no-evidence | 87 / 36,812 B | 87 / 36,812 B (0 attributed) |
| `0x52xxxx` no-evidence | 255 / 38,204 B | 255 / 38,204 B (81 attributed) |
| freetype bucket | 2 / 946 B | 2 / 946 B (both re-attributed at high) |
| **Scope** | **344 / 75,962 B** | 344 / 75,962 B |
| Attributed | — | 83 / 7,874 B |
| Investigation-required | — | 261 / 68,088 B |

Attributed + investigation-required = 75,016 + 946 = 75,962 official bytes,
zero drift.  The parent's freetype-bucket member `0x005264A6` is confirmed
by an independent tier: its body contains both audit-pinned `FT_Open_Face`
cleanup call sites (`0x0052659C`, `0x005267D0`).

**Oversized-envelope reconciliation.** The two rejected envelopes whose
entries sit in these regions (`0x00513E2E`, `0x00514F3C`) are never in
scope — the parent census rejects them by the 16,384-byte trust cap, and
this analyzer fails closed if either leaks in.  The
[boundary-envelopes audit](g2-boundary-envelopes-audit.md) found the
`0x00513E2E` span to be 98.7% accepted-envelope code with only 774
interstitial bytes (small rodata tables and gaps).  That is consistent with
this census: the accepted code inside the span *is* this frontier's
discovered functions (the span covers most of the `0x51xxxx` region), and
the 774 interstitial bytes are data the per-function corpus never claimed.
Nothing in either rejected envelope is attributed here.

## Notable findings

1. **Only the base module is evidenced in this frontier.**  All 83
   attributions are `src/base` code.  The driver/renderer modules the G2
   build links (autofit, truetype, cff, psaux, psnames, pshinter, sfnt,
   smooth ×3 — per the authenticated module table) live outside the
   `0x51`/`0x52xxxx` regions; the seven byte-matched snapshot tables pin
   CFF/psaux/psnames *data* in the image with zero in-scope references.
2. **The `ps_property` get/set asymmetry matches 2.9.1 to the name.**
   `0x00527F0A` references all four `ps_property_set` names
   (`darkening-parameters`, `hinting-engine`, `no-stem-darkening`,
   `random-seed`); `0x00527FF2` references exactly the three
   `ps_property_get` names — `random-seed` is set-only in the vendored
   `ftpsprop.c`.  Both sets are re-parsed from the hash-verified snapshot
   on every run.
3. **The vendor graft is visible and deliberately unattributed.**
   `FT_Open_Face` statically calls `0x00526452`, a 9-slot font-fallback
   loader that parses `0x80`-aligned resource-container headers — an Even
   extension of the stock open path.  It and its subtree (`0x005262AC`,
   `0x005261AC`, `0x00526356`, `0x00525E16`, `0x005260A4`, …) fail the
   closed community rule and stay investigation-required.  `FT_Stream_New`
   at `0x00524F96` (body dispatches `FT_OPEN_MEMORY`/`FT_OPEN_PATHNAME`/
   `FT_OPEN_STREAM`) was bucketed `lvgl` by the parent's topology tier; it
   is recorded here as an out-of-scope observation (medium), never
   re-bucketed.
4. **The `0x51xxxx` region is not FreeType.**  Its 87 functions are
   dominated by LVGL-adjacent draw helpers (11 call the lvgl-bucketed
   `0x004B127C` cluster) and the 8,374-byte peripheral-register function
   `0x005202EC`, which calls the rejected `0x00513E2E` envelope — a
   display/graphics-driver candidate, consistent with the parent census's
   hardware-hint list.
5. **A FreeType glyph-API cluster is visible but unprovable.**
   `0x00524606`, `0x005246F8`, `0x00524754`, `0x00525574` are heavily
   called from the LVGL wrapper (`lv_freetype_font_create` at `0x004B1C9C`)
   and the `0x56`/`0x5A`/`0x5D`/`0x5E`/`0x5F` driver regions — the expected
   signature of `FT_Set_Pixel_Sizes`/`FT_Load_Glyph`-family APIs — but they
   carry no distinctive constant, string, or table evidence, so they stay
   investigation-required rather than being named.

## Investigation-required remainder (261 functions / 68,088 bytes)

Leading hypotheses, all recorded per function in the manifest:

- `0x51xxxx` LVGL/first-party draw pipeline (87 / 36,812 B; largest
  `0x005202EC`, 8,374 B, peripheral-register + rejected-envelope caller).
- `0x52A63C`–`0x52B97C` first-party UI/widget clusters (called from dozens
  of `0x4B`/`0x53`/`0x56` first-party functions).
- `0x52DC24`–`0x52F38C` first-party cluster adjacent to nanopb-labelled
  functions.
- FreeType-adjacent internals lacking distinctive evidence: the glyph-API
  cluster above, the `0x00528DB8`–`0x0052910E` utility cluster (ftcalc-like;
  called from the `0x568xxx` region), and the `0x005295A8`/`0x00529936`/
  `0x00529F8E` pointer-dispatched functions that call into the base
  community from above (candidate class-record service routines).

## Reproduction

```sh
python3 tools/analyze_g2_freetype_engine_census.py \
  --ghidra-corpus /path/to/full64-j64-auth \
  --write-manifests tools/manifests
```

Machine-readable output:

- `tools/manifests/g2-freetype-engine-census.tsv` — all 344 per-function
  rows (entry, body range, envelope and official bytes, scope, parent
  bucket, status, module, attribution, evidence, confidence, detail).
- `tools/manifests/g2-freetype-engine-census-summary.json` — inputs,
  reconciliation, module summary, external observations, limitations.

The fail-closed guard is
[`../../tests/test_analyze_g2_freetype_engine_census.py`](../../tests/test_analyze_g2_freetype_engine_census.py):
28 tests covering rule totality, anchor/allowlist/table pin well-formedness,
closure-rule behaviour on synthetic graphs, parser behaviour on synthetic
sources, exact census counts, the pinned 83-row attribution, mutation
rejection (attribution map, anchors, property sets, located tables,
allowlist), and byte-for-byte manifest regeneration.

## Limitations

- Attribution is evidence-tiered triage, not per-function source ownership,
  behavioral reconstruction, or production-candidate readiness; the
  `base-call-graph-indirect` tier in particular is community-topology
  membership only.
- Community members include shared utility functions also called by other
  modules' code outside this frontier (the linker hoists ftutil-style
  helpers); low-confidence rows are hypotheses for queue ordering.
- The vendor-modified face-open path means even high-confidence anchors
  (e.g. `FT_Open_Face`) may contain non-stock bodies; the tiers prove
  identity evidence, not pristine upstream bytes.
- The neutral-passthrough rule is a deliberate one-hop concession through
  leaf/runtime-only helpers; relaxing it further admits the vendor
  fallback-loader subtree, which is why it is pinned exactly.
- Hardware hints reuse the parent census's coarse `0x40000000`-range token
  heuristic and may false-positive on large numeric constants.
- Ghidra envelope boundaries are analyzer artifacts inherited from the
  corpus; official-byte attribution follows the parent's mask semantics.
