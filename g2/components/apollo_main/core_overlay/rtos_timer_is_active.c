/*
 * SPDX-License-Identifier: MIT
 *
 * RTOS timer active-state query matched to stock entry 0x0047EAF6.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_is_active_uintptr;

typedef void (*open_cfw_rtos_timer_is_active_void_function)(void);

#ifndef OPEN_CFW_RTOS_TIMER_IS_ACTIVE_ENTER_CRITICAL
#define OPEN_CFW_RTOS_TIMER_IS_ACTIVE_ENTER_CRITICAL() \
    (((open_cfw_rtos_timer_is_active_void_function) \
        (open_cfw_rtos_timer_is_active_uintptr)0x004420D1U)())
#endif

#ifndef OPEN_CFW_RTOS_TIMER_IS_ACTIVE_EXIT_CRITICAL
#define OPEN_CFW_RTOS_TIMER_IS_ACTIVE_EXIT_CRITICAL() \
    (((open_cfw_rtos_timer_is_active_void_function) \
        (open_cfw_rtos_timer_is_active_uintptr)0x004420E9U)())
#endif

#ifndef OPEN_CFW_RTOS_TIMER_IS_ACTIVE_READ_STATUS
#define OPEN_CFW_RTOS_TIMER_IS_ACTIVE_READ_STATUS(timer) \
    (*(volatile const unsigned char *)( \
        (const volatile unsigned char *)(timer) + 0x28U))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_IS_ACTIVE_FAIL_STOP
#define OPEN_CFW_RTOS_TIMER_IS_ACTIVE_FAIL_STOP() \
    do { \
        ((open_cfw_rtos_timer_is_active_void_function) \
            (open_cfw_rtos_timer_is_active_uintptr)0x005FA0A5U)(); \
        *(volatile unsigned int *) \
            (open_cfw_rtos_timer_is_active_uintptr) \
            (~(open_cfw_rtos_timer_is_active_uintptr)0U) = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

__attribute__((used, noinline))
unsigned int open_cfw_rtos_timer_is_active(const void *timer)
{
    unsigned char status;
    unsigned int active;

    if (timer == (const void *)0) {
        OPEN_CFW_RTOS_TIMER_IS_ACTIVE_FAIL_STOP();
        return 0U;
    }

    OPEN_CFW_RTOS_TIMER_IS_ACTIVE_ENTER_CRITICAL();
    status = OPEN_CFW_RTOS_TIMER_IS_ACTIVE_READ_STATUS(timer);
    active = (status & 0x01U) != 0U;
    OPEN_CFW_RTOS_TIMER_IS_ACTIVE_EXIT_CRITICAL();
    return active;
}

#undef OPEN_CFW_RTOS_TIMER_IS_ACTIVE_FAIL_STOP
#undef OPEN_CFW_RTOS_TIMER_IS_ACTIVE_READ_STATUS
#undef OPEN_CFW_RTOS_TIMER_IS_ACTIVE_EXIT_CRITICAL
#undef OPEN_CFW_RTOS_TIMER_IS_ACTIVE_ENTER_CRITICAL
