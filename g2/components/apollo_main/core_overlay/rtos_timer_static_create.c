/*
 * SPDX-License-Identifier: MIT
 *
 * Static-control-block RTOS timer creation matched to stock entry
 * 0x0047E712.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_static_uintptr;

typedef void (*open_cfw_rtos_timer_static_initialize_function)(
    const void *,
    unsigned int,
    unsigned int,
    const void *,
    const void *,
    void *
);
typedef void (*open_cfw_rtos_timer_static_lock_function)(void);

#ifndef OPEN_CFW_RTOS_TIMER_STATIC_OBJECT_SIZE
#define OPEN_CFW_RTOS_TIMER_STATIC_OBJECT_SIZE() 0x2CU
#endif

#ifndef OPEN_CFW_RTOS_TIMER_STATIC_INITIALIZE
#define OPEN_CFW_RTOS_TIMER_STATIC_INITIALIZE(...) \
    (((open_cfw_rtos_timer_static_initialize_function) \
        (open_cfw_rtos_timer_static_uintptr)0x0047E75BU)(__VA_ARGS__))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_STATIC_FAIL_STOP
#define OPEN_CFW_RTOS_TIMER_STATIC_FAIL_STOP() \
    do { \
        ((open_cfw_rtos_timer_static_lock_function) \
            (open_cfw_rtos_timer_static_uintptr)0x005FA0A5U)(); \
        *(volatile unsigned int *) \
            (open_cfw_rtos_timer_static_uintptr) \
            (~(open_cfw_rtos_timer_static_uintptr)0U) = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

__attribute__((used, noinline))
void *open_cfw_rtos_timer_static_create(
    const void *name,
    unsigned int period_ticks,
    unsigned int periodic,
    const void *callback_context,
    const void *callback,
    void *object
)
{
    if (OPEN_CFW_RTOS_TIMER_STATIC_OBJECT_SIZE() != 0x2CU) {
        OPEN_CFW_RTOS_TIMER_STATIC_FAIL_STOP();
        return (void *)0;
    }
    if (object == (void *)0) {
        OPEN_CFW_RTOS_TIMER_STATIC_FAIL_STOP();
        return (void *)0;
    }

    ((volatile unsigned char *)object)[0x28U] = 2U;
    OPEN_CFW_RTOS_TIMER_STATIC_INITIALIZE(
        name,
        period_ticks,
        periodic,
        callback_context,
        callback,
        object
    );
    return object;
}

#undef OPEN_CFW_RTOS_TIMER_STATIC_FAIL_STOP
#undef OPEN_CFW_RTOS_TIMER_STATIC_INITIALIZE
#undef OPEN_CFW_RTOS_TIMER_STATIC_OBJECT_SIZE
