/* SPDX-License-Identifier: MIT */
/*
 * Copyright (c) 2025 LVGL Kft
 *
 * Bounds-hardened transcription of the area, color-format, event-accessor,
 * and matrix operations at LVGL commit
 * 344c7c318047b7348e1be8572a9fd4260c251cfa.  For valid LVGL inputs the
 * operations are equivalent to the pinned upstream implementations.  Null
 * pointers and arithmetic outside the signed source domain are made bounded
 * here because upstream leaves those cases undefined.
 */

#include "lvgl_ambiq_lvgl_core_provider.h"

#include <limits.h>
#include <stdint.h>

static int32_t wrap_add_i32(int32_t lhs, int32_t rhs)
{
    return (int32_t)((uint32_t)lhs + (uint32_t)rhs);
}

static int32_t wrap_sub_i32(int32_t lhs, int32_t rhs)
{
    return (int32_t)((uint32_t)lhs - (uint32_t)rhs);
}

static bool point_within_circle(const lv_area_t * area, const lv_point_t * point)
{
    int64_t radius = ((int64_t)area->x2 - (int64_t)area->x1) / 2;
    int64_t center_x = (int64_t)area->x1 + radius;
    int64_t center_y = (int64_t)area->y1 + radius;
    int64_t dx = (int64_t)point->x - center_x;
    int64_t dy = (int64_t)point->y - center_y;

    /* Valid rounded LVGL areas have a non-negative, INT32-bounded radius. */
    if(radius < 0 || radius > INT32_MAX) return false;
    if(dx < -radius || dx > radius || dy < -radius || dy > radius) return false;

    return ((uint64_t)(dx * dx) + (uint64_t)(dy * dy)) <=
           (uint64_t)(radius * radius);
}

static bool area_is_point_on(const lv_area_t * area, const lv_point_t * point,
                             int32_t radius)
{
    lv_area_t corner;
    int64_t width;
    int64_t height;
    int32_t max_radius;

    if(area == NULL || point == NULL) return false;
    if(point->x < area->x1 || point->x > area->x2 ||
       point->y < area->y1 || point->y > area->y2) {
        return false;
    }
    if(radius <= 0) return true;

    width = (int64_t)area->x2 - (int64_t)area->x1 + 1;
    height = (int64_t)area->y2 - (int64_t)area->y1 + 1;
    if(width <= 0 || height <= 0 || width > INT32_MAX || height > INT32_MAX) {
        return false;
    }
    max_radius = (int32_t)((width / 2 < height / 2) ? width / 2 : height / 2);
    if(radius > max_radius) radius = max_radius;

    corner.x1 = area->x1;
    corner.x2 = wrap_add_i32(area->x1, radius);
    corner.y1 = area->y1;
    corner.y2 = wrap_add_i32(area->y1, radius);
    if(point->x >= corner.x1 && point->x <= corner.x2 &&
       point->y >= corner.y1 && point->y <= corner.y2) {
        corner.x2 = wrap_add_i32(corner.x2, radius);
        corner.y2 = wrap_add_i32(corner.y2, radius);
        return point_within_circle(&corner, point);
    }

    corner.y1 = wrap_sub_i32(area->y2, radius);
    corner.y2 = area->y2;
    if(point->x >= corner.x1 && point->x <= corner.x2 &&
       point->y >= corner.y1 && point->y <= corner.y2) {
        corner.x2 = wrap_add_i32(corner.x2, radius);
        corner.y1 = wrap_sub_i32(corner.y1, radius);
        return point_within_circle(&corner, point);
    }

    corner.x1 = wrap_sub_i32(area->x2, radius);
    corner.x2 = area->x2;
    if(point->x >= corner.x1 && point->x <= corner.x2 &&
       point->y >= corner.y1 && point->y <= corner.y2) {
        corner.x1 = wrap_sub_i32(corner.x1, radius);
        corner.y1 = wrap_sub_i32(corner.y1, radius);
        return point_within_circle(&corner, point);
    }

    corner.y1 = area->y1;
    corner.y2 = wrap_add_i32(area->y1, radius);
    if(point->x >= corner.x1 && point->x <= corner.x2 &&
       point->y >= corner.y1 && point->y <= corner.y2) {
        corner.x1 = wrap_sub_i32(corner.x1, radius);
        corner.y2 = wrap_add_i32(corner.y2, radius);
        return point_within_circle(&corner, point);
    }

    return true;
}

void lv_area_set(lv_area_t * area, int32_t x1, int32_t y1, int32_t x2, int32_t y2)
{
    if(area == NULL) return;
    area->x1 = x1;
    area->y1 = y1;
    area->x2 = x2;
    area->y2 = y2;
}

int32_t lv_area_get_width(const lv_area_t * area)
{
    if(area == NULL) return 0;
    return wrap_add_i32(wrap_sub_i32(area->x2, area->x1), 1);
}

int32_t lv_area_get_height(const lv_area_t * area)
{
    if(area == NULL) return 0;
    return wrap_add_i32(wrap_sub_i32(area->y2, area->y1), 1);
}

void lv_area_set_width(lv_area_t * area, int32_t width)
{
    if(area == NULL) return;
    area->x2 = wrap_sub_i32(wrap_add_i32(area->x1, width), 1);
}

void lv_area_set_height(lv_area_t * area, int32_t height)
{
    if(area == NULL) return;
    area->y2 = wrap_sub_i32(wrap_add_i32(area->y1, height), 1);
}

void lv_area_increase(lv_area_t * area, int32_t width_extra, int32_t height_extra)
{
    if(area == NULL) return;
    area->x1 = wrap_sub_i32(area->x1, width_extra);
    area->x2 = wrap_add_i32(area->x2, width_extra);
    area->y1 = wrap_sub_i32(area->y1, height_extra);
    area->y2 = wrap_add_i32(area->y2, height_extra);
}

void lv_area_move(lv_area_t * area, int32_t x_offset, int32_t y_offset)
{
    if(area == NULL) return;
    area->x1 = wrap_add_i32(area->x1, x_offset);
    area->x2 = wrap_add_i32(area->x2, x_offset);
    area->y1 = wrap_add_i32(area->y1, y_offset);
    area->y2 = wrap_add_i32(area->y2, y_offset);
}

bool lv_area_intersect(lv_area_t * result, const lv_area_t * first,
                       const lv_area_t * second)
{
    lv_area_t intersection;

    if(result == NULL || first == NULL || second == NULL) return false;
    intersection.x1 = first->x1 > second->x1 ? first->x1 : second->x1;
    intersection.y1 = first->y1 > second->y1 ? first->y1 : second->y1;
    intersection.x2 = first->x2 < second->x2 ? first->x2 : second->x2;
    intersection.y2 = first->y2 < second->y2 ? first->y2 : second->y2;
    *result = intersection;
    return intersection.x1 <= intersection.x2 && intersection.y1 <= intersection.y2;
}

bool lv_area_is_in(const lv_area_t * inner, const lv_area_t * holder, int32_t radius)
{
    lv_point_t point;

    if(inner == NULL || holder == NULL) return false;
    if(inner->x1 < holder->x1 || inner->y1 < holder->y1 ||
       inner->x2 > holder->x2 || inner->y2 > holder->y2) {
        return false;
    }
    if(radius == 0) return true;

    point.x = inner->x1;
    point.y = inner->y1;
    if(!area_is_point_on(holder, &point, radius)) return false;
    point.x = inner->x2;
    if(!area_is_point_on(holder, &point, radius)) return false;
    point.x = inner->x1;
    point.y = inner->y2;
    if(!area_is_point_on(holder, &point, radius)) return false;
    point.x = inner->x2;
    return area_is_point_on(holder, &point, radius);
}

uint8_t lv_color_format_get_bpp(lv_color_format_t format)
{
    switch(format) {
        case LV_COLOR_FORMAT_I1:
        case LV_COLOR_FORMAT_A1:
            return 1;
        case LV_COLOR_FORMAT_I2:
        case LV_COLOR_FORMAT_A2:
            return 2;
        case LV_COLOR_FORMAT_I4:
        case LV_COLOR_FORMAT_A4:
        case LV_COLOR_FORMAT_NEMA_TSC4:
            return 4;
        case LV_COLOR_FORMAT_NEMA_TSC6:
        case LV_COLOR_FORMAT_NEMA_TSC6A:
        case LV_COLOR_FORMAT_NEMA_TSC6AP:
            return 6;
        case LV_COLOR_FORMAT_L8:
        case LV_COLOR_FORMAT_A8:
        case LV_COLOR_FORMAT_I8:
        case LV_COLOR_FORMAT_ARGB2222:
            return 8;
        case LV_COLOR_FORMAT_NEMA_TSC12:
        case LV_COLOR_FORMAT_NEMA_TSC12A:
            return 12;
        case LV_COLOR_FORMAT_RGB565A8:
        case LV_COLOR_FORMAT_RGB565:
        case LV_COLOR_FORMAT_YUY2:
        case LV_COLOR_FORMAT_AL88:
        case LV_COLOR_FORMAT_ARGB1555:
        case LV_COLOR_FORMAT_ARGB4444:
            return 16;
        case LV_COLOR_FORMAT_ARGB8565:
        case LV_COLOR_FORMAT_RGB888:
            return 24;
        case LV_COLOR_FORMAT_ARGB8888:
        case LV_COLOR_FORMAT_XRGB8888:
            return 32;
        case LV_COLOR_FORMAT_UNKNOWN:
        default:
            return 0;
    }
}

lv_event_code_t lv_event_get_code(lv_event_t * event)
{
    if(event == NULL) return LV_EVENT_ALL;
    return event->code & ~LV_EVENT_PREPROCESS;
}

void * lv_event_get_param(lv_event_t * event)
{
    return event == NULL ? NULL : event->param;
}

void lv_matrix_translate(lv_matrix_t * matrix, float dx, float dy)
{
    lv_matrix_t product;
    int row;

    if(matrix == NULL) return;
    if(matrix->m[0][0] == 1.0f && matrix->m[0][1] == 0.0f &&
       matrix->m[1][0] == 0.0f && matrix->m[1][1] == 1.0f &&
       matrix->m[2][0] == 0.0f && matrix->m[2][1] == 0.0f &&
       matrix->m[2][2] == 1.0f) {
        matrix->m[0][2] += dx;
        matrix->m[1][2] += dy;
        return;
    }

    for(row = 0; row < 3; ++row) {
        product.m[row][0] = matrix->m[row][0];
        product.m[row][1] = matrix->m[row][1];
        product.m[row][2] = matrix->m[row][0] * dx +
                            matrix->m[row][1] * dy + matrix->m[row][2];
    }
    *matrix = product;
}

void lv_matrix_transform_point(const lv_matrix_t * matrix, lv_fpoint_t * point)
{
    float x;
    float y;

    if(matrix == NULL || point == NULL) return;
    x = point->x;
    y = point->y;
    point->x = x * matrix->m[0][0] + y * matrix->m[1][0] + matrix->m[0][2];
    point->y = x * matrix->m[0][1] + y * matrix->m[1][1] + matrix->m[1][2];
}
