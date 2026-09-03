/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_draw_task_provider.h"
#include "src/core/lv_global.h"
#include "src/display/lv_display_private.h"

#include <assert.h>
#include <string.h>

lv_global_t lv_global;

bool lv_area_intersect(lv_area_t * result, const lv_area_t * first,
                       const lv_area_t * second)
{
    result->x1 = first->x1 > second->x1 ? first->x1 : second->x1;
    result->y1 = first->y1 > second->y1 ? first->y1 : second->y1;
    result->x2 = first->x2 < second->x2 ? first->x2 : second->x2;
    result->y2 = first->y2 < second->y2 ? first->y2 : second->y2;
    return result->x1 <= result->x2 && result->y1 <= result->y2;
}

static void set_area(lv_area_t * area, int32_t x1, int32_t y1,
                     int32_t x2, int32_t y2)
{
    area->x1 = x1;
    area->y1 = y1;
    area->x2 = x2;
    area->y2 = y2;
}

static void init_task(lv_draw_task_t * task, lv_draw_task_state_t state,
                      int32_t x1, int32_t y1, int32_t x2, int32_t y2)
{
    memset(task, 0, sizeof(*task));
    task->state = state;
    task->preferred_draw_unit_id = LV_DRAW_UNIT_NONE;
    set_area(&task->area, x1, y1, x2, y2);
    task->_real_area = task->area;
}

int main(void)
{
    lv_layer_t layer;
    lv_draw_task_t first;
    lv_draw_task_t second;
    lv_draw_task_t third;
    lv_display_t display;

    memset(&lv_global, 0, sizeof(lv_global));
    memset(&layer, 0, sizeof(layer));
    memset(&display, 0, sizeof(display));
    assert(lv_draw_get_available_task(NULL, NULL, 1U) == NULL);

    lv_global.draw_info.unit_cnt = 1U;
    init_task(&first, LV_DRAW_TASK_STATE_QUEUED, 0, 0, 9, 9);
    layer.draw_task_head = &first;
    assert(lv_draw_get_available_task(&layer, NULL, 1U) == &first);
    first.state = LV_DRAW_TASK_STATE_IN_PROGRESS;
    assert(lv_draw_get_available_task(&layer, NULL, 1U) == NULL);

    lv_global.draw_info.unit_cnt = 2U;
    display.hor_res = 100;
    display.ver_res = 50;
    lv_global.disp_refresh = &display;
    init_task(&first, LV_DRAW_TASK_STATE_IN_PROGRESS, 0, 0, 99, 49);
    layer.draw_task_head = &first;
    assert(lv_draw_get_available_task(&layer, NULL, 1U) == NULL);

    display.rotation = LV_DISPLAY_ROTATION_90;
    set_area(&first.area, 0, 0, 49, 99);
    assert(lv_draw_get_available_task(&layer, NULL, 1U) == NULL);

    display.rotation = LV_DISPLAY_ROTATION_0;
    init_task(&first, LV_DRAW_TASK_STATE_READY, 0, 0, 20, 20);
    init_task(&second, LV_DRAW_TASK_STATE_QUEUED, 10, 10, 30, 30);
    init_task(&third, LV_DRAW_TASK_STATE_QUEUED, 40, 40, 49, 49);
    first.next = &second;
    second.next = &third;
    layer.draw_task_head = &first;
    second.preferred_draw_unit_id = 7U;
    assert(lv_draw_get_available_task(&layer, NULL, 3U) == &third);
    assert(lv_draw_get_available_task(&layer, NULL, 7U) == &second);
    assert(lv_draw_get_available_task(&layer, &second, 7U) == &third);

    first.state = LV_DRAW_TASK_STATE_IN_PROGRESS;
    second.preferred_draw_unit_id = LV_DRAW_UNIT_NONE;
    assert(lv_draw_get_available_task(&layer, NULL, 7U) == &third);
    set_area(&first._real_area, 0, 0, 5, 5);
    assert(lv_draw_get_available_task(&layer, NULL, 7U) == &second);

    memset(&layer, 0, sizeof(layer));
    assert(lv_draw_get_available_task(&layer, NULL, 1U) == NULL);
    return 0;
}
