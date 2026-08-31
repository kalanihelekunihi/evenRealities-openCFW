/* SPDX-License-Identifier: MIT */
/* Exact lifecycle subset of authenticated LVGL lv_draw_vector.c. */
#include "lvgl_ambiq_lvgl_vector_destroy_provider.h"

#include "src/stdlib/lv_mem.h"

#include <stddef.h>
#include <stdint.h>

typedef struct {
    lv_vector_path_t * path;
    lv_vector_draw_dsc_t dsc;
} open_cfw_vector_draw_task_t;

static lv_ll_node_t * open_cfw_next(const lv_ll_t * list, const void * node)
{
    const uint8_t * bytes = (const uint8_t *)node;
    return *(lv_ll_node_t * const *)(bytes + list->n_size + sizeof(lv_ll_node_t *));
}

static void open_cfw_set_previous(const lv_ll_t * list, void * node,
                                  lv_ll_node_t * previous)
{
    uint8_t * bytes = (uint8_t *)node;
    *(lv_ll_node_t **)(bytes + list->n_size) = previous;
}

static void open_cfw_vector_path_delete(lv_vector_path_t * path)
{
    lv_array_deinit(&path->ops);
    lv_array_deinit(&path->points);
    lv_free(path);
}

void lv_vector_for_each_destroy_tasks(lv_ll_t * task_list,
                                      vector_draw_task_cb callback,
                                      void * data)
{
    open_cfw_vector_draw_task_t * task;

    if(task_list == NULL) return;
    task = (open_cfw_vector_draw_task_t *)task_list->head;
    while(task != NULL) {
        open_cfw_vector_draw_task_t * next =
            (open_cfw_vector_draw_task_t *)open_cfw_next(task_list, task);

        task_list->head = (lv_ll_node_t *)next;
        if(next != NULL) open_cfw_set_previous(task_list, next, NULL);
        else task_list->tail = NULL;

        if(callback != NULL) callback(data, task->path, &task->dsc);
        if(task->path != NULL) open_cfw_vector_path_delete(task->path);
        lv_array_deinit(&task->dsc.stroke_dsc.dash_pattern);
        lv_free(task);
        task = next;
    }
    lv_free(task_list);
}
