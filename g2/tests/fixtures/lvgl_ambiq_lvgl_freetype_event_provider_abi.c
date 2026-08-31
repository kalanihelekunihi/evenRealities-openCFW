/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_freetype_event_provider.h"

void open_cfw_lvgl_freetype_event_probe(
    lv_event_cb_t event_cb,
    lv_event_code_t filter,
    void * user_data
)
{
    lv_freetype_outline_add_event(event_cb, filter, user_data);
}
