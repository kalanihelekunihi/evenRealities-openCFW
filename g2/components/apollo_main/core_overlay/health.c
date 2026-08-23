/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room reconstruction of the G2 health mutex and common-event object.
 * The authenticated stock control flow and provider addresses are documented
 * in docs/research/g2-health-recovery.md.
 */

#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_HEALTH_MUTEX_CELL
#define OPEN_CFW_HEALTH_MUTEX_CELL \
    (*(void *volatile *)(uintptr_t)0x20074658U)
#endif

#ifndef OPEN_CFW_HEALTH_MUTEX_NEW
void *open_cfw_cmsis_mutex_new(const void *attributes);
#define OPEN_CFW_HEALTH_MUTEX_NEW(attributes) \
    open_cfw_cmsis_mutex_new((attributes))
#endif

#ifndef OPEN_CFW_HEALTH_MUTEX_ACQUIRE
int open_cfw_cmsis_mutex_acquire(void *mutex, uint32_t timeout);
#define OPEN_CFW_HEALTH_MUTEX_ACQUIRE(mutex, timeout) \
    open_cfw_cmsis_mutex_acquire((mutex), (timeout))
#endif

#ifndef OPEN_CFW_HEALTH_MUTEX_RELEASE
int open_cfw_cmsis_mutex_release(void *mutex);
#define OPEN_CFW_HEALTH_MUTEX_RELEASE(mutex) \
    open_cfw_cmsis_mutex_release((mutex))
#endif

#ifndef OPEN_CFW_HEALTH_DATA_HANDLE
unsigned int open_cfw_retained_health_data_handle(
    unsigned char *data,
    unsigned short length
);
#define OPEN_CFW_HEALTH_DATA_HANDLE(data, length) \
    open_cfw_retained_health_data_handle((data), (length))
#endif

#ifndef OPEN_CFW_HEALTH_LENS_SIDE
unsigned int open_cfw_lens_side(void);
#define OPEN_CFW_HEALTH_LENS_SIDE() open_cfw_lens_side()
#endif

#ifndef OPEN_CFW_HEALTH_DISPLAY_RUNNING
unsigned int open_cfw_retained_health_display_running(void);
#define OPEN_CFW_HEALTH_DISPLAY_RUNNING() \
    open_cfw_retained_health_display_running()
#endif

#ifndef OPEN_CFW_HEALTH_DISPLAY_MATCHES
unsigned int open_cfw_retained_health_display_matches(unsigned int state);
#define OPEN_CFW_HEALTH_DISPLAY_MATCHES(state) \
    open_cfw_retained_health_display_matches((state))
#endif

#ifndef OPEN_CFW_HEALTH_POST_SERVICE_RECORD
unsigned int open_cfw_retained_health_post_service_record(
    unsigned int service,
    const unsigned char *record,
    unsigned int length,
    unsigned int flags
);
#define OPEN_CFW_HEALTH_POST_SERVICE_RECORD(service, record, length, flags) \
    open_cfw_retained_health_post_service_record( \
        (service), (record), (length), (flags))
#endif

#define OPEN_CFW_HEALTH_WAIT_FOREVER UINT32_MAX
#define OPEN_CFW_HEALTH_EVENT_DATA 0U
#define OPEN_CFW_HEALTH_EVENT_COMMON 5U
#define OPEN_CFW_HEALTH_COMMAND_ACCEPT 1U

int open_cfw_health_data_mutex_init(void);

/* ABI-compatible replacement for stock [0x004FFBD8,0x004FFC32). */
#if !defined(OPEN_CFW_HEALTH_LOCK_ONLY) && \
    !defined(OPEN_CFW_HEALTH_UNLOCK_ONLY) && \
    !defined(OPEN_CFW_HEALTH_HANDLER_ONLY)
__attribute__((used, noinline))
int open_cfw_health_data_mutex_init(void)
{
    if (OPEN_CFW_HEALTH_MUTEX_CELL != NULL) {
        return 0;
    }

    OPEN_CFW_HEALTH_MUTEX_CELL = OPEN_CFW_HEALTH_MUTEX_NEW(NULL);
    return OPEN_CFW_HEALTH_MUTEX_CELL != NULL ? 0 : -1;
}
#endif

/* ABI-compatible replacement for stock [0x004FFC32,0x004FFC90). */
#if !defined(OPEN_CFW_HEALTH_INIT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_UNLOCK_ONLY) && \
    !defined(OPEN_CFW_HEALTH_HANDLER_ONLY)
__attribute__((used, noinline))
unsigned int open_cfw_health_lock_storage(void)
{
    void *mutex = OPEN_CFW_HEALTH_MUTEX_CELL;

    if (mutex == NULL) {
        return 0U;
    }
    return OPEN_CFW_HEALTH_MUTEX_ACQUIRE(
        mutex,
        OPEN_CFW_HEALTH_WAIT_FOREVER
    ) == 0 ? 1U : 0U;
}
#endif

/* ABI-compatible replacement for stock [0x004FFC90,0x004FFCA2). */
#if !defined(OPEN_CFW_HEALTH_INIT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_LOCK_ONLY) && \
    !defined(OPEN_CFW_HEALTH_HANDLER_ONLY)
__attribute__((used, noinline))
void open_cfw_health_unlock_storage(void)
{
    void *mutex = OPEN_CFW_HEALTH_MUTEX_CELL;

    if (mutex != NULL) {
        (void)OPEN_CFW_HEALTH_MUTEX_RELEASE(mutex);
    }
}
#endif

/*
 * ABI-compatible replacement for stock [0x004FFCA2,0x004FFDD0).
 *
 * Event zero forwards the payload to the retained health schema/policy
 * provider. A successful master-side update is acknowledged only while the
 * display is running in the required state. Event five accepts command byte
 * one; other common commands and event types are deliberately side-effect
 * free. Diagnostic logging is not part of the functional state transition.
 */
#if !defined(OPEN_CFW_HEALTH_INIT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_LOCK_ONLY) && \
    !defined(OPEN_CFW_HEALTH_UNLOCK_ONLY)
__attribute__((used, noinline))
unsigned int open_cfw_health_common_data_handler(
    unsigned int event_type,
    unsigned char *data,
    unsigned int length
)
{
    unsigned char response[6];
    volatile unsigned char *response_writer = response;

    response_writer[0] = 6U;
    response_writer[1] = 0U;
    response_writer[2] = 0U;
    response_writer[3] = 0U;
    response_writer[4] = 0U;
    response_writer[5] = 0U;

    (void)open_cfw_health_data_mutex_init();

    if (event_type == OPEN_CFW_HEALTH_EVENT_DATA) {
        if (
            OPEN_CFW_HEALTH_DATA_HANDLE(data, (unsigned short)length) == 0U &&
            OPEN_CFW_HEALTH_LENS_SIDE() == 1U &&
            OPEN_CFW_HEALTH_DISPLAY_RUNNING() == 1U &&
            OPEN_CFW_HEALTH_DISPLAY_MATCHES(1U) == 1U
        ) {
            (void)OPEN_CFW_HEALTH_POST_SERVICE_RECORD(
                1U,
                response,
                (unsigned int)sizeof(response),
                0U
            );
        }
        return 0U;
    }

    if (event_type == OPEN_CFW_HEALTH_EVENT_COMMON) {
        if (data == NULL || length == 0U) {
            return 0U;
        }
        if (data[0] == OPEN_CFW_HEALTH_COMMAND_ACCEPT) {
            return 0U;
        }
    }

    return 0U;
}
#endif
