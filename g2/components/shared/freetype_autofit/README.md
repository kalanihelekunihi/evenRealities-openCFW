# G2 FreeType autofit community source

SPDX-License-Identifier: FTL

This component admits the authenticated FreeType 2.9.1 autofitter as a
software-only community-source candidate.  The implementation is the
unmodified `third_party/freetype/src/autofit/autofit.c` single-object
translation unit under the FreeType Project License.

The exact stock envelope `0x005A6260..0x005ABEF8` accounts for 87 callable
bodies / 23,612 bytes and five literal-pool intervals / 92 bytes.  It leaves
no unresolved callable or unclassified physical byte.  Twenty-nine functions
/ 3,270 bytes have module, auto-hinter interface, writing-system callback,
source-order, or independently matching leaf evidence; 58 / 20,342 have
authenticated whole-body, source-order, and call-graph evidence.  This is
source and semantic identity, not original-compiler byte identity.

The authenticated `src/autofit` inventory contains 37 `.c`/`.h` files and
650,482 bytes.  The focused gate compiles the single-object translation unit
for Cortex-M55 Thumb hard-float with warnings as errors.  The sole warning
compatibility exception, `-Wno-cast-function-type-mismatch`, is needed by the
unaltered 2.9.1 dummy writing-system callback cast and is also used by the
existing full FreeType candidate link gate.

No stock callsite, relocation, or placement is changed.  Exact
IAR-compatible code generation, authenticated font payloads, stack/WCET
qualification, and authorized hardware rendering remain release gates; no
hardware behavior is claimed.

Run the focused checks with:

```sh
python3 g2/tools/analyze_g2_freetype_autofit_source_admission.py --check-manifest
python3 -m unittest g2.tests.test_freetype_autofit_source_admission
```
