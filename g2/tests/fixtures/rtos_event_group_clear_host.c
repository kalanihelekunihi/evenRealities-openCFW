/*
 * SPDX-License-Identifier: MIT
 */

typedef __UINTPTR_TYPE__ open_cfw_test_rtos_event_group_clear_uintptr;

unsigned int open_cfw_test_rtos_event_group_clear_events[16];
unsigned int open_cfw_test_rtos_event_group_clear_event_depths[16];
unsigned int open_cfw_test_rtos_event_group_clear_event_count;
unsigned int open_cfw_test_rtos_event_group_clear_fail_stop_calls;
unsigned int open_cfw_test_rtos_event_group_clear_enter_calls;
unsigned int open_cfw_test_rtos_event_group_clear_exit_calls;
unsigned int open_cfw_test_rtos_event_group_clear_read_calls;
unsigned int open_cfw_test_rtos_event_group_clear_write_calls;
unsigned int open_cfw_test_rtos_event_group_clear_critical_depth;
unsigned int open_cfw_test_rtos_event_group_clear_mutate_after_first_read;
unsigned int open_cfw_test_rtos_event_group_clear_mutated_bits;
unsigned int open_cfw_test_rtos_event_group_clear_last_write;
open_cfw_test_rtos_event_group_clear_uintptr
    open_cfw_test_rtos_event_group_clear_last_read_group;
open_cfw_test_rtos_event_group_clear_uintptr
    open_cfw_test_rtos_event_group_clear_last_write_group;
unsigned int open_cfw_test_rtos_event_group_clear_group[8];

static void open_cfw_test_rtos_event_group_clear_record(unsigned int event)
{
    unsigned int index =
        open_cfw_test_rtos_event_group_clear_event_count++;

    open_cfw_test_rtos_event_group_clear_events[index] = event;
    open_cfw_test_rtos_event_group_clear_event_depths[index] =
        open_cfw_test_rtos_event_group_clear_critical_depth;
}

void open_cfw_test_rtos_event_group_clear_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_event_group_clear_event_count = 0U;
    open_cfw_test_rtos_event_group_clear_fail_stop_calls = 0U;
    open_cfw_test_rtos_event_group_clear_enter_calls = 0U;
    open_cfw_test_rtos_event_group_clear_exit_calls = 0U;
    open_cfw_test_rtos_event_group_clear_read_calls = 0U;
    open_cfw_test_rtos_event_group_clear_write_calls = 0U;
    open_cfw_test_rtos_event_group_clear_critical_depth = 0U;
    open_cfw_test_rtos_event_group_clear_mutate_after_first_read = 0U;
    open_cfw_test_rtos_event_group_clear_mutated_bits = 0U;
    open_cfw_test_rtos_event_group_clear_last_write = 0U;
    open_cfw_test_rtos_event_group_clear_last_read_group = 0U;
    open_cfw_test_rtos_event_group_clear_last_write_group = 0U;
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_rtos_event_group_clear_events[index] = 0U;
        open_cfw_test_rtos_event_group_clear_event_depths[index] = 0U;
    }
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_rtos_event_group_clear_group[index] = 0U;
    }
}

void open_cfw_test_rtos_event_group_clear_set_group_bits(
    unsigned int value
)
{
    open_cfw_test_rtos_event_group_clear_group[0] = value;
}

void open_cfw_test_rtos_event_group_clear_set_mutated_bits(
    unsigned int enabled,
    unsigned int value
)
{
    open_cfw_test_rtos_event_group_clear_mutate_after_first_read = enabled;
    open_cfw_test_rtos_event_group_clear_mutated_bits = value;
}

static void open_cfw_test_rtos_event_group_clear_enter(void)
{
    ++open_cfw_test_rtos_event_group_clear_critical_depth;
    open_cfw_test_rtos_event_group_clear_record(20U);
    ++open_cfw_test_rtos_event_group_clear_enter_calls;
}

static void open_cfw_test_rtos_event_group_clear_exit(void)
{
    open_cfw_test_rtos_event_group_clear_record(50U);
    ++open_cfw_test_rtos_event_group_clear_exit_calls;
    --open_cfw_test_rtos_event_group_clear_critical_depth;
}

static unsigned int open_cfw_test_rtos_event_group_clear_read_bits(
    void *group
)
{
    unsigned int value = *(unsigned int *)group;

    open_cfw_test_rtos_event_group_clear_record(30U);
    open_cfw_test_rtos_event_group_clear_last_read_group =
        (open_cfw_test_rtos_event_group_clear_uintptr)group;
    ++open_cfw_test_rtos_event_group_clear_read_calls;
    if (
        open_cfw_test_rtos_event_group_clear_read_calls == 1U
        && open_cfw_test_rtos_event_group_clear_mutate_after_first_read
            != 0U
    ) {
        *(unsigned int *)group =
            open_cfw_test_rtos_event_group_clear_mutated_bits;
    }
    return value;
}

static void open_cfw_test_rtos_event_group_clear_write_bits(
    void *group,
    unsigned int value
)
{
    open_cfw_test_rtos_event_group_clear_record(40U);
    ++open_cfw_test_rtos_event_group_clear_write_calls;
    open_cfw_test_rtos_event_group_clear_last_write_group =
        (open_cfw_test_rtos_event_group_clear_uintptr)group;
    open_cfw_test_rtos_event_group_clear_last_write = value;
    *(unsigned int *)group = value;
}

static void open_cfw_test_rtos_event_group_clear_fail_stop(void)
{
    open_cfw_test_rtos_event_group_clear_record(10U);
    ++open_cfw_test_rtos_event_group_clear_fail_stop_calls;
}

#define OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_ENTER_CRITICAL() \
    open_cfw_test_rtos_event_group_clear_enter()
#define OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_EXIT_CRITICAL() \
    open_cfw_test_rtos_event_group_clear_exit()
#define OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_READ_BITS(group) \
    open_cfw_test_rtos_event_group_clear_read_bits(group)
#define OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_WRITE_BITS(group, value) \
    open_cfw_test_rtos_event_group_clear_write_bits((group), (value))
#define OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_FAIL_STOP() \
    open_cfw_test_rtos_event_group_clear_fail_stop()

#include "../../components/apollo_main/core_overlay/rtos_event_group_clear.c"
