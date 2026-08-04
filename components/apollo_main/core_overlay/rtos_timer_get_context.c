/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * RTOS timer callback-context getter matched to stock entry 0x0047EB26.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_get_context_uintptr;

typedef void (*open_cfw_rtos_timer_get_context_void_function)(void);

#ifndef OPEN_CFW_RTOS_TIMER_GET_CONTEXT_ENTER_CRITICAL
#define OPEN_CFW_RTOS_TIMER_GET_CONTEXT_ENTER_CRITICAL() \
    (((open_cfw_rtos_timer_get_context_void_function) \
        (open_cfw_rtos_timer_get_context_uintptr)0x004420D1U)())
#endif

#ifndef OPEN_CFW_RTOS_TIMER_GET_CONTEXT_EXIT_CRITICAL
#define OPEN_CFW_RTOS_TIMER_GET_CONTEXT_EXIT_CRITICAL() \
    (((open_cfw_rtos_timer_get_context_void_function) \
        (open_cfw_rtos_timer_get_context_uintptr)0x004420E9U)())
#endif

#ifndef OPEN_CFW_RTOS_TIMER_GET_CONTEXT_READ_CONTEXT
#define OPEN_CFW_RTOS_TIMER_GET_CONTEXT_READ_CONTEXT(timer) \
    (*(void *volatile const *)( \
        (const volatile unsigned char *)(timer) + 0x1CU))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_GET_CONTEXT_FAIL_STOP
#define OPEN_CFW_RTOS_TIMER_GET_CONTEXT_FAIL_STOP() \
    do { \
        ((open_cfw_rtos_timer_get_context_void_function) \
            (open_cfw_rtos_timer_get_context_uintptr)0x005FA0A5U)(); \
        *(volatile unsigned int *) \
            (open_cfw_rtos_timer_get_context_uintptr) \
            (~(open_cfw_rtos_timer_get_context_uintptr)0U) = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

__attribute__((used, noinline))
void *open_cfw_rtos_timer_get_context(const void *timer)
{
    void *context;

    if (timer == (const void *)0) {
        OPEN_CFW_RTOS_TIMER_GET_CONTEXT_FAIL_STOP();
        return (void *)0;
    }

    OPEN_CFW_RTOS_TIMER_GET_CONTEXT_ENTER_CRITICAL();
    context = OPEN_CFW_RTOS_TIMER_GET_CONTEXT_READ_CONTEXT(timer);
    OPEN_CFW_RTOS_TIMER_GET_CONTEXT_EXIT_CRITICAL();
    return context;
}

#undef OPEN_CFW_RTOS_TIMER_GET_CONTEXT_FAIL_STOP
#undef OPEN_CFW_RTOS_TIMER_GET_CONTEXT_READ_CONTEXT
#undef OPEN_CFW_RTOS_TIMER_GET_CONTEXT_EXIT_CRITICAL
#undef OPEN_CFW_RTOS_TIMER_GET_CONTEXT_ENTER_CRITICAL
