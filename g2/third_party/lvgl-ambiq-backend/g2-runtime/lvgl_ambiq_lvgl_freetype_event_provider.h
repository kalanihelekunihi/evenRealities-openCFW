/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LVGL_AMBIQ_FREETYPE_EVENT_PROVIDER_H
#define OPEN_CFW_LVGL_AMBIQ_FREETYPE_EVENT_PROVIDER_H

#include "src/libs/freetype/lv_freetype.h"

#ifdef __cplusplus
extern "C" {
#endif

void lv_freetype_outline_add_event(
    lv_event_cb_t event_cb,
    lv_event_code_t filter,
    void * user_data
);

#ifdef __cplusplus
}
#endif

#endif
