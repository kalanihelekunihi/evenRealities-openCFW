/*
 * SPDX-License-Identifier: MIT
 *
 * RTOS active-timer-list query matched to stock entry 0x0047E8F2.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_query_uintptr;

#ifndef OPEN_CFW_RTOS_TIMER_QUERY_ITEM_COUNT
#define OPEN_CFW_RTOS_TIMER_QUERY_ITEM_COUNT() \
    (*(volatile unsigned int *)(open_cfw_rtos_timer_query_uintptr)( \
        *(volatile unsigned int *)(open_cfw_rtos_timer_query_uintptr) \
            0x20074AA8U))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_QUERY_HEAD_EXPIRY
#define OPEN_CFW_RTOS_TIMER_QUERY_HEAD_EXPIRY() \
    (*(volatile unsigned int *)(open_cfw_rtos_timer_query_uintptr)( \
        *(volatile unsigned int *)(open_cfw_rtos_timer_query_uintptr)( \
            (open_cfw_rtos_timer_query_uintptr)( \
                *(volatile unsigned int *)( \
                    open_cfw_rtos_timer_query_uintptr)0x20074AA8U) \
            + 12U)))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_rtos_timer_query(unsigned int *active_list_empty)
{
    volatile unsigned int *empty = active_list_empty;

    *empty = (OPEN_CFW_RTOS_TIMER_QUERY_ITEM_COUNT() == 0U);
    if (*empty != 0U) {
        return 0U;
    }
    return OPEN_CFW_RTOS_TIMER_QUERY_HEAD_EXPIRY();
}

#undef OPEN_CFW_RTOS_TIMER_QUERY_HEAD_EXPIRY
#undef OPEN_CFW_RTOS_TIMER_QUERY_ITEM_COUNT
