# Wave 17: sign tests, draw_fill carriers, stack residuals

## Ledger
- The stray root C-RECONSTRUCTION-PROGRESS.md (Waves 12-16) was merged into this file and deleted.

## display_lv_init_children.c
- Each of the 10 batch-3 sign tests has its own stock citation: 0x563106, 0x563188, 0x5632ec, 0x56336a, 0x563400, 0x563446, 0x5634e4, 0x56352e, 0x563588, 0x5635da. Pattern: vcmp #0; ite gt; vmov +/-1.0. Matched by order and sqrt-operand shape (flagged).
- The last NAN test was rewritten as `!(a >= b)` (stock 0x562ab2, it lt). The NAN macro was removed, and nvg_leftover went 1 -> 0.

## g2c_nema_vg_path.c
### draw_fill_51d2e0
- All FPSCR-carrier compares were rewritten as direct compares, each citing its branch condition (see the in-code comments).
- Decompiler bugs fixed:
  - NaN-only tests at 0x51dafa and 0x51df2e.
  - 8 zero-pair sites: the stock code copies the value, not the address.
  - sp+0 out0 slot (fStack_2d0).
- The uVar4 0xfffffff masks were removed. uVar14 is now only a stencil handle.

### vector_shape_draw_5202ec
- Fixed out-of-bounds UB: 3 scalar residuals were indexed `i*8`.
- Stock frame: push 9 regs, sub sp,#4, vpush d8-d15, sub sp,#104 (0x5202ec-0x5202f8). That puts sp at entry-0xd0.
- The 3 residuals and afStack_c4 (sp+0xc) now share one `uint g2c_sp_frame_5202ec[26]`.

### draw_box_shadow_540036
- Fixed a real semantic bug: stock 0x540938-0x540948 memcpy's 3 bytes from dsc+0x20 into [sp] and passes [sp] as color_resolve arg0. The decompiled C passed uVar5 (the old [sp] value) and discarded the memcpy.

### path_cmd_5156b8
- The two CONCAT31 GUESS sites were replaced with byte stores to sp+4: stock 0x515b22 and 0x516588 `strb.w sl,[sp,#4]`, read back as bytes at 0x515b8a and 0x5165ee. The old `(float)CONCAT31` was a value conversion, not a byte merge.

## Not done (still flagged; no evidence recovered)
- apollo guess (8):
  - file headers in g2c_ble_leaves, am_hal_clkmgr_g2, g2c_vectors, g2c_nema_leaves, g2c_ghidra_shim.h, gpu_patch.h
  - the vg_path file header (about 240 FPSCR/carrier sites remain outside draw_fill)
  - .ld MRAM/SSRAM size
- stub 1 (notify_app_icon), unverified 2 (vg_path header), inferred 11.
- .ld raw_decompile 1: this is the provenance line "Ghidra 12.1.4" in the memory-map note, a scanner false positive. Left as is.
- em9305 .ld FLAG/UNVERIFIED (RAMHI 0x80fe20..0x810000 unused by stock): the stock em9305 binary was not at hand this wave. Next check: grep it for 0x80fe20-0x810000 literals and the initial SP (the stack may sit there).
- codec-a .ld FLAG/GUESS (stage1/2 and generic .text ownership): not resolved.

## Builds (0 undefined each)
| Target | Output | Notes |
|---|---|---|
| apollo-main | g2/build/g2c-w17-final-apollo-main | from g2c-w17b-apollo-main; text 3,481,241 / data 168,651 / bss 1,999,768 |
| apollo-bootloader | g2/build/g2c-w17-final-apollo-bootloader | identical to w15 |
| em9305 | g2/build/g2c-w17-final-em9305 | |
| codec-a | g2/build/g2c-w17-final-codec-a | |
| codec-b | g2/build/g2c-w17-final-codec-b | |
| touch | g2/build/g2c-w17-final-touch | |

Inventory: g2/docs/inventory-w17.json
