# Wave 13 — loadable image origins/regions

Stock reference: `g2/blobs/official/g2-2.2.6.10/`. Every region length is now bounded,
so an overflow fails the link (tested: touch without gc → `FLASH overflowed by 5456 bytes`;
em9305 with NVM shortened to stock 210888 B → `NVM overflowed by 114736 bytes`;
codec-a with the earlier oversized resident text → overlap error against pinned stock data at 0x100264e4).

| target | origin | region (evidence) | our size | stock size |
|---|---|---|---|---|
| touch | FLASH 0x3300, RAMVEC 0x20000400 | 0x3300..0x10000 (CY8C4046 64 KB flash); RAM 0x20000f58..0x20002000 (8 KB SRAM, SP 0x20002000) | 26,984 B bin (text 26972 / data 12 / bss 272), with `--gc-sections` | 34,428 B payload (0x867C) |
| em9305 | NVM 0x302400 | 0x302400..0x380000 (DS Table 5-1 flash 0x300000..0x37FFFF; no FOTA updater record in stock pkg); DRAM 0x800000..0x810000 | 325,624 B | 210,888 B app record |
| codec-a | RES 0x10023400 (vectors), entry 0x10023500; XIP 0x10203004; STAGE1 0x10000000; STAGE2 0x10002800 | RES to 0x10034000, stock data pinned from 0x100264e4; XIP to 0x10280000 (512 KB NOR, XIP base inferred) | RES text 0x10023400..0x100261f0 (+data 0xe0 at 0x10026d7c), XIP 47,364 B, stage1 6,484 B, stage2 21,156 B | RES 14,716 / XIP 36,484 / stage1 10,240 / stage2 27,964 |
| codec-b | 0x10003000 vectors, reset 0x10003100 (ASSERTed) | IRAM to 0x10034000; bss confined to stock clear span 0x20017090..0x2002d79c; retained 0x2002d79c..0x2002d7b8 pinned | 89,112 B bin | 82,060 B |

## Evidence per target
- touch: FWPK header (record type 3, size 0x8680 at 0x20, CRC-32C), stock vectors decode only at 0x3300,
  apollo-main DFU template 0x78c098 = `01 00330000`, stock Reset 0x4674 copies 0xC0-byte vectors to
  0x20000400 and sets VTOR. `.waves/w13/pack_touch_fwpk.py --selftest` re-creates stock FWPK byte-exact.
- em9305: EM9305 DS v4.5.3 Table 5-1; stock rodata pointer tables 0x3357a8 = {0x802d20,0x802fe0,0x8032a0}
  and 0x3357b4 = {0x8035dc,0x802a60,0x80389c} → address-named `.bss.opencfw_*` sections pinned there.
- codec: corpus RUN.json bases/sizes; memory-map.md; GX8002 datasheet 208 KB SRAM; stock CRT 0x10003128 bss span.

## Fit work / rejected options
- touch: `-Wl,--gc-sections` (profile already -ffunction-sections). Fits.
- em9305: `-ffunction-sections -fdata-sections` + gc **rejected**: it dropped the image to 7,272 B because most
  code is reached only through stock absolute addresses/ROM tables, so gc is unsound. `-Os` **rejected**: GCC emits
  memcpy calls the freestanding image doesn't provide (link fails). Kept -O2, no gc: fits the region, 1.54x stock.
- codec-a: five asm units used plain `.text`, mixing stage1 init and resident trap/irq into one input section,
  which overflowed resident text by 0x30c into stock data. Gave them named sections (placement only, code unchanged).

## FLAGS (unverified)
- touch: stock absolute-addressed RAM init data/copy tables not reproduced; stack size not recovered.
- em9305: linker small data (.sdata/.sbss/.bss < 0x40 B) at 0x80fe20..0x810000, above max stock-referenced RAM 0x80fe1c — free window UNVERIFIED.
- codec: 208 KB SRAM fully mapped at 0x10000000 UNVERIFIED; XIP base 0x10200000 inferred. codec-a libgcc /
  g2_codec_* glue / unowned rodata ownership (XIP) is a GUESS; `.gx8002.sram.*` data placed after 0x10026d7c (past stock image end).
- codec-b is 7,052 B over stock and runs to 0x10018c18; if 0x1xxxxxxx and 0x2xxxxxxx alias the same SRAM it would overlap the stock bss start 0x20017090.
