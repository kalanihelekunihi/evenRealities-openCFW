/*
 * SPDX-License-Identifier: MIT
 *
 * EasyLogger tracepoint deferral state machine matched to stock entries
 * 0x0047DD62, 0x0047DD8A, 0x0047DD92, and 0x0047DDAC.
 */

typedef __UINTPTR_TYPE__ open_cfw_tracepoint_uintptr;

typedef unsigned int (*open_cfw_tracepoint_query_function)(void);
typedef unsigned int (*open_cfw_tracepoint_action_function)(void);
typedef unsigned int (*open_cfw_tracepoint_timer_command_function)(
    void *,
    unsigned int,
    unsigned int,
    void *,
    unsigned int
);

#ifndef OPEN_CFW_TRACEPOINT_SHOULD_DEFER
#define OPEN_CFW_TRACEPOINT_SHOULD_DEFER() \
    (((open_cfw_tracepoint_query_function) \
        (open_cfw_tracepoint_uintptr)0x00443485U)())
#endif

#ifndef OPEN_CFW_TRACEPOINT_EVENT_SET
#define OPEN_CFW_TRACEPOINT_EVENT_SET() \
    (((open_cfw_tracepoint_action_function) \
        (open_cfw_tracepoint_uintptr)0x00448F99U)())
#endif

#ifndef OPEN_CFW_TRACEPOINT_CAPTURE
#define OPEN_CFW_TRACEPOINT_CAPTURE() \
    (((open_cfw_tracepoint_action_function) \
        (open_cfw_tracepoint_uintptr)0x0048EB91U)())
#endif

#ifndef OPEN_CFW_TRACEPOINT_TIMER_COMMAND
#define OPEN_CFW_TRACEPOINT_TIMER_COMMAND( \
    timer, command, value, higher_priority_task_woken, wait_ticks \
) \
    (((open_cfw_tracepoint_timer_command_function) \
        (open_cfw_tracepoint_uintptr)0x0047E7B1U)( \
            (timer), \
            (command), \
            (value), \
            (higher_priority_task_woken), \
            (wait_ticks) \
        ))
#endif

#ifndef OPEN_CFW_TRACEPOINT_TIMER_HANDLE
#define OPEN_CFW_TRACEPOINT_TIMER_HANDLE \
    (*(void * volatile *)(open_cfw_tracepoint_uintptr)0x20074ACCU)
#endif

#ifndef OPEN_CFW_TRACEPOINT_RETRY_COUNT
#define OPEN_CFW_TRACEPOINT_RETRY_COUNT \
    (*(volatile int *)(open_cfw_tracepoint_uintptr)0x20074AD0U)
#endif

#define OPEN_CFW_TRACEPOINT_TIMER_CHANGE_PERIOD 4U
#define OPEN_CFW_TRACEPOINT_DEFER_TICKS 2000U
#define OPEN_CFW_TRACEPOINT_RETRY_TICKS 5000U
#define OPEN_CFW_TRACEPOINT_RETRY_LIMIT 10

__attribute__((used, noinline))
void open_cfw_tracepoint_defer_dispatch(void)
{
    if (OPEN_CFW_TRACEPOINT_SHOULD_DEFER() != 0U) {
        (void)OPEN_CFW_TRACEPOINT_TIMER_COMMAND(
            OPEN_CFW_TRACEPOINT_TIMER_HANDLE,
            OPEN_CFW_TRACEPOINT_TIMER_CHANGE_PERIOD,
            OPEN_CFW_TRACEPOINT_DEFER_TICKS,
            (void *)0,
            0U
        );
    }
    else {
        (void)OPEN_CFW_TRACEPOINT_EVENT_SET();
    }
}

__attribute__((used, noinline))
void open_cfw_tracepoint_defer_timer_callback(void *timer)
{
    (void)timer;
    open_cfw_tracepoint_defer_dispatch();
}

__attribute__((used, noinline))
void open_cfw_tracepoint_defer_begin(void)
{
    if (OPEN_CFW_TRACEPOINT_TIMER_HANDLE != (void *)0) {
        OPEN_CFW_TRACEPOINT_RETRY_COUNT = 0;
        open_cfw_tracepoint_defer_dispatch();
    }
}

__attribute__((used, noinline))
void open_cfw_tracepoint_capture_retry(void)
{
    int retry_count;

    if (OPEN_CFW_TRACEPOINT_SHOULD_DEFER() != 0U) {
        (void)OPEN_CFW_TRACEPOINT_TIMER_COMMAND(
            OPEN_CFW_TRACEPOINT_TIMER_HANDLE,
            OPEN_CFW_TRACEPOINT_TIMER_CHANGE_PERIOD,
            OPEN_CFW_TRACEPOINT_DEFER_TICKS,
            (void *)0,
            0U
        );
        return;
    }

    if (OPEN_CFW_TRACEPOINT_CAPTURE() == 0U) {
        return;
    }

    retry_count = OPEN_CFW_TRACEPOINT_RETRY_COUNT;
    if (retry_count >= OPEN_CFW_TRACEPOINT_RETRY_LIMIT) {
        return;
    }

    OPEN_CFW_TRACEPOINT_RETRY_COUNT = retry_count + 1;
    (void)OPEN_CFW_TRACEPOINT_TIMER_COMMAND(
        OPEN_CFW_TRACEPOINT_TIMER_HANDLE,
        OPEN_CFW_TRACEPOINT_TIMER_CHANGE_PERIOD,
        OPEN_CFW_TRACEPOINT_RETRY_TICKS,
        (void *)0,
        0U
    );
}

#undef OPEN_CFW_TRACEPOINT_RETRY_LIMIT
#undef OPEN_CFW_TRACEPOINT_RETRY_TICKS
#undef OPEN_CFW_TRACEPOINT_DEFER_TICKS
#undef OPEN_CFW_TRACEPOINT_TIMER_CHANGE_PERIOD
#undef OPEN_CFW_TRACEPOINT_RETRY_COUNT
#undef OPEN_CFW_TRACEPOINT_TIMER_HANDLE
#undef OPEN_CFW_TRACEPOINT_TIMER_COMMAND
#undef OPEN_CFW_TRACEPOINT_CAPTURE
#undef OPEN_CFW_TRACEPOINT_EVENT_SET
#undef OPEN_CFW_TRACEPOINT_SHOULD_DEFER
