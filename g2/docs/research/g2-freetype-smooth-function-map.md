# G2 FreeType 2.9.1 smooth renderer callable and source admission

SPDX-License-Identifier: MIT

## Result

The closed SFNT interval ends at `0x005E1594`; the authenticated Cordio SMP-SC
interval begins at `0x005E267C`.  Between them, the three renderer classes at
`0x00718D9C`, `0x00718DD8`, and `0x00718E14`, their shared gray-raster table at
`0x0077BEFC`, and the outline callback table at `0x0077BEE4` close the complete
smooth family envelope to `0x005E1594-0x005E267C` (4,328 bytes).

All 29 callable bodies / 4,310 bytes map to exact FreeType 2.9.1 definitions.
Sixteen / 804 bytes have renderer-class, outline-table, or raster-table
function-pointer evidence plus complete body and source-order corroboration.
Thirteen internal raster/render helpers / 3,506 bytes have the pinned Ghidra
body or recovered complete Thumb body, exact single-object source order, and
call-graph evidence.  No callable identity is unresolved.

The final 18 bytes before the three render wrappers split into two bytes of
alignment and a pinned 16-byte literal pool.  Its first word is the outline
callback table address; the remaining words are the exact generic-render
constants.  No physical byte is unclassified.

## Renderer semantics

The stock classes do not alias their render entry:

| Class | Stock callback | Required mode |
|---|---:|---|
| `smooth` | `0x005E2648` | `FT_RENDER_MODE_NORMAL` |
| `smooth-lcd` | `0x005E2660` | `FT_RENDER_MODE_LCD` |
| `smooth-lcdv` | `0x005E266E` | `FT_RENDER_MODE_LCD_V` |

The analyzer pins all 45 class words, all three names, the wrapper bodies, and
the corresponding 2.9.1 source tokens.  A merged callback or changed mode
therefore fails closed.

## Source admission

The isolated production-capable candidate is the upstream 2.9.1 single-object
translation unit `src/smooth/smooth.c`, pinned to tag `VER-2-9-1` and commit
`86bc8a95056c97a810986434a3f268cbe67f2902`.  The complete eight-file smooth
inventory is 88,859 bytes.  Focused verification compiles the unmodified unit
for Cortex-M55 Thumb hard-float with warnings as errors and checks the result
is an ARM ELF relocatable object containing all three renderer names.

This proves source availability and target compilation, not original IAR
compiler-byte identity.  No authenticated callsite, relocation, placement, or
core overlay route was found or added.  Font payload/face-path configuration,
task stack and worst-case execution time, and authorized hardware rendering
are explicit remaining gates.  No hardware behavior is claimed.

## Reproduction

```sh
python3 g2/tools/analyze_g2_freetype_smooth_function_map.py --check-manifest
python3 g2/tools/analyze_g2_freetype_smooth_source_admission.py --check-manifest
python3 -m unittest \
  g2.tests.test_analyze_g2_freetype_smooth_function_map \
  g2.tests.test_freetype_smooth_source_admission
```
