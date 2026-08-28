/*
 * SPDX-License-Identifier: MIT
 *
 * Startup application-ID policy replacement for the Even Realities G2
 * 2.2.6.10 Apollo510B application. Exact stock boundaries, callers, fixed
 * ABI, and behavioral evidence are recorded in EVIDENCE.md.
 */

typedef unsigned int (*open_cfw_ui_startup_policy_fn)(
    unsigned int system_ready,
    unsigned int operation_type
);
typedef unsigned int (*open_cfw_ui_startup_log_flags_fn)(void);
typedef void (*open_cfw_ui_startup_log_record_fn)(
    unsigned int level,
    const void *module,
    const void *file,
    const void *tag,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_ui_startup_trace_record_fn)(
    unsigned int mask,
    const void *schema,
    const void *format,
    ...
);

#ifndef OPEN_CFW_UI_STARTUP_POLICY
#define OPEN_CFW_UI_STARTUP_POLICY(system_ready, operation_type) \
    (((open_cfw_ui_startup_policy_fn)0x0046651FU)( \
        (system_ready), \
        (operation_type) \
    ))
#endif

#ifndef OPEN_CFW_UI_STARTUP_LOG_FLAGS
#define OPEN_CFW_UI_STARTUP_LOG_FLAGS \
    ((open_cfw_ui_startup_log_flags_fn)0x0043D0CFU)
#endif

#ifndef OPEN_CFW_UI_STARTUP_LOG_RECORD
#define OPEN_CFW_UI_STARTUP_LOG_RECORD \
    ((open_cfw_ui_startup_log_record_fn)0x0043D575U)
#endif

#ifndef OPEN_CFW_UI_STARTUP_TRACE_RECORD
#define OPEN_CFW_UI_STARTUP_TRACE_RECORD \
    ((open_cfw_ui_startup_trace_record_fn)0x0043CE9FU)
#endif

#define OPEN_CFW_UI_STARTUP_LOG_MODULE ((const void *)0x00785AA0U)
#define OPEN_CFW_UI_STARTUP_LOG_FILE ((const void *)0x00701FB4U)
#define OPEN_CFW_UI_STARTUP_TAG ((const void *)0x00785AC0U)
#define OPEN_CFW_UI_STARTUP_UNKNOWN_FORMAT ((const void *)0x0077ED5CU)
#define OPEN_CFW_UI_STARTUP_UNKNOWN_TRACE ((const void *)0x007535DCU)
#define OPEN_CFW_UI_STARTUP_RESULT_FORMAT ((const void *)0x006E7534U)
#define OPEN_CFW_UI_STARTUP_RESULT_TRACE ((const void *)0x006DA6D8U)

static inline __attribute__((always_inline))
unsigned int open_cfw_ui_startup_trace_enabled(void)
{
    unsigned int flags = OPEN_CFW_UI_STARTUP_LOG_FLAGS();

    if (flags & 1U) {
        return 1U;
    }
    return (OPEN_CFW_UI_STARTUP_LOG_FLAGS() & 4U) != 0U;
}

/*
 * Stock ABI at 0x00442BA8:
 *   r0 system status (low byte), r1 input type, r0 startup app ID result.
 *
 * Input types 0, 1, and 4 map to operation types 0, 1, and 2. The stock
 * policy returns an application type: zero maps to app ID zero, one maps to
 * app ID three, and every other low-byte result is diagnosed and mapped to
 * zero.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_startup_app_id(
    unsigned int system_status,
    unsigned int input_type
)
{
    unsigned int operation_type;
    unsigned int application_type;
    unsigned int application_id;
    unsigned int ready = (system_status & 0xFFU) == 1U;

    if (input_type == 0U) {
        operation_type = 0U;
    } else if (input_type == 1U) {
        operation_type = 1U;
    } else if (input_type == 4U) {
        operation_type = 2U;
    } else {
        return 0U;
    }

    application_type =
        OPEN_CFW_UI_STARTUP_POLICY(ready, operation_type) & 0xFFU;
    if (application_type == 0U) {
        application_id = 0U;
    } else if (application_type == 1U) {
        application_id = 3U;
    } else {
        if (OPEN_CFW_UI_STARTUP_LOG_FLAGS() & 2U) {
            OPEN_CFW_UI_STARTUP_LOG_RECORD(
                2U,
                OPEN_CFW_UI_STARTUP_LOG_MODULE,
                OPEN_CFW_UI_STARTUP_LOG_FILE,
                OPEN_CFW_UI_STARTUP_TAG,
                0x156U,
                OPEN_CFW_UI_STARTUP_UNKNOWN_FORMAT,
                application_type
            );
        }
        if (open_cfw_ui_startup_trace_enabled()) {
            OPEN_CFW_UI_STARTUP_TRACE_RECORD(
                0x08400000U,
                OPEN_CFW_UI_STARTUP_UNKNOWN_TRACE,
                OPEN_CFW_UI_STARTUP_UNKNOWN_TRACE,
                application_type
            );
        }
        application_id = 0U;
    }

    if (OPEN_CFW_UI_STARTUP_LOG_FLAGS() & 2U) {
        OPEN_CFW_UI_STARTUP_LOG_RECORD(
            4U,
            OPEN_CFW_UI_STARTUP_LOG_MODULE,
            OPEN_CFW_UI_STARTUP_LOG_FILE,
            OPEN_CFW_UI_STARTUP_TAG,
            0x15CU,
            OPEN_CFW_UI_STARTUP_RESULT_FORMAT,
            system_status & 0xFFU,
            input_type,
            operation_type & 0xFFU,
            application_type,
            application_id
        );
    }
    if (open_cfw_ui_startup_trace_enabled()) {
        OPEN_CFW_UI_STARTUP_TRACE_RECORD(
            0x11400000U,
            OPEN_CFW_UI_STARTUP_RESULT_TRACE,
            OPEN_CFW_UI_STARTUP_RESULT_TRACE,
            system_status & 0xFFU,
            input_type,
            operation_type & 0xFFU,
            application_type,
            application_id
        );
    }
    return application_id;
}
