/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LVGL_DRAW_BUF_SHAPE_HOST_CONFIG_H
#define OPEN_CFW_LVGL_DRAW_BUF_SHAPE_HOST_CONFIG_H

struct _lv_draw_buf_handlers_t;
const struct _lv_draw_buf_handlers_t * open_cfw_test_draw_buf_handlers(void);

#define OPEN_CFW_LVGL_DRAW_BUF_DEFAULT_HANDLERS() \
    open_cfw_test_draw_buf_handlers()

#endif
