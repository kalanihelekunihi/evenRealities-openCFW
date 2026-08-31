/* SPDX-License-Identifier: MIT */
/*
 * Cache-free LVGL radius-mask provider for the G2 Ambiq box-shadow backend.
 *
 * The raster and AA-table algorithms are derived from LVGL commit
 * 344c7c318047b7348e1be8572a9fd4260c251cfa, src/draw/sw/lv_draw_sw_mask.c.
 * The only semantic adaptation for valid inputs is ownership: every nonzero
 * radius owns a short-lived circle descriptor instead of using lv_global_t's
 * circle cache.  This preserves G2's authenticated LV_DRAW_SW_COMPLEX=0 ABI.
 */

#include "lvgl_ambiq_sw_mask_compat.h"

#include "../../stdlib/lv_mem.h"
#include "../../stdlib/lv_string.h"

#include <limits.h>

/* The authenticated ABI stores row coordinates in uint16_t. */
#define OPEN_CFW_RADIUS_MAX ((int32_t)UINT16_MAX)

static lv_draw_sw_mask_res_t radius_mask_cb(lv_opa_t * mask_buf,
                                             int32_t abs_x,
                                             int32_t abs_y,
                                             int32_t len,
                                             void * opaque);
static bool circle_calc_aa4(lv_draw_sw_mask_radius_circle_dsc_t * circle,
                            int32_t radius);
static void circle_init(lv_point_t * point, int32_t * decision, int32_t radius);
static bool circle_continue(const lv_point_t * point);
static void circle_next(lv_point_t * point, int32_t * decision);
static lv_opa_t * circle_line(lv_draw_sw_mask_radius_circle_dsc_t * circle,
                              int32_t y,
                              int32_t * len,
                              int32_t * x_start);
static inline lv_opa_t mask_mix(lv_opa_t current, lv_opa_t incoming);

static lv_draw_sw_mask_res_t fail_closed_mask(void)
{
    /* LVGL's TRANSP result contract permits leaving mask_buf unchanged. */
    return LV_DRAW_SW_MASK_RES_TRANSP;
}

void lv_draw_sw_mask_radius_init(lv_draw_sw_mask_radius_param_t * param,
                                 const lv_area_t * rect,
                                 int32_t radius,
                                 bool inv)
{
    int64_t width;
    int64_t height;
    int64_t short_side;
    lv_draw_sw_mask_radius_circle_dsc_t * circle;

    if(param == NULL) return;

    param->dsc.cb = radius_mask_cb;
    param->dsc.type = LV_DRAW_SW_MASK_TYPE_RADIUS;
    param->circle = NULL;
    param->cfg.outer = inv ? 1U : 0U;

    if(rect == NULL) {
        param->cfg.rect.x1 = 0;
        param->cfg.rect.y1 = 0;
        param->cfg.rect.x2 = -1;
        param->cfg.rect.y2 = -1;
        param->cfg.radius = 0;
        return;
    }

    param->cfg.rect = *rect;
    width = (int64_t)rect->x2 - (int64_t)rect->x1 + 1;
    height = (int64_t)rect->y2 - (int64_t)rect->y1 + 1;
    if(width <= 0 || height <= 0 || width > INT32_MAX || height > INT32_MAX) {
        param->cfg.radius = 0;
        return;
    }

    short_side = width < height ? width : height;
    if((int64_t)radius > (short_side >> 1)) radius = (int32_t)(short_side >> 1);
    if(radius < 0) radius = 0;
    param->cfg.radius = radius;

    if(radius == 0) return;

    /* Larger values cannot be represented by the authenticated uint16_t row
     * tables. Leave circle NULL so the callback fails closed without drawing.
     */
    if(radius > OPEN_CFW_RADIUS_MAX) return;

    circle = lv_malloc_zeroed(sizeof(*circle));
    if(circle == NULL) return;
    circle->life = -1;
    circle->used_cnt = 1;
    param->circle = circle;

    if(!circle_calc_aa4(circle, radius)) {
        lv_free(circle->buf);
        lv_free(circle);
        param->circle = NULL;
    }
}

void lv_draw_sw_mask_free_param(void * opaque)
{
    lv_draw_sw_mask_common_dsc_t * common = opaque;
    lv_draw_sw_mask_radius_param_t * param;
    lv_draw_sw_mask_radius_circle_dsc_t * circle;

    if(common == NULL || common->type != LV_DRAW_SW_MASK_TYPE_RADIUS) return;

    param = opaque;
    circle = param->circle;
    param->circle = NULL;
    if(circle == NULL) return;

    lv_free(circle->buf);
    circle->buf = NULL;
    circle->cir_opa = NULL;
    circle->opa_start_on_y = NULL;
    circle->x_start_on_y = NULL;
    lv_free(circle);
}

static lv_draw_sw_mask_res_t radius_mask_cb(lv_opa_t * mask_buf,
                                             int32_t abs_x,
                                             int32_t abs_y,
                                             int32_t len,
                                             void * opaque)
{
    lv_draw_sw_mask_radius_param_t * param = opaque;
    bool outer;
    int32_t radius;
    lv_area_t rect;
    int64_t line_end;
    int64_t left_inner;
    int64_t right_inner;
    int64_t rectangle_width;
    int64_t rectangle_height;
    int64_t relative_y;
    int32_t k;
    int32_t width;
    int32_t height;
    int32_t aa_len;
    int32_t x_start;
    int32_t circle_y;
    int32_t circle_x_right;
    int32_t circle_x_left;
    int32_t i;
    lv_opa_t * aa_opa;

    if(param == NULL || mask_buf == NULL || len <= 0) {
        return LV_DRAW_SW_MASK_RES_FULL_COVER;
    }

    outer = param->cfg.outer != 0;
    radius = param->cfg.radius;
    rect = param->cfg.rect;
    line_end = (int64_t)abs_x + (int64_t)len;
    rectangle_width = (int64_t)rect.x2 - (int64_t)rect.x1 + 1;
    rectangle_height = (int64_t)rect.y2 - (int64_t)rect.y1 + 1;
    relative_y = (int64_t)abs_y - rect.y1;

    if(radius < 0 || radius > OPEN_CFW_RADIUS_MAX ||
       rectangle_width <= 0 || rectangle_width > INT32_MAX ||
       rectangle_height <= 0 || rectangle_height > INT32_MAX ||
       relative_y < INT32_MIN || relative_y > INT32_MAX ||
       line_end < INT32_MIN || line_end > INT32_MAX ||
       (int64_t)rect.x1 - abs_x < INT32_MIN ||
       (int64_t)rect.x1 - abs_x > INT32_MAX ||
       (int64_t)rect.x2 - abs_x < INT32_MIN ||
       (int64_t)rect.x2 - abs_x > INT32_MAX) {
        return fail_closed_mask();
    }

    if(!outer) {
        if(abs_y < rect.y1 || abs_y > rect.y2) return fail_closed_mask();
    }
    else if(abs_y < rect.y1 || abs_y > rect.y2) {
        return LV_DRAW_SW_MASK_RES_FULL_COVER;
    }

    left_inner = (int64_t)rect.x1 + radius;
    right_inner = (int64_t)rect.x2 - radius;
    if((int64_t)abs_x >= left_inner && line_end <= right_inner) {
        /* Horizontal span is between both rounded corners. */
    }
    else if((int64_t)abs_y < (int64_t)rect.y1 + radius ||
            (int64_t)abs_y > (int64_t)rect.y2 - radius) {
        goto rounded_corner;
    }

    if(!outer) {
        int64_t last = (int64_t)rect.x1 - abs_x;
        int64_t first;
        if(last > len) return fail_closed_mask();
        if(last >= 0) lv_memset(mask_buf, 0, (size_t)last);
        first = (int64_t)rect.x2 - abs_x + 1;
        if(first <= 0) return fail_closed_mask();
        if(first < len) {
            lv_memset(&mask_buf[(int32_t)first], 0, (size_t)(len - first));
        }
        if(last == 0 && first == len) return LV_DRAW_SW_MASK_RES_FULL_COVER;
        return LV_DRAW_SW_MASK_RES_CHANGED;
    }
    else {
        int64_t first = (int64_t)rect.x1 - abs_x;
        if(first < 0) first = 0;
        if(first <= len) {
            int64_t last = (int64_t)rect.x2 - abs_x - first + 1;
            if(first + last > len) last = len - first;
            if(last >= 0) {
                lv_memset(&mask_buf[(int32_t)first], 0, (size_t)last);
            }
        }
        return LV_DRAW_SW_MASK_RES_CHANGED;
    }

rounded_corner:
    if(radius == 0) return fail_closed_mask();
    if(param->circle == NULL || param->circle->radius != radius ||
       param->circle->cir_opa == NULL ||
       param->circle->opa_start_on_y == NULL ||
       param->circle->x_start_on_y == NULL) {
        return fail_closed_mask();
    }

    k = (int32_t)((int64_t)rect.x1 - abs_x);
    width = (int32_t)rectangle_width;
    height = (int32_t)rectangle_height;
    abs_y = (int32_t)relative_y;
    if(abs_y < radius) circle_y = radius - abs_y - 1;
    else circle_y = abs_y - (height - radius);
    if(circle_y < 0 || circle_y >= radius) return fail_closed_mask();

    aa_opa = circle_line(param->circle, circle_y, &aa_len, &x_start);
    if(aa_opa == NULL || aa_len < 0 || aa_len > radius ||
       x_start < 0 || x_start > radius) {
        return fail_closed_mask();
    }
    {
        int64_t right = (int64_t)k + width - radius + x_start;
        int64_t left = (int64_t)k + radius - x_start - 1;
        if(right < INT32_MIN || right > INT32_MAX ||
           left < INT32_MIN || left > INT32_MAX) {
            return fail_closed_mask();
        }
        circle_x_right = (int32_t)right;
        circle_x_left = (int32_t)left;
    }
    if((int64_t)circle_x_right + aa_len > INT32_MAX ||
       (int64_t)circle_x_left - aa_len + 1 < INT32_MIN ||
       circle_x_left == INT32_MAX) {
        return fail_closed_mask();
    }

    if(!outer) {
        for(i = 0; i < aa_len; i++) {
            lv_opa_t opacity = aa_opa[aa_len - i - 1];
            if(circle_x_right + i >= 0 && circle_x_right + i < len) {
                mask_buf[circle_x_right + i] =
                    mask_mix(opacity, mask_buf[circle_x_right + i]);
            }
            if(circle_x_left - i >= 0 && circle_x_left - i < len) {
                mask_buf[circle_x_left - i] =
                    mask_mix(opacity, mask_buf[circle_x_left - i]);
            }
        }
        circle_x_right = LV_CLAMP(0, circle_x_right + i, len);
        lv_memset(&mask_buf[circle_x_right], 0,
                  (size_t)(len - circle_x_right));
        circle_x_left = LV_CLAMP(0, circle_x_left - aa_len + 1, len);
        lv_memset(mask_buf, 0, (size_t)circle_x_left);
    }
    else {
        for(i = 0; i < aa_len; i++) {
            lv_opa_t opacity = (lv_opa_t)(255U - aa_opa[aa_len - i - 1]);
            if(circle_x_right + i >= 0 && circle_x_right + i < len) {
                mask_buf[circle_x_right + i] =
                    mask_mix(opacity, mask_buf[circle_x_right + i]);
            }
            if(circle_x_left - i >= 0 && circle_x_left - i < len) {
                mask_buf[circle_x_left - i] =
                    mask_mix(opacity, mask_buf[circle_x_left - i]);
            }
        }
        {
            int32_t clear_start = LV_CLAMP(0, circle_x_left + 1, len);
            int32_t clear_len =
                LV_CLAMP(0, circle_x_right - clear_start, len - clear_start);
            lv_memset(&mask_buf[clear_start], 0, (size_t)clear_len);
        }
    }

    return LV_DRAW_SW_MASK_RES_CHANGED;
}

static void circle_init(lv_point_t * point, int32_t * decision, int32_t radius)
{
    point->x = radius;
    point->y = 0;
    *decision = 1 - radius;
}

static bool circle_continue(const lv_point_t * point)
{
    return point->y <= point->x;
}

static void circle_next(lv_point_t * point, int32_t * decision)
{
    if(*decision <= 0) {
        *decision += 2 * point->y + 3;
    }
    else {
        *decision += 2 * (point->y - point->x) + 5;
        point->x--;
    }
    point->y++;
}

static bool circle_calc_aa4(lv_draw_sw_mask_radius_circle_dsc_t * circle,
                            int32_t radius)
{
    size_t persistent_size;
    size_t coordinate_count;
    int32_t coordinate_capacity;
    int32_t * circle_x;
    int32_t * circle_y;
    uint32_t eighth_y = 0;
    lv_point_t point;
    int32_t decision;
    int32_t i;
    uint32_t x_integer[4];
    uint32_t x_fraction[4];
    int32_t circle_size = 0;
    int32_t y;

    if(circle == NULL || radius <= 0 || radius > OPEN_CFW_RADIUS_MAX) return false;

    persistent_size = (size_t)radius * 6U + 6U;
    coordinate_count = ((size_t)radius + 1U) * 4U;
    coordinate_capacity = (radius + 1) * 2;
    circle->buf = lv_malloc(persistent_size);
    if(circle->buf == NULL) return false;
    lv_memset(circle->buf, 0, persistent_size);
    circle->radius = radius;
    circle->cir_opa = circle->buf;
    circle->opa_start_on_y = (uint16_t *)(circle->buf + 2 * radius + 2);
    circle->x_start_on_y = (uint16_t *)(circle->buf + 4 * radius + 4);

    if(radius == 1) {
        circle->cir_opa[0] = 180;
        circle->opa_start_on_y[0] = 0;
        circle->opa_start_on_y[1] = 1;
        circle->x_start_on_y[0] = 0;
        return true;
    }

    circle_x = lv_malloc_zeroed(coordinate_count * sizeof(*circle_x));
    if(circle_x == NULL) return false;
    circle_y = &circle_x[((size_t)radius + 1U) * 2U];

    circle_init(&point, &decision, radius * 4);
    x_integer[0] = (uint32_t)point.x >> 2;
    x_fraction[0] = 0;
    while(circle_continue(&point)) {
        for(i = 0; i < 4; i++) {
            circle_next(&point, &decision);
            if(!circle_continue(&point)) break;
            x_integer[i] = (uint32_t)point.x >> 2;
            x_fraction[i] = (uint32_t)point.x & 3U;
        }
        if(i != 4) break;

        if(circle_size > coordinate_capacity - 2) {
            lv_free(circle_x);
            return false;
        }

        circle_x[circle_size] = (int32_t)x_integer[0];
        circle_y[circle_size] = (int32_t)eighth_y;
        if(x_integer[0] == x_integer[3]) {
            circle->cir_opa[circle_size] =
                (lv_opa_t)((x_fraction[0] + x_fraction[1] +
                            x_fraction[2] + x_fraction[3]) * 16U);
            circle_size++;
        }
        else {
            uint32_t split;
            if(x_integer[0] != x_integer[1]) split = 1;
            else if(x_integer[0] != x_integer[2]) split = 2;
            else split = 3;
            circle->cir_opa[circle_size] = (lv_opa_t)(
                (x_fraction[0] + (split > 1 ? x_fraction[1] : 0U) +
                 (split > 2 ? x_fraction[2] : 0U)) * 16U);
            circle_size++;
            circle_x[circle_size] = (int32_t)x_integer[0] - 1;
            circle_y[circle_size] = (int32_t)eighth_y;
            circle->cir_opa[circle_size] = (lv_opa_t)(
                (split * 4U + x_fraction[split] +
                 (split < 2 ? x_fraction[2] : 0U) +
                 (split < 3 ? x_fraction[3] : 0U)) * 16U);
            circle_size++;
        }
        eighth_y++;
    }

    if(circle_size <= 0) {
        lv_free(circle_x);
        return false;
    }

    {
        int32_t middle = radius * 723;
        int32_t middle_integer = middle >> 10;
        if(circle_x[circle_size - 1] != middle_integer ||
           circle_y[circle_size - 1] != middle_integer) {
            int32_t value = middle - (middle_integer << 10);
            if(value <= 512) {
                value = (value * value * 2) >> 16;
            }
            else {
                value = 1024 - value;
                value = 15 - ((value * value * 2) >> 16);
            }
            circle_x[circle_size] = middle_integer;
            circle_y[circle_size] = middle_integer;
            circle->cir_opa[circle_size] = (lv_opa_t)(value * 16);
            circle_size++;
        }
    }

    for(i = circle_size - 2; i >= 0; i--, circle_size++) {
        if(circle_size >= coordinate_capacity) {
            lv_free(circle_x);
            return false;
        }
        circle_x[circle_size] = circle_y[i];
        circle_y[circle_size] = circle_x[i];
        circle->cir_opa[circle_size] = circle->cir_opa[i];
    }

    y = 0;
    i = 0;
    circle->opa_start_on_y[0] = 0;
    while(i < circle_size && y <= radius) {
        circle->opa_start_on_y[y] = (uint16_t)i;
        circle->x_start_on_y[y] = (uint16_t)circle_x[i];
        while(i < circle_size && circle_y[i] == y) {
            if(circle_x[i] < circle->x_start_on_y[y]) {
                circle->x_start_on_y[y] = (uint16_t)circle_x[i];
            }
            i++;
        }
        y++;
    }
    lv_free(circle_x);
    return y == radius + 1;
}

static lv_opa_t * circle_line(lv_draw_sw_mask_radius_circle_dsc_t * circle,
                              int32_t y,
                              int32_t * len,
                              int32_t * x_start)
{
    uint16_t first;
    uint16_t next;
    if(circle == NULL || len == NULL || x_start == NULL ||
       y < 0 || y >= circle->radius) {
        return NULL;
    }
    first = circle->opa_start_on_y[y];
    next = circle->opa_start_on_y[y + 1];
    if(next < first) return NULL;
    *len = (int32_t)(next - first);
    *x_start = circle->x_start_on_y[y];
    return &circle->cir_opa[first];
}

static inline lv_opa_t mask_mix(lv_opa_t current, lv_opa_t incoming)
{
    if(incoming >= LV_OPA_MAX) return current;
    if(incoming <= LV_OPA_MIN) return 0;
    return (lv_opa_t)LV_UDIV255((uint32_t)current * incoming);
}
