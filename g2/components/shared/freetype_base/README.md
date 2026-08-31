# G2 FreeType base community source

SPDX-License-Identifier: FTL

This component admits the complete retained FreeType 2.9.1 base envelope at
`[0x005242FC,0x005293C0)`. It contains 182 source callables and 20,442 callable
bytes. The remaining 234 bytes are pinned literal/pointer data pools and four
alignment bytes, so all 20,676 physical bytes are classified and no callable
bytes remain unresolved.

The earlier base candidate remains visible as a narrower evidence tier: its
83-function cluster plus seven Mac/resource-fork mechanics covers 90 functions
and 9,736 bytes. The complete map adds 92 functions and 10,706 callable bytes.
It also corrects a Ghidra artifact: `0x005292C8` is an internal basic block of
the 42-byte `ft_mem_strcpyn` body at `0x005292BC`, not another source function.
Five source-ordered callbacks missed by Ghidra were recovered from their
callback/table use and bounded Thumb bodies.

The maintained adapter exposes the recovered caller-owned allocator lifecycle:

```text
allocate FT_MemoryRec -> FT_New_Library -> FT_Add_Default_Modules
```

It checks the exact ten-module G2 set before publishing the library. Its face
boundary preserves upstream autodetection and also offers explicit TrueType-only
and CFF-only modes through `FT_OPEN_DRIVER`. The caller retains every memory
font buffer until its face is released.

This is source admission, not compiler-byte identity or production placement.
Stock has no safely assignable `FT_Done_FreeType` entry, so maintained firmware
uses the public `FT_Done_Library` symmetry before releasing its separately
allocated memory record. The component is not referenced by the Apollo overlay
or component builder.

The upstream `ftbase.c`, `ftinit.c`, and `ftbitmap.c` translation units and
the maintained adapter are compiled in the focused gate for
`arm-none-eabi`, Cortex-M55 Thumb hard-float, short enums, freestanding C11,
and warnings-as-errors. This establishes source portability, not IAR output
identity or authenticated stock placement.

Run the software-only checks with:

```sh
cd g2
python3 tools/analyze_g2_freetype_base_source_admission.py --check-manifest
python3 -m unittest -v tests.test_runtime_freetype_base_admission
```

No hardware was accessed. IAR code generation, placement, authenticated font
payloads, stack/WCET qualification, and authorized rendering evidence remain
separate gates.
