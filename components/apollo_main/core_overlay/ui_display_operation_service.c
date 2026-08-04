/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the G2 2.2.6.10 Apollo display-operation service
 * routine at 0x0058E534. The exact stock boundary, state layout, and
 * behavioral evidence are recorded in EVIDENCE.md.
 */

typedef void (*open_cfw_ui_display_operation_service_callback_fn)(
    unsigned int result,
    void *context
);
unsigned int open_cfw_ui_display_direct_write(
    void *handle,
    const void *source,
    unsigned int count,
    unsigned int *written
);
unsigned int open_cfw_ring_write(
    void *ring,
    const void *source,
    unsigned int count
);
unsigned int open_cfw_ui_display_ring_drain(void *handle);

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CRITICAL_ENTER
static inline unsigned int
open_cfw_ui_display_operation_service_critical_enter(void)
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
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CRITICAL_ENTER() \
    open_cfw_ui_display_operation_service_critical_enter()
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CRITICAL_EXIT
static inline void open_cfw_ui_display_operation_service_critical_exit(
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
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_ui_display_operation_service_critical_exit(interrupt_mask)
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_BUSY
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_BUSY(handle) \
    (((volatile unsigned char *)(handle))[0x119U])
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_SOURCE
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_SOURCE(handle) \
    ((const unsigned char *)(*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0xA0U \
    )))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_TOTAL
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_TOTAL(handle) \
    (*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0xA4U \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_PROGRESS_POINTER
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_PROGRESS_POINTER(handle) \
    ((volatile unsigned int *)(*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0xA8U \
    )))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CALLBACK
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CALLBACK(handle) \
    ((open_cfw_ui_display_operation_service_callback_fn)( \
        *(const volatile unsigned int *)(const void *)( \
            (const unsigned char *)(handle) + 0xB0U \
        ) \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CALLBACK_CONTEXT
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CALLBACK_CONTEXT(handle) \
    ((void *)(*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0xB4U \
    )))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_OFFSET
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_OFFSET(handle) \
    (*(volatile unsigned int *)(void *)( \
        (unsigned char *)(handle) + 0xD8U \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_MODE
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_MODE(handle) \
    (((const volatile unsigned char *)(handle))[0xDCU])
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_AVAILABLE
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_AVAILABLE(handle) \
    ( \
        *(const volatile unsigned int *)(const void *)( \
            (const unsigned char *)(handle) + 0x40U \
        ) \
        - *(const volatile unsigned int *)(const void *)( \
            (const unsigned char *)(handle) + 0x3CU \
        ) \
    )
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_DIRECT_WRITE
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_DIRECT_WRITE( \
    handle, \
    source, \
    count, \
    written \
) \
    (open_cfw_ui_display_direct_write( \
        (handle), \
        (source), \
        (count), \
        (written) \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_WRITE
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_WRITE( \
    ring, \
    source, \
    count \
) \
    (open_cfw_ring_write( \
        (ring), \
        (source), \
        (count) \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING(handle) \
    ((void *)((unsigned char *)(handle) + 0x34U))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_SERVICE
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_SERVICE(handle) \
    ((void)open_cfw_ui_display_ring_drain(handle))
#endif

/*
 * Stock ABI at 0x0058E534. All three recovered callers ignore the incidental
 * r0/r1 values restored by the stock epilogue, so the reviewed contract is
 * void service(handle).
 */
__attribute__((used, noinline))
void open_cfw_ui_display_operation_service(void *handle)
{
    unsigned int transferred;
    unsigned int interrupt_mask;
    unsigned int remaining;
    unsigned int available;
    const unsigned char *source;
    volatile unsigned int *progress;
    open_cfw_ui_display_operation_service_callback_fn callback;
    unsigned int aborted = 0U;

    if (OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_BUSY(handle) != 0U) {
        interrupt_mask =
            OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CRITICAL_ENTER();
        remaining =
            OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_TOTAL(handle)
            - OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_OFFSET(handle);
        source =
            OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_SOURCE(handle)
            + OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_OFFSET(handle);

        if (OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_MODE(handle) == 0U) {
            (void)OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_DIRECT_WRITE(
                handle,
                source,
                remaining,
                &transferred
            );
        } else {
            available =
                OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_AVAILABLE(handle);
            transferred =
                remaining < available
                    ? remaining
                    : available;
            if (
                (unsigned char)
                    OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_WRITE(
                        OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING(handle),
                        source,
                        transferred
                    )
                    == 0U
            ) {
                OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_BUSY(handle) = 0U;
                callback =
                    OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CALLBACK(handle);
                if (
                    callback
                        != (
                            open_cfw_ui_display_operation_service_callback_fn
                        )0
                ) {
                    callback(
                        1U,
                        OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CALLBACK_CONTEXT(
                            handle
                        )
                    );
                    aborted = 1U;
                }
            }
        }

        if (aborted == 0U) {
            OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_OFFSET(handle) +=
                transferred;
        }
        OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CRITICAL_EXIT(interrupt_mask);

        if (aborted != 0U) {
            return;
        }

        progress =
            OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_PROGRESS_POINTER(handle);
        if (progress != (volatile unsigned int *)0) {
            *progress =
                OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_OFFSET(handle);
        }

        if (
            OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_OFFSET(handle)
                == OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_TOTAL(handle)
            && OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_BUSY(handle) != 0U
        ) {
            OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_BUSY(handle) = 0U;
            callback =
                OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CALLBACK(handle);
            if (
                callback
                    != (
                        open_cfw_ui_display_operation_service_callback_fn
                    )0
            ) {
                callback(
                    0U,
                    OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CALLBACK_CONTEXT(
                        handle
                    )
                );
            }
        }
    }

    if (OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_MODE(handle) != 0U) {
        OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_SERVICE(handle);
    }
}
