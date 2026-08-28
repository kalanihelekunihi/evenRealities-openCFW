# Apollo `0x5Dxxxx` anchor and hop-3 source attribution

Status: research-only, software-only, not production-routed.

This tranche continues the corrected sea audit after the first hop-2 pass.  It
positively identifies three groups whose census labels describe reachability,
not ownership:

| Group | Functions | Bytes | Result |
|---|---:|---:|---|
| Medium anchor/direct callees | 12 | 9,420 | exact upstream identities |
| Formerly external hop-2 bodies | 11 | 2,854 | exact upstream identities |
| Closure hop 3 | 22 | 3,400 | exact upstream identities |

All 45 bodies are members of the vendored FreeType PostScript/CFF
implementation.  Representative exact matches include `cf2_blues_init`,
`cf2_computeDarkening`, `cf2_getWindingMomentum`, the complete hint-map and
glyph-path families, the hint-mask family, `cf2_doStems`, `cf2_doFlex`,
`cf2_doBlend`, and `cf2_interpT2CharString`.  The 78-byte hop-3 body at
`0x005D2196` is `cff_lookup_glyph_by_stdcharcode`.

Evidence combines authenticated stock ranges, distinctive decompiled
semantics, exact structure offsets and error values, and ordered function
families in pinned upstream files.  The analyzer requires every upstream
definition and retained FreeType license notice.  It also requires the prior
hop-2 analyzer to remain qualified before accepting a refinement.

The implementation remains in `g2/third_party/freetype` under the FreeType
Project License and each file's retained notices and grants.  The Apache-2.0
code under `g2/research/candidates/cordio_ll_sea_anchor_hop3` is only a named,
typed provider adapter; it copies no upstream implementation and is not part of
production component discovery.

The three hop-2 bodies at `0x005D185E`, `0x005D1986`, and `0x005D1ED0` remain
fail-closed external boundaries in the prior research adapter.  No semantics
are invented for their combined 308 bytes.

## Remainder accounting

| State | Functions | Bytes |
|---|---:|---:|
| Before this continuation | 243 | 41,602 |
| Source recovered here | 33 | 6,254 |
| Remaining unsupported | 210 | 35,348 |
| Unselected after hop 3 | 207 | 35,040 |
| Typed external hop-2 residue | 3 | 308 |

The medium anchor group improves exact identity and licensing but was already
excluded from the 243-function baseline, so it is not subtracted twice.

The isolated analyzer is
`g2/tools/analyze_g2_cordio_ll_sea_anchor_hop3_candidate.py`; tests are in
`g2/tests/test_g2_cordio_ll_sea_anchor_hop3_candidate.py`.  Global census
outputs, manifests, packaging, overlays, Makefiles, and hardware are unchanged.
