/*
 * SPDX-License-Identifier: MIT
 *
 * Deterministic host graph for the G2 vTaskSwitchContext source candidate.
 */

#include <stdint.h>
#include <string.h>

#define OPEN_CFW_FREERTOS_SWITCH_CURRENT_TCB_LOAD() \
    (open_cfw_test_switch_current)
#define OPEN_CFW_FREERTOS_SWITCH_CURRENT_TCB_STORE(value) \
    (open_cfw_test_switch_current = (value))
#define OPEN_CFW_FREERTOS_SWITCH_TOP_READY_PRIORITY_LOAD() \
    (open_cfw_test_switch_top_priority)
#define OPEN_CFW_FREERTOS_SWITCH_TOP_READY_PRIORITY_STORE(value) \
    (open_cfw_test_switch_top_priority = (value))
#define OPEN_CFW_FREERTOS_SWITCH_YIELD_PENDING_STORE(value) \
    (open_cfw_test_switch_yield_pending = (value))
#define OPEN_CFW_FREERTOS_SWITCH_SCHEDULER_SUSPENDED_LOAD() \
    (open_cfw_test_switch_scheduler_suspended)
#define OPEN_CFW_FREERTOS_SWITCH_TRACE_INDEX_LOAD() \
    (open_cfw_test_switch_trace_index)
#define OPEN_CFW_FREERTOS_SWITCH_TRACE_INDEX_STORE(value) \
    (open_cfw_test_switch_trace_index = (value))
#define OPEN_CFW_FREERTOS_SWITCH_READY_LIST(priority) \
    (&open_cfw_test_switch_ready[(priority)])
#define OPEN_CFW_FREERTOS_SWITCH_TRACE_RECORD(index) \
    (&open_cfw_test_switch_trace[(index)])
#define OPEN_CFW_FREERTOS_SWITCH_STACK_OVERFLOW_HOOK(tcb, task_name) \
    open_cfw_test_switch_stack_overflow((tcb), (task_name))
#define OPEN_CFW_FREERTOS_SWITCH_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            ++open_cfw_test_switch_assertions; \
            return; \
        } \
    } while (0)

#include "../../components/shared/freertos/runtime_freertos_task_switch_context.h"

enum {
    OPEN_CFW_TEST_SWITCH_TASK_COUNT = 8U,
    OPEN_CFW_TEST_SWITCH_SENTINEL = 0xFFFFFFFFU
};

static struct open_cfw_freertos_switch_tcb open_cfw_test_switch_tasks[
    OPEN_CFW_TEST_SWITCH_TASK_COUNT
];
static open_cfw_freertos_switch_stack_type open_cfw_test_switch_stacks[
    OPEN_CFW_TEST_SWITCH_TASK_COUNT
][4];
static struct open_cfw_freertos_switch_list open_cfw_test_switch_ready[
    OPEN_CFW_FREERTOS_SWITCH_MAX_PRIORITIES
];
static struct open_cfw_freertos_switch_trace_record open_cfw_test_switch_trace[
    OPEN_CFW_FREERTOS_SWITCH_TRACE_CAPACITY
];
static struct open_cfw_freertos_switch_tcb *open_cfw_test_switch_current;
static open_cfw_freertos_switch_ubase_type open_cfw_test_switch_top_priority;
static open_cfw_freertos_switch_ubase_type open_cfw_test_switch_yield_pending;
static open_cfw_freertos_switch_ubase_type
    open_cfw_test_switch_scheduler_suspended;
static open_cfw_freertos_switch_ubase_type open_cfw_test_switch_trace_index;
static open_cfw_freertos_switch_ubase_type open_cfw_test_switch_assertions;
static open_cfw_freertos_switch_ubase_type open_cfw_test_switch_overflows;
static struct open_cfw_freertos_switch_tcb *
    open_cfw_test_switch_overflow_tcb;
static const char *open_cfw_test_switch_overflow_name;

static struct open_cfw_freertos_switch_list_item *
open_cfw_test_switch_sentinel(struct open_cfw_freertos_switch_list *list)
{
    return (struct open_cfw_freertos_switch_list_item *)(void *)&list->end;
}

static void open_cfw_test_switch_list_initialise(
    struct open_cfw_freertos_switch_list *list
)
{
    struct open_cfw_freertos_switch_list_item *sentinel =
        open_cfw_test_switch_sentinel(list);

    list->item_count = 0U;
    list->index = sentinel;
    list->end.item_value = 0xFFFFFFFFU;
    list->end.next = sentinel;
    list->end.previous = sentinel;
}

static void open_cfw_test_switch_stack_overflow(
    struct open_cfw_freertos_switch_tcb *tcb,
    const char *task_name
)
{
    ++open_cfw_test_switch_overflows;
    open_cfw_test_switch_overflow_tcb = tcb;
    open_cfw_test_switch_overflow_name = task_name;
}

static uint32_t open_cfw_test_switch_task_identifier(
    const struct open_cfw_freertos_switch_tcb *tcb
)
{
    uint32_t index;

    for (index = 0U; index < OPEN_CFW_TEST_SWITCH_TASK_COUNT; ++index) {
        if (tcb == &open_cfw_test_switch_tasks[index]) {
            return index;
        }
    }
    return OPEN_CFW_TEST_SWITCH_SENTINEL;
}

void open_cfw_test_switch_reset(void)
{
    uint32_t index;
    uint32_t word;

    memset(open_cfw_test_switch_tasks, 0, sizeof(open_cfw_test_switch_tasks));
    memset(open_cfw_test_switch_trace, 0xCC, sizeof(open_cfw_test_switch_trace));
    for (index = 0U; index < OPEN_CFW_FREERTOS_SWITCH_MAX_PRIORITIES; ++index) {
        open_cfw_test_switch_list_initialise(&open_cfw_test_switch_ready[index]);
    }
    for (index = 0U; index < OPEN_CFW_TEST_SWITCH_TASK_COUNT; ++index) {
        struct open_cfw_freertos_switch_tcb *tcb =
            &open_cfw_test_switch_tasks[index];

        tcb->state_list_item.owner = tcb;
        tcb->stack_base = open_cfw_test_switch_stacks[index];
        tcb->task_name[0] = 'T';
        tcb->task_name[1] = (char)('0' + index);
        tcb->task_name[2] = '\0';
        tcb->task_number = 100U + index;
        for (word = 0U; word < 4U; ++word) {
            open_cfw_test_switch_stacks[index][word] =
                OPEN_CFW_FREERTOS_SWITCH_STACK_FILL_WORD;
        }
    }
    open_cfw_test_switch_current = &open_cfw_test_switch_tasks[0];
    open_cfw_test_switch_top_priority = 0U;
    open_cfw_test_switch_yield_pending = 0xCCCCCCCCU;
    open_cfw_test_switch_scheduler_suspended = 0U;
    open_cfw_test_switch_trace_index = 0U;
    open_cfw_test_switch_assertions = 0U;
    open_cfw_test_switch_overflows = 0U;
    open_cfw_test_switch_overflow_tcb =
        (struct open_cfw_freertos_switch_tcb *)0;
    open_cfw_test_switch_overflow_name = (const char *)0;
}

void open_cfw_test_switch_set_suspended(uint32_t value)
{
    open_cfw_test_switch_scheduler_suspended = value;
}

void open_cfw_test_switch_set_current(uint32_t identifier)
{
    open_cfw_test_switch_current = &open_cfw_test_switch_tasks[identifier];
}

void open_cfw_test_switch_set_top_priority(uint32_t priority)
{
    open_cfw_test_switch_top_priority = priority;
}

void open_cfw_test_switch_set_trace_index(uint32_t index)
{
    open_cfw_test_switch_trace_index = index;
}

void open_cfw_test_switch_set_stack_word(
    uint32_t identifier,
    uint32_t word,
    uint32_t value
)
{
    open_cfw_test_switch_stacks[identifier][word] = value;
}

void open_cfw_test_switch_add_ready(uint32_t priority, uint32_t identifier)
{
    struct open_cfw_freertos_switch_list *list =
        &open_cfw_test_switch_ready[priority];
    struct open_cfw_freertos_switch_list_item *item =
        &open_cfw_test_switch_tasks[identifier].state_list_item;
    struct open_cfw_freertos_switch_list_item *sentinel =
        open_cfw_test_switch_sentinel(list);

    item->next = sentinel;
    item->previous = sentinel->previous;
    sentinel->previous->next = item;
    sentinel->previous = item;
    item->container = list;
    ++list->item_count;
}

void open_cfw_test_switch_set_ready_index(
    uint32_t priority,
    uint32_t identifier
)
{
    struct open_cfw_freertos_switch_list *list =
        &open_cfw_test_switch_ready[priority];

    if (identifier == OPEN_CFW_TEST_SWITCH_SENTINEL) {
        list->index = open_cfw_test_switch_sentinel(list);
    } else {
        list->index = &open_cfw_test_switch_tasks[identifier].state_list_item;
    }
}

uint32_t open_cfw_test_switch_get_current(void)
{
    return open_cfw_test_switch_task_identifier(open_cfw_test_switch_current);
}

uint32_t open_cfw_test_switch_get_top_priority(void)
{
    return open_cfw_test_switch_top_priority;
}

uint32_t open_cfw_test_switch_get_yield_pending(void)
{
    return open_cfw_test_switch_yield_pending;
}

uint32_t open_cfw_test_switch_get_trace_index(void)
{
    return open_cfw_test_switch_trace_index;
}

uint32_t open_cfw_test_switch_get_trace_out(uint32_t index)
{
    return open_cfw_test_switch_trace[index].switched_out;
}

uint32_t open_cfw_test_switch_get_trace_in(uint32_t index)
{
    return open_cfw_test_switch_trace[index].switched_in;
}

uint32_t open_cfw_test_switch_get_ready_index(uint32_t priority)
{
    struct open_cfw_freertos_switch_list *list =
        &open_cfw_test_switch_ready[priority];
    struct open_cfw_freertos_switch_list_item *item = list->index;

    if (item == open_cfw_test_switch_sentinel(list)) {
        return OPEN_CFW_TEST_SWITCH_SENTINEL;
    }
    return open_cfw_test_switch_task_identifier(
        (const struct open_cfw_freertos_switch_tcb *)item->owner
    );
}

uint32_t open_cfw_test_switch_get_assertions(void)
{
    return open_cfw_test_switch_assertions;
}

uint32_t open_cfw_test_switch_get_overflows(void)
{
    return open_cfw_test_switch_overflows;
}

uint32_t open_cfw_test_switch_get_overflow_task(void)
{
    return open_cfw_test_switch_task_identifier(
        open_cfw_test_switch_overflow_tcb
    );
}

const char *open_cfw_test_switch_get_overflow_name(void)
{
    return open_cfw_test_switch_overflow_name;
}

#include "../../components/shared/freertos/runtime_freertos_task_switch_context.c"
