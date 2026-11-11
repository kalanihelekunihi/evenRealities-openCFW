# Wave 12: evidence and removals

## (0) Why apollo-main GUESS went from 81 to 17
All 64 removals were in g2c_nema_vg_path.c (72 -> 8), compared against `.waves/w10-bak/g2c_nema_vg_path.c.w11start`. Each removed marker was a `/* GUESS/residual */` comment attached to an extraout_/unaff_ declaration or a pfVar25 extraout assignment. It went away when wave 11 recovered that nvg value, so every removal is nvg-incidental. None came from a regex change.

| function | removed | wave-11 evidence comment (line) |
|---|---|---|
| arc_to_51a8ec | 3 | 4964, 5008 |
| draw_fill_51d2e0 | 12 (9 decl + 3 pfVar25) | 7319, 7403, 7545 |
| draw_stroke_51f798 | 37 | 8485 |
| path_bounds_5639e8 | 5 | 12009 |
| arc_build_564974 | 4 | 12488 |
| arc_draw_5653a0 | 1 | 13354 |
| draw_path_inner_5657d8 | 2 | 13418 |

Every function has a citation, so nothing was restored. The wave 11 statement "GUESS not worked" was wrong.

## (1) Bootloader
- Stock f89a4c46 is 148599 B at 0x410000..0x434477, and apollo-main starts at 0x438000.
- Cause of the overflow:
  - unused upstream code (gc-sections drops 486 sections, 226 of them .text)
  - an orphaned .boot_vectors section placed at about 0x439964
- Fix:
  - MRAM LENGTH set to 0x28000
  - KEEP(.boot_vectors) placed first, at 0x410000
  - KEEP(.boot_* .event_* .cmdq_*)
  - --gc-sections
- Result: text 157364 (+8765 vs stock, clang -O2 vs IAR), ending at about 0x4366b4.
- Negative test: linking without gc now fails with "region MRAM overflowed by 8060 bytes".

## Other targets (flags, unchanged; no datasheets in the repo)
- touch: our FLASH origin is 0 with length 0x10000. The stock image base is 0x3300.
- codec-a: our XIP origin is 0x18000000. The stock image_a_xip base is 0x10203004.
- codec-b: our IRAM origin is 0x10000000. The stock image_b_sram base is 0x10003000.
- em9305: NVM 0x302400 + 0x80000. Stock is 211948 B and ours is a 325624 B bin. It fits, but the length is not datasheet-verified.
- apollo-main: MRAM 0x438000 + 0x3C8000. _etext is 0x78087c.

## (2) FPSCR
- path.c: in_fpscr is now 0, and every compare is cited inline. Runtime evidence: FPSCR=0x02040000 (RN) at 0x5e428c, and the only other vmsr writers are 0x4d42e0/ec and 0x59d2ea/f6, which handle exception bits.
- FLAG: draw_fill keeps the uVar4/uVar12/uVar13/uVar14 carrier chains, now rooted at 0. They are not nvg tokens but are still undocumented.
- display_lv: unaff_d9 became d9_pair=0 (vlive at 0x561c74: s18/s19 have no def). 6 ge-pairs were rewritten, with a banner citing 0x56280a..0x56286e and 0x562be6..0x562c1c. in_fpscr went 77 -> 53. These remaining sites derive from a real vmrs (pp306_fpscr) and are not uninitialized.

## (3) Markers
- Removed with evidence:
  - g2c_first_party_data.c GUESS: stock pool 0x47bc10 = 0x20067a30, which is the same object as stock word 0x78ee60.
  - g2c_ghidra_shim.h GUESS "FPSCR rounding ignored": RN evidence above.
- Kept:
  - iar_stdout.c weak x3: faithful weak-undefined refs (stock NOP.W at 0x5f9fb8)
  - notify_app_icon.c "stub": a regex hit on the doc word "placeholders"; not reworded
  - stack0x/CONCAT31 GUESS in path.c
  - generic header GUESS
  - all 3 UNVERIFIED: display_lv still has nvg, and path.c still has GUESS residuals
