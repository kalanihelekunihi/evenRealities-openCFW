#include <stddef.h>
#include "src/core/lv_global.h"

/* Trial profile: removing three optional theme pointers accounts for 12 bytes. */
_Static_assert(LV_USE_THEME_DEFAULT == 0, "default theme must be disabled");
_Static_assert(LV_USE_THEME_SIMPLE == 0, "simple theme must be disabled");
_Static_assert(LV_USE_THEME_MONO == 0, "mono theme must be disabled");
_Static_assert(sizeof(lv_global_t) == 0x1ec, "Apollo global clear size");
_Static_assert(offsetof(lv_global_t, disp_ll) == 0x04, "display list");
_Static_assert(offsetof(lv_global_t, indev_ll) == 0x44, "input list");
_Static_assert(offsetof(lv_global_t, memory_zero) == 0x64, "memory sentinel");
_Static_assert(offsetof(lv_global_t, event_last_register_id) == 0x70, "event id");
