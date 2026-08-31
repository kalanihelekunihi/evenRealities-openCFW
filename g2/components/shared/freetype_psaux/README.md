# G2 FreeType PSAux community source

SPDX-License-Identifier: FTL

This component admits the authenticated FreeType 2.9.1 PostScript auxiliary
module as a software-only community-source candidate.  The implementation is
the unmodified `third_party/freetype/src/psaux/psaux.c` single-object
translation unit under the FreeType Project License, including the retained
Adobe notices and patent grant in the CF2 files.

The complete stock envelope accounts for 199 PSAux callable bodies / 29,750
bytes and leaves no unresolved callable code.  Sixty-five functions / 7,020
bytes have stock interface, callback-table, or literal function-pointer
evidence; 134 / 22,730 have authenticated source-order, semantic-call, and
whole-body evidence.  Two interleaved Cordio callables / 762 bytes remain
explicitly foreign.  The remaining 144 bytes are pinned literals, pointer
tables, strings, or alignment.  This is source and behavior identity, not
original-compiler byte identity.

The complete authenticated `src/psaux` inventory contains 37 `.c`/`.h` files
and 625,815 bytes.  The focused gate compiles the upstream single-object
translation unit warning-clean for Cortex-M55 Thumb hard-float.

No stock callsite, relocation, or placement is changed.  Exact IAR-compatible
code generation, font payloads, stack/WCET qualification, and authorized
hardware rendering remain release gates; no hardware behavior is claimed.

Run the focused checks with:

```sh
python3 g2/tools/analyze_g2_freetype_psaux_source_admission.py --check-manifest
python3 -m unittest g2.tests.test_freetype_psaux_source_admission
```
