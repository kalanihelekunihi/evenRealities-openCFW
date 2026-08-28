/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded CMSIS event-loop, delayed-callback, and timer reimplementation
 * matched to stock entries 0x004764E0 through 0x00476BEF.
 */

typedef __UINTPTR_TYPE__ open_cfw_event_loop_uintptr;
typedef void (*open_cfw_event_loop_callback)(void *);
typedef void (*open_cfw_event_loop_thread_entry)(void *);
typedef void (*open_cfw_event_loop_timer_entry)(unsigned int);

typedef unsigned int (*open_cfw_event_loop_log_level_function)(void);
typedef void (*open_cfw_event_loop_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_event_loop_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

typedef void *(*open_cfw_event_loop_queue_create_function)(
    unsigned int,
    unsigned int,
    const void *
);
typedef void *(*open_cfw_event_loop_timer_create_function)(
    open_cfw_event_loop_timer_entry,
    unsigned int,
    unsigned int,
    const void *
);
typedef void *(*open_cfw_event_loop_mutex_create_function)(const void *);
typedef void *(*open_cfw_event_loop_thread_create_function)(
    open_cfw_event_loop_thread_entry,
    void *,
    const void *
);
typedef unsigned int (*open_cfw_event_loop_handle_function)(void *);
typedef unsigned int (*open_cfw_event_loop_queue_get_function)(
    void *,
    void *,
    unsigned char *,
    unsigned int
);
typedef unsigned int (*open_cfw_event_loop_queue_put_function)(
    void *,
    const void *,
    unsigned char,
    unsigned int
);
typedef unsigned int (*open_cfw_event_loop_mutex_acquire_function)(
    void *,
    unsigned int
);
typedef unsigned int (*open_cfw_event_loop_timer_start_function)(
    void *,
    unsigned int
);
typedef void (*open_cfw_event_loop_void_function)(void);
typedef void (*open_cfw_event_loop_delay_function)(unsigned int);
typedef unsigned int (*open_cfw_event_loop_tick_function)(void);

#ifndef OPEN_CFW_EVENT_LOOP_QUEUE_HANDLE
#define OPEN_CFW_EVENT_LOOP_QUEUE_HANDLE \
    (*(void *volatile *)0x200745ECU)
#endif
#ifndef OPEN_CFW_EVENT_LOOP_THREAD_HANDLE
#define OPEN_CFW_EVENT_LOOP_THREAD_HANDLE \
    (*(void *volatile *)0x200745F0U)
#endif
#ifndef OPEN_CFW_EVENT_LOOP_MUTEX_HANDLE
#define OPEN_CFW_EVENT_LOOP_MUTEX_HANDLE \
    (*(void *volatile *)0x200745F4U)
#endif
#ifndef OPEN_CFW_EVENT_LOOP_TIMER_HANDLE
#define OPEN_CFW_EVENT_LOOP_TIMER_HANDLE \
    (*(void *volatile *)0x200745F8U)
#endif
#ifndef OPEN_CFW_EVENT_LOOP_LAST_TICK
#define OPEN_CFW_EVENT_LOOP_LAST_TICK \
    (*(volatile unsigned int *)0x200745FCU)
#endif
#ifndef OPEN_CFW_EVENT_LOOP_NEXT_DELAY
#define OPEN_CFW_EVENT_LOOP_NEXT_DELAY \
    (*(volatile unsigned int *)0x20074600U)
#endif
#ifndef OPEN_CFW_EVENT_LOOP_CALLBACKS
#define OPEN_CFW_EVENT_LOOP_CALLBACKS \
    ((open_cfw_event_loop_callback volatile *)0x2006DAD4U)
#endif
#ifndef OPEN_CFW_EVENT_LOOP_ARGUMENTS
#define OPEN_CFW_EVENT_LOOP_ARGUMENTS \
    ((void *volatile *)0x2006DBD4U)
#endif
#ifndef OPEN_CFW_EVENT_LOOP_DELAYS
#define OPEN_CFW_EVENT_LOOP_DELAYS \
    ((volatile unsigned int *)0x2006DCD4U)
#endif

#ifndef OPEN_CFW_EVENT_LOOP_LOG_LEVEL
#define OPEN_CFW_EVENT_LOOP_LOG_LEVEL() \
    (((open_cfw_event_loop_log_level_function)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_EVENT_LOOP_LOG
#define OPEN_CFW_EVENT_LOOP_LOG(...) \
    (((open_cfw_event_loop_log_function)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_EVENT_LOOP_TRACE
#define OPEN_CFW_EVENT_LOOP_TRACE(...) \
    (((open_cfw_event_loop_trace_function)0x0043CE9FU)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_EVENT_LOOP_QUEUE_CREATE
#define OPEN_CFW_EVENT_LOOP_QUEUE_CREATE(count, size, attributes) \
    (((open_cfw_event_loop_queue_create_function)0x00449A33U)( \
        (count), (size), (attributes) \
    ))
#endif
#ifndef OPEN_CFW_EVENT_LOOP_TIMER_CREATE
#define OPEN_CFW_EVENT_LOOP_TIMER_CREATE(callback, type, argument, attributes) \
    (((open_cfw_event_loop_timer_create_function)0x004493B1U)( \
        (callback), (type), (argument), (attributes) \
    ))
#endif
#ifndef OPEN_CFW_EVENT_LOOP_MUTEX_CREATE
#define OPEN_CFW_EVENT_LOOP_MUTEX_CREATE(attributes) \
    (((open_cfw_event_loop_mutex_create_function)0x0044971DU)(attributes))
#endif
#ifndef OPEN_CFW_EVENT_LOOP_THREAD_CREATE
#define OPEN_CFW_EVENT_LOOP_THREAD_CREATE(entry, argument, attributes) \
    (((open_cfw_event_loop_thread_create_function)0x004490E3U)( \
        (entry), (argument), (attributes) \
    ))
#endif
#ifndef OPEN_CFW_EVENT_LOOP_THREAD_TERMINATE
#define OPEN_CFW_EVENT_LOOP_THREAD_TERMINATE(handle) \
    (((open_cfw_event_loop_handle_function)0x004491FFU)(handle))
#endif
#ifndef OPEN_CFW_EVENT_LOOP_QUEUE_GET
#define OPEN_CFW_EVENT_LOOP_QUEUE_GET(queue, event, priority, timeout) \
    (((open_cfw_event_loop_queue_get_function)0x00449B3DU)( \
        (queue), (event), (priority), (timeout) \
    ))
#endif
#ifndef OPEN_CFW_EVENT_LOOP_QUEUE_PUT
#define OPEN_CFW_EVENT_LOOP_QUEUE_PUT(queue, event, priority, timeout) \
    (((open_cfw_event_loop_queue_put_function)0x00449ABFU)( \
        (queue), (event), (priority), (timeout) \
    ))
#endif
#ifndef OPEN_CFW_EVENT_LOOP_MUTEX_ACQUIRE
#define OPEN_CFW_EVENT_LOOP_MUTEX_ACQUIRE(handle, timeout) \
    (((open_cfw_event_loop_mutex_acquire_function)0x004497B7U)( \
        (handle), (timeout) \
    ))
#endif
#ifndef OPEN_CFW_EVENT_LOOP_MUTEX_RELEASE
#define OPEN_CFW_EVENT_LOOP_MUTEX_RELEASE(handle) \
    (((open_cfw_event_loop_handle_function)0x0044981DU)(handle))
#endif
#ifndef OPEN_CFW_EVENT_LOOP_TIMER_START
#define OPEN_CFW_EVENT_LOOP_TIMER_START(handle, ticks) \
    (((open_cfw_event_loop_timer_start_function)0x00449499U)( \
        (handle), (ticks) \
    ))
#endif
#ifndef OPEN_CFW_EVENT_LOOP_TIMER_STOP
#define OPEN_CFW_EVENT_LOOP_TIMER_STOP(handle) \
    (((open_cfw_event_loop_handle_function)0x004494D9U)(handle))
#endif
#ifndef OPEN_CFW_EVENT_LOOP_CRITICAL_ENTER
#define OPEN_CFW_EVENT_LOOP_CRITICAL_ENTER() \
    (((open_cfw_event_loop_void_function)0x004420D1U)())
#endif
#ifndef OPEN_CFW_EVENT_LOOP_CRITICAL_EXIT
#define OPEN_CFW_EVENT_LOOP_CRITICAL_EXIT() \
    (((open_cfw_event_loop_void_function)0x004420E9U)())
#endif
#ifndef OPEN_CFW_EVENT_LOOP_DELAY
#define OPEN_CFW_EVENT_LOOP_DELAY(ticks) \
    (((open_cfw_event_loop_delay_function)0x00449377U)(ticks))
#endif
#ifndef OPEN_CFW_EVENT_LOOP_TICK
#define OPEN_CFW_EVENT_LOOP_TICK() \
    (((open_cfw_event_loop_tick_function)0x004490CDU)())
#endif

#ifndef OPEN_CFW_EVENT_LOOP_TASK_CONTINUE
#define OPEN_CFW_EVENT_LOOP_TASK_CONTINUE() 1
#endif

struct open_cfw_event_loop_event {
    void *argument;
    open_cfw_event_loop_callback callback;
};

void open_cfw_event_loop_task(void *argument);
void open_cfw_event_loop_push(
    open_cfw_event_loop_callback callback,
    void *argument,
    unsigned int timeout
);
void open_cfw_event_loop_timer_callback(unsigned int elapsed_code);

static __attribute__((always_inline)) inline int
open_cfw_event_loop_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_EVENT_LOOP_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_EVENT_LOOP_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_event_loop_diagnostic(
    const void *function,
    unsigned int line,
    const void *message,
    unsigned int trace_level,
    const void *trace,
    unsigned int argument_count,
    unsigned int first,
    unsigned int second
)
{
    const void *module =
        (const void *)(open_cfw_event_loop_uintptr)0x0078D65CU;
    const void *file =
        (const void *)(open_cfw_event_loop_uintptr)0x006F3C38U;

    if ((OPEN_CFW_EVENT_LOOP_LOG_LEVEL() & 2U) != 0U) {
        if (argument_count == 0U) {
            OPEN_CFW_EVENT_LOOP_LOG(
                1U, module, file, function, line, message
            );
        }
        else if (argument_count == 1U) {
            OPEN_CFW_EVENT_LOOP_LOG(
                1U, module, file, function, line, message, first
            );
        }
        else {
            OPEN_CFW_EVENT_LOOP_LOG(
                1U, module, file, function, line, message, first, second
            );
        }
    }

    if (open_cfw_event_loop_trace_enabled()) {
        if (argument_count == 0U) {
            OPEN_CFW_EVENT_LOOP_TRACE(trace_level, trace, trace);
        }
        else if (argument_count == 1U) {
            OPEN_CFW_EVENT_LOOP_TRACE(
                trace_level, trace, trace, first
            );
        }
        else {
            OPEN_CFW_EVENT_LOOP_TRACE(
                trace_level, trace, trace, first, second
            );
        }
    }
}

void open_cfw_event_loop_initialize(void)
{
    if (OPEN_CFW_EVENT_LOOP_QUEUE_HANDLE == (void *)0) {
        OPEN_CFW_EVENT_LOOP_QUEUE_HANDLE = OPEN_CFW_EVENT_LOOP_QUEUE_CREATE(
            15U,
            8U,
            (const void *)(open_cfw_event_loop_uintptr)0x007776FCU
        );
        if (OPEN_CFW_EVENT_LOOP_QUEUE_HANDLE == (void *)0) {
            open_cfw_event_loop_diagnostic(
                (const void *)(open_cfw_event_loop_uintptr)0x0077F658U,
                0x58U,
                (const void *)(open_cfw_event_loop_uintptr)0x0073EF24U,
                0x04000000U,
                (const void *)(open_cfw_event_loop_uintptr)0x00729C74U,
                0U,
                0U,
                0U
            );
        }
    }

    if (OPEN_CFW_EVENT_LOOP_TIMER_HANDLE == (void *)0) {
        OPEN_CFW_EVENT_LOOP_TIMER_HANDLE = OPEN_CFW_EVENT_LOOP_TIMER_CREATE(
            open_cfw_event_loop_timer_callback,
            0U,
            0U,
            (const void *)(open_cfw_event_loop_uintptr)0x00785FF0U
        );
        if (OPEN_CFW_EVENT_LOOP_TIMER_HANDLE == (void *)0) {
            open_cfw_event_loop_diagnostic(
                (const void *)(open_cfw_event_loop_uintptr)0x0077F658U,
                0x61U,
                (const void *)(open_cfw_event_loop_uintptr)0x0074A30CU,
                0x04000000U,
                (const void *)(open_cfw_event_loop_uintptr)0x00734364U,
                0U,
                0U,
                0U
            );
        }
    }

    if (OPEN_CFW_EVENT_LOOP_MUTEX_HANDLE == (void *)0) {
        OPEN_CFW_EVENT_LOOP_MUTEX_HANDLE = OPEN_CFW_EVENT_LOOP_MUTEX_CREATE(
            (const void *)(open_cfw_event_loop_uintptr)0x00785FE0U
        );
        if (OPEN_CFW_EVENT_LOOP_MUTEX_HANDLE == (void *)0) {
            open_cfw_event_loop_diagnostic(
                (const void *)(open_cfw_event_loop_uintptr)0x0077F658U,
                0x6AU,
                (const void *)(open_cfw_event_loop_uintptr)0x00734394U,
                0x04000000U,
                (const void *)(open_cfw_event_loop_uintptr)0x0071F3D8U,
                0U,
                0U,
                0U
            );
        }
    }

    if (OPEN_CFW_EVENT_LOOP_THREAD_HANDLE != (void *)0) {
        (void)OPEN_CFW_EVENT_LOOP_THREAD_TERMINATE(
            OPEN_CFW_EVENT_LOOP_THREAD_HANDLE
        );
        OPEN_CFW_EVENT_LOOP_THREAD_HANDLE = (void *)0;
    }
    if (OPEN_CFW_EVENT_LOOP_THREAD_HANDLE == (void *)0) {
        OPEN_CFW_EVENT_LOOP_THREAD_HANDLE = OPEN_CFW_EVENT_LOOP_THREAD_CREATE(
            open_cfw_event_loop_task,
            (void *)0,
            (const void *)(open_cfw_event_loop_uintptr)0x00754A1CU
        );
        if (OPEN_CFW_EVENT_LOOP_THREAD_HANDLE == (void *)0) {
            open_cfw_event_loop_diagnostic(
                (const void *)(open_cfw_event_loop_uintptr)0x0077F658U,
                0x79U,
                (const void *)(open_cfw_event_loop_uintptr)0x007549F8U,
                0x04000000U,
                (const void *)(open_cfw_event_loop_uintptr)0x007343C4U,
                0U,
                0U,
                0U
            );
        }
    }
}

void open_cfw_event_loop_task(void *argument)
{
    struct open_cfw_event_loop_event event;
    unsigned int result;

    (void)argument;
    do {
        result = OPEN_CFW_EVENT_LOOP_QUEUE_GET(
            OPEN_CFW_EVENT_LOOP_QUEUE_HANDLE,
            &event,
            (unsigned char *)0,
            0xFFFFFFFFU
        );
        if (result == 0U) {
            event.callback(event.argument);
        }
        else {
            open_cfw_event_loop_diagnostic(
                (const void *)(open_cfw_event_loop_uintptr)0x0077F66CU,
                0x8CU,
                (const void *)(open_cfw_event_loop_uintptr)0x00729CA8U,
                0x04400000U,
                (const void *)(open_cfw_event_loop_uintptr)0x0070C064U,
                1U,
                result,
                0U
            );
        }
    } while (OPEN_CFW_EVENT_LOOP_TASK_CONTINUE());
}

void open_cfw_event_loop_push(
    open_cfw_event_loop_callback callback,
    void *argument,
    unsigned int timeout
)
{
    struct open_cfw_event_loop_event event;
    unsigned int result;

    if (OPEN_CFW_EVENT_LOOP_THREAD_HANDLE == (void *)0) {
        open_cfw_event_loop_diagnostic(
            (const void *)(open_cfw_event_loop_uintptr)0x0077F680U,
            0x96U,
            (const void *)(open_cfw_event_loop_uintptr)0x007343F4U,
            0x04000000U,
            (const void *)(open_cfw_event_loop_uintptr)0x00715700U,
            0U,
            0U,
            0U
        );
        return;
    }

    event.argument = argument;
    event.callback = callback;
    if (OPEN_CFW_EVENT_LOOP_QUEUE_HANDLE == (void *)0) {
        return;
    }

    result = OPEN_CFW_EVENT_LOOP_QUEUE_PUT(
        OPEN_CFW_EVENT_LOOP_QUEUE_HANDLE,
        &event,
        0U,
        timeout
    );
    if (result != 0U) {
        open_cfw_event_loop_diagnostic(
            (const void *)(open_cfw_event_loop_uintptr)0x0077F680U,
            0xA0U,
            (const void *)(open_cfw_event_loop_uintptr)0x0073EF50U,
            0x04400000U,
            (const void *)(open_cfw_event_loop_uintptr)0x00729CDCU,
            1U,
            result,
            0U
        );
    }
}

void open_cfw_event_loop_timer_callback(unsigned int elapsed_code)
{
    unsigned int elapsed;
    unsigned int minimum = 0xFFFFFFFFU;
    unsigned int index;
    unsigned int result;

    OPEN_CFW_EVENT_LOOP_CRITICAL_ENTER();
    elapsed = OPEN_CFW_EVENT_LOOP_NEXT_DELAY;
    OPEN_CFW_EVENT_LOOP_CRITICAL_EXIT();

    if ((elapsed_code & 0xFF000000U) == 0xFF000000U) {
        elapsed = elapsed_code & 0x00FFFFFFU;
    }

    result = OPEN_CFW_EVENT_LOOP_MUTEX_ACQUIRE(
        OPEN_CFW_EVENT_LOOP_MUTEX_HANDLE,
        0xFFFFFFFFU
    );
    if (result != 0U) {
        open_cfw_event_loop_diagnostic(
            (const void *)(open_cfw_event_loop_uintptr)0x0076BA94U,
            0xB8U,
            (const void *)(open_cfw_event_loop_uintptr)0x00734424U,
            0x04000000U,
            (const void *)(open_cfw_event_loop_uintptr)0x0071F410U,
            0U,
            0U,
            0U
        );
    }

    for (index = 0U; index < 64U; ++index) {
        open_cfw_event_loop_callback callback =
            OPEN_CFW_EVENT_LOOP_CALLBACKS[index];

        if (callback != (open_cfw_event_loop_callback)0) {
            unsigned int remaining = OPEN_CFW_EVENT_LOOP_DELAYS[index];

            if (elapsed >= remaining) {
                remaining = 0U;
            }
            else {
                remaining -= elapsed;
            }
            OPEN_CFW_EVENT_LOOP_DELAYS[index] = remaining;
            if (remaining == 0U) {
                OPEN_CFW_EVENT_LOOP_CALLBACKS[index] =
                    (open_cfw_event_loop_callback)0;
                open_cfw_event_loop_push(
                    callback,
                    OPEN_CFW_EVENT_LOOP_ARGUMENTS[index],
                    1U
                );
            }
        }
    }

    for (index = 0U; index < 64U; ++index) {
        if (
            OPEN_CFW_EVENT_LOOP_CALLBACKS[index]
            != (open_cfw_event_loop_callback)0
            && OPEN_CFW_EVENT_LOOP_DELAYS[index] < minimum
        ) {
            minimum = OPEN_CFW_EVENT_LOOP_DELAYS[index];
        }
    }

    result = OPEN_CFW_EVENT_LOOP_MUTEX_RELEASE(
        OPEN_CFW_EVENT_LOOP_MUTEX_HANDLE
    );
    if (result != 0U) {
        open_cfw_event_loop_diagnostic(
            (const void *)(open_cfw_event_loop_uintptr)0x0076BA94U,
            0xD5U,
            (const void *)(open_cfw_event_loop_uintptr)0x00729D10U,
            0x04000000U,
            (const void *)(open_cfw_event_loop_uintptr)0x0071573CU,
            0U,
            0U,
            0U
        );
    }

    if (minimum == 0x7FFFFFFFU || minimum == 0U) {
        return;
    }

    OPEN_CFW_EVENT_LOOP_CRITICAL_ENTER();
    OPEN_CFW_EVENT_LOOP_NEXT_DELAY = minimum;
    OPEN_CFW_EVENT_LOOP_CRITICAL_EXIT();

    result = OPEN_CFW_EVENT_LOOP_TIMER_START(
        OPEN_CFW_EVENT_LOOP_TIMER_HANDLE,
        minimum
    );
    if (result != 0U) {
        open_cfw_event_loop_diagnostic(
            (const void *)(open_cfw_event_loop_uintptr)0x0076BA94U,
            0xE1U,
            (const void *)(open_cfw_event_loop_uintptr)0x0074A334U,
            0x04800000U,
            (const void *)(open_cfw_event_loop_uintptr)0x00734454U,
            2U,
            minimum,
            result
        );
    }
    OPEN_CFW_EVENT_LOOP_LAST_TICK = OPEN_CFW_EVENT_LOOP_TICK();
}

void open_cfw_event_loop_push_delayed(
    open_cfw_event_loop_callback callback,
    void *argument,
    unsigned int delay
)
{
    unsigned int index;
    unsigned int now = 0U;
    unsigned int elapsed = 0U;
    unsigned int result;

    if (OPEN_CFW_EVENT_LOOP_THREAD_HANDLE == (void *)0) {
        open_cfw_event_loop_diagnostic(
            (const void *)(open_cfw_event_loop_uintptr)0x0076BAB0U,
            0xEFU,
            (const void *)(open_cfw_event_loop_uintptr)0x00703180U,
            0x04000000U,
            (const void *)(open_cfw_event_loop_uintptr)0x006F3C84U,
            0U,
            0U,
            0U
        );
        do {
            OPEN_CFW_EVENT_LOOP_DELAY(10U);
        } while (OPEN_CFW_EVENT_LOOP_THREAD_HANDLE == (void *)0);
    }

    if (delay < 2U) {
        open_cfw_event_loop_push(callback, argument, 0xFFFFFFFFU);
        return;
    }

    result = OPEN_CFW_EVENT_LOOP_MUTEX_ACQUIRE(
        OPEN_CFW_EVENT_LOOP_MUTEX_HANDLE,
        0xFFFFFFFFU
    );
    if (result != 0U) {
        open_cfw_event_loop_diagnostic(
            (const void *)(open_cfw_event_loop_uintptr)0x0076BAB0U,
            0x100U,
            (const void *)(open_cfw_event_loop_uintptr)0x00734484U,
            0x04000000U,
            (const void *)(open_cfw_event_loop_uintptr)0x0071F448U,
            0U,
            0U,
            0U
        );
    }

    for (index = 0U; index < 64U; ++index) {
        if (
            OPEN_CFW_EVENT_LOOP_CALLBACKS[index]
            == (open_cfw_event_loop_callback)0
        ) {
            break;
        }
    }
    if (index < 64U) {
        OPEN_CFW_EVENT_LOOP_CALLBACKS[index] = callback;
        OPEN_CFW_EVENT_LOOP_ARGUMENTS[index] = argument;
        now = OPEN_CFW_EVENT_LOOP_TICK();
        elapsed = now - OPEN_CFW_EVENT_LOOP_LAST_TICK;
        OPEN_CFW_EVENT_LOOP_DELAYS[index] = elapsed + delay;
    }

    result = OPEN_CFW_EVENT_LOOP_MUTEX_RELEASE(
        OPEN_CFW_EVENT_LOOP_MUTEX_HANDLE
    );
    if (result != 0U) {
        open_cfw_event_loop_diagnostic(
            (const void *)(open_cfw_event_loop_uintptr)0x0076BAB0U,
            0x110U,
            (const void *)(open_cfw_event_loop_uintptr)0x007344B4U,
            0x04000000U,
            (const void *)(open_cfw_event_loop_uintptr)0x0071F480U,
            0U,
            0U,
            0U
        );
    }

    if (index < 64U) {
        (void)OPEN_CFW_EVENT_LOOP_TIMER_STOP(
            OPEN_CFW_EVENT_LOOP_TIMER_HANDLE
        );
        open_cfw_event_loop_timer_callback(elapsed | 0xFF000000U);
    }
}

unsigned char open_cfw_event_loop_remove_delayed(
    open_cfw_event_loop_callback callback
)
{
    unsigned int index;
    unsigned int elapsed;
    unsigned int result;
    unsigned char found = 0U;

    if (OPEN_CFW_EVENT_LOOP_THREAD_HANDLE == (void *)0) {
        open_cfw_event_loop_diagnostic(
            (const void *)(open_cfw_event_loop_uintptr)0x0076BACCU,
            0x11EU,
            (const void *)(open_cfw_event_loop_uintptr)0x00760250U,
            0x04000000U,
            (const void *)(open_cfw_event_loop_uintptr)0x0073EF7CU,
            0U,
            0U,
            0U
        );
        return 0U;
    }

    result = OPEN_CFW_EVENT_LOOP_MUTEX_ACQUIRE(
        OPEN_CFW_EVENT_LOOP_MUTEX_HANDLE,
        0xFFFFFFFFU
    );
    if (result != 0U) {
        open_cfw_event_loop_diagnostic(
            (const void *)(open_cfw_event_loop_uintptr)0x0076BACCU,
            0x124U,
            (const void *)(open_cfw_event_loop_uintptr)0x007344E4U,
            0x04000000U,
            (const void *)(open_cfw_event_loop_uintptr)0x0071F4B8U,
            0U,
            0U,
            0U
        );
    }

    for (index = 0U; index < 64U; ++index) {
        if (OPEN_CFW_EVENT_LOOP_CALLBACKS[index] == callback) {
            OPEN_CFW_EVENT_LOOP_CALLBACKS[index] =
                (open_cfw_event_loop_callback)0;
            found = 1U;
        }
    }

    result = OPEN_CFW_EVENT_LOOP_MUTEX_RELEASE(
        OPEN_CFW_EVENT_LOOP_MUTEX_HANDLE
    );
    if (result != 0U) {
        open_cfw_event_loop_diagnostic(
            (const void *)(open_cfw_event_loop_uintptr)0x0076BACCU,
            0x12EU,
            (const void *)(open_cfw_event_loop_uintptr)0x007031C4U,
            0x04000000U,
            (const void *)(open_cfw_event_loop_uintptr)0x006F3CD0U,
            0U,
            0U,
            0U
        );
    }

    if (found != 0U) {
        elapsed = OPEN_CFW_EVENT_LOOP_TICK()
            - OPEN_CFW_EVENT_LOOP_LAST_TICK;
        (void)OPEN_CFW_EVENT_LOOP_TIMER_STOP(
            OPEN_CFW_EVENT_LOOP_TIMER_HANDLE
        );
        open_cfw_event_loop_timer_callback(elapsed | 0xFF000000U);
    }
    return found;
}
