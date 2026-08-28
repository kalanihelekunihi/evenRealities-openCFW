/*
 * SPDX-License-Identifier: MIT
 *
 * EvenHub registry UI-event handler replacement for the Even Realities G2
 * 2.2.6.10 Apollo510B application. The reviewed registry row, complete stock
 * body, state words, event behavior, and downstream ABIs are in EVIDENCE.md.
 */

typedef unsigned int (*open_cfw_evenhub_ui_timer_fn)(void);
typedef void (*open_cfw_evenhub_ui_void_fn)(void);
typedef void *(*open_cfw_evenhub_ui_allocate_fn)(unsigned int size);
typedef void (*open_cfw_evenhub_ui_memset_fn)(
    void *destination,
    unsigned int size,
    unsigned int value
);
typedef void *(*open_cfw_evenhub_ui_create_root_fn)(unsigned int context);
typedef unsigned int (*open_cfw_evenhub_ui_create_display_fn)(
    unsigned int arg1,
    unsigned int arg2,
    void *manager
);
typedef void (*open_cfw_evenhub_ui_show_fn)(void *page_root);
typedef void (*open_cfw_evenhub_ui_route_fn)(
    void *manager,
    unsigned int arg1,
    unsigned int arg2
);
typedef void (*open_cfw_evenhub_ui_driver_fn)(
    unsigned int operation,
    unsigned int arg1
);
typedef void (*open_cfw_evenhub_ui_send_status_fn)(
    unsigned int arg0,
    unsigned int arg1,
    unsigned int arg2,
    unsigned int status,
    unsigned int arg4,
    unsigned int arg5
);
typedef void (*open_cfw_evenhub_ui_display_stop_fn)(
    unsigned int device,
    unsigned int arg1,
    unsigned int arg2,
    unsigned int arg3
);
typedef void (*open_cfw_evenhub_ui_send_raw_fn)(
    unsigned int device,
    const void *data,
    unsigned int count,
    unsigned int offset,
    unsigned int length
);
typedef void (*open_cfw_evenhub_ui_display_cleanup_fn)(
    unsigned int arg0,
    unsigned int arg1
);
typedef void (*open_cfw_evenhub_ui_state_report_fn)(unsigned int active);
typedef void (*open_cfw_evenhub_ui_destroy_fn)(void *manager);
typedef void (*open_cfw_evenhub_ui_free_fn)(void *allocation);
typedef unsigned int (*open_cfw_evenhub_ui_timestamp_fn)(void);
typedef void (*open_cfw_evenhub_ui_enqueue_fn)(
    void *endpoint,
    unsigned int event_type,
    const unsigned int *event
);
typedef unsigned int (*open_cfw_evenhub_ui_log_flags_fn)(void);
typedef void (*open_cfw_evenhub_ui_log_record_fn)(
    unsigned int level,
    const void *module,
    const void *file,
    const void *tag,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_evenhub_ui_trace_record_fn)(
    unsigned int mask,
    const void *schema,
    const void *format,
    ...
);

unsigned int open_cfw_lens_side(void);
unsigned int open_cfw_evenhub_imu_enable(unsigned int enabled);
unsigned int open_cfw_evenhub_state_get(void);

#ifndef OPEN_CFW_EVENHUB_UI_IMU_ENABLED
#define OPEN_CFW_EVENHUB_UI_IMU_ENABLED \
    (*(volatile unsigned int *)0x200745B4U)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_START_TICK
#define OPEN_CFW_EVENHUB_UI_START_TICK \
    (*(volatile unsigned int *)0x200745C8U)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_DISPLAY_FLAG
#define OPEN_CFW_EVENHUB_UI_DISPLAY_FLAG \
    (*(volatile unsigned int *)0x200745BCU)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_STATE
#define OPEN_CFW_EVENHUB_UI_STATE \
    (*(volatile unsigned int *)0x200745B8U)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_NAVIGATION
#define OPEN_CFW_EVENHUB_UI_NAVIGATION \
    (*(volatile unsigned int *)0x200745C0U)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_ACTIVE
#define OPEN_CFW_EVENHUB_UI_ACTIVE \
    (*(volatile unsigned int *)0x200745C4U)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_MANAGER
#define OPEN_CFW_EVENHUB_UI_MANAGER \
    (*(void * volatile *)0x200745A8U)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_STARTED
#define OPEN_CFW_EVENHUB_UI_STARTED \
    (*(volatile unsigned char *)0x20074FC3U)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_KEEPALIVE_COUNT
#define OPEN_CFW_EVENHUB_UI_KEEPALIVE_COUNT \
    (*(volatile unsigned int *)0x200745ACU)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_SECOND_COUNT
#define OPEN_CFW_EVENHUB_UI_SECOND_COUNT \
    (*(volatile unsigned int *)0x200745B0U)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_SECOND_FLAG
#define OPEN_CFW_EVENHUB_UI_SECOND_FLAG \
    (*(volatile unsigned char *)0x20074FC4U)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_REGISTRY_ROOT
#define OPEN_CFW_EVENHUB_UI_REGISTRY_ROOT \
    (*(void * volatile *)0x20000B3CU)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_TIMER
#define OPEN_CFW_EVENHUB_UI_TIMER() \
    (((open_cfw_evenhub_ui_timer_fn)0x004490CDU)())
#endif

#ifndef OPEN_CFW_EVENHUB_UI_INITIALIZE
#define OPEN_CFW_EVENHUB_UI_INITIALIZE() \
    (((open_cfw_evenhub_ui_void_fn)0x004D9B35U)())
#endif

#ifndef OPEN_CFW_EVENHUB_UI_ALLOCATE
#define OPEN_CFW_EVENHUB_UI_ALLOCATE(size) \
    (((open_cfw_evenhub_ui_allocate_fn)0x00474CD3U)(size))
#endif

#ifndef OPEN_CFW_EVENHUB_UI_CLEAR
#define OPEN_CFW_EVENHUB_UI_CLEAR(destination, size, value) \
    (((open_cfw_evenhub_ui_memset_fn)0x0043C0E5U)( \
        (destination), \
        (size), \
        (value) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_UI_CREATE_ROOT
#define OPEN_CFW_EVENHUB_UI_CREATE_ROOT(context) \
    (((open_cfw_evenhub_ui_create_root_fn)0x00494835U)(context))
#endif

#ifndef OPEN_CFW_EVENHUB_UI_CREATE_DISPLAY
#define OPEN_CFW_EVENHUB_UI_CREATE_DISPLAY(arg1, arg2, manager) \
    (((open_cfw_evenhub_ui_create_display_fn)0x00494BEDU)( \
        (arg1), \
        (arg2), \
        (manager) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_UI_SHOW
#define OPEN_CFW_EVENHUB_UI_SHOW(root) \
    (((open_cfw_evenhub_ui_show_fn)0x0046410BU)(root))
#endif

#ifndef OPEN_CFW_EVENHUB_UI_ROUTE
#define OPEN_CFW_EVENHUB_UI_ROUTE(manager, arg1, arg2) \
    (((open_cfw_evenhub_ui_route_fn)0x00496545U)( \
        (manager), \
        (arg1), \
        (arg2) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_UI_DRIVER
#define OPEN_CFW_EVENHUB_UI_DRIVER(operation, arg1) \
    (((open_cfw_evenhub_ui_driver_fn)0x004D9D9BU)( \
        (operation), \
        (arg1) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_UI_SEND_STATUS
#define OPEN_CFW_EVENHUB_UI_SEND_STATUS(a0, a1, a2, status, a4, a5) \
    (((open_cfw_evenhub_ui_send_status_fn)0x004DA16BU)( \
        (a0), \
        (a1), \
        (a2), \
        (status), \
        (a4), \
        (a5) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_UI_REQUEST_DISPLAY_STOP
#define OPEN_CFW_EVENHUB_UI_REQUEST_DISPLAY_STOP(device, a1, a2, a3) \
    (((open_cfw_evenhub_ui_display_stop_fn)0x00464C37U)( \
        (device), \
        (a1), \
        (a2), \
        (a3) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_UI_SEND_RAW
#define OPEN_CFW_EVENHUB_UI_SEND_RAW(device, data, count, offset, length) \
    (((open_cfw_evenhub_ui_send_raw_fn)0x00465481U)( \
        (device), \
        (data), \
        (count), \
        (offset), \
        (length) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_UI_DISPLAY_CLEANUP
#define OPEN_CFW_EVENHUB_UI_DISPLAY_CLEANUP(a0, a1) \
    (((open_cfw_evenhub_ui_display_cleanup_fn)0x004DA721U)((a0), (a1)))
#endif

#ifndef OPEN_CFW_EVENHUB_UI_STATE_REPORT
#define OPEN_CFW_EVENHUB_UI_STATE_REPORT(active) \
    (((open_cfw_evenhub_ui_state_report_fn)0x004DA079U)(active))
#endif

#ifndef OPEN_CFW_EVENHUB_UI_DESTROY
#define OPEN_CFW_EVENHUB_UI_DESTROY(manager) \
    (((open_cfw_evenhub_ui_destroy_fn)0x00493D03U)(manager))
#endif

#ifndef OPEN_CFW_EVENHUB_UI_FREE
#define OPEN_CFW_EVENHUB_UI_FREE(allocation) \
    (((open_cfw_evenhub_ui_free_fn)0x00474D17U)(allocation))
#endif

#ifndef OPEN_CFW_EVENHUB_UI_TIMESTAMP
#define OPEN_CFW_EVENHUB_UI_TIMESTAMP() \
    (((open_cfw_evenhub_ui_timestamp_fn)0x004935FFU)())
#endif

#ifndef OPEN_CFW_EVENHUB_UI_ENQUEUE
#define OPEN_CFW_EVENHUB_UI_ENQUEUE(endpoint, type, event) \
    (((open_cfw_evenhub_ui_enqueue_fn)0x0048EB33U)( \
        (endpoint), \
        (type), \
        (event) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_UI_FATAL
#define OPEN_CFW_EVENHUB_UI_FATAL() \
    do { \
        ((open_cfw_evenhub_ui_void_fn)0x005FA0A5U)(); \
        for (;;) { \
        } \
    } while (0)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_LOG_FLAGS
#define OPEN_CFW_EVENHUB_UI_LOG_FLAGS \
    ((open_cfw_evenhub_ui_log_flags_fn)0x0043D0CFU)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_LOG_RECORD
#define OPEN_CFW_EVENHUB_UI_LOG_RECORD \
    ((open_cfw_evenhub_ui_log_record_fn)0x0043D575U)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_TRACE_RECORD
#define OPEN_CFW_EVENHUB_UI_TRACE_RECORD \
    ((open_cfw_evenhub_ui_trace_record_fn)0x0043CE9FU)
#endif

#define OPEN_CFW_EVENHUB_UI_DEVICE 0xE0U

#ifndef OPEN_CFW_EVENHUB_UI_TICK_TEMPLATE
#define OPEN_CFW_EVENHUB_UI_TICK_TEMPLATE \
    ((const unsigned char *)0x0078D5B4U)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_TICK_ENDPOINT
#define OPEN_CFW_EVENHUB_UI_TICK_ENDPOINT ((void *)0x0071EE60U)
#endif

#ifndef OPEN_CFW_EVENHUB_UI_EXIT_ENDPOINT
#define OPEN_CFW_EVENHUB_UI_EXIT_ENDPOINT ((void *)0x00040103U)
#endif

#define OPEN_CFW_EVENHUB_UI_LOG_MODULE ((const void *)0x00785E70U)
#define OPEN_CFW_EVENHUB_UI_LOG_FILE ((const void *)0x00702988U)
#define OPEN_CFW_EVENHUB_UI_LOG_TAG ((const void *)0x0076B864U)
#define OPEN_CFW_EVENHUB_UI_ROOT_FAIL_LOG ((const void *)0x0072972CU)
#define OPEN_CFW_EVENHUB_UI_ROOT_FAIL_TRACE ((const void *)0x00702A10U)
#define OPEN_CFW_EVENHUB_UI_DISPLAY_FAIL_LOG ((const void *)0x006FA454U)
#define OPEN_CFW_EVENHUB_UI_DISPLAY_FAIL_TRACE ((const void *)0x006E3408U)
#define OPEN_CFW_EVENHUB_UI_SIDE_ONE_LOG ((const void *)0x006E03A8U)
#define OPEN_CFW_EVENHUB_UI_SIDE_ONE_TRACE ((const void *)0x006CA83CU)
#define OPEN_CFW_EVENHUB_UI_SIDE_OTHER_LOG ((const void *)0x006D8A04U)
#define OPEN_CFW_EVENHUB_UI_SIDE_OTHER_TRACE ((const void *)0x006D61A0U)
#define OPEN_CFW_EVENHUB_UI_KEEPALIVE_LOG ((const void *)0x0070B6E4U)
#define OPEN_CFW_EVENHUB_UI_KEEPALIVE_TRACE ((const void *)0x006ED1F8U)
#define OPEN_CFW_EVENHUB_UI_SECOND_LOG ((const void *)0x006FA49CU)
#define OPEN_CFW_EVENHUB_UI_SECOND_TRACE ((const void *)0x006E7CC0U)
#define OPEN_CFW_EVENHUB_UI_EXIT_LOG ((const void *)0x0074A03CU)
#define OPEN_CFW_EVENHUB_UI_EXIT_TRACE ((const void *)0x00729760U)
#define OPEN_CFW_EVENHUB_UI_CLEANUP_LOG ((const void *)0x00734094U)
#define OPEN_CFW_EVENHUB_UI_CLEANUP_TRACE ((const void *)0x0070B724U)
#define OPEN_CFW_EVENHUB_UI_FREE_LOG ((const void *)0x007150E8U)
#define OPEN_CFW_EVENHUB_UI_FREE_TRACE ((const void *)0x006FA4E4U)

static inline __attribute__((always_inline))
unsigned int open_cfw_evenhub_ui_trace_enabled(void)
{
    unsigned int flags = OPEN_CFW_EVENHUB_UI_LOG_FLAGS();

    if (flags & 1U) {
        return 1U;
    }
    return (OPEN_CFW_EVENHUB_UI_LOG_FLAGS() & 4U) != 0U;
}

static inline __attribute__((always_inline))
void open_cfw_evenhub_ui_diagnostic(
    unsigned int level,
    unsigned int line,
    const void *message,
    unsigned int trace_mask,
    const void *trace_schema
)
{
    if (OPEN_CFW_EVENHUB_UI_LOG_FLAGS() & 2U) {
        OPEN_CFW_EVENHUB_UI_LOG_RECORD(
            level,
            OPEN_CFW_EVENHUB_UI_LOG_MODULE,
            OPEN_CFW_EVENHUB_UI_LOG_FILE,
            OPEN_CFW_EVENHUB_UI_LOG_TAG,
            line,
            message
        );
    }
    if (open_cfw_evenhub_ui_trace_enabled()) {
        OPEN_CFW_EVENHUB_UI_TRACE_RECORD(
            trace_mask,
            trace_schema,
            trace_schema
        );
    }
}

static inline __attribute__((always_inline))
unsigned int open_cfw_evenhub_ui_load_u32(const unsigned char *source)
{
    return
        (unsigned int)source[0] |
        ((unsigned int)source[1] << 8) |
        ((unsigned int)source[2] << 16) |
        ((unsigned int)source[3] << 24);
}

/*
 * Registry UI-handler ABI for service 0xE0. Events 2, 3, 4, and 5 create,
 * route, tick, and destroy the shared EvenHub UI state. Every path returns 0.
 */
__attribute__((used, noinline))
unsigned int open_cfw_evenhub_ui_event_handler(
    unsigned int event_type,
    unsigned int arg1,
    unsigned int arg2,
    unsigned int context
)
{
    void *manager;
    void *page_root;
    unsigned int result;
    unsigned int event[2];
    unsigned char error_payload[5];

    arg2 &= 0xFFFFU;

    if (event_type == 2U) {
        OPEN_CFW_EVENHUB_UI_START_TICK = OPEN_CFW_EVENHUB_UI_TIMER();
        OPEN_CFW_EVENHUB_UI_IMU_ENABLED = 0U;
        OPEN_CFW_EVENHUB_UI_DISPLAY_FLAG = 0U;
        OPEN_CFW_EVENHUB_UI_STATE = 0U;
        OPEN_CFW_EVENHUB_UI_NAVIGATION = 0U;
        OPEN_CFW_EVENHUB_UI_ACTIVE = 0U;
        OPEN_CFW_EVENHUB_UI_INITIALIZE();

        manager = OPEN_CFW_EVENHUB_UI_ALLOCATE(0x38U);
        OPEN_CFW_EVENHUB_UI_MANAGER = manager;
        if (manager == (void *)0) {
            OPEN_CFW_EVENHUB_UI_FATAL();
            return 0U;
        }
        OPEN_CFW_EVENHUB_UI_CLEAR(manager, 0x38U, 0U);
        page_root = OPEN_CFW_EVENHUB_UI_CREATE_ROOT(context);
        *(void **)manager = page_root;
        if (page_root == (void *)0) {
            open_cfw_evenhub_ui_diagnostic(
                1U,
                0x11DU,
                OPEN_CFW_EVENHUB_UI_ROOT_FAIL_LOG,
                0x04000000U,
                OPEN_CFW_EVENHUB_UI_ROOT_FAIL_TRACE
            );
            OPEN_CFW_EVENHUB_UI_FATAL();
            return 0U;
        }

        result = OPEN_CFW_EVENHUB_UI_CREATE_DISPLAY(arg1, arg2, manager);
        if (result != 0U) {
            open_cfw_evenhub_ui_diagnostic(
                1U,
                0x124U,
                OPEN_CFW_EVENHUB_UI_DISPLAY_FAIL_LOG,
                0x04000000U,
                OPEN_CFW_EVENHUB_UI_DISPLAY_FAIL_TRACE
            );
            if (open_cfw_lens_side() == 1U) {
                open_cfw_evenhub_ui_diagnostic(
                    1U,
                    0x126U,
                    OPEN_CFW_EVENHUB_UI_SIDE_ONE_LOG,
                    0x04000000U,
                    OPEN_CFW_EVENHUB_UI_SIDE_ONE_TRACE
                );
                OPEN_CFW_EVENHUB_UI_SEND_STATUS(
                    0U,
                    0U,
                    0U,
                    6U,
                    0U,
                    0U
                );
                OPEN_CFW_EVENHUB_UI_REQUEST_DISPLAY_STOP(
                    OPEN_CFW_EVENHUB_UI_DEVICE,
                    0U,
                    0U,
                    0U
                );
            } else {
                open_cfw_evenhub_ui_diagnostic(
                    1U,
                    0x12BU,
                    OPEN_CFW_EVENHUB_UI_SIDE_OTHER_LOG,
                    0x04000000U,
                    OPEN_CFW_EVENHUB_UI_SIDE_OTHER_TRACE
                );
                OPEN_CFW_EVENHUB_UI_CLEAR(error_payload, 5U, 0U);
                OPEN_CFW_EVENHUB_UI_SEND_RAW(
                    OPEN_CFW_EVENHUB_UI_DEVICE,
                    error_payload,
                    1U,
                    0U,
                    5U
                );
            }
        }

        OPEN_CFW_EVENHUB_UI_REGISTRY_ROOT = page_root;
        if (result == 0U) {
            OPEN_CFW_EVENHUB_UI_SHOW(page_root);
        }
        OPEN_CFW_EVENHUB_UI_STARTED = 1U;
        OPEN_CFW_EVENHUB_UI_KEEPALIVE_COUNT = 0U;
        OPEN_CFW_EVENHUB_UI_SECOND_COUNT = 0U;
        OPEN_CFW_EVENHUB_UI_SECOND_FLAG = 0U;
    } else if (event_type == 3U) {
        OPEN_CFW_EVENHUB_UI_ROUTE(
            OPEN_CFW_EVENHUB_UI_MANAGER,
            arg1,
            arg2
        );
    } else if (event_type == 4U) {
        if (OPEN_CFW_EVENHUB_UI_STARTED == 1U) {
            ++OPEN_CFW_EVENHUB_UI_KEEPALIVE_COUNT;
            if (OPEN_CFW_EVENHUB_UI_KEEPALIVE_COUNT > 899U) {
                OPEN_CFW_EVENHUB_UI_KEEPALIVE_COUNT = 0U;
                open_cfw_evenhub_ui_diagnostic(
                    3U,
                    0x144U,
                    OPEN_CFW_EVENHUB_UI_KEEPALIVE_LOG,
                    0x0C000000U,
                    OPEN_CFW_EVENHUB_UI_KEEPALIVE_TRACE
                );
                if (open_cfw_lens_side() == 1U) {
                    OPEN_CFW_EVENHUB_UI_DRIVER(0U, 0U);
                }
            }
        }
        if (
            OPEN_CFW_EVENHUB_UI_SECOND_FLAG == 1U &&
            OPEN_CFW_EVENHUB_UI_STARTED == 1U
        ) {
            ++OPEN_CFW_EVENHUB_UI_SECOND_COUNT;
            if (OPEN_CFW_EVENHUB_UI_SECOND_COUNT > 239U) {
                OPEN_CFW_EVENHUB_UI_SECOND_COUNT = 0U;
                open_cfw_evenhub_ui_diagnostic(
                    3U,
                    0x14FU,
                    OPEN_CFW_EVENHUB_UI_SECOND_LOG,
                    0x0C000000U,
                    OPEN_CFW_EVENHUB_UI_SECOND_TRACE
                );
                if (open_cfw_lens_side() == 1U) {
                    OPEN_CFW_EVENHUB_UI_DRIVER(1U, 0U);
                    event[0] = OPEN_CFW_EVENHUB_UI_TIMESTAMP();
                    event[1] = open_cfw_evenhub_ui_load_u32(
                        OPEN_CFW_EVENHUB_UI_TICK_TEMPLATE + 4
                    );
                    OPEN_CFW_EVENHUB_UI_ENQUEUE(
                        OPEN_CFW_EVENHUB_UI_TICK_ENDPOINT,
                        2U,
                        event
                    );
                }
            }
        }
    } else if (event_type == 5U) {
        open_cfw_evenhub_ui_diagnostic(
            3U,
            0x159U,
            OPEN_CFW_EVENHUB_UI_EXIT_LOG,
            0x0C000000U,
            OPEN_CFW_EVENHUB_UI_EXIT_TRACE
        );
        if (OPEN_CFW_EVENHUB_UI_IMU_ENABLED == 1U) {
            (void)open_cfw_evenhub_imu_enable(0U);
        }
        if (OPEN_CFW_EVENHUB_UI_DISPLAY_FLAG == 1U) {
            open_cfw_evenhub_ui_diagnostic(
                4U,
                0x15FU,
                OPEN_CFW_EVENHUB_UI_CLEANUP_LOG,
                0x10000000U,
                OPEN_CFW_EVENHUB_UI_CLEANUP_TRACE
            );
            OPEN_CFW_EVENHUB_UI_DISPLAY_FLAG = 0U;
            OPEN_CFW_EVENHUB_UI_DISPLAY_CLEANUP(0U, 0U);
        }
        OPEN_CFW_EVENHUB_UI_STATE_REPORT(
            open_cfw_evenhub_state_get() == 1U ? 1U : 0U
        );

        manager = OPEN_CFW_EVENHUB_UI_MANAGER;
        if (manager != (void *)0) {
            OPEN_CFW_EVENHUB_UI_DESTROY(manager);
            OPEN_CFW_EVENHUB_UI_FREE(manager);
            OPEN_CFW_EVENHUB_UI_MANAGER = (void *)0;
            open_cfw_evenhub_ui_diagnostic(
                4U,
                0x16EU,
                OPEN_CFW_EVENHUB_UI_FREE_LOG,
                0x10000000U,
                OPEN_CFW_EVENHUB_UI_FREE_TRACE
            );
        }

        OPEN_CFW_EVENHUB_UI_STARTED = 0U;
        OPEN_CFW_EVENHUB_UI_KEEPALIVE_COUNT = 0U;
        OPEN_CFW_EVENHUB_UI_SECOND_COUNT = 0U;
        OPEN_CFW_EVENHUB_UI_SECOND_FLAG = 0U;
        OPEN_CFW_EVENHUB_UI_ACTIVE = 0U;
        OPEN_CFW_EVENHUB_UI_IMU_ENABLED = 0U;
        OPEN_CFW_EVENHUB_UI_DISPLAY_FLAG = 0U;
        OPEN_CFW_EVENHUB_UI_STATE = 0U;
        OPEN_CFW_EVENHUB_UI_NAVIGATION = 0U;

        result = OPEN_CFW_EVENHUB_UI_TIMER()
            - OPEN_CFW_EVENHUB_UI_START_TICK;
        event[0] = OPEN_CFW_EVENHUB_UI_TIMESTAMP();
        event[1] = result;
        OPEN_CFW_EVENHUB_UI_ENQUEUE(
            OPEN_CFW_EVENHUB_UI_EXIT_ENDPOINT,
            2U,
            event
        );
    }

    return 0U;
}
