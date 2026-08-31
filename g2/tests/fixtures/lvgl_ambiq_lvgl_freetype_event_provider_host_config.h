/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LVGL_FREETYPE_EVENT_HOST_CONFIG_H
#define OPEN_CFW_LVGL_FREETYPE_EVENT_HOST_CONFIG_H

struct _lv_freetype_context_t;
struct _lv_freetype_context_t * open_cfw_test_freetype_context(void);

#define OPEN_CFW_LVGL_FREETYPE_CONTEXT() open_cfw_test_freetype_context()

#endif
