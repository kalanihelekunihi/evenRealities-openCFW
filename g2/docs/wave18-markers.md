# Wave 18: markers and evidence

Stock images: apollo /tmp/apm.bin (base 0x438000); em9305 g2/blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin (sha256 91a38f7f..., the same in all 18 official packages); codec corpus g2/research/corpus/codec/ghidra/open-2026-09-29.

## (1) em9305 linker script (g2/src/em9305/link/g2-em9305.ld)
- The plaintext rodata table at 0x335874..0x335890 references 0x80ff54, which is inside 0x80fe20..0x810000. That refutes the earlier claim that the highest stock reference is 0x80fe1c.
- The stock SP was not found. The code region does not decode as plain ARC (probably encrypted), and the ROM likely sets the SP. FLAG/UNVERIFIED stays.
- Added pins: g2_em_myapp_ao at 0x801970 (36 B) and g2_em_myapp_queue at 0x80f97c (16 B), with an ASSERT. GUESS: the addresses come from myapp.c:54/56 and were not re-derived from stock.
- Only 8 B are left in the window (.sdata g2_em_qf_next_priority, .sbss g2_em_app_start_callback).

## (2) codec-a section ownership (g2/src/codec/link/g2-codec-a.ld)
- .stage2 now takes .text.combine, .text.special, .text.unlink_free and .text.parse_argument (stock 0x100076c4/0x100076f4, 0x10007730/0x10007930, 0x10007240, 0x10005628).
- .res.text now takes g2_codec_critical_save/restore, header_sync, timestamp, queue_enqueue and gx8002_cache_lines (stock 0x10025560, 0x1002556c, 0x10025664, 0x10025930/0x1002585c, 0x100261b8, 0x10025608/0x100256c0; each has image_a_sram/decomp/<addr>.c).
- Still FLAG/GUESS in XIP: libgcc/compiler-rt, csky_* DSP, crc32, __fe_*, and the 0x102xxxxx glue.

## (3) ABS<2 r5/r6 modelling (vg_path)
- Stock 0x51e7c8 (r6) and 0x51dcd8/0x51dd34 (r5). The flag is now computed once as the stock register and tested directly. The bug where a stale bVar15 was tested is fixed.

## (4) vg_path carriers. NAN( tokens went from 215 to 158 (one is the #define). Rewritten sites:
- stroke_join 0x517aca/0x517ad8 (r4 GE-or) and 0x517b72 (ittt gt / vldrgt chain).
- arc_seg2 0x51c080/0x51c0a2 (movge r5; cmp r5 at 0x51c0d0).
- arc_seg3 0x51cd78/0x51cd9e (cmp r5 at 0x51cdcc).
- draw_stroke 0x51fefc/0x51ff0e (r4 at 0x51ff18; test at 0x51ffe4).
- stroke_path 0x518474/0x518482 and 0x51891c/0x51892e. fill_path 0x519834/0x519842 and 0x519cdc/0x519cee. These four are matched by site order within the function.
- vector_shape_draw 0x520a84..0x520ab6 (4 GE vs vcvt [r1+0x10]) and 0x520b00..0x520b6a (8 LT vs 1535.0001f, literal at 0x520c68).
- Remaining (not done): 157 NAN tokens in vector_shape_draw, arc_draw and draw_path_inner (epsilon SUB41 and fpscr-bit idioms) and 43 g2c_fpscr_* uses. The vg_path UNVERIFIED header stays.

## (5) apollo stub/unverified/inferred/guess
No change. notify_app_icon.c:5 means the function names are placeholders; removing it would need the real names, which no stock string provides. The other markers have no new evidence.

## (6) 8-byte text growth
Confirmed: it is not __LINE__. It is __FILE__ strings in generated LVGL units that embed the compose dir name ("g2c-w17b" is one character longer than "g2c-w17"). Six objects each gained 1 B, rounded to 8 B. The W18 builds use same-length dir names.
