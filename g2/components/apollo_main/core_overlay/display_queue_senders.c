/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacements for the G2 2.2.6.10 display-driver queue sender family
 * at 0x00473E2E...0x004740FF.
 */

typedef int (*open_cfw_display_sender_queue_send_fn)(
    void *queue,
    const void *message,
    unsigned int priority,
    unsigned int timeout
);
typedef unsigned int (*open_cfw_display_sender_log_flags_fn)(void);
typedef void (*open_cfw_display_sender_log_fn)(
    unsigned int level,
    const void *tag,
    const void *file,
    const void *function,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_display_sender_backend_log_fn)(
    unsigned int mask,
    const void *format,
    const void *duplicate_format,
    ...
);

#ifndef OPEN_CFW_DISPLAY_SENDER_QUEUE_HANDLE
#define OPEN_CFW_DISPLAY_SENDER_QUEUE_HANDLE \
    (*(void * volatile *)(void *)0x20000664U)
#endif

#ifndef OPEN_CFW_DISPLAY_SENDER_QUEUE_SEND
#define OPEN_CFW_DISPLAY_SENDER_QUEUE_SEND( \
    queue, \
    message, \
    priority, \
    timeout \
) \
    (((open_cfw_display_sender_queue_send_fn)0x00449ABFU)( \
        (queue), \
        (message), \
        (priority), \
        (timeout) \
    ))
#endif

#ifndef OPEN_CFW_DISPLAY_SENDER_LOG_FLAGS
#define OPEN_CFW_DISPLAY_SENDER_LOG_FLAGS() \
    (((open_cfw_display_sender_log_flags_fn)0x0043D0CFU)())
#endif

#ifndef OPEN_CFW_DISPLAY_SENDER_LOG
#define OPEN_CFW_DISPLAY_SENDER_LOG \
    ((open_cfw_display_sender_log_fn)0x0043D575U)
#endif

#ifndef OPEN_CFW_DISPLAY_SENDER_BACKEND_LOG
#define OPEN_CFW_DISPLAY_SENDER_BACKEND_LOG \
    ((open_cfw_display_sender_backend_log_fn)0x0043CE9FU)
#endif

#define OPEN_CFW_DISPLAY_SENDER_TAG ((const void *)0x0077EDC0U)
#define OPEN_CFW_DISPLAY_SENDER_FILE ((const void *)0x006ECB68U)

static __attribute__((always_inline)) inline int
open_cfw_display_sender_backend_log_enabled(void)
{
    if ((OPEN_CFW_DISPLAY_SENDER_LOG_FLAGS() & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_DISPLAY_SENDER_LOG_FLAGS() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_display_sender_clear(unsigned int message[9])
{
    unsigned int index;

    for (index = 0U; index < 9U; index += 1U) {
        message[index] = 0U;
    }
}

static __attribute__((always_inline)) inline int
open_cfw_display_sender_send(const unsigned int message[9])
{
    return OPEN_CFW_DISPLAY_SENDER_QUEUE_SEND(
        OPEN_CFW_DISPLAY_SENDER_QUEUE_HANDLE,
        message,
        0U,
        1000U
    );
}

static __attribute__((always_inline)) inline void
open_cfw_display_sender_log_failure(
    const void *function,
    unsigned int line,
    const void *format,
    const void *backend_format
)
{
    if ((OPEN_CFW_DISPLAY_SENDER_LOG_FLAGS() & 2U) != 0U) {
        OPEN_CFW_DISPLAY_SENDER_LOG(
            2U,
            OPEN_CFW_DISPLAY_SENDER_TAG,
            OPEN_CFW_DISPLAY_SENDER_FILE,
            function,
            line,
            format
        );
    }
    if (open_cfw_display_sender_backend_log_enabled()) {
        OPEN_CFW_DISPLAY_SENDER_BACKEND_LOG(
            0x08000000U,
            backend_format,
            backend_format
        );
    }
}

__attribute__((used, noinline))
void open_cfw_display_clear_screen(void)
{
    unsigned int message[9];

    open_cfw_display_sender_clear(message);
    message[0] = 2U;
    if (open_cfw_display_sender_send(message) != 0) {
        open_cfw_display_sender_log_failure(
            (const void *)0x0075F430U,
            0x127U,
            (const void *)0x00702080U,
            (const void *)0x006E2E88U
        );
    }
}

__attribute__((used, noinline))
void open_cfw_display_initialize_async(void)
{
    unsigned int message[9];

    open_cfw_display_sender_clear(message);
    message[0] = 1U;
    if (open_cfw_display_sender_send(message) != 0) {
        open_cfw_display_sender_log_failure(
            (const void *)0x00776A0CU,
            0x131U,
            (const void *)0x007143C8U,
            (const void *)0x006ECBB8U
        );
    }
}

__attribute__((used, noinline))
void open_cfw_display_power_up(void)
{
    unsigned int message[9];

    open_cfw_display_sender_clear(message);
    message[0] = 0U;
    if (open_cfw_display_sender_send(message) != 0) {
        open_cfw_display_sender_log_failure(
            (const void *)0x0076AE8CU,
            0x13BU,
            (const void *)0x0070ACE4U,
            (const void *)0x006E75DCU
        );
    }
}

__attribute__((used, noinline))
void open_cfw_display_power_down(void)
{
    unsigned int message[9];

    open_cfw_display_sender_clear(message);
    message[0] = 5U;
    if (open_cfw_display_sender_send(message) != 0) {
        open_cfw_display_sender_log_failure(
            (const void *)0x0076AEA8U,
            0x145U,
            (const void *)0x007020C4U,
            (const void *)0x006E2EE0U
        );
    }
}

__attribute__((used, noinline))
void open_cfw_display_brightness_control(unsigned int value)
{
    unsigned int message[9];

    open_cfw_display_sender_clear(message);
    message[0] = 4U;
    message[7] = value;
    if (open_cfw_display_sender_send(message) != 0) {
        open_cfw_display_sender_log_failure(
            (const void *)0x0075F450U,
            0x150U,
            (const void *)0x00702108U,
            (const void *)0x006E2F38U
        );
    }
}

__attribute__((used, noinline))
int open_cfw_display_send_reflash(
    unsigned int word1,
    unsigned int word2,
    unsigned int word3,
    unsigned int word4,
    unsigned int word5,
    unsigned int word6
)
{
    unsigned int message[9];

    open_cfw_display_sender_clear(message);
    message[0] = 3U;
    message[1] = word1;
    message[2] = word2;
    message[3] = word3;
    message[4] = word4;
    message[5] = word5;
    message[6] = word6;
    if (open_cfw_display_sender_send(message) == 0) {
        return 0;
    }
    open_cfw_display_sender_log_failure(
        (const void *)0x00776A24U,
        0x161U,
        (const void *)0x00733194U,
        (const void *)0x0070214CU
    );
    return -1;
}

#undef OPEN_CFW_DISPLAY_SENDER_FILE
#undef OPEN_CFW_DISPLAY_SENDER_TAG
#undef OPEN_CFW_DISPLAY_SENDER_BACKEND_LOG
#undef OPEN_CFW_DISPLAY_SENDER_LOG
#undef OPEN_CFW_DISPLAY_SENDER_LOG_FLAGS
#undef OPEN_CFW_DISPLAY_SENDER_QUEUE_SEND
#undef OPEN_CFW_DISPLAY_SENDER_QUEUE_HANDLE
