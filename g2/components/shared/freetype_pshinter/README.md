# G2 FreeType PSHinter community source

SPDX-License-Identifier: FTL

This component admits the authenticated FreeType 2.9.1 PostScript hinter as a
software-only community-source candidate.  The implementation remains the
unmodified `third_party/freetype/src/pshinter/pshinter.c` single-object
translation unit under the FreeType Project License.

The stock map accounts for 79 callable bodies / 9,188 bytes and leaves no
callable-code residue.  Eighteen functions / 1,554 bytes have direct module,
interface, or nested function-table pointers plus complete boundary evidence;
61 / 7,634 retain medium source/call-graph confidence.  The physical
complement is only a four-byte literal and the 52-byte function table.  This
is source and behavior identity, not original-compiler byte identity.

The complete authenticated `src/pshinter` inventory contains 12 `.c`/`.h`
files and 147,127 bytes.  The focused gate compiles the upstream single-object
translation unit warning-clean for Cortex-M55 Thumb hard-float, while the
existing full provider gate links it with the selected FreeType stack.

No stock callsite, relocation, or placement is changed.  Exact IAR-compatible
code generation, font payloads, stack/WCET qualification, and authorized
hardware rendering remain release gates; no hardware behavior is claimed.

Run the focused checks with:

```sh
python3 g2/tools/analyze_g2_freetype_pshinter_source_admission.py --check-manifest
python3 -m unittest g2.tests.test_freetype_pshinter_source_admission
```
