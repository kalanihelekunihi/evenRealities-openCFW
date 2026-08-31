# G2 FreeType 2.9.1 PSNames callable and source admission

SPDX-License-Identifier: MIT

## Result

The stock `psnames` module class at `0x00758A60`, the `psnames` string at
`0x0078E444`, its service interface at `0x00764290`, and the next authenticated
foreign function at `0x005D9950` bound the complete retained PSNames text
envelope to `0x005D94C0-0x005D9950` (1,168 bytes).

All 11 callable bodies / 1,132 bytes are mapped to exact FreeType 2.9.1 source
definitions.  Eight / 844 bytes have a stock service slot, module requester,
or private qsort callback pointer plus complete body and source-order evidence.
Three private helpers / 288 bytes have the pinned Ghidra whole body and closed
source census evidence and remain medium confidence because there is no direct
stock function-pointer anchor.  No callable identity is unresolved.

The final `0x005D992C-0x005D9950` interval (36 bytes) is a pinned literal and
pointer pool, including the Thumb pointer to `compare_uni_maps`; it is not a
twelfth callable body.  The analyzer requires the exact nine-word pool and its
whole SHA-256, so a code/data reinterpretation or address drift fails closed.

## Source admission

The isolated production-capable source candidate is the upstream 2.9.1
single-object translation unit `src/psnames/psnames.c`, pinned to tag
`VER-2-9-1` and commit `86bc8a95056c97a810986434a3f268cbe67f2902`.
The complete seven-file PSNames `.c`/`.h` inventory is 296,242 bytes.  Focused
verification compiles the unmodified unit for Cortex-M55 Thumb hard-float with
warnings as errors and checks the output is an ARM ELF relocatable object.

This proves source availability and target compilation, not original IAR
compiler-byte identity.  No authenticated callsite, relocation, placement, or
core overlay route was found or added.  Font payload/face-path configuration,
task stack and worst-case execution time, and authorized hardware rendering
are still explicit release gates.  No hardware behavior is claimed.

## Reproduction

```sh
python3 g2/tools/analyze_g2_freetype_psnames_function_map.py --check-manifest
python3 g2/tools/analyze_g2_freetype_psnames_source_admission.py --check-manifest
python3 -m unittest \
  g2.tests.test_analyze_g2_freetype_psnames_function_map \
  g2.tests.test_freetype_psnames_source_admission
```
