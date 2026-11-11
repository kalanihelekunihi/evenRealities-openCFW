# Wave 16 — apollo-main FPSCR rewrite

File: g2/src/apollo-main/ui/lvgl/display-lv/display_lv_init_children.c
(audio_uart_nema_vg_path_process_561c68, stock 0x561c68, ota_s200 2.2.6.10, base 0x438000).
Script: .waves/w16/fp_rewrite.py batches 1-5. Backup: .waves/w13-bak/display_lv_init_children.c.w16pre.

- Batches 1-2: cubic/quad extrema (0x56295c, 0x5629a6/b0, 0x562908..0x56292a, 0x562a30, 0x562b22,
  0x562c4c..0x562c74, 0x562ce6..0x562d06).
- Batch 3: arc radius |r|<1e-5 (0x562d86/0x562d9c, bmi.w 0x563802); fVar24==0 (0x562e68, beq.w 0x56385a);
  10 sign tests (GT/LE) in the vcmp #0.0 / ite gt region 0x563106..0x5635da. They were mapped by regex and
  matched to the region, NOT one by one to an address (flagged).
- Batch 4: angle ==0/180 (0x562f90/0x562fa4) and ==90/270 (0x562fb4/0x562fca).
- Batch 5: closepath dx==0 && dy==0 (0x5623b6/0x5623cc, beq.n 0x562452).
- Removed: 13 dead `& 0xfffffff` masks (low 28 bits never read), pp306_fpscr(), and the g2c_fpscr_* helpers with their GUESS banner.
  The UNVERIFIED header was replaced with an evidence note.
- in_fpscr went from 53 to 0. The file compiles with rc=0. apollo-main relinks with 0 undefined: text 3,481,161 / data 168,651 / bss 1,999,768.
