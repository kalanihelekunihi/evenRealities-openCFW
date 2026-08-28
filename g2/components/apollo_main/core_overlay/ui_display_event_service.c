/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 Apollo event-side display-operation
 * service routine at 0x0058E618. The exact stock boundary, state layout, and
 * behavioral evidence are recorded in EVIDENCE.md.
 */

typedef void (*open_cfw_ui_display_event_service_callback_fn)(
    unsigned int result,
    void *context
);

unsigned int open_cfw_ui_display_ring_fill(void *handle);
unsigned int open_cfw_ui_display_direct_read(
    void *handle,
    void *destination,
    unsigned int count,
    unsigned int *read_count
);
unsigned int open_cfw_ring_read(
    void *ring,
    void *destination,
    unsigned int count
);

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CRITICAL_ENTER
static inline unsigned int
open_cfw_ui_display_event_service_critical_enter(void)
{
    unsigned int interrupt_mask;

    __asm__ volatile(
        "mrs %0, primask\n"
        "cpsid i"
        : "=r"(interrupt_mask)
        :
        : "memory"
    );
    return interrupt_mask;
}
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CRITICAL_ENTER() \
    open_cfw_ui_display_event_service_critical_enter()
#endif

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CRITICAL_EXIT
static inline void open_cfw_ui_display_event_service_critical_exit(
    unsigned int interrupt_mask
)
{
    __asm__ volatile(
        "msr primask, %0"
        :
        : "r"(interrupt_mask)
        : "memory"
    );
}
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_ui_display_event_service_critical_exit(interrupt_mask)
#endif

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_BUSY
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_BUSY(handle) \
    (((volatile unsigned char *)(handle))[0x11AU])
#endif

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_DESTINATION
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_DESTINATION(handle) \
    ((unsigned char *)(*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0x64U \
    )))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_TOTAL
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_TOTAL(handle) \
    (*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0x68U \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_PROGRESS_POINTER
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_PROGRESS_POINTER(handle) \
    ((volatile unsigned int *)(*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0x6CU \
    )))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CALLBACK
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CALLBACK(handle) \
    ((open_cfw_ui_display_event_service_callback_fn)( \
        *(const volatile unsigned int *)(const void *)( \
            (const unsigned char *)(handle) + 0x74U \
        ) \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CALLBACK_CONTEXT
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CALLBACK_CONTEXT(handle) \
    ((void *)(*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0x78U \
    )))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_OFFSET
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_OFFSET(handle) \
    (*(volatile unsigned int *)(void *)( \
        (unsigned char *)(handle) + 0x9CU \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_MODE
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_MODE(handle) \
    (((const volatile unsigned char *)(handle))[0xDDU])
#endif

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_AVAILABLE
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_AVAILABLE(handle) \
    (*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0x54U \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING(handle) \
    ((void *)((unsigned char *)(handle) + 0x4CU))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_FILL
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_FILL(handle) \
    ((void)open_cfw_ui_display_ring_fill(handle))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_DIRECT_READ
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_DIRECT_READ( \
    handle, \
    destination, \
    count, \
    read_count \
) \
    (open_cfw_ui_display_direct_read( \
        (handle), \
        (destination), \
        (count), \
        (read_count) \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_READ
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_READ( \
    ring, \
    destination, \
    count \
) \
    (open_cfw_ring_read((ring), (destination), (count)))
#endif

/*
 * Stock ABI at 0x0058E618. The three recovered callers ignore the incidental
 * r0/r1 values restored by the stock epilogue, so the reviewed contract is
 * void service(handle).
 */
__attribute__((used, noinline))
void open_cfw_ui_display_event_service(void *handle)
{
    unsigned int transferred;
    unsigned int interrupt_mask;
    unsigned int remaining;
    unsigned int available;
    unsigned char *destination;
    volatile unsigned int *progress;
    open_cfw_ui_display_event_service_callback_fn callback;
    unsigned int aborted = 0U;

    if (OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_MODE(handle) != 0U) {
        OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_FILL(handle);
    }

    if (OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_BUSY(handle) == 0U) {
        return;
    }

    interrupt_mask = OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CRITICAL_ENTER();
    remaining =
        OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_TOTAL(handle)
        - OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_OFFSET(handle);
    destination =
        OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_DESTINATION(handle)
        + OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_OFFSET(handle);
    transferred = 0U;

    if (OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_MODE(handle) == 0U) {
        (void)OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_DIRECT_READ(
            handle,
            destination,
            remaining,
            &transferred
        );
    } else {
        available =
            OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_AVAILABLE(handle);
        transferred =
            remaining < available
                ? remaining
                : available;
        if (
            (unsigned char)OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_READ(
                OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING(handle),
                destination,
                transferred
            )
                == 0U
        ) {
            OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_BUSY(handle) = 0U;
            callback = OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CALLBACK(handle);
            if (
                callback
                    != (
                        open_cfw_ui_display_event_service_callback_fn
                    )0
            ) {
                callback(
                    1U,
                    OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CALLBACK_CONTEXT(
                        handle
                    )
                );
                aborted = 1U;
            }
        }
    }

    if (aborted == 0U) {
        OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_OFFSET(handle) += transferred;
    }
    OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CRITICAL_EXIT(interrupt_mask);

    if (aborted != 0U) {
        return;
    }

    progress = OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_PROGRESS_POINTER(handle);
    if (progress != (volatile unsigned int *)0) {
        *progress = OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_OFFSET(handle);
    }

    if (
        OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_OFFSET(handle)
            == OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_TOTAL(handle)
    ) {
        OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_BUSY(handle) = 0U;
        callback = OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CALLBACK(handle);
        if (
            callback
                != (
                    open_cfw_ui_display_event_service_callback_fn
                )0
        ) {
            callback(
                0U,
                OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CALLBACK_CONTEXT(handle)
            );
        }
    }
}
