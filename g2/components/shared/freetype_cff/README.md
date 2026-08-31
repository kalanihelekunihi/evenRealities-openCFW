# G2 FreeType CFF community source

SPDX-License-Identifier: FTL

This component exposes the production-facing policy boundary for the
authenticated FreeType 2.9.1 CFF driver.  The unmodified CFF implementation is
retained under `third_party/freetype`; this adapter is distributed under the
same FreeType Project License.

Two independent earlier stock-image closures source-authenticate 47 retained
functions and 12,062 code bytes.  Thirty-eight functions / 11,326 bytes are
CFF engine bodies and nine functions / 736 bytes are exact FreeType base
support.  They are retained as a narrower historical candidate rather than
treated as a complete module map.

The complete CFF physical audit covers `[0x005ABEF8,0x005B0114)`: 101 callable
bodies / 16,718 bytes plus 204 bytes of literal-pointer data and two bytes of
alignment padding.  It has no unclassified or unresolved callable bytes.  The
complete selected CFF source inventory contains 17 authenticated `.c`/`.h`
files and 269,028 source bytes.

The adapter makes the recovered runtime policy fail closed:

- only the Adobe hinting engine is accepted because the G2 configuration
  excludes `CFF_CONFIG_OPTION_OLD_ENGINE`;
- stem-darkening input is a strict Boolean; and
- all eight darkening coordinates are checked before the upstream property
  service is called.

The focused host gate executes the adapter against the actual selected 2.9.1
module set.  A strict Cortex-M55 Thumb hard-float gate compiles the unmodified
`src/cff/cff.c` translation unit and the policy adapter with warnings as errors
and short enums.  Mutation tests reject changes to the image, Ghidra corpus,
source inventory, retained boundary tables, and physical-residue hashes.

This is community-source admission, not stock-image patch admission.  Exact
IAR code generation, link placement, external font payloads, task stack/WCET,
and hardware rendering remain separate release gates.  No hardware behavior is
claimed here.

Run the software-only checks with:

```sh
cd g2
make freetype-cff-source-closure
```
