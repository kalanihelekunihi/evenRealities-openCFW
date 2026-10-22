/**
 * @file lv_conf.h
 * Proven G2 LVGL configuration subset for openCFW.
 *
 * This is intentionally incomplete.  Every definition below is backed by the
 * authenticated G2 2.2.6.10 image.  Undefined LVGL options are unresolved,
 * not inferred to equal upstream defaults.  Do not use this header for a
 * production link until the source-integration gate in lvgl_g2_abi.json closes.
 */

#ifndef LV_CONF_H
#define LV_CONF_H

#define LV_COLOR_DEPTH 8

#define LV_USE_OS LV_OS_FREERTOS

#define LV_USE_FREETYPE 1
#define LV_USE_FLEX 1
#define LV_USE_GRID 1
#define LV_USE_FS_LITTLEFS 1
#define LV_USE_BMP 1
#define LV_USE_SPAN 1
#define LV_USE_OBJ_ID_BUILTIN 1

#define LV_USE_DRAW_AMBIQ 1
#define LV_USE_AMBIQ_VG 1
#define LV_AMBIQ_COMMAND_LIST_SECTOR 100
#define LV_AMBIQ_COMMAND_LIST_SECTOR_SIZE 1024

/* Stock powers the GPU on with retained NemaGFX/NemaVG context. */
#define NEMAGFX_POWER_SAVE 1

#define LV_DRAW_SW_COMPLEX 0
#define LV_USE_STDLIB_MALLOC LV_STDLIB_CUSTOM

#define LV_USE_LOG 1
#define LV_LOG_LEVEL LV_LOG_LEVEL_WARN
#define LV_USE_ASSERT_NULL 1
#define LV_BIG_ENDIAN_SYSTEM 0

/* Recovered 2026-10-21 from 2.2.6.10 code shape (see g2/docs/reference/findings-hardware-drivers.md):
 * float points in lv_draw_line_dsc_t and s0-passed coordinates (0x5C9344);
 * inline lv_bidi_calculate_align copy (0x489ED4); cell text at +8 (lv_table);
 * buttonmatrix default map "Btn1".."Btn5" (0x5C1A74); 0x24-byte class descriptors. */
#define LV_USE_FLOAT 1
#define LV_USE_BIDI 0
#define LV_USE_USER_DATA 1
#define LV_WIDGETS_HAS_DEFAULT_VALUE 1
#define LV_USE_OBJ_PROPERTY 0

/* Recovered 2026-10-21: stock LV_ASSERT_HANDLER is an endless store of 0 to
 * address 0xFFFFFFFF (e.g. 0x5C10FE..0x5C1106 in lv_draw_arc). */
#define LV_ASSERT_HANDLER_INCLUDE <stdint.h>
#define LV_ASSERT_HANDLER while(1) { *(volatile uint32_t *)0xFFFFFFFFu = 0u; }

/* Recovered 2026-10-21: fmt_txt fonts use 16-byte glyph descriptors
 * (0x4b26a4 indexes glyph_dsc as glyph*16; upstream lv_font_montserrat_14.c
 * built with this setting matches ROM 0x755610 exactly). */
#define LV_FONT_FMT_TXT_LARGE 1

#endif /* LV_CONF_H */
