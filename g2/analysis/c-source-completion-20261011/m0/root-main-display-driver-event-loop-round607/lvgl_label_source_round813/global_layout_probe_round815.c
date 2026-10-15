#include <stddef.h>
#include "src/core/lv_global.h"

/* Apollo 0x4734cc initializes these fields at the listed offsets. */
#define CHECK(field, offset) _Static_assert(offsetof(lv_global_t, field) == offset, #field)
CHECK(disp_ll, 0x04);
CHECK(style_refresh, 0x24);
CHECK(style_last_custom_prop_id, 0x2c);
CHECK(indev_ll, 0x44);
CHECK(layout_count, 0x58);
CHECK(memory_zero, 0x64);
CHECK(event_last_register_id, 0x70);

/* The trial defaults are 0x1f8; Apollo clears only 0x1ec bytes. */
_Static_assert(sizeof(lv_global_t) == 0x1f8, "trial LVGL global size changed");
