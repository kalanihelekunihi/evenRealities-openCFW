/*
 * SPDX-License-Identifier: MIT
 *
 * EasyLogger tracepoint timer bootstrap matched to stock entry 0x0047E232.
 */

typedef __UINTPTR_TYPE__ open_cfw_tracepoint_bootstrap_uintptr;

typedef void (*open_cfw_tracepoint_bootstrap_callback)(void *);
typedef void *(*open_cfw_tracepoint_bootstrap_timer_create_function)(
    const char *,
    unsigned int,
    unsigned int,
    unsigned int,
    open_cfw_tracepoint_bootstrap_callback,
    void *
);
typedef void (*open_cfw_tracepoint_bootstrap_action_function)(void);

extern void open_cfw_tracepoint_defer_timer_callback(void *);
extern void open_cfw_tracepoint_defer_begin(void);

#ifndef OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_CREATE
#define OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_CREATE( \
    name, period, auto_reload, identifier, callback, storage \
) \
    (((open_cfw_tracepoint_bootstrap_timer_create_function) \
        (open_cfw_tracepoint_bootstrap_uintptr)0x0047E713U)( \
            (name), \
            (period), \
            (auto_reload), \
            (identifier), \
            (callback), \
            (storage) \
        ))
#endif

#ifndef OPEN_CFW_TRACEPOINT_BOOTSTRAP_RETAINED_SETUP
#define OPEN_CFW_TRACEPOINT_BOOTSTRAP_RETAINED_SETUP() \
    (((open_cfw_tracepoint_bootstrap_action_function) \
        (open_cfw_tracepoint_bootstrap_uintptr)0x0048EAC9U)())
#endif

#ifndef OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_HANDLE
#define OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_HANDLE \
    (*(void * volatile *) \
        (open_cfw_tracepoint_bootstrap_uintptr)0x20074ACCU)
#endif

#ifndef OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_STORAGE
#define OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_STORAGE \
    ((void *)(open_cfw_tracepoint_bootstrap_uintptr)0x20073758U)
#endif

#ifndef OPEN_CFW_TRACEPOINT_BOOTSTRAP_FAIL_STOP
#define OPEN_CFW_TRACEPOINT_BOOTSTRAP_FAIL_STOP() \
    do { \
        ((open_cfw_tracepoint_bootstrap_action_function) \
            (open_cfw_tracepoint_bootstrap_uintptr)0x005FA0A5U)(); \
        *(volatile unsigned int *) \
            (open_cfw_tracepoint_bootstrap_uintptr)-1 = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

#ifndef OPEN_CFW_TRACEPOINT_BOOTSTRAP_DEFER_CALLBACK
#define OPEN_CFW_TRACEPOINT_BOOTSTRAP_DEFER_CALLBACK \
    open_cfw_tracepoint_defer_timer_callback
#endif

#ifndef OPEN_CFW_TRACEPOINT_BOOTSTRAP_DEFER_BEGIN
#define OPEN_CFW_TRACEPOINT_BOOTSTRAP_DEFER_BEGIN() \
    open_cfw_tracepoint_defer_begin()
#endif

#define OPEN_CFW_TRACEPOINT_BOOTSTRAP_PERIOD_TICKS 2000U

static const char open_cfw_tracepoint_bootstrap_timer_name[] =
    "tracepoint_defer";

__attribute__((used, noinline))
void open_cfw_tracepoint_runtime_initialize(void)
{
    if (OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_HANDLE != (void *)0) {
        return;
    }

    OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_HANDLE =
        OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_CREATE(
            open_cfw_tracepoint_bootstrap_timer_name,
            OPEN_CFW_TRACEPOINT_BOOTSTRAP_PERIOD_TICKS,
            0U,
            0U,
            OPEN_CFW_TRACEPOINT_BOOTSTRAP_DEFER_CALLBACK,
            OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_STORAGE
        );
    if (OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_HANDLE == (void *)0) {
        OPEN_CFW_TRACEPOINT_BOOTSTRAP_FAIL_STOP();
        return;
    }

    OPEN_CFW_TRACEPOINT_BOOTSTRAP_RETAINED_SETUP();
    OPEN_CFW_TRACEPOINT_BOOTSTRAP_DEFER_BEGIN();
}

#undef OPEN_CFW_TRACEPOINT_BOOTSTRAP_PERIOD_TICKS
#undef OPEN_CFW_TRACEPOINT_BOOTSTRAP_DEFER_BEGIN
#undef OPEN_CFW_TRACEPOINT_BOOTSTRAP_DEFER_CALLBACK
#undef OPEN_CFW_TRACEPOINT_BOOTSTRAP_FAIL_STOP
#undef OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_STORAGE
#undef OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_HANDLE
#undef OPEN_CFW_TRACEPOINT_BOOTSTRAP_RETAINED_SETUP
#undef OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_CREATE
