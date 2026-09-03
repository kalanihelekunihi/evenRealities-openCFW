/* SPDX-License-Identifier: MIT */
/*
 * Source-owned leaves required by the pinned LVGL label iterator.  Valid-input
 * behavior follows LVGL commit 344c7c318047b7348e1be8572a9fd4260c251cfa;
 * null and overflowing geometry is rejected before access.
 */

#include "lvgl_ambiq_lvgl_label_support_provider.h"

#include <limits.h>
#include <stdint.h>

static bool checked_add_i32(int32_t lhs, int32_t rhs, int32_t * result)
{
    int64_t value = (int64_t)lhs + (int64_t)rhs;
    if(result == NULL || value < INT32_MIN || value > INT32_MAX) return false;
    *result = (int32_t)value;
    return true;
}

static bool checked_sub_i32(int32_t lhs, int32_t rhs, int32_t * result)
{
    int64_t value = (int64_t)lhs - (int64_t)rhs;
    if(result == NULL || value < INT32_MIN || value > INT32_MAX) return false;
    *result = (int32_t)value;
    return true;
}

static bool point_within_circle(const lv_area_t * area, const lv_point_t * point)
{
    int64_t radius = ((int64_t)area->x2 - (int64_t)area->x1) / 2;
    int64_t center_x;
    int64_t center_y;
    int64_t dx;
    int64_t dy;

    if(radius < 0 || radius > INT32_MAX) return false;
    center_x = (int64_t)area->x1 + radius;
    center_y = (int64_t)area->y1 + radius;
    dx = (int64_t)point->x - center_x;
    dy = (int64_t)point->y - center_y;
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
       point->y < area->y1 || point->y > area->y2) return false;
    if(radius <= 0) return true;

    width = (int64_t)area->x2 - (int64_t)area->x1 + 1;
    height = (int64_t)area->y2 - (int64_t)area->y1 + 1;
    if(width <= 0 || height <= 0 || width > INT32_MAX || height > INT32_MAX) return false;
    max_radius = (int32_t)((width / 2 < height / 2) ? width / 2 : height / 2);
    if(radius > max_radius) radius = max_radius;

    corner.x1 = area->x1;
    if(!checked_add_i32(area->x1, radius, &corner.x2)) return false;
    corner.y1 = area->y1;
    if(!checked_add_i32(area->y1, radius, &corner.y2)) return false;
    if(area_is_point_on(&corner, point, 0)) {
        if(!checked_add_i32(corner.x2, radius, &corner.x2) ||
           !checked_add_i32(corner.y2, radius, &corner.y2)) return false;
        return point_within_circle(&corner, point);
    }
    if(!checked_sub_i32(area->y2, radius, &corner.y1)) return false;
    corner.y2 = area->y2;
    if(area_is_point_on(&corner, point, 0)) {
        if(!checked_add_i32(corner.x2, radius, &corner.x2) ||
           !checked_sub_i32(corner.y1, radius, &corner.y1)) return false;
        return point_within_circle(&corner, point);
    }
    if(!checked_sub_i32(area->x2, radius, &corner.x1)) return false;
    corner.x2 = area->x2;
    if(area_is_point_on(&corner, point, 0)) {
        if(!checked_sub_i32(corner.x1, radius, &corner.x1) ||
           !checked_sub_i32(corner.y1, radius, &corner.y1)) return false;
        return point_within_circle(&corner, point);
    }
    corner.y1 = area->y1;
    if(!checked_add_i32(area->y1, radius, &corner.y2)) return false;
    if(area_is_point_on(&corner, point, 0)) {
        if(!checked_sub_i32(corner.x1, radius, &corner.x1) ||
           !checked_add_i32(corner.y2, radius, &corner.y2)) return false;
        return point_within_circle(&corner, point);
    }
    return true;
}

bool lv_area_is_out(const lv_area_t * outside, const lv_area_t * holder, int32_t radius)
{
    lv_point_t point;

    if(outside == NULL || holder == NULL) return true;
    if(outside->x2 < holder->x1 || outside->y2 < holder->y1 ||
       outside->x1 > holder->x2 || outside->y1 > holder->y2) return true;
    if(radius == 0) return false;

    lv_point_set(&point, outside->x1, outside->y1);
    if(area_is_point_on(holder, &point, radius)) return false;
    lv_point_set(&point, outside->x2, outside->y1);
    if(area_is_point_on(holder, &point, radius)) return false;
    lv_point_set(&point, outside->x1, outside->y2);
    if(area_is_point_on(holder, &point, radius)) return false;
    lv_point_set(&point, outside->x2, outside->y2);
    if(area_is_point_on(holder, &point, radius)) return false;
    return true;
}

void lv_point_set(lv_point_t * point, int32_t x, int32_t y)
{
    if(point == NULL) return;
    point->x = x;
    point->y = y;
}

lv_color_t lv_color_make(uint8_t red, uint8_t green, uint8_t blue)
{
    lv_color_t color;
    color.red = red;
    color.green = green;
    color.blue = blue;
    return color;
}

lv_color_t lv_color_black(void)
{
    return lv_color_make(0U, 0U, 0U);
}
