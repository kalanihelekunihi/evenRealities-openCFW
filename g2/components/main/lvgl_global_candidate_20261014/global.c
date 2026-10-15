#include <stddef.h>
#include "src/core/lv_global.h"

/* Candidate Apollo global profile: the native initializer at 0x4734cc
 * clears 0x1ec bytes and touches these fields at the observed offsets.
 * Final placement at 0x2006f548 and startup ownership are separate gates. */
_Static_assert(LV_USE_THEME_DEFAULT == 0, "default theme profile");
_Static_assert(LV_USE_THEME_SIMPLE == 0, "simple theme profile");
_Static_assert(LV_USE_THEME_MONO == 0, "mono theme profile");
_Static_assert(sizeof(lv_global_t) == 0x1ec, "Apollo LVGL global extent");
_Static_assert(offsetof(lv_global_t, disp_ll) == 0x04, "display list offset");
_Static_assert(offsetof(lv_global_t, style_refresh) == 0x24, "style refresh offset");
_Static_assert(offsetof(lv_global_t, style_last_custom_prop_id) == 0x2c, "style property offset");
_Static_assert(offsetof(lv_global_t, indev_ll) == 0x44, "input list offset");
_Static_assert(offsetof(lv_global_t, layout_count) == 0x58, "layout count offset");
_Static_assert(offsetof(lv_global_t, memory_zero) == 0x64, "memory sentinel offset");
_Static_assert(offsetof(lv_global_t, event_last_register_id) == 0x70, "event id offset");

lv_global_t lv_global __attribute__((section(".bss.opencfw_lv_global")));
