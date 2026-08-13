/* SPDX-License-Identifier: MIT */

#include <setjmp.h>
#include <stdint.h>
#include <string.h>

#include "../../components/shared/freertos/runtime_freertos_queue_next_closure.h"

enum {
    OPEN_CFW_QUEUE_RX_HOST_ASSERTED = 0x80000000U,
    OPEN_CFW_QUEUE_RX_HOST_STORAGE_SIZE = 32U
};

static struct open_cfw_freertos_queue_next_control open_cfw_queue_rx_host_queue;
static uint8_t open_cfw_queue_rx_host_storage[OPEN_CFW_QUEUE_RX_HOST_STORAGE_SIZE];
static uint8_t open_cfw_queue_rx_host_output[OPEN_CFW_QUEUE_RX_HOST_STORAGE_SIZE];
static uint32_t open_cfw_queue_rx_host_task_count;
static int32_t open_cfw_queue_rx_host_remove_result;
static int32_t open_cfw_queue_rx_host_flag;
static uint32_t open_cfw_queue_rx_host_set_mask_calls;
static uint32_t open_cfw_queue_rx_host_clear_mask_calls;
static uint32_t open_cfw_queue_rx_host_clear_mask_argument;
static uint32_t open_cfw_queue_rx_host_task_count_calls;
static uint32_t open_cfw_queue_rx_host_remove_calls;
static uint32_t open_cfw_queue_rx_host_copy_calls;
static uint32_t open_cfw_queue_rx_host_copy_size;
static uint32_t open_cfw_queue_rx_host_validate_calls;
static uint32_t open_cfw_queue_rx_host_trace_calls;
static uint32_t open_cfw_queue_rx_host_trace_failed_calls;
static uint32_t open_cfw_queue_rx_host_assert_calls;
static int open_cfw_queue_rx_host_execute_active;
static jmp_buf open_cfw_queue_rx_host_assert_jump;

static uint32_t open_cfw_queue_rx_host_set_mask(void)
{
    ++open_cfw_queue_rx_host_set_mask_calls;
    return 0x5AU;
}

static void open_cfw_queue_rx_host_clear_mask(uint32_t mask)
{
    ++open_cfw_queue_rx_host_clear_mask_calls;
    open_cfw_queue_rx_host_clear_mask_argument = mask;
}

static uint32_t open_cfw_queue_rx_host_get_task_count(void)
{
    ++open_cfw_queue_rx_host_task_count_calls;
    return open_cfw_queue_rx_host_task_count;
}

static void open_cfw_queue_rx_host_assert(int condition)
{
    if (!condition) {
        ++open_cfw_queue_rx_host_assert_calls;
        (void)open_cfw_queue_rx_host_set_mask();
        if (open_cfw_queue_rx_host_execute_active != 0) {
            longjmp(open_cfw_queue_rx_host_assert_jump, 1);
        }
    }
}

static void open_cfw_queue_rx_host_validate(void)
{
    ++open_cfw_queue_rx_host_validate_calls;
}

static void open_cfw_queue_rx_host_trace(
    struct open_cfw_freertos_queue_next_control *queue
)
{
    (void)queue;
    ++open_cfw_queue_rx_host_trace_calls;
}

static void open_cfw_queue_rx_host_trace_failed(
    struct open_cfw_freertos_queue_next_control *queue
)
{
    (void)queue;
    ++open_cfw_queue_rx_host_trace_failed_calls;
}

#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_SET_MASK
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_CLEAR_MASK
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_TASK_COUNT_LOAD
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_VALIDATE_INTERRUPT_PRIORITY

#define OPEN_CFW_FREERTOS_QUEUE_NEXT_SET_MASK() \
    open_cfw_queue_rx_host_set_mask()
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_CLEAR_MASK(mask) \
    open_cfw_queue_rx_host_clear_mask(mask)
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_TASK_COUNT_LOAD() \
    open_cfw_queue_rx_host_get_task_count()
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(condition) \
    open_cfw_queue_rx_host_assert((condition))
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_VALIDATE_INTERRUPT_PRIORITY() \
    open_cfw_queue_rx_host_validate()
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TRACE(queue) \
    open_cfw_queue_rx_host_trace((queue))
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TRACE_FAILED(queue) \
    open_cfw_queue_rx_host_trace_failed((queue))

open_cfw_freertos_queue_next_base_type
open_cfw_freertos_task_remove_from_event_list(
    const struct open_cfw_freertos_queue_next_list *event_list
)
{
    (void)event_list;
    ++open_cfw_queue_rx_host_remove_calls;
    return open_cfw_queue_rx_host_remove_result;
}

void __aeabi_memcpy(void *destination, const void *source, uint32_t size)
{
    ++open_cfw_queue_rx_host_copy_calls;
    open_cfw_queue_rx_host_copy_size = size;
    memcpy(destination, source, size);
}

#include "../../components/shared/freertos/runtime_freertos_queue_copy_data_from_queue.c"
#include "../../components/shared/freertos/runtime_freertos_queue_receive_from_isr.c"

void open_cfw_queue_rx_host_reset(
    uint32_t messages,
    uint32_t item_size,
    int32_t receive_lock,
    uint32_t task_count,
    int32_t remove_result
)
{
    uint32_t index;

    memset(&open_cfw_queue_rx_host_queue, 0,
           sizeof(open_cfw_queue_rx_host_queue));
    memset(open_cfw_queue_rx_host_output, 0,
           sizeof(open_cfw_queue_rx_host_output));
    for (index = 0U; index < OPEN_CFW_QUEUE_RX_HOST_STORAGE_SIZE; ++index) {
        open_cfw_queue_rx_host_storage[index] = (uint8_t)(0x40U + index);
    }
    open_cfw_queue_rx_host_queue.head =
        (open_cfw_freertos_queue_next_int8 *)open_cfw_queue_rx_host_storage;
    open_cfw_queue_rx_host_queue.value.queue.tail =
        (open_cfw_freertos_queue_next_int8 *)
        (open_cfw_queue_rx_host_storage + OPEN_CFW_QUEUE_RX_HOST_STORAGE_SIZE);
    open_cfw_queue_rx_host_queue.value.queue.read_from =
        (open_cfw_freertos_queue_next_int8 *)open_cfw_queue_rx_host_storage;
    open_cfw_queue_rx_host_queue.messages_waiting = messages;
    open_cfw_queue_rx_host_queue.item_size = item_size;
    open_cfw_queue_rx_host_queue.receive_lock =
        (open_cfw_freertos_queue_next_int8)receive_lock;
    open_cfw_queue_rx_host_task_count = task_count;
    open_cfw_queue_rx_host_remove_result = remove_result;
    open_cfw_queue_rx_host_flag = 0;
    open_cfw_queue_rx_host_set_mask_calls = 0U;
    open_cfw_queue_rx_host_clear_mask_calls = 0U;
    open_cfw_queue_rx_host_clear_mask_argument = 0U;
    open_cfw_queue_rx_host_task_count_calls = 0U;
    open_cfw_queue_rx_host_remove_calls = 0U;
    open_cfw_queue_rx_host_copy_calls = 0U;
    open_cfw_queue_rx_host_copy_size = 0U;
    open_cfw_queue_rx_host_validate_calls = 0U;
    open_cfw_queue_rx_host_trace_calls = 0U;
    open_cfw_queue_rx_host_trace_failed_calls = 0U;
    open_cfw_queue_rx_host_assert_calls = 0U;
    open_cfw_queue_rx_host_execute_active = 0;
}

void open_cfw_queue_rx_host_set_read_offset(uint32_t offset)
{
    open_cfw_queue_rx_host_queue.value.queue.read_from =
        (open_cfw_freertos_queue_next_int8 *)
        (open_cfw_queue_rx_host_storage + offset);
}

void open_cfw_queue_rx_host_set_waiters(uint32_t count)
{
    open_cfw_queue_rx_host_queue.tasks_waiting_to_send.item_count = count;
}

static int32_t open_cfw_queue_rx_host_run(
    struct open_cfw_freertos_queue_next_control *queue,
    uint32_t use_buffer,
    uint32_t use_flag,
    int32_t initial_flag
)
{
    int32_t result;

    open_cfw_queue_rx_host_flag = initial_flag;
    open_cfw_queue_rx_host_execute_active = 1;
    if (setjmp(open_cfw_queue_rx_host_assert_jump) != 0) {
        open_cfw_queue_rx_host_execute_active = 0;
        return (int32_t)OPEN_CFW_QUEUE_RX_HOST_ASSERTED;
    }
    result = open_cfw_freertos_queue_receive_from_isr(
        queue,
        use_buffer != 0U ? open_cfw_queue_rx_host_output : (void *)0,
        use_flag != 0U ? &open_cfw_queue_rx_host_flag : (int32_t *)0
    );
    open_cfw_queue_rx_host_execute_active = 0;
    return result;
}

int32_t open_cfw_queue_rx_host_execute(
    uint32_t use_buffer,
    uint32_t use_flag,
    int32_t initial_flag
)
{
    return open_cfw_queue_rx_host_run(
        &open_cfw_queue_rx_host_queue, use_buffer, use_flag, initial_flag
    );
}

int32_t open_cfw_queue_rx_host_execute_null_queue(void)
{
    return open_cfw_queue_rx_host_run(
        (struct open_cfw_freertos_queue_next_control *)0, 0U, 0U, 0
    );
}

uint32_t open_cfw_queue_rx_host_get_output(uint32_t index)
{
    if (index >= OPEN_CFW_QUEUE_RX_HOST_STORAGE_SIZE) {
        return 0xFFFFFFFFU;
    }
    return open_cfw_queue_rx_host_output[index];
}

uint32_t open_cfw_queue_rx_host_get_read_offset(void)
{
    return (uint32_t)(
        open_cfw_queue_rx_host_queue.value.queue.read_from -
        (open_cfw_freertos_queue_next_int8 *)open_cfw_queue_rx_host_storage
    );
}

uint32_t open_cfw_queue_rx_host_get_messages(void)
{
    return open_cfw_queue_rx_host_queue.messages_waiting;
}

int32_t open_cfw_queue_rx_host_get_receive_lock(void)
{
    return open_cfw_queue_rx_host_queue.receive_lock;
}

int32_t open_cfw_queue_rx_host_get_flag(void)
{
    return open_cfw_queue_rx_host_flag;
}

#define OPEN_CFW_QUEUE_RX_HOST_GETTER(name) \
    uint32_t open_cfw_queue_rx_host_get_##name(void) \
    { \
        return open_cfw_queue_rx_host_##name; \
    }

OPEN_CFW_QUEUE_RX_HOST_GETTER(set_mask_calls)
OPEN_CFW_QUEUE_RX_HOST_GETTER(clear_mask_calls)
OPEN_CFW_QUEUE_RX_HOST_GETTER(clear_mask_argument)
OPEN_CFW_QUEUE_RX_HOST_GETTER(task_count_calls)
OPEN_CFW_QUEUE_RX_HOST_GETTER(remove_calls)
OPEN_CFW_QUEUE_RX_HOST_GETTER(copy_calls)
OPEN_CFW_QUEUE_RX_HOST_GETTER(copy_size)
OPEN_CFW_QUEUE_RX_HOST_GETTER(validate_calls)
OPEN_CFW_QUEUE_RX_HOST_GETTER(trace_calls)
OPEN_CFW_QUEUE_RX_HOST_GETTER(trace_failed_calls)
OPEN_CFW_QUEUE_RX_HOST_GETTER(assert_calls)
