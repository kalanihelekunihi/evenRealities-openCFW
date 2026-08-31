# G2 FreeType PSNames community source

SPDX-License-Identifier: FTL

This component admits the authenticated FreeType 2.9.1 PostScript names
module as a software-only community-source candidate.  The implementation is
the unmodified `third_party/freetype/src/psnames/psnames.c` single-object
translation unit under the FreeType Project License.

The complete stock envelope accounts for 11 PSNames callable bodies / 1,132
bytes and leaves no unresolved callable code.  Eight functions / 844 bytes
have stock service-interface, module-requester, or callback-pointer evidence;
three / 288 have authenticated source-order, semantic-call, and whole-body
evidence.  The remaining 36 bytes are a pinned literal/pointer pool.  This is
source and behavior identity, not original-compiler byte identity.

The authenticated `src/psnames` inventory contains seven `.c`/`.h` files and
296,242 bytes.  The focused gate compiles the upstream single-object
translation unit warning-clean for Cortex-M55 Thumb hard-float.

No stock callsite, relocation, or placement is changed.  Exact
IAR-compatible code generation, authenticated font payloads, stack/WCET
qualification, and authorized hardware rendering remain release gates; no
hardware behavior is claimed.

Run the focused checks with:

```sh
python3 g2/tools/analyze_g2_freetype_psnames_source_admission.py --check-manifest
python3 -m unittest g2.tests.test_freetype_psnames_source_admission
```
