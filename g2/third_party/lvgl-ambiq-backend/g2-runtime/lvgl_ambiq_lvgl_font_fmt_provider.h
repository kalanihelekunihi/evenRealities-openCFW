/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_LVGL_AMBIQ_FONT_FMT_PROVIDER_H
#define OPENCFW_LVGL_AMBIQ_FONT_FMT_PROVIDER_H

#include "src/font/lv_font_fmt_txt.h"

#ifdef __cplusplus
extern "C" {
#endif

const void * lv_font_get_bitmap_fmt_txt(lv_font_glyph_dsc_t * glyph,
                                        lv_draw_buf_t * draw_buf);

#ifdef __cplusplus
}
#endif

#endif
