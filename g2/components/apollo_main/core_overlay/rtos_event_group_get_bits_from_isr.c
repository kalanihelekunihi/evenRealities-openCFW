/*
 * SPDX-License-Identifier: MIT
 *
 * RTOS event-group bit-snapshot getter matched to stock entry 0x0047ED64.
 */

typedef __UINTPTR_TYPE__
    open_cfw_rtos_event_group_get_bits_from_isr_uintptr;

typedef unsigned int
    (*open_cfw_rtos_event_group_get_bits_from_isr_set_mask_function)(void);
typedef void
    (*open_cfw_rtos_event_group_get_bits_from_isr_restore_mask_function)(
        unsigned int mask
    );

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_GET_BITS_FROM_ISR_SET_MASK
#define OPEN_CFW_RTOS_EVENT_GROUP_GET_BITS_FROM_ISR_SET_MASK() \
    (((open_cfw_rtos_event_group_get_bits_from_isr_set_mask_function) \
        (open_cfw_rtos_event_group_get_bits_from_isr_uintptr) \
        0x005FA0A5U)())
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_GET_BITS_FROM_ISR_RESTORE_MASK
#define OPEN_CFW_RTOS_EVENT_GROUP_GET_BITS_FROM_ISR_RESTORE_MASK(mask) \
    (((open_cfw_rtos_event_group_get_bits_from_isr_restore_mask_function) \
        (open_cfw_rtos_event_group_get_bits_from_isr_uintptr) \
        0x005FA0BBU)((mask)))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_GET_BITS_FROM_ISR_READ_BITS
#define OPEN_CFW_RTOS_EVENT_GROUP_GET_BITS_FROM_ISR_READ_BITS(group) \
    (*(volatile unsigned int *)(group))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_rtos_event_group_get_bits_from_isr(void *group)
{
    unsigned int mask;
    unsigned int bits;

    mask = OPEN_CFW_RTOS_EVENT_GROUP_GET_BITS_FROM_ISR_SET_MASK();
    bits = OPEN_CFW_RTOS_EVENT_GROUP_GET_BITS_FROM_ISR_READ_BITS(group);
    OPEN_CFW_RTOS_EVENT_GROUP_GET_BITS_FROM_ISR_RESTORE_MASK(mask);
    return bits;
}

#undef OPEN_CFW_RTOS_EVENT_GROUP_GET_BITS_FROM_ISR_READ_BITS
#undef OPEN_CFW_RTOS_EVENT_GROUP_GET_BITS_FROM_ISR_RESTORE_MASK
#undef OPEN_CFW_RTOS_EVENT_GROUP_GET_BITS_FROM_ISR_SET_MASK
