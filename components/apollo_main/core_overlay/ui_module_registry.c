/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * UI-module registry event/data dispatch, broadcast close, initialization,
 * and mode lookup replacements for the Even Realities G2 2.2.6.10 Apollo510B
 * application. Exact stock boundaries, registry layout, callers,
 * diagnostics, and behavioral evidence are recorded in EVIDENCE.md.
 */

typedef unsigned long open_cfw_ui_registry_uintptr;

typedef void (*open_cfw_ui_registry_data_handler_fn)(
    unsigned int event,
    const void *data,
    unsigned int length,
    open_cfw_ui_registry_uintptr handler_entry
);
typedef void (*open_cfw_ui_registry_event_handler_fn)(
    unsigned int event,
    unsigned int arg1,
    unsigned int arg2,
    void *context
);
typedef unsigned int (*open_cfw_ui_registry_terminal_mode_fn)(void);
typedef void (*open_cfw_ui_registry_transition_fn)(
    void *display_manager,
    void *module_state
);
typedef void (*open_cfw_ui_registry_special_mode_fn)(
    unsigned int service_id,
    unsigned int enabled
);
typedef void (*open_cfw_ui_registry_activate_fn)(
    void *display_manager,
    unsigned int state_id
);
typedef void *(*open_cfw_ui_registry_copy_fn)(
    void *destination,
    const void *source,
    unsigned int length
);
typedef unsigned int (*open_cfw_ui_registry_log_flags_fn)(void);
typedef void (*open_cfw_ui_registry_log_record_fn)(
    unsigned int level,
    const void *module,
    const void *file,
    const void *tag,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_ui_registry_trace_record_fn)(
    unsigned int mask,
    const void *schema,
    const void *format,
    ...
);

#ifndef OPEN_CFW_UI_REGISTRY_COUNT
#define OPEN_CFW_UI_REGISTRY_COUNT \
    (*(volatile unsigned int *)0x200744D4U)
#endif

#ifndef OPEN_CFW_UI_REGISTRY_SERVICE_ID
#define OPEN_CFW_UI_REGISTRY_SERVICE_ID(index) \
    (*(volatile unsigned int *)( \
        0x20066230U + ((unsigned int)(index) << 4) \
    ))
#endif

#ifndef OPEN_CFW_UI_REGISTRY_DATA_HANDLER_WORD
#define OPEN_CFW_UI_REGISTRY_DATA_HANDLER_WORD(index) \
    ((open_cfw_ui_registry_uintptr)( \
        *(volatile unsigned int *)( \
            0x20066234U + ((unsigned int)(index) << 4) \
        ) \
    ))
#endif

#ifndef OPEN_CFW_UI_REGISTRY_UI_HANDLER_WORD
#define OPEN_CFW_UI_REGISTRY_UI_HANDLER_WORD(index) \
    ((open_cfw_ui_registry_uintptr)( \
        *(volatile unsigned int *)( \
            0x20066238U + ((unsigned int)(index) << 4) \
        ) \
    ))
#endif

#ifndef OPEN_CFW_UI_REGISTRY_STATE_POINTER
#define OPEN_CFW_UI_REGISTRY_STATE_POINTER(index) \
    ((open_cfw_ui_registry_uintptr)( \
        *(volatile unsigned int *)( \
            0x2006623CU + ((unsigned int)(index) << 4) \
        ) \
    ))
#endif

#ifndef OPEN_CFW_UI_REGISTRY_STATE_ID
#define OPEN_CFW_UI_REGISTRY_STATE_ID(index) \
    (*(volatile unsigned int *)OPEN_CFW_UI_REGISTRY_STATE_POINTER(index))
#endif

#ifndef OPEN_CFW_UI_REGISTRY_MODE
#define OPEN_CFW_UI_REGISTRY_MODE(index) \
    (*(volatile unsigned char *)( \
        OPEN_CFW_UI_REGISTRY_STATE_POINTER(index) + 0xBU \
    ))
#endif

#ifndef OPEN_CFW_UI_REGISTRY_DISPLAY_MANAGER
#define OPEN_CFW_UI_REGISTRY_DISPLAY_MANAGER \
    (*(void * volatile *)0x200744D0U)
#endif

#ifndef OPEN_CFW_UI_REGISTRY_PRIMARY_CONTEXT
#define OPEN_CFW_UI_REGISTRY_PRIMARY_CONTEXT \
    ((void *)(open_cfw_ui_registry_uintptr)( \
        *(volatile unsigned int *)( \
            (open_cfw_ui_registry_uintptr) \
                OPEN_CFW_UI_REGISTRY_DISPLAY_MANAGER + 0x1CU \
        ) \
    ))
#endif

#ifndef OPEN_CFW_UI_REGISTRY_SECONDARY_CONTEXT
#define OPEN_CFW_UI_REGISTRY_SECONDARY_CONTEXT \
    ((void *)(open_cfw_ui_registry_uintptr)( \
        *(volatile unsigned int *)( \
            (open_cfw_ui_registry_uintptr) \
                OPEN_CFW_UI_REGISTRY_DISPLAY_MANAGER + 0x20U \
        ) \
    ))
#endif

#ifndef OPEN_CFW_UI_REGISTRY_STAGE
#define OPEN_CFW_UI_REGISTRY_STAGE \
    (*(volatile unsigned int *)0x200744DCU)
#endif

#ifndef OPEN_CFW_UI_REGISTRY_CURRENT_SERVICE
#define OPEN_CFW_UI_REGISTRY_CURRENT_SERVICE \
    (*(volatile unsigned int *)0x200744E0U)
#endif

#ifndef OPEN_CFW_UI_REGISTRY_TERMINAL_MODE
#define OPEN_CFW_UI_REGISTRY_TERMINAL_MODE() \
    (((open_cfw_ui_registry_terminal_mode_fn)0x0045BBF5U)())
#endif

#ifndef OPEN_CFW_UI_REGISTRY_TRANSITION
#define OPEN_CFW_UI_REGISTRY_TRANSITION(display_manager, module_state) \
    (((open_cfw_ui_registry_transition_fn)0x0045F3C9U)( \
        (display_manager), \
        (module_state) \
    ))
#endif

#ifndef OPEN_CFW_UI_REGISTRY_SPECIAL_MODE
#define OPEN_CFW_UI_REGISTRY_SPECIAL_MODE(service_id, enabled) \
    (((open_cfw_ui_registry_special_mode_fn)0x0045FE33U)( \
        (service_id), \
        (enabled) \
    ))
#endif

#ifndef OPEN_CFW_UI_REGISTRY_ACTIVATE
#define OPEN_CFW_UI_REGISTRY_ACTIVATE(display_manager, state_id) \
    (((open_cfw_ui_registry_activate_fn)0x0045F877U)( \
        (display_manager), \
        (state_id) \
    ))
#endif

#ifndef OPEN_CFW_UI_REGISTRY_FLASH_START
#define OPEN_CFW_UI_REGISTRY_FLASH_START ((const void *)0x006A44B0U)
#endif

#ifndef OPEN_CFW_UI_REGISTRY_FLASH_END
#define OPEN_CFW_UI_REGISTRY_FLASH_END ((const void *)0x006A4760U)
#endif

#ifndef OPEN_CFW_UI_REGISTRY_RUNTIME_TABLE
#define OPEN_CFW_UI_REGISTRY_RUNTIME_TABLE ((void *)0x20066230U)
#endif

#ifndef OPEN_CFW_UI_REGISTRY_COPY
#define OPEN_CFW_UI_REGISTRY_COPY(destination, source, length) \
    (((open_cfw_ui_registry_copy_fn)0x00439BE5U)( \
        (destination), \
        (source), \
        (length) \
    ))
#endif

#ifndef OPEN_CFW_UI_REGISTRY_LOG_FLAGS
#define OPEN_CFW_UI_REGISTRY_LOG_FLAGS \
    ((open_cfw_ui_registry_log_flags_fn)0x0043D0CFU)
#endif

#ifndef OPEN_CFW_UI_REGISTRY_LOG_RECORD
#define OPEN_CFW_UI_REGISTRY_LOG_RECORD \
    ((open_cfw_ui_registry_log_record_fn)0x0043D575U)
#endif

#ifndef OPEN_CFW_UI_REGISTRY_TRACE_RECORD
#define OPEN_CFW_UI_REGISTRY_TRACE_RECORD \
    ((open_cfw_ui_registry_trace_record_fn)0x0043CE9FU)
#endif

#define OPEN_CFW_UI_REGISTRY_MAX_MODULES 0x80U
#define OPEN_CFW_UI_REGISTRY_ROW_SIZE 0x10U
#define OPEN_CFW_UI_REGISTRY_MISSING_MODE 2U

#define OPEN_CFW_UI_REGISTRY_LOG_MODULE ((const void *)0x00785AA0U)
#define OPEN_CFW_UI_REGISTRY_LOG_FILE ((const void *)0x00701FB4U)
#define OPEN_CFW_UI_REGISTRY_FIND_TAG ((const void *)0x0076AD04U)
#define OPEN_CFW_UI_REGISTRY_FIND_FORMAT ((const void *)0x0074913CU)
#define OPEN_CFW_UI_REGISTRY_FIND_TRACE ((const void *)0x0071DC70U)
#define OPEN_CFW_UI_REGISTRY_INIT_TAG ((const void *)0x00785AB0U)
#define OPEN_CFW_UI_REGISTRY_INIT_FORMAT ((const void *)0x00776934U)
#define OPEN_CFW_UI_REGISTRY_INIT_TRACE ((const void *)0x00749164U)
#define OPEN_CFW_UI_REGISTRY_EVENT_TAG ((const void *)0x0075F310U)
#define OPEN_CFW_UI_REGISTRY_EVENT_SPECIAL_FORMAT \
    ((const void *)0x0075F330U)
#define OPEN_CFW_UI_REGISTRY_EVENT_SPECIAL_TRACE \
    ((const void *)0x00732FE4U)
#define OPEN_CFW_UI_REGISTRY_BROADCAST_TAG ((const void *)0x00753594U)
#define OPEN_CFW_UI_REGISTRY_BROADCAST_FORMAT ((const void *)0x0071DCA8U)
#define OPEN_CFW_UI_REGISTRY_BROADCAST_TRACE ((const void *)0x006F9D04U)

static inline __attribute__((always_inline))
unsigned int open_cfw_ui_registry_trace_enabled(void)
{
    unsigned int flags = OPEN_CFW_UI_REGISTRY_LOG_FLAGS();

    if (flags & 1U) {
        return 1U;
    }
    return (OPEN_CFW_UI_REGISTRY_LOG_FLAGS() & 4U) != 0U;
}

static inline __attribute__((always_inline))
void open_cfw_ui_registry_missing_diagnostic(unsigned int service_id)
{
    if (OPEN_CFW_UI_REGISTRY_LOG_FLAGS() & 2U) {
        OPEN_CFW_UI_REGISTRY_LOG_RECORD(
            2U,
            OPEN_CFW_UI_REGISTRY_LOG_MODULE,
            OPEN_CFW_UI_REGISTRY_LOG_FILE,
            OPEN_CFW_UI_REGISTRY_FIND_TAG,
            0x97U,
            OPEN_CFW_UI_REGISTRY_FIND_FORMAT,
            service_id
        );
    }
    if (open_cfw_ui_registry_trace_enabled()) {
        OPEN_CFW_UI_REGISTRY_TRACE_RECORD(
            0x08400000U,
            OPEN_CFW_UI_REGISTRY_FIND_TRACE,
            OPEN_CFW_UI_REGISTRY_FIND_TRACE,
            service_id
        );
    }
}

static inline __attribute__((always_inline))
void open_cfw_ui_registry_missing_event_diagnostic(unsigned int service_id)
{
    if (OPEN_CFW_UI_REGISTRY_LOG_FLAGS() & 2U) {
        OPEN_CFW_UI_REGISTRY_LOG_RECORD(
            2U,
            OPEN_CFW_UI_REGISTRY_LOG_MODULE,
            OPEN_CFW_UI_REGISTRY_LOG_FILE,
            OPEN_CFW_UI_REGISTRY_EVENT_TAG,
            0x7AU,
            OPEN_CFW_UI_REGISTRY_FIND_FORMAT,
            service_id
        );
    }
    if (open_cfw_ui_registry_trace_enabled()) {
        OPEN_CFW_UI_REGISTRY_TRACE_RECORD(
            0x08400000U,
            OPEN_CFW_UI_REGISTRY_FIND_TRACE,
            OPEN_CFW_UI_REGISTRY_FIND_TRACE,
            service_id
        );
    }
}

static inline __attribute__((always_inline))
void open_cfw_ui_registry_special_diagnostic(unsigned int service_id)
{
    if (OPEN_CFW_UI_REGISTRY_LOG_FLAGS() & 2U) {
        OPEN_CFW_UI_REGISTRY_LOG_RECORD(
            4U,
            OPEN_CFW_UI_REGISTRY_LOG_MODULE,
            OPEN_CFW_UI_REGISTRY_LOG_FILE,
            OPEN_CFW_UI_REGISTRY_EVENT_TAG,
            0x6CU,
            OPEN_CFW_UI_REGISTRY_EVENT_SPECIAL_FORMAT,
            service_id
        );
    }
    if (open_cfw_ui_registry_trace_enabled()) {
        OPEN_CFW_UI_REGISTRY_TRACE_RECORD(
            0x10400000U,
            OPEN_CFW_UI_REGISTRY_EVENT_SPECIAL_TRACE,
            OPEN_CFW_UI_REGISTRY_EVENT_SPECIAL_TRACE,
            service_id
        );
    }
}

static inline __attribute__((always_inline))
void open_cfw_ui_registry_broadcast_diagnostic(unsigned int service_id)
{
    if (OPEN_CFW_UI_REGISTRY_LOG_FLAGS() & 2U) {
        OPEN_CFW_UI_REGISTRY_LOG_RECORD(
            3U,
            OPEN_CFW_UI_REGISTRY_LOG_MODULE,
            OPEN_CFW_UI_REGISTRY_LOG_FILE,
            OPEN_CFW_UI_REGISTRY_BROADCAST_TAG,
            0x80U,
            OPEN_CFW_UI_REGISTRY_BROADCAST_FORMAT,
            service_id
        );
    }
    if (open_cfw_ui_registry_trace_enabled()) {
        OPEN_CFW_UI_REGISTRY_TRACE_RECORD(
            0x0C400000U,
            OPEN_CFW_UI_REGISTRY_BROADCAST_TRACE,
            OPEN_CFW_UI_REGISTRY_BROADCAST_TRACE,
            service_id
        );
    }
}

/*
 * Stock ABI at 0x0044228A:
 *   r0 service ID, r1 event, r2 event argument 1, r3 event argument 2.
 *
 * Mode-zero modules use display context +0x1C. Mode-one modules use +0x20
 * and are unavailable while terminal mode is active. A create event (2)
 * publishes the selected registry stage and drives the stock transition
 * hooks after the module callback.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_module_dispatch_event(
    unsigned int service_id,
    unsigned int event,
    unsigned int arg1,
    unsigned int arg2
)
{
    unsigned int index;
    unsigned int count = OPEN_CFW_UI_REGISTRY_COUNT;

    for (index = 0U; (int)index < (int)count; ++index) {
        if (
            OPEN_CFW_UI_REGISTRY_SERVICE_ID(index) == service_id &&
            OPEN_CFW_UI_REGISTRY_UI_HANDLER_WORD(index) != 0U
        ) {
            unsigned int module_mode = OPEN_CFW_UI_REGISTRY_MODE(index);

            if (module_mode == 0U) {
                if (
                    OPEN_CFW_UI_REGISTRY_TERMINAL_MODE() == 0U ||
                    OPEN_CFW_UI_REGISTRY_STATE_ID(index) == 0x30U
                ) {
                    open_cfw_ui_registry_event_handler_fn handler =
                        (open_cfw_ui_registry_event_handler_fn)
                            OPEN_CFW_UI_REGISTRY_UI_HANDLER_WORD(index);

                    handler(
                        event,
                        arg1,
                        arg2,
                        OPEN_CFW_UI_REGISTRY_PRIMARY_CONTEXT
                    );
                    if (event == 2U) {
                        OPEN_CFW_UI_REGISTRY_STAGE = 1U;
                        OPEN_CFW_UI_REGISTRY_TRANSITION(
                            OPEN_CFW_UI_REGISTRY_DISPLAY_MANAGER,
                            (void *)OPEN_CFW_UI_REGISTRY_STATE_POINTER(index)
                        );
                    }
                }
            } else if (
                module_mode == 1U &&
                OPEN_CFW_UI_REGISTRY_TERMINAL_MODE() == 0U
            ) {
                open_cfw_ui_registry_event_handler_fn handler =
                    (open_cfw_ui_registry_event_handler_fn)
                        OPEN_CFW_UI_REGISTRY_UI_HANDLER_WORD(index);

                handler(
                    event,
                    arg1,
                    arg2,
                    OPEN_CFW_UI_REGISTRY_SECONDARY_CONTEXT
                );
                if (event == 2U) {
                    unsigned int state_id =
                        OPEN_CFW_UI_REGISTRY_STATE_ID(index);

                    OPEN_CFW_UI_REGISTRY_STAGE = 2U;
                    OPEN_CFW_UI_REGISTRY_CURRENT_SERVICE = service_id;
                    OPEN_CFW_UI_REGISTRY_TRANSITION(
                        OPEN_CFW_UI_REGISTRY_DISPLAY_MANAGER,
                        (void *)OPEN_CFW_UI_REGISTRY_STATE_POINTER(index)
                    );
                    if (service_id == 7U || service_id == 4U) {
                        open_cfw_ui_registry_special_diagnostic(service_id);
                        OPEN_CFW_UI_REGISTRY_SPECIAL_MODE(service_id, 1U);
                    }
                    OPEN_CFW_UI_REGISTRY_ACTIVATE(
                        OPEN_CFW_UI_REGISTRY_DISPLAY_MANAGER,
                        state_id
                    );
                }
            }
            return service_id;
        }
    }

    open_cfw_ui_registry_missing_event_diagnostic(service_id);
    return service_id;
}

/*
 * Stock ABI at 0x00442456. Event two closes every mode-one module except the
 * supplied state ID. Other events and terminal mode one return 0xFFFFFFFF.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_modules_close_mode1(
    unsigned int event,
    unsigned int excluded_state_id,
    unsigned int unused_arg2,
    unsigned int unused_arg3
)
{
    unsigned int index;
    unsigned int count;

    (void)unused_arg2;
    (void)unused_arg3;
    if (event != 2U) {
        return 0xFFFFFFFFU;
    }
    if (OPEN_CFW_UI_REGISTRY_TERMINAL_MODE() == 1U) {
        open_cfw_ui_registry_broadcast_diagnostic(excluded_state_id);
        return 0xFFFFFFFFU;
    }

    count = OPEN_CFW_UI_REGISTRY_COUNT;
    for (index = 0U; (int)index < (int)count; ++index) {
        if (
            OPEN_CFW_UI_REGISTRY_MODE(index) == 1U &&
            OPEN_CFW_UI_REGISTRY_UI_HANDLER_WORD(index) != 0U &&
            OPEN_CFW_UI_REGISTRY_STATE_ID(index) != excluded_state_id
        ) {
            open_cfw_ui_registry_event_handler_fn handler =
                (open_cfw_ui_registry_event_handler_fn)
                    OPEN_CFW_UI_REGISTRY_UI_HANDLER_WORD(index);

            handler(
                2U,
                0U,
                0U,
                OPEN_CFW_UI_REGISTRY_SECONDARY_CONTEXT
            );
            OPEN_CFW_UI_REGISTRY_TRANSITION(
                OPEN_CFW_UI_REGISTRY_DISPLAY_MANAGER,
                (void *)OPEN_CFW_UI_REGISTRY_STATE_POINTER(index)
            );
        }
    }
    return 0U;
}

/*
 * Stock ABI at 0x00442524:
 *   r0 service ID, r1 data, r2 length, r3 event (low 16 bits used).
 *
 * The stock indirect BLX leaves the callback entry itself in r3. Preserve
 * that otherwise-unused fourth callback argument because other registry rows
 * share this dispatcher.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_module_dispatch_data(
    unsigned int service_id,
    const void *data,
    unsigned int length,
    unsigned int event
)
{
    unsigned int index;
    unsigned int count = OPEN_CFW_UI_REGISTRY_COUNT;

    for (index = 0U; (int)index < (int)count; ++index) {
        if (
            OPEN_CFW_UI_REGISTRY_SERVICE_ID(index) == service_id &&
            OPEN_CFW_UI_REGISTRY_DATA_HANDLER_WORD(index) != 0U
        ) {
            open_cfw_ui_registry_uintptr handler_entry =
                OPEN_CFW_UI_REGISTRY_DATA_HANDLER_WORD(index);
            open_cfw_ui_registry_data_handler_fn handler =
                (open_cfw_ui_registry_data_handler_fn)handler_entry;

            handler(event & 0xFFFFU, data, length, handler_entry);
            return service_id;
        }
    }

    open_cfw_ui_registry_missing_diagnostic(service_id);
    return service_id;
}

/*
 * Stock ABI at 0x004425A6: no meaningful arguments or return value. Copy the
 * linker-provided 16-byte registry rows into their runtime SRAM table after
 * capping the module count at 128.
 */
__attribute__((used, noinline))
void open_cfw_ui_modules_initialize(void)
{
    open_cfw_ui_registry_uintptr start =
        (open_cfw_ui_registry_uintptr)OPEN_CFW_UI_REGISTRY_FLASH_START;
    open_cfw_ui_registry_uintptr end =
        (open_cfw_ui_registry_uintptr)OPEN_CFW_UI_REGISTRY_FLASH_END;
    unsigned int count = (unsigned int)((end - start) >> 4);

    if (count > OPEN_CFW_UI_REGISTRY_MAX_MODULES) {
        count = OPEN_CFW_UI_REGISTRY_MAX_MODULES;
    }
    OPEN_CFW_UI_REGISTRY_COUNT = count;

    if (OPEN_CFW_UI_REGISTRY_LOG_FLAGS() & 2U) {
        OPEN_CFW_UI_REGISTRY_LOG_RECORD(
            4U,
            OPEN_CFW_UI_REGISTRY_LOG_MODULE,
            OPEN_CFW_UI_REGISTRY_LOG_FILE,
            OPEN_CFW_UI_REGISTRY_INIT_TAG,
            0xABU,
            OPEN_CFW_UI_REGISTRY_INIT_FORMAT,
            count
        );
    }
    if (open_cfw_ui_registry_trace_enabled()) {
        OPEN_CFW_UI_REGISTRY_TRACE_RECORD(
            0x10400000U,
            OPEN_CFW_UI_REGISTRY_INIT_TRACE,
            OPEN_CFW_UI_REGISTRY_INIT_TRACE,
            count
        );
    }

    (void)OPEN_CFW_UI_REGISTRY_COPY(
        OPEN_CFW_UI_REGISTRY_RUNTIME_TABLE,
        OPEN_CFW_UI_REGISTRY_FLASH_START,
        count << 4
    );
}

/*
 * Stock ABI at 0x00442618: return the byte at registry state offset +0x0B
 * for the first matching row that owns a UI handler, or mode two when no
 * eligible row exists.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_module_mode(unsigned int service_id)
{
    unsigned int index;
    unsigned int count = OPEN_CFW_UI_REGISTRY_COUNT;

    for (index = 0U; (int)index < (int)count; ++index) {
        if (
            OPEN_CFW_UI_REGISTRY_SERVICE_ID(index) == service_id &&
            OPEN_CFW_UI_REGISTRY_UI_HANDLER_WORD(index) != 0U
        ) {
            return OPEN_CFW_UI_REGISTRY_MODE(index);
        }
    }
    return OPEN_CFW_UI_REGISTRY_MISSING_MODE;
}
