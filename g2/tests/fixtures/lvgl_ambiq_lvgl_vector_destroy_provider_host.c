/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_vector_destroy_provider.h"

#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    lv_vector_path_t * path;
    lv_vector_draw_dsc_t dsc;
} test_task_t;

static void * freed[32];
static unsigned free_count;
static lv_ll_t * active_list;
static lv_vector_path_t * callback_paths[3];
static unsigned callback_count;

void lv_free(void * pointer)
{
    assert(pointer != NULL);
    assert(free_count < sizeof(freed) / sizeof(freed[0]));
    freed[free_count++] = pointer;
    free(pointer);
}

void lv_array_deinit(lv_array_t * array)
{
    if(array->data != NULL) {
        if(array->inner_alloc) lv_free(array->data);
        array->data = NULL;
    }
    array->size = 0U;
    array->capacity = 0U;
}

static bool was_freed(const void * pointer)
{
    unsigned index;
    for(index = 0U; index < free_count; index++) {
        if(freed[index] == pointer) return true;
    }
    return false;
}

static test_task_t * make_task(lv_ll_t * list, test_task_t * previous)
{
    size_t bytes = list->n_size + 2U * sizeof(lv_ll_node_t *);
    test_task_t * task = calloc(1U, bytes);
    uint8_t * metadata;
    assert(task != NULL);
    metadata = (uint8_t *)task + list->n_size;
    memcpy(metadata, &previous, sizeof(previous));
    if(previous != NULL) {
        uint8_t * prior_next = (uint8_t *)previous + list->n_size +
                               sizeof(lv_ll_node_t *);
        memcpy(prior_next, &task, sizeof(task));
    }
    else list->head = (lv_ll_node_t *)task;
    list->tail = (lv_ll_node_t *)task;
    return task;
}

static lv_vector_path_t * make_path(bool owned_ops, bool owned_points)
{
    lv_vector_path_t * path = calloc(1U, sizeof(*path));
    assert(path != NULL);
    if(owned_ops) {
        path->ops.data = malloc(8U);
        assert(path->ops.data != NULL);
        path->ops.inner_alloc = true;
        path->ops.capacity = 8U;
    }
    if(owned_points) {
        path->points.data = malloc(8U);
        assert(path->points.data != NULL);
        path->points.inner_alloc = true;
        path->points.capacity = 1U;
    }
    return path;
}

static void callback(void * data, const lv_vector_path_t * path,
                     const lv_vector_draw_dsc_t * descriptor)
{
    unsigned * cookie = data;
    assert(cookie != NULL && *cookie == 0xA55AU);
    assert(descriptor != NULL);
    assert(active_list != NULL);
    assert(active_list->head != (const lv_ll_node_t *)descriptor);
    assert(callback_count < 3U);
    assert(path == callback_paths[callback_count]);
    callback_count++;
}

static void test_owned_lifecycle_and_order(void)
{
    lv_ll_t * list = calloc(1U, sizeof(*list));
    test_task_t * first;
    test_task_t * second;
    test_task_t * third;
    lv_vector_path_t * first_path;
    lv_vector_path_t * third_path;
    void * first_ops;
    void * first_dash;
    void * third_points;
    unsigned cookie = 0xA55AU;

    assert(list != NULL);
    list->n_size = (uint32_t)((sizeof(test_task_t) + sizeof(void *) - 1U) &
                              ~(sizeof(void *) - 1U));
    first = make_task(list, NULL);
    second = make_task(list, first);
    third = make_task(list, second);
    first_path = make_path(true, false);
    third_path = make_path(false, true);
    first->path = first_path;
    third->path = third_path;
    first->dsc.stroke_dsc.dash_pattern.data = malloc(12U);
    assert(first->dsc.stroke_dsc.dash_pattern.data != NULL);
    first->dsc.stroke_dsc.dash_pattern.inner_alloc = true;
    first->dsc.stroke_dsc.dash_pattern.capacity = 3U;
    second->dsc.stroke_dsc.dash_pattern.data = (uint8_t *)&cookie;
    second->dsc.stroke_dsc.dash_pattern.inner_alloc = false;
    second->dsc.stroke_dsc.dash_pattern.capacity = 1U;
    first_ops = first_path->ops.data;
    first_dash = first->dsc.stroke_dsc.dash_pattern.data;
    third_points = third_path->points.data;
    callback_paths[0] = first_path;
    callback_paths[1] = NULL;
    callback_paths[2] = third_path;
    active_list = list;
    callback_count = 0U;
    free_count = 0U;

    lv_vector_for_each_destroy_tasks(list, callback, &cookie);
    assert(callback_count == 3U);
    assert(free_count == 9U);
    assert(was_freed(first_ops));
    assert(was_freed(first_path));
    assert(was_freed(first_dash));
    assert(was_freed(first));
    assert(was_freed(second));
    assert(was_freed(third_points));
    assert(was_freed(third_path));
    assert(was_freed(third));
    assert(was_freed(list));
    active_list = NULL;
}

static void test_null_and_empty(void)
{
    lv_ll_t * empty;
    free_count = 0U;
    lv_vector_for_each_destroy_tasks(NULL, callback, NULL);
    assert(free_count == 0U);

    empty = calloc(1U, sizeof(*empty));
    assert(empty != NULL);
    empty->n_size = sizeof(test_task_t);
    lv_vector_for_each_destroy_tasks(empty, NULL, NULL);
    assert(free_count == 1U && was_freed(empty));
}

int main(void)
{
    test_owned_lifecycle_and_order();
    test_null_and_empty();
    return 0;
}
