/*
 * SPDX-License-Identifier: MIT
 *
 * RTOS auto-reload catch-up loop matched to stock entry 0x0047E812.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_reload_uintptr;

typedef void (*open_cfw_rtos_timer_reload_callback_function)(void *);

unsigned int open_cfw_rtos_timer_insert(
    void *,
    unsigned int,
    unsigned int,
    unsigned int
);

#ifndef OPEN_CFW_RTOS_TIMER_RELOAD_PERIOD
#define OPEN_CFW_RTOS_TIMER_RELOAD_PERIOD(timer) \
    (*(volatile unsigned int *)( \
        (volatile unsigned char *)(timer) + 0x18U))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_RELOAD_INSERT
#define OPEN_CFW_RTOS_TIMER_RELOAD_INSERT( \
    timer, next_expiry, time_now, expired_time \
) \
    open_cfw_rtos_timer_insert( \
        timer, next_expiry, time_now, expired_time \
    )
#endif

#ifndef OPEN_CFW_RTOS_TIMER_RELOAD_CALLBACK
#define OPEN_CFW_RTOS_TIMER_RELOAD_CALLBACK(timer) \
    do { \
        unsigned int open_cfw_callback_address = \
            *(volatile unsigned int *)( \
                (volatile unsigned char *)(timer) + 0x20U); \
        ((open_cfw_rtos_timer_reload_callback_function) \
            (open_cfw_rtos_timer_reload_uintptr) \
            open_cfw_callback_address)(timer); \
    } while (0)
#endif

__attribute__((used, noinline))
void open_cfw_rtos_timer_reload(
    void *timer,
    unsigned int expired_time,
    unsigned int time_now
)
{
    for (;;) {
        unsigned int period =
            OPEN_CFW_RTOS_TIMER_RELOAD_PERIOD(timer);
        unsigned int next_expiry = period + expired_time;

        if (
            OPEN_CFW_RTOS_TIMER_RELOAD_INSERT(
                timer,
                next_expiry,
                time_now,
                expired_time
            ) == 0U
        ) {
            return;
        }

        period = OPEN_CFW_RTOS_TIMER_RELOAD_PERIOD(timer);
        expired_time += period;
        OPEN_CFW_RTOS_TIMER_RELOAD_CALLBACK(timer);
    }
}

#undef OPEN_CFW_RTOS_TIMER_RELOAD_CALLBACK
#undef OPEN_CFW_RTOS_TIMER_RELOAD_INSERT
#undef OPEN_CFW_RTOS_TIMER_RELOAD_PERIOD
