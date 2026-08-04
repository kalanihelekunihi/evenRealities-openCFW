/*
 * SPDX-License-Identifier: GPL-3.0-only
 */

typedef __UINTPTR_TYPE__
    open_cfw_test_rtos_event_group_get_bits_from_isr_uintptr;

unsigned int open_cfw_test_rtos_event_group_get_bits_from_isr_events[8];
unsigned int open_cfw_test_rtos_event_group_get_bits_from_isr_event_count;
unsigned int open_cfw_test_rtos_event_group_get_bits_from_isr_set_calls;
unsigned int open_cfw_test_rtos_event_group_get_bits_from_isr_read_calls;
unsigned int open_cfw_test_rtos_event_group_get_bits_from_isr_restore_calls;
unsigned int open_cfw_test_rtos_event_group_get_bits_from_isr_mask;
unsigned int open_cfw_test_rtos_event_group_get_bits_from_isr_bits;
unsigned int open_cfw_test_rtos_event_group_get_bits_from_isr_restored_mask;
open_cfw_test_rtos_event_group_get_bits_from_isr_uintptr
    open_cfw_test_rtos_event_group_get_bits_from_isr_group;

static void open_cfw_test_rtos_event_group_get_bits_from_isr_record(
    unsigned int event
)
{
    open_cfw_test_rtos_event_group_get_bits_from_isr_events[
        open_cfw_test_rtos_event_group_get_bits_from_isr_event_count++
    ] = event;
}

void open_cfw_test_rtos_event_group_get_bits_from_isr_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_event_group_get_bits_from_isr_event_count = 0U;
    open_cfw_test_rtos_event_group_get_bits_from_isr_set_calls = 0U;
    open_cfw_test_rtos_event_group_get_bits_from_isr_read_calls = 0U;
    open_cfw_test_rtos_event_group_get_bits_from_isr_restore_calls = 0U;
    open_cfw_test_rtos_event_group_get_bits_from_isr_mask = 0U;
    open_cfw_test_rtos_event_group_get_bits_from_isr_bits = 0U;
    open_cfw_test_rtos_event_group_get_bits_from_isr_restored_mask = 0U;
    open_cfw_test_rtos_event_group_get_bits_from_isr_group = 0U;
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_rtos_event_group_get_bits_from_isr_events[index] =
            0U;
    }
}

void open_cfw_test_rtos_event_group_get_bits_from_isr_set_values(
    unsigned int mask,
    unsigned int bits
)
{
    open_cfw_test_rtos_event_group_get_bits_from_isr_mask = mask;
    open_cfw_test_rtos_event_group_get_bits_from_isr_bits = bits;
}

static unsigned int
open_cfw_test_rtos_event_group_get_bits_from_isr_set_mask(void)
{
    open_cfw_test_rtos_event_group_get_bits_from_isr_record(10U);
    ++open_cfw_test_rtos_event_group_get_bits_from_isr_set_calls;
    return open_cfw_test_rtos_event_group_get_bits_from_isr_mask;
}

static unsigned int
open_cfw_test_rtos_event_group_get_bits_from_isr_read_bits(void *group)
{
    open_cfw_test_rtos_event_group_get_bits_from_isr_record(20U);
    ++open_cfw_test_rtos_event_group_get_bits_from_isr_read_calls;
    open_cfw_test_rtos_event_group_get_bits_from_isr_group =
        (open_cfw_test_rtos_event_group_get_bits_from_isr_uintptr)group;
    return open_cfw_test_rtos_event_group_get_bits_from_isr_bits;
}

static void open_cfw_test_rtos_event_group_get_bits_from_isr_restore_mask(
    unsigned int mask
)
{
    open_cfw_test_rtos_event_group_get_bits_from_isr_record(30U);
    ++open_cfw_test_rtos_event_group_get_bits_from_isr_restore_calls;
    open_cfw_test_rtos_event_group_get_bits_from_isr_restored_mask = mask;
}

#define OPEN_CFW_RTOS_EVENT_GROUP_GET_BITS_FROM_ISR_SET_MASK() \
    open_cfw_test_rtos_event_group_get_bits_from_isr_set_mask()
#define OPEN_CFW_RTOS_EVENT_GROUP_GET_BITS_FROM_ISR_RESTORE_MASK(mask) \
    open_cfw_test_rtos_event_group_get_bits_from_isr_restore_mask(mask)
#define OPEN_CFW_RTOS_EVENT_GROUP_GET_BITS_FROM_ISR_READ_BITS(group) \
    open_cfw_test_rtos_event_group_get_bits_from_isr_read_bits(group)

#include "../../components/apollo_main/core_overlay/rtos_event_group_get_bits_from_isr.c"
