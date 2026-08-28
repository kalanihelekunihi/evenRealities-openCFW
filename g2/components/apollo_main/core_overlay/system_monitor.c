/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the G2 system-monitor peer-reboot callback.
 * The authenticated stock control flow and provider addresses are documented
 * in docs/research/g2-system-monitor-recovery.md.
 */

#include <stddef.h>
#include <stdint.h>

typedef void (*open_cfw_system_monitor_log_record_fn)(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_system_monitor_trace_record_fn)(
    unsigned int mask,
    const void *schema,
    const void *format,
    ...
);

#ifndef OPEN_CFW_SYSTEM_MONITOR_LOG_FLAGS
unsigned int open_cfw_retained_system_monitor_log_flags(void);
#define OPEN_CFW_SYSTEM_MONITOR_LOG_FLAGS() \
    open_cfw_retained_system_monitor_log_flags()
#endif

#ifndef OPEN_CFW_SYSTEM_MONITOR_LOG_RECORD
void open_cfw_retained_system_monitor_log_record(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *format,
    ...
);
#define OPEN_CFW_SYSTEM_MONITOR_LOG_RECORD \
    open_cfw_retained_system_monitor_log_record
#endif

#ifndef OPEN_CFW_SYSTEM_MONITOR_TRACE_RECORD
void open_cfw_retained_system_monitor_trace_record(
    unsigned int mask,
    const void *schema,
    const void *format,
    ...
);
#define OPEN_CFW_SYSTEM_MONITOR_TRACE_RECORD \
    open_cfw_retained_system_monitor_trace_record
#endif

#ifndef OPEN_CFW_SYSTEM_MONITOR_DISPLAY_RUNNING
unsigned int open_cfw_retained_system_monitor_display_running(void);
#define OPEN_CFW_SYSTEM_MONITOR_DISPLAY_RUNNING() \
    open_cfw_retained_system_monitor_display_running()
#endif

#ifndef OPEN_CFW_SYSTEM_MONITOR_FOREGROUND_RUNNING
unsigned int open_cfw_retained_system_monitor_foreground_running(void);
#define OPEN_CFW_SYSTEM_MONITOR_FOREGROUND_RUNNING() \
    open_cfw_retained_system_monitor_foreground_running()
#endif

#ifndef OPEN_CFW_SYSTEM_MONITOR_BACKGROUND_RUNNING
unsigned int open_cfw_retained_system_monitor_background_running(void);
#define OPEN_CFW_SYSTEM_MONITOR_BACKGROUND_RUNNING() \
    open_cfw_retained_system_monitor_background_running()
#endif

#ifndef OPEN_CFW_SYSTEM_MONITOR_POST_DISPLAY_COMMAND
unsigned int open_cfw_retained_system_monitor_post_display_command(
    unsigned int command,
    unsigned int argument,
    unsigned int length
);
#define OPEN_CFW_SYSTEM_MONITOR_POST_DISPLAY_COMMAND(command, argument, length) \
    open_cfw_retained_system_monitor_post_display_command( \
        (command), (argument), (length))
#endif

#ifndef OPEN_CFW_SYSTEM_MONITOR_DELAY
void open_cfw_freertos_task_delay(unsigned int ticks);
#define OPEN_CFW_SYSTEM_MONITOR_DELAY(ticks) \
    open_cfw_freertos_task_delay((ticks))
#endif

#ifndef OPEN_CFW_SYSTEM_MONITOR_LENS_SIDE
unsigned int open_cfw_lens_side(void);
#define OPEN_CFW_SYSTEM_MONITOR_LENS_SIDE() open_cfw_lens_side()
#endif

#ifndef OPEN_CFW_SYSTEM_MONITOR_SEND_SCHEDULER_IDLE
unsigned int open_cfw_retained_system_monitor_send_scheduler_idle(void);
#define OPEN_CFW_SYSTEM_MONITOR_SEND_SCHEDULER_IDLE() \
    open_cfw_retained_system_monitor_send_scheduler_idle()
#endif

#ifndef OPEN_CFW_SYSTEM_MONITOR_RESET_DASHBOARD
void open_cfw_retained_system_monitor_reset_dashboard(void);
#define OPEN_CFW_SYSTEM_MONITOR_RESET_DASHBOARD() \
    open_cfw_retained_system_monitor_reset_dashboard()
#endif

#ifndef OPEN_CFW_SYSTEM_MONITOR_RESET_APP_STATE
void open_cfw_retained_system_monitor_reset_app_state(unsigned int reason);
#define OPEN_CFW_SYSTEM_MONITOR_RESET_APP_STATE(reason) \
    open_cfw_retained_system_monitor_reset_app_state((reason))
#endif

#ifndef OPEN_CFW_SYSTEM_MONITOR_RESET_ONBOARDING_COLORS
void open_cfw_retained_system_monitor_reset_onboarding_colors(void);
#define OPEN_CFW_SYSTEM_MONITOR_RESET_ONBOARDING_COLORS() \
    open_cfw_retained_system_monitor_reset_onboarding_colors()
#endif

#ifndef OPEN_CFW_SYSTEM_MONITOR_RESET_TERMINAL_STATE
void open_cfw_retained_system_monitor_reset_terminal_state(void);
#define OPEN_CFW_SYSTEM_MONITOR_RESET_TERMINAL_STATE() \
    open_cfw_retained_system_monitor_reset_terminal_state()
#endif

#ifndef OPEN_CFW_SYSTEM_MONITOR_PUBLISH_LENS_STATUS
void open_cfw_lens_status_publish(void);
#define OPEN_CFW_SYSTEM_MONITOR_PUBLISH_LENS_STATUS() \
    open_cfw_lens_status_publish()
#endif

#define OPEN_CFW_SYSTEM_MONITOR_EVENT_COMMON 5U
#define OPEN_CFW_SYSTEM_MONITOR_REBOOT_BYTES 6U
#define OPEN_CFW_SYSTEM_MONITOR_WAIT_TICKS 100U
#define OPEN_CFW_SYSTEM_MONITOR_WAIT_LIMIT 11U

#define OPEN_CFW_SYSTEM_MONITOR_LOG_MODULE ((const void *)0x00789650U)
#define OPEN_CFW_SYSTEM_MONITOR_LOG_FILE ((const void *)0x00706590U)
#define OPEN_CFW_SYSTEM_MONITOR_LOG_FUNCTION ((const void *)0x0075A950U)

#define OPEN_CFW_SYSTEM_MONITOR_EVENT_FORMAT ((const void *)0x0070FA24U)
#define OPEN_CFW_SYSTEM_MONITOR_EVENT_TRACE ((const void *)0x006EFEA8U)
#define OPEN_CFW_SYSTEM_MONITOR_REBOOT_FORMAT ((const void *)0x00738F24U)
#define OPEN_CFW_SYSTEM_MONITOR_REBOOT_TRACE ((const void *)0x0070FA64U)
#define OPEN_CFW_SYSTEM_MONITOR_DISPLAY_FORMAT ((const void *)0x00723B28U)
#define OPEN_CFW_SYSTEM_MONITOR_DISPLAY_TRACE ((const void *)0x006FD814U)
#define OPEN_CFW_SYSTEM_MONITOR_FOREGROUND_FORMAT ((const void *)0x0070FAA4U)
#define OPEN_CFW_SYSTEM_MONITOR_FOREGROUND_TRACE ((const void *)0x006EFEF8U)
#define OPEN_CFW_SYSTEM_MONITOR_BACKGROUND_FORMAT ((const void *)0x0070FAE4U)
#define OPEN_CFW_SYSTEM_MONITOR_BACKGROUND_TRACE ((const void *)0x006EFF48U)
#define OPEN_CFW_SYSTEM_MONITOR_MASTER_FORMAT ((const void *)0x006E5458U)
#define OPEN_CFW_SYSTEM_MONITOR_MASTER_TRACE ((const void *)0x006D9AACU)

static unsigned int open_cfw_system_monitor_trace_enabled(void)
{
    unsigned int flags = OPEN_CFW_SYSTEM_MONITOR_LOG_FLAGS();

    if ((flags & 1U) != 0U) {
        return 1U;
    }
    return (OPEN_CFW_SYSTEM_MONITOR_LOG_FLAGS() & 4U) != 0U;
}

static void open_cfw_system_monitor_message(
    unsigned int level,
    unsigned int line,
    const void *format,
    unsigned int trace_mask,
    const void *trace
)
{
    if ((OPEN_CFW_SYSTEM_MONITOR_LOG_FLAGS() & 2U) != 0U) {
        OPEN_CFW_SYSTEM_MONITOR_LOG_RECORD(
            level,
            OPEN_CFW_SYSTEM_MONITOR_LOG_MODULE,
            OPEN_CFW_SYSTEM_MONITOR_LOG_FILE,
            OPEN_CFW_SYSTEM_MONITOR_LOG_FUNCTION,
            line,
            format
        );
    }
    if (open_cfw_system_monitor_trace_enabled() != 0U) {
        OPEN_CFW_SYSTEM_MONITOR_TRACE_RECORD(trace_mask, trace, trace);
    }
}

/*
 * ABI-compatible replacement for stock [0x00584EE4,0x005850E2).
 *
 * The callback is registered through descriptor word 0x006A4674. Only common
 * event five with the six-byte reboot sentinel performs work. The stock body
 * dereferences six bytes without validating its buffer; this reconstruction
 * deliberately rejects NULL/short records before the sentinel comparison.
 */
__attribute__((used, noinline))
unsigned int open_cfw_system_monitor_common_data_handler(
    unsigned int event_type,
    const unsigned char *data,
    unsigned int length
)
{
    static const unsigned char reboot_sentinel[OPEN_CFW_SYSTEM_MONITOR_REBOOT_BYTES] = {
        0x55U, 0x04U, 0x12U, 0x34U, 0x56U, 0x78U
    };
    unsigned int index;
    unsigned int waits;

    if ((OPEN_CFW_SYSTEM_MONITOR_LOG_FLAGS() & 2U) != 0U) {
        OPEN_CFW_SYSTEM_MONITOR_LOG_RECORD(
            3U,
            OPEN_CFW_SYSTEM_MONITOR_LOG_MODULE,
            OPEN_CFW_SYSTEM_MONITOR_LOG_FILE,
            OPEN_CFW_SYSTEM_MONITOR_LOG_FUNCTION,
            0x30U,
            OPEN_CFW_SYSTEM_MONITOR_EVENT_FORMAT,
            event_type,
            length
        );
    }
    if (open_cfw_system_monitor_trace_enabled() != 0U) {
        OPEN_CFW_SYSTEM_MONITOR_TRACE_RECORD(
            0x0C800000U,
            OPEN_CFW_SYSTEM_MONITOR_EVENT_TRACE,
            OPEN_CFW_SYSTEM_MONITOR_EVENT_TRACE,
            event_type,
            length
        );
    }

    if (
        event_type != OPEN_CFW_SYSTEM_MONITOR_EVENT_COMMON ||
        data == NULL ||
        length < OPEN_CFW_SYSTEM_MONITOR_REBOOT_BYTES
    ) {
        return 0U;
    }
    for (index = 0U; index < OPEN_CFW_SYSTEM_MONITOR_REBOOT_BYTES; ++index) {
        if (data[index] != reboot_sentinel[index]) {
            return 0U;
        }
    }

    open_cfw_system_monitor_message(
        4U, 0x34U, OPEN_CFW_SYSTEM_MONITOR_REBOOT_FORMAT,
        0x10000000U, OPEN_CFW_SYSTEM_MONITOR_REBOOT_TRACE
    );

    if (OPEN_CFW_SYSTEM_MONITOR_DISPLAY_RUNNING() == 1U) {
        open_cfw_system_monitor_message(
            4U, 0x36U, OPEN_CFW_SYSTEM_MONITOR_DISPLAY_FORMAT,
            0x10000000U, OPEN_CFW_SYSTEM_MONITOR_DISPLAY_TRACE
        );
        if (OPEN_CFW_SYSTEM_MONITOR_FOREGROUND_RUNNING() == 1U) {
            open_cfw_system_monitor_message(
                4U, 0x38U, OPEN_CFW_SYSTEM_MONITOR_FOREGROUND_FORMAT,
                0x10000000U, OPEN_CFW_SYSTEM_MONITOR_FOREGROUND_TRACE
            );
            (void)OPEN_CFW_SYSTEM_MONITOR_POST_DISPLAY_COMMAND(0U, 0U, 0U);
        } else if (OPEN_CFW_SYSTEM_MONITOR_BACKGROUND_RUNNING() == 1U) {
            open_cfw_system_monitor_message(
                3U, 0x3DU, OPEN_CFW_SYSTEM_MONITOR_BACKGROUND_FORMAT,
                0x0C000000U, OPEN_CFW_SYSTEM_MONITOR_BACKGROUND_TRACE
            );
            (void)OPEN_CFW_SYSTEM_MONITOR_POST_DISPLAY_COMMAND(0U, 0U, 0U);
        }
    }

    waits = 0U;
    while (
        OPEN_CFW_SYSTEM_MONITOR_DISPLAY_RUNNING() == 1U &&
        waits < OPEN_CFW_SYSTEM_MONITOR_WAIT_LIMIT
    ) {
        OPEN_CFW_SYSTEM_MONITOR_DELAY(OPEN_CFW_SYSTEM_MONITOR_WAIT_TICKS);
        ++waits;
    }

    if (OPEN_CFW_SYSTEM_MONITOR_LENS_SIDE() == 1U) {
        open_cfw_system_monitor_message(
            3U, 0x4CU, OPEN_CFW_SYSTEM_MONITOR_MASTER_FORMAT,
            0x0C000000U, OPEN_CFW_SYSTEM_MONITOR_MASTER_TRACE
        );
        (void)OPEN_CFW_SYSTEM_MONITOR_SEND_SCHEDULER_IDLE();
    }

    OPEN_CFW_SYSTEM_MONITOR_RESET_DASHBOARD();
    OPEN_CFW_SYSTEM_MONITOR_RESET_APP_STATE(0U);
    OPEN_CFW_SYSTEM_MONITOR_RESET_ONBOARDING_COLORS();
    OPEN_CFW_SYSTEM_MONITOR_RESET_TERMINAL_STATE();
    OPEN_CFW_SYSTEM_MONITOR_PUBLISH_LENS_STATUS();
    return 0U;
}
