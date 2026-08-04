/*
 * SPDX-License-Identifier: MIT
 *
 * Deterministic hosted graph and seam harness for the isolated
 * xQueueGiveFromISR/xTaskRemoveFromEventList source closure.
 */

#include <setjmp.h>
#include <stdint.h>
#include <string.h>

#include "../../components/shared/freertos/runtime_freertos_queue_next_closure.h"

enum {
    OPEN_CFW_QUEUE_NEXT_HOST_TASKS = 3U,
    OPEN_CFW_QUEUE_NEXT_HOST_ASSERTED = 0x80000000U,
    OPEN_CFW_QUEUE_NEXT_HOST_CONTAINER_NONE = 0U,
    OPEN_CFW_QUEUE_NEXT_HOST_CONTAINER_BLOCKED = 1U,
    OPEN_CFW_QUEUE_NEXT_HOST_CONTAINER_RECEIVE = 2U,
    OPEN_CFW_QUEUE_NEXT_HOST_CONTAINER_PENDING = 3U,
    OPEN_CFW_QUEUE_NEXT_HOST_CONTAINER_READY_BASE = 0x100U
};

static struct open_cfw_freertos_queue_next_tcb
    open_cfw_queue_next_host_tasks[OPEN_CFW_QUEUE_NEXT_HOST_TASKS];
static struct open_cfw_freertos_queue_next_control
    open_cfw_queue_next_host_queue;
static struct open_cfw_freertos_queue_next_list
    open_cfw_queue_next_host_ready[OPEN_CFW_FREERTOS_QUEUE_NEXT_MAX_PRIORITIES];
static struct open_cfw_freertos_queue_next_list
    open_cfw_queue_next_host_pending;
static struct open_cfw_freertos_queue_next_list
    open_cfw_queue_next_host_blocked;
static struct open_cfw_freertos_queue_next_list_item
    open_cfw_queue_next_host_ownerless_item;
static struct open_cfw_freertos_queue_next_tcb
    *open_cfw_queue_next_host_current;
static uint32_t open_cfw_queue_next_host_scheduler_suspended;
static uint32_t open_cfw_queue_next_host_top_ready_priority;
static int32_t open_cfw_queue_next_host_yield_pending;
static uint32_t open_cfw_queue_next_host_task_count;
static int32_t open_cfw_queue_next_host_flag;
static uint32_t open_cfw_queue_next_host_set_mask_calls;
static uint32_t open_cfw_queue_next_host_clear_mask_calls;
static uint32_t open_cfw_queue_next_host_clear_mask_argument;
static uint32_t open_cfw_queue_next_host_task_count_loads;
static uint32_t open_cfw_queue_next_host_reset_unblock_calls;
static uint32_t open_cfw_queue_next_host_reset_after_ready;
static uint32_t open_cfw_queue_next_host_validate_calls;
static uint32_t open_cfw_queue_next_host_trace_send_calls;
static uint32_t open_cfw_queue_next_host_trace_failed_calls;
static uint32_t open_cfw_queue_next_host_assert_calls;
static int open_cfw_queue_next_host_execute_active;
static jmp_buf open_cfw_queue_next_host_assert_jump;

static struct open_cfw_freertos_queue_next_list_item *
open_cfw_queue_next_host_sentinel(
    struct open_cfw_freertos_queue_next_list *list
)
{
    return (struct open_cfw_freertos_queue_next_list_item *)(void *)&list->end;
}

static void open_cfw_queue_next_host_list_initialise(
    struct open_cfw_freertos_queue_next_list *list
)
{
    struct open_cfw_freertos_queue_next_list_item *sentinel =
        open_cfw_queue_next_host_sentinel(list);

    list->item_count = 0U;
    list->index = sentinel;
    list->end.item_value = 0xFFFFFFFFU;
    list->end.next = sentinel;
    list->end.previous = sentinel;
}

static void open_cfw_queue_next_host_list_insert_end(
    struct open_cfw_freertos_queue_next_list *list,
    struct open_cfw_freertos_queue_next_list_item *item
)
{
    struct open_cfw_freertos_queue_next_list_item *index = list->index;

    item->next = index;
    item->previous = index->previous;
    index->previous->next = item;
    index->previous = item;
    item->container = list;
    ++list->item_count;
}

static uint32_t open_cfw_queue_next_host_set_mask(void)
{
    ++open_cfw_queue_next_host_set_mask_calls;
    return 0x35U;
}

static void open_cfw_queue_next_host_clear_mask(uint32_t value)
{
    ++open_cfw_queue_next_host_clear_mask_calls;
    open_cfw_queue_next_host_clear_mask_argument = value;
}

static uint32_t open_cfw_queue_next_host_task_count_load(void)
{
    ++open_cfw_queue_next_host_task_count_loads;
    return open_cfw_queue_next_host_task_count;
}

static void open_cfw_queue_next_host_reset_unblock(void)
{
    const struct open_cfw_freertos_queue_next_tcb *task =
        &open_cfw_queue_next_host_tasks[1];

    ++open_cfw_queue_next_host_reset_unblock_calls;
    if (
        task->priority < OPEN_CFW_FREERTOS_QUEUE_NEXT_MAX_PRIORITIES &&
        task->state_list_item.container ==
            &open_cfw_queue_next_host_ready[task->priority] &&
        task->event_list_item.container == 0 &&
        open_cfw_queue_next_host_ready[task->priority].item_count != 0U
    ) {
        open_cfw_queue_next_host_reset_after_ready = 1U;
    }
}

static void open_cfw_queue_next_host_validate(void)
{
    ++open_cfw_queue_next_host_validate_calls;
}

static void open_cfw_queue_next_host_trace_send(
    struct open_cfw_freertos_queue_next_control *queue
)
{
    (void)queue;
    ++open_cfw_queue_next_host_trace_send_calls;
}

static void open_cfw_queue_next_host_trace_failed(
    struct open_cfw_freertos_queue_next_control *queue
)
{
    (void)queue;
    ++open_cfw_queue_next_host_trace_failed_calls;
}

static void open_cfw_queue_next_host_assert(int condition)
{
    if (!condition) {
        ++open_cfw_queue_next_host_assert_calls;
        (void)open_cfw_queue_next_host_set_mask();
        if (open_cfw_queue_next_host_execute_active != 0) {
            longjmp(open_cfw_queue_next_host_assert_jump, 1);
        }
    }
}

#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_SET_MASK
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_CLEAR_MASK
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_TASK_COUNT_LOAD
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TCB_LOAD
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_LOAD
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_STORE
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_YIELD_PENDING_STORE
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_SCHEDULER_SUSPENDED_LOAD
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_PENDING_READY_LIST
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_READY_LIST
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_RESET_UNBLOCK
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_VALIDATE_INTERRUPT_PRIORITY
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_TRACE_SEND_FROM_ISR
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_TRACE_SEND_FROM_ISR_FAILED

#define OPEN_CFW_FREERTOS_QUEUE_NEXT_SET_MASK() \
    open_cfw_queue_next_host_set_mask()
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_CLEAR_MASK(mask) \
    open_cfw_queue_next_host_clear_mask(mask)
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_TASK_COUNT_LOAD() \
    open_cfw_queue_next_host_task_count_load()
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TCB_LOAD() \
    (open_cfw_queue_next_host_current)
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_LOAD() \
    (open_cfw_queue_next_host_top_ready_priority)
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_STORE(value) \
    (open_cfw_queue_next_host_top_ready_priority = (value))
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_YIELD_PENDING_STORE(value) \
    (open_cfw_queue_next_host_yield_pending = (value))
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_SCHEDULER_SUSPENDED_LOAD() \
    (open_cfw_queue_next_host_scheduler_suspended)
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_PENDING_READY_LIST() \
    (&open_cfw_queue_next_host_pending)
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_READY_LIST(priority) \
    (&open_cfw_queue_next_host_ready[(priority)])
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_RESET_UNBLOCK() \
    open_cfw_queue_next_host_reset_unblock()
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(condition) \
    open_cfw_queue_next_host_assert((condition))
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_VALIDATE_INTERRUPT_PRIORITY() \
    open_cfw_queue_next_host_validate()
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_TRACE_SEND_FROM_ISR(queue) \
    open_cfw_queue_next_host_trace_send((queue))
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_TRACE_SEND_FROM_ISR_FAILED(queue) \
    open_cfw_queue_next_host_trace_failed((queue))

#include "../../components/shared/freertos/runtime_freertos_queue_next_closure.c"

void open_cfw_queue_next_host_reset(
    uint32_t scheduler_suspended,
    uint32_t current_priority,
    uint32_t top_ready_priority,
    uint32_t task_count
)
{
    uint32_t index;

    memset(open_cfw_queue_next_host_tasks, 0,
           sizeof(open_cfw_queue_next_host_tasks));
    memset(&open_cfw_queue_next_host_queue, 0,
           sizeof(open_cfw_queue_next_host_queue));
    memset(&open_cfw_queue_next_host_ownerless_item, 0,
           sizeof(open_cfw_queue_next_host_ownerless_item));
    for (index = 0U;
         index < OPEN_CFW_FREERTOS_QUEUE_NEXT_MAX_PRIORITIES;
         ++index) {
        open_cfw_queue_next_host_list_initialise(
            &open_cfw_queue_next_host_ready[index]
        );
    }
    open_cfw_queue_next_host_list_initialise(
        &open_cfw_queue_next_host_pending
    );
    open_cfw_queue_next_host_list_initialise(
        &open_cfw_queue_next_host_blocked
    );
    open_cfw_queue_next_host_list_initialise(
        &open_cfw_queue_next_host_queue.tasks_waiting_to_send
    );
    open_cfw_queue_next_host_list_initialise(
        &open_cfw_queue_next_host_queue.tasks_waiting_to_receive
    );

    for (index = 0U; index < OPEN_CFW_QUEUE_NEXT_HOST_TASKS; ++index) {
        open_cfw_queue_next_host_tasks[index].state_list_item.owner =
            &open_cfw_queue_next_host_tasks[index];
        open_cfw_queue_next_host_tasks[index].event_list_item.owner =
            &open_cfw_queue_next_host_tasks[index];
    }
    open_cfw_queue_next_host_tasks[0].priority = current_priority;
    open_cfw_queue_next_host_current = &open_cfw_queue_next_host_tasks[0];
    open_cfw_queue_next_host_scheduler_suspended = scheduler_suspended;
    open_cfw_queue_next_host_top_ready_priority = top_ready_priority;
    open_cfw_queue_next_host_yield_pending = 0;
    open_cfw_queue_next_host_task_count = task_count;
    open_cfw_queue_next_host_flag = 0;
    open_cfw_queue_next_host_set_mask_calls = 0U;
    open_cfw_queue_next_host_clear_mask_calls = 0U;
    open_cfw_queue_next_host_clear_mask_argument = 0U;
    open_cfw_queue_next_host_task_count_loads = 0U;
    open_cfw_queue_next_host_reset_unblock_calls = 0U;
    open_cfw_queue_next_host_reset_after_ready = 0U;
    open_cfw_queue_next_host_validate_calls = 0U;
    open_cfw_queue_next_host_trace_send_calls = 0U;
    open_cfw_queue_next_host_trace_failed_calls = 0U;
    open_cfw_queue_next_host_assert_calls = 0U;
    open_cfw_queue_next_host_execute_active = 0;
}

void open_cfw_queue_next_host_configure_queue(
    uint32_t length,
    uint32_t messages,
    uint32_t item_size,
    uint32_t mutex_held,
    int32_t transmit_lock
)
{
    open_cfw_queue_next_host_queue.head =
        mutex_held != 0U ? (open_cfw_freertos_queue_next_int8 *)0 :
        (open_cfw_freertos_queue_next_int8 *)(uintptr_t)1U;
    open_cfw_queue_next_host_queue.value.semaphore.mutex_holder =
        mutex_held != 0U ? &open_cfw_queue_next_host_tasks[2] : (void *)0;
    open_cfw_queue_next_host_queue.length = length;
    open_cfw_queue_next_host_queue.messages_waiting = messages;
    open_cfw_queue_next_host_queue.item_size = item_size;
    open_cfw_queue_next_host_queue.receive_lock =
        OPEN_CFW_FREERTOS_QUEUE_NEXT_UNLOCKED;
    open_cfw_queue_next_host_queue.transmit_lock =
        (open_cfw_freertos_queue_next_int8)transmit_lock;
}

void open_cfw_queue_next_host_configure_mutex_alias(
    uint32_t head_is_null,
    uint32_t holder_word_is_nonnull
)
{
    open_cfw_queue_next_host_queue.head =
        head_is_null != 0U ? (open_cfw_freertos_queue_next_int8 *)0 :
        (open_cfw_freertos_queue_next_int8 *)(uintptr_t)1U;
    open_cfw_queue_next_host_queue.value.semaphore.mutex_holder =
        holder_word_is_nonnull != 0U ?
            &open_cfw_queue_next_host_tasks[2] : (void *)0;
}

void open_cfw_queue_next_host_insert_waiter(uint32_t priority)
{
    struct open_cfw_freertos_queue_next_tcb *task =
        &open_cfw_queue_next_host_tasks[1];

    task->priority = priority;
    task->state_list_item.item_value = 100U;
    task->event_list_item.item_value =
        OPEN_CFW_FREERTOS_QUEUE_NEXT_MAX_PRIORITIES - priority;
    open_cfw_queue_next_host_list_insert_end(
        &open_cfw_queue_next_host_blocked,
        &task->state_list_item
    );
    open_cfw_queue_next_host_list_insert_end(
        &open_cfw_queue_next_host_queue.tasks_waiting_to_receive,
        &task->event_list_item
    );
}

void open_cfw_queue_next_host_seed_ready(uint32_t priority)
{
    struct open_cfw_freertos_queue_next_tcb *task =
        &open_cfw_queue_next_host_tasks[2];

    if (priority >= OPEN_CFW_FREERTOS_QUEUE_NEXT_MAX_PRIORITIES) {
        return;
    }
    task->priority = priority;
    open_cfw_queue_next_host_list_insert_end(
        &open_cfw_queue_next_host_ready[priority],
        &task->state_list_item
    );
}

void open_cfw_queue_next_host_set_ready_index(
    uint32_t priority,
    uint32_t use_seed_task
)
{
    if (priority >= OPEN_CFW_FREERTOS_QUEUE_NEXT_MAX_PRIORITIES) {
        return;
    }
    open_cfw_queue_next_host_ready[priority].index =
        use_seed_task != 0U ?
            &open_cfw_queue_next_host_tasks[2].state_list_item :
            open_cfw_queue_next_host_sentinel(
                &open_cfw_queue_next_host_ready[priority]
            );
}

static int32_t open_cfw_queue_next_host_run_queue(
    struct open_cfw_freertos_queue_next_control *queue,
    uint32_t use_flag,
    int32_t initial_flag
)
{
    int32_t result;

    open_cfw_queue_next_host_flag = initial_flag;
    open_cfw_queue_next_host_execute_active = 1;
    if (setjmp(open_cfw_queue_next_host_assert_jump) != 0) {
        open_cfw_queue_next_host_execute_active = 0;
        return (int32_t)OPEN_CFW_QUEUE_NEXT_HOST_ASSERTED;
    }
    result = open_cfw_freertos_queue_give_from_isr(
        queue,
        use_flag != 0U ? &open_cfw_queue_next_host_flag : (int32_t *)0
    );
    open_cfw_queue_next_host_execute_active = 0;
    return result;
}

int32_t open_cfw_queue_next_host_execute(
    uint32_t use_flag,
    int32_t initial_flag
)
{
    return open_cfw_queue_next_host_run_queue(
        &open_cfw_queue_next_host_queue,
        use_flag,
        initial_flag
    );
}

int32_t open_cfw_queue_next_host_execute_null_queue(void)
{
    return open_cfw_queue_next_host_run_queue(
        (struct open_cfw_freertos_queue_next_control *)0,
        0U,
        0
    );
}

int32_t open_cfw_queue_next_host_execute_ownerless_remove(void)
{
    int32_t result;

    open_cfw_queue_next_host_ownerless_item.owner = (void *)0;
    open_cfw_queue_next_host_list_insert_end(
        &open_cfw_queue_next_host_queue.tasks_waiting_to_receive,
        &open_cfw_queue_next_host_ownerless_item
    );
    open_cfw_queue_next_host_execute_active = 1;
    if (setjmp(open_cfw_queue_next_host_assert_jump) != 0) {
        open_cfw_queue_next_host_execute_active = 0;
        return (int32_t)OPEN_CFW_QUEUE_NEXT_HOST_ASSERTED;
    }
    result = open_cfw_freertos_task_remove_from_event_list(
        &open_cfw_queue_next_host_queue.tasks_waiting_to_receive
    );
    open_cfw_queue_next_host_execute_active = 0;
    return result;
}

uint32_t open_cfw_queue_next_host_get_messages(void)
{
    return open_cfw_queue_next_host_queue.messages_waiting;
}

int32_t open_cfw_queue_next_host_get_transmit_lock(void)
{
    return open_cfw_queue_next_host_queue.transmit_lock;
}

int32_t open_cfw_queue_next_host_get_flag(void)
{
    return open_cfw_queue_next_host_flag;
}

int32_t open_cfw_queue_next_host_get_yield_pending(void)
{
    return open_cfw_queue_next_host_yield_pending;
}

uint32_t open_cfw_queue_next_host_get_top_ready_priority(void)
{
    return open_cfw_queue_next_host_top_ready_priority;
}

#define OPEN_CFW_QUEUE_NEXT_HOST_COUNTER_GETTER(name) \
    uint32_t open_cfw_queue_next_host_get_##name(void) \
    { \
        return open_cfw_queue_next_host_##name; \
    }

OPEN_CFW_QUEUE_NEXT_HOST_COUNTER_GETTER(set_mask_calls)
OPEN_CFW_QUEUE_NEXT_HOST_COUNTER_GETTER(clear_mask_calls)
OPEN_CFW_QUEUE_NEXT_HOST_COUNTER_GETTER(clear_mask_argument)
OPEN_CFW_QUEUE_NEXT_HOST_COUNTER_GETTER(task_count_loads)
OPEN_CFW_QUEUE_NEXT_HOST_COUNTER_GETTER(reset_unblock_calls)
OPEN_CFW_QUEUE_NEXT_HOST_COUNTER_GETTER(reset_after_ready)
OPEN_CFW_QUEUE_NEXT_HOST_COUNTER_GETTER(validate_calls)
OPEN_CFW_QUEUE_NEXT_HOST_COUNTER_GETTER(trace_send_calls)
OPEN_CFW_QUEUE_NEXT_HOST_COUNTER_GETTER(trace_failed_calls)
OPEN_CFW_QUEUE_NEXT_HOST_COUNTER_GETTER(assert_calls)

uint32_t open_cfw_queue_next_host_get_receive_count(void)
{
    return open_cfw_queue_next_host_queue.tasks_waiting_to_receive.item_count;
}

uint32_t open_cfw_queue_next_host_get_blocked_count(void)
{
    return open_cfw_queue_next_host_blocked.item_count;
}

uint32_t open_cfw_queue_next_host_get_pending_count(void)
{
    return open_cfw_queue_next_host_pending.item_count;
}

uint32_t open_cfw_queue_next_host_get_ready_count(uint32_t priority)
{
    if (priority >= OPEN_CFW_FREERTOS_QUEUE_NEXT_MAX_PRIORITIES) {
        return 0xFFFFFFFFU;
    }
    return open_cfw_queue_next_host_ready[priority].item_count;
}

static uint32_t open_cfw_queue_next_host_task_identifier(const void *owner)
{
    uint32_t identifier;

    if (owner == 0) {
        return 0xFFFFFFFFU;
    }
    for (identifier = 0U;
         identifier < OPEN_CFW_QUEUE_NEXT_HOST_TASKS;
         ++identifier) {
        if (owner == &open_cfw_queue_next_host_tasks[identifier]) {
            return identifier;
        }
    }
    return 0xFFFFFFFFU;
}

uint32_t open_cfw_queue_next_host_get_ready_head_owner(uint32_t priority)
{
    if (priority >= OPEN_CFW_FREERTOS_QUEUE_NEXT_MAX_PRIORITIES) {
        return 0xFFFFFFFFU;
    }
    return open_cfw_queue_next_host_task_identifier(
        open_cfw_queue_next_host_ready[priority].end.next->owner
    );
}

uint32_t open_cfw_queue_next_host_get_ready_tail_owner(uint32_t priority)
{
    if (priority >= OPEN_CFW_FREERTOS_QUEUE_NEXT_MAX_PRIORITIES) {
        return 0xFFFFFFFFU;
    }
    return open_cfw_queue_next_host_task_identifier(
        open_cfw_queue_next_host_ready[priority].end.previous->owner
    );
}

uint32_t open_cfw_queue_next_host_get_ready_index_owner(uint32_t priority)
{
    struct open_cfw_freertos_queue_next_list *list;

    if (priority >= OPEN_CFW_FREERTOS_QUEUE_NEXT_MAX_PRIORITIES) {
        return 0xFFFFFFFFU;
    }
    list = &open_cfw_queue_next_host_ready[priority];
    if (list->index == open_cfw_queue_next_host_sentinel(list)) {
        return 0xFFFFFFFEU;
    }
    return open_cfw_queue_next_host_task_identifier(list->index->owner);
}

static uint32_t open_cfw_queue_next_host_container(
    const struct open_cfw_freertos_queue_next_list *container
)
{
    uint32_t priority;

    if (container == 0) {
        return OPEN_CFW_QUEUE_NEXT_HOST_CONTAINER_NONE;
    }
    if (container == &open_cfw_queue_next_host_blocked) {
        return OPEN_CFW_QUEUE_NEXT_HOST_CONTAINER_BLOCKED;
    }
    if (
        container ==
        &open_cfw_queue_next_host_queue.tasks_waiting_to_receive
    ) {
        return OPEN_CFW_QUEUE_NEXT_HOST_CONTAINER_RECEIVE;
    }
    if (container == &open_cfw_queue_next_host_pending) {
        return OPEN_CFW_QUEUE_NEXT_HOST_CONTAINER_PENDING;
    }
    for (priority = 0U;
         priority < OPEN_CFW_FREERTOS_QUEUE_NEXT_MAX_PRIORITIES;
         ++priority) {
        if (container == &open_cfw_queue_next_host_ready[priority]) {
            return OPEN_CFW_QUEUE_NEXT_HOST_CONTAINER_READY_BASE + priority;
        }
    }
    return 0xFFFFFFFFU;
}

uint32_t open_cfw_queue_next_host_get_waiter_state_container(void)
{
    return open_cfw_queue_next_host_container(
        open_cfw_queue_next_host_tasks[1].state_list_item.container
    );
}

uint32_t open_cfw_queue_next_host_get_waiter_event_container(void)
{
    return open_cfw_queue_next_host_container(
        open_cfw_queue_next_host_tasks[1].event_list_item.container
    );
}
