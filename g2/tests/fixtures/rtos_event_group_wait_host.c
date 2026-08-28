/*
 * SPDX-License-Identifier: MIT
 */

typedef __UINTPTR_TYPE__ open_cfw_test_rtos_event_group_wait_uintptr;

unsigned int open_cfw_test_rtos_event_group_wait_events[64];
unsigned int open_cfw_test_rtos_event_group_wait_event_depths[64];
unsigned int open_cfw_test_rtos_event_group_wait_event_count;
unsigned int open_cfw_test_rtos_event_group_wait_fail_stop_calls;
unsigned int open_cfw_test_rtos_event_group_wait_scheduler_reads;
unsigned int open_cfw_test_rtos_event_group_wait_suspend_calls;
unsigned int open_cfw_test_rtos_event_group_wait_resume_calls;
unsigned int open_cfw_test_rtos_event_group_wait_read_calls;
unsigned int open_cfw_test_rtos_event_group_wait_write_calls;
unsigned int open_cfw_test_rtos_event_group_wait_place_calls;
unsigned int open_cfw_test_rtos_event_group_wait_yield_calls;
unsigned int open_cfw_test_rtos_event_group_wait_reset_calls;
unsigned int open_cfw_test_rtos_event_group_wait_enter_calls;
unsigned int open_cfw_test_rtos_event_group_wait_exit_calls;
unsigned int open_cfw_test_rtos_event_group_wait_critical_depth;
unsigned int open_cfw_test_rtos_event_group_wait_scheduler_state;
unsigned int open_cfw_test_rtos_event_group_wait_resume_result;
unsigned int open_cfw_test_rtos_event_group_wait_reset_value;
unsigned int open_cfw_test_rtos_event_group_wait_reset_new_bits_enabled;
unsigned int open_cfw_test_rtos_event_group_wait_reset_new_bits;
unsigned int open_cfw_test_rtos_event_group_wait_last_write;
unsigned int open_cfw_test_rtos_event_group_wait_last_place_value;
unsigned int open_cfw_test_rtos_event_group_wait_last_place_ticks;
open_cfw_test_rtos_event_group_wait_uintptr
    open_cfw_test_rtos_event_group_wait_last_read_group;
open_cfw_test_rtos_event_group_wait_uintptr
    open_cfw_test_rtos_event_group_wait_last_write_group;
open_cfw_test_rtos_event_group_wait_uintptr
    open_cfw_test_rtos_event_group_wait_last_place_list;
unsigned int open_cfw_test_rtos_event_group_wait_group[8];

static void open_cfw_test_rtos_event_group_wait_record(unsigned int event)
{
    unsigned int index =
        open_cfw_test_rtos_event_group_wait_event_count++;

    open_cfw_test_rtos_event_group_wait_events[index] = event;
    open_cfw_test_rtos_event_group_wait_event_depths[index] =
        open_cfw_test_rtos_event_group_wait_critical_depth;
}

void open_cfw_test_rtos_event_group_wait_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_event_group_wait_event_count = 0U;
    open_cfw_test_rtos_event_group_wait_fail_stop_calls = 0U;
    open_cfw_test_rtos_event_group_wait_scheduler_reads = 0U;
    open_cfw_test_rtos_event_group_wait_suspend_calls = 0U;
    open_cfw_test_rtos_event_group_wait_resume_calls = 0U;
    open_cfw_test_rtos_event_group_wait_read_calls = 0U;
    open_cfw_test_rtos_event_group_wait_write_calls = 0U;
    open_cfw_test_rtos_event_group_wait_place_calls = 0U;
    open_cfw_test_rtos_event_group_wait_yield_calls = 0U;
    open_cfw_test_rtos_event_group_wait_reset_calls = 0U;
    open_cfw_test_rtos_event_group_wait_enter_calls = 0U;
    open_cfw_test_rtos_event_group_wait_exit_calls = 0U;
    open_cfw_test_rtos_event_group_wait_critical_depth = 0U;
    open_cfw_test_rtos_event_group_wait_scheduler_state = 2U;
    open_cfw_test_rtos_event_group_wait_resume_result = 1U;
    open_cfw_test_rtos_event_group_wait_reset_value = 0U;
    open_cfw_test_rtos_event_group_wait_reset_new_bits_enabled = 0U;
    open_cfw_test_rtos_event_group_wait_reset_new_bits = 0U;
    open_cfw_test_rtos_event_group_wait_last_write = 0U;
    open_cfw_test_rtos_event_group_wait_last_place_value = 0U;
    open_cfw_test_rtos_event_group_wait_last_place_ticks = 0U;
    open_cfw_test_rtos_event_group_wait_last_read_group = 0U;
    open_cfw_test_rtos_event_group_wait_last_write_group = 0U;
    open_cfw_test_rtos_event_group_wait_last_place_list = 0U;
    for (index = 0U; index < 64U; ++index) {
        open_cfw_test_rtos_event_group_wait_events[index] = 0U;
        open_cfw_test_rtos_event_group_wait_event_depths[index] = 0U;
    }
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_rtos_event_group_wait_group[index] = 0U;
    }
}

void open_cfw_test_rtos_event_group_wait_set_group_bits(unsigned int value)
{
    open_cfw_test_rtos_event_group_wait_group[0] = value;
}

void open_cfw_test_rtos_event_group_wait_set_scheduler_state(
    unsigned int value
)
{
    open_cfw_test_rtos_event_group_wait_scheduler_state = value;
}

void open_cfw_test_rtos_event_group_wait_set_resume_result(
    unsigned int value
)
{
    open_cfw_test_rtos_event_group_wait_resume_result = value;
}

void open_cfw_test_rtos_event_group_wait_set_reset_value(
    unsigned int value
)
{
    open_cfw_test_rtos_event_group_wait_reset_value = value;
}

void open_cfw_test_rtos_event_group_wait_set_reset_new_bits(
    unsigned int enabled,
    unsigned int value
)
{
    open_cfw_test_rtos_event_group_wait_reset_new_bits_enabled = enabled;
    open_cfw_test_rtos_event_group_wait_reset_new_bits = value;
}

static unsigned int open_cfw_test_rtos_event_group_wait_scheduler(void)
{
    open_cfw_test_rtos_event_group_wait_record(20U);
    ++open_cfw_test_rtos_event_group_wait_scheduler_reads;
    return open_cfw_test_rtos_event_group_wait_scheduler_state;
}

static void open_cfw_test_rtos_event_group_wait_suspend(void)
{
    open_cfw_test_rtos_event_group_wait_record(30U);
    ++open_cfw_test_rtos_event_group_wait_suspend_calls;
}

static unsigned int open_cfw_test_rtos_event_group_wait_resume(void)
{
    open_cfw_test_rtos_event_group_wait_record(70U);
    ++open_cfw_test_rtos_event_group_wait_resume_calls;
    return open_cfw_test_rtos_event_group_wait_resume_result;
}

static unsigned int open_cfw_test_rtos_event_group_wait_read_bits(
    void *group
)
{
    open_cfw_test_rtos_event_group_wait_record(40U);
    ++open_cfw_test_rtos_event_group_wait_read_calls;
    open_cfw_test_rtos_event_group_wait_last_read_group =
        (open_cfw_test_rtos_event_group_wait_uintptr)group;
    return *(unsigned int *)group;
}

static void open_cfw_test_rtos_event_group_wait_write_bits(
    void *group,
    unsigned int value
)
{
    open_cfw_test_rtos_event_group_wait_record(50U);
    ++open_cfw_test_rtos_event_group_wait_write_calls;
    open_cfw_test_rtos_event_group_wait_last_write_group =
        (open_cfw_test_rtos_event_group_wait_uintptr)group;
    open_cfw_test_rtos_event_group_wait_last_write = value;
    *(unsigned int *)group = value;
}

static void open_cfw_test_rtos_event_group_wait_place(
    void *list,
    unsigned int value,
    unsigned int ticks
)
{
    open_cfw_test_rtos_event_group_wait_record(60U);
    ++open_cfw_test_rtos_event_group_wait_place_calls;
    open_cfw_test_rtos_event_group_wait_last_place_list =
        (open_cfw_test_rtos_event_group_wait_uintptr)list;
    open_cfw_test_rtos_event_group_wait_last_place_value = value;
    open_cfw_test_rtos_event_group_wait_last_place_ticks = ticks;
}

static void open_cfw_test_rtos_event_group_wait_yield(void)
{
    open_cfw_test_rtos_event_group_wait_record(80U);
    ++open_cfw_test_rtos_event_group_wait_yield_calls;
}

static unsigned int open_cfw_test_rtos_event_group_wait_reset_item(void)
{
    open_cfw_test_rtos_event_group_wait_record(90U);
    ++open_cfw_test_rtos_event_group_wait_reset_calls;
    if (
        open_cfw_test_rtos_event_group_wait_reset_new_bits_enabled != 0U
    ) {
        open_cfw_test_rtos_event_group_wait_group[0] =
            open_cfw_test_rtos_event_group_wait_reset_new_bits;
    }
    return open_cfw_test_rtos_event_group_wait_reset_value;
}

static void open_cfw_test_rtos_event_group_wait_enter(void)
{
    ++open_cfw_test_rtos_event_group_wait_critical_depth;
    open_cfw_test_rtos_event_group_wait_record(100U);
    ++open_cfw_test_rtos_event_group_wait_enter_calls;
}

static void open_cfw_test_rtos_event_group_wait_exit(void)
{
    open_cfw_test_rtos_event_group_wait_record(110U);
    ++open_cfw_test_rtos_event_group_wait_exit_calls;
    --open_cfw_test_rtos_event_group_wait_critical_depth;
}

static void open_cfw_test_rtos_event_group_wait_fail_stop(void)
{
    open_cfw_test_rtos_event_group_wait_record(10U);
    ++open_cfw_test_rtos_event_group_wait_fail_stop_calls;
}

#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_SCHEDULER_STATE() \
    open_cfw_test_rtos_event_group_wait_scheduler()
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_SUSPEND_ALL() \
    open_cfw_test_rtos_event_group_wait_suspend()
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_RESUME_ALL() \
    open_cfw_test_rtos_event_group_wait_resume()
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_PLACE(list, value, ticks) \
    open_cfw_test_rtos_event_group_wait_place((list), (value), (ticks))
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_RESET_ITEM_VALUE() \
    open_cfw_test_rtos_event_group_wait_reset_item()
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_YIELD() \
    open_cfw_test_rtos_event_group_wait_yield()
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_ENTER_CRITICAL() \
    open_cfw_test_rtos_event_group_wait_enter()
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_EXIT_CRITICAL() \
    open_cfw_test_rtos_event_group_wait_exit()
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_READ_BITS(group) \
    open_cfw_test_rtos_event_group_wait_read_bits(group)
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_WRITE_BITS(group, value) \
    open_cfw_test_rtos_event_group_wait_write_bits((group), (value))
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_FAIL_STOP() \
    open_cfw_test_rtos_event_group_wait_fail_stop()

#include "../../components/apollo_main/core_overlay/rtos_event_group_test_wait_condition.c"
#include "../../components/apollo_main/core_overlay/rtos_event_group_wait.c"
