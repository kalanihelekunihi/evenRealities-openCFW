/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacements for the G2 2.2.6.10 display-driver runtime cluster at
 * 0x00473AA4...0x00473C43.
 */

typedef void (*open_cfw_display_runtime_thread_terminate_fn)(void *thread);
typedef void (*open_cfw_display_runtime_resource_fn)(unsigned int resource);
typedef void (*open_cfw_display_runtime_timer_callback_fn)(void *argument);
typedef void *(*open_cfw_display_runtime_timer_create_fn)(
    open_cfw_display_runtime_timer_callback_fn callback,
    unsigned int kind,
    void *argument,
    const void *attributes
);
typedef int (*open_cfw_display_runtime_timer_start_fn)(
    void *timer,
    unsigned int ticks
);
typedef int (*open_cfw_display_runtime_timer_stop_fn)(void *timer);
typedef int (*open_cfw_display_runtime_queue_send_fn)(
    void *queue,
    const void *message,
    unsigned int priority,
    unsigned int timeout
);
typedef unsigned int (*open_cfw_display_runtime_log_flags_fn)(void);
typedef void (*open_cfw_display_runtime_log_fn)(
    unsigned int level,
    const void *tag,
    const void *file,
    const void *function,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_display_runtime_backend_log_fn)(
    unsigned int mask,
    const void *format,
    const void *duplicate_format,
    ...
);

#ifndef OPEN_CFW_DISPLAY_RUNTIME_THREAD_HANDLE
#define OPEN_CFW_DISPLAY_RUNTIME_THREAD_HANDLE \
    (*(void * volatile *)(void *)0x20000660U)
#endif

#ifndef OPEN_CFW_DISPLAY_RUNTIME_QUEUE_HANDLE
#define OPEN_CFW_DISPLAY_RUNTIME_QUEUE_HANDLE \
    (*(void * volatile *)(void *)0x20000664U)
#endif

#ifndef OPEN_CFW_DISPLAY_RUNTIME_TIMER_HANDLE
#define OPEN_CFW_DISPLAY_RUNTIME_TIMER_HANDLE \
    (*(void * volatile *)(void *)0x200744F0U)
#endif

#ifndef OPEN_CFW_DISPLAY_RUNTIME_THREAD_TERMINATE
#define OPEN_CFW_DISPLAY_RUNTIME_THREAD_TERMINATE(thread) \
    (((open_cfw_display_runtime_thread_terminate_fn)0x004491FFU)(thread))
#endif

#ifndef OPEN_CFW_DISPLAY_RUNTIME_RESOURCE_ACQUIRE
#define OPEN_CFW_DISPLAY_RUNTIME_RESOURCE_ACQUIRE(resource) \
    (((open_cfw_display_runtime_resource_fn)0x004C9B87U)(resource))
#endif

#ifndef OPEN_CFW_DISPLAY_RUNTIME_RESOURCE_RELEASE
#define OPEN_CFW_DISPLAY_RUNTIME_RESOURCE_RELEASE(resource) \
    (((open_cfw_display_runtime_resource_fn)0x004C9BE3U)(resource))
#endif

#ifndef OPEN_CFW_DISPLAY_RUNTIME_TIMER_CREATE
#define OPEN_CFW_DISPLAY_RUNTIME_TIMER_CREATE( \
    callback, \
    kind, \
    argument, \
    attributes \
) \
    (((open_cfw_display_runtime_timer_create_fn)0x004493B1U)( \
        (callback), \
        (kind), \
        (argument), \
        (attributes) \
    ))
#endif

#ifndef OPEN_CFW_DISPLAY_RUNTIME_TIMER_START
#define OPEN_CFW_DISPLAY_RUNTIME_TIMER_START(timer, ticks) \
    (((open_cfw_display_runtime_timer_start_fn)0x00449499U)( \
        (timer), \
        (ticks) \
    ))
#endif

#ifndef OPEN_CFW_DISPLAY_RUNTIME_TIMER_STOP
#define OPEN_CFW_DISPLAY_RUNTIME_TIMER_STOP(timer) \
    (((open_cfw_display_runtime_timer_stop_fn)0x004494D9U)(timer))
#endif

#ifndef OPEN_CFW_DISPLAY_RUNTIME_QUEUE_SEND
#define OPEN_CFW_DISPLAY_RUNTIME_QUEUE_SEND( \
    queue, \
    message, \
    priority, \
    timeout \
) \
    (((open_cfw_display_runtime_queue_send_fn)0x00449ABFU)( \
        (queue), \
        (message), \
        (priority), \
        (timeout) \
    ))
#endif

#ifndef OPEN_CFW_DISPLAY_RUNTIME_LOG_FLAGS
#define OPEN_CFW_DISPLAY_RUNTIME_LOG_FLAGS() \
    (((open_cfw_display_runtime_log_flags_fn)0x0043D0CFU)())
#endif

#ifndef OPEN_CFW_DISPLAY_RUNTIME_LOG
#define OPEN_CFW_DISPLAY_RUNTIME_LOG \
    ((open_cfw_display_runtime_log_fn)0x0043D575U)
#endif

#ifndef OPEN_CFW_DISPLAY_RUNTIME_BACKEND_LOG
#define OPEN_CFW_DISPLAY_RUNTIME_BACKEND_LOG \
    ((open_cfw_display_runtime_backend_log_fn)0x0043CE9FU)
#endif

#define OPEN_CFW_DISPLAY_RUNTIME_TIMER_CALLBACK \
    ((open_cfw_display_runtime_timer_callback_fn)0x00473B55U)
#define OPEN_CFW_DISPLAY_RUNTIME_TIMER_ATTRIBUTES ((const void *)0x00785B20U)
#define OPEN_CFW_DISPLAY_RUNTIME_TAG ((const void *)0x0077EDC0U)
#define OPEN_CFW_DISPLAY_RUNTIME_FILE ((const void *)0x006ECB68U)
#define OPEN_CFW_DISPLAY_RUNTIME_TIMER_INIT_FUNCTION \
    ((const void *)0x0075F3D0U)
#define OPEN_CFW_DISPLAY_RUNTIME_TIMER_INIT_FAILED \
    ((const void *)0x0073DF80U)
#define OPEN_CFW_DISPLAY_RUNTIME_TIMER_INIT_BACKEND \
    ((const void *)0x0070ACA4U)
#define OPEN_CFW_DISPLAY_RUNTIME_TIMER_CALLBACK_FUNCTION \
    ((const void *)0x0075F3F0U)
#define OPEN_CFW_DISPLAY_RUNTIME_QUEUE_COMMAND8_FUNCTION \
    ((const void *)0x007769DCU)
#define OPEN_CFW_DISPLAY_RUNTIME_QUEUE_SEND_FAILED \
    ((const void *)0x007492CCU)
#define OPEN_CFW_DISPLAY_RUNTIME_QUEUE_SEND_BACKEND \
    ((const void *)0x0071438CU)

static __attribute__((always_inline)) inline int
open_cfw_display_runtime_backend_log_enabled(void)
{
    if ((OPEN_CFW_DISPLAY_RUNTIME_LOG_FLAGS() & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_DISPLAY_RUNTIME_LOG_FLAGS() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_display_runtime_clear_message(unsigned int message[9])
{
    unsigned int index;

    for (index = 0U; index < 9U; index += 1U) {
        message[index] = 0U;
    }
}

static __attribute__((always_inline)) inline void
open_cfw_display_runtime_log_queue_failure(
    const void *function,
    unsigned int line
)
{
    if ((OPEN_CFW_DISPLAY_RUNTIME_LOG_FLAGS() & 2U) != 0U) {
        OPEN_CFW_DISPLAY_RUNTIME_LOG(
            2U,
            OPEN_CFW_DISPLAY_RUNTIME_TAG,
            OPEN_CFW_DISPLAY_RUNTIME_FILE,
            function,
            line,
            OPEN_CFW_DISPLAY_RUNTIME_QUEUE_SEND_FAILED
        );
    }
    if (open_cfw_display_runtime_backend_log_enabled()) {
        OPEN_CFW_DISPLAY_RUNTIME_BACKEND_LOG(
            0x08000000U,
            OPEN_CFW_DISPLAY_RUNTIME_QUEUE_SEND_BACKEND,
            OPEN_CFW_DISPLAY_RUNTIME_QUEUE_SEND_BACKEND
        );
    }
}

__attribute__((used, noinline))
void open_cfw_display_thread_deinitialize(void)
{
    void *thread = OPEN_CFW_DISPLAY_RUNTIME_THREAD_HANDLE;

    if (thread != (void *)0) {
        OPEN_CFW_DISPLAY_RUNTIME_THREAD_TERMINATE(thread);
        OPEN_CFW_DISPLAY_RUNTIME_THREAD_HANDLE = (void *)0;
    }
}

__attribute__((used, noinline))
void open_cfw_display_resource_acquire(void)
{
    OPEN_CFW_DISPLAY_RUNTIME_RESOURCE_ACQUIRE(12U);
}

__attribute__((used, noinline))
void open_cfw_display_resource_release(void)
{
    OPEN_CFW_DISPLAY_RUNTIME_RESOURCE_RELEASE(12U);
}

__attribute__((used, noinline))
void open_cfw_display_timer_initialize(void)
{
    void *timer = OPEN_CFW_DISPLAY_RUNTIME_TIMER_CREATE(
        OPEN_CFW_DISPLAY_RUNTIME_TIMER_CALLBACK,
        1U,
        (void *)0,
        OPEN_CFW_DISPLAY_RUNTIME_TIMER_ATTRIBUTES
    );

    OPEN_CFW_DISPLAY_RUNTIME_TIMER_HANDLE = timer;
    if (OPEN_CFW_DISPLAY_RUNTIME_TIMER_HANDLE == (void *)0) {
        if ((OPEN_CFW_DISPLAY_RUNTIME_LOG_FLAGS() & 2U) != 0U) {
            OPEN_CFW_DISPLAY_RUNTIME_LOG(
                1U,
                OPEN_CFW_DISPLAY_RUNTIME_TAG,
                OPEN_CFW_DISPLAY_RUNTIME_FILE,
                OPEN_CFW_DISPLAY_RUNTIME_TIMER_INIT_FUNCTION,
                0x9FU,
                OPEN_CFW_DISPLAY_RUNTIME_TIMER_INIT_FAILED
            );
        }
        if (open_cfw_display_runtime_backend_log_enabled()) {
            OPEN_CFW_DISPLAY_RUNTIME_BACKEND_LOG(
                0x04000000U,
                OPEN_CFW_DISPLAY_RUNTIME_TIMER_INIT_BACKEND,
                OPEN_CFW_DISPLAY_RUNTIME_TIMER_INIT_BACKEND
            );
        }
    }
}

__attribute__((used, noinline))
void open_cfw_display_timer_start(void)
{
    (void)OPEN_CFW_DISPLAY_RUNTIME_TIMER_START(
        OPEN_CFW_DISPLAY_RUNTIME_TIMER_HANDLE,
        2000U
    );
}

__attribute__((used, noinline))
void open_cfw_display_timer_stop(void)
{
    (void)OPEN_CFW_DISPLAY_RUNTIME_TIMER_STOP(
        OPEN_CFW_DISPLAY_RUNTIME_TIMER_HANDLE
    );
}

__attribute__((used, noinline))
void open_cfw_display_timer_callback(void *argument)
{
    unsigned int message[9];
    int result;

    (void)argument;
    open_cfw_display_runtime_clear_message(message);
    message[0] = 6U;
    result = OPEN_CFW_DISPLAY_RUNTIME_QUEUE_SEND(
        OPEN_CFW_DISPLAY_RUNTIME_QUEUE_HANDLE,
        message,
        0U,
        1000U
    );
    if (result != 0) {
        open_cfw_display_runtime_log_queue_failure(
            OPEN_CFW_DISPLAY_RUNTIME_TIMER_CALLBACK_FUNCTION,
            0xB5U
        );
    }
}

__attribute__((used, noinline))
int open_cfw_display_queue_command8(unsigned int value)
{
    unsigned int message[9];
    int result;

    open_cfw_display_runtime_clear_message(message);
    message[0] = 8U;
    message[7] = value & 0xFFU;
    result = OPEN_CFW_DISPLAY_RUNTIME_QUEUE_SEND(
        OPEN_CFW_DISPLAY_RUNTIME_QUEUE_HANDLE,
        message,
        0U,
        1000U
    );
    if (result == 0) {
        return 0;
    }
    open_cfw_display_runtime_log_queue_failure(
        OPEN_CFW_DISPLAY_RUNTIME_QUEUE_COMMAND8_FUNCTION,
        0xC1U
    );
    return -1;
}

#undef OPEN_CFW_DISPLAY_RUNTIME_QUEUE_SEND_BACKEND
#undef OPEN_CFW_DISPLAY_RUNTIME_QUEUE_SEND_FAILED
#undef OPEN_CFW_DISPLAY_RUNTIME_QUEUE_COMMAND8_FUNCTION
#undef OPEN_CFW_DISPLAY_RUNTIME_TIMER_CALLBACK_FUNCTION
#undef OPEN_CFW_DISPLAY_RUNTIME_TIMER_INIT_BACKEND
#undef OPEN_CFW_DISPLAY_RUNTIME_TIMER_INIT_FAILED
#undef OPEN_CFW_DISPLAY_RUNTIME_TIMER_INIT_FUNCTION
#undef OPEN_CFW_DISPLAY_RUNTIME_FILE
#undef OPEN_CFW_DISPLAY_RUNTIME_TAG
#undef OPEN_CFW_DISPLAY_RUNTIME_TIMER_ATTRIBUTES
#undef OPEN_CFW_DISPLAY_RUNTIME_TIMER_CALLBACK
#undef OPEN_CFW_DISPLAY_RUNTIME_BACKEND_LOG
#undef OPEN_CFW_DISPLAY_RUNTIME_LOG
#undef OPEN_CFW_DISPLAY_RUNTIME_LOG_FLAGS
#undef OPEN_CFW_DISPLAY_RUNTIME_QUEUE_SEND
#undef OPEN_CFW_DISPLAY_RUNTIME_TIMER_STOP
#undef OPEN_CFW_DISPLAY_RUNTIME_TIMER_START
#undef OPEN_CFW_DISPLAY_RUNTIME_TIMER_CREATE
#undef OPEN_CFW_DISPLAY_RUNTIME_RESOURCE_RELEASE
#undef OPEN_CFW_DISPLAY_RUNTIME_RESOURCE_ACQUIRE
#undef OPEN_CFW_DISPLAY_RUNTIME_THREAD_TERMINATE
#undef OPEN_CFW_DISPLAY_RUNTIME_TIMER_HANDLE
#undef OPEN_CFW_DISPLAY_RUNTIME_QUEUE_HANDLE
#undef OPEN_CFW_DISPLAY_RUNTIME_THREAD_HANDLE
