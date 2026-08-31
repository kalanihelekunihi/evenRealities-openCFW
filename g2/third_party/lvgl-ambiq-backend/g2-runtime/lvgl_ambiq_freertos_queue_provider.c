/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_freertos_queue_provider.h"

#include <stddef.h>
#include <stdint.h>

/*
 * Exact FreeRTOS V10.5.1 public-ABI adapters for the source-qualified G2
 * Queue_t implementation.  Invalid constructor arithmetic and null queue
 * handles fail closed before reaching the stock-compatible assertion seams.
 */
enum {
    OPEN_CFW_LVGL_FREERTOS_QUEUE_CONTROL_SIZE = 0x50U,
    OPEN_CFW_LVGL_FREERTOS_FAIL = 0
};

struct open_cfw_queue_create_control;
struct open_cfw_freertos_queue_next_control;
struct open_cfw_semaphore_take_queue;

struct open_cfw_queue_create_control *
open_cfw_freertos_queue_generic_create(
    uint32_t length,
    uint32_t item_size,
    uint8_t queue_type
);

int32_t open_cfw_freertos_queue_give_from_isr(
    struct open_cfw_freertos_queue_next_control *queue,
    int32_t *higher_priority_task_woken
);

int32_t open_cfw_freertos_queue_semaphore_take_upstream_candidate(
    struct open_cfw_semaphore_take_queue *queue,
    uint32_t ticks_to_wait
);

open_cfw_lvgl_freertos_queue_handle xQueueGenericCreate(
    open_cfw_lvgl_freertos_ubase_type length,
    open_cfw_lvgl_freertos_ubase_type item_size,
    uint8_t queue_type
)
{
    uint32_t payload_size;

    if (length == 0U) {
        return NULL;
    }
    if ((item_size != 0U) && (length > (UINT32_MAX / item_size))) {
        return NULL;
    }
    payload_size = length * item_size;
    if (payload_size >
        (UINT32_MAX - OPEN_CFW_LVGL_FREERTOS_QUEUE_CONTROL_SIZE)) {
        return NULL;
    }

    return (open_cfw_lvgl_freertos_queue_handle)
        open_cfw_freertos_queue_generic_create(length, item_size, queue_type);
}

open_cfw_lvgl_freertos_base_type xQueueGiveFromISR(
    open_cfw_lvgl_freertos_queue_handle queue,
    open_cfw_lvgl_freertos_base_type *higher_priority_task_woken
)
{
    int32_t internal_woken;
    int32_t *internal_woken_pointer = NULL;
    int32_t result;

    if (queue == NULL) {
        return OPEN_CFW_LVGL_FREERTOS_FAIL;
    }
    if (higher_priority_task_woken != NULL) {
        internal_woken = (int32_t)*higher_priority_task_woken;
        internal_woken_pointer = &internal_woken;
    }
    result = open_cfw_freertos_queue_give_from_isr(
        (struct open_cfw_freertos_queue_next_control *)queue,
        internal_woken_pointer
    );
    if (higher_priority_task_woken != NULL) {
        *higher_priority_task_woken =
            (open_cfw_lvgl_freertos_base_type)internal_woken;
    }
    return (open_cfw_lvgl_freertos_base_type)result;
}

open_cfw_lvgl_freertos_base_type xQueueSemaphoreTake(
    open_cfw_lvgl_freertos_queue_handle queue,
    open_cfw_lvgl_freertos_tick_type ticks_to_wait
)
{
    if (queue == NULL) {
        return OPEN_CFW_LVGL_FREERTOS_FAIL;
    }
    return open_cfw_freertos_queue_semaphore_take_upstream_candidate(
        (struct open_cfw_semaphore_take_queue *)queue,
        ticks_to_wait
    );
}
