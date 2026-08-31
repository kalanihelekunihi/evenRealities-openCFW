/* SPDX-License-Identifier: MIT */
#include "../../third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_freertos_queue_provider.h"

#include <stddef.h>
#include <stdint.h>

struct open_cfw_queue_create_control { uint32_t token; };
struct open_cfw_freertos_queue_next_control { uint32_t token; };
struct open_cfw_semaphore_take_queue { uint32_t token; };

static struct open_cfw_queue_create_control created_queue;
static struct open_cfw_freertos_queue_next_control give_queue;
static struct open_cfw_semaphore_take_queue take_queue;
static uint32_t create_calls;
static uint32_t give_calls;
static uint32_t take_calls;
static uint32_t last_length;
static uint32_t last_item_size;
static uint32_t last_queue_type;
static void *last_give_queue;
static int32_t *last_woken_pointer;
static void *last_take_queue;
static uint32_t last_ticks;
static int32_t woken_value;

struct open_cfw_queue_create_control *
open_cfw_freertos_queue_generic_create(
    uint32_t length,
    uint32_t item_size,
    uint8_t queue_type
)
{
    ++create_calls;
    last_length = length;
    last_item_size = item_size;
    last_queue_type = queue_type;
    return &created_queue;
}

int32_t open_cfw_freertos_queue_give_from_isr(
    struct open_cfw_freertos_queue_next_control *queue,
    int32_t *higher_priority_task_woken
)
{
    ++give_calls;
    last_give_queue = queue;
    last_woken_pointer = higher_priority_task_woken;
    if (higher_priority_task_woken != NULL) {
        *higher_priority_task_woken = 1;
    }
    return -17;
}

int32_t open_cfw_freertos_queue_semaphore_take_upstream_candidate(
    struct open_cfw_semaphore_take_queue *queue,
    uint32_t ticks_to_wait
)
{
    ++take_calls;
    last_take_queue = queue;
    last_ticks = ticks_to_wait;
    return -23;
}

void test_freertos_provider_reset(void)
{
    create_calls = 0U;
    give_calls = 0U;
    take_calls = 0U;
    last_length = 0U;
    last_item_size = 0U;
    last_queue_type = 0U;
    last_give_queue = NULL;
    last_woken_pointer = NULL;
    last_take_queue = NULL;
    last_ticks = 0U;
    woken_value = 0x5A5A5A5A;
}

uint32_t test_freertos_provider_create(
    uint32_t length,
    uint32_t item_size,
    uint32_t queue_type
)
{
    return xQueueGenericCreate(length, item_size, (uint8_t)queue_type) != NULL;
}

int32_t test_freertos_provider_give(uint32_t null_queue, uint32_t null_woken)
{
    return xQueueGiveFromISR(
        null_queue != 0U ? NULL :
            (open_cfw_lvgl_freertos_queue_handle)&give_queue,
        null_woken != 0U ? NULL : &woken_value
    );
}

int32_t test_freertos_provider_take(uint32_t null_queue, uint32_t ticks)
{
    return xQueueSemaphoreTake(
        null_queue != 0U ? NULL :
            (open_cfw_lvgl_freertos_queue_handle)&take_queue,
        ticks
    );
}

uint32_t test_freertos_provider_create_calls(void) { return create_calls; }
uint32_t test_freertos_provider_give_calls(void) { return give_calls; }
uint32_t test_freertos_provider_take_calls(void) { return take_calls; }
uint32_t test_freertos_provider_last_length(void) { return last_length; }
uint32_t test_freertos_provider_last_item_size(void) { return last_item_size; }
uint32_t test_freertos_provider_last_queue_type(void) { return last_queue_type; }
uint32_t test_freertos_provider_give_queue_is_exact(void)
{
    return last_give_queue == &give_queue;
}
uint32_t test_freertos_provider_woken_pointer_is_nonnull(void)
{
    return last_woken_pointer != NULL;
}
uint32_t test_freertos_provider_woken_pointer_is_null(void)
{
    return last_woken_pointer == NULL;
}
uint32_t test_freertos_provider_woken_value(void) { return (uint32_t)woken_value; }
uint32_t test_freertos_provider_take_queue_is_exact(void)
{
    return last_take_queue == &take_queue;
}
uint32_t test_freertos_provider_last_ticks(void) { return last_ticks; }
