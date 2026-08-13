/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Shared RTOS timer-object initialization matched to stock entry 0x0047E75A.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_initialize_uintptr;

typedef void (*open_cfw_rtos_timer_initialize_lock_function)(void);

void open_cfw_rtos_timer_runtime_initialize(void);

#ifndef OPEN_CFW_RTOS_TIMER_INITIALIZE_RUNTIME
#define OPEN_CFW_RTOS_TIMER_INITIALIZE_RUNTIME() \
    open_cfw_rtos_timer_runtime_initialize()
#endif

#ifndef OPEN_CFW_RTOS_TIMER_INITIALIZE_STORE_U32
#define OPEN_CFW_RTOS_TIMER_INITIALIZE_STORE_U32(object, offset, value) \
    (*(volatile unsigned int *)( \
        (volatile unsigned char *)(object) + (offset)) = \
            (unsigned int)(value))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_INITIALIZE_OR_U8
#define OPEN_CFW_RTOS_TIMER_INITIALIZE_OR_U8(object, offset, mask) \
    (*(volatile unsigned char *)( \
        (volatile unsigned char *)(object) + (offset)) |= \
            (unsigned char)(mask))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_INITIALIZE_FAIL_STOP
#define OPEN_CFW_RTOS_TIMER_INITIALIZE_FAIL_STOP() \
    do { \
        ((open_cfw_rtos_timer_initialize_lock_function) \
            (open_cfw_rtos_timer_initialize_uintptr)0x005FA0A5U)(); \
        *(volatile unsigned int *) \
            (open_cfw_rtos_timer_initialize_uintptr) \
            (~(open_cfw_rtos_timer_initialize_uintptr)0U) = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

__attribute__((used, noinline))
void open_cfw_rtos_timer_initialize(
    const void *name,
    unsigned int period_ticks,
    unsigned int periodic,
    const void *callback_context,
    const void *callback,
    void *object
)
{
    if (period_ticks == 0U) {
        OPEN_CFW_RTOS_TIMER_INITIALIZE_FAIL_STOP();
        return;
    }

    OPEN_CFW_RTOS_TIMER_INITIALIZE_RUNTIME();
    OPEN_CFW_RTOS_TIMER_INITIALIZE_STORE_U32(
        object,
        0x00U,
        (unsigned int)(open_cfw_rtos_timer_initialize_uintptr)name
    );
    OPEN_CFW_RTOS_TIMER_INITIALIZE_STORE_U32(
        object,
        0x18U,
        period_ticks
    );
    OPEN_CFW_RTOS_TIMER_INITIALIZE_STORE_U32(
        object,
        0x1CU,
        (unsigned int)(open_cfw_rtos_timer_initialize_uintptr)callback_context
    );
    OPEN_CFW_RTOS_TIMER_INITIALIZE_STORE_U32(
        object,
        0x20U,
        (unsigned int)(open_cfw_rtos_timer_initialize_uintptr)callback
    );
    OPEN_CFW_RTOS_TIMER_INITIALIZE_STORE_U32(object, 0x14U, 0U);
    if (periodic != 0U) {
        OPEN_CFW_RTOS_TIMER_INITIALIZE_OR_U8(object, 0x28U, 0x04U);
    }
}

#undef OPEN_CFW_RTOS_TIMER_INITIALIZE_FAIL_STOP
#undef OPEN_CFW_RTOS_TIMER_INITIALIZE_OR_U8
#undef OPEN_CFW_RTOS_TIMER_INITIALIZE_STORE_U32
#undef OPEN_CFW_RTOS_TIMER_INITIALIZE_RUNTIME
