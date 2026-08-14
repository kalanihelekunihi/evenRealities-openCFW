# G2 LVGL vendor-fork object census

Status: authenticated per-module triage map for the LVGL frontier of official
G2 `2.2.6.10` Apollo-main.
Analysis mode: read-only; no signing, flashing, erase, or hardware operation.

## Result

The [Apollo unanchored-function provenance census](g2-apollo-unanchored-census.md)
buckets 1,054 unanchored functions (97,430 official opaque bytes) as the LVGL
9.3.0-development vendor fork and names two no-evidence address seas as its
highest-value LVGL follow-up frontiers.  This census deepens that triage to
per-source-object/module granularity over a **1,484-function / 187,354-byte**
scope:

- **804 functions (58,708 official bytes)** receive a module attribution —
  556 at medium and 248 at low confidence — across 15 LVGL modules,
  separating the Ambiq/Nema vendor-fork backend (15 functions / 4,080 bytes)
  from the public LVGL core (789 functions / 54,628 bytes).
- **680 functions (128,646 bytes)** stay explicitly `investigation-required`:
  57 with within-LVGL call evidence spanning multiple modules and 623 with no
  within-LVGL evidence at all — including **all 430 functions of the
  `0x5Dxxxx` and `0x5Axxxx` seas**.

The seas fail every within-LVGL test this census applies: no sea function
calls any LVGL-path-anchored seed, none is called by one, none is link-order
bracketed by two seeds of one module, and none calls a medium-confidence
attributed member of a single LVGL file.  The parent census's region
hypotheses ("LVGL vendor-fork draw/Nema internals", "LVGL/first-party draw
pipeline") are therefore **not confirmed**; see "Sea findings" below for the
evidence that actively points elsewhere for `0x5Dxxxx`.

Scope, seed set, and byte totals are re-derived on every run from the
authenticated image, the authenticated 64-shard Ghidra corpus, the embedded
source-path census, and the checked-in parent census manifest — nothing is
hardcoded from this report.  The analyzer fails closed on any drift in the
5,610-row parent manifest, the 78 retained LVGL paths, the 344 LVGL-anchored
seed functions, the 1,054/97,430 parent LVGL bucket, the 300/52,866 and
130/37,058 sea frontiers, or the frozen module/evidence census.

## Method

Every scoped function gets exactly one module label (or
`investigation-required`), one evidence class, and one confidence level.
Evidence tiers are evaluated in strict priority order:

| Tier | Evidence class | Confidence | Basis |
|---|---|---|---|
| 1 | `call-topology-single-file` | medium | every LVGL-path-anchored call target belongs to one retained LVGL source file |
| 2 | `call-topology-single-module` | medium | anchored LVGL call targets span several files of exactly one module |
| 3 | `call-topology-second-order-file` | low | no anchored targets; every medium-labelled call target is one file |
| 4 | `call-topology-second-order-module` | low | the same collapse at module granularity |
| 5 | `link-order-file-sandwich` | low | nearest LVGL-path-anchored functions on both sides share one file |
| 6 | `link-order-module-sandwich` | low | the same bracket at module granularity |
| 7 | `call-topology-mixed` | none | LVGL call evidence spans multiple modules |
| 8 | `none` | none | no within-LVGL evidence; external caller/callee families recorded |

Seeds are the 344 functions anchored by the 78 retained
`third_party\lvgl_v9.3` source paths (the parent census's `lvgl_v9.3`
anchors).  Module labels derive only from those retained paths; the mapping
is total and fails closed on any unmapped path.  Second-order propagation
draws only from medium-confidence tier-1/2 labels, never from other
low-confidence assignments — mirroring the parent census's rule that
heuristic labels never become seeds.

Scope selection re-derives from the checked-in parent manifest:

| Scope | Functions | Official bytes | Parent-census rows |
|---|---:|---:|---|
| `lvgl-topology` | 613 | 67,074 | LVGL bucket, `call-topology-single-family` |
| `lvgl-sandwich` | 441 | 30,356 | LVGL bucket, `link-order-sandwich` |
| `sea-0x5d` | 300 | 52,866 | no-evidence, `0x5D0000`–`0x5DFFFF` |
| `sea-0x5a` | 130 | 37,058 | no-evidence, `0x5A0000`–`0x5AFFFF` |
| **Total** | **1,484** | **187,354** | |

## Module census

| Module | Functions | Official bytes | Evidence (functions) |
|---|---:|---:|---|
| lvgl-core | 555 | 31,740 | single-file 417; single-module 26; 2nd-order 57; sandwich 55 |
| lvgl-misc | 107 | 15,232 | single-file 67; 2nd-order 13; sandwich 27 |
| lvgl-draw | 33 | 1,972 | single-file 12; 2nd-order 1; sandwich 20 |
| lvgl-widgets | 26 | 1,956 | single-file 7; single-module 1; 2nd-order 1; sandwich 17 |
| lvgl-display | 17 | 628 | single-file 1; sandwich 16 |
| lvgl-cache | 13 | 710 | single-file 7; single-module 2; 2nd-order 1; sandwich 3 |
| lvgl-freetype-wrapper | 13 | 604 | single-file 4; single-module 1; 2nd-order 3; sandwich 5 |
| lvgl-osal-freertos | 11 | 258 | single-file 3; 2nd-order 1; sandwich 7 |
| lvgl-layouts | 7 | 312 | sandwich 7 |
| lvgl-font | 4 | 922 | single-file 4 |
| lvgl-bin-decoder | 2 | 218 | sandwich 2 |
| lvgl-stdlib | 1 | 76 | single-file 1 |
| **public LVGL core subtotal** | **789** | **54,628** | |
| ambiq-draw-backend | 13 | 3,932 | single-file 1; sandwich 12 |
| ambiq-display-port | 1 | 0 | single-file 1 |
| ambiq-freetype-system | 1 | 148 | single-file 1 |
| **Ambiq/Nema vendor backend subtotal** | **15** | **4,080** | |
| investigation-required | 680 | 128,646 | mixed 57; none 623 |
| **Total** | **1,484** | **187,354** | |

Confidence split over the 804 attributed functions: **medium 556**
(single-file 526, single-module 30), **low 248** (second-order 77,
link-order sandwich 171).

Notes on specific modules:

- **lvgl-core dominance is structural.** 342 of the 417 single-file core
  attributions name `LVGL/src/core/lv_obj_style.c`, consistent with the large
  `lv_obj_set_style_*` setter family that file defines; a widget function that
  only calls style APIs is topologically indistinguishable from a member, so
  these are module triage labels, not file membership proofs.
- **ambiq-draw-backend** attributions cluster around the anchored
  `lv_draw_ambiq_*.c` files of the exact public Ambiq subtree `1e774257…`;
  the single zero-byte `ambiq-display-port` member is fully production
  source-owned per the display-port closure audit, so it contributes no
  official bytes.
- **lvgl-font** (4 functions / 922 bytes, all medium) maps to `lv_font.c`;
  the retained `lv_font_fmt_txt.c` path has no anchored function and therefore
  cannot seed attributions.

## Sea findings

**`0x5Dxxxx` (300 functions / 52,866 bytes): LVGL hypothesis not confirmed;
reverse topology points at Cordio.**  The sea's only external callers are the
Cordio-anchored `dm_conn.c` function at `0x005D2BAE` (8 call edges), the
medium-confidence Cordio function at `0x005D2E0C` (4 edges), and other
no-evidence functions at `0x5C`/`0x5E`/`0x5F`; 12 sea functions record
`external callers: cordio`.  No LVGL or Ambiq-backend function calls into the
sea, and the sea calls no LVGL seed.  Six sea functions call small first-party
utilities (`0x0044A43C`, `0x0046CACC`, `0x004751C8`, `0x005BF004`) and one
calls a Cordio function.  The sea's largest member `0x005D4ED0` (7,880 bytes,
multi-KB stack frames) is called only from within the sea.  Known NemaGFX
functions live elsewhere (`0x005141xx`, `0x005FAxxx` per the NemaGFX/Ambiq
dependency audit), so "Nema internals" is also not supported.  Revised leading
hypothesis: Cordio link-layer/security library internals adjacent to the
anchored `dm_conn.c` island — a Cordio-side follow-up, not an LVGL one.

**`0x5Axxxx` (130 functions / 37,058 bytes): no direct callers at all.**  No
function outside the sea calls into it; it calls only other no-evidence
functions plus six small first-party utilities.  Absence of direct callers is
consistent with function-pointer-dispatched code (LVGL class constructors,
draw-unit and decoder callbacks), but equally with any other
indirect-dispatch library, so the "LVGL/first-party draw pipeline" hypothesis
remains open and every member stays investigation-required.

## Reconciliation against the parent census

- LVGL bucket: 613 + 441 = **1,054 functions**; 67,074 + 30,356 =
  **97,430 official bytes** — exact match, zero drift.
- `0x5Dxxxx` frontier: **300 functions / 52,866 bytes** — exact match;
  largest member `0x005D4ED0` at 7,880 envelope bytes confirmed.
- `0x5Axxxx` frontier: **130 functions / 37,058 bytes** — exact match.
- Scope total: **1,484 functions / 187,354 official bytes**; module census
  sums to the same figures with no remainder.
- Seed set: 78 retained LVGL paths, 344 LVGL-anchored functions (338 under
  `LVGL\src`, 5 `lv_ambiq_display.c`, 1 `am_ftsystem.c`) — matches the parent
  census's 344 path-anchored LVGL functions.

## Reproduction

```sh
python3 tools/analyze_g2_lvgl_vendor_fork_census.py \
  --ghidra-corpus /path/to/full64-j64-auth \
  --write-manifests tools/manifests
```

Machine-readable output:

- `tools/manifests/g2-lvgl-vendor-fork-census.tsv` — all 1,484 per-function
  assignments (entry, body range, envelope and official bytes, scope, module,
  source file, evidence, confidence, detail).
- `tools/manifests/g2-lvgl-vendor-fork-census-summary.json` — the module
  table, evidence census, and reconciliation block above.

The fail-closed guard is
[`../../tests/test_analyze_g2_lvgl_vendor_fork_census.py`](../../tests/test_analyze_g2_lvgl_vendor_fork_census.py):
18 tests covering module-rule totality, closed evidence/confidence tables,
frozen-census internal consistency, parent-manifest mutation rejection, exact
scope/module/evidence pins, the investigation-required sea invariants, and
byte-identical manifest regeneration.

## Limitations

- Module and file labels are triage attributions for queue ordering, not
  per-function source ownership, behavioral reconstruction, or
  candidate-readiness claims; `low`-confidence labels in particular are
  hypotheses.
- The topology tiers infer membership from call targets into retained-path
  anchor functions; a caller that only uses another file's public API is
  indistinguishable from a member of that file (the `lv_obj_style.c` caveat
  above).
- Call targets are recovered from address tokens in decompiled bodies; data
  references that alias function entries are indistinguishable from calls.
- Second-order labels propagate only from medium-confidence single-family
  collapses and never feed further propagation.
- Functions fully source-owned in production (for example the Ambiq display
  port) show zero official bytes yet remain in the stock-side census.
- The 0x5D/0x5A seas are not per-function classified beyond "no
  within-LVGL evidence"; resolving them needs provider evidence outside the
  LVGL seed set (Cordio link-layer manifests, Nema archive admission).
