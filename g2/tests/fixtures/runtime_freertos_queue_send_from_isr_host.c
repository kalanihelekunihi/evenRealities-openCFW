/* SPDX-License-Identifier: MIT */

#include <setjmp.h>
#include <stdint.h>
#include <string.h>

#include "../../components/shared/freertos/runtime_freertos_queue_next_closure.h"

enum { HOST_ASSERTED = 0x80000000U, HOST_STORAGE = 16U };

static struct open_cfw_freertos_queue_next_control host_queue;
static uint8_t host_storage[HOST_STORAGE];
static uint8_t host_item[4];
static uint8_t host_tcb[0x70];
static uint8_t host_other_tcb[0x70];
static uint8_t host_ready_lists[56U * 0x14U];
static uint32_t host_top_ready;
static uint32_t host_task_count;
static int32_t host_remove_result;
static int32_t host_woken;
static uint32_t host_set_mask_calls;
static uint32_t host_clear_mask_calls;
static uint32_t host_copy_calls;
static uint32_t host_remove_calls;
static uint32_t host_insert_calls;
static uint32_t host_assert_calls;
static uint32_t host_trace_calls;
static uint32_t host_failed_calls;
static void *host_removed_item;
static void *host_inserted_item;
static void *host_inserted_list;
static void *host_current_tcb;
static int host_active;
static jmp_buf host_jump;

static uint32_t host_u32(void *base, uint32_t offset)
{
    uint32_t value;
    memcpy(&value, (uint8_t *)base + offset, sizeof(value));
    return value;
}

static void host_set_u32(void *base, uint32_t offset, uint32_t value)
{
    memcpy((uint8_t *)base + offset, &value, sizeof(value));
}

static void host_assert(int condition)
{
    if (!condition) {
        ++host_assert_calls;
        if (host_active != 0) {
            longjmp(host_jump, 1);
        }
    }
}

static uint32_t host_set_mask(void)
{
    ++host_set_mask_calls;
    return 0x5AU;
}

static void host_clear_mask(uint32_t value)
{
    host_assert(value == 0x5AU);
    ++host_clear_mask_calls;
}

static uint32_t host_get_task_count(void)
{
    return host_task_count;
}

static void host_trace(struct open_cfw_freertos_queue_next_control *queue)
{
    host_assert(queue == &host_queue);
    ++host_trace_calls;
}

static void host_trace_failed(
    struct open_cfw_freertos_queue_next_control *queue
)
{
    host_assert(queue == &host_queue);
    ++host_failed_calls;
}

#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_SET_MASK
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_CLEAR_MASK
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_TASK_COUNT_LOAD
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_TRACE_SEND_FROM_ISR
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_TRACE_SEND_FROM_ISR_FAILED
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_SET_MASK() host_set_mask()
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_CLEAR_MASK(value) host_clear_mask(value)
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_TASK_COUNT_LOAD() host_get_task_count()
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(condition) host_assert(condition)
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_TRACE_SEND_FROM_ISR(queue) \
    host_trace(queue)
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_TRACE_SEND_FROM_ISR_FAILED(queue) \
    host_trace_failed(queue)

#define OPEN_CFW_FREERTOS_DISINHERIT_CURRENT_TCB() host_current_tcb
#define OPEN_CFW_FREERTOS_DISINHERIT_TOP_READY() host_top_ready
#define OPEN_CFW_FREERTOS_DISINHERIT_READY_LIST(priority) \
    ((void *)(host_ready_lists + ((priority) * 0x14U)))
#define OPEN_CFW_FREERTOS_DISINHERIT_ASSERT(condition) host_assert(condition)

uint32_t open_cfw_freertos_list_remove(void *item)
{
    ++host_remove_calls;
    host_removed_item = item;
    return 0U;
}

void open_cfw_freertos_list_insert_end(void *list, void *item)
{
    ++host_insert_calls;
    host_inserted_list = list;
    host_inserted_item = item;
}

open_cfw_freertos_queue_next_base_type
open_cfw_freertos_task_remove_from_event_list(
    const struct open_cfw_freertos_queue_next_list *list
)
{
    (void)list;
    ++host_remove_calls;
    return host_remove_result;
}

void __aeabi_memcpy(void *destination, const void *source, uint32_t size)
{
    ++host_copy_calls;
    memcpy(destination, source, size);
}

#include "../../components/shared/freertos/runtime_freertos_task_priority_disinherit.c"
#include "../../components/shared/freertos/runtime_freertos_queue_copy_data_to_queue.c"
#include "../../components/shared/freertos/runtime_freertos_queue_generic_send_from_isr.c"

void open_cfw_send_isr_host_reset(
    uint32_t messages,
    uint32_t length,
    int32_t transmit_lock,
    uint32_t task_count,
    int32_t remove_result
)
{
    uint32_t index;
    memset(&host_queue, 0, sizeof(host_queue));
    memset(host_storage, 0, sizeof(host_storage));
    memset(host_tcb, 0, sizeof(host_tcb));
    memset(host_other_tcb, 0, sizeof(host_other_tcb));
    memset(host_ready_lists, 0, sizeof(host_ready_lists));
    for (index = 0U; index < sizeof(host_item); ++index) {
        host_item[index] = (uint8_t)(0xA0U + index);
    }
    host_queue.head = (int8_t *)host_storage;
    host_queue.write_to = (int8_t *)host_storage;
    host_queue.value.queue.tail = (int8_t *)(host_storage + HOST_STORAGE);
    host_queue.value.queue.read_from = (int8_t *)host_storage;
    host_queue.messages_waiting = messages;
    host_queue.length = length;
    host_queue.item_size = 4U;
    host_queue.transmit_lock = (int8_t)transmit_lock;
    host_task_count = task_count;
    host_remove_result = remove_result;
    host_woken = 0;
    host_set_mask_calls = 0U;
    host_clear_mask_calls = 0U;
    host_copy_calls = 0U;
    host_remove_calls = 0U;
    host_insert_calls = 0U;
    host_assert_calls = 0U;
    host_trace_calls = 0U;
    host_failed_calls = 0U;
    host_removed_item = 0;
    host_inserted_item = 0;
    host_inserted_list = 0;
    host_current_tcb = host_tcb;
    host_top_ready = 0U;
    host_active = 0;
}

void open_cfw_send_isr_host_set_write_offset(uint32_t offset)
{
    host_queue.write_to = (int8_t *)(host_storage + offset);
}

void open_cfw_send_isr_host_set_read_offset(uint32_t offset)
{
    host_queue.value.queue.read_from = (int8_t *)(host_storage + offset);
}

void open_cfw_send_isr_host_set_waiters(uint32_t count)
{
    host_queue.tasks_waiting_to_receive.item_count = count;
}

static int32_t host_send(
    struct open_cfw_freertos_queue_next_control *queue,
    uint32_t use_item,
    uint32_t use_flag,
    int32_t position
)
{
    int32_t result;
    host_active = 1;
    if (setjmp(host_jump) != 0) {
        host_active = 0;
        return (int32_t)HOST_ASSERTED;
    }
    result = open_cfw_freertos_queue_generic_send_from_isr(
        queue,
        use_item != 0U ? host_item : (const void *)0,
        use_flag != 0U ? &host_woken : (int32_t *)0,
        position
    );
    host_active = 0;
    return result;
}

int32_t open_cfw_send_isr_host_send(
    uint32_t use_item,
    uint32_t use_flag,
    int32_t position
)
{
    return host_send(&host_queue, use_item, use_flag, position);
}

int32_t open_cfw_send_isr_host_send_null(void)
{
    return host_send(0, 0U, 0U, 0);
}

void open_cfw_send_isr_host_priority_reset(
    uint32_t priority,
    uint32_t base_priority,
    uint32_t mutexes,
    uint32_t top_ready,
    uint32_t current_matches
)
{
    host_set_u32(host_tcb, 0x2CU, priority);
    host_set_u32(host_tcb, 0x60U, base_priority);
    host_set_u32(host_tcb, 0x64U, mutexes);
    host_top_ready = top_ready;
    host_current_tcb = current_matches != 0U ? host_tcb : host_other_tcb;
    host_remove_calls = 0U;
    host_insert_calls = 0U;
    host_assert_calls = 0U;
    host_removed_item = 0;
    host_inserted_item = 0;
    host_inserted_list = 0;
}

int32_t open_cfw_send_isr_host_disinherit(uint32_t use_holder)
{
    int32_t result;
    host_active = 1;
    if (setjmp(host_jump) != 0) {
        host_active = 0;
        return (int32_t)HOST_ASSERTED;
    }
    result = open_cfw_freertos_task_priority_disinherit(
        use_holder != 0U ? host_tcb : (void *)0
    );
    host_active = 0;
    return result;
}

uint32_t open_cfw_send_isr_host_get(uint32_t selector)
{
    switch (selector) {
        case 0: return host_queue.messages_waiting;
        case 1: return (uint32_t)(host_queue.write_to - (int8_t *)host_storage);
        case 2: return (uint32_t)(host_queue.value.queue.read_from - (int8_t *)host_storage);
        case 3: return (uint32_t)(uint8_t)host_queue.transmit_lock;
        case 4: return (uint32_t)host_woken;
        case 5: return host_set_mask_calls;
        case 6: return host_clear_mask_calls;
        case 7: return host_copy_calls;
        case 8: return host_remove_calls;
        case 9: return host_insert_calls;
        case 10: return host_assert_calls;
        case 11: return host_trace_calls;
        case 12: return host_failed_calls;
        case 13: return host_u32(host_tcb, 0x2CU);
        case 14: return host_u32(host_tcb, 0x18U);
        case 15: return host_u32(host_tcb, 0x64U);
        case 16: return host_top_ready;
        case 17: return host_removed_item == (void *)(host_tcb + 0x04U);
        case 18: return host_inserted_item == (void *)(host_tcb + 0x04U);
        case 19: return host_inserted_list == (void *)(host_ready_lists + host_u32(host_tcb, 0x2CU) * 0x14U);
        default: return 0U;
    }
}

uint32_t open_cfw_send_isr_host_storage(uint32_t index)
{
    return index < HOST_STORAGE ? host_storage[index] : 0U;
}
