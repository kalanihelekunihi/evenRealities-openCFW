# G2 FreeType CFF size-optimization experiment

SPDX-License-Identifier: MIT

This software-only experiment compiles the exact admitted FreeType 2.9.1 CFF
single-object translation unit, the existing policy adapter, and the existing
source-owned import providers.  It changes no source file, public ABI, feature
definition, allocator/error path, module class, callback table, or supported
CFF input.  Its only selected change is clang's semantics-preserving `-Oz`
optimization level for Cortex-M55 Thumb hard-float code.

## Results

The authenticated legal application scatter upper bound is 21,706 bytes.
Baseline `-O2` needs 26,780 Apple or 26,712 Linux loadable bytes.  `-Os`
improves those figures to 22,144 and 22,368 but remains short.  The selected
whole-translation-unit `-Oz` build needs:

| Profile | text | exidx | rodata | loadable | flat binary | loadable margin |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Apple clang | 15,482 | 16 | 4,918 | 20,416 | 20,430 | 1,290 |
| Linux clang | 15,430 | 16 | 4,918 | 20,364 | 20,378 | 1,342 |

Both profiles therefore close the byte-count threshold.  This is not an exact
scatter placement proof: the 21,706 bytes comprise a 16,924-byte old CFF
envelope, 360 individually authenticated table/callback bytes, and the
4,422-byte application tail.  Function/input-section atomicity, collisions,
final relocated bytes, and the guarded class-pointer patch remain separate
gates.

Section GC produces byte-identical `-Oz` final binaries after the seven public
roots are retained, so it saves zero.  Rooted full LTO reaches 20,252 Apple and
20,244 Linux loadable bytes.  Adding `-fmerge-all-constants` changes nothing.
LTO is not selected because it internalizes and folds the independently
auditable function/callback symbol surface and is unnecessary to close the
byte threshold.

No new source-level feature elimination is admitted.  The recovered G2
configuration already excludes environment properties, zlib, subpixel
rendering, and the old CFF engine while retaining incremental loading and the
Adobe engine.  Inventing additional exclusions would change the supported
input or policy surface.

## Roots, imports, and evidence bounds

The non-LTO `-Oz` source object retains 58 address-taking relocations to 55
distinct CFF callback/service/parser roots in both compiler profiles.  Of the
complete 101 mapped source functions, 81 remain named emitted functions and
clang's inline remarks account for exactly the other 20.  The two sets are
disjoint and their union is the complete map.  A section-GC link rooted at
`cff_driver_class` and the six adapter exports is byte-identical to the
non-GC result, proving that all emitted sections remain reachable from those
seven public/class roots; this is why the 20 absent symbols are inlining, not
an incomplete source closure.  The final links have no undefined symbols,
relocations, writable static data, or BSS.

`-Oz` introduces one compiler-generated `R_ARM_THM_CALL` to
`__aeabi_memcpy`, in `cff_ps_get_font_info` at section offset 26.  It binds to
the authenticated current-package redirect at `0x00439BE4`, which branches to
the 152-byte source-compiled void-EABI leaf at `0x007C29F8`.  The leaf accepts
destination, source, and count in `r0`–`r2`; the compiler-generated call does
not consume a return value.

Compiler byte identity, exact scatter placement, font payload identity,
dynamic allocation bounds, task stack, WCET, and hardware rendering are not
claimed.  The module-class pointer patch is not emitted or permitted, and no
firmware image is produced.

Run the deterministic experiment and hostile checks with:

```sh
cd g2
python3 tools/analyze_g2_freetype_cff_size_optimization.py --check-manifest
python3 -m unittest -v tests/test_freetype_cff_size_optimization.py
```
