/*
 * SPDX-License-Identifier: GPL-3.0-only
 */

typedef __UINTPTR_TYPE__
    open_cfw_test_rtos_event_group_set_callback_uintptr;

unsigned int open_cfw_test_rtos_event_group_set_callback_calls;
unsigned int open_cfw_test_rtos_event_group_set_callback_bits;
unsigned int open_cfw_test_rtos_event_group_set_callback_result;
open_cfw_test_rtos_event_group_set_callback_uintptr
    open_cfw_test_rtos_event_group_set_callback_group;

void open_cfw_test_rtos_event_group_set_callback_reset(void)
{
    open_cfw_test_rtos_event_group_set_callback_calls = 0U;
    open_cfw_test_rtos_event_group_set_callback_bits = 0U;
    open_cfw_test_rtos_event_group_set_callback_result = 0U;
    open_cfw_test_rtos_event_group_set_callback_group = 0U;
}

void open_cfw_test_rtos_event_group_set_callback_set_result(
    unsigned int result
)
{
    open_cfw_test_rtos_event_group_set_callback_result = result;
}

static unsigned int open_cfw_test_rtos_event_group_set_callback_set(
    void *group,
    unsigned int bits
)
{
    ++open_cfw_test_rtos_event_group_set_callback_calls;
    open_cfw_test_rtos_event_group_set_callback_group =
        (open_cfw_test_rtos_event_group_set_callback_uintptr)group;
    open_cfw_test_rtos_event_group_set_callback_bits = bits;
    return open_cfw_test_rtos_event_group_set_callback_result;
}

#define OPEN_CFW_RTOS_EVENT_GROUP_SET_CALLBACK_SET(group, bits) \
    open_cfw_test_rtos_event_group_set_callback_set((group), (bits))

#include "../../components/apollo_main/core_overlay/rtos_event_group_set_callback.c"
