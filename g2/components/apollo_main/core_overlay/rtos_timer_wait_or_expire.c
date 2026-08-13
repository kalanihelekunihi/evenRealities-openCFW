/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * RTOS timer wait-or-expire processor matched to stock entry 0x0047E88C.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_wait_or_expire_uintptr;

typedef void (*open_cfw_rtos_timer_wait_or_expire_suspend_function)(void);
typedef unsigned int (
    *open_cfw_rtos_timer_wait_or_expire_resume_function
)(void);
typedef void (*open_cfw_rtos_timer_wait_or_expire_wait_function)(
    void *,
    unsigned int,
    unsigned int
);
typedef void (*open_cfw_rtos_timer_wait_or_expire_yield_function)(void);

void open_cfw_rtos_timer_expire(unsigned int, unsigned int);
unsigned int open_cfw_rtos_timer_sample(unsigned int *);

#ifndef OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_SUSPEND
#define OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_SUSPEND() \
    (((open_cfw_rtos_timer_wait_or_expire_suspend_function) \
        (open_cfw_rtos_timer_wait_or_expire_uintptr)0x00454D7DU)())
#endif

#ifndef OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_SAMPLE
#define OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_SAMPLE(switched) \
    open_cfw_rtos_timer_sample(switched)
#endif

#ifndef OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_RESUME
#define OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_RESUME() \
    (((open_cfw_rtos_timer_wait_or_expire_resume_function) \
        (open_cfw_rtos_timer_wait_or_expire_uintptr)0x00454DCDU)())
#endif

#ifndef OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_EXPIRE
#define OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_EXPIRE(expiry, time_now) \
    open_cfw_rtos_timer_expire(expiry, time_now)
#endif

#ifndef OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_OVERFLOW_EMPTY
#define OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_OVERFLOW_EMPTY() \
    ( \
        *(volatile unsigned int *)( \
            open_cfw_rtos_timer_wait_or_expire_uintptr)( \
                *(volatile unsigned int *) \
                    (open_cfw_rtos_timer_wait_or_expire_uintptr) \
                    0x20074AACU) == 0U \
    )
#endif

#ifndef OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_QUEUE
#define OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_QUEUE() \
    ((void *)(open_cfw_rtos_timer_wait_or_expire_uintptr) \
        (*(volatile unsigned int *) \
            (open_cfw_rtos_timer_wait_or_expire_uintptr)0x20074AB0U))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_WAIT
#define OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_WAIT( \
    queue, delay, wait_indefinitely \
) \
    (((open_cfw_rtos_timer_wait_or_expire_wait_function) \
        (open_cfw_rtos_timer_wait_or_expire_uintptr)0x00442031U)( \
            queue, delay, wait_indefinitely))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_YIELD
#define OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_YIELD() \
    (((open_cfw_rtos_timer_wait_or_expire_yield_function) \
        (open_cfw_rtos_timer_wait_or_expire_uintptr)0x004420BDU)())
#endif

__attribute__((used, noinline))
void open_cfw_rtos_timer_wait_or_expire(
    unsigned int next_expiry,
    unsigned int active_list_empty
)
{
    unsigned int timer_lists_switched = 0U;
    unsigned int time_now;

    OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_SUSPEND();
    time_now = OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_SAMPLE(
        &timer_lists_switched
    );
    if (timer_lists_switched != 0U) {
        (void)OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_RESUME();
        return;
    }

    if (
        active_list_empty == 0U
        && time_now >= next_expiry
    ) {
        (void)OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_RESUME();
        OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_EXPIRE(
            next_expiry,
            time_now
        );
        return;
    }

    if (active_list_empty != 0U) {
        active_list_empty =
            (
                OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_OVERFLOW_EMPTY()
                != 0U
            );
    }
    OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_WAIT(
        OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_QUEUE(),
        next_expiry - time_now,
        active_list_empty
    );
    if (OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_RESUME() == 0U) {
        OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_YIELD();
    }
}

#undef OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_YIELD
#undef OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_WAIT
#undef OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_QUEUE
#undef OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_OVERFLOW_EMPTY
#undef OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_EXPIRE
#undef OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_RESUME
#undef OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_SAMPLE
#undef OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_SUSPEND
