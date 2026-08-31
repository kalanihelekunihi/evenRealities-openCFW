/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_font_fmt_provider.h"

const void * open_cfw_lvgl_font_fmt_probe(lv_font_glyph_dsc_t * glyph,
                                          lv_draw_buf_t * draw_buf)
{
    return lv_font_get_bitmap_fmt_txt(glyph, draw_buf);
}
