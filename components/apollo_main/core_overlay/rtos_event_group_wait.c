/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * RTOS event-group wait operation matched to stock entry 0x0047EBF8.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_event_group_wait_uintptr;

typedef void (*open_cfw_rtos_event_group_wait_void_function)(void);
typedef unsigned int (*open_cfw_rtos_event_group_wait_uint_function)(void);
typedef void (*open_cfw_rtos_event_group_wait_place_function)(
    void *list,
    unsigned int item_value,
    unsigned int ticks_to_wait
);

unsigned int open_cfw_rtos_event_group_test_wait_condition(
    unsigned int current_bits,
    unsigned int bits_to_wait_for,
    unsigned int wait_for_all
);

#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_CONTROL_MASK 0xFF000000U
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_CLEAR_ON_EXIT 0x01000000U
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_UNBLOCKED_BY_BITS 0x02000000U
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_FOR_ALL 0x04000000U

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_SCHEDULER_STATE
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_SCHEDULER_STATE() \
    (((open_cfw_rtos_event_group_wait_uint_function) \
        (open_cfw_rtos_event_group_wait_uintptr)0x004558A5U)())
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_SUSPEND_ALL
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_SUSPEND_ALL() \
    (((open_cfw_rtos_event_group_wait_void_function) \
        (open_cfw_rtos_event_group_wait_uintptr)0x00454D7DU)())
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_RESUME_ALL
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_RESUME_ALL() \
    (((open_cfw_rtos_event_group_wait_uint_function) \
        (open_cfw_rtos_event_group_wait_uintptr)0x00454DCDU)())
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_PLACE
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_PLACE(list, value, ticks) \
    (((open_cfw_rtos_event_group_wait_place_function) \
        (open_cfw_rtos_event_group_wait_uintptr)0x004552AFU)( \
            (list), \
            (value), \
            (ticks) \
        ))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_RESET_ITEM_VALUE
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_RESET_ITEM_VALUE() \
    (((open_cfw_rtos_event_group_wait_uint_function) \
        (open_cfw_rtos_event_group_wait_uintptr)0x00455ACBU)())
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_YIELD
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_YIELD() \
    (((open_cfw_rtos_event_group_wait_void_function) \
        (open_cfw_rtos_event_group_wait_uintptr)0x004420BDU)())
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_ENTER_CRITICAL
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_ENTER_CRITICAL() \
    (((open_cfw_rtos_event_group_wait_void_function) \
        (open_cfw_rtos_event_group_wait_uintptr)0x004420D1U)())
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_EXIT_CRITICAL
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_EXIT_CRITICAL() \
    (((open_cfw_rtos_event_group_wait_void_function) \
        (open_cfw_rtos_event_group_wait_uintptr)0x004420E9U)())
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_READ_BITS
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_READ_BITS(group) \
    (*(volatile unsigned int *)(group))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_WRITE_BITS
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_WRITE_BITS(group, value) \
    (*(volatile unsigned int *)(group) = (value))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_FAIL_STOP
#define OPEN_CFW_RTOS_EVENT_GROUP_WAIT_FAIL_STOP() \
    do { \
        ((open_cfw_rtos_event_group_wait_void_function) \
            (open_cfw_rtos_event_group_wait_uintptr)0x005FA0A5U)(); \
        *(volatile unsigned int *) \
            (open_cfw_rtos_event_group_wait_uintptr) \
            (~(open_cfw_rtos_event_group_wait_uintptr)0U) = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

__attribute__((used, noinline))
unsigned int open_cfw_rtos_event_group_wait(
    void *group,
    unsigned int bits_to_wait_for,
    unsigned int clear_on_exit,
    unsigned int wait_for_all,
    unsigned int ticks_to_wait
)
{
    unsigned int return_bits;
    unsigned int current_bits;

    if (
        group == (void *)0
        || (bits_to_wait_for
            & OPEN_CFW_RTOS_EVENT_GROUP_WAIT_CONTROL_MASK) != 0U
        || bits_to_wait_for == 0U
    ) {
        OPEN_CFW_RTOS_EVENT_GROUP_WAIT_FAIL_STOP();
        return 0U;
    }

    if (
        OPEN_CFW_RTOS_EVENT_GROUP_WAIT_SCHEDULER_STATE() == 0U
        && ticks_to_wait != 0U
    ) {
        OPEN_CFW_RTOS_EVENT_GROUP_WAIT_FAIL_STOP();
        return 0U;
    }

    OPEN_CFW_RTOS_EVENT_GROUP_WAIT_SUSPEND_ALL();
    current_bits = OPEN_CFW_RTOS_EVENT_GROUP_WAIT_READ_BITS(group);
    return_bits = current_bits;

    if (
        open_cfw_rtos_event_group_test_wait_condition(
            current_bits,
            bits_to_wait_for,
            wait_for_all
        ) != 0U
    ) {
        ticks_to_wait = 0U;
        if (clear_on_exit != 0U) {
            OPEN_CFW_RTOS_EVENT_GROUP_WAIT_WRITE_BITS(
                group,
                current_bits & ~bits_to_wait_for
            );
        }
    } else if (ticks_to_wait != 0U) {
        unsigned int control_bits = bits_to_wait_for;

        if (clear_on_exit != 0U) {
            control_bits |= OPEN_CFW_RTOS_EVENT_GROUP_WAIT_CLEAR_ON_EXIT;
        }
        if (wait_for_all != 0U) {
            control_bits |= OPEN_CFW_RTOS_EVENT_GROUP_WAIT_FOR_ALL;
        }
        OPEN_CFW_RTOS_EVENT_GROUP_WAIT_PLACE(
            (void *)((unsigned char *)group + 0x04U),
            control_bits,
            ticks_to_wait
        );
        return_bits = 0U;
    }

    current_bits = OPEN_CFW_RTOS_EVENT_GROUP_WAIT_RESUME_ALL();
    if (ticks_to_wait != 0U) {
        if (current_bits == 0U) {
            OPEN_CFW_RTOS_EVENT_GROUP_WAIT_YIELD();
        }

        return_bits =
            OPEN_CFW_RTOS_EVENT_GROUP_WAIT_RESET_ITEM_VALUE();
        if (
            (return_bits
                & OPEN_CFW_RTOS_EVENT_GROUP_WAIT_UNBLOCKED_BY_BITS) == 0U
        ) {
            OPEN_CFW_RTOS_EVENT_GROUP_WAIT_ENTER_CRITICAL();
            return_bits =
                OPEN_CFW_RTOS_EVENT_GROUP_WAIT_READ_BITS(group);
            if (
                open_cfw_rtos_event_group_test_wait_condition(
                    return_bits,
                    bits_to_wait_for,
                    wait_for_all
                ) != 0U
                && clear_on_exit != 0U
            ) {
                OPEN_CFW_RTOS_EVENT_GROUP_WAIT_WRITE_BITS(
                    group,
                    return_bits & ~bits_to_wait_for
                );
            }
            OPEN_CFW_RTOS_EVENT_GROUP_WAIT_EXIT_CRITICAL();
        }
        return_bits &=
            ~OPEN_CFW_RTOS_EVENT_GROUP_WAIT_CONTROL_MASK;
    }

    return return_bits;
}

#undef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_FAIL_STOP
#undef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_WRITE_BITS
#undef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_READ_BITS
#undef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_EXIT_CRITICAL
#undef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_ENTER_CRITICAL
#undef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_YIELD
#undef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_RESET_ITEM_VALUE
#undef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_PLACE
#undef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_RESUME_ALL
#undef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_SUSPEND_ALL
#undef OPEN_CFW_RTOS_EVENT_GROUP_WAIT_SCHEDULER_STATE
