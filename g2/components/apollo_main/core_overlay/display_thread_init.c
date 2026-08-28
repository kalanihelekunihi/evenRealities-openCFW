/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacements for the G2 2.2.6.10 display-driver thread and message
 * queue initializers at 0x00473952...0x00473AA3.
 */

typedef void (*open_cfw_display_thread_entry_fn)(void *argument);
typedef void *(*open_cfw_display_thread_create_fn)(
    open_cfw_display_thread_entry_fn entry,
    void *argument,
    const void *attributes
);
typedef unsigned int (*open_cfw_display_thread_log_flags_fn)(void);
typedef void *(*open_cfw_display_queue_create_fn)(
    unsigned int message_count,
    unsigned int message_size,
    const void *attributes
);
typedef void (*open_cfw_display_thread_log_fn)(
    unsigned int level,
    const void *tag,
    const void *file,
    const void *function,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_display_thread_backend_log_fn)(
    unsigned int mask,
    const void *format,
    const void *duplicate_format,
    ...
);

#ifndef OPEN_CFW_DISPLAY_THREAD_HANDLE
#define OPEN_CFW_DISPLAY_THREAD_HANDLE \
    (*(void * volatile *)(void *)0x20000660U)
#endif

#ifndef OPEN_CFW_DISPLAY_THREAD_CREATE
#define OPEN_CFW_DISPLAY_THREAD_CREATE(entry, argument, attributes) \
    (((open_cfw_display_thread_create_fn)0x004490E3U)( \
        (entry), \
        (argument), \
        (attributes) \
    ))
#endif

#ifndef OPEN_CFW_DISPLAY_THREAD_LOG_FLAGS
#define OPEN_CFW_DISPLAY_THREAD_LOG_FLAGS() \
    (((open_cfw_display_thread_log_flags_fn)0x0043D0CFU)())
#endif

#ifndef OPEN_CFW_DISPLAY_QUEUE_HANDLE
#define OPEN_CFW_DISPLAY_QUEUE_HANDLE \
    (*(void * volatile *)(void *)0x20000664U)
#endif

#ifndef OPEN_CFW_DISPLAY_QUEUE_CREATE
#define OPEN_CFW_DISPLAY_QUEUE_CREATE(count, size, attributes) \
    (((open_cfw_display_queue_create_fn)0x00449A33U)( \
        (count), \
        (size), \
        (attributes) \
    ))
#endif

#ifndef OPEN_CFW_DISPLAY_THREAD_LOG
#define OPEN_CFW_DISPLAY_THREAD_LOG \
    ((open_cfw_display_thread_log_fn)0x0043D575U)
#endif

#ifndef OPEN_CFW_DISPLAY_THREAD_BACKEND_LOG
#define OPEN_CFW_DISPLAY_THREAD_BACKEND_LOG \
    ((open_cfw_display_thread_backend_log_fn)0x0043CE9FU)
#endif

#define OPEN_CFW_DISPLAY_THREAD_ENTRY \
    ((open_cfw_display_thread_entry_fn)0x00473C45U)
#define OPEN_CFW_DISPLAY_THREAD_ATTRIBUTES ((const void *)0x0075381CU)
#define OPEN_CFW_DISPLAY_THREAD_TAG ((const void *)0x0077EDC0U)
#define OPEN_CFW_DISPLAY_THREAD_FILE ((const void *)0x006ECB68U)
#define OPEN_CFW_DISPLAY_THREAD_FUNCTION ((const void *)0x00785B10U)
#define OPEN_CFW_DISPLAY_THREAD_CREATE_FAILED ((const void *)0x007537B0U)
#define OPEN_CFW_DISPLAY_THREAD_CREATED ((const void *)0x0073DF54U)
#define OPEN_CFW_DISPLAY_THREAD_BACKEND_FAILED ((const void *)0x0071DE68U)
#define OPEN_CFW_DISPLAY_THREAD_BACKEND_CREATED ((const void *)0x0070AC64U)
#define OPEN_CFW_DISPLAY_QUEUE_ATTRIBUTES ((const void *)0x2000067CU)
#define OPEN_CFW_DISPLAY_QUEUE_FUNCTION ((const void *)0x007769C4U)
#define OPEN_CFW_DISPLAY_QUEUE_CREATE_FAILED ((const void *)0x00733164U)
#define OPEN_CFW_DISPLAY_QUEUE_CREATED ((const void *)0x0073DF80U)
#define OPEN_CFW_DISPLAY_QUEUE_BACKEND_FAILED ((const void *)0x0070203CU)
#define OPEN_CFW_DISPLAY_QUEUE_BACKEND_CREATED ((const void *)0x006F2F74U)

static __attribute__((always_inline)) inline int
open_cfw_display_thread_backend_log_enabled(void)
{
    if ((OPEN_CFW_DISPLAY_THREAD_LOG_FLAGS() & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_DISPLAY_THREAD_LOG_FLAGS() & 4U) != 0U;
}

__attribute__((used, noinline))
void open_cfw_display_thread_initialize(void)
{
    void *thread = OPEN_CFW_DISPLAY_THREAD_CREATE(
        OPEN_CFW_DISPLAY_THREAD_ENTRY,
        (void *)0,
        OPEN_CFW_DISPLAY_THREAD_ATTRIBUTES
    );

    OPEN_CFW_DISPLAY_THREAD_HANDLE = thread;
    if (OPEN_CFW_DISPLAY_THREAD_HANDLE == (void *)0) {
        if ((OPEN_CFW_DISPLAY_THREAD_LOG_FLAGS() & 2U) != 0U) {
            OPEN_CFW_DISPLAY_THREAD_LOG(
                1U,
                OPEN_CFW_DISPLAY_THREAD_TAG,
                OPEN_CFW_DISPLAY_THREAD_FILE,
                OPEN_CFW_DISPLAY_THREAD_FUNCTION,
                0x64U,
                OPEN_CFW_DISPLAY_THREAD_CREATE_FAILED
            );
        }
        if (open_cfw_display_thread_backend_log_enabled()) {
            OPEN_CFW_DISPLAY_THREAD_BACKEND_LOG(
                0x04000000U,
                OPEN_CFW_DISPLAY_THREAD_BACKEND_FAILED,
                OPEN_CFW_DISPLAY_THREAD_BACKEND_FAILED
            );
        }
        return;
    }

    if ((OPEN_CFW_DISPLAY_THREAD_LOG_FLAGS() & 2U) != 0U) {
        OPEN_CFW_DISPLAY_THREAD_LOG(
            4U,
            OPEN_CFW_DISPLAY_THREAD_TAG,
            OPEN_CFW_DISPLAY_THREAD_FILE,
            OPEN_CFW_DISPLAY_THREAD_FUNCTION,
            0x66U,
            OPEN_CFW_DISPLAY_THREAD_CREATED,
            OPEN_CFW_DISPLAY_THREAD_HANDLE
        );
    }
    if (open_cfw_display_thread_backend_log_enabled()) {
        OPEN_CFW_DISPLAY_THREAD_BACKEND_LOG(
            0x10400000U,
            OPEN_CFW_DISPLAY_THREAD_BACKEND_CREATED,
            OPEN_CFW_DISPLAY_THREAD_BACKEND_CREATED,
            OPEN_CFW_DISPLAY_THREAD_HANDLE
        );
    }
}

__attribute__((used, noinline))
void open_cfw_display_queue_initialize(void)
{
    void *queue = OPEN_CFW_DISPLAY_QUEUE_CREATE(
        0x60U,
        0x24U,
        OPEN_CFW_DISPLAY_QUEUE_ATTRIBUTES
    );

    OPEN_CFW_DISPLAY_QUEUE_HANDLE = queue;
    if (OPEN_CFW_DISPLAY_QUEUE_HANDLE == (void *)0) {
        if ((OPEN_CFW_DISPLAY_THREAD_LOG_FLAGS() & 2U) != 0U) {
            OPEN_CFW_DISPLAY_THREAD_LOG(
                1U,
                OPEN_CFW_DISPLAY_THREAD_TAG,
                OPEN_CFW_DISPLAY_THREAD_FILE,
                OPEN_CFW_DISPLAY_QUEUE_FUNCTION,
                0x6EU,
                OPEN_CFW_DISPLAY_QUEUE_CREATE_FAILED
            );
        }
        if (open_cfw_display_thread_backend_log_enabled()) {
            OPEN_CFW_DISPLAY_THREAD_BACKEND_LOG(
                0x04000000U,
                OPEN_CFW_DISPLAY_QUEUE_BACKEND_FAILED,
                OPEN_CFW_DISPLAY_QUEUE_BACKEND_FAILED
            );
        }
        return;
    }

    if ((OPEN_CFW_DISPLAY_THREAD_LOG_FLAGS() & 2U) != 0U) {
        OPEN_CFW_DISPLAY_THREAD_LOG(
            4U,
            OPEN_CFW_DISPLAY_THREAD_TAG,
            OPEN_CFW_DISPLAY_THREAD_FILE,
            OPEN_CFW_DISPLAY_QUEUE_FUNCTION,
            0x70U,
            OPEN_CFW_DISPLAY_QUEUE_CREATED,
            OPEN_CFW_DISPLAY_QUEUE_HANDLE
        );
    }
    if (open_cfw_display_thread_backend_log_enabled()) {
        OPEN_CFW_DISPLAY_THREAD_BACKEND_LOG(
            0x10400000U,
            OPEN_CFW_DISPLAY_QUEUE_BACKEND_CREATED,
            OPEN_CFW_DISPLAY_QUEUE_BACKEND_CREATED,
            OPEN_CFW_DISPLAY_QUEUE_HANDLE
        );
    }
}

#undef OPEN_CFW_DISPLAY_QUEUE_BACKEND_CREATED
#undef OPEN_CFW_DISPLAY_QUEUE_BACKEND_FAILED
#undef OPEN_CFW_DISPLAY_QUEUE_CREATED
#undef OPEN_CFW_DISPLAY_QUEUE_CREATE_FAILED
#undef OPEN_CFW_DISPLAY_QUEUE_FUNCTION
#undef OPEN_CFW_DISPLAY_QUEUE_ATTRIBUTES
#undef OPEN_CFW_DISPLAY_THREAD_BACKEND_CREATED
#undef OPEN_CFW_DISPLAY_THREAD_BACKEND_FAILED
#undef OPEN_CFW_DISPLAY_THREAD_CREATED
#undef OPEN_CFW_DISPLAY_THREAD_CREATE_FAILED
#undef OPEN_CFW_DISPLAY_THREAD_FUNCTION
#undef OPEN_CFW_DISPLAY_THREAD_FILE
#undef OPEN_CFW_DISPLAY_THREAD_TAG
#undef OPEN_CFW_DISPLAY_THREAD_ATTRIBUTES
#undef OPEN_CFW_DISPLAY_THREAD_ENTRY
#undef OPEN_CFW_DISPLAY_THREAD_BACKEND_LOG
#undef OPEN_CFW_DISPLAY_THREAD_LOG
#undef OPEN_CFW_DISPLAY_QUEUE_CREATE
#undef OPEN_CFW_DISPLAY_QUEUE_HANDLE
#undef OPEN_CFW_DISPLAY_THREAD_LOG_FLAGS
#undef OPEN_CFW_DISPLAY_THREAD_CREATE
#undef OPEN_CFW_DISPLAY_THREAD_HANDLE
