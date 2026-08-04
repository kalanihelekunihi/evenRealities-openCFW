/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * RTOS timer-list insertion helper matched to stock entry 0x0047E93C.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_insert_uintptr;

typedef void (*open_cfw_rtos_timer_insert_list_function)(void *, void *);

#ifndef OPEN_CFW_RTOS_TIMER_INSERT_WRITE_EXPIRY
#define OPEN_CFW_RTOS_TIMER_INSERT_WRITE_EXPIRY(timer, value) \
    (*(volatile unsigned int *)( \
        (volatile unsigned char *)(timer) + 0x04U) = (value))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_INSERT_WRITE_OWNER
#define OPEN_CFW_RTOS_TIMER_INSERT_WRITE_OWNER(timer) \
    (*(volatile unsigned int *)( \
        (volatile unsigned char *)(timer) + 0x10U) = \
            (unsigned int)(open_cfw_rtos_timer_insert_uintptr)(timer))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_INSERT_PERIOD
#define OPEN_CFW_RTOS_TIMER_INSERT_PERIOD(timer) \
    (*(volatile unsigned int *)( \
        (volatile unsigned char *)(timer) + 0x18U))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_INSERT_ACTIVE_LIST
#define OPEN_CFW_RTOS_TIMER_INSERT_ACTIVE_LIST() \
    ((void *)(open_cfw_rtos_timer_insert_uintptr)( \
        *(volatile unsigned int *)( \
            open_cfw_rtos_timer_insert_uintptr)0x20074AA8U))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_INSERT_OVERFLOW_LIST
#define OPEN_CFW_RTOS_TIMER_INSERT_OVERFLOW_LIST() \
    ((void *)(open_cfw_rtos_timer_insert_uintptr)( \
        *(volatile unsigned int *)( \
            open_cfw_rtos_timer_insert_uintptr)0x20074AACU))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_INSERT_LIST_ITEM
#define OPEN_CFW_RTOS_TIMER_INSERT_LIST_ITEM(timer) \
    ((void *)((unsigned char *)(timer) + 0x04U))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_INSERT_LIST
#define OPEN_CFW_RTOS_TIMER_INSERT_LIST(list, item) \
    (((open_cfw_rtos_timer_insert_list_function) \
        (open_cfw_rtos_timer_insert_uintptr)0x004560B3U)(list, item))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_rtos_timer_insert(
    void *timer,
    unsigned int next_expiry,
    unsigned int time_now,
    unsigned int previous_expiry
)
{
    OPEN_CFW_RTOS_TIMER_INSERT_WRITE_EXPIRY(timer, next_expiry);
    OPEN_CFW_RTOS_TIMER_INSERT_WRITE_OWNER(timer);

    if (time_now < next_expiry) {
        if (
            time_now < previous_expiry
            && previous_expiry <= next_expiry
        ) {
            return 1U;
        }
        OPEN_CFW_RTOS_TIMER_INSERT_LIST(
            OPEN_CFW_RTOS_TIMER_INSERT_ACTIVE_LIST(),
            OPEN_CFW_RTOS_TIMER_INSERT_LIST_ITEM(timer)
        );
        return 0U;
    }

    if (
        time_now - previous_expiry
        < OPEN_CFW_RTOS_TIMER_INSERT_PERIOD(timer)
    ) {
        OPEN_CFW_RTOS_TIMER_INSERT_LIST(
            OPEN_CFW_RTOS_TIMER_INSERT_OVERFLOW_LIST(),
            OPEN_CFW_RTOS_TIMER_INSERT_LIST_ITEM(timer)
        );
        return 0U;
    }
    return 1U;
}

#undef OPEN_CFW_RTOS_TIMER_INSERT_LIST
#undef OPEN_CFW_RTOS_TIMER_INSERT_LIST_ITEM
#undef OPEN_CFW_RTOS_TIMER_INSERT_OVERFLOW_LIST
#undef OPEN_CFW_RTOS_TIMER_INSERT_ACTIVE_LIST
#undef OPEN_CFW_RTOS_TIMER_INSERT_PERIOD
#undef OPEN_CFW_RTOS_TIMER_INSERT_WRITE_OWNER
#undef OPEN_CFW_RTOS_TIMER_INSERT_WRITE_EXPIRY
