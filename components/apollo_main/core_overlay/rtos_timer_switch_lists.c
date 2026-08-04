/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * RTOS timer-list overflow switch matched to stock entry 0x0047EA90.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_switch_lists_uintptr;

void open_cfw_rtos_timer_expire(unsigned int, unsigned int);

#ifndef OPEN_CFW_RTOS_TIMER_SWITCH_READ_CURRENT
#define OPEN_CFW_RTOS_TIMER_SWITCH_READ_CURRENT() \
    ((void *)(open_cfw_rtos_timer_switch_lists_uintptr)( \
        *(volatile unsigned int *)( \
            open_cfw_rtos_timer_switch_lists_uintptr)0x20074AA8U))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_SWITCH_READ_OVERFLOW
#define OPEN_CFW_RTOS_TIMER_SWITCH_READ_OVERFLOW() \
    ((void *)(open_cfw_rtos_timer_switch_lists_uintptr)( \
        *(volatile unsigned int *)( \
            open_cfw_rtos_timer_switch_lists_uintptr)0x20074AACU))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_SWITCH_WRITE_CURRENT
#define OPEN_CFW_RTOS_TIMER_SWITCH_WRITE_CURRENT(value) \
    (*(volatile unsigned int *)( \
        open_cfw_rtos_timer_switch_lists_uintptr)0x20074AA8U = \
            (unsigned int)(open_cfw_rtos_timer_switch_lists_uintptr)(value))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_SWITCH_WRITE_OVERFLOW
#define OPEN_CFW_RTOS_TIMER_SWITCH_WRITE_OVERFLOW(value) \
    (*(volatile unsigned int *)( \
        open_cfw_rtos_timer_switch_lists_uintptr)0x20074AACU = \
            (unsigned int)(open_cfw_rtos_timer_switch_lists_uintptr)(value))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_SWITCH_ITEM_COUNT
#define OPEN_CFW_RTOS_TIMER_SWITCH_ITEM_COUNT(list) \
    (*(volatile unsigned int *)(list))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_SWITCH_HEAD_EXPIRY
#define OPEN_CFW_RTOS_TIMER_SWITCH_HEAD_EXPIRY(list) \
    (*(volatile unsigned int *)( \
        *(volatile unsigned int *)( \
            (volatile unsigned char *)(list) + 0x0CU)))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_SWITCH_PROCESS_EXPIRED
#define OPEN_CFW_RTOS_TIMER_SWITCH_PROCESS_EXPIRED(expiry, time_now) \
    open_cfw_rtos_timer_expire(expiry, time_now)
#endif

__attribute__((used, noinline))
void open_cfw_rtos_timer_switch_lists(void)
{
    void *current_list;
    void *overflow_list;

    for (;;) {
        current_list = OPEN_CFW_RTOS_TIMER_SWITCH_READ_CURRENT();
        if (
            OPEN_CFW_RTOS_TIMER_SWITCH_ITEM_COUNT(current_list)
            == 0U
        ) {
            break;
        }

        current_list = OPEN_CFW_RTOS_TIMER_SWITCH_READ_CURRENT();
        OPEN_CFW_RTOS_TIMER_SWITCH_PROCESS_EXPIRED(
            OPEN_CFW_RTOS_TIMER_SWITCH_HEAD_EXPIRY(current_list),
            0xFFFFFFFFU
        );
    }

    current_list = OPEN_CFW_RTOS_TIMER_SWITCH_READ_CURRENT();
    overflow_list = OPEN_CFW_RTOS_TIMER_SWITCH_READ_OVERFLOW();
    OPEN_CFW_RTOS_TIMER_SWITCH_WRITE_CURRENT(overflow_list);
    OPEN_CFW_RTOS_TIMER_SWITCH_WRITE_OVERFLOW(current_list);
}

#undef OPEN_CFW_RTOS_TIMER_SWITCH_PROCESS_EXPIRED
#undef OPEN_CFW_RTOS_TIMER_SWITCH_HEAD_EXPIRY
#undef OPEN_CFW_RTOS_TIMER_SWITCH_ITEM_COUNT
#undef OPEN_CFW_RTOS_TIMER_SWITCH_WRITE_OVERFLOW
#undef OPEN_CFW_RTOS_TIMER_SWITCH_WRITE_CURRENT
#undef OPEN_CFW_RTOS_TIMER_SWITCH_READ_OVERFLOW
#undef OPEN_CFW_RTOS_TIMER_SWITCH_READ_CURRENT
