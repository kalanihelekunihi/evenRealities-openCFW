# G2 FreeType 2.9.1 engine census

Status: authenticated module-attribution triage map for the 0x51/0x52xxxx
FreeType frontier of official G2 `2.2.6.10`
Analysis mode: read-only; no signing, flashing, erase, or hardware operation

## Result

The [Apollo unanchored-function provenance census](g2-apollo-unanchored-census.md)
names the 342 no-evidence functions in the `0x51xxxx`/`0x52xxxx` ranges
(75,016 official opaque bytes) as its #1 follow-up frontier — the
hypothesized FreeType 2.9.1 engine around the byte-exact `FT_Done_Face`
anchor.  This census takes those 342 functions plus the 2 functions the
parent census already buckets `freetype` (the `FT_Done_Face` envelope
`0x00526814` and the `FT_Open_Face` envelope `0x005264A6`, 946 bytes) — a
**344-function, 75,962-official-byte census set** — and attributes each
function to a FreeType 2.9.1 module where distinctive evidence supports it:

- **128 functions (16,570 official bytes)** are attributed to the FreeType
  **base** module (`src/base`): 12 at high, 3 at medium, and 113 at low
  confidence.
- **216 functions (59,392 official bytes)** remain `investigation-required`:
  all 87 `0x51xxxx` functions (36,812 bytes) and 129 `0x52xxxx` functions
  (22,580 bytes).

No census function is attributed to any other module.  This is not evidence
that the frontier contains only base-layer code — it reflects where the
proven seeds sit (see [Limitations](#limitations)).  Everything is re-derived
from the authenticated official image (`36c5b0e4…78a27863`), the
authenticated 64-shard corpus, the authenticated FreeType 2.9.1 snapshot
(`PROVENANCE.json` `2be87176…794bf`), the recovered G2 module header
(`522c1d35…f05d74`), and the checked-in parent census manifest
(`a36c51c0…f7b96`) on every run; any drift raises `CensusError`.

## Method

The G2 module set is re-derived from the recovered
`third_party/freetype/g2-config/freetype/config/ftmodule.h` and validated
against the image: the ten `ft_default_modules[]` pointers at `0x0073EEF8`,
the NULL terminator, and each class struct's `module_name` string must match
the pins exactly.  Nine source modules are linked: `autofit`, `truetype`,
`cff`, `psaux`, `psnames`, `pshinter`, `sfnt`, `smooth` (three renderer
classes), plus `base`, which is not a registered module — it is linked
unconditionally and its presence is proven by the `FT_New_Library` anchor.

Seeds are built over the whole image in four tiers; the 344 census functions
are then classified by seed membership, call topology, and link-order
sandwich, in strict priority order.  Every function gets exactly one bucket,
one evidence class, and one confidence level.

| Tier | Evidence class | Confidence | Basis |
|---|---|---|---|
| 1 | `recovery-audit-anchor` | high | exact code pin from the [FreeType recovery audit](freetype-recovery-audit.md): `FT_Add_Default_Modules` `0x005242FC`, `FT_Init_FreeType` `0x0052431C`, `destroy_face` `0x005258A8`, `FT_Open_Face` `0x005264A6`, `FT_Done_Face` `0x00526814`, `FT_Add_Module` `0x0052729C`, `FT_New_Library` `0x005274B2` (all base), smooth three-pass LCD fallback body `0x005E22E0` (smooth) |
| 2 | `module-string-signature` | high | references, via a code-region literal-pool cell, a string literal of ≥6 characters appearing in exactly one G2-linked module's snapshot sources; literals used only inside `FT_TRACE*`/`FT_ERROR`/`FT_ASSERT` are excluded (dead in release builds) |
| 3 | `module-class-callback` / `raster-funcs-callback` | high | entry stored as a callback pointer in one of the ten pinned module class structs (9-word `FT_Module_Class`, 22-word `FT_Driver_ClassRec`, 15-word `FT_Renderer_Class`) or the smooth `FT_Raster_Funcs` table |
| 4 | `service-record-callback` | medium | entry stored in a service record behind a service-description table whose service-id list uniquely matches one module's `FT_DEFINE_SERVICEDESCRECn` variant in the snapshot |
| 5 | `call-topology-single-module` | medium | every closed-world call target collapses to one module |
| 6 | `call-topology-multi-module` | low | call targets span several modules (module unresolved; none occurred) |
| 7 | `link-order-sandwich` | low | nearest seed-labelled functions on both sides in address order share one module |
| 8 | `none` | none | no corroborating evidence |

Tier conflicts on seeds resolve to the higher tier and are reported; a
same-tier cross-module conflict fails closed.  Two conflicts occurred and
both resolve to **base**: the cff service table's `properties` record points
at `0x00527F0A`/`0x00527FF2`, which are `ps_property_set`/`ps_property_get` —
their implementation lives in `src/base/ftpsprop.c`, which is exactly what
the tier-2 string evidence (`hinting-engine`, `random-seed` literals) says.

### Derived seed map (50 seeds)

| Module | Seeds | In census set | Evidence |
|---|---:|---:|---|
| base | 12 | 12 | 7 anchors; 5 string (`Type 1`, `hinting-engine`/`random-seed`, `/..namedfork/rsrc`, `resource.frk/` — ftobjs/ftpsprop/ftrfork) |
| truetype | 11 | 0 | 1 string (`OpticalSize`); 2 class callbacks; 8 service callbacks (`multi-masters`, `metrics-variations`, `tt-glyf`) |
| cff | 10 | 0 | 4 class callbacks; 6 service callbacks (`glyph-dict`, `cff-load`, `multi-masters`) |
| autofit | 5 | 0 | 4 string (property names, digits table); 1 class callback |
| psnames | 4 | 0 | 4 service callbacks (`postscript-cmaps`) |
| smooth | 4 | 0 | 1 anchor; 3 raster-funcs callbacks |
| sfnt | 3 | 0 | 1 string (`missing`); 2 service callbacks (`sfnt-table`, `postscript-font-name`) |
| psaux | 1 | 0 | 1 string (`StartFontMetrics`, afmparse) |
| pshinter | 0 | 0 | no distinctive evidence recovered |

The five image service-description tables each matched exactly one snapshot
module variant: cff `0x006E2750` (10 ids — the
`TT_CONFIG_OPTION_GX_VAR_SUPPORT`-on, glyph-names-on variant, consistent with
the recovered configuration), truetype `0x00725060` (6 ids), sfnt
`0x00738B04` (5 ids — the `TT_CONFIG_OPTION_BDF`-on variant), autofit
`0x00785370` and psnames `0x00788430` (1 id each).

## Bucket census (census set)

| Bucket | Functions | Official bytes | Evidence (functions) |
|---|---:|---:|---|
| base (src/base) | 128 | 16,570 | anchor 7; string 5; topology 3; sandwich 113 |
| investigation-required | 216 | 59,392 | none 216 |
| **Total** | **344** | **75,962** | |

Attributed functions span `0x005242FC`–`0x0052862C`, the exact bracket
covered by the in-sea base anchors.  The three topology members are
`0x00524412` (targets the `Type 1` driver-check function `0x00525574`) and
`0x00525ADE`/`0x00525B6E` (both target only `FT_Open_Face`).

## Reconciliation with the parent census

| Figure | Parent census | This census |
|---|---:|---:|
| `0x51xxxx` no-evidence functions / bytes | 87 / 36,812 | 87 / 36,812 (all unattributed) |
| `0x52xxxx` no-evidence functions / bytes | 255 / 38,204 | 255 / 38,204 (126 attributed base / 15,624 B) |
| frontier total | 342 / 75,016 | 342 / 75,016 |
| parent `freetype` bucket | 2 / 946 | 2 / 946 (both now base, high) |
| census set | — | 344 / 75,962 |

The parent manifest's identity is pinned by SHA-256 and its per-function
body ranges are re-validated against the corpus; the frontier figures match
with zero drift.  The 2 parent `freetype` members keep their family and gain
a module: `FT_Done_Face` and `FT_Open_Face` are both `src/base/ftobjs.c`.

## Rejected evidence classes (considered and dropped)

- **Four-byte tag constants** (`'incr'`, `'OTTO'`, `'fvar'`, …): the Ghidra
  decompilation corpus never renders them as address tokens, and the audited
  compare sites (e.g. the `'incr'` compare at `0x005262A8`) are covered only
  by the rejected oversized analyzer envelopes, not by trustworthy functions.
- **String literals shorter than 6 characters**: generic words collide with
  non-FreeType providers (the psaux literal `"true"` occurs at three image
  addresses, two referenced by non-FreeType functions at `0x004D7F98` and
  `0x005001D2`).  The ≥6 rule plus the single-module rule and the pinned
  derived set keep the string tier exact.

## Limitations

- Attribution is **base-only** because every in-sea seed is a base seed.
  `truetype`, `cff`, `autofit`, `smooth`, `sfnt`, `psnames`, and `psaux`
  seeds all link outside the census ranges (`0x00577D7C`–`0x005F919C`), and
  large parts of the truetype/cff/smooth bodies (including the proven
  `tt_driver_init` `0x005F903C`, `tt_property_set` `0x005EF0B0`, and the CFF
  module initializer `0x005B004A`) are covered only by the rejected oversized
  envelope `0x005FA120`, so they cannot seed function-level topology.
- The 87 `0x51xxxx` functions (36,812 bytes) sit below the lowest in-sea
  seed (`0x005242FC`) and therefore cannot even sandwich; they remain
  unattributed wholesale.  Leading hypotheses: the sfnt module body
  (`ttcmap`/`ttload`/`ttmtx`/`sfobjs`/`ttsbit`), the remaining base objects
  (`ftgloadr`, `ftoutln`, `ftglyph`, `ftbitmap`, `ftstroke`, `ftcalc`,
  `fttrigon`, `ftmm`), and possibly `pshinter`/`psaux` internals.  Note the
  parent census flags the largest of them, `0x005202EC` (8,374 bytes), as a
  peripheral-register function — an Ambiq HAL/driver candidate that is
  probably *not* FreeType at all; this census correctly leaves it
  unattributed.
- The 82 unattributed functions above the last in-sea seed
  (`0x0052862C`–`0x0052FFFF`, 6,682 bytes) bracket against out-of-range
  seeds of different modules and stay unattributed.
- The 113 `link-order-sandwich` base labels are low-confidence adjacency
  hypotheses for queue ordering, never proof of ownership; the bracket spans
  several translation units (`ftobjs.c`, `ftinit.c`, `ftpsprop.c`,
  `ftrfork.c`, and whatever links between them).
- Module buckets are evidence triage, not per-function source ownership,
  behavioral reconstruction, or production-candidate readiness.

## Reproduction

```sh
python3 tools/analyze_g2_freetype_engine_census.py \
  --ghidra-corpus /path/to/full64-j64-auth \
  --write-manifests tools/manifests
```

Machine-readable output:

- `tools/manifests/g2-freetype-engine-census.tsv` — all 344 per-function
  assignments (entry, body range, envelope and official bytes, module bucket,
  evidence, confidence, detail).
- `tools/manifests/g2-freetype-engine-census-summary.json` — reconciliation,
  module order, seed map, service tables, and resolved seed conflicts.

The fail-closed guard is
[`../../tests/test_analyze_g2_freetype_engine_census.py`](../../tests/test_analyze_g2_freetype_engine_census.py):
rule-totality and pin well-formedness checks that run without the corpus,
plus corpus-backed checks (gated on `OPENCFW_APOLLO_GHIDRA_CORPUS`, default
`/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth`) covering the exact
bucket census, the per-function pins, mutation rejection, and byte-for-byte
manifest regeneration.
