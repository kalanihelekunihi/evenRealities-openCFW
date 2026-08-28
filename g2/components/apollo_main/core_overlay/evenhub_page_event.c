/*
 * SPDX-License-Identifier: MIT
 *
 * EvenHub page-event callback replacement for the Even Realities G2
 * 2.2.6.10 Apollo510B application. Exact stock boundaries, callback behavior,
 * state, diagnostics, and fixed-address ABI dependencies are in EVIDENCE.md.
 */

struct open_cfw_evenhub_page_manager_view {
    void *page_root_obj;
    unsigned char reserved_to_active[0x34U - sizeof(void *)];
    unsigned char active;
};

typedef void (*open_cfw_evenhub_page_opacity_fn)(
    void *page_root,
    unsigned int opacity,
    unsigned int duration
);
typedef void (*open_cfw_evenhub_page_send_status_fn)(
    unsigned int arg0,
    unsigned int arg1,
    unsigned int arg2,
    unsigned int status,
    unsigned int arg4,
    unsigned int input_device
);
typedef unsigned int (*open_cfw_evenhub_page_validate_fn)(
    struct open_cfw_evenhub_page_manager_view *manager,
    unsigned int event_type,
    const unsigned int *event
);
typedef unsigned int (*open_cfw_evenhub_page_display_stop_fn)(
    unsigned int device,
    unsigned int arg1,
    unsigned int arg2,
    unsigned int arg3
);
typedef void (*open_cfw_evenhub_page_exit_cleanup_fn)(
    void *page_root,
    unsigned int device
);
typedef unsigned int (*open_cfw_evenhub_page_timestamp_fn)(void);
typedef void (*open_cfw_evenhub_page_enqueue_fn)(
    void *queue,
    unsigned int event_type,
    const unsigned int *event
);
typedef unsigned int (*open_cfw_evenhub_page_log_flags_fn)(void);
typedef void (*open_cfw_evenhub_page_log_record_fn)(
    unsigned int level,
    const void *module,
    const void *file,
    const void *tag,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_evenhub_page_trace_record_fn)(
    unsigned int mask,
    const void *schema,
    const void *format,
    ...
);

unsigned int open_cfw_lens_side(void);
void open_cfw_evenhub_active_mark(void);

#ifndef OPEN_CFW_EVENHUB_PAGE_MANAGER
#define OPEN_CFW_EVENHUB_PAGE_MANAGER \
    (*(struct open_cfw_evenhub_page_manager_view * volatile *)0x200745A8U)
#endif

#ifndef OPEN_CFW_EVENHUB_PAGE_NAVIGATION_OPAQUE
#define OPEN_CFW_EVENHUB_PAGE_NAVIGATION_OPAQUE \
    (*(volatile unsigned int *)0x200745C0U)
#endif

#ifndef OPEN_CFW_EVENHUB_PAGE_STOPPED
#define OPEN_CFW_EVENHUB_PAGE_STOPPED \
    (*(volatile unsigned char *)0x20074FC3U)
#endif

#ifndef OPEN_CFW_EVENHUB_PAGE_ACTIVE
#define OPEN_CFW_EVENHUB_PAGE_ACTIVE \
    (*(volatile unsigned int *)0x200745C4U)
#endif

#ifndef OPEN_CFW_EVENHUB_PAGE_SET_OPACITY
#define OPEN_CFW_EVENHUB_PAGE_SET_OPACITY(root, opacity, duration) \
    (((open_cfw_evenhub_page_opacity_fn)0x00441489U)( \
        (root), \
        (opacity), \
        (duration) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_PAGE_SEND_STATUS
#define OPEN_CFW_EVENHUB_PAGE_SEND_STATUS(a0, a1, a2, status, a4, device) \
    (((open_cfw_evenhub_page_send_status_fn)0x004DA16BU)( \
        (a0), \
        (a1), \
        (a2), \
        (status), \
        (a4), \
        (device) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_PAGE_VALIDATE
#define OPEN_CFW_EVENHUB_PAGE_VALIDATE(manager, type, event) \
    (((open_cfw_evenhub_page_validate_fn)0x00494611U)( \
        (manager), \
        (type), \
        (event) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_PAGE_REQUEST_DISPLAY_STOP
#define OPEN_CFW_EVENHUB_PAGE_REQUEST_DISPLAY_STOP(device, a1, a2, a3) \
    (((open_cfw_evenhub_page_display_stop_fn)0x00464C37U)( \
        (device), \
        (a1), \
        (a2), \
        (a3) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_PAGE_EXIT_CLEANUP
#define OPEN_CFW_EVENHUB_PAGE_EXIT_CLEANUP(root, device) \
    (((open_cfw_evenhub_page_exit_cleanup_fn)0x004641B7U)( \
        (root), \
        (device) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_PAGE_TIMESTAMP
#define OPEN_CFW_EVENHUB_PAGE_TIMESTAMP() \
    (((open_cfw_evenhub_page_timestamp_fn)0x004935FFU)())
#endif

#ifndef OPEN_CFW_EVENHUB_PAGE_ENQUEUE
#define OPEN_CFW_EVENHUB_PAGE_ENQUEUE(queue, type, event) \
    (((open_cfw_evenhub_page_enqueue_fn)0x0048EB33U)( \
        (queue), \
        (type), \
        (event) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_PAGE_INPUT_DEVICE
#define OPEN_CFW_EVENHUB_PAGE_INPUT_DEVICE(event) \
    (((event) != (const unsigned int *)0 && (event)[4] != 0U) \
        ? *(const unsigned short *)(event)[4] \
        : 0U)
#endif

#ifndef OPEN_CFW_EVENHUB_PAGE_EXIT_TEMPLATE
#define OPEN_CFW_EVENHUB_PAGE_EXIT_TEMPLATE \
    ((const unsigned char *)0x00040102U)
#endif

#ifndef OPEN_CFW_EVENHUB_PAGE_EXIT_QUEUE
#define OPEN_CFW_EVENHUB_PAGE_EXIT_QUEUE ((void *)0x0071EE60U)
#endif

#ifndef OPEN_CFW_EVENHUB_PAGE_LOG_FLAGS
#define OPEN_CFW_EVENHUB_PAGE_LOG_FLAGS \
    ((open_cfw_evenhub_page_log_flags_fn)0x0043D0CFU)
#endif

#ifndef OPEN_CFW_EVENHUB_PAGE_LOG_RECORD
#define OPEN_CFW_EVENHUB_PAGE_LOG_RECORD \
    ((open_cfw_evenhub_page_log_record_fn)0x0043D575U)
#endif

#ifndef OPEN_CFW_EVENHUB_PAGE_TRACE_RECORD
#define OPEN_CFW_EVENHUB_PAGE_TRACE_RECORD \
    ((open_cfw_evenhub_page_trace_record_fn)0x0043CE9FU)
#endif

#define OPEN_CFW_EVENHUB_PAGE_DEVICE 0xE0U

#define OPEN_CFW_EVENHUB_PAGE_LOG_MODULE ((const void *)0x00785E70U)
#define OPEN_CFW_EVENHUB_PAGE_LOG_FILE ((const void *)0x00702988U)
#define OPEN_CFW_EVENHUB_PAGE_LOG_TAG ((const void *)0x0076B82CU)

#define OPEN_CFW_EVENHUB_PAGE_FOREGROUND_LOG ((const void *)0x0077F400U)
#define OPEN_CFW_EVENHUB_PAGE_FOREGROUND_TRACE ((const void *)0x0075FF70U)
#define OPEN_CFW_EVENHUB_PAGE_OPACITY_LOG ((const void *)0x00734034U)
#define OPEN_CFW_EVENHUB_PAGE_OPACITY_TRACE ((const void *)0x00714FBCU)
#define OPEN_CFW_EVENHUB_PAGE_RESTORE_LOG ((const void *)0x0073ED14U)
#define OPEN_CFW_EVENHUB_PAGE_RESTORE_TRACE ((const void *)0x00714FF8U)
#define OPEN_CFW_EVENHUB_PAGE_STOP_LOG ((const void *)0x00734064U)
#define OPEN_CFW_EVENHUB_PAGE_STOP_TRACE ((const void *)0x00715034U)
#define OPEN_CFW_EVENHUB_PAGE_DOUBLE_CLICK_LOG ((const void *)0x00715070U)
#define OPEN_CFW_EVENHUB_PAGE_DOUBLE_CLICK_TRACE ((const void *)0x006FA40CU)
#define OPEN_CFW_EVENHUB_PAGE_INPUT_LOG ((const void *)0x007775DCU)
#define OPEN_CFW_EVENHUB_PAGE_INPUT_TRACE ((const void *)0x00749FC4U)
#define OPEN_CFW_EVENHUB_PAGE_EXIT_LOG ((const void *)0x00749FECU)
#define OPEN_CFW_EVENHUB_PAGE_EXIT_TRACE ((const void *)0x007296F8U)
#define OPEN_CFW_EVENHUB_PAGE_EXIT_DONE_LOG ((const void *)0x007029CCU)
#define OPEN_CFW_EVENHUB_PAGE_EXIT_DONE_TRACE ((const void *)0x0073ED40U)

static inline __attribute__((always_inline))
unsigned int open_cfw_evenhub_page_trace_enabled(void)
{
    unsigned int flags = OPEN_CFW_EVENHUB_PAGE_LOG_FLAGS();

    if (flags & 1U) {
        return 1U;
    }
    return (OPEN_CFW_EVENHUB_PAGE_LOG_FLAGS() & 4U) != 0U;
}

static inline __attribute__((always_inline))
void open_cfw_evenhub_page_fixed_diagnostic(
    unsigned int level,
    unsigned int line,
    const void *message,
    unsigned int trace_mask,
    const void *trace_schema
)
{
    if (OPEN_CFW_EVENHUB_PAGE_LOG_FLAGS() & 2U) {
        OPEN_CFW_EVENHUB_PAGE_LOG_RECORD(
            level,
            OPEN_CFW_EVENHUB_PAGE_LOG_MODULE,
            OPEN_CFW_EVENHUB_PAGE_LOG_FILE,
            OPEN_CFW_EVENHUB_PAGE_LOG_TAG,
            line,
            message
        );
    }
    if (open_cfw_evenhub_page_trace_enabled()) {
        OPEN_CFW_EVENHUB_PAGE_TRACE_RECORD(
            trace_mask,
            trace_schema,
            trace_schema
        );
    }
}

static inline __attribute__((always_inline))
unsigned int open_cfw_evenhub_page_load_u32(const unsigned char *source)
{
    return
        (unsigned int)source[0] |
        ((unsigned int)source[1] << 8) |
        ((unsigned int)source[2] << 16) |
        ((unsigned int)source[3] << 24);
}

/*
 * ABI-compatible source replacement for stock 0x004E0D3A...0x004E1191.
 * The first two callback parameters are unused; event_type is in r2 and the
 * page-event record is in r3. Every stock path returns one.
 */
__attribute__((used, noinline))
unsigned int open_cfw_evenhub_page_event_handler(
    unsigned int unused0,
    unsigned int unused1,
    unsigned int event_type,
    const unsigned int *event
)
{
    struct open_cfw_evenhub_page_manager_view *manager;
    unsigned int foreground_id;
    unsigned int input_device;
    unsigned int exit_event[2];

    (void)unused0;
    (void)unused1;

    if (event_type == 0x42U) {
        foreground_id =
            event != (const unsigned int *)0 ? event[0] : 0U;
        if (OPEN_CFW_EVENHUB_PAGE_LOG_FLAGS() & 2U) {
            OPEN_CFW_EVENHUB_PAGE_LOG_RECORD(
                3U,
                OPEN_CFW_EVENHUB_PAGE_LOG_MODULE,
                OPEN_CFW_EVENHUB_PAGE_LOG_FILE,
                OPEN_CFW_EVENHUB_PAGE_LOG_TAG,
                0x76U,
                OPEN_CFW_EVENHUB_PAGE_FOREGROUND_LOG,
                foreground_id
            );
        }
        if (open_cfw_evenhub_page_trace_enabled()) {
            OPEN_CFW_EVENHUB_PAGE_TRACE_RECORD(
                0x0C400000U,
                OPEN_CFW_EVENHUB_PAGE_FOREGROUND_TRACE,
                OPEN_CFW_EVENHUB_PAGE_FOREGROUND_TRACE,
                foreground_id
            );
        }

        manager = OPEN_CFW_EVENHUB_PAGE_MANAGER;
        if (
            manager != (struct open_cfw_evenhub_page_manager_view *)0 &&
            manager->page_root_obj != (void *)0 &&
            foreground_id != 0U &&
            foreground_id != 0x21U
        ) {
            open_cfw_evenhub_page_fixed_diagnostic(
                4U,
                0x79U,
                OPEN_CFW_EVENHUB_PAGE_OPACITY_LOG,
                0x10000000U,
                OPEN_CFW_EVENHUB_PAGE_OPACITY_TRACE
            );
            OPEN_CFW_EVENHUB_PAGE_NAVIGATION_OPAQUE = 1U;
            OPEN_CFW_EVENHUB_PAGE_SET_OPACITY(
                manager->page_root_obj,
                0x7FU,
                0U
            );
        }
        OPEN_CFW_EVENHUB_PAGE_SEND_STATUS(0U, 0U, 0U, 4U, 0U, 0U);
        OPEN_CFW_EVENHUB_PAGE_STOPPED = 0U;
    } else if (event_type == 0x43U) {
        OPEN_CFW_EVENHUB_PAGE_SEND_STATUS(0U, 0U, 0U, 5U, 0U, 0U);
        manager = OPEN_CFW_EVENHUB_PAGE_MANAGER;
        if (
            manager != (struct open_cfw_evenhub_page_manager_view *)0 &&
            manager->page_root_obj != (void *)0
        ) {
            open_cfw_evenhub_page_fixed_diagnostic(
                4U,
                0x84U,
                OPEN_CFW_EVENHUB_PAGE_RESTORE_LOG,
                0x10000000U,
                OPEN_CFW_EVENHUB_PAGE_RESTORE_TRACE
            );
            if (OPEN_CFW_EVENHUB_PAGE_NAVIGATION_OPAQUE == 1U) {
                OPEN_CFW_EVENHUB_PAGE_NAVIGATION_OPAQUE = 0U;
                OPEN_CFW_EVENHUB_PAGE_SET_OPACITY(
                    manager->page_root_obj,
                    0xFFU,
                    0U
                );
            }
        }
        OPEN_CFW_EVENHUB_PAGE_STOPPED = 1U;
        if (
            OPEN_CFW_EVENHUB_PAGE_ACTIVE == 1U &&
            open_cfw_lens_side() == 1U
        ) {
            OPEN_CFW_EVENHUB_PAGE_ACTIVE = 0U;
            open_cfw_evenhub_page_fixed_diagnostic(
                3U,
                0x8EU,
                OPEN_CFW_EVENHUB_PAGE_STOP_LOG,
                0x0C000000U,
                OPEN_CFW_EVENHUB_PAGE_STOP_TRACE
            );
            (void)OPEN_CFW_EVENHUB_PAGE_REQUEST_DISPLAY_STOP(
                OPEN_CFW_EVENHUB_PAGE_DEVICE,
                0U,
                0U,
                0U
            );
        }
    } else if (
        event_type == 0x0AU ||
        event_type == 0x44U ||
        event_type == 0x45U
    ) {
        manager = OPEN_CFW_EVENHUB_PAGE_MANAGER;
        if (
            manager != (struct open_cfw_evenhub_page_manager_view *)0 &&
            manager->page_root_obj != (void *)0 &&
            manager->active == 1U &&
            OPEN_CFW_EVENHUB_PAGE_VALIDATE(
                manager,
                event_type,
                event
            ) == 1U
        ) {
            input_device =
                event_type == 0x0AU
                ? OPEN_CFW_EVENHUB_PAGE_INPUT_DEVICE(event)
                : 0U;
            OPEN_CFW_EVENHUB_PAGE_SEND_STATUS(
                0U,
                0U,
                0U,
                event_type == 0x0AU
                    ? 0U
                    : (event_type == 0x44U ? 1U : 2U),
                0U,
                input_device
            );
        }
    } else if (event_type == 0x48U) {
        manager = OPEN_CFW_EVENHUB_PAGE_MANAGER;
        if (
            manager != (struct open_cfw_evenhub_page_manager_view *)0 &&
            manager->page_root_obj != (void *)0
        ) {
            open_cfw_evenhub_page_fixed_diagnostic(
                4U,
                0xB7U,
                OPEN_CFW_EVENHUB_PAGE_DOUBLE_CLICK_LOG,
                0x10000000U,
                OPEN_CFW_EVENHUB_PAGE_DOUBLE_CLICK_TRACE
            );
            input_device = OPEN_CFW_EVENHUB_PAGE_INPUT_DEVICE(event);
            if (OPEN_CFW_EVENHUB_PAGE_LOG_FLAGS() & 2U) {
                OPEN_CFW_EVENHUB_PAGE_LOG_RECORD(
                    3U,
                    OPEN_CFW_EVENHUB_PAGE_LOG_MODULE,
                    OPEN_CFW_EVENHUB_PAGE_LOG_FILE,
                    OPEN_CFW_EVENHUB_PAGE_LOG_TAG,
                    0xBFU,
                    OPEN_CFW_EVENHUB_PAGE_INPUT_LOG,
                    input_device
                );
            }
            if (open_cfw_evenhub_page_trace_enabled()) {
                OPEN_CFW_EVENHUB_PAGE_TRACE_RECORD(
                    0x0C400000U,
                    OPEN_CFW_EVENHUB_PAGE_INPUT_TRACE,
                    OPEN_CFW_EVENHUB_PAGE_INPUT_TRACE,
                    input_device
                );
            }
            OPEN_CFW_EVENHUB_PAGE_SEND_STATUS(
                0U,
                0U,
                0U,
                3U,
                0U,
                input_device
            );
        }
    } else if (event_type == 0x4FU) {
        open_cfw_evenhub_page_fixed_diagnostic(
            4U,
            0xC4U,
            OPEN_CFW_EVENHUB_PAGE_EXIT_LOG,
            0x10000000U,
            OPEN_CFW_EVENHUB_PAGE_EXIT_TRACE
        );
        manager = OPEN_CFW_EVENHUB_PAGE_MANAGER;
        if (
            manager != (struct open_cfw_evenhub_page_manager_view *)0 &&
            manager->page_root_obj != (void *)0
        ) {
            OPEN_CFW_EVENHUB_PAGE_EXIT_CLEANUP(
                manager->page_root_obj,
                OPEN_CFW_EVENHUB_PAGE_DEVICE
            );
            exit_event[0] = OPEN_CFW_EVENHUB_PAGE_TIMESTAMP();
            exit_event[1] = open_cfw_evenhub_page_load_u32(
                OPEN_CFW_EVENHUB_PAGE_EXIT_TEMPLATE + 4
            );
            OPEN_CFW_EVENHUB_PAGE_ENQUEUE(
                OPEN_CFW_EVENHUB_PAGE_EXIT_QUEUE,
                2U,
                exit_event
            );
            open_cfw_evenhub_active_mark();
            open_cfw_evenhub_page_fixed_diagnostic(
                4U,
                0xCBU,
                OPEN_CFW_EVENHUB_PAGE_EXIT_DONE_LOG,
                0x10000000U,
                OPEN_CFW_EVENHUB_PAGE_EXIT_DONE_TRACE
            );
        }
    }

    return 1U;
}
