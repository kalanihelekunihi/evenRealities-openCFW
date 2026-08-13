/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Dynamic RTOS timer-object creation matched to stock entry 0x0047E6DC.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_dynamic_uintptr;

typedef void *(*open_cfw_rtos_timer_dynamic_allocate_function)(
    unsigned int
);
typedef void (*open_cfw_rtos_timer_dynamic_initialize_function)(
    const void *,
    unsigned int,
    unsigned int,
    const void *,
    const void *,
    void *
);

#ifndef OPEN_CFW_RTOS_TIMER_DYNAMIC_ALLOCATE
#define OPEN_CFW_RTOS_TIMER_DYNAMIC_ALLOCATE(size) \
    (((open_cfw_rtos_timer_dynamic_allocate_function) \
        (open_cfw_rtos_timer_dynamic_uintptr)0x00456111U)(size))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_DYNAMIC_INITIALIZE
#define OPEN_CFW_RTOS_TIMER_DYNAMIC_INITIALIZE(...) \
    (((open_cfw_rtos_timer_dynamic_initialize_function) \
        (open_cfw_rtos_timer_dynamic_uintptr)0x0047E75BU)(__VA_ARGS__))
#endif

__attribute__((used, noinline))
void *open_cfw_rtos_timer_dynamic_create(
    const void *name,
    unsigned int period_ticks,
    unsigned int periodic,
    const void *callback_context,
    const void *callback
)
{
    void *object = OPEN_CFW_RTOS_TIMER_DYNAMIC_ALLOCATE(0x2CU);

    if (object != (void *)0) {
        ((volatile unsigned char *)object)[0x28U] = 0U;
        OPEN_CFW_RTOS_TIMER_DYNAMIC_INITIALIZE(
            name,
            period_ticks,
            periodic,
            callback_context,
            callback,
            object
        );
    }
    return object;
}

#undef OPEN_CFW_RTOS_TIMER_DYNAMIC_INITIALIZE
#undef OPEN_CFW_RTOS_TIMER_DYNAMIC_ALLOCATE
