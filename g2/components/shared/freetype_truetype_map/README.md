# G2 FreeType TrueType complete-map community source

SPDX-License-Identifier: FTL

This component supplements, but does not replace, the existing
`components/shared/freetype` TrueType candidate.  That candidate proves a
reachable driver/interpreter graph of 248 functions / 38,828 bytes and a
successful full-source link.  It did not claim a complete stock physical map.

The complete stock envelope is `0x005EF0B0..0x005F958C` (42,204 bytes).  It
contains 265 source-authenticated callable bodies / 41,728 bytes and 25 pinned
literal, pointer, data, or padding intervals / 476 bytes.  The additional 17
functions / 2,900 bytes include property-service callbacks, glyph-frame
callbacks, GX variation service wrappers, and other source-ordered bodies
outside the prior reachability tranche.  No callable or physical byte remains
unresolved or unclassified.  This is source/semantic identity, not
original-compiler byte identity.

The authenticated `src/truetype` inventory contains 18 `.c`/`.h` files and
739,559 bytes.  The admitted implementation is the unmodified FreeType 2.9.1
`truetype.c` single-object translation unit under the FreeType Project License.
The focused gate compiles it for Cortex-M55 Thumb hard-float with warnings as
errors and the same documented 2.9.1 callback-cast exception as the full
FreeType link gate.

No stock callsite, relocation, or placement is changed.  Exact IAR-compatible
code generation, authenticated font payloads, stack/WCET qualification, and
authorized hardware rendering remain release gates; no hardware behavior is
claimed.

```sh
python3 g2/tools/analyze_g2_freetype_truetype_source_admission.py --check-manifest
python3 -m unittest g2.tests.test_freetype_truetype_map_source_admission
```
