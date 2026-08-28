/*
 * SPDX-License-Identifier: MIT
 *
 * Display-mode transition replacement for the Even Realities G2 2.2.6.10
 * Apollo510B application. Exact stock boundaries, caller, fixed ABIs, and
 * behavioral evidence are recorded in EVIDENCE.md.
 */

typedef unsigned long open_cfw_ui_switch_uintptr;

#ifndef OPEN_CFW_UI_SWITCH_EVENT_ARG_TYPE
#define OPEN_CFW_UI_SWITCH_EVENT_ARG_TYPE unsigned int
#endif

typedef unsigned int (*open_cfw_ui_switch_terminal_mode_fn)(void);
typedef void *(*open_cfw_ui_switch_active_state_fn)(void *display_manager);
typedef unsigned int (*open_cfw_ui_switch_open_fn)(
    void *display_manager,
    unsigned int operation,
    unsigned int service_id
);
typedef void *(*open_cfw_ui_switch_primary_state_fn)(void *display_manager);
typedef open_cfw_ui_switch_uintptr (*open_cfw_ui_switch_lookup_fn)(
    void *display_manager,
    unsigned int service_id
);
typedef unsigned int (*open_cfw_ui_switch_is_active_fn)(
    void *display_manager,
    open_cfw_ui_switch_uintptr entry
);
typedef void (*open_cfw_ui_switch_cancel_fn)(
    unsigned int handle,
    unsigned int timeout
);
typedef void (*open_cfw_ui_switch_poll_fn)(void);
typedef void (*open_cfw_ui_switch_delay_fn)(unsigned int ticks);
typedef void (*open_cfw_ui_switch_close_mode_fn)(
    unsigned int service_id,
    unsigned int arg1,
    unsigned int arg2,
    unsigned int arg3
);
typedef void (*open_cfw_ui_switch_start_mode0_fn)(
    unsigned int service_id,
    unsigned int arg1,
    unsigned int arg2,
    unsigned int arg3
);
typedef void (*open_cfw_ui_switch_replace_mode0_fn)(
    unsigned int service_id,
    unsigned int arg1,
    unsigned int arg2,
    unsigned int timeout
);
typedef unsigned int (*open_cfw_ui_switch_resource_size_fn)(
    const void *resource
);
typedef void (*open_cfw_ui_switch_resource_prepare_fn)(
    const void *resource,
    unsigned int size
);
typedef int (*open_cfw_ui_switch_resource_result_fn)(void);
typedef void *(*open_cfw_ui_switch_fill_fn)(
    void *destination,
    unsigned int length,
    unsigned int value
);
typedef unsigned int (*open_cfw_ui_switch_log_flags_fn)(void);
typedef void (*open_cfw_ui_switch_log_record_fn)(
    unsigned int level,
    const void *module,
    const void *file,
    const void *tag,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_ui_switch_trace_record_fn)(
    unsigned int mask,
    const void *schema,
    const void *format,
    ...
);

extern unsigned int open_cfw_ui_module_dispatch_event(
    unsigned int service_id,
    unsigned int event,
    OPEN_CFW_UI_SWITCH_EVENT_ARG_TYPE arg1,
    unsigned int arg2
);
extern unsigned int open_cfw_ui_module_mode(unsigned int service_id);
extern unsigned int open_cfw_lens_side(void);

#ifndef OPEN_CFW_UI_SWITCH_DISPLAY_MANAGER
#define OPEN_CFW_UI_SWITCH_DISPLAY_MANAGER \
    (*(void * volatile *)0x200744D0U)
#endif

#ifndef OPEN_CFW_UI_SWITCH_CURRENT_SERVICE
#define OPEN_CFW_UI_SWITCH_CURRENT_SERVICE \
    (*(volatile unsigned int *)0x200744E0U)
#endif

#ifndef OPEN_CFW_UI_SWITCH_TERMINAL_MODE
#define OPEN_CFW_UI_SWITCH_TERMINAL_MODE() \
    (((open_cfw_ui_switch_terminal_mode_fn)0x0045BBF5U)())
#endif

#ifndef OPEN_CFW_UI_SWITCH_ACTIVE_STATE
#define OPEN_CFW_UI_SWITCH_ACTIVE_STATE(display_manager) \
    (((open_cfw_ui_switch_active_state_fn)0x0045F8D1U)(display_manager))
#endif

#ifndef OPEN_CFW_UI_SWITCH_OPEN
#define OPEN_CFW_UI_SWITCH_OPEN(display_manager, operation, service_id) \
    (((open_cfw_ui_switch_open_fn)0x0045FAA9U)( \
        (display_manager), \
        (operation), \
        (service_id) \
    ))
#endif

#ifndef OPEN_CFW_UI_SWITCH_PRIMARY_STATE
#define OPEN_CFW_UI_SWITCH_PRIMARY_STATE(display_manager) \
    (((open_cfw_ui_switch_primary_state_fn)0x0045F6A9U)(display_manager))
#endif

#ifndef OPEN_CFW_UI_SWITCH_LOOKUP
#define OPEN_CFW_UI_SWITCH_LOOKUP(display_manager, service_id) \
    (((open_cfw_ui_switch_lookup_fn)0x0045F841U)( \
        (display_manager), \
        (service_id) \
    ))
#endif

#ifndef OPEN_CFW_UI_SWITCH_IS_ACTIVE
#define OPEN_CFW_UI_SWITCH_IS_ACTIVE(display_manager, entry) \
    (((open_cfw_ui_switch_is_active_fn)0x0045F707U)( \
        (display_manager), \
        (entry) \
    ))
#endif

#ifndef OPEN_CFW_UI_SWITCH_CANCEL
#define OPEN_CFW_UI_SWITCH_CANCEL(handle, timeout) \
    (((open_cfw_ui_switch_cancel_fn)0x00464243U)((handle), (timeout)))
#endif

#ifndef OPEN_CFW_UI_SWITCH_POLL
#define OPEN_CFW_UI_SWITCH_POLL() \
    (((open_cfw_ui_switch_poll_fn)0x00464345U)())
#endif

#ifndef OPEN_CFW_UI_SWITCH_DELAY
#define OPEN_CFW_UI_SWITCH_DELAY(ticks) \
    (((open_cfw_ui_switch_delay_fn)0x00454B4DU)(ticks))
#endif

#ifndef OPEN_CFW_UI_SWITCH_CLOSE_MODE
#define OPEN_CFW_UI_SWITCH_CLOSE_MODE(service_id, arg1, arg2, arg3) \
    (((open_cfw_ui_switch_close_mode_fn)0x00464C37U)( \
        (service_id), \
        (arg1), \
        (arg2), \
        (arg3) \
    ))
#endif

#ifndef OPEN_CFW_UI_SWITCH_START_MODE0
#define OPEN_CFW_UI_SWITCH_START_MODE0(service_id, arg1, arg2, arg3) \
    (((open_cfw_ui_switch_start_mode0_fn)0x00464B2FU)( \
        (service_id), \
        (arg1), \
        (arg2), \
        (arg3) \
    ))
#endif

#ifndef OPEN_CFW_UI_SWITCH_REPLACE_MODE0
#define OPEN_CFW_UI_SWITCH_REPLACE_MODE0(service_id, arg1, arg2, timeout) \
    (((open_cfw_ui_switch_replace_mode0_fn)0x0045A8EFU)( \
        (service_id), \
        (arg1), \
        (arg2), \
        (timeout) \
    ))
#endif

#ifndef OPEN_CFW_UI_SWITCH_RESOURCE_SIZE
#define OPEN_CFW_UI_SWITCH_RESOURCE_SIZE(resource) \
    (((open_cfw_ui_switch_resource_size_fn)0x00460085U)(resource))
#endif

#ifndef OPEN_CFW_UI_SWITCH_RESOURCE_PREPARE
#define OPEN_CFW_UI_SWITCH_RESOURCE_PREPARE(resource, size) \
    (((open_cfw_ui_switch_resource_prepare_fn)0x0045FFFFU)( \
        (resource), \
        (size) \
    ))
#endif

#ifndef OPEN_CFW_UI_SWITCH_RESOURCE_RESULT
#define OPEN_CFW_UI_SWITCH_RESOURCE_RESULT() \
    (((open_cfw_ui_switch_resource_result_fn)0x004628C5U)())
#endif

#ifndef OPEN_CFW_UI_SWITCH_FILL
#define OPEN_CFW_UI_SWITCH_FILL(destination, length, value) \
    (((open_cfw_ui_switch_fill_fn)0x0043C0E5U)( \
        (destination), \
        (length), \
        (value) \
    ))
#endif

#ifndef OPEN_CFW_UI_SWITCH_LOG_FLAGS
#define OPEN_CFW_UI_SWITCH_LOG_FLAGS \
    ((open_cfw_ui_switch_log_flags_fn)0x0043D0CFU)
#endif

#ifndef OPEN_CFW_UI_SWITCH_LOG_RECORD
#define OPEN_CFW_UI_SWITCH_LOG_RECORD \
    ((open_cfw_ui_switch_log_record_fn)0x0043D575U)
#endif

#ifndef OPEN_CFW_UI_SWITCH_TRACE_RECORD
#define OPEN_CFW_UI_SWITCH_TRACE_RECORD \
    ((open_cfw_ui_switch_trace_record_fn)0x0043CE9FU)
#endif

#define OPEN_CFW_UI_SWITCH_LOG_MODULE ((const void *)0x00785AA0U)
#define OPEN_CFW_UI_SWITCH_LOG_FILE ((const void *)0x00701FB4U)
#define OPEN_CFW_UI_SWITCH_TAG ((const void *)0x0076AD20U)

#define OPEN_CFW_UI_SWITCH_TERMINAL_FORMAT ((const void *)0x0073DCC0U)
#define OPEN_CFW_UI_SWITCH_TERMINAL_TRACE ((const void *)0x00714170U)
#define OPEN_CFW_UI_SWITCH_SAME_FORMAT ((const void *)0x0076AD3CU)
#define OPEN_CFW_UI_SWITCH_SAME_TRACE ((const void *)0x0073DCECU)
#define OPEN_CFW_UI_SWITCH_CURRENT_FORMAT ((const void *)0x007535B8U)
#define OPEN_CFW_UI_SWITCH_CURRENT_TRACE ((const void *)0x00728928U)
#define OPEN_CFW_UI_SWITCH_NULL_FORMAT ((const void *)0x0077694CU)
#define OPEN_CFW_UI_SWITCH_NULL_TRACE ((const void *)0x0074918CU)
#define OPEN_CFW_UI_SWITCH_MODE_FORMAT ((const void *)0x0075F350U)
#define OPEN_CFW_UI_SWITCH_MODE_TRACE ((const void *)0x00733014U)
#define OPEN_CFW_UI_SWITCH_DIRECTION_FORMAT ((const void *)0x007491B4U)
#define OPEN_CFW_UI_SWITCH_DIRECTION_TRACE ((const void *)0x0071DCE0U)
#define OPEN_CFW_UI_SWITCH_SERVICE3_FORMAT ((const void *)0x006E74E0U)
#define OPEN_CFW_UI_SWITCH_SERVICE3_TRACE ((const void *)0x006DA674U)
#define OPEN_CFW_UI_SWITCH_RESULT_FORMAT ((const void *)0x0073DD18U)
#define OPEN_CFW_UI_SWITCH_RESULT_TRACE ((const void *)0x007141ACU)
#define OPEN_CFW_UI_SWITCH_RESULT_ERROR_FORMAT ((const void *)0x0076AD58U)
#define OPEN_CFW_UI_SWITCH_RESULT_ERROR_TRACE ((const void *)0x0073DD44U)
#define OPEN_CFW_UI_SWITCH_OPEN_FORMAT ((const void *)0x00776964U)
#define OPEN_CFW_UI_SWITCH_OPEN_TRACE ((const void *)0x007491DCU)
#define OPEN_CFW_UI_SWITCH_REPLACE_FORMAT ((const void *)0x00733044U)
#define OPEN_CFW_UI_SWITCH_REPLACE_TRACE ((const void *)0x0070AB64U)

#define OPEN_CFW_UI_SWITCH_RESOURCE_SERVICE_11 ((const void *)0x0077ED0CU)
#define OPEN_CFW_UI_SWITCH_RESOURCE_SERVICE_5 ((const void *)0x0077ED20U)
#define OPEN_CFW_UI_SWITCH_RESOURCE_SERVICE_6 ((const void *)0x0077ED34U)
#define OPEN_CFW_UI_SWITCH_RESOURCE_SERVICE_8 ((const void *)0x0077ED48U)

static inline __attribute__((always_inline))
unsigned int open_cfw_ui_switch_trace_enabled(void)
{
    unsigned int flags = OPEN_CFW_UI_SWITCH_LOG_FLAGS();

    if (flags & 1U) {
        return 1U;
    }
    return (OPEN_CFW_UI_SWITCH_LOG_FLAGS() & 4U) != 0U;
}

static inline __attribute__((always_inline))
void open_cfw_ui_switch_diag0(
    unsigned int level,
    unsigned int line,
    const void *format,
    unsigned int mask,
    const void *trace
)
{
    if (OPEN_CFW_UI_SWITCH_LOG_FLAGS() & 2U) {
        OPEN_CFW_UI_SWITCH_LOG_RECORD(
            level,
            OPEN_CFW_UI_SWITCH_LOG_MODULE,
            OPEN_CFW_UI_SWITCH_LOG_FILE,
            OPEN_CFW_UI_SWITCH_TAG,
            line,
            format
        );
    }
    if (open_cfw_ui_switch_trace_enabled()) {
        OPEN_CFW_UI_SWITCH_TRACE_RECORD(mask, trace, trace);
    }
}

static inline __attribute__((always_inline))
void open_cfw_ui_switch_diag1(
    unsigned int level,
    unsigned int line,
    const void *format,
    unsigned int mask,
    const void *trace,
    unsigned int arg
)
{
    if (OPEN_CFW_UI_SWITCH_LOG_FLAGS() & 2U) {
        OPEN_CFW_UI_SWITCH_LOG_RECORD(
            level,
            OPEN_CFW_UI_SWITCH_LOG_MODULE,
            OPEN_CFW_UI_SWITCH_LOG_FILE,
            OPEN_CFW_UI_SWITCH_TAG,
            line,
            format,
            arg
        );
    }
    if (open_cfw_ui_switch_trace_enabled()) {
        OPEN_CFW_UI_SWITCH_TRACE_RECORD(mask, trace, trace, arg);
    }
}

static inline __attribute__((always_inline))
void open_cfw_ui_switch_diag2(
    unsigned int level,
    unsigned int line,
    const void *format,
    unsigned int mask,
    const void *trace,
    unsigned int arg1,
    unsigned int arg2
)
{
    if (OPEN_CFW_UI_SWITCH_LOG_FLAGS() & 2U) {
        OPEN_CFW_UI_SWITCH_LOG_RECORD(
            level,
            OPEN_CFW_UI_SWITCH_LOG_MODULE,
            OPEN_CFW_UI_SWITCH_LOG_FILE,
            OPEN_CFW_UI_SWITCH_TAG,
            line,
            format,
            arg1,
            arg2
        );
    }
    if (open_cfw_ui_switch_trace_enabled()) {
        OPEN_CFW_UI_SWITCH_TRACE_RECORD(
            mask,
            trace,
            trace,
            arg1,
            arg2
        );
    }
}

static inline __attribute__((always_inline))
unsigned int open_cfw_ui_switch_state_id(const void *state)
{
    return *(const volatile unsigned int *)state;
}

static inline __attribute__((always_inline))
unsigned int open_cfw_ui_switch_state_mode(const void *state)
{
    return *(const volatile unsigned char *)(
        (open_cfw_ui_switch_uintptr)state + 0xBU
    );
}

static inline __attribute__((always_inline))
unsigned int open_cfw_ui_switch_primary_id(const void *state)
{
    return *(const volatile unsigned int *)state;
}

static inline __attribute__((always_inline))
unsigned int open_cfw_ui_switch_primary_handle(const void *state)
{
    return *(const volatile unsigned int *)(
        (open_cfw_ui_switch_uintptr)state + 4U
    );
}

static inline __attribute__((always_inline))
int open_cfw_ui_switch_service3_result(unsigned int current_service)
{
    const void *resource;
    unsigned int size;

    if (current_service == 1U) {
        return 0;
    }
    if (current_service == 11U) {
        resource = OPEN_CFW_UI_SWITCH_RESOURCE_SERVICE_11;
    } else if (current_service == 5U) {
        resource = OPEN_CFW_UI_SWITCH_RESOURCE_SERVICE_5;
    } else if (current_service == 6U) {
        resource = OPEN_CFW_UI_SWITCH_RESOURCE_SERVICE_6;
    } else if (current_service == 8U) {
        resource = OPEN_CFW_UI_SWITCH_RESOURCE_SERVICE_8;
    } else {
        return -1;
    }

    size = OPEN_CFW_UI_SWITCH_RESOURCE_SIZE(resource);
    OPEN_CFW_UI_SWITCH_RESOURCE_PREPARE(resource, size);
    return OPEN_CFW_UI_SWITCH_RESOURCE_RESULT();
}

static inline __attribute__((always_inline))
void open_cfw_ui_switch_service3_packet(unsigned int current_service)
{
    unsigned char packet[10];
    int result;
    unsigned int encoded;

    (void)OPEN_CFW_UI_SWITCH_FILL(packet, sizeof(packet), 0U);
    (void)OPEN_CFW_UI_SWITCH_FILL(packet, sizeof(packet), 0U);
    packet[0] = 1U;
    packet[1] = 0xF0U;

    result = open_cfw_ui_switch_service3_result(current_service);
    if (result < 0) {
        open_cfw_ui_switch_diag0(
            4U,
            0xFAU,
            OPEN_CFW_UI_SWITCH_RESULT_ERROR_FORMAT,
            0x10000000U,
            OPEN_CFW_UI_SWITCH_RESULT_ERROR_TRACE
        );
        encoded = 0U;
    } else {
        open_cfw_ui_switch_diag1(
            4U,
            0xEEU,
            OPEN_CFW_UI_SWITCH_RESULT_FORMAT,
            0x10400000U,
            OPEN_CFW_UI_SWITCH_RESULT_TRACE,
            (unsigned int)result
        );
        encoded = (unsigned int)result;
    }

    packet[2] = (unsigned char)encoded;
    packet[3] = (unsigned char)(encoded >> 8);
    packet[4] = (unsigned char)(encoded >> 16);
    packet[5] = (unsigned char)(encoded >> 24);
    (void)open_cfw_ui_module_dispatch_event(
        3U,
        3U,
        (OPEN_CFW_UI_SWITCH_EVENT_ARG_TYPE)(open_cfw_ui_switch_uintptr)packet,
        6U
    );
}

/*
 * Stock ABI at 0x0044264E:
 *   r0 target service ID, r1 transition argument 1, r2 transition argument 2.
 *
 * Return one only when a mode-one target becomes the current service, zero
 * after a handled/no-op transition, and 0xFFFFFFFF for rejected requests.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_switch_display(
    unsigned int target_service,
    unsigned int transition_arg1,
    unsigned int transition_arg2
)
{
    void *display_manager;
    void *active_state;
    unsigned int target_mode;
    unsigned int current_mode;
    unsigned int current_service;

    if (OPEN_CFW_UI_SWITCH_TERMINAL_MODE() == 1U) {
        open_cfw_ui_switch_diag1(
            3U,
            0xBCU,
            OPEN_CFW_UI_SWITCH_TERMINAL_FORMAT,
            0x0C400000U,
            OPEN_CFW_UI_SWITCH_TERMINAL_TRACE,
            target_service
        );
        return 0xFFFFFFFFU;
    }

    display_manager = OPEN_CFW_UI_SWITCH_DISPLAY_MANAGER;
    active_state = OPEN_CFW_UI_SWITCH_ACTIVE_STATE(display_manager);
    if (
        active_state == (void *)0 ||
        open_cfw_ui_switch_state_id(active_state) == target_service
    ) {
        open_cfw_ui_switch_diag1(
            3U,
            0xC1U,
            OPEN_CFW_UI_SWITCH_SAME_FORMAT,
            0x0C400000U,
            OPEN_CFW_UI_SWITCH_SAME_TRACE,
            target_service
        );
        if (active_state == (void *)0) {
            open_cfw_ui_switch_diag0(
                4U,
                0xC5U,
                OPEN_CFW_UI_SWITCH_NULL_FORMAT,
                0x10000000U,
                OPEN_CFW_UI_SWITCH_NULL_TRACE
            );
        } else {
            open_cfw_ui_switch_diag1(
                4U,
                0xC3U,
                OPEN_CFW_UI_SWITCH_CURRENT_FORMAT,
                0x10400000U,
                OPEN_CFW_UI_SWITCH_CURRENT_TRACE,
                open_cfw_ui_switch_state_id(active_state)
            );
        }
        return 0xFFFFFFFFU;
    }

    target_mode = open_cfw_ui_module_mode(target_service) & 0xFFU;
    if (target_mode == 2U) {
        open_cfw_ui_switch_diag1(
            2U,
            0xCBU,
            OPEN_CFW_UI_SWITCH_MODE_FORMAT,
            0x08400000U,
            OPEN_CFW_UI_SWITCH_MODE_TRACE,
            target_service
        );
        return 0xFFFFFFFFU;
    }

    current_service = open_cfw_ui_switch_state_id(active_state);
    current_mode = open_cfw_ui_switch_state_mode(active_state);
    if (current_mode == 0U) {
        if (target_mode == 1U) {
            open_cfw_ui_switch_diag2(
                4U,
                0xD0U,
                OPEN_CFW_UI_SWITCH_DIRECTION_FORMAT,
                0x10800000U,
                OPEN_CFW_UI_SWITCH_DIRECTION_TRACE,
                target_service,
                1U
            );
            if (target_service == 3U) {
                open_cfw_ui_switch_diag0(
                    4U,
                    0xD2U,
                    OPEN_CFW_UI_SWITCH_SERVICE3_FORMAT,
                    0x10000000U,
                    OPEN_CFW_UI_SWITCH_SERVICE3_TRACE
                );
                open_cfw_ui_switch_service3_packet(current_service);
            }
            if (
                (OPEN_CFW_UI_SWITCH_OPEN(
                    display_manager,
                    1U,
                    target_service
                ) & 0xFFU) == 1U
            ) {
                open_cfw_ui_switch_diag0(
                    4U,
                    0x100U,
                    OPEN_CFW_UI_SWITCH_OPEN_FORMAT,
                    0x10000000U,
                    OPEN_CFW_UI_SWITCH_OPEN_TRACE
                );
                OPEN_CFW_UI_SWITCH_CURRENT_SERVICE = target_service;
                return 1U;
            }
        } else if (target_mode == 0U) {
            void *primary_state =
                OPEN_CFW_UI_SWITCH_PRIMARY_STATE(display_manager);
            unsigned int primary_service =
                open_cfw_ui_switch_primary_id(primary_state);

            if (primary_service != target_service) {
                unsigned int index;

                OPEN_CFW_UI_SWITCH_CANCEL(
                    open_cfw_ui_switch_primary_handle(primary_state),
                    300U
                );
                for (index = 0U; index < 22U; ++index) {
                    OPEN_CFW_UI_SWITCH_POLL();
                    OPEN_CFW_UI_SWITCH_DELAY(16U);
                }
            }
            if (
                open_cfw_lens_side() == 1U &&
                primary_service != target_service
            ) {
                OPEN_CFW_UI_SWITCH_CLOSE_MODE(
                    current_service & 0xFFFFU,
                    0U,
                    0U,
                    0U
                );
                OPEN_CFW_UI_SWITCH_START_MODE0(
                    target_service & 0xFFFFU,
                    transition_arg1,
                    transition_arg2 & 0xFFFFU,
                    0U
                );
            }
        }
    } else if (current_mode == 1U) {
        if (target_mode == 0U) {
            open_cfw_ui_switch_diag2(
                4U,
                0x115U,
                OPEN_CFW_UI_SWITCH_REPLACE_FORMAT,
                0x10800000U,
                OPEN_CFW_UI_SWITCH_REPLACE_TRACE,
                target_service,
                0U
            );
            if (open_cfw_lens_side() == 1U) {
                OPEN_CFW_UI_SWITCH_CLOSE_MODE(
                    current_service & 0xFFFFU,
                    0U,
                    0U,
                    0U
                );
                OPEN_CFW_UI_SWITCH_REPLACE_MODE0(
                    target_service,
                    transition_arg1,
                    transition_arg2,
                    500U
                );
            }
        } else if (target_mode == 1U) {
            open_cfw_ui_switch_uintptr entry =
                OPEN_CFW_UI_SWITCH_LOOKUP(display_manager, target_service);

            if (OPEN_CFW_UI_SWITCH_IS_ACTIVE(display_manager, entry) == 1U) {
                (void)open_cfw_ui_module_dispatch_event(
                    current_service,
                    5U,
                    0U,
                    0U
                );
            }
            if (
                (OPEN_CFW_UI_SWITCH_OPEN(
                    display_manager,
                    2U,
                    target_service
                ) & 0xFFU) == 1U
            ) {
                entry =
                    OPEN_CFW_UI_SWITCH_LOOKUP(
                        display_manager,
                        target_service
                    );
                if (
                    OPEN_CFW_UI_SWITCH_IS_ACTIVE(display_manager, entry) == 1U
                ) {
                    OPEN_CFW_UI_SWITCH_CURRENT_SERVICE = target_service;
                    return 1U;
                }
            }
        }
    }
    return 0U;
}
