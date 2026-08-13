/*
 * SPDX-License-Identifier: GPL-3.0-only
 */

typedef __UINTPTR_TYPE__
    open_cfw_test_rtos_event_group_clear_from_isr_uintptr;

unsigned int open_cfw_test_rtos_event_group_clear_from_isr_calls;
int open_cfw_test_rtos_event_group_clear_from_isr_result;
open_cfw_test_rtos_event_group_clear_from_isr_uintptr
    open_cfw_test_rtos_event_group_clear_from_isr_callback;
open_cfw_test_rtos_event_group_clear_from_isr_uintptr
    open_cfw_test_rtos_event_group_clear_from_isr_group;
unsigned int open_cfw_test_rtos_event_group_clear_from_isr_bits;
open_cfw_test_rtos_event_group_clear_from_isr_uintptr
    open_cfw_test_rtos_event_group_clear_from_isr_wake_pointer;

void open_cfw_test_rtos_event_group_clear_from_isr_reset(void)
{
    open_cfw_test_rtos_event_group_clear_from_isr_calls = 0U;
    open_cfw_test_rtos_event_group_clear_from_isr_result = 0;
    open_cfw_test_rtos_event_group_clear_from_isr_callback = 0U;
    open_cfw_test_rtos_event_group_clear_from_isr_group = 0U;
    open_cfw_test_rtos_event_group_clear_from_isr_bits = 0U;
    open_cfw_test_rtos_event_group_clear_from_isr_wake_pointer = 0U;
}

void open_cfw_test_rtos_event_group_clear_from_isr_set_result(int result)
{
    open_cfw_test_rtos_event_group_clear_from_isr_result = result;
}

void open_cfw_rtos_event_group_clear_callback(
    void *group,
    unsigned int bits_to_clear
)
{
    (void)group;
    (void)bits_to_clear;
}

static int open_cfw_test_rtos_event_group_clear_from_isr_pend(
    void (*callback)(void *, unsigned int),
    void *group,
    unsigned int bits,
    int *wake_pointer
)
{
    ++open_cfw_test_rtos_event_group_clear_from_isr_calls;
    open_cfw_test_rtos_event_group_clear_from_isr_callback =
        (open_cfw_test_rtos_event_group_clear_from_isr_uintptr)callback;
    open_cfw_test_rtos_event_group_clear_from_isr_group =
        (open_cfw_test_rtos_event_group_clear_from_isr_uintptr)group;
    open_cfw_test_rtos_event_group_clear_from_isr_bits = bits;
    open_cfw_test_rtos_event_group_clear_from_isr_wake_pointer =
        (open_cfw_test_rtos_event_group_clear_from_isr_uintptr)wake_pointer;
    return open_cfw_test_rtos_event_group_clear_from_isr_result;
}

#define OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_FROM_ISR_PEND( \
    callback, group, bits, wake_pointer \
) \
    open_cfw_test_rtos_event_group_clear_from_isr_pend( \
        (callback), \
        (group), \
        (bits), \
        (wake_pointer) \
    )

#include "../../components/apollo_main/core_overlay/rtos_event_group_clear_from_isr.c"
