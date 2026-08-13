/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * RTOS event-group set-bits operation matched to stock entry 0x0047ED76.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_event_group_set_uintptr;

typedef void (*open_cfw_rtos_event_group_set_void_function)(void);
typedef unsigned int
    (*open_cfw_rtos_event_group_set_uint_function)(void);
typedef unsigned int
    (*open_cfw_rtos_event_group_set_remove_function)(
        void *item,
        unsigned int value
    );

#define OPEN_CFW_RTOS_EVENT_GROUP_SET_CONTROL_MASK 0xFF000000U
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_CLEAR_ON_EXIT 0x01000000U
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_UNBLOCKED_BY_BITS 0x02000000U
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_WAIT_FOR_ALL 0x04000000U

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_SET_SUSPEND_ALL
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_SUSPEND_ALL() \
    (((open_cfw_rtos_event_group_set_void_function) \
        (open_cfw_rtos_event_group_set_uintptr)0x00454D7DU)())
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_SET_RESUME_ALL
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_RESUME_ALL() \
    (((open_cfw_rtos_event_group_set_uint_function) \
        (open_cfw_rtos_event_group_set_uintptr)0x00454DCDU)())
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_SET_REMOVE
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_REMOVE(item, value) \
    (((open_cfw_rtos_event_group_set_remove_function) \
        (open_cfw_rtos_event_group_set_uintptr)0x0045547DU)( \
            (item), \
            (value) \
        ))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_SET_READ_BITS
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_READ_BITS(group) \
    (*(volatile unsigned int *)(group))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_SET_WRITE_BITS
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_WRITE_BITS(group, value) \
    (*(volatile unsigned int *)(group) = (value))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_SET_LIST_END
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_LIST_END(group) \
    ((void *)((unsigned char *)(group) + 0x0CU))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_SET_LIST_HEAD
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_LIST_HEAD(group) \
    (*(void **)((unsigned char *)(group) + 0x10U))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_SET_ITEM_NEXT
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_ITEM_NEXT(item) \
    (*(void **)((unsigned char *)(item) + 0x04U))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_SET_ITEM_VALUE
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_ITEM_VALUE(item) \
    (*(unsigned int *)(item))
#endif

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_SET_FAIL_STOP
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_FAIL_STOP() \
    do { \
        ((open_cfw_rtos_event_group_set_void_function) \
            (open_cfw_rtos_event_group_set_uintptr)0x005FA0A5U)(); \
        *(volatile unsigned int *) \
            (open_cfw_rtos_event_group_set_uintptr) \
            (~(open_cfw_rtos_event_group_set_uintptr)0U) = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

__attribute__((used, noinline))
unsigned int open_cfw_rtos_event_group_set(
    void *group,
    unsigned int bits_to_set
)
{
    void *item;
    void *next;
    void *list_end;
    unsigned int bits_to_clear = 0U;

    if (
        group == (void *)0
        || (bits_to_set
            & OPEN_CFW_RTOS_EVENT_GROUP_SET_CONTROL_MASK) != 0U
    ) {
        OPEN_CFW_RTOS_EVENT_GROUP_SET_FAIL_STOP();
        return 0U;
    }

    list_end = OPEN_CFW_RTOS_EVENT_GROUP_SET_LIST_END(group);
    OPEN_CFW_RTOS_EVENT_GROUP_SET_SUSPEND_ALL();
    OPEN_CFW_RTOS_EVENT_GROUP_SET_WRITE_BITS(
        group,
        OPEN_CFW_RTOS_EVENT_GROUP_SET_READ_BITS(group) | bits_to_set
    );

    item = OPEN_CFW_RTOS_EVENT_GROUP_SET_LIST_HEAD(group);
    while (item != list_end) {
        unsigned int item_value;
        unsigned int control_bits;
        unsigned int waited_bits;
        unsigned int match;

        next = OPEN_CFW_RTOS_EVENT_GROUP_SET_ITEM_NEXT(item);
        item_value = OPEN_CFW_RTOS_EVENT_GROUP_SET_ITEM_VALUE(item);
        control_bits =
            item_value & OPEN_CFW_RTOS_EVENT_GROUP_SET_CONTROL_MASK;
        waited_bits =
            item_value & ~OPEN_CFW_RTOS_EVENT_GROUP_SET_CONTROL_MASK;

        if (
            (control_bits
                & OPEN_CFW_RTOS_EVENT_GROUP_SET_WAIT_FOR_ALL) == 0U
        ) {
            match =
                (
                    OPEN_CFW_RTOS_EVENT_GROUP_SET_READ_BITS(group)
                    & waited_bits
                ) != 0U;
        } else {
            match =
                (
                    OPEN_CFW_RTOS_EVENT_GROUP_SET_READ_BITS(group)
                    & waited_bits
                ) == waited_bits;
        }

        if (match != 0U) {
            if (
                (control_bits
                    & OPEN_CFW_RTOS_EVENT_GROUP_SET_CLEAR_ON_EXIT) != 0U
            ) {
                bits_to_clear |= waited_bits;
            }
            (void)OPEN_CFW_RTOS_EVENT_GROUP_SET_REMOVE(
                item,
                OPEN_CFW_RTOS_EVENT_GROUP_SET_READ_BITS(group)
                    | OPEN_CFW_RTOS_EVENT_GROUP_SET_UNBLOCKED_BY_BITS
            );
        }

        item = next;
    }

    OPEN_CFW_RTOS_EVENT_GROUP_SET_WRITE_BITS(
        group,
        OPEN_CFW_RTOS_EVENT_GROUP_SET_READ_BITS(group) & ~bits_to_clear
    );
    (void)OPEN_CFW_RTOS_EVENT_GROUP_SET_RESUME_ALL();
    return OPEN_CFW_RTOS_EVENT_GROUP_SET_READ_BITS(group);
}

#undef OPEN_CFW_RTOS_EVENT_GROUP_SET_FAIL_STOP
#undef OPEN_CFW_RTOS_EVENT_GROUP_SET_ITEM_VALUE
#undef OPEN_CFW_RTOS_EVENT_GROUP_SET_ITEM_NEXT
#undef OPEN_CFW_RTOS_EVENT_GROUP_SET_LIST_HEAD
#undef OPEN_CFW_RTOS_EVENT_GROUP_SET_LIST_END
#undef OPEN_CFW_RTOS_EVENT_GROUP_SET_WRITE_BITS
#undef OPEN_CFW_RTOS_EVENT_GROUP_SET_READ_BITS
#undef OPEN_CFW_RTOS_EVENT_GROUP_SET_REMOVE
#undef OPEN_CFW_RTOS_EVENT_GROUP_SET_RESUME_ALL
#undef OPEN_CFW_RTOS_EVENT_GROUP_SET_SUSPEND_ALL
