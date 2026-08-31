# G2 FreeType 2.9.1 autofit source admission

The authenticated Apollo-main default-module table contains FreeType
`autofitter`, TrueType, CFF, PSAux, PSNames, PSHinter, SFNT, and three smooth
renderer classes.  The admitted FreeType candidate already covers TrueType;
the table contains no standalone monochrome raster class.  Autofit was thus
the largest coherent authenticated default module not covered by the existing
base/CFF/SFNT/PSHinter/PSAux/PSNames/smooth admissions.

## Stock closure

The autofitter class at `0x00752520`, its interface at `0x00785380`, and the
CJK, dummy, Indic, and Latin writing-system callback records at `0x0075E310`
bound the callable set.  Exact FreeType 2.9.1 single-object source order and
the authenticated Ghidra call graph close internal identities.

| Category | Functions | Bytes |
|---|---:|---:|
| high confidence | 29 | 3,270 |
| medium confidence | 58 | 20,342 |
| mapped callable total | 87 | 23,612 |
| literal pools | 5 intervals | 92 |
| unresolved callable / unclassified physical | 0 | 0 |

The exact physical envelope is `0x005A6260..0x005ABEF8` (23,704 bytes).
It begins with source-exact `af_sort_pos`; the immediately preceding
authenticated body is not FreeType and ends at `0x005A6258`.  It ends after
`af_warper_compute`; the next address is independently table-referenced as a
separate callable.  Five complement intervals contain aligned literals and
pointers, not undecoded callable bodies.  The map analyzer rejects any byte
gap, overlap, input drift, callback-table drift, or source identity drift.

## Source admission

The upstream snapshot is FreeType 2.9.1 tag `VER-2-9-1`, peeled commit
`86bc8a95056c97a810986434a3f268cbe67f2902`, under the FreeType Project
License.  Its `src/autofit` inventory is 37 `.c`/`.h` files / 650,482 bytes.
The admitted entry is the unmodified `src/autofit/autofit.c` single-object
translation unit in its pinned 15-file include order.

The focused gate compiles that translation unit for ARM Cortex-M55, Thumb,
hard-float, freestanding C11, optimization enabled, and warnings as errors.
The only warning exception is `-Wno-cast-function-type-mismatch`, required by
an unmodified FreeType 2.9.1 dummy writing-system callback cast and already
used by the complete FreeType candidate link gate.

## Evidence boundary

This is a software-only source admission.  It does not claim original IAR
compiler-byte identity and does not add a stock callsite, relocation, target
placement, or production-image route.  No authorized physical G2 hardware or
authenticated external font payload was supplied.  Pinned IAR-compatible code
generation/placement, font configuration, task-stack and WCET qualification,
and authorized on-device rendering remain explicit release gates.

Run:

```sh
python3 g2/tools/analyze_g2_freetype_autofit_function_map.py --pretty
python3 g2/tools/analyze_g2_freetype_autofit_source_admission.py --check-manifest
python3 -m unittest g2.tests.test_freetype_autofit_source_admission
```
