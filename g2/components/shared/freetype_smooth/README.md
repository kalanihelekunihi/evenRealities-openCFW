# G2 FreeType smooth-renderer community source

SPDX-License-Identifier: FTL

This component admits the authenticated FreeType 2.9.1 smooth raster and
renderer family as a software-only community-source candidate.  The
implementation is the unmodified `third_party/freetype/src/smooth/smooth.c`
single-object translation unit under the FreeType Project License.

The complete stock envelope accounts for 29 callable bodies / 4,310 bytes
and leaves no unresolved callable code.  Sixteen functions / 804 bytes have
stock renderer-class, outline-table, or raster-table pointer evidence;
13 / 3,506 have authenticated source-order, call-graph, and whole-body
evidence.  The remaining 18 bytes are pinned alignment and literal data.
This is source and behavior identity, not original-compiler byte identity.

The three classes remain distinct: `smooth` selects normal grayscale,
`smooth-lcd` selects horizontal LCD, and `smooth-lcdv` selects vertical LCD.
All share the authenticated gray-raster callback table, as FreeType 2.9.1
defines, without merging their render callbacks or required modes.

The authenticated `src/smooth` inventory contains eight `.c`/`.h` files and
88,859 bytes.  The focused gate compiles the upstream single-object
translation unit warning-clean for Cortex-M55 Thumb hard-float.

No stock callsite, relocation, or placement is changed.  Exact
IAR-compatible code generation, authenticated font payloads, stack/WCET
qualification, and authorized hardware rendering remain release gates; no
hardware behavior is claimed.

Run the focused checks with:

```sh
python3 g2/tools/analyze_g2_freetype_smooth_source_admission.py --check-manifest
python3 -m unittest g2.tests.test_freetype_smooth_source_admission
```
