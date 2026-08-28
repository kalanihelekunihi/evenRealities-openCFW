# Apollo `0x5Dxxxx` hop-4 and residue source attribution

Status: research-only, software-only, not production-routed.

This tranche closes every function in the corrected census's hop-4 and
island-caller groups and resolves the last three typed-external hop-2 bodies.
All twelve are exact members of the vendored FreeType PostScript/CFF source.

| Group | Functions | Bytes |
|---|---:|---:|
| Final hop-2 residue | 3 | 308 |
| Island caller | 1 | 448 |
| Closure hop 4 | 8 | 948 |

The former hop-2 residue identities are:

- `0x005D185E`: `psobjs.c:ps_builder_check_points`; the decompilation is the
  expanded glyph-loader capacity check followed by the checked allocator call.
- `0x005D1986`: `psobjs.c:ps_builder_close_contour`; point, tag, contour, empty
  contour, duplicate endpoint, and one-point contour behavior all match.
- `0x005D1ED0`: `t1decode.c:t1_lookup_glyph_by_stdcharcode_ps`; it performs the
  0..255 check, Adobe standard-name lookup, first-character filter, and full
  glyph-name comparison.

The single 448-byte island caller at `0x005D3068` is
`psft.c:cf2_decoder_parse_charstrings`.  Its persistent CF2 instance setup,
outline callback initialization, scale/hint extraction, transform validation,
glyph-outline call, and width propagation provide positive identity evidence.

The eight hop-4 bodies complete the ordered `pshints.c` family:
`cf2_hint_isValid`, `cf2_hint_isPair`, `cf2_hint_isPairTop`,
`cf2_hint_isBottom`, `cf2_hint_lock`, `cf2_hintmap_map`,
`cf2_glyphpath_hintPoint`, and `cf2_glyphpath_computeIntersection`.

The actual implementations remain in `g2/third_party/freetype` under the
FreeType Project License and retained file-specific notices and grants.  The
Apache-2.0 code under `g2/research/candidates/cordio_ll_sea_hop4_residue` is a
typed identity/provider adapter only; it copies no upstream implementation.

## Accounting

| State | Functions | Bytes |
|---|---:|---:|
| Previous unsupported remainder | 210 | 35,348 |
| Source recovered here | 12 | 1,704 |
| Remaining unsupported | 198 | 33,644 |
| Remaining typed-external hop-2 | 0 | 0 |

The remaining 198 functions are outside the now-complete attributed closure;
they require a separate source-attribution pass rather than extrapolation from
the former Cordio topology label.

The isolated analyzer is
`g2/tools/analyze_g2_cordio_ll_sea_hop4_residue_candidate.py`; focused tests are
`g2/tests/test_g2_cordio_ll_sea_hop4_residue_candidate.py`.  No production
components, global census outputs, manifests, packaging, overlays, Makefiles,
or hardware are modified.
