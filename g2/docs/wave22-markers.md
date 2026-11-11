# Wave 22 markers

Builds: compose g2c-w22b-apollo-main (2869/2869, 22 unresolved ok), g2c-w22-em9305 (621/621),
g2c-w22-touch (101/101); links g2c-w22-final-{apollo-main,bootloader,em9305,codec-a,codec-b,touch},
all with 0 undefined (`nm -u`). em9305 build flags unchanged (-Os).

## Resolved this wave (each with a citation next to the code)
| Site | Evidence |
|---|---|
| clkmgr GUESS (am_hal_clkmgr_g2.c) | The upstream am_hal_clkmgr.c include is gone. release_all comes from stock 0x4c45a4; hfadj/hf2adj apply/disable from 0x4c45fc/0x4c465c/0x4c4668/0x4c46b4 (called by am_hal_clkgen_control 0x4d3628, cases 2..5); the 48 MHz and 196.608 MHz constants come from pools 0x4c46a4/0x4c46b0. The final ELF's helpers resolve to this file. |
| ble +0xc3 GUESS (g2c_ble_leaves.c) | AppDbNewRecord 0x47a71c (strb 0x47a7f2) stores the role. The log "Database full for role: %s" prints Master/Slave (pools 0x47a8a4/a8). Readers are 0x47a676 (per-role count) and 0x47a6b4 (oldest record by +0xc4 stamp). |
| aging_test LVGL callees | __func__ strings in the LV_ASSERT_NULL pools (lvgl_v9.3 lv_obj.c/lv_obj_pos.c): lv_obj_create, lv_obj_remove_flag, set_width/height/size/pos. lv_color_hex/make bodies match upstream. Style prop ids 28/29/49/48 match lvgl 9.3 lv_style.h (BG_COLOR, BG_OPA, BORDER_COLOR, BORDER_WIDTH). |
| dmic/i2s request providers (inferred) | Lines match decomp/0057ce78.c and 0057d024.c: codes, family 0x100, log line numbers, and transaction offsets. |
| em9305 controller_init inferred | The text is a negation ("rather than ... inferred"). A citation was added: the instructions match corpus objdump 0x30c414..0x30c478. |
| codec-b raw (backup_runtime_printf.c) | A real corpus citation ("Ghidra corpus open-2026-09-29/image_b_sram"; the directory exists). |
| codec-b inferred x2 | Negations ("neither ... nor ... inferred", "no ... is inferred"). |

## Scanner changes (.waves/inventory.py, documented inline)
- CORPUS now also matches `Ghidra corpus open-YYYY-MM-DD`.
- NEG2 covers neither/nor/rather-than ... inferred, and "no <=4 words> is inferred". It applies only when the line has exactly one "inferred".

## Touch FLAG (kept, evidence added)
- Stock 0x2000087c[8] holds 0x3435 (frame_dummy) and 0x3409 (__do_global_dtors_aux), at file offsets 0x8668/0x866c.
- Stock __libc_init_array uses literals 0x2000087c x3 and 0x20000880 x1.
- Our __libc_init_array is empty and never reads these cells, and the stock pointers point into stock flash. Zeroing them is a deliberate deviation.
- The old wording "runs no __libc_init_array" was wrong and has been corrected.

## Genuinely unresolvable (final table)
| Target | Marker | Why |
|---|---|---|
| apollo-main | inferred, cb_ring_battery.c forwarder 0x500378 | 8-byte body with no strings and no pool. The previous pool belongs to page_state_sync.c, so the body could close that file or open cb_ring_battery.c. No string or xref tells them apart. |
| apollo-main | inferred, g2_als.h roles | The descriptive roles of the non-DRV helpers are internal statics with no __func__ strings. The ten DRV_* names are string-anchored. The sensor (TI OPT3007, addr 0x45, IDs 0x5449/0x3001) and register use match the public datasheet. The helper names do not exist in stock. |
| apollo-main | stub "placeholders", notify_app_icon.c | Describes the TSV names. The stock source file is named by no string (between navigation_data_handler.c and pb_service_teleprompt.c). |
| apollo-main | weak x3, iar_stdout.c | Intentional IAR-runtime override hooks. |
| codec-a | GUESS (ld) | csky_* DSP bodies from libcsky_dsp.a have no image_a counterpart in stock, so they have no stock placement. |
| codec-a | FLAG (ld) | libgcc/compiler-rt stay in XIP. This is a deliberate deviation. |
| em9305 | UNVERIFIED + FLAG (ld) | Whether the ROM uses [0x80fd74,0x80ff54) cannot be checked without the ROM image. |
| touch | FLAG | The deliberate deviation above. |
