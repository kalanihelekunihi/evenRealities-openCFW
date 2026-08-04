/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Display input-event handler replacement for the Even Realities G2
 * 2.2.6.10 Apollo510B application. Exact stock boundaries, caller, packed
 * record ABI, and behavioral evidence are recorded in EVIDENCE.md.
 */

typedef unsigned long open_cfw_ui_input_uintptr;
typedef int *(*open_cfw_ui_input_current_state_fn)(void *manager);
typedef int (*open_cfw_ui_input_post_fn)(
    void *manager,
    unsigned int event,
    const void *data
);
typedef unsigned int (*open_cfw_ui_input_query_fn)(void);
typedef unsigned int (*open_cfw_ui_input_mode_handle_fn)(
    void *manager,
    unsigned int mode
);
typedef unsigned int (*open_cfw_ui_input_mode_active_fn)(
    void *manager,
    unsigned int handle
);
typedef void (*open_cfw_ui_input_void_fn)(void);
typedef void (*open_cfw_ui_input_system_event_fn)(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int
);
typedef void (*open_cfw_ui_input_value_fn)(unsigned int value);
typedef unsigned int (*open_cfw_ui_input_log_flags_fn)(void);
typedef void (*open_cfw_ui_input_log_record_fn)(
    unsigned int level,
    const void *module,
    const void *file,
    const void *tag,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_ui_input_trace_record_fn)(
    unsigned int mask,
    const void *schema,
    const void *format,
    ...
);

void evenhub_longpress(void);
int ring_release(void *context, int code, void *data);
unsigned int open_cfw_lens_side(void);
unsigned int open_cfw_ui_onboarding_running(void);
unsigned int open_cfw_ui_module_dispatch_event(
    unsigned int service_id,
    unsigned int event,
    unsigned int arg1,
    unsigned int arg2
);

#ifndef OPEN_CFW_UI_INPUT_MANAGER
#define OPEN_CFW_UI_INPUT_MANAGER \
    (*(void * volatile *)0x200744D0U)
#endif

#ifndef OPEN_CFW_UI_INPUT_STAGE
#define OPEN_CFW_UI_INPUT_STAGE \
    (*(volatile unsigned int *)0x200744DCU)
#endif

#ifndef OPEN_CFW_UI_INPUT_CURRENT_SERVICE
#define OPEN_CFW_UI_INPUT_CURRENT_SERVICE \
    (*(volatile unsigned int *)0x200744E0U)
#endif

#ifndef OPEN_CFW_UI_INPUT_CURRENT_STATE
#define OPEN_CFW_UI_INPUT_CURRENT_STATE(manager) \
    (((open_cfw_ui_input_current_state_fn)0x0045F8E7U)(manager))
#endif

#ifndef OPEN_CFW_UI_INPUT_POST
#define OPEN_CFW_UI_INPUT_POST(manager, event, data) \
    (((open_cfw_ui_input_post_fn)0x0045F8FDU)(manager, event, data))
#endif

#ifndef OPEN_CFW_UI_INPUT_TERMINAL_MODE
#define OPEN_CFW_UI_INPUT_TERMINAL_MODE() \
    (((open_cfw_ui_input_query_fn)0x0045BBF5U)())
#endif

#ifndef OPEN_CFW_UI_INPUT_MODE3_RESET
#define OPEN_CFW_UI_INPUT_MODE3_RESET() \
    (((open_cfw_ui_input_void_fn)0x00460375U)())
#endif

#ifndef OPEN_CFW_UI_INPUT_MODE_HANDLE
#define OPEN_CFW_UI_INPUT_MODE_HANDLE(manager, mode) \
    (((open_cfw_ui_input_mode_handle_fn)0x0045F841U)(manager, mode))
#endif

#ifndef OPEN_CFW_UI_INPUT_MODE_ACTIVE
#define OPEN_CFW_UI_INPUT_MODE_ACTIVE(manager, handle) \
    (((open_cfw_ui_input_mode_active_fn)0x0045F707U)(manager, handle))
#endif

#ifndef OPEN_CFW_UI_INPUT_SEND_SYSTEM_EVENT
#define OPEN_CFW_UI_INPUT_SEND_SYSTEM_EVENT(a, b, c, d) \
    (((open_cfw_ui_input_system_event_fn)0x00464B2FU)(a, b, c, d))
#endif

#ifndef OPEN_CFW_UI_INPUT_SET_Y
#define OPEN_CFW_UI_INPUT_SET_Y(value) \
    (((open_cfw_ui_input_value_fn)0x0046C623U)(value))
#endif

#ifndef OPEN_CFW_UI_INPUT_APPLY_Y
#define OPEN_CFW_UI_INPUT_APPLY_Y() \
    (((open_cfw_ui_input_void_fn)0x0046C985U)())
#endif

#ifndef OPEN_CFW_UI_INPUT_SET_X
#define OPEN_CFW_UI_INPUT_SET_X(value) \
    (((open_cfw_ui_input_value_fn)0x0046C601U)(value))
#endif

#ifndef OPEN_CFW_UI_INPUT_APPLY_X
#define OPEN_CFW_UI_INPUT_APPLY_X() \
    (((open_cfw_ui_input_void_fn)0x0046C9ABU)())
#endif

#ifndef OPEN_CFW_UI_INPUT_ONBOARDING_RUNNING
#define OPEN_CFW_UI_INPUT_ONBOARDING_RUNNING() \
    open_cfw_ui_onboarding_running()
#endif

#ifndef OPEN_CFW_UI_INPUT_LONGPRESS
#define OPEN_CFW_UI_INPUT_LONGPRESS() evenhub_longpress()
#endif

#ifndef OPEN_CFW_UI_INPUT_RING_RELEASE
#define OPEN_CFW_UI_INPUT_RING_RELEASE(manager, event, data) \
    ring_release(manager, event, data)
#endif

#ifndef OPEN_CFW_UI_INPUT_LENS_SIDE
#define OPEN_CFW_UI_INPUT_LENS_SIDE() open_cfw_lens_side()
#endif

#ifndef OPEN_CFW_UI_INPUT_DISPATCH_EVENT
#define OPEN_CFW_UI_INPUT_DISPATCH_EVENT(service, event, arg1, arg2) \
    open_cfw_ui_module_dispatch_event(service, event, arg1, arg2)
#endif

#ifndef OPEN_CFW_UI_INPUT_LOG_FLAGS
#define OPEN_CFW_UI_INPUT_LOG_FLAGS \
    ((open_cfw_ui_input_log_flags_fn)0x0043D0CFU)
#endif

#ifndef OPEN_CFW_UI_INPUT_LOG_RECORD
#define OPEN_CFW_UI_INPUT_LOG_RECORD \
    ((open_cfw_ui_input_log_record_fn)0x0043D575U)
#endif

#ifndef OPEN_CFW_UI_INPUT_TRACE_RECORD
#define OPEN_CFW_UI_INPUT_TRACE_RECORD \
    ((open_cfw_ui_input_trace_record_fn)0x0043CE9FU)
#endif

#define OPEN_CFW_UI_INPUT_LOG_MODULE ((const void *)0x00785AA0U)
#define OPEN_CFW_UI_INPUT_LOG_FILE ((const void *)0x00701FB4U)
#define OPEN_CFW_UI_INPUT_LOG_TAG ((const void *)0x0077697CU)

static inline __attribute__((always_inline))
unsigned int open_cfw_ui_input_u16(const unsigned char *value)
{
    return (unsigned int)value[0] | ((unsigned int)value[1] << 8U);
}

static inline __attribute__((always_inline))
unsigned int open_cfw_ui_input_u32(const unsigned char *value)
{
    return open_cfw_ui_input_u16(value) |
        (open_cfw_ui_input_u16(value + 2U) << 16U);
}

static inline __attribute__((always_inline))
unsigned int open_cfw_ui_input_trace_enabled(void)
{
    unsigned int flags = OPEN_CFW_UI_INPUT_LOG_FLAGS();

    if (flags & 1U) {
        return 1U;
    }
    return (OPEN_CFW_UI_INPUT_LOG_FLAGS() & 4U) != 0U;
}

static inline __attribute__((always_inline))
void open_cfw_ui_input_diag0(
    unsigned int level,
    unsigned int line,
    const void *format,
    unsigned int mask,
    const void *schema
)
{
    if (OPEN_CFW_UI_INPUT_LOG_FLAGS() & 2U) {
        OPEN_CFW_UI_INPUT_LOG_RECORD(
            level,
            OPEN_CFW_UI_INPUT_LOG_MODULE,
            OPEN_CFW_UI_INPUT_LOG_FILE,
            OPEN_CFW_UI_INPUT_LOG_TAG,
            line,
            format
        );
    }
    if (open_cfw_ui_input_trace_enabled()) {
        OPEN_CFW_UI_INPUT_TRACE_RECORD(mask, schema, schema);
    }
}

static inline __attribute__((always_inline))
void open_cfw_ui_input_diag1(
    unsigned int level,
    unsigned int line,
    const void *format,
    unsigned int mask,
    const void *schema,
    unsigned int value
)
{
    if (OPEN_CFW_UI_INPUT_LOG_FLAGS() & 2U) {
        OPEN_CFW_UI_INPUT_LOG_RECORD(
            level,
            OPEN_CFW_UI_INPUT_LOG_MODULE,
            OPEN_CFW_UI_INPUT_LOG_FILE,
            OPEN_CFW_UI_INPUT_LOG_TAG,
            line,
            format,
            value
        );
    }
    if (open_cfw_ui_input_trace_enabled()) {
        OPEN_CFW_UI_INPUT_TRACE_RECORD(mask, schema, schema, value);
    }
}

static inline __attribute__((always_inline))
void open_cfw_ui_input_diag2(
    unsigned int level,
    unsigned int line,
    const void *format,
    unsigned int mask,
    const void *schema,
    int first,
    int second
)
{
    if (OPEN_CFW_UI_INPUT_LOG_FLAGS() & 2U) {
        OPEN_CFW_UI_INPUT_LOG_RECORD(
            level,
            OPEN_CFW_UI_INPUT_LOG_MODULE,
            OPEN_CFW_UI_INPUT_LOG_FILE,
            OPEN_CFW_UI_INPUT_LOG_TAG,
            line,
            format,
            first,
            second
        );
    }
    if (open_cfw_ui_input_trace_enabled()) {
        OPEN_CFW_UI_INPUT_TRACE_RECORD(
            mask,
            schema,
            schema,
            first,
            second
        );
    }
}

static inline __attribute__((always_inline))
unsigned int open_cfw_ui_input_long_press(
    void *manager,
    int *state,
    unsigned int payload
)
{
    unsigned int application_id = (unsigned int)state[0];
    unsigned int display_mode =
        (unsigned int)*((const unsigned char *)state + 0xBU);

    if (OPEN_CFW_UI_INPUT_ONBOARDING_RUNNING() != 0U) {
        open_cfw_ui_input_diag0(
            4U,
            0x1A4U,
            (const void *)0x00753624U,
            0x10000000U,
            (const void *)0x00728990U
        );
        (void)OPEN_CFW_UI_INPUT_POST(manager, 8U, &payload);
        return 0U;
    }

    if (OPEN_CFW_UI_INPUT_TERMINAL_MODE() != 0U) {
        open_cfw_ui_input_diag0(
            4U,
            0x19DU,
            (const void *)0x0070ABA4U,
            0x10000000U,
            (const void *)0x006ECB18U
        );
        if (application_id == 0x30U) {
            open_cfw_ui_input_diag0(
                3U,
                0x19FU,
                (const void *)0x007141E8U,
                0x0C000000U,
                (const void *)0x006F2E90U
            );
            (void)OPEN_CFW_UI_INPUT_POST(manager, 8U, &payload);
        }
        return 0U;
    }

    if (display_mode == 0U) {
        if (application_id == 0xE0U) {
            OPEN_CFW_UI_INPUT_LONGPRESS();
        } else if (OPEN_CFW_UI_INPUT_LENS_SIDE() == 1U) {
            OPEN_CFW_UI_INPUT_SEND_SYSTEM_EVENT(3U, 0U, 0U, 0U);
        }
        return 0U;
    }

    if (display_mode == 1U) {
        if (application_id == 3U) {
            OPEN_CFW_UI_INPUT_MODE3_RESET();
            (void)OPEN_CFW_UI_INPUT_POST(
                manager,
                0U,
                (const void *)(open_cfw_ui_input_uintptr)3U
            );
            if (OPEN_CFW_UI_INPUT_STAGE == 2U) {
                return 1U;
            }
            OPEN_CFW_UI_INPUT_CURRENT_SERVICE = 0U;
        } else {
            unsigned int handle =
                OPEN_CFW_UI_INPUT_MODE_HANDLE(manager, 3U);

            if (OPEN_CFW_UI_INPUT_MODE_ACTIVE(manager, handle) == 1U) {
                (void)OPEN_CFW_UI_INPUT_DISPATCH_EVENT(
                    application_id,
                    5U,
                    0U,
                    0U
                );
            }
            if (
                (unsigned int)OPEN_CFW_UI_INPUT_POST(
                    manager,
                    2U,
                    (const void *)(open_cfw_ui_input_uintptr)3U
                ) == 1U
            ) {
                handle = OPEN_CFW_UI_INPUT_MODE_HANDLE(manager, 3U);
                if (
                    OPEN_CFW_UI_INPUT_MODE_ACTIVE(manager, handle) == 1U
                ) {
                    OPEN_CFW_UI_INPUT_CURRENT_SERVICE = 3U;
                }
            }
        }
    }
    return 0U;
}

/*
 * Stock ABI at 0x00442D86:
 *   r0 points to a packed ten-byte input record:
 *     +0 u16 event value, +2 u32 event ID, +6 u32 payload/coordinates.
 *   r0 returns zero, 0xFFFFFFFF for missing display state, or one for the
 *   mode-three long-press early-completion case.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_input_event_handler(const unsigned char *record)
{
    void *manager = OPEN_CFW_UI_INPUT_MANAGER;
    int *state = OPEN_CFW_UI_INPUT_CURRENT_STATE(manager);
    unsigned int event_value = open_cfw_ui_input_u16(record);
    unsigned int event_id = open_cfw_ui_input_u32(record + 2U);
    unsigned int payload = open_cfw_ui_input_u32(record + 6U);
    int coordinates[2];

    if (state == (int *)0) {
        open_cfw_ui_input_diag0(
            2U,
            0x177U,
            (const void *)0x00753600U,
            0x08000000U,
            (const void *)0x0072895CU
        );
        return 0xFFFFFFFFU;
    }

    switch (event_id) {
        case 0U:
            (void)OPEN_CFW_UI_INPUT_POST(
                manager,
                10U,
                &event_value
            );
            break;
        case 1U:
            (void)OPEN_CFW_UI_INPUT_POST(
                manager,
                0x48U,
                &event_value
            );
            break;
        case 2U:
            (void)OPEN_CFW_UI_INPUT_POST(manager, 0x3FU, &payload);
            break;
        case 3U:
            return open_cfw_ui_input_long_press(manager, state, payload);
        case 4U:
        case 5U:
        case 14U:
            coordinates[0] = (short)(payload & 0xFFFFU);
            coordinates[1] = (short)(payload >> 16U);
            open_cfw_ui_input_diag2(
                4U,
                event_id == 4U
                    ? 0x1BAU
                    : (event_id == 5U ? 0x1C5U : 0x1D3U),
                (const void *)0x0076AD74U,
                0x10800000U,
                (const void *)0x0073DD70U,
                coordinates[0],
                coordinates[1]
            );
            if (event_id == 4U) {
                (void)OPEN_CFW_UI_INPUT_POST(
                    manager,
                    0x44U,
                    coordinates
                );
            } else if (event_id == 5U) {
                (void)OPEN_CFW_UI_INPUT_POST(
                    manager,
                    0x45U,
                    coordinates
                );
            } else {
                (void)OPEN_CFW_UI_INPUT_RING_RELEASE(
                    manager,
                    0x4AU,
                    coordinates
                );
            }
            break;
        case 6U:
            if (OPEN_CFW_UI_INPUT_ONBOARDING_RUNNING() == 1U) {
                open_cfw_ui_input_diag0(
                    4U,
                    0x1DBU,
                    (const void *)0x00714224U,
                    0x10000000U,
                    (const void *)0x006F2EDCU
                );
                (void)OPEN_CFW_UI_INPUT_POST(manager, 0x4BU, &payload);
            }
            break;
        case 7U:
            (void)OPEN_CFW_UI_INPUT_POST(manager, 0x49U, &payload);
            break;
        case 8U:
            (void)OPEN_CFW_UI_INPUT_POST(manager, 0x40U, &payload);
            break;
        case 9U:
            open_cfw_ui_input_diag1(
                3U,
                0x1E9U,
                (const void *)0x00749204U,
                0x0C400000U,
                (const void *)0x0071DD18U,
                payload
            );
            (void)OPEN_CFW_UI_INPUT_POST(manager, 0x41U, &payload);
            break;
        case 10U:
            open_cfw_ui_input_diag0(
                2U,
                0x1F3U,
                (const void *)0x00753648U,
                0x08000000U,
                (const void *)0x007289C4U
            );
            break;
        case 11U:
            open_cfw_ui_input_diag1(
                4U,
                0x1FCU,
                (const void *)0x0073DD9CU,
                0x10400000U,
                (const void *)0x00714260U,
                payload
            );
            OPEN_CFW_UI_INPUT_SET_Y(payload);
            OPEN_CFW_UI_INPUT_APPLY_Y();
            break;
        case 12U:
            open_cfw_ui_input_diag1(
                4U,
                0x202U,
                (const void *)0x0073DDC8U,
                0x10400000U,
                (const void *)0x0071429CU,
                payload
            );
            OPEN_CFW_UI_INPUT_SET_X(payload);
            OPEN_CFW_UI_INPUT_APPLY_X();
            break;
        case 13U:
            break;
        case 15U:
            open_cfw_ui_input_diag1(
                3U,
                0x1F7U,
                (const void *)0x0075366CU,
                0x0C400000U,
                (const void *)0x007289F8U,
                payload
            );
            (void)OPEN_CFW_UI_INPUT_POST(manager, 0x4FU, &payload);
            break;
        case 16U:
            open_cfw_ui_input_diag1(
                3U,
                0x1EEU,
                (const void *)0x0074922CU,
                0x0C400000U,
                (const void *)0x0071DD50U,
                payload
            );
            (void)OPEN_CFW_UI_INPUT_POST(manager, 0x50U, &payload);
            break;
        default:
            open_cfw_ui_input_diag1(
                2U,
                0x20BU,
                (const void *)0x0076AD90U,
                0x08400000U,
                (const void *)0x0073DDF4U,
                event_id
            );
            break;
    }
    return 0U;
}
