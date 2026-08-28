/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacements for the G2 2.2.6.10 forced display-driver lifecycle
 * routines at 0x00474100...0x004742F7 and 0x0047432C...0x00474473.
 */

typedef int (*open_cfw_display_lifecycle_running_fn)(void);
typedef int (*open_cfw_display_lifecycle_queue_send_fn)(
    void *queue,
    const void *message,
    unsigned int priority,
    unsigned int timeout
);
typedef unsigned int (*open_cfw_display_lifecycle_log_flags_fn)(void);
typedef void (*open_cfw_display_lifecycle_log_fn)(
    unsigned int level,
    const void *tag,
    const void *file,
    const void *function,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_display_lifecycle_backend_log_fn)(
    unsigned int mask,
    const void *format,
    const void *duplicate_format,
    ...
);

#ifndef OPEN_CFW_DISPLAY_LIFECYCLE_ACTIVE
#define OPEN_CFW_DISPLAY_LIFECYCLE_ACTIVE \
    (*(volatile unsigned int *)(void *)0x200744ECU)
#endif

#ifndef OPEN_CFW_DISPLAY_LIFECYCLE_QUEUE_HANDLE
#define OPEN_CFW_DISPLAY_LIFECYCLE_QUEUE_HANDLE \
    (*(void * volatile *)(void *)0x20000664U)
#endif

#ifndef OPEN_CFW_DISPLAY_LIFECYCLE_RUNNING
#define OPEN_CFW_DISPLAY_LIFECYCLE_RUNNING() \
    (((open_cfw_display_lifecycle_running_fn)0x00443485U)())
#endif

#ifndef OPEN_CFW_DISPLAY_LIFECYCLE_QUEUE_SEND
#define OPEN_CFW_DISPLAY_LIFECYCLE_QUEUE_SEND( \
    queue, \
    message, \
    priority, \
    timeout \
) \
    (((open_cfw_display_lifecycle_queue_send_fn)0x00449ABFU)( \
        (queue), \
        (message), \
        (priority), \
        (timeout) \
    ))
#endif

#ifndef OPEN_CFW_DISPLAY_LIFECYCLE_LOG_FLAGS
#define OPEN_CFW_DISPLAY_LIFECYCLE_LOG_FLAGS() \
    (((open_cfw_display_lifecycle_log_flags_fn)0x0043D0CFU)())
#endif

#ifndef OPEN_CFW_DISPLAY_LIFECYCLE_LOG
#define OPEN_CFW_DISPLAY_LIFECYCLE_LOG \
    ((open_cfw_display_lifecycle_log_fn)0x0043D575U)
#endif

#ifndef OPEN_CFW_DISPLAY_LIFECYCLE_BACKEND_LOG
#define OPEN_CFW_DISPLAY_LIFECYCLE_BACKEND_LOG \
    ((open_cfw_display_lifecycle_backend_log_fn)0x0043CE9FU)
#endif

#define OPEN_CFW_DISPLAY_LIFECYCLE_TAG ((const void *)0x0077EDC0U)
#define OPEN_CFW_DISPLAY_LIFECYCLE_FILE ((const void *)0x006ECB68U)

#define OPEN_CFW_DISPLAY_INIT_FUNCTION ((const void *)0x0075F470U)
#define OPEN_CFW_DISPLAY_INIT_ALREADY_ACTIVE ((const void *)0x0071DF10U)
#define OPEN_CFW_DISPLAY_INIT_ALREADY_ACTIVE_BACKEND \
    ((const void *)0x006F2FC0U)
#define OPEN_CFW_DISPLAY_INIT_NOT_RUNNING ((const void *)0x007537F8U)
#define OPEN_CFW_DISPLAY_INIT_NOT_RUNNING_BACKEND \
    ((const void *)0x0071DF48U)
#define OPEN_CFW_DISPLAY_INIT_STARTED ((const void *)0x0075F490U)
#define OPEN_CFW_DISPLAY_INIT_STARTED_BACKEND ((const void *)0x00728AFCU)
#define OPEN_CFW_DISPLAY_INIT_POWER_UP_FAILED ((const void *)0x0070ACE4U)
#define OPEN_CFW_DISPLAY_INIT_POWER_UP_FAILED_BACKEND \
    ((const void *)0x006E75DCU)
#define OPEN_CFW_DISPLAY_INIT_DEVICE_FAILED ((const void *)0x00714404U)
#define OPEN_CFW_DISPLAY_INIT_DEVICE_FAILED_BACKEND \
    ((const void *)0x006ECC08U)
#define OPEN_CFW_DISPLAY_INIT_REFLASH_FAILED ((const void *)0x00733194U)
#define OPEN_CFW_DISPLAY_INIT_REFLASH_FAILED_BACKEND \
    ((const void *)0x0070214CU)

#define OPEN_CFW_DISPLAY_DEINIT_FUNCTION ((const void *)0x0075F4B0U)
#define OPEN_CFW_DISPLAY_DEINIT_ALREADY_INACTIVE ((const void *)0x0071DF80U)
#define OPEN_CFW_DISPLAY_DEINIT_ALREADY_INACTIVE_BACKEND \
    ((const void *)0x006F300CU)
#define OPEN_CFW_DISPLAY_DEINIT_STARTED ((const void *)0x0075F4D0U)
#define OPEN_CFW_DISPLAY_DEINIT_STARTED_BACKEND ((const void *)0x00728B30U)
#define OPEN_CFW_DISPLAY_DEINIT_CLEAR_FAILED ((const void *)0x00702190U)
#define OPEN_CFW_DISPLAY_DEINIT_CLEAR_FAILED_BACKEND \
    ((const void *)0x006E2F90U)
#define OPEN_CFW_DISPLAY_DEINIT_POWER_DOWN_FAILED ((const void *)0x007020C4U)
#define OPEN_CFW_DISPLAY_DEINIT_POWER_DOWN_FAILED_BACKEND \
    ((const void *)0x006E2EE0U)

static __attribute__((always_inline)) inline int
open_cfw_display_lifecycle_backend_log_enabled(void)
{
    if ((OPEN_CFW_DISPLAY_LIFECYCLE_LOG_FLAGS() & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_DISPLAY_LIFECYCLE_LOG_FLAGS() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_display_lifecycle_log(
    unsigned int level,
    const void *function,
    unsigned int line,
    const void *format,
    unsigned int backend_mask,
    const void *backend_format
)
{
    if ((OPEN_CFW_DISPLAY_LIFECYCLE_LOG_FLAGS() & 2U) != 0U) {
        OPEN_CFW_DISPLAY_LIFECYCLE_LOG(
            level,
            OPEN_CFW_DISPLAY_LIFECYCLE_TAG,
            OPEN_CFW_DISPLAY_LIFECYCLE_FILE,
            function,
            line,
            format
        );
    }
    if (open_cfw_display_lifecycle_backend_log_enabled()) {
        OPEN_CFW_DISPLAY_LIFECYCLE_BACKEND_LOG(
            backend_mask,
            backend_format,
            backend_format
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_display_lifecycle_clear(unsigned int message[9])
{
    unsigned int index;

    for (index = 0U; index < 9U; index += 1U) {
        message[index] = 0U;
    }
}

static __attribute__((always_inline)) inline int
open_cfw_display_lifecycle_send(const unsigned int message[9])
{
    return OPEN_CFW_DISPLAY_LIFECYCLE_QUEUE_SEND(
        OPEN_CFW_DISPLAY_LIFECYCLE_QUEUE_HANDLE,
        message,
        0U,
        1000U
    );
}

__attribute__((used, noinline))
int open_cfw_display_initialize_force(void)
{
    unsigned int message[9];

    if (OPEN_CFW_DISPLAY_LIFECYCLE_ACTIVE != 0U) {
        open_cfw_display_lifecycle_log(
            4U,
            OPEN_CFW_DISPLAY_INIT_FUNCTION,
            0x16AU,
            OPEN_CFW_DISPLAY_INIT_ALREADY_ACTIVE,
            0x10000000U,
            OPEN_CFW_DISPLAY_INIT_ALREADY_ACTIVE_BACKEND
        );
        return 0;
    }
    if (OPEN_CFW_DISPLAY_LIFECYCLE_RUNNING() == 0) {
        open_cfw_display_lifecycle_log(
            3U,
            OPEN_CFW_DISPLAY_INIT_FUNCTION,
            0x170U,
            OPEN_CFW_DISPLAY_INIT_NOT_RUNNING,
            0x0C000000U,
            OPEN_CFW_DISPLAY_INIT_NOT_RUNNING_BACKEND
        );
        return 0;
    }

    open_cfw_display_lifecycle_log(
        3U,
        OPEN_CFW_DISPLAY_INIT_FUNCTION,
        0x174U,
        OPEN_CFW_DISPLAY_INIT_STARTED,
        0x0C000000U,
        OPEN_CFW_DISPLAY_INIT_STARTED_BACKEND
    );
    open_cfw_display_lifecycle_clear(message);
    message[8] = 1U;
    message[0] = 0U;
    if (open_cfw_display_lifecycle_send(message) != 0) {
        open_cfw_display_lifecycle_log(
            2U,
            OPEN_CFW_DISPLAY_INIT_FUNCTION,
            0x17CU,
            OPEN_CFW_DISPLAY_INIT_POWER_UP_FAILED,
            0x08000000U,
            OPEN_CFW_DISPLAY_INIT_POWER_UP_FAILED_BACKEND
        );
        return -1;
    }
    message[0] = 1U;
    if (open_cfw_display_lifecycle_send(message) != 0) {
        open_cfw_display_lifecycle_log(
            2U,
            OPEN_CFW_DISPLAY_INIT_FUNCTION,
            0x182U,
            OPEN_CFW_DISPLAY_INIT_DEVICE_FAILED,
            0x08000000U,
            OPEN_CFW_DISPLAY_INIT_DEVICE_FAILED_BACKEND
        );
        return -1;
    }
    message[0] = 3U;
    if (open_cfw_display_lifecycle_send(message) != 0) {
        open_cfw_display_lifecycle_log(
            2U,
            OPEN_CFW_DISPLAY_INIT_FUNCTION,
            0x188U,
            OPEN_CFW_DISPLAY_INIT_REFLASH_FAILED,
            0x08000000U,
            OPEN_CFW_DISPLAY_INIT_REFLASH_FAILED_BACKEND
        );
        return -1;
    }
    return 0;
}

__attribute__((used, noinline))
int open_cfw_display_deinitialize_force(void)
{
    unsigned int message[9];

    if (OPEN_CFW_DISPLAY_LIFECYCLE_ACTIVE == 0U) {
        open_cfw_display_lifecycle_log(
            4U,
            OPEN_CFW_DISPLAY_DEINIT_FUNCTION,
            0x191U,
            OPEN_CFW_DISPLAY_DEINIT_ALREADY_INACTIVE,
            0x10000000U,
            OPEN_CFW_DISPLAY_DEINIT_ALREADY_INACTIVE_BACKEND
        );
        return 0;
    }

    open_cfw_display_lifecycle_log(
        3U,
        OPEN_CFW_DISPLAY_DEINIT_FUNCTION,
        0x194U,
        OPEN_CFW_DISPLAY_DEINIT_STARTED,
        0x0C000000U,
        OPEN_CFW_DISPLAY_DEINIT_STARTED_BACKEND
    );
    open_cfw_display_lifecycle_clear(message);
    message[8] = 1U;
    message[0] = 2U;
    if (open_cfw_display_lifecycle_send(message) != 0) {
        open_cfw_display_lifecycle_log(
            2U,
            OPEN_CFW_DISPLAY_DEINIT_FUNCTION,
            0x19BU,
            OPEN_CFW_DISPLAY_DEINIT_CLEAR_FAILED,
            0x08000000U,
            OPEN_CFW_DISPLAY_DEINIT_CLEAR_FAILED_BACKEND
        );
        return -1;
    }
    message[0] = 5U;
    if (open_cfw_display_lifecycle_send(message) != 0) {
        open_cfw_display_lifecycle_log(
            2U,
            OPEN_CFW_DISPLAY_DEINIT_FUNCTION,
            0x1A1U,
            OPEN_CFW_DISPLAY_DEINIT_POWER_DOWN_FAILED,
            0x08000000U,
            OPEN_CFW_DISPLAY_DEINIT_POWER_DOWN_FAILED_BACKEND
        );
        return -1;
    }
    return 0;
}

#undef OPEN_CFW_DISPLAY_DEINIT_POWER_DOWN_FAILED_BACKEND
#undef OPEN_CFW_DISPLAY_DEINIT_POWER_DOWN_FAILED
#undef OPEN_CFW_DISPLAY_DEINIT_CLEAR_FAILED_BACKEND
#undef OPEN_CFW_DISPLAY_DEINIT_CLEAR_FAILED
#undef OPEN_CFW_DISPLAY_DEINIT_STARTED_BACKEND
#undef OPEN_CFW_DISPLAY_DEINIT_STARTED
#undef OPEN_CFW_DISPLAY_DEINIT_ALREADY_INACTIVE_BACKEND
#undef OPEN_CFW_DISPLAY_DEINIT_ALREADY_INACTIVE
#undef OPEN_CFW_DISPLAY_DEINIT_FUNCTION
#undef OPEN_CFW_DISPLAY_INIT_REFLASH_FAILED_BACKEND
#undef OPEN_CFW_DISPLAY_INIT_REFLASH_FAILED
#undef OPEN_CFW_DISPLAY_INIT_DEVICE_FAILED_BACKEND
#undef OPEN_CFW_DISPLAY_INIT_DEVICE_FAILED
#undef OPEN_CFW_DISPLAY_INIT_POWER_UP_FAILED_BACKEND
#undef OPEN_CFW_DISPLAY_INIT_POWER_UP_FAILED
#undef OPEN_CFW_DISPLAY_INIT_STARTED_BACKEND
#undef OPEN_CFW_DISPLAY_INIT_STARTED
#undef OPEN_CFW_DISPLAY_INIT_NOT_RUNNING_BACKEND
#undef OPEN_CFW_DISPLAY_INIT_NOT_RUNNING
#undef OPEN_CFW_DISPLAY_INIT_ALREADY_ACTIVE_BACKEND
#undef OPEN_CFW_DISPLAY_INIT_ALREADY_ACTIVE
#undef OPEN_CFW_DISPLAY_INIT_FUNCTION
#undef OPEN_CFW_DISPLAY_LIFECYCLE_FILE
#undef OPEN_CFW_DISPLAY_LIFECYCLE_TAG
#undef OPEN_CFW_DISPLAY_LIFECYCLE_BACKEND_LOG
#undef OPEN_CFW_DISPLAY_LIFECYCLE_LOG
#undef OPEN_CFW_DISPLAY_LIFECYCLE_LOG_FLAGS
#undef OPEN_CFW_DISPLAY_LIFECYCLE_QUEUE_SEND
#undef OPEN_CFW_DISPLAY_LIFECYCLE_RUNNING
#undef OPEN_CFW_DISPLAY_LIFECYCLE_QUEUE_HANDLE
#undef OPEN_CFW_DISPLAY_LIFECYCLE_ACTIVE
