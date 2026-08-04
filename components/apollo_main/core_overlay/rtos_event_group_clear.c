/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * RTOS event-group clear operation matched to stock entry 0x0047ED10.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_event_group_clear_uintptr;

typedef void (*open_cfw_rtos_event_group_clear_void_function)(void);

#define OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_CONTROL_MASK 0xFF000000U

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_ENTER_CRITICAL
#define OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_ENTER_CRITICAL() \
    (((open_cfw_rtos_event_group_clear_void_function) \
        (open_cfw_rtos_event_group_clear_uintptr)0x004420D1U)())
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_EXIT_CRITICAL
#define OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_EXIT_CRITICAL() \
    (((open_cfw_rtos_event_group_clear_void_function) \
        (open_cfw_rtos_event_group_clear_uintptr)0x004420E9U)())
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_READ_BITS
#define OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_READ_BITS(group) \
    (*(volatile unsigned int *)(group))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_WRITE_BITS
#define OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_WRITE_BITS(group, value) \
    (*(volatile unsigned int *)(group) = (value))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_FAIL_STOP
#define OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_FAIL_STOP() \
    do { \
        ((open_cfw_rtos_event_group_clear_void_function) \
            (open_cfw_rtos_event_group_clear_uintptr)0x005FA0A5U)(); \
        *(volatile unsigned int *) \
            (open_cfw_rtos_event_group_clear_uintptr) \
            (~(open_cfw_rtos_event_group_clear_uintptr)0U) = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

__attribute__((used, noinline))
unsigned int open_cfw_rtos_event_group_clear(
    void *group,
    unsigned int bits_to_clear
)
{
    unsigned int return_bits;
    unsigned int current_bits;

    if (
        group == (void *)0
        || (
            bits_to_clear
            & OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_CONTROL_MASK
        ) != 0U
    ) {
        OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_FAIL_STOP();
        return 0U;
    }

    OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_ENTER_CRITICAL();
    return_bits = OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_READ_BITS(group);
    current_bits = OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_READ_BITS(group);
    OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_WRITE_BITS(
        group,
        current_bits & ~bits_to_clear
    );
    OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_EXIT_CRITICAL();

    return return_bits;
}

#undef OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_FAIL_STOP
#undef OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_WRITE_BITS
#undef OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_READ_BITS
#undef OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_EXIT_CRITICAL
#undef OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_ENTER_CRITICAL
