# G2 FreeType SFNT community source

SPDX-License-Identifier: FTL

This component admits the authenticated FreeType 2.9.1 SFNT implementation as
a software-only community-source candidate.  The implementation remains the
unmodified single-object translation unit at
`third_party/freetype/src/sfnt/sfnt.c` under the FreeType Project License.

The pinned stock-image map accounts for 136 callable bodies / 29,258 bytes.
Seventy-five bodies / 13,164 bytes have direct table or decoded call-edge
anchors plus complete-boundary evidence; 61 / 16,094 retain medium
source/call-graph confidence.  No callable-code bytes remain in the mapped
envelope's physical complement.  This is source and behavior identity, not
original-compiler byte identity.

The complete authenticated `src/sfnt` inventory contains 25 `.c`/`.h` files
and 413,337 bytes.  The Cortex-M55 gate compiles the upstream `sfnt.c` single
object with the recovered G2 FreeType configuration.  Clang's
`-Wno-cast-function-type-mismatch` exception is narrowly required for the
upstream 2.9.1 format-14 callback cast (`FT_Int` implementation versus the
historical `FT_Bool` callback typedef); all other selected warnings remain
errors.

No stock callsite, relocation, or placement is changed.  Exact IAR-compatible
code generation, font payloads, stack/WCET qualification, and authorized
hardware rendering remain release gates; no hardware behavior is claimed.

Run the focused software checks with:

```sh
python3 g2/tools/analyze_g2_freetype_sfnt_source_admission.py --check-manifest
python3 -m unittest g2.tests.test_freetype_sfnt_source_admission
```
