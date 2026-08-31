# G2 FreeType base complete-map source admission

SPDX-License-Identifier: MIT

## Result

The stock Apollo-main FreeType 2.9.1 base envelope is completely classified:

| Class | Functions | Bytes |
| --- | ---: | ---: |
| High-confidence source identities | 126 | 16,014 |
| Retained medium-confidence identities from the earlier candidate | 56 | 4,428 |
| Callable total | 182 | 20,442 |
| Literal/pointer data pools | — | 230 |
| Alignment padding | — | 4 |
| Physical total | — | 20,676 |
| Unresolved callable or physical bytes | — | 0 |

The exact envelope is `[0x005242FC,0x005293C0)`. The following Ghidra body at
`0x005293C0` is separately pinned and is not assigned to FreeType base.

## Why the former admission was narrower

The earlier admission closed an 83-function, 7,874-byte reachable cluster and
seven 1,862-byte Mac-resource mechanics. That 90-function, 9,736-byte source
candidate was useful, but it was not a complete physical map. The present map
adds 92 functions and 10,706 callable bytes while preserving the old direct,
indirect, and documented-anchor confidence tiers.

The complete census also corrects a decompiler artifact. The source function
`ft_mem_strcpyn` occupies `[0x005292BC,0x005292E6)`. Its entry branches forward
to a loop test and then backward into the loop body. Ghidra represented the
two-byte entry as a thunk and incorrectly promoted the internal basic block at
`0x005292C8` as another overlapping function. Thumb control flow and the exact
2.9.1 source independently show one 42-byte source function.

Five complete source callables were present in authenticated bytes but absent
from the Ghidra function list:

| Address | Bytes | Source identity | Corroboration |
| --- | ---: | --- | --- |
| `0x00528272` | 38 | `ft_raccess_sort_ref_by_id` | qsort callback role, signed-ID comparator semantics, source order |
| `0x0052857E` | 86 | `raccess_guess_darwin_hfsplus` | rule table, `/rsrc` construction, neighboring rule bodies |
| `0x00528650` | 36 | `raccess_guess_linux_cap` | rule table and `.resource/` path construction |
| `0x00528674` | 62 | `raccess_guess_linux_double` | rule table and shared AppleDouble loader call |
| `0x005286B2` | 64 | `raccess_guess_linux_netatalk` | rule table and shared AppleDouble loader call |

Every callable record is tied to an official-image body hash, a pinned
FreeType 2.9.1 definition, and source-order plus call, table, string, or
control-flow semantics. Ambiguous aliases are not promoted; the only apparent
alias was the `ft_mem_strcpyn` internal-block artifact above and is explicitly
removed from the callable ledger.

## Source admission and deterministic gates

The existing `components/shared/freetype_base` adapter is retained. Its source
inventory contains the 21 provenance-pinned base inputs selected by the
FreeType `ftbase.c` amalgamation and the standalone `ftinit.c` and
`ftbitmap.c` units. Focused tests compile those three upstream translation
units and the maintained adapter for `arm-none-eabi`, Cortex-M55 Thumb
hard-float, short enums, freestanding C11, and warnings-as-errors. Host tests
exercise the allocator lifecycle, all injected initialization failures, the
exact ten-module set, memory-face policies, and a real minimal TrueType render.

The complete-map tests fail closed on mutations to:

- an official callable byte;
- either pinned Ghidra bundle;
- an authenticated upstream source file;
- any classified physical-residue digest;
- the checked-in complete-map or source-admission manifest.

Run:

```sh
cd g2
python3 tools/analyze_g2_freetype_base_function_map.py --pretty
python3 tools/analyze_g2_freetype_base_source_admission.py --check-manifest
python3 -m unittest -v tests.test_runtime_freetype_base_admission
```

## Evidence limits

This is source and semantic admission, not compiler-byte identity. Nothing in
this tranche authenticates IAR-equivalent code generation, relocation,
placement, a stock callsite route, an external font payload, task stack or
worst-case execution time, or behavior on physical G2 hardware. The component
is not routed by the Apollo overlay or its component builder. Hardware
validation was not performed because no authorized device or authenticated
font payload was supplied to this software-only work.
