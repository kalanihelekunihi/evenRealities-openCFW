/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_core_provider.h"

#include <assert.h>
#include <limits.h>
#include <math.h>
#include <stddef.h>
#include <stdint.h>

static void test_area_operations(void)
{
    lv_area_t area;
    lv_area_t other;
    lv_area_t result;

    lv_area_set(&area, 10, 20, 19, 29);
    assert(lv_area_get_width(&area) == 10);
    assert(lv_area_get_height(&area) == 10);
    lv_area_set_width(&area, 5);
    lv_area_set_height(&area, 7);
    assert(area.x2 == 14 && area.y2 == 26);
    lv_area_increase(&area, 2, 3);
    assert(area.x1 == 8 && area.x2 == 16 && area.y1 == 17 && area.y2 == 29);
    lv_area_move(&area, -8, -17);
    assert(area.x1 == 0 && area.x2 == 8 && area.y1 == 0 && area.y2 == 12);

    lv_area_set(&other, 4, 5, 20, 30);
    assert(lv_area_intersect(&result, &area, &other));
    assert(result.x1 == 4 && result.y1 == 5 && result.x2 == 8 && result.y2 == 12);
    lv_area_set(&other, 20, 30, 40, 50);
    assert(!lv_area_intersect(&result, &area, &other));

    lv_area_set(&area, 0, 0, 99, 99);
    lv_area_set(&other, 10, 10, 89, 89);
    assert(lv_area_is_in(&other, &area, 10));
    lv_area_set(&other, 0, 0, 2, 2);
    assert(!lv_area_is_in(&other, &area, 10));
}

static void test_hostile_area_inputs_are_bounded(void)
{
    lv_area_t area = {INT32_MIN, INT32_MIN, INT32_MAX, INT32_MAX};
    lv_area_t before = area;

    assert(lv_area_get_width(NULL) == 0);
    assert(lv_area_get_height(NULL) == 0);
    lv_area_set(NULL, 1, 2, 3, 4);
    lv_area_set_width(NULL, INT32_MAX);
    lv_area_set_height(NULL, INT32_MAX);
    lv_area_increase(NULL, INT32_MAX, INT32_MIN);
    lv_area_move(NULL, INT32_MAX, INT32_MIN);
    assert(!lv_area_intersect(NULL, &area, &area));
    assert(!lv_area_intersect(&area, NULL, &area));
    assert(!lv_area_is_in(NULL, &area, 0));
    assert(!lv_area_is_in(&area, NULL, 0));

    lv_area_move(&area, INT32_MAX, INT32_MIN);
    lv_area_move(&area, -INT32_MAX, INT32_MIN);
    assert(area.x1 == before.x1 && area.x2 == before.x2);
    assert(area.y1 == before.y1 && area.y2 == before.y2);
}

static void test_color_event_and_matrix(void)
{
    lv_event_t event = {0};
    int parameter = 42;
    lv_matrix_t matrix = {{{1.0f, 0.0f, 0.0f},
                           {0.0f, 1.0f, 0.0f},
                           {0.0f, 0.0f, 1.0f}}};
    lv_fpoint_t point = {2.0f, 3.0f};

    assert(lv_color_format_get_bpp(LV_COLOR_FORMAT_I1) == 1);
    assert(lv_color_format_get_bpp(LV_COLOR_FORMAT_NEMA_TSC6A) == 6);
    assert(lv_color_format_get_bpp(LV_COLOR_FORMAT_RGB565) == 16);
    assert(lv_color_format_get_bpp(LV_COLOR_FORMAT_ARGB8888) == 32);
    assert(lv_color_format_get_bpp((lv_color_format_t)0x7fff) == 0);

    event.code = (lv_event_code_t)(LV_EVENT_CLICKED | LV_EVENT_PREPROCESS);
    event.param = &parameter;
    assert(lv_event_get_code(&event) == LV_EVENT_CLICKED);
    assert(lv_event_get_param(&event) == &parameter);
    assert(lv_event_get_code(NULL) == LV_EVENT_ALL);
    assert(lv_event_get_param(NULL) == NULL);

    lv_matrix_translate(&matrix, 4.0f, -1.0f);
    lv_matrix_transform_point(&matrix, &point);
    assert(fabsf(point.x - 6.0f) < 0.0001f);
    assert(fabsf(point.y - 2.0f) < 0.0001f);

    matrix.m[0][0] = 2.0f;
    matrix.m[0][1] = 1.0f;
    matrix.m[0][2] = 3.0f;
    matrix.m[1][0] = -1.0f;
    matrix.m[1][1] = 4.0f;
    matrix.m[1][2] = 5.0f;
    matrix.m[2][0] = 0.0f;
    matrix.m[2][1] = 0.0f;
    matrix.m[2][2] = 1.0f;
    lv_matrix_translate(&matrix, 7.0f, -2.0f);
    assert(fabsf(matrix.m[0][2] - 15.0f) < 0.0001f);
    assert(fabsf(matrix.m[1][2] + 10.0f) < 0.0001f);
    lv_matrix_translate(NULL, 1.0f, 1.0f);
    lv_matrix_transform_point(NULL, &point);
    lv_matrix_transform_point(&matrix, NULL);
}

int main(void)
{
    test_area_operations();
    test_hostile_area_inputs_are_bounded();
    test_color_event_and_matrix();
    return 0;
}
