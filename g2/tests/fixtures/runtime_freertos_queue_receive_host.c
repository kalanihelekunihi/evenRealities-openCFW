/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <string.h>

#include "../../components/shared/freertos/runtime_freertos_queue_receive.h"

static struct open_cfw_freertos_queue_next_tcb host_tcb;
static struct open_cfw_freertos_queue_next_list host_delayed;
static struct open_cfw_freertos_queue_next_list host_overflow;
static struct open_cfw_freertos_queue_next_list host_suspended;
static open_cfw_freertos_queue_next_tick_type host_tick, host_next_unblock;
static uint32_t host_insert_calls, host_remove_calls, host_remove_event_calls;
static uint32_t host_missed_yields, host_yields, host_enter, host_exit;
static uint32_t host_set_timeout, host_suspend, host_resume;
static int host_scheduler_state = 1, host_timeout_result, host_empty = 1;
static int host_resume_result = 1, host_remove_event_result;
static struct open_cfw_freertos_queue_next_list *host_last_insert_list;

#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TCB_LOAD
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TCB_LOAD() (&host_tcb)
#undef OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TICK_COUNT_LOAD
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TICK_COUNT_LOAD() (host_tick)
#undef OPEN_CFW_FREERTOS_QUEUE_RECEIVE_DELAYED_LIST_LOAD
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_DELAYED_LIST_LOAD() (&host_delayed)
#undef OPEN_CFW_FREERTOS_QUEUE_RECEIVE_OVERFLOW_LIST_LOAD
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_OVERFLOW_LIST_LOAD() (&host_overflow)
#undef OPEN_CFW_FREERTOS_QUEUE_RECEIVE_SUSPENDED_LIST
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_SUSPENDED_LIST() (&host_suspended)
#undef OPEN_CFW_FREERTOS_QUEUE_RECEIVE_NEXT_UNBLOCK_LOAD
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_NEXT_UNBLOCK_LOAD() (host_next_unblock)
#undef OPEN_CFW_FREERTOS_QUEUE_RECEIVE_NEXT_UNBLOCK_STORE
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_NEXT_UNBLOCK_STORE(value) \
    (host_next_unblock = (value))
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(condition) do { if (!(condition)) __builtin_trap(); } while (0)

static void host_list_init(struct open_cfw_freertos_queue_next_list *list)
{
    memset(list, 0, sizeof(*list));
    list->index = (struct open_cfw_freertos_queue_next_list_item *)&list->end;
    list->end.next = (struct open_cfw_freertos_queue_next_list_item *)&list->end;
    list->end.previous = (struct open_cfw_freertos_queue_next_list_item *)&list->end;
}

void open_cfw_freertos_list_insert(
    struct open_cfw_freertos_queue_next_list *list,
    struct open_cfw_freertos_queue_next_list_item *item
)
{
    ++host_insert_calls; host_last_insert_list = list;
    item->container = list; ++list->item_count;
}
open_cfw_freertos_queue_next_ubase_type open_cfw_freertos_list_remove(
    struct open_cfw_freertos_queue_next_list_item *item
)
{
    ++host_remove_calls; item->container = 0; return 0U;
}
void open_cfw_freertos_port_enter_critical(void) { ++host_enter; }
void open_cfw_freertos_port_exit_critical(void) { ++host_exit; }
void open_cfw_freertos_task_missed_yield(void) { ++host_missed_yields; }
void open_cfw_freertos_task_internal_set_timeout_state(
    struct open_cfw_freertos_queue_receive_timeout *timeout
) { ++host_set_timeout; timeout->overflow_count = 0; timeout->time_on_entering = host_tick; }
void open_cfw_freertos_task_suspend_all(void) { ++host_suspend; }
open_cfw_freertos_queue_next_base_type open_cfw_freertos_task_check_for_timeout(
    struct open_cfw_freertos_queue_receive_timeout *timeout,
    open_cfw_freertos_queue_next_tick_type *ticks
) { (void)timeout; (void)ticks; return host_timeout_result; }
open_cfw_freertos_queue_next_base_type open_cfw_freertos_queue_is_empty(
    const struct open_cfw_freertos_queue_next_control *queue
) { (void)queue; return host_empty; }
open_cfw_freertos_queue_next_base_type open_cfw_freertos_task_resume_all(void)
{ ++host_resume; return host_resume_result; }
void open_cfw_freertos_port_yield(void) { ++host_yields; }
open_cfw_freertos_queue_next_base_type open_cfw_freertos_task_get_scheduler_state(void)
{ return host_scheduler_state; }
void open_cfw_freertos_queue_copy_data_from_queue(
    struct open_cfw_freertos_queue_next_control *queue, void *buffer
) { *(uint32_t *)buffer = *(uint32_t *)queue->value.queue.read_from; }
open_cfw_freertos_queue_next_base_type open_cfw_freertos_task_remove_from_event_list(
    const struct open_cfw_freertos_queue_next_list *list
) { (void)list; ++host_remove_event_calls; return host_remove_event_result; }

#include "../../components/shared/freertos/runtime_freertos_queue_receive.c"

void open_cfw_queue_receive_host_reset(void)
{
    memset(&host_tcb, 0, sizeof(host_tcb)); host_list_init(&host_delayed);
    host_list_init(&host_overflow); host_list_init(&host_suspended);
    host_tick = 100U; host_next_unblock = UINT32_MAX;
    host_insert_calls = host_remove_calls = host_remove_event_calls = 0U;
    host_missed_yields = host_yields = host_enter = host_exit = 0U;
    host_set_timeout = host_suspend = host_resume = 0U;
    host_scheduler_state = 1; host_timeout_result = 0; host_empty = 1;
    host_resume_result = 1; host_remove_event_result = 0;
    host_last_insert_list = 0;
}
uintptr_t open_cfw_queue_receive_host_delayed(uint32_t ticks, int can_block)
{
    open_cfw_freertos_task_add_current_to_delayed_list(ticks, can_block);
    if (host_tcb.state_list_item.container == &host_suspended) return 3U;
    if (host_last_insert_list == &host_delayed) return 1U;
    if (host_last_insert_list == &host_overflow) return 2U;
    return 0U;
}
int open_cfw_queue_receive_host_immediate(uint32_t waiting, uint32_t timeout)
{
    struct open_cfw_freertos_queue_next_control queue;
    uint32_t value = 0xA55AA55AU, out = 0U;
    memset(&queue, 0, sizeof(queue)); queue.item_size = 4U;
    queue.messages_waiting = waiting; queue.value.queue.read_from = (int8_t *)&value;
    queue.receive_lock = queue.transmit_lock = -1;
    return open_cfw_freertos_queue_receive(&queue, &out, timeout) * 2 +
        (out == value ? 1 : 0);
}
int open_cfw_queue_receive_host_timeout(void)
{
    struct open_cfw_freertos_queue_next_control queue;
    uint32_t out = 0U; memset(&queue, 0, sizeof(queue)); queue.item_size = 4U;
    queue.receive_lock = queue.transmit_lock = -1; host_timeout_result = 1;
    return open_cfw_freertos_queue_receive(&queue, &out, 5U);
}
uintptr_t open_cfw_queue_receive_host_get(uint32_t selector)
{
    switch (selector) {
        case 0: return host_insert_calls; case 1: return host_remove_calls;
        case 2: return host_tick; case 3: return host_next_unblock;
        case 4: return host_set_timeout; case 5: return host_suspend;
        case 6: return host_resume; case 7: return host_enter;
        case 8: return host_exit; default: return 0U;
    }
}
