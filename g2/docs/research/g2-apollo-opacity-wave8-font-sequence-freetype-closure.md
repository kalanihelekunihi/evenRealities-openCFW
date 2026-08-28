# G2 Apollo opacity wave 8: Unicode sequence and FreeType closure

## Result

Wave 8 closes the complete static actionable graph rooted at
`0x005A8D06–0x005A9628`.  Starting from the wave-7 residual of 1,386
functions and 163,138 official opaque bytes, the graph contains:

- 28 positive-byte functions totaling 5,370 bytes;
- one reachable 22-byte physical `strchr`-compatible body at `0x00481818`
  which the parent census already counts as zero official opaque bytes;
- six terminal callees already classified by prior source/family work; and
- 38 distinct caller/callee pairs, including multiplicity at repeated call
  sites.

After reconciling all 29 reachable residual rows, 1,357 functions and 157,768
bytes remain.  The next-largest envelope is `0x0051A8EC` / 2,090 bytes.

## Positive FreeType attribution

The earlier family census intentionally left the `0x00524354–0x00527BCA`
rows negative because call-community reachability alone was insufficient.
This closure supplies independent positive evidence:

- `0x00524606` consumes the scalar `0x0001FB66` (129,894), the distinctive
  overflow threshold in FreeType 2.9.1 `FT_MulDiv`;
- `0x00524B64` resolves the `"font-format"` service string and has the exact
  `FT_Get_Font_Format` service-dispatch shape;
- `0x00525574` resolves `"Type 1"` and reproduces the 2.9.1
  `FT_Load_Glyph` flag resolution, Adobe-engine exception, auto-hinter,
  outline, transform, and render flow; and
- source-order, call topology, constants, data layouts, and branch semantics
  then identify the 17 supporting arithmetic, advance, bitmap, character-map,
  and outline functions.

The 20 newly source-attributed functions total 2,552 bytes:

| Source file | Exact identities |
|---|---|
| `ftadvanc.c` | `_ft_face_scale_advances`, `FT_Get_Advance`, `FT_Get_Advances` |
| `ftcalc.c` | `FT_MSB`, `ft_multo64`, `ft_div64by32`, `FT_Add64`, `FT_MulDiv`, `FT_MulFix` |
| `ftfntfmt.c` | `FT_Get_Font_Format` |
| `ftlcdfil.c` | `ft_lcd_padding` |
| `ftobjs.c` | `ft_glyphslot_preset_bitmap`, `ft_glyphslot_grid_fit_metrics`, `FT_Load_Glyph`, `FT_Get_Char_Index` |
| `ftoutln.c` | `FT_Outline_Check`, `FT_Outline_Get_CBox`, `FT_Outline_Translate`, `FT_Vector_Transform`, `FT_Outline_Transform` |

Five already family-classified terminal functions are also upgraded in the
isolated frontier record to exact identities: `ft_glyphslot_clear`,
`ft_lookup_glyph_renderer`, `FT_Render_Glyph`, `ft_mem_alloc`, and
`ft_mem_free`.  They add no wave-8 bytes because their census rows were
already outside the residual.

The source is the checked-in authenticated FreeType `VER-2-9-1` snapshot at
peeled commit `86bc8a95056c97a810986434a3f268cbe67f2902`.  Its FreeType Project License
(FTL) is retained.  The source pin and semantic identity do not prove a
byte-identical G2 checkout, IAR version, preprocessor configuration, or object
layout; the provenance record itself explicitly says the exact G2 checkout is
not proven.

## Product-specific and runtime boundaries

Eight positive-byte functions (2,818 bytes) remain fail-closed:

- the 2,338-byte Unicode-script/glyph-fit coordinator;
- six linked sorting, allocation, UTF-8 decoding, and advance-query wrappers;
  and
- the 44-byte `strstr`-compatible IAR DLIB-family helper.

The zero-official-byte `strchr`-compatible helper is likewise typed, SHA
pinned, and not treated as source-owned merely because its behavior is
recognizable.  Exact maintained product source and license are unavailable;
the exact IAR DLIB release/source/license route is also unavailable.  No
implementation semantics are invented for these boundaries.

## Complete support-data graph

All 29 reachable bodies have contiguous Ghidra ranges, so their function
envelopes contain zero interior gap bytes.  Scanning every body yields exactly
five direct `DAT_` cells.  The cells and their four referenced targets form
nine pinned support-data records (6,264 physical bytes), all outside function
opacity accounting:

- the `FT_MulDiv` scalar and two pointers to `"font-format"` and `"Type 1"`;
- two root pointers to a 250-record `<u16 offset, u16 flags>` table and a
  5,225-byte UTF-8 sequence pool.

The sequence table contains 53 sentinel records.  Its sentinel value is
`0x1469`, exactly the pool length.  The other records contain 186 unique
offsets; every offset begins a valid NUL-terminated UTF-8 string, and the
maximum referenced string ends exactly at the pool boundary.  This proves the
bounded table/pool extent without guessing a provider identity.  Support data
add zero function-opacity bytes.

## Production admission

This wave is source-level and research-only.  FreeType source is release-ready
under its retained FTL terms, but no source body or support table is routed into
the production binary overlay.  Honest binary admission still requires a
reviewed Cortex-M55/IAR-compatible build configuration plus byte-exact codegen,
relocation, symbol/link closure, and placement evidence.  The unavailable
product-specific and IAR runtime rows additionally require maintained source
and license resolution or clean-room replacements with independent
qualification.

The analyzer performs only offline reads; no directed hardware work is part of
this wave.
