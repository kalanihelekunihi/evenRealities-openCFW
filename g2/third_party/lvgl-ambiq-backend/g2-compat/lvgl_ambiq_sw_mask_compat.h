/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LVGL_AMBIQ_SW_MASK_COMPAT_H
#define OPEN_CFW_LVGL_AMBIQ_SW_MASK_COMPAT_H

/*
 * G2 authenticates LV_DRAW_SW_COMPLEX=0 and therefore has no global software
 * circle cache.  Ambiq's box-shadow unit nevertheless uses LVGL's radius-mask
 * parameter ABI as short-lived local state.  Preserve only that public/private
 * interface when complex software drawing is disabled. The companion
 * lvgl_ambiq_sw_mask_cache_free.c owns one bounded circle table per parameter,
 * so no cache fields or mutexes are added to lv_global_t.
 */
#include "../sw/lv_draw_sw_mask.h"

#if !LV_DRAW_SW_COMPLEX

typedef enum {
    LV_DRAW_SW_MASK_TYPE_LINE,
    LV_DRAW_SW_MASK_TYPE_ANGLE,
    LV_DRAW_SW_MASK_TYPE_RADIUS,
    LV_DRAW_SW_MASK_TYPE_FADE,
    LV_DRAW_SW_MASK_TYPE_MAP,
} lv_draw_sw_mask_type_t;

typedef lv_draw_sw_mask_res_t (*lv_draw_sw_mask_xcb_t)(lv_opa_t * mask_buf,
                                                       int32_t abs_x,
                                                       int32_t abs_y,
                                                       int32_t len,
                                                       void * p);

typedef struct {
    uint8_t * buf;
    lv_opa_t * cir_opa;
    uint16_t * x_start_on_y;
    uint16_t * opa_start_on_y;
    int32_t life;
    uint32_t used_cnt;
    int32_t radius;
} lv_draw_sw_mask_radius_circle_dsc_t;

struct _lv_draw_sw_mask_common_dsc_t {
    lv_draw_sw_mask_xcb_t cb;
    lv_draw_sw_mask_type_t type;
};

struct _lv_draw_sw_mask_radius_param_t {
    lv_draw_sw_mask_common_dsc_t dsc;

    struct {
        lv_area_t rect;
        int32_t radius;
        uint8_t outer : 1;
    } cfg;

    lv_draw_sw_mask_radius_circle_dsc_t * circle;
};

void lv_draw_sw_mask_radius_init(lv_draw_sw_mask_radius_param_t * param,
                                 const lv_area_t * rect,
                                 int32_t radius,
                                 bool inv);
void lv_draw_sw_mask_free_param(void * p);

#endif /* !LV_DRAW_SW_COMPLEX */

#endif /* OPEN_CFW_LVGL_AMBIQ_SW_MASK_COMPAT_H */
