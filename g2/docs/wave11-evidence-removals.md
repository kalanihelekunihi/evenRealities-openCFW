# Wave 11 evidence removals (2026-10-26)

## Corrections
- Wave 10 said apollo-main never had a final link. That was wrong. `.waves/link.sh` had produced `g2/build/g2c-link/g2-apollo-main.elf` from the g2c-wave objects. `.waves/link-final.sh` simply had no apollo-main case. The current relink is `g2/build/g2c-w11c-final-apollo-main/g2-apollo-main.elf`: rc 0, 0 undefined.
- FLAG: bootloader `.text` runs from 0x410000 to about 0x439f78, past the apollo-main base 0x438000. The MRAM LENGTH 0x40000 in the .ld allows it, but the two images would overlap on the device. This is not resolved.

## Bootloader
- `link/g2-apollo-bootloader.ld`: added the missing closing `}` of SECTIONS.
- `link-final.sh`: the 3 untyped ABS ROM symbols are weakened (`objcopy --weaken-symbol`), so the typed `.thumb_set` ROM object wins.

## Touch
- `vendor/cycfg_peripherals.h`: the EXT_FRM_START stub defines are removed. Their only use is `cy_capsense_sensing_lp.c:3121` (infineon-capsense-v5), under `CY_CAPSENSE_EXT_FRM_START_EN`, which is DISABLE (`cycfg_capsense_defines.h:57`).
- `glue/touch_cybsp.c`: 2 weak fallbacks removed. The strong defs are mtb-pdl-cat2 35f1714 `cy_syslib.c:162/175`, at map addresses 0x8e84/0x8e98.

## Strengthened Wave 9 citations
- `a6ng_panel.c`: the citation is now stock 0x5bcc18 (handle *0x20074510, fb *0x20074514, mask 0x7fc00 @0x5bd31c, clamps 0x27f/0x1df). The only bl is 0x4910f4, so stock has no QSPI write.
- `g2_als.h`: all 29 entries match the corpus. The 10 DRV_ALS names are proven via string → pool word → loader.
- `prvCommand_teleprompt.c`: the citation is now stock 0x5827b6..0x5827ce (str 0x741ec0, pool 0x5828e4, bl 0x4733ee, then r0=0x109 and bl 0x464b2e, return 0).

## g2c_nema_vg_path.c (tool: `.waves/w11/vlive.py`, stock VFP read-before-write)
- arc_to_51a8ec: removed the two callee-leftover s1 values (s1 redefined by ite at 0x51b03c/0x51b0bc). The d8 entry value is dead: s17 is written by vabspl at 0x51a91c on the bpl-taken path, and vlive from 0x51a8f6 reports none.
- draw_fill_51d2e0: callee-leftover values dead at 0x51ea88, 0x51eb72, 0x51ed3e.
- draw_stroke_51f798: all 37 removed; dead after each bl, and at 0x51fa72.
- path_bounds_5639e8: s0-s4 dead from 0x563f20; arc_seg2 0x51bf7c does not read them.
- arc_build_564974: dead after the bl at 0x564b04/0x564cb0/0x564e0c.
- arc_draw_5653a0: s3 is dead after the bl at 0x5655c0.
- draw_path_inner_5657d8: d10 entry value is dead (vlive from 0x5657e0). The d15 entry value is only stored to [sp+88] at 0x565802, then overwritten at 0x5662c2/c6 before use. Renamed to d10_pair/d15_pair = 0.

ASSUMPTION (vlive): an indirect `blx reg` takes no VFP args. These calls are counted and printed per run.
Wave 11 vlive fix: an all-then IT block followed by a same-condition branch kills the IT writes on the taken edge.

## Remaining
- in_fpscr chains in path draw_fill and path_bounds, plus display_lv (85 in_fpscr, 10 d9). Some chains read FPSCR bits 24..27 (`>>0x18`) from the incoming value, so they cannot be removed by masking. They need a per-site vcmp/vmrs rewrite.
- 3 UNVERIFIED banners remain, because no file has reached 0 nvg.
