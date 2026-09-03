/* SPDX-License-Identifier: MIT */
/*
 * Copyright (c) 2025 LVGL Kft
 *
 * Bounded transcription of lv_draw_get_available_task and its two private
 * helpers from authenticated LVGL commit
 * 344c7c318047b7348e1be8572a9fd4260c251cfa. The valid-state path preserves
 * single-unit ordering, multi-unit full-screen serialization, preferred-unit
 * selection, and independence from every older unfinished task.
 */

#include <stddef.h>
#include <stdint.h>

#include "lvgl_ambiq_lvgl_draw_task_provider.h"
#include "src/core/lv_global.h"
#include "src/display/lv_display_private.h"
#include "src/misc/lv_area_private.h"

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(offsetof(lv_global_t, disp_refresh) == 0x10U,
               "G2 refreshing-display offset changed");
_Static_assert(offsetof(lv_global_t, disp_default) == 0x14U,
               "G2 default-display offset changed");
_Static_assert(offsetof(lv_global_t, draw_info) == 0x13CU,
               "G2 draw-info offset changed");
_Static_assert(offsetof(lv_draw_global_info_t, unit_head) == 0x00U,
               "G2 draw-unit head offset changed");
_Static_assert(offsetof(lv_draw_global_info_t, unit_cnt) == 0x04U,
               "G2 draw-unit count offset changed");
_Static_assert(offsetof(lv_layer_t, draw_task_head) == 0x44U,
               "G2 layer task-head offset changed");
_Static_assert(offsetof(lv_draw_task_t, next) == 0x00U,
               "G2 draw-task next offset changed");
_Static_assert(offsetof(lv_draw_task_t, area) == 0x08U,
               "G2 draw-task area offset changed");
_Static_assert(offsetof(lv_draw_task_t, _real_area) == 0x18U,
               "G2 draw-task real-area offset changed");
#endif

static const lv_display_t * effective_display(const lv_display_t * display)
{
    return display != NULL ? display : LV_GLOBAL_DEFAULT()->disp_default;
}

static int32_t horizontal_resolution(const lv_display_t * display)
{
    display = effective_display(display);
    if(display == NULL) return 0;
    if(display->rotation == LV_DISPLAY_ROTATION_90 ||
       display->rotation == LV_DISPLAY_ROTATION_270) {
        return display->ver_res;
    }
    return display->hor_res;
}

static int32_t vertical_resolution(const lv_display_t * display)
{
    display = effective_display(display);
    if(display == NULL) return 0;
    if(display->rotation == LV_DISPLAY_ROTATION_90 ||
       display->rotation == LV_DISPLAY_ROTATION_270) {
        return display->hor_res;
    }
    return display->ver_res;
}

static lv_draw_task_t * first_available_task(lv_layer_t * layer)
{
    lv_draw_task_t * task = layer->draw_task_head;
    if(task != NULL && task->state != LV_DRAW_TASK_STATE_QUEUED) return NULL;
    return task;
}

static bool task_is_independent(lv_layer_t * layer, lv_draw_task_t * candidate)
{
    lv_draw_task_t * older = layer->draw_task_head;

    while(older != NULL && older != candidate) {
        if(older->state != LV_DRAW_TASK_STATE_READY) {
            lv_area_t intersection;
            if(lv_area_intersect(&intersection, &older->_real_area,
                                 &candidate->_real_area)) {
                return false;
            }
        }
        older = older->next;
    }
    return older == candidate;
}

lv_draw_task_t * lv_draw_get_available_task(lv_layer_t * layer,
                                             lv_draw_task_t * previous,
                                             uint8_t draw_unit_id)
{
    lv_draw_global_info_t * draw_info;
    lv_draw_task_t * task;

    if(layer == NULL) return NULL;
    draw_info = &LV_GLOBAL_DEFAULT()->draw_info;
    if(draw_info->unit_cnt == 1U) return first_available_task(layer);

    task = layer->draw_task_head;
    if(task != NULL) {
        const lv_display_t * display = LV_GLOBAL_DEFAULT()->disp_refresh;
        const int32_t horizontal = horizontal_resolution(display);
        const int32_t vertical = vertical_resolution(display);

        if(task->state != LV_DRAW_TASK_STATE_QUEUED &&
           task->area.x1 <= 0 && task->area.x2 >= horizontal - 1 &&
           task->area.y1 <= 0 && task->area.y2 >= vertical - 1) {
            return NULL;
        }
    }

    task = previous != NULL ? previous->next : layer->draw_task_head;
    while(task != NULL) {
        if(task->state == LV_DRAW_TASK_STATE_QUEUED &&
           (task->preferred_draw_unit_id == LV_DRAW_UNIT_NONE ||
            task->preferred_draw_unit_id == draw_unit_id) &&
           task_is_independent(layer, task)) {
            return task;
        }
        task = task->next;
    }
    return NULL;
}
