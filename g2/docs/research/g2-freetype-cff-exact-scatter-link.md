# G2 FreeType CFF exact scatter link

SPDX-License-Identifier: MIT

This software-only tranche final-links the selected complete FreeType 2.9.1
CFF `-Oz` objects into two authenticated Apollo-application intervals.  It
does not modify the core builder, write a component/package, apply the module
pointer patch, sign, flash, or claim hardware behavior.

## Placement

The layout needs only the 16,924-byte stock CFF envelope and the 4,422-byte
free application tail.  It consumes none of the 360 scattered table/callback
bytes, no bootloader headroom, and no protected update bytes.  Both locations
and the guarded class-pointer slot are in Apollo package entry 6, so this plan
has zero cross-entry mutations.

| Profile | Range | Contents | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| Apple | `[0x005ABEF8,0x005AD22E)` | rodata/class/tables | 4,918 | `af26a89e31bd570876eb6525feca32796170b4e1d126d30c7c9a475ca5c87761` |
| Apple | `[0x005AD230,0x005AFEA6)` | rooted text | 11,382 | `875b144a03be6535cbda9d925aaec7db2a17f088376d2f300e0e38c2b154bd26` |
| Apple | `[0x007FCEC0,0x007FDEC4)` | seven atomic text sections | 4,100 | `a27cfc1302153a5bc2f2e2253d7d3e9eb8dd75fdae0c66426c898bc46376ccb0` |
| Apple | `[0x007FDEC4,0x007FDED4)` | unwind index | 16 | `c7f38a59fd9b7e9eca1ba1e07f3de5b1c3b5f7eb5b6322638f42f668c62abd66` |
| Linux | `[0x005ABEF8,0x005AD22E)` | rodata/class/tables | 4,918 | `5c2f3b649f62d1d86f3c900498f4ba679dc9b0eb3bb46cf184e27fa5ccb268a2` |
| Linux | `[0x005AD230,0x005AFE6A)` | rooted text | 11,322 | `257e531397359a887481018b7679a280250714be8bc07b56003900969cf57ee4` |
| Linux | `[0x007FCEC0,0x007FDEC4)` | eight atomic text sections | 4,100 | `632fe6b5d869358279803fa7bb07f6717b5c2ab5706fafd38ac40a30e873f2f1` |
| Linux | `[0x007FDEC4,0x007FDED4)` | unwind index | 16 | `c7f38a59fd9b7e9eca1ba1e07f3de5b1c3b5f7eb5b6322638f42f668c62abd66` |

Apple consumes 20,416 loadable bytes and leaves 930 bytes across the two
intervals; Linux consumes 20,356 and leaves 990.  Six bytes before the aligned
tail text and 300 bytes after the unwind index remain unused.  The stock
envelope retains 622 Apple or 682 Linux bytes after the final section.

The packer enumerates every input `.text.*` section and its alignment.  A
deterministic largest-first selection places exactly 4,100 aligned input bytes
in the tail; every other text section and all read-only input sections are
listed explicitly in the generated linker script.  The final ELF has only the
four allocated output sections above, so no orphan allocated section silently
escapes the reviewed intervals.

## Relocations, roots, and patch

Both final ELFs have zero undefined symbols and zero relocations.  All 36
bindings are exact, including the authenticated `__aeabi_memcpy` redirect at
`0x00439BE4`.  The widest address domain is 3,949,296 bytes, inside the Thumb
call/jump range, and LLD generates no veneer.  Every one of the 58
address-taking callback records resolves to the expected relocated Thumb
symbol, covering 55 distinct callback targets.  The 81 materialized complete
map symbols remain present; the size experiment independently accounts for
the other 20 through clang inline proofs.

`cff_driver_class` is a 96-byte object at `0x005AC014`.  The exact guarded
registration contract is:

- patch address: `0x0073EF00`;
- required current bytes: `74 cb 6d 00` (`0x006DCB74`);
- candidate bytes: `14 c0 5a 00` (`0x005AC014`); and
- compare-before-write and same-entry atomic component generation are required.

The patch is not applied.  The scatter proof's pinned root-level package ends
at `0x007FCEBA` and would grow 4,122 bytes, but it is not today's canonical
profile base.  Current canonical Apple/Linux entry 6 ends at `0x007ECA44` /
`0x007B9F10`; reaching the fixed `0x007FDED4` end therefore requires 70,800 /
278,468 bytes of profile-specific growth, including authenticated `0xFF` fill.
A production component must bind those base bytes and regenerate the Apollo
entry length, CRC, flash plan, and package receipts.  That component-builder
integration is not present, so production routing and firmware-image emission
remain false even though the dual-profile scatter link itself is exact and
reproducible.

Font payload identity, heap behavior under real fonts, task stack, WCET,
compiler-byte identity, and physical rendering remain unavailable gates.

Run the replay and hostile checks with:

```sh
cd g2
python3 tools/analyze_g2_freetype_cff_scatter_link.py --check-manifest
python3 -m unittest -v tests/test_freetype_cff_scatter_link.py
```
