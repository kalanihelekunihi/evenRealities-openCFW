/*
 * SPDX-License-Identifier: MIT
 *
 * Deterministic host graph and access-order harness for the source-owned
 * FreeRTOS xTaskIncrementTick() candidate.
 */

#include <setjmp.h>
#include <stdint.h>
#include <string.h>

#include "../../components/shared/freertos/runtime_freertos_task_increment_tick.h"

enum {
    OPEN_CFW_CANDIDATE_TICK_TASK_COUNT = 16U,
    OPEN_CFW_CANDIDATE_TICK_EVENT_LIST_COUNT = 4U,
    OPEN_CFW_CANDIDATE_TICK_DELAYED_LIST_1 = 0U,
    OPEN_CFW_CANDIDATE_TICK_DELAYED_LIST_2 = 1U,
    OPEN_CFW_CANDIDATE_TICK_READY_LIST_BASE = 0x100U,
    OPEN_CFW_CANDIDATE_TICK_EVENT_LIST_BASE = 0x200U,
    OPEN_CFW_CANDIDATE_TICK_SENTINEL = 0xFFFFFFFEU,
    OPEN_CFW_CANDIDATE_TICK_NULL = 0xFFFFFFFFU,
    OPEN_CFW_CANDIDATE_TICK_ASSERTED = 0x80000000U,
    OPEN_CFW_CANDIDATE_TICK_EVENT_CAPACITY = 256U,

    OPEN_CFW_CANDIDATE_EVENT_SUSPENDED_LOAD = 1U,
    OPEN_CFW_CANDIDATE_EVENT_TICK_LOAD = 2U,
    OPEN_CFW_CANDIDATE_EVENT_TICK_STORE = 3U,
    OPEN_CFW_CANDIDATE_EVENT_DELAYED_LOAD = 4U,
    OPEN_CFW_CANDIDATE_EVENT_DELAYED_STORE = 5U,
    OPEN_CFW_CANDIDATE_EVENT_OVERFLOW_LOAD = 6U,
    OPEN_CFW_CANDIDATE_EVENT_OVERFLOW_STORE = 7U,
    OPEN_CFW_CANDIDATE_EVENT_OVERFLOW_COUNT_LOAD = 8U,
    OPEN_CFW_CANDIDATE_EVENT_OVERFLOW_COUNT_STORE = 9U,
    OPEN_CFW_CANDIDATE_EVENT_NEXT_LOAD = 10U,
    OPEN_CFW_CANDIDATE_EVENT_NEXT_STORE = 11U,
    OPEN_CFW_CANDIDATE_EVENT_TOP_LOAD = 12U,
    OPEN_CFW_CANDIDATE_EVENT_TOP_STORE = 13U,
    OPEN_CFW_CANDIDATE_EVENT_CURRENT_LOAD = 14U,
    OPEN_CFW_CANDIDATE_EVENT_READY_SELECT = 15U,
    OPEN_CFW_CANDIDATE_EVENT_YIELD_LOAD = 16U,
    OPEN_CFW_CANDIDATE_EVENT_PENDED_LOAD = 17U,
    OPEN_CFW_CANDIDATE_EVENT_PENDED_STORE = 18U,
    OPEN_CFW_CANDIDATE_EVENT_RESET_HELPER = 19U,
    OPEN_CFW_CANDIDATE_EVENT_ASSERT = 20U
};

struct open_cfw_candidate_tick_event {
    uint32_t kind;
    uint32_t subject;
    uint32_t value;
};

static struct open_cfw_freertos_tick_tcb open_cfw_candidate_tick_tasks[
    OPEN_CFW_CANDIDATE_TICK_TASK_COUNT
];
static struct open_cfw_freertos_tick_list open_cfw_candidate_tick_delayed[2];
static struct open_cfw_freertos_tick_list open_cfw_candidate_tick_ready[
    OPEN_CFW_FREERTOS_TICK_MAX_PRIORITIES
];
static struct open_cfw_freertos_tick_list open_cfw_candidate_tick_events[
    OPEN_CFW_CANDIDATE_TICK_EVENT_LIST_COUNT
];
static struct open_cfw_freertos_tick_tcb *open_cfw_candidate_tick_current;
static struct open_cfw_freertos_tick_list *open_cfw_candidate_tick_delayed_ptr;
static struct open_cfw_freertos_tick_list *open_cfw_candidate_tick_overflow_ptr;
static uint32_t open_cfw_candidate_tick_count;
static uint32_t open_cfw_candidate_tick_suspended;
static uint32_t open_cfw_candidate_tick_pended;
static int32_t open_cfw_candidate_tick_yield;
static int32_t open_cfw_candidate_tick_overflow_count;
static uint32_t open_cfw_candidate_tick_next;
static uint32_t open_cfw_candidate_tick_top;
static uint32_t open_cfw_candidate_tick_assert_failures;
static struct open_cfw_candidate_tick_event open_cfw_candidate_tick_log[
    OPEN_CFW_CANDIDATE_TICK_EVENT_CAPACITY
];
static uint32_t open_cfw_candidate_tick_log_count;
static jmp_buf open_cfw_candidate_tick_assert_jump;
static int open_cfw_candidate_tick_execute_active;

static void open_cfw_candidate_tick_record(
    uint32_t kind,
    uint32_t subject,
    uint32_t value
)
{
    if (open_cfw_candidate_tick_log_count <
        OPEN_CFW_CANDIDATE_TICK_EVENT_CAPACITY) {
        struct open_cfw_candidate_tick_event *event =
            &open_cfw_candidate_tick_log[open_cfw_candidate_tick_log_count];

        event->kind = kind;
        event->subject = subject;
        event->value = value;
    }
    ++open_cfw_candidate_tick_log_count;
}

static struct open_cfw_freertos_tick_list_item *
open_cfw_candidate_tick_sentinel(struct open_cfw_freertos_tick_list *list)
{
    return (struct open_cfw_freertos_tick_list_item *)(void *)&list->end;
}

static void open_cfw_candidate_tick_list_initialise(
    struct open_cfw_freertos_tick_list *list
)
{
    struct open_cfw_freertos_tick_list_item *sentinel =
        open_cfw_candidate_tick_sentinel(list);

    list->item_count = 0U;
    list->index = sentinel;
    list->end.item_value = OPEN_CFW_FREERTOS_TICK_PORT_MAX_DELAY;
    list->end.next = sentinel;
    list->end.previous = sentinel;
}

static void open_cfw_candidate_tick_list_insert_sorted(
    struct open_cfw_freertos_tick_list *list,
    struct open_cfw_freertos_tick_list_item *item
)
{
    struct open_cfw_freertos_tick_list_item *sentinel =
        open_cfw_candidate_tick_sentinel(list);
    struct open_cfw_freertos_tick_list_item *iterator;

    if (item->item_value == OPEN_CFW_FREERTOS_TICK_PORT_MAX_DELAY) {
        iterator = sentinel->previous;
    } else {
        iterator = sentinel;
        while (iterator->next->item_value <= item->item_value) {
            iterator = iterator->next;
        }
    }
    item->next = iterator->next;
    item->next->previous = item;
    item->previous = iterator;
    iterator->next = item;
    item->container = list;
    ++list->item_count;
}

static void open_cfw_candidate_tick_list_insert_end(
    struct open_cfw_freertos_tick_list *list,
    struct open_cfw_freertos_tick_list_item *item
)
{
    struct open_cfw_freertos_tick_list_item *index = list->index;

    item->next = index;
    item->previous = index->previous;
    index->previous->next = item;
    index->previous = item;
    item->container = list;
    ++list->item_count;
}

static uint32_t open_cfw_candidate_tick_list_selector(
    const struct open_cfw_freertos_tick_list *list
)
{
    if (list == &open_cfw_candidate_tick_delayed[1]) {
        return 1U;
    }
    return 0U;
}

static struct open_cfw_freertos_tick_list *open_cfw_candidate_tick_list(
    uint32_t kind
)
{
    if (kind < 2U) {
        return &open_cfw_candidate_tick_delayed[kind];
    }
    if (
        kind >= OPEN_CFW_CANDIDATE_TICK_READY_LIST_BASE &&
        kind < OPEN_CFW_CANDIDATE_TICK_READY_LIST_BASE +
            OPEN_CFW_FREERTOS_TICK_MAX_PRIORITIES
    ) {
        return &open_cfw_candidate_tick_ready[
            kind - OPEN_CFW_CANDIDATE_TICK_READY_LIST_BASE
        ];
    }
    if (
        kind >= OPEN_CFW_CANDIDATE_TICK_EVENT_LIST_BASE &&
        kind < OPEN_CFW_CANDIDATE_TICK_EVENT_LIST_BASE +
            OPEN_CFW_CANDIDATE_TICK_EVENT_LIST_COUNT
    ) {
        return &open_cfw_candidate_tick_events[
            kind - OPEN_CFW_CANDIDATE_TICK_EVENT_LIST_BASE
        ];
    }
    return (struct open_cfw_freertos_tick_list *)0;
}

static struct open_cfw_freertos_tick_tcb *open_cfw_candidate_tick_task(
    uint32_t identifier
)
{
    if (identifier >= OPEN_CFW_CANDIDATE_TICK_TASK_COUNT) {
        return (struct open_cfw_freertos_tick_tcb *)0;
    }
    return &open_cfw_candidate_tick_tasks[identifier];
}

static uint32_t open_cfw_candidate_tick_task_identifier(const void *owner)
{
    uint32_t index;

    if (owner == (const void *)0) {
        return OPEN_CFW_CANDIDATE_TICK_NULL;
    }
    for (index = 0U; index < OPEN_CFW_CANDIDATE_TICK_TASK_COUNT; ++index) {
        if (owner == &open_cfw_candidate_tick_tasks[index]) {
            return index;
        }
    }
    return OPEN_CFW_CANDIDATE_TICK_NULL;
}

static uint32_t open_cfw_candidate_tick_node_identifier(
    const struct open_cfw_freertos_tick_list *list,
    const struct open_cfw_freertos_tick_list_item *item
)
{
    if (item == (const struct open_cfw_freertos_tick_list_item *)0) {
        return OPEN_CFW_CANDIDATE_TICK_NULL;
    }
    if (
        list != (const struct open_cfw_freertos_tick_list *)0 &&
        item == (const struct open_cfw_freertos_tick_list_item *)(const void *)
            &list->end
    ) {
        return OPEN_CFW_CANDIDATE_TICK_SENTINEL;
    }
    return open_cfw_candidate_tick_task_identifier(item->owner);
}

static struct open_cfw_freertos_tick_tcb *open_cfw_candidate_current_load(void)
{
    open_cfw_candidate_tick_record(
        OPEN_CFW_CANDIDATE_EVENT_CURRENT_LOAD,
        0U,
        open_cfw_candidate_tick_task_identifier(open_cfw_candidate_tick_current)
    );
    return open_cfw_candidate_tick_current;
}

static struct open_cfw_freertos_tick_list *open_cfw_candidate_delayed_load(void)
{
    open_cfw_candidate_tick_record(
        OPEN_CFW_CANDIDATE_EVENT_DELAYED_LOAD,
        open_cfw_candidate_tick_list_selector(open_cfw_candidate_tick_delayed_ptr),
        open_cfw_candidate_tick_delayed_ptr->item_count
    );
    return open_cfw_candidate_tick_delayed_ptr;
}

static void open_cfw_candidate_delayed_store(
    struct open_cfw_freertos_tick_list *value
)
{
    open_cfw_candidate_tick_delayed_ptr = value;
    open_cfw_candidate_tick_record(
        OPEN_CFW_CANDIDATE_EVENT_DELAYED_STORE,
        open_cfw_candidate_tick_list_selector(value),
        value->item_count
    );
}

static struct open_cfw_freertos_tick_list *open_cfw_candidate_overflow_load(void)
{
    open_cfw_candidate_tick_record(
        OPEN_CFW_CANDIDATE_EVENT_OVERFLOW_LOAD,
        open_cfw_candidate_tick_list_selector(open_cfw_candidate_tick_overflow_ptr),
        open_cfw_candidate_tick_overflow_ptr->item_count
    );
    return open_cfw_candidate_tick_overflow_ptr;
}

static void open_cfw_candidate_overflow_store(
    struct open_cfw_freertos_tick_list *value
)
{
    open_cfw_candidate_tick_overflow_ptr = value;
    open_cfw_candidate_tick_record(
        OPEN_CFW_CANDIDATE_EVENT_OVERFLOW_STORE,
        open_cfw_candidate_tick_list_selector(value),
        value->item_count
    );
}

#define OPEN_CFW_CANDIDATE_SCALAR_LOAD(name, event, type) \
    static type open_cfw_candidate_##name##_load(void) \
    { \
        open_cfw_candidate_tick_record((event), 0U, \
            (uint32_t)open_cfw_candidate_tick_##name); \
        return open_cfw_candidate_tick_##name; \
    }

#define OPEN_CFW_CANDIDATE_SCALAR_STORE(name, event, type) \
    static void open_cfw_candidate_##name##_store(type value) \
    { \
        open_cfw_candidate_tick_##name = value; \
        open_cfw_candidate_tick_record((event), 0U, (uint32_t)value); \
    }

OPEN_CFW_CANDIDATE_SCALAR_LOAD(count, OPEN_CFW_CANDIDATE_EVENT_TICK_LOAD, uint32_t)
OPEN_CFW_CANDIDATE_SCALAR_STORE(count, OPEN_CFW_CANDIDATE_EVENT_TICK_STORE, uint32_t)
OPEN_CFW_CANDIDATE_SCALAR_LOAD(top, OPEN_CFW_CANDIDATE_EVENT_TOP_LOAD, uint32_t)
OPEN_CFW_CANDIDATE_SCALAR_STORE(top, OPEN_CFW_CANDIDATE_EVENT_TOP_STORE, uint32_t)
OPEN_CFW_CANDIDATE_SCALAR_LOAD(pended, OPEN_CFW_CANDIDATE_EVENT_PENDED_LOAD, uint32_t)
OPEN_CFW_CANDIDATE_SCALAR_STORE(pended, OPEN_CFW_CANDIDATE_EVENT_PENDED_STORE, uint32_t)
OPEN_CFW_CANDIDATE_SCALAR_LOAD(yield, OPEN_CFW_CANDIDATE_EVENT_YIELD_LOAD, int32_t)
OPEN_CFW_CANDIDATE_SCALAR_LOAD(overflow_count, OPEN_CFW_CANDIDATE_EVENT_OVERFLOW_COUNT_LOAD, int32_t)
OPEN_CFW_CANDIDATE_SCALAR_STORE(overflow_count, OPEN_CFW_CANDIDATE_EVENT_OVERFLOW_COUNT_STORE, int32_t)
OPEN_CFW_CANDIDATE_SCALAR_LOAD(next, OPEN_CFW_CANDIDATE_EVENT_NEXT_LOAD, uint32_t)
OPEN_CFW_CANDIDATE_SCALAR_STORE(next, OPEN_CFW_CANDIDATE_EVENT_NEXT_STORE, uint32_t)
OPEN_CFW_CANDIDATE_SCALAR_LOAD(suspended, OPEN_CFW_CANDIDATE_EVENT_SUSPENDED_LOAD, uint32_t)

static struct open_cfw_freertos_tick_list *open_cfw_candidate_ready_list(
    uint32_t priority
)
{
    open_cfw_candidate_tick_record(
        OPEN_CFW_CANDIDATE_EVENT_READY_SELECT,
        priority,
        open_cfw_candidate_tick_ready[priority].item_count
    );
    return &open_cfw_candidate_tick_ready[priority];
}

static void open_cfw_candidate_assert_fail(void)
{
    ++open_cfw_candidate_tick_assert_failures;
    open_cfw_candidate_tick_record(
        OPEN_CFW_CANDIDATE_EVENT_ASSERT,
        0U,
        open_cfw_candidate_tick_assert_failures
    );
    if (open_cfw_candidate_tick_execute_active != 0) {
        longjmp(open_cfw_candidate_tick_assert_jump, 1);
    }
}

#undef OPEN_CFW_FREERTOS_TICK_CURRENT_TCB_LOAD
#undef OPEN_CFW_FREERTOS_TICK_DELAYED_LIST_LOAD
#undef OPEN_CFW_FREERTOS_TICK_DELAYED_LIST_STORE
#undef OPEN_CFW_FREERTOS_TICK_OVERFLOW_LIST_LOAD
#undef OPEN_CFW_FREERTOS_TICK_OVERFLOW_LIST_STORE
#undef OPEN_CFW_FREERTOS_TICK_COUNT_LOAD
#undef OPEN_CFW_FREERTOS_TICK_COUNT_STORE
#undef OPEN_CFW_FREERTOS_TICK_TOP_READY_PRIORITY_LOAD
#undef OPEN_CFW_FREERTOS_TICK_TOP_READY_PRIORITY_STORE
#undef OPEN_CFW_FREERTOS_TICK_PENDED_TICKS_LOAD
#undef OPEN_CFW_FREERTOS_TICK_PENDED_TICKS_STORE
#undef OPEN_CFW_FREERTOS_TICK_YIELD_PENDING_LOAD
#undef OPEN_CFW_FREERTOS_TICK_OVERFLOW_COUNT_LOAD
#undef OPEN_CFW_FREERTOS_TICK_OVERFLOW_COUNT_STORE
#undef OPEN_CFW_FREERTOS_TICK_NEXT_UNBLOCK_TIME_LOAD
#undef OPEN_CFW_FREERTOS_TICK_NEXT_UNBLOCK_TIME_STORE
#undef OPEN_CFW_FREERTOS_TICK_SCHEDULER_SUSPENDED_LOAD
#undef OPEN_CFW_FREERTOS_TICK_READY_LIST
#undef OPEN_CFW_FREERTOS_TICK_ASSERT

#define OPEN_CFW_FREERTOS_TICK_CURRENT_TCB_LOAD() open_cfw_candidate_current_load()
#define OPEN_CFW_FREERTOS_TICK_DELAYED_LIST_LOAD() open_cfw_candidate_delayed_load()
#define OPEN_CFW_FREERTOS_TICK_DELAYED_LIST_STORE(value) open_cfw_candidate_delayed_store(value)
#define OPEN_CFW_FREERTOS_TICK_OVERFLOW_LIST_LOAD() open_cfw_candidate_overflow_load()
#define OPEN_CFW_FREERTOS_TICK_OVERFLOW_LIST_STORE(value) open_cfw_candidate_overflow_store(value)
#define OPEN_CFW_FREERTOS_TICK_COUNT_LOAD() open_cfw_candidate_count_load()
#define OPEN_CFW_FREERTOS_TICK_COUNT_STORE(value) open_cfw_candidate_count_store(value)
#define OPEN_CFW_FREERTOS_TICK_TOP_READY_PRIORITY_LOAD() open_cfw_candidate_top_load()
#define OPEN_CFW_FREERTOS_TICK_TOP_READY_PRIORITY_STORE(value) open_cfw_candidate_top_store(value)
#define OPEN_CFW_FREERTOS_TICK_PENDED_TICKS_LOAD() open_cfw_candidate_pended_load()
#define OPEN_CFW_FREERTOS_TICK_PENDED_TICKS_STORE(value) open_cfw_candidate_pended_store(value)
#define OPEN_CFW_FREERTOS_TICK_YIELD_PENDING_LOAD() open_cfw_candidate_yield_load()
#define OPEN_CFW_FREERTOS_TICK_OVERFLOW_COUNT_LOAD() open_cfw_candidate_overflow_count_load()
#define OPEN_CFW_FREERTOS_TICK_OVERFLOW_COUNT_STORE(value) open_cfw_candidate_overflow_count_store(value)
#define OPEN_CFW_FREERTOS_TICK_NEXT_UNBLOCK_TIME_LOAD() open_cfw_candidate_next_load()
#define OPEN_CFW_FREERTOS_TICK_NEXT_UNBLOCK_TIME_STORE(value) open_cfw_candidate_next_store(value)
#define OPEN_CFW_FREERTOS_TICK_SCHEDULER_SUSPENDED_LOAD() open_cfw_candidate_suspended_load()
#define OPEN_CFW_FREERTOS_TICK_READY_LIST(priority) open_cfw_candidate_ready_list(priority)
#define OPEN_CFW_FREERTOS_TICK_ASSERT(condition) \
    do { if (!(condition)) { open_cfw_candidate_assert_fail(); } } while (0)

#include "../../components/shared/freertos/runtime_freertos_task_increment_tick.c"

open_cfw_freertos_tick_ubase_type ulSetInterruptMask(void)
{
    return 0U;
}

void open_cfw_freertos_task_reset_next_task_unblock_time(void)
{
    struct open_cfw_freertos_tick_list *list =
        open_cfw_candidate_tick_delayed_ptr;
    uint32_t value = (list->item_count == 0U) ?
        OPEN_CFW_FREERTOS_TICK_PORT_MAX_DELAY : list->end.next->item_value;

    open_cfw_candidate_tick_record(
        OPEN_CFW_CANDIDATE_EVENT_RESET_HELPER,
        open_cfw_candidate_tick_list_selector(list),
        value
    );
    open_cfw_candidate_tick_next = value;
}

void open_cfw_candidate_freertos_task_increment_tick_reset(
    uint32_t tick_count,
    uint32_t scheduler_suspended,
    uint32_t pended_ticks,
    int32_t yield_pending,
    int32_t overflow_count,
    uint32_t next_unblock_time,
    uint32_t top_ready_priority,
    uint32_t current_identifier,
    uint32_t delayed_selector
)
{
    uint32_t index;

    memset(open_cfw_candidate_tick_tasks, 0, sizeof(open_cfw_candidate_tick_tasks));
    for (index = 0U; index < 2U; ++index) {
        open_cfw_candidate_tick_list_initialise(&open_cfw_candidate_tick_delayed[index]);
    }
    for (index = 0U; index < OPEN_CFW_FREERTOS_TICK_MAX_PRIORITIES; ++index) {
        open_cfw_candidate_tick_list_initialise(&open_cfw_candidate_tick_ready[index]);
    }
    for (index = 0U; index < OPEN_CFW_CANDIDATE_TICK_EVENT_LIST_COUNT; ++index) {
        open_cfw_candidate_tick_list_initialise(&open_cfw_candidate_tick_events[index]);
    }
    for (index = 0U; index < OPEN_CFW_CANDIDATE_TICK_TASK_COUNT; ++index) {
        open_cfw_candidate_tick_tasks[index].state_list_item.owner =
            &open_cfw_candidate_tick_tasks[index];
        open_cfw_candidate_tick_tasks[index].event_list_item.owner =
            &open_cfw_candidate_tick_tasks[index];
    }
    if (delayed_selector == 1U) {
        open_cfw_candidate_tick_delayed_ptr = &open_cfw_candidate_tick_delayed[1];
        open_cfw_candidate_tick_overflow_ptr = &open_cfw_candidate_tick_delayed[0];
    } else {
        open_cfw_candidate_tick_delayed_ptr = &open_cfw_candidate_tick_delayed[0];
        open_cfw_candidate_tick_overflow_ptr = &open_cfw_candidate_tick_delayed[1];
    }
    open_cfw_candidate_tick_current = open_cfw_candidate_tick_task(current_identifier);
    open_cfw_candidate_tick_count = tick_count;
    open_cfw_candidate_tick_suspended = scheduler_suspended;
    open_cfw_candidate_tick_pended = pended_ticks;
    open_cfw_candidate_tick_yield = yield_pending;
    open_cfw_candidate_tick_overflow_count = overflow_count;
    open_cfw_candidate_tick_next = next_unblock_time;
    open_cfw_candidate_tick_top = top_ready_priority;
    open_cfw_candidate_tick_assert_failures = 0U;
    open_cfw_candidate_tick_log_count = 0U;
    open_cfw_candidate_tick_execute_active = 0;
}

void open_cfw_candidate_freertos_task_increment_tick_set_task(
    uint32_t identifier,
    uint32_t priority,
    uint32_t wake_tick
)
{
    struct open_cfw_freertos_tick_tcb *task =
        open_cfw_candidate_tick_task(identifier);

    if (task == (struct open_cfw_freertos_tick_tcb *)0 ||
        priority >= OPEN_CFW_FREERTOS_TICK_MAX_PRIORITIES) {
        return;
    }
    task->priority = priority;
    task->state_list_item.item_value = wake_tick;
    task->event_list_item.item_value = wake_tick;
}

void open_cfw_candidate_freertos_task_increment_tick_insert_delayed(
    uint32_t selector,
    uint32_t identifier
)
{
    struct open_cfw_freertos_tick_tcb *task = open_cfw_candidate_tick_task(identifier);
    struct open_cfw_freertos_tick_list *list = open_cfw_candidate_tick_list(selector);

    if (task != (struct open_cfw_freertos_tick_tcb *)0 &&
        list != (struct open_cfw_freertos_tick_list *)0) {
        open_cfw_candidate_tick_list_insert_sorted(list, &task->state_list_item);
    }
}

void open_cfw_candidate_freertos_task_increment_tick_insert_event(
    uint32_t event_list,
    uint32_t identifier
)
{
    struct open_cfw_freertos_tick_tcb *task = open_cfw_candidate_tick_task(identifier);
    struct open_cfw_freertos_tick_list *list = open_cfw_candidate_tick_list(
        OPEN_CFW_CANDIDATE_TICK_EVENT_LIST_BASE + event_list
    );

    if (task != (struct open_cfw_freertos_tick_tcb *)0 &&
        list != (struct open_cfw_freertos_tick_list *)0) {
        open_cfw_candidate_tick_list_insert_end(list, &task->event_list_item);
    }
}

void open_cfw_candidate_freertos_task_increment_tick_insert_ready(
    uint32_t priority,
    uint32_t identifier
)
{
    struct open_cfw_freertos_tick_tcb *task = open_cfw_candidate_tick_task(identifier);

    if (task != (struct open_cfw_freertos_tick_tcb *)0 &&
        priority < OPEN_CFW_FREERTOS_TICK_MAX_PRIORITIES &&
        task->priority == priority) {
        open_cfw_candidate_tick_list_insert_end(
            &open_cfw_candidate_tick_ready[priority],
            &task->state_list_item
        );
    }
}

void open_cfw_candidate_freertos_task_increment_tick_set_index(
    uint32_t kind,
    uint32_t identifier
)
{
    struct open_cfw_freertos_tick_list *list = open_cfw_candidate_tick_list(kind);
    struct open_cfw_freertos_tick_tcb *task;

    if (list == (struct open_cfw_freertos_tick_list *)0) {
        return;
    }
    if (identifier == OPEN_CFW_CANDIDATE_TICK_SENTINEL) {
        list->index = open_cfw_candidate_tick_sentinel(list);
        return;
    }
    if (identifier == OPEN_CFW_CANDIDATE_TICK_NULL) {
        list->index = (struct open_cfw_freertos_tick_list_item *)0;
        return;
    }
    task = open_cfw_candidate_tick_task(identifier);
    if (task == (struct open_cfw_freertos_tick_tcb *)0) {
        return;
    }
    if (kind >= OPEN_CFW_CANDIDATE_TICK_EVENT_LIST_BASE &&
        kind < OPEN_CFW_CANDIDATE_TICK_EVENT_LIST_BASE +
            OPEN_CFW_CANDIDATE_TICK_EVENT_LIST_COUNT) {
        list->index = &task->event_list_item;
    } else {
        list->index = &task->state_list_item;
    }
}

int32_t open_cfw_candidate_freertos_task_increment_tick_execute(void)
{
    int32_t result;

    open_cfw_candidate_tick_execute_active = 1;
    if (setjmp(open_cfw_candidate_tick_assert_jump) != 0) {
        open_cfw_candidate_tick_execute_active = 0;
        return (int32_t)OPEN_CFW_CANDIDATE_TICK_ASSERTED;
    }
    result = open_cfw_freertos_task_increment_tick();
    open_cfw_candidate_tick_execute_active = 0;
    return result;
}

#define OPEN_CFW_CANDIDATE_GETTER(name, type, expression) \
    type open_cfw_candidate_freertos_task_increment_tick_get_##name(void) \
    { return (type)(expression); }

OPEN_CFW_CANDIDATE_GETTER(tick, uint32_t, open_cfw_candidate_tick_count)
OPEN_CFW_CANDIDATE_GETTER(suspended, uint32_t, open_cfw_candidate_tick_suspended)
OPEN_CFW_CANDIDATE_GETTER(pended, uint32_t, open_cfw_candidate_tick_pended)
OPEN_CFW_CANDIDATE_GETTER(yield, int32_t, open_cfw_candidate_tick_yield)
OPEN_CFW_CANDIDATE_GETTER(overflow, int32_t, open_cfw_candidate_tick_overflow_count)
OPEN_CFW_CANDIDATE_GETTER(next, uint32_t, open_cfw_candidate_tick_next)
OPEN_CFW_CANDIDATE_GETTER(top, uint32_t, open_cfw_candidate_tick_top)
OPEN_CFW_CANDIDATE_GETTER(delayed_selector, uint32_t,
    open_cfw_candidate_tick_list_selector(open_cfw_candidate_tick_delayed_ptr))
OPEN_CFW_CANDIDATE_GETTER(assert_failures, uint32_t,
    open_cfw_candidate_tick_assert_failures)

uint32_t open_cfw_candidate_freertos_task_increment_tick_get_list_count(
    uint32_t kind
)
{
    struct open_cfw_freertos_tick_list *list = open_cfw_candidate_tick_list(kind);
    return (list == (struct open_cfw_freertos_tick_list *)0) ?
        OPEN_CFW_CANDIDATE_TICK_NULL : list->item_count;
}

uint32_t open_cfw_candidate_freertos_task_increment_tick_get_list_index(
    uint32_t kind
)
{
    struct open_cfw_freertos_tick_list *list = open_cfw_candidate_tick_list(kind);
    return (list == (struct open_cfw_freertos_tick_list *)0) ?
        OPEN_CFW_CANDIDATE_TICK_NULL :
        open_cfw_candidate_tick_node_identifier(list, list->index);
}

uint32_t open_cfw_candidate_freertos_task_increment_tick_get_list_owner(
    uint32_t kind,
    uint32_t position
)
{
    struct open_cfw_freertos_tick_list *list = open_cfw_candidate_tick_list(kind);
    struct open_cfw_freertos_tick_list_item *sentinel;
    struct open_cfw_freertos_tick_list_item *item;
    uint32_t index;

    if (list == (struct open_cfw_freertos_tick_list *)0) {
        return OPEN_CFW_CANDIDATE_TICK_NULL;
    }
    sentinel = open_cfw_candidate_tick_sentinel(list);
    item = sentinel->next;
    for (index = 0U; index < position && item != sentinel; ++index) {
        item = item->next;
    }
    return (item == sentinel) ? OPEN_CFW_CANDIDATE_TICK_NULL :
        open_cfw_candidate_tick_task_identifier(item->owner);
}

uint32_t open_cfw_candidate_freertos_task_increment_tick_get_task_priority(
    uint32_t identifier
)
{
    struct open_cfw_freertos_tick_tcb *task = open_cfw_candidate_tick_task(identifier);
    return (task == (struct open_cfw_freertos_tick_tcb *)0) ?
        OPEN_CFW_CANDIDATE_TICK_NULL : task->priority;
}

uint32_t open_cfw_candidate_freertos_task_increment_tick_get_task_wake(
    uint32_t identifier
)
{
    struct open_cfw_freertos_tick_tcb *task = open_cfw_candidate_tick_task(identifier);
    return (task == (struct open_cfw_freertos_tick_tcb *)0) ?
        OPEN_CFW_CANDIDATE_TICK_NULL : task->state_list_item.item_value;
}

uint32_t open_cfw_candidate_freertos_task_increment_tick_get_task_container(
    uint32_t identifier
)
{
    struct open_cfw_freertos_tick_tcb *task = open_cfw_candidate_tick_task(identifier);
    uint32_t priority;

    if (task == (struct open_cfw_freertos_tick_tcb *)0 ||
        task->state_list_item.container == (struct open_cfw_freertos_tick_list *)0) {
        return OPEN_CFW_CANDIDATE_TICK_NULL;
    }
    if (task->state_list_item.container == &open_cfw_candidate_tick_delayed[0]) {
        return 0U;
    }
    if (task->state_list_item.container == &open_cfw_candidate_tick_delayed[1]) {
        return 1U;
    }
    for (priority = 0U; priority < OPEN_CFW_FREERTOS_TICK_MAX_PRIORITIES; ++priority) {
        if (task->state_list_item.container == &open_cfw_candidate_tick_ready[priority]) {
            return OPEN_CFW_CANDIDATE_TICK_READY_LIST_BASE + priority;
        }
    }
    return OPEN_CFW_CANDIDATE_TICK_NULL;
}

uint32_t open_cfw_candidate_freertos_task_increment_tick_get_event_container(
    uint32_t identifier
)
{
    struct open_cfw_freertos_tick_tcb *task = open_cfw_candidate_tick_task(identifier);
    uint32_t event_list;

    if (task == (struct open_cfw_freertos_tick_tcb *)0 ||
        task->event_list_item.container == (struct open_cfw_freertos_tick_list *)0) {
        return OPEN_CFW_CANDIDATE_TICK_NULL;
    }
    for (event_list = 0U; event_list < OPEN_CFW_CANDIDATE_TICK_EVENT_LIST_COUNT;
         ++event_list) {
        if (task->event_list_item.container == &open_cfw_candidate_tick_events[event_list]) {
            return OPEN_CFW_CANDIDATE_TICK_EVENT_LIST_BASE + event_list;
        }
    }
    return OPEN_CFW_CANDIDATE_TICK_NULL;
}

uint32_t open_cfw_candidate_freertos_task_increment_tick_get_event_count(void)
{
    return open_cfw_candidate_tick_log_count;
}

uint32_t open_cfw_candidate_freertos_task_increment_tick_get_event_kind(
    uint32_t index
)
{
    return (index < open_cfw_candidate_tick_log_count &&
        index < OPEN_CFW_CANDIDATE_TICK_EVENT_CAPACITY) ?
        open_cfw_candidate_tick_log[index].kind : OPEN_CFW_CANDIDATE_TICK_NULL;
}

uint32_t open_cfw_candidate_freertos_task_increment_tick_get_event_subject(
    uint32_t index
)
{
    return (index < open_cfw_candidate_tick_log_count &&
        index < OPEN_CFW_CANDIDATE_TICK_EVENT_CAPACITY) ?
        open_cfw_candidate_tick_log[index].subject : OPEN_CFW_CANDIDATE_TICK_NULL;
}

uint32_t open_cfw_candidate_freertos_task_increment_tick_get_event_value(
    uint32_t index
)
{
    return (index < open_cfw_candidate_tick_log_count &&
        index < OPEN_CFW_CANDIDATE_TICK_EVENT_CAPACITY) ?
        open_cfw_candidate_tick_log[index].value : OPEN_CFW_CANDIDATE_TICK_NULL;
}
