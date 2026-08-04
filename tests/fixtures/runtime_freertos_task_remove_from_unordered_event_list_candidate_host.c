/* SPDX-License-Identifier: MIT */

#include <setjmp.h>
#include <stdint.h>
#include <string.h>

#include "../../components/shared/freertos/runtime_freertos_task_remove_from_unordered_event_list.h"

enum {
    OPEN_CFW_UNORDERED_HOST_TASKS = 3U,
    OPEN_CFW_UNORDERED_HOST_ASSERTED = 0x80000000U,
    OPEN_CFW_UNORDERED_HOST_SENTINEL = 0xFFFFFFFEU,
    OPEN_CFW_UNORDERED_HOST_NULL = 0xFFFFFFFFU,
    OPEN_CFW_UNORDERED_HOST_BLOCKED = 0U,
    OPEN_CFW_UNORDERED_HOST_EVENT = 0x200U,
    OPEN_CFW_UNORDERED_HOST_READY_BASE = 0x100U
};

static struct open_cfw_freertos_unordered_tcb
    open_cfw_unordered_host_tasks[OPEN_CFW_UNORDERED_HOST_TASKS];
static struct open_cfw_freertos_unordered_list
    open_cfw_unordered_host_ready[OPEN_CFW_FREERTOS_UNORDERED_MAX_PRIORITIES];
static struct open_cfw_freertos_unordered_list
    open_cfw_unordered_host_blocked;
static struct open_cfw_freertos_unordered_list
    open_cfw_unordered_host_event;
static struct open_cfw_freertos_unordered_tcb
    *open_cfw_unordered_host_current;
static uint32_t open_cfw_unordered_host_scheduler_suspended;
static uint32_t open_cfw_unordered_host_top_ready_priority;
static int32_t open_cfw_unordered_host_yield_pending;
static uint32_t open_cfw_unordered_host_next_unblock_time;
static uint32_t open_cfw_unordered_host_reset_calls;
static uint32_t open_cfw_unordered_host_reset_before_state_remove;
static uint32_t open_cfw_unordered_host_trace_calls;
static uint32_t open_cfw_unordered_host_assert_calls;
static int open_cfw_unordered_host_execute_active;
static jmp_buf open_cfw_unordered_host_assert_jump;

static struct open_cfw_freertos_unordered_list_item *
open_cfw_unordered_host_sentinel(
    struct open_cfw_freertos_unordered_list *list
)
{
    return (struct open_cfw_freertos_unordered_list_item *)(void *)&list->end;
}

static void open_cfw_unordered_host_list_initialise(
    struct open_cfw_freertos_unordered_list *list
)
{
    struct open_cfw_freertos_unordered_list_item *sentinel =
        open_cfw_unordered_host_sentinel(list);

    list->item_count = 0U;
    list->index = sentinel;
    list->end.item_value = 0xFFFFFFFFU;
    list->end.next = sentinel;
    list->end.previous = sentinel;
}

static void open_cfw_unordered_host_list_insert_end(
    struct open_cfw_freertos_unordered_list *list,
    struct open_cfw_freertos_unordered_list_item *item
)
{
    struct open_cfw_freertos_unordered_list_item *index = list->index;

    item->next = index;
    item->previous = index->previous;
    index->previous->next = item;
    index->previous = item;
    item->container = list;
    ++list->item_count;
}

static uint32_t open_cfw_unordered_host_assert_mask(void)
{
    return 0x35U;
}

static void open_cfw_unordered_host_assert(int condition)
{
    if (!condition) {
        ++open_cfw_unordered_host_assert_calls;
        (void)open_cfw_unordered_host_assert_mask();
        if (open_cfw_unordered_host_execute_active != 0) {
            longjmp(open_cfw_unordered_host_assert_jump, 1);
        }
    }
}

static void open_cfw_unordered_host_reset_next(void)
{
    struct open_cfw_freertos_unordered_list_item *sentinel =
        open_cfw_unordered_host_sentinel(&open_cfw_unordered_host_blocked);
    struct open_cfw_freertos_unordered_list_item *head =
        open_cfw_unordered_host_blocked.end.next;

    ++open_cfw_unordered_host_reset_calls;
    open_cfw_unordered_host_reset_before_state_remove =
        open_cfw_unordered_host_tasks[1].state_list_item.container ==
            &open_cfw_unordered_host_blocked ? 1U : 0U;
    open_cfw_unordered_host_next_unblock_time =
        head == sentinel ? 0xFFFFFFFFU : head->item_value;
}

static void open_cfw_unordered_host_trace(
    struct open_cfw_freertos_unordered_tcb *task
)
{
    (void)task;
    ++open_cfw_unordered_host_trace_calls;
}

#undef OPEN_CFW_FREERTOS_UNORDERED_ASSERT_MASK
#undef OPEN_CFW_FREERTOS_UNORDERED_ASSERT
#undef OPEN_CFW_FREERTOS_UNORDERED_RESET_NEXT_UNBLOCK
#undef OPEN_CFW_FREERTOS_UNORDERED_SCHEDULER_SUSPENDED_LOAD
#undef OPEN_CFW_FREERTOS_UNORDERED_CURRENT_TCB_LOAD
#undef OPEN_CFW_FREERTOS_UNORDERED_TOP_READY_PRIORITY_LOAD
#undef OPEN_CFW_FREERTOS_UNORDERED_TOP_READY_PRIORITY_STORE
#undef OPEN_CFW_FREERTOS_UNORDERED_YIELD_PENDING_STORE
#undef OPEN_CFW_FREERTOS_UNORDERED_READY_LIST
#undef OPEN_CFW_FREERTOS_UNORDERED_TRACE_MOVED_TO_READY

#define OPEN_CFW_FREERTOS_UNORDERED_ASSERT_MASK() \
    open_cfw_unordered_host_assert_mask()
#define OPEN_CFW_FREERTOS_UNORDERED_ASSERT(condition) \
    open_cfw_unordered_host_assert((condition))
#define OPEN_CFW_FREERTOS_UNORDERED_RESET_NEXT_UNBLOCK() \
    open_cfw_unordered_host_reset_next()
#define OPEN_CFW_FREERTOS_UNORDERED_SCHEDULER_SUSPENDED_LOAD() \
    (open_cfw_unordered_host_scheduler_suspended)
#define OPEN_CFW_FREERTOS_UNORDERED_CURRENT_TCB_LOAD() \
    (open_cfw_unordered_host_current)
#define OPEN_CFW_FREERTOS_UNORDERED_TOP_READY_PRIORITY_LOAD() \
    (open_cfw_unordered_host_top_ready_priority)
#define OPEN_CFW_FREERTOS_UNORDERED_TOP_READY_PRIORITY_STORE(value) \
    (open_cfw_unordered_host_top_ready_priority = (value))
#define OPEN_CFW_FREERTOS_UNORDERED_YIELD_PENDING_STORE(value) \
    (open_cfw_unordered_host_yield_pending = (value))
#define OPEN_CFW_FREERTOS_UNORDERED_READY_LIST(priority) \
    (&open_cfw_unordered_host_ready[(priority)])
#define OPEN_CFW_FREERTOS_UNORDERED_TRACE_MOVED_TO_READY(task) \
    open_cfw_unordered_host_trace((task))

#include "../../components/shared/freertos/runtime_freertos_task_remove_from_unordered_event_list.c"

void open_cfw_unordered_host_reset(
    uint32_t scheduler_suspended,
    uint32_t current_priority,
    uint32_t waiter_priority,
    uint32_t top_ready_priority,
    uint32_t wake_tick,
    uint32_t seed_ready
)
{
    uint32_t index;

    memset(open_cfw_unordered_host_tasks, 0,
           sizeof(open_cfw_unordered_host_tasks));
    for (
        index = 0U;
        index < OPEN_CFW_FREERTOS_UNORDERED_MAX_PRIORITIES;
        ++index
    ) {
        open_cfw_unordered_host_list_initialise(
            &open_cfw_unordered_host_ready[index]
        );
    }
    open_cfw_unordered_host_list_initialise(&open_cfw_unordered_host_blocked);
    open_cfw_unordered_host_list_initialise(&open_cfw_unordered_host_event);
    for (index = 0U; index < OPEN_CFW_UNORDERED_HOST_TASKS; ++index) {
        open_cfw_unordered_host_tasks[index].state_list_item.owner =
            &open_cfw_unordered_host_tasks[index];
        open_cfw_unordered_host_tasks[index].event_list_item.owner =
            &open_cfw_unordered_host_tasks[index];
    }
    open_cfw_unordered_host_tasks[0].priority = current_priority;
    open_cfw_unordered_host_tasks[1].priority = waiter_priority;
    open_cfw_unordered_host_tasks[1].state_list_item.item_value = wake_tick;
    open_cfw_unordered_host_tasks[1].event_list_item.item_value = 17U;
    open_cfw_unordered_host_list_insert_end(
        &open_cfw_unordered_host_blocked,
        &open_cfw_unordered_host_tasks[1].state_list_item
    );
    open_cfw_unordered_host_list_insert_end(
        &open_cfw_unordered_host_event,
        &open_cfw_unordered_host_tasks[1].event_list_item
    );
    if (seed_ready != 0U) {
        open_cfw_unordered_host_tasks[2].priority = waiter_priority;
        open_cfw_unordered_host_list_insert_end(
            &open_cfw_unordered_host_ready[waiter_priority],
            &open_cfw_unordered_host_tasks[2].state_list_item
        );
    }
    open_cfw_unordered_host_current = &open_cfw_unordered_host_tasks[0];
    open_cfw_unordered_host_scheduler_suspended = scheduler_suspended;
    open_cfw_unordered_host_top_ready_priority = top_ready_priority;
    open_cfw_unordered_host_yield_pending = 0;
    open_cfw_unordered_host_next_unblock_time = 0xA5A5A5A5U;
    open_cfw_unordered_host_reset_calls = 0U;
    open_cfw_unordered_host_reset_before_state_remove = 0U;
    open_cfw_unordered_host_trace_calls = 0U;
    open_cfw_unordered_host_assert_calls = 0U;
    open_cfw_unordered_host_execute_active = 0;
}

void open_cfw_unordered_host_set_indexes(
    uint32_t event_uses_waiter,
    uint32_t blocked_uses_waiter,
    uint32_t ready_uses_seed
)
{
    open_cfw_unordered_host_event.index = event_uses_waiter != 0U ?
        &open_cfw_unordered_host_tasks[1].event_list_item :
        open_cfw_unordered_host_sentinel(&open_cfw_unordered_host_event);
    open_cfw_unordered_host_blocked.index = blocked_uses_waiter != 0U ?
        &open_cfw_unordered_host_tasks[1].state_list_item :
        open_cfw_unordered_host_sentinel(&open_cfw_unordered_host_blocked);
    open_cfw_unordered_host_ready[
        open_cfw_unordered_host_tasks[1].priority
    ].index = ready_uses_seed != 0U ?
        &open_cfw_unordered_host_tasks[2].state_list_item :
        open_cfw_unordered_host_sentinel(
            &open_cfw_unordered_host_ready[
                open_cfw_unordered_host_tasks[1].priority
            ]
        );
}

int32_t open_cfw_unordered_host_execute(uint32_t item_value)
{
    open_cfw_unordered_host_execute_active = 1;
    if (setjmp(open_cfw_unordered_host_assert_jump) != 0) {
        open_cfw_unordered_host_execute_active = 0;
        return (int32_t)OPEN_CFW_UNORDERED_HOST_ASSERTED;
    }
    open_cfw_freertos_task_remove_from_unordered_event_list(
        &open_cfw_unordered_host_tasks[1].event_list_item,
        item_value
    );
    open_cfw_unordered_host_execute_active = 0;
    return 0;
}

int32_t open_cfw_unordered_host_execute_ownerless(uint32_t item_value)
{
    open_cfw_unordered_host_tasks[1].event_list_item.owner = 0;
    return open_cfw_unordered_host_execute(item_value);
}

static uint32_t open_cfw_unordered_host_identifier(const void *owner)
{
    uint32_t index;

    for (index = 0U; index < OPEN_CFW_UNORDERED_HOST_TASKS; ++index) {
        if (owner == &open_cfw_unordered_host_tasks[index]) {
            return index;
        }
    }
    return OPEN_CFW_UNORDERED_HOST_NULL;
}

static uint32_t open_cfw_unordered_host_index_identifier(
    struct open_cfw_freertos_unordered_list *list
)
{
    if (list->index == open_cfw_unordered_host_sentinel(list)) {
        return OPEN_CFW_UNORDERED_HOST_SENTINEL;
    }
    return open_cfw_unordered_host_identifier(list->index->owner);
}

uint32_t open_cfw_unordered_host_get_event_value(void)
{
    return open_cfw_unordered_host_tasks[1].event_list_item.item_value;
}

uint32_t open_cfw_unordered_host_get_event_count(void)
{
    return open_cfw_unordered_host_event.item_count;
}

uint32_t open_cfw_unordered_host_get_blocked_count(void)
{
    return open_cfw_unordered_host_blocked.item_count;
}

uint32_t open_cfw_unordered_host_get_ready_count(void)
{
    return open_cfw_unordered_host_ready[
        open_cfw_unordered_host_tasks[1].priority
    ].item_count;
}

uint32_t open_cfw_unordered_host_get_event_index(void)
{
    return open_cfw_unordered_host_index_identifier(
        &open_cfw_unordered_host_event
    );
}

uint32_t open_cfw_unordered_host_get_blocked_index(void)
{
    return open_cfw_unordered_host_index_identifier(
        &open_cfw_unordered_host_blocked
    );
}

uint32_t open_cfw_unordered_host_get_ready_index(void)
{
    return open_cfw_unordered_host_index_identifier(
        &open_cfw_unordered_host_ready[
            open_cfw_unordered_host_tasks[1].priority
        ]
    );
}

uint32_t open_cfw_unordered_host_get_ready_head(void)
{
    return open_cfw_unordered_host_identifier(
        open_cfw_unordered_host_ready[
            open_cfw_unordered_host_tasks[1].priority
        ].end.next->owner
    );
}

uint32_t open_cfw_unordered_host_get_ready_tail(void)
{
    return open_cfw_unordered_host_identifier(
        open_cfw_unordered_host_ready[
            open_cfw_unordered_host_tasks[1].priority
        ].end.previous->owner
    );
}

uint32_t open_cfw_unordered_host_get_state_container(void)
{
    return open_cfw_unordered_host_tasks[1].state_list_item.container ==
        &open_cfw_unordered_host_ready[
            open_cfw_unordered_host_tasks[1].priority
        ] ? OPEN_CFW_UNORDERED_HOST_READY_BASE +
            open_cfw_unordered_host_tasks[1].priority :
        OPEN_CFW_UNORDERED_HOST_NULL;
}

uint32_t open_cfw_unordered_host_get_event_container(void)
{
    return open_cfw_unordered_host_tasks[1].event_list_item.container == 0 ?
        OPEN_CFW_UNORDERED_HOST_NULL : OPEN_CFW_UNORDERED_HOST_EVENT;
}

#define OPEN_CFW_UNORDERED_HOST_GETTER(name, variable) \
    uint32_t open_cfw_unordered_host_get_##name(void) \
    { \
        return (uint32_t)(variable); \
    }

OPEN_CFW_UNORDERED_HOST_GETTER(top, open_cfw_unordered_host_top_ready_priority)
OPEN_CFW_UNORDERED_HOST_GETTER(yield, open_cfw_unordered_host_yield_pending)
OPEN_CFW_UNORDERED_HOST_GETTER(next, open_cfw_unordered_host_next_unblock_time)
OPEN_CFW_UNORDERED_HOST_GETTER(reset_calls, open_cfw_unordered_host_reset_calls)
OPEN_CFW_UNORDERED_HOST_GETTER(
    reset_before_state_remove,
    open_cfw_unordered_host_reset_before_state_remove
)
OPEN_CFW_UNORDERED_HOST_GETTER(trace_calls, open_cfw_unordered_host_trace_calls)
OPEN_CFW_UNORDERED_HOST_GETTER(assert_calls, open_cfw_unordered_host_assert_calls)
