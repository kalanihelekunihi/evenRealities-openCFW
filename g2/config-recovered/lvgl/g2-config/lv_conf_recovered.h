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

#endif /* LV_CONF_H */
