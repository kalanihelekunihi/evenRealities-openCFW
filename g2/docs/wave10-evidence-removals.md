# Wave 10 evidence-cited marker removals

Stock reference: g2-2.2.6.10 `ota_s200_firmware_ota.bin` minus its 32-byte preamble, base 0x438000. Touch reference: 18 stock `firmware_touch.bin` images.

## Touch: CapSense UpdateThresholds_Lib / CalculateRawTarget (2 GUESS/stub removed)
- (a) The marker was a GUESS stub in `g2/src/touch/glue/touch_vectors_and_capsense_tail.c`.
- (b) The closed Infineon `libcy_capsense.a` 5.0.0.6806 is public (lib sha256 ca1187b3…). Its `UpdateThresholds_Lib` is 70 bytes and position-independent. That byte sequence, and every SOFTFP lib variant probed, is absent from all 18 stock touch images. The only callers are `Cy_CapSense_DpUpdateThresholds` (cy_capsense_processing.c v5:813) and `Cy_CapSense_CdacSuccessAppr` (cy_capsense_sensing_lp.c v5:2209). Neither is reachable in the w9 final ELF.
- (c) Fix: both stubs were deleted and the two dead callers are gc-stripped through `retain` in `g2/src/sources.json`. The lib is not linked: the license (Cypress EULA §2b) would allow it, but it would add code that is not in stock. `TuInitialize` is kept. text went from 58044 to 57624.

## apollo-main `g2c_nema_vg_path.c` (nvg 344→262, GUESS 90→81 across apollo-main)
- FPSCR RMode: stock writes FPSCR once, at 0x5e428c, with the value 0x02040000 (RMode=RN). The other writers (0x4d42e0/ec, 0x59d2ea/f6) only clear exception bits and restore. So 21 `(in_fpscr>>0x16)&3` became `G2C_FPSCR_RMODE_RN` (0).
- `arc_seg3_51c5ec`: 6 extraout values removed, because stock reloads s1/s2/s4 via vldreq at 0x51c708/0x51c70c/0x51c732 before any read. NZCV synthesis was replaced by direct compares: bhi at 0x51c850 became `!(f<=0)`, which also fixes NaN handling; gt at 0x51c80e became `f>0`.
- `shape_draw_5202ec`: the N==V chain became ge/lt compares, matching vcmp/vmrs at 0x520352/364/372/380.
- Three unused local `in_fpscr` declarations removed (old lines 9235, 11288, 11744). The file-scope static `in_fpscr` was also removed. All remaining uses are function locals.
- `near_5177a4`: in_s1/in_s3 are |*a| and |*b|, from vcmp #0 / ite mi vnegmi/vmovpl at 0x5177ac..0x5177d0, and min at 0x5177d4. The blt at 0x517804 matches `<=` for NaN.
- `path_cmd_5156b8`: unaff_r6 (local and static GUESS) is dominated by its assignment from literal DAT_00516230 (= `audio_uart_nema_vg_context_cell`), per stock decomp 005156b8.c:60/71.

## Not done this wave
- `draw_fill_51d2e0` and `path_bounds_5639e8` in_fpscr chains, plus their extraout values.
- The stack0x/unaff_d8/d10/d15 residuals.
- The display_lv FP chains (85 in_fpscr, 10 unaff_d9).
- The other 81 apollo GUESS markers.
- The 3 UNVERIFIED banners.
