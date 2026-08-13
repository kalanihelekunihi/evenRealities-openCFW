/*
 * SPDX-License-Identifier: MIT
 *
 * Deterministic host graph and access-order harness for the isolated
 * FreeRTOS xTaskResumeAll() candidate.
 */

#include <setjmp.h>
#include <stdint.h>
#include <string.h>

#include "../../components/shared/freertos/runtime_freertos_task_resume_all.h"

enum {
    OPEN_CFW_RESUME_HOST_TASKS = 8U,
    OPEN_CFW_RESUME_HOST_EVENTS = 256U,
    OPEN_CFW_RESUME_HOST_READY = 0x100U,
    OPEN_CFW_RESUME_HOST_BLOCKED = 0x200U,
    OPEN_CFW_RESUME_HOST_PENDING = 0x300U,
    OPEN_CFW_RESUME_HOST_SENTINEL = 0xFFFFFFFEU,
    OPEN_CFW_RESUME_HOST_NULL = 0xFFFFFFFFU,
    OPEN_CFW_RESUME_HOST_ASSERTED = 0x80000000U,
    OPEN_CFW_RESUME_EVENT_SUSPENDED_LOAD = 1U,
    OPEN_CFW_RESUME_EVENT_ENTER = 2U,
    OPEN_CFW_RESUME_EVENT_SUSPENDED_STORE = 3U,
    OPEN_CFW_RESUME_EVENT_TASK_COUNT_LOAD = 4U,
    OPEN_CFW_RESUME_EVENT_MEMORY_BARRIER = 5U,
    OPEN_CFW_RESUME_EVENT_TOP_LOAD = 6U,
    OPEN_CFW_RESUME_EVENT_TOP_STORE = 7U,
    OPEN_CFW_RESUME_EVENT_CURRENT_LOAD = 8U,
    OPEN_CFW_RESUME_EVENT_YIELD_STORE = 9U,
    OPEN_CFW_RESUME_EVENT_RESET_NEXT = 10U,
    OPEN_CFW_RESUME_EVENT_PENDED_LOAD = 11U,
    OPEN_CFW_RESUME_EVENT_INCREMENT_TICK = 12U,
    OPEN_CFW_RESUME_EVENT_PENDED_STORE = 13U,
    OPEN_CFW_RESUME_EVENT_YIELD_LOAD = 14U,
    OPEN_CFW_RESUME_EVENT_YIELD_CALL = 15U,
    OPEN_CFW_RESUME_EVENT_EXIT = 16U,
    OPEN_CFW_RESUME_EVENT_ASSERT = 17U
};

struct open_cfw_resume_host_event {
    uint32_t kind;
    uint32_t value;
};

static struct open_cfw_freertos_resume_tcb open_cfw_resume_host_tasks[
    OPEN_CFW_RESUME_HOST_TASKS
];
static struct open_cfw_freertos_resume_list open_cfw_resume_host_ready[
    OPEN_CFW_FREERTOS_RESUME_MAX_PRIORITIES
];
static struct open_cfw_freertos_resume_list open_cfw_resume_host_pending;
static struct open_cfw_freertos_resume_list open_cfw_resume_host_blocked;
static struct open_cfw_freertos_resume_tcb *open_cfw_resume_host_current;
static uint32_t open_cfw_resume_host_current_tasks;
static uint32_t open_cfw_resume_host_top;
static uint32_t open_cfw_resume_host_pended;
static int32_t open_cfw_resume_host_yield_pending;
static uint32_t open_cfw_resume_host_suspended;
static uint32_t open_cfw_resume_host_tick_results;
static uint32_t open_cfw_resume_host_tick_calls;
static uint32_t open_cfw_resume_host_enter_calls;
static uint32_t open_cfw_resume_host_exit_calls;
static uint32_t open_cfw_resume_host_yield_calls;
static uint32_t open_cfw_resume_host_reset_calls;
static uint32_t open_cfw_resume_host_assert_calls;
static struct open_cfw_resume_host_event open_cfw_resume_host_log[
    OPEN_CFW_RESUME_HOST_EVENTS
];
static uint32_t open_cfw_resume_host_log_count;
static jmp_buf open_cfw_resume_host_assert_jump;
static int open_cfw_resume_host_execute_active;

static void open_cfw_resume_host_record(uint32_t kind, uint32_t value)
{
    if (open_cfw_resume_host_log_count < OPEN_CFW_RESUME_HOST_EVENTS) {
        open_cfw_resume_host_log[open_cfw_resume_host_log_count].kind = kind;
        open_cfw_resume_host_log[open_cfw_resume_host_log_count].value = value;
    }
    ++open_cfw_resume_host_log_count;
}

static struct open_cfw_freertos_resume_list_item *
open_cfw_resume_host_sentinel(struct open_cfw_freertos_resume_list *list)
{
    return (struct open_cfw_freertos_resume_list_item *)(void *)&list->end;
}

static void open_cfw_resume_host_list_initialise(
    struct open_cfw_freertos_resume_list *list
)
{
    struct open_cfw_freertos_resume_list_item *sentinel =
        open_cfw_resume_host_sentinel(list);

    list->item_count = 0U;
    list->index = sentinel;
    list->end.item_value = 0xFFFFFFFFU;
    list->end.next = sentinel;
    list->end.previous = sentinel;
}

static void open_cfw_resume_host_list_insert_end(
    struct open_cfw_freertos_resume_list *list,
    struct open_cfw_freertos_resume_list_item *item
)
{
    struct open_cfw_freertos_resume_list_item *index = list->index;

    item->next = index;
    item->previous = index->previous;
    index->previous->next = item;
    index->previous = item;
    item->container = list;
    ++list->item_count;
}

static struct open_cfw_freertos_resume_tcb *open_cfw_resume_host_task(
    uint32_t identifier
)
{
    if (identifier >= OPEN_CFW_RESUME_HOST_TASKS) {
        return (struct open_cfw_freertos_resume_tcb *)0;
    }
    return &open_cfw_resume_host_tasks[identifier];
}

static struct open_cfw_freertos_resume_list *open_cfw_resume_host_list(
    uint32_t kind
)
{
    if (
        kind >= OPEN_CFW_RESUME_HOST_READY &&
        kind <
            OPEN_CFW_RESUME_HOST_READY +
            OPEN_CFW_FREERTOS_RESUME_MAX_PRIORITIES
    ) {
        return &open_cfw_resume_host_ready[kind - OPEN_CFW_RESUME_HOST_READY];
    }
    if (kind == OPEN_CFW_RESUME_HOST_BLOCKED) {
        return &open_cfw_resume_host_blocked;
    }
    if (kind == OPEN_CFW_RESUME_HOST_PENDING) {
        return &open_cfw_resume_host_pending;
    }
    return (struct open_cfw_freertos_resume_list *)0;
}

static uint32_t open_cfw_resume_host_task_identifier(const void *task)
{
    uint32_t index;

    for (index = 0U; index < OPEN_CFW_RESUME_HOST_TASKS; ++index) {
        if (task == &open_cfw_resume_host_tasks[index]) {
            return index;
        }
    }
    return OPEN_CFW_RESUME_HOST_NULL;
}

static uint32_t open_cfw_resume_host_suspended_load(void)
{
    open_cfw_resume_host_record(
        OPEN_CFW_RESUME_EVENT_SUSPENDED_LOAD,
        open_cfw_resume_host_suspended
    );
    return open_cfw_resume_host_suspended;
}

static void open_cfw_resume_host_suspended_store(uint32_t value)
{
    open_cfw_resume_host_suspended = value;
    open_cfw_resume_host_record(OPEN_CFW_RESUME_EVENT_SUSPENDED_STORE, value);
}

static uint32_t open_cfw_resume_host_current_tasks_load(void)
{
    open_cfw_resume_host_record(
        OPEN_CFW_RESUME_EVENT_TASK_COUNT_LOAD,
        open_cfw_resume_host_current_tasks
    );
    return open_cfw_resume_host_current_tasks;
}

static uint32_t open_cfw_resume_host_top_load(void)
{
    open_cfw_resume_host_record(OPEN_CFW_RESUME_EVENT_TOP_LOAD, open_cfw_resume_host_top);
    return open_cfw_resume_host_top;
}

static void open_cfw_resume_host_top_store(uint32_t value)
{
    open_cfw_resume_host_top = value;
    open_cfw_resume_host_record(OPEN_CFW_RESUME_EVENT_TOP_STORE, value);
}

static struct open_cfw_freertos_resume_tcb *open_cfw_resume_host_current_load(void)
{
    open_cfw_resume_host_record(
        OPEN_CFW_RESUME_EVENT_CURRENT_LOAD,
        open_cfw_resume_host_task_identifier(open_cfw_resume_host_current)
    );
    return open_cfw_resume_host_current;
}

static uint32_t open_cfw_resume_host_pended_load(void)
{
    open_cfw_resume_host_record(
        OPEN_CFW_RESUME_EVENT_PENDED_LOAD,
        open_cfw_resume_host_pended
    );
    return open_cfw_resume_host_pended;
}

static void open_cfw_resume_host_pended_store(uint32_t value)
{
    open_cfw_resume_host_pended = value;
    open_cfw_resume_host_record(OPEN_CFW_RESUME_EVENT_PENDED_STORE, value);
}

static int32_t open_cfw_resume_host_yield_load(void)
{
    open_cfw_resume_host_record(
        OPEN_CFW_RESUME_EVENT_YIELD_LOAD,
        (uint32_t)open_cfw_resume_host_yield_pending
    );
    return open_cfw_resume_host_yield_pending;
}

static void open_cfw_resume_host_yield_store(int32_t value)
{
    open_cfw_resume_host_yield_pending = value;
    open_cfw_resume_host_record(
        OPEN_CFW_RESUME_EVENT_YIELD_STORE,
        (uint32_t)value
    );
}

static void open_cfw_resume_host_enter(void)
{
    ++open_cfw_resume_host_enter_calls;
    open_cfw_resume_host_record(OPEN_CFW_RESUME_EVENT_ENTER, 0U);
}

static void open_cfw_resume_host_exit(void)
{
    ++open_cfw_resume_host_exit_calls;
    open_cfw_resume_host_record(OPEN_CFW_RESUME_EVENT_EXIT, 0U);
}

static void open_cfw_resume_host_yield(void)
{
    ++open_cfw_resume_host_yield_calls;
    open_cfw_resume_host_record(OPEN_CFW_RESUME_EVENT_YIELD_CALL, 0U);
}

static void open_cfw_resume_host_reset_next(void)
{
    ++open_cfw_resume_host_reset_calls;
    open_cfw_resume_host_record(OPEN_CFW_RESUME_EVENT_RESET_NEXT, 0U);
}

static int32_t open_cfw_resume_host_increment_tick(void)
{
    uint32_t result =
        (open_cfw_resume_host_tick_results >> open_cfw_resume_host_tick_calls) & 1U;

    ++open_cfw_resume_host_tick_calls;
    open_cfw_resume_host_record(OPEN_CFW_RESUME_EVENT_INCREMENT_TICK, result);
    return (int32_t)result;
}

static void open_cfw_resume_host_memory_barrier(void)
{
    open_cfw_resume_host_record(OPEN_CFW_RESUME_EVENT_MEMORY_BARRIER, 0U);
}

static void open_cfw_resume_host_assert(int condition)
{
    if (!condition) {
        ++open_cfw_resume_host_assert_calls;
        open_cfw_resume_host_record(OPEN_CFW_RESUME_EVENT_ASSERT, 0U);
        if (open_cfw_resume_host_execute_active != 0) {
            longjmp(open_cfw_resume_host_assert_jump, 1);
        }
    }
}

#undef OPEN_CFW_FREERTOS_RESUME_CURRENT_TCB_LOAD
#undef OPEN_CFW_FREERTOS_RESUME_CURRENT_TASK_COUNT_LOAD
#undef OPEN_CFW_FREERTOS_RESUME_TOP_READY_PRIORITY_LOAD
#undef OPEN_CFW_FREERTOS_RESUME_TOP_READY_PRIORITY_STORE
#undef OPEN_CFW_FREERTOS_RESUME_PENDED_TICKS_LOAD
#undef OPEN_CFW_FREERTOS_RESUME_PENDED_TICKS_STORE
#undef OPEN_CFW_FREERTOS_RESUME_YIELD_PENDING_LOAD
#undef OPEN_CFW_FREERTOS_RESUME_YIELD_PENDING_STORE
#undef OPEN_CFW_FREERTOS_RESUME_SCHEDULER_SUSPENDED_LOAD
#undef OPEN_CFW_FREERTOS_RESUME_SCHEDULER_SUSPENDED_STORE
#undef OPEN_CFW_FREERTOS_RESUME_PENDING_READY_LIST
#undef OPEN_CFW_FREERTOS_RESUME_READY_LIST
#undef OPEN_CFW_FREERTOS_RESUME_MEMORY_BARRIER
#undef OPEN_CFW_FREERTOS_RESUME_ENTER_CRITICAL
#undef OPEN_CFW_FREERTOS_RESUME_EXIT_CRITICAL
#undef OPEN_CFW_FREERTOS_RESUME_YIELD
#undef OPEN_CFW_FREERTOS_RESUME_RESET_NEXT_UNBLOCK_TIME
#undef OPEN_CFW_FREERTOS_RESUME_INCREMENT_TICK
#undef OPEN_CFW_FREERTOS_RESUME_ASSERT

#define OPEN_CFW_FREERTOS_RESUME_CURRENT_TCB_LOAD() \
    open_cfw_resume_host_current_load()
#define OPEN_CFW_FREERTOS_RESUME_CURRENT_TASK_COUNT_LOAD() \
    open_cfw_resume_host_current_tasks_load()
#define OPEN_CFW_FREERTOS_RESUME_TOP_READY_PRIORITY_LOAD() \
    open_cfw_resume_host_top_load()
#define OPEN_CFW_FREERTOS_RESUME_TOP_READY_PRIORITY_STORE(value) \
    open_cfw_resume_host_top_store(value)
#define OPEN_CFW_FREERTOS_RESUME_PENDED_TICKS_LOAD() \
    open_cfw_resume_host_pended_load()
#define OPEN_CFW_FREERTOS_RESUME_PENDED_TICKS_STORE(value) \
    open_cfw_resume_host_pended_store(value)
#define OPEN_CFW_FREERTOS_RESUME_YIELD_PENDING_LOAD() \
    open_cfw_resume_host_yield_load()
#define OPEN_CFW_FREERTOS_RESUME_YIELD_PENDING_STORE(value) \
    open_cfw_resume_host_yield_store(value)
#define OPEN_CFW_FREERTOS_RESUME_SCHEDULER_SUSPENDED_LOAD() \
    open_cfw_resume_host_suspended_load()
#define OPEN_CFW_FREERTOS_RESUME_SCHEDULER_SUSPENDED_STORE(value) \
    open_cfw_resume_host_suspended_store(value)
#define OPEN_CFW_FREERTOS_RESUME_PENDING_READY_LIST() \
    (&open_cfw_resume_host_pending)
#define OPEN_CFW_FREERTOS_RESUME_READY_LIST(priority) \
    (&open_cfw_resume_host_ready[(priority)])
#define OPEN_CFW_FREERTOS_RESUME_MEMORY_BARRIER() \
    open_cfw_resume_host_memory_barrier()
#define OPEN_CFW_FREERTOS_RESUME_ENTER_CRITICAL() \
    open_cfw_resume_host_enter()
#define OPEN_CFW_FREERTOS_RESUME_EXIT_CRITICAL() \
    open_cfw_resume_host_exit()
#define OPEN_CFW_FREERTOS_RESUME_YIELD() open_cfw_resume_host_yield()
#define OPEN_CFW_FREERTOS_RESUME_RESET_NEXT_UNBLOCK_TIME() \
    open_cfw_resume_host_reset_next()
#define OPEN_CFW_FREERTOS_RESUME_INCREMENT_TICK() \
    open_cfw_resume_host_increment_tick()
#define OPEN_CFW_FREERTOS_RESUME_ASSERT(condition) \
    open_cfw_resume_host_assert((condition))

#include "../../components/shared/freertos/runtime_freertos_task_resume_all.c"

void open_cfw_resume_host_reset(
    uint32_t suspended,
    uint32_t current_tasks,
    uint32_t pended_ticks,
    int32_t yield_pending,
    uint32_t top_ready_priority,
    uint32_t current_identifier,
    uint32_t tick_results
)
{
    uint32_t index;

    memset(open_cfw_resume_host_tasks, 0, sizeof(open_cfw_resume_host_tasks));
    open_cfw_resume_host_list_initialise(&open_cfw_resume_host_pending);
    open_cfw_resume_host_list_initialise(&open_cfw_resume_host_blocked);
    for (index = 0U; index < OPEN_CFW_FREERTOS_RESUME_MAX_PRIORITIES; ++index) {
        open_cfw_resume_host_list_initialise(&open_cfw_resume_host_ready[index]);
    }
    for (index = 0U; index < OPEN_CFW_RESUME_HOST_TASKS; ++index) {
        open_cfw_resume_host_tasks[index].state_list_item.owner =
            &open_cfw_resume_host_tasks[index];
        open_cfw_resume_host_tasks[index].event_list_item.owner =
            &open_cfw_resume_host_tasks[index];
    }
    open_cfw_resume_host_current = open_cfw_resume_host_task(current_identifier);
    open_cfw_resume_host_current_tasks = current_tasks;
    open_cfw_resume_host_top = top_ready_priority;
    open_cfw_resume_host_pended = pended_ticks;
    open_cfw_resume_host_yield_pending = yield_pending;
    open_cfw_resume_host_suspended = suspended;
    open_cfw_resume_host_tick_results = tick_results;
    open_cfw_resume_host_tick_calls = 0U;
    open_cfw_resume_host_enter_calls = 0U;
    open_cfw_resume_host_exit_calls = 0U;
    open_cfw_resume_host_yield_calls = 0U;
    open_cfw_resume_host_reset_calls = 0U;
    open_cfw_resume_host_assert_calls = 0U;
    open_cfw_resume_host_log_count = 0U;
    open_cfw_resume_host_execute_active = 0;
}

void open_cfw_resume_host_set_task(uint32_t identifier, uint32_t priority)
{
    struct open_cfw_freertos_resume_tcb *task =
        open_cfw_resume_host_task(identifier);

    if (task != (struct open_cfw_freertos_resume_tcb *)0 &&
        priority < OPEN_CFW_FREERTOS_RESUME_MAX_PRIORITIES) {
        task->priority = priority;
    }
}

void open_cfw_resume_host_insert_ready(uint32_t identifier)
{
    struct open_cfw_freertos_resume_tcb *task =
        open_cfw_resume_host_task(identifier);

    if (task != (struct open_cfw_freertos_resume_tcb *)0) {
        open_cfw_resume_host_list_insert_end(
            &open_cfw_resume_host_ready[task->priority],
            &task->state_list_item
        );
    }
}

void open_cfw_resume_host_insert_pending(uint32_t identifier)
{
    struct open_cfw_freertos_resume_tcb *task =
        open_cfw_resume_host_task(identifier);

    if (task != (struct open_cfw_freertos_resume_tcb *)0) {
        open_cfw_resume_host_list_insert_end(
            &open_cfw_resume_host_blocked,
            &task->state_list_item
        );
        open_cfw_resume_host_list_insert_end(
            &open_cfw_resume_host_pending,
            &task->event_list_item
        );
    }
}

void open_cfw_resume_host_set_list_index(uint32_t kind, uint32_t identifier)
{
    struct open_cfw_freertos_resume_list *list =
        open_cfw_resume_host_list(kind);
    struct open_cfw_freertos_resume_tcb *task;
    struct open_cfw_freertos_resume_list_item *item;

    if (list == (struct open_cfw_freertos_resume_list *)0) {
        return;
    }
    if (identifier == OPEN_CFW_RESUME_HOST_SENTINEL) {
        list->index = open_cfw_resume_host_sentinel(list);
        return;
    }
    task = open_cfw_resume_host_task(identifier);
    if (task == (struct open_cfw_freertos_resume_tcb *)0) {
        return;
    }
    item = (kind == OPEN_CFW_RESUME_HOST_PENDING) ?
        &task->event_list_item : &task->state_list_item;
    if (item->container == list) {
        list->index = item;
    }
}

int32_t open_cfw_resume_host_execute(void)
{
    int32_t result;

    open_cfw_resume_host_execute_active = 1;
    if (setjmp(open_cfw_resume_host_assert_jump) != 0) {
        open_cfw_resume_host_execute_active = 0;
        return (int32_t)OPEN_CFW_RESUME_HOST_ASSERTED;
    }
    result = open_cfw_freertos_task_resume_all();
    open_cfw_resume_host_execute_active = 0;
    return result;
}

#define OPEN_CFW_RESUME_HOST_GETTER(name, type, expression) \
    type open_cfw_resume_host_get_##name(void) { return (type)(expression); }

OPEN_CFW_RESUME_HOST_GETTER(suspended, uint32_t, open_cfw_resume_host_suspended)
OPEN_CFW_RESUME_HOST_GETTER(pended, uint32_t, open_cfw_resume_host_pended)
OPEN_CFW_RESUME_HOST_GETTER(yield_pending, int32_t, open_cfw_resume_host_yield_pending)
OPEN_CFW_RESUME_HOST_GETTER(top, uint32_t, open_cfw_resume_host_top)
OPEN_CFW_RESUME_HOST_GETTER(tick_calls, uint32_t, open_cfw_resume_host_tick_calls)
OPEN_CFW_RESUME_HOST_GETTER(enter_calls, uint32_t, open_cfw_resume_host_enter_calls)
OPEN_CFW_RESUME_HOST_GETTER(exit_calls, uint32_t, open_cfw_resume_host_exit_calls)
OPEN_CFW_RESUME_HOST_GETTER(yield_calls, uint32_t, open_cfw_resume_host_yield_calls)
OPEN_CFW_RESUME_HOST_GETTER(reset_calls, uint32_t, open_cfw_resume_host_reset_calls)
OPEN_CFW_RESUME_HOST_GETTER(assert_calls, uint32_t, open_cfw_resume_host_assert_calls)
OPEN_CFW_RESUME_HOST_GETTER(pending_count, uint32_t, open_cfw_resume_host_pending.item_count)
OPEN_CFW_RESUME_HOST_GETTER(blocked_count, uint32_t, open_cfw_resume_host_blocked.item_count)
OPEN_CFW_RESUME_HOST_GETTER(event_count, uint32_t, open_cfw_resume_host_log_count)

uint32_t open_cfw_resume_host_get_ready_count(uint32_t priority)
{
    if (priority >= OPEN_CFW_FREERTOS_RESUME_MAX_PRIORITIES) {
        return OPEN_CFW_RESUME_HOST_NULL;
    }
    return open_cfw_resume_host_ready[priority].item_count;
}

uint32_t open_cfw_resume_host_get_state_container(uint32_t identifier)
{
    struct open_cfw_freertos_resume_tcb *task =
        open_cfw_resume_host_task(identifier);
    uint32_t priority;

    if (task == (struct open_cfw_freertos_resume_tcb *)0) {
        return OPEN_CFW_RESUME_HOST_NULL;
    }
    if (task->state_list_item.container == &open_cfw_resume_host_blocked) {
        return OPEN_CFW_RESUME_HOST_BLOCKED;
    }
    for (priority = 0U; priority < OPEN_CFW_FREERTOS_RESUME_MAX_PRIORITIES; ++priority) {
        if (task->state_list_item.container == &open_cfw_resume_host_ready[priority]) {
            return OPEN_CFW_RESUME_HOST_READY + priority;
        }
    }
    return OPEN_CFW_RESUME_HOST_NULL;
}

uint32_t open_cfw_resume_host_get_event_container(uint32_t identifier)
{
    struct open_cfw_freertos_resume_tcb *task =
        open_cfw_resume_host_task(identifier);

    if (task != (struct open_cfw_freertos_resume_tcb *)0 &&
        task->event_list_item.container == &open_cfw_resume_host_pending) {
        return OPEN_CFW_RESUME_HOST_PENDING;
    }
    return OPEN_CFW_RESUME_HOST_NULL;
}

uint32_t open_cfw_resume_host_get_list_index(uint32_t kind)
{
    struct open_cfw_freertos_resume_list *list =
        open_cfw_resume_host_list(kind);
    struct open_cfw_freertos_resume_list_item *index;

    if (list == (struct open_cfw_freertos_resume_list *)0) {
        return OPEN_CFW_RESUME_HOST_NULL;
    }
    index = list->index;
    if (index == open_cfw_resume_host_sentinel(list)) {
        return OPEN_CFW_RESUME_HOST_SENTINEL;
    }
    return open_cfw_resume_host_task_identifier(index->owner);
}

uint32_t open_cfw_resume_host_get_list_owner(
    uint32_t kind,
    uint32_t position
)
{
    struct open_cfw_freertos_resume_list *list =
        open_cfw_resume_host_list(kind);
    struct open_cfw_freertos_resume_list_item *sentinel;
    struct open_cfw_freertos_resume_list_item *item;
    uint32_t index;

    if (list == (struct open_cfw_freertos_resume_list *)0) {
        return OPEN_CFW_RESUME_HOST_NULL;
    }
    sentinel = open_cfw_resume_host_sentinel(list);
    item = sentinel->next;
    for (index = 0U; index < position && item != sentinel; ++index) {
        item = item->next;
    }
    if (item == sentinel) {
        return OPEN_CFW_RESUME_HOST_NULL;
    }
    return open_cfw_resume_host_task_identifier(item->owner);
}

uint32_t open_cfw_resume_host_get_event_kind(uint32_t index)
{
    if (index >= open_cfw_resume_host_log_count ||
        index >= OPEN_CFW_RESUME_HOST_EVENTS) {
        return OPEN_CFW_RESUME_HOST_NULL;
    }
    return open_cfw_resume_host_log[index].kind;
}

uint32_t open_cfw_resume_host_get_event_value(uint32_t index)
{
    if (index >= open_cfw_resume_host_log_count ||
        index >= OPEN_CFW_RESUME_HOST_EVENTS) {
        return OPEN_CFW_RESUME_HOST_NULL;
    }
    return open_cfw_resume_host_log[index].value;
}
