/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 Apollo display transport IRQ owner
 * at 0x0058E860. The exact stock boundary, status policy, and state layout are
 * recorded in EVIDENCE.md.
 */

typedef void (*open_cfw_ui_display_irq_callback_fn)(
    unsigned int result,
    void *context
);

void open_cfw_ui_display_event_service(void *handle);
void open_cfw_ui_display_operation_service(void *handle);
void open_cfw_ui_display_irq_bit6(void *handle);
void open_cfw_ui_display_irq_bit12(void *handle);
unsigned int open_cfw_ui_display_irq_result(
    unsigned int instance,
    unsigned int status
);
void open_cfw_ui_display_irq_finish(void *handle);

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_SIGNATURE
#define OPEN_CFW_UI_DISPLAY_IRQ_SIGNATURE(handle) \
    (*(const volatile unsigned int *)(const void *)(handle))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_INSTANCE
#define OPEN_CFW_UI_DISPLAY_IRQ_INSTANCE(handle) \
    (*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0x28U \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL
#define OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL(handle) \
    (((volatile unsigned char *)(handle))[0x11BU])
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_NORMAL_FLAG
#define OPEN_CFW_UI_DISPLAY_IRQ_NORMAL_FLAG(handle) \
    (((volatile unsigned char *)(handle))[0xDEU])
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_PROGRESS_BASE
#define OPEN_CFW_UI_DISPLAY_IRQ_PROGRESS_BASE(handle) \
    (*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0xE4U \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_PROGRESS_POINTER
#define OPEN_CFW_UI_DISPLAY_IRQ_PROGRESS_POINTER(handle) \
    ((volatile unsigned int *)(*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0xE8U \
    )))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_CALLBACK
#define OPEN_CFW_UI_DISPLAY_IRQ_CALLBACK(handle) \
    (*(open_cfw_ui_display_irq_callback_fn volatile *)(void *)( \
        (unsigned char *)(handle) + 0xF0U \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_CALLBACK_CONTEXT
#define OPEN_CFW_UI_DISPLAY_IRQ_CALLBACK_CONTEXT(handle) \
    ((void *)(*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(handle) + 0xF4U \
    )))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_FIFO_POSITION
#define OPEN_CFW_UI_DISPLAY_IRQ_FIFO_POSITION(instance) \
    ( \
        *(const volatile unsigned int *)(const void *)( \
            0x40039050U + (instance) * 0x1000U \
        ) \
        & 0x00000FFFU \
    )
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_EVENT_SERVICE
#define OPEN_CFW_UI_DISPLAY_IRQ_EVENT_SERVICE(handle) \
    open_cfw_ui_display_event_service(handle)
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_OPERATION_SERVICE
#define OPEN_CFW_UI_DISPLAY_IRQ_OPERATION_SERVICE(handle) \
    open_cfw_ui_display_operation_service(handle)
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL_BIT6
#define OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL_BIT6(handle) \
    open_cfw_ui_display_irq_bit6(handle)
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL_BIT12
#define OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL_BIT12(handle) \
    open_cfw_ui_display_irq_bit12(handle)
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_CALLBACK_RESULT
#define OPEN_CFW_UI_DISPLAY_IRQ_CALLBACK_RESULT(instance, status) \
    open_cfw_ui_display_irq_result((instance), (status))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL_FINISH
#define OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL_FINISH(handle) \
    open_cfw_ui_display_irq_finish(handle)
#endif

/*
 * Stock ABI at 0x0058E860. High handle flag bits are ignored by the same
 * low-25-bit signature test used by the submit dispatcher.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_display_irq_service(
    void *handle,
    unsigned int status
)
{
    unsigned int instance;
    volatile unsigned int *progress;
    open_cfw_ui_display_irq_callback_fn callback;
    unsigned int result;

    if (
        handle == (void *)0
        || (
            OPEN_CFW_UI_DISPLAY_IRQ_SIGNATURE(handle)
                & 0x01FFFFFFU
        )
            != 0x01EA9E06U
    ) {
        return 2U;
    }

    instance = OPEN_CFW_UI_DISPLAY_IRQ_INSTANCE(handle);
    if (OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL(handle) == 0U) {
        if ((status & 0x50U) != 0U) {
            OPEN_CFW_UI_DISPLAY_IRQ_EVENT_SERVICE(handle);
        }
        if ((status & 0x20U) != 0U) {
            OPEN_CFW_UI_DISPLAY_IRQ_OPERATION_SERVICE(handle);
        }
        if ((status & 0x01U) != 0U) {
            OPEN_CFW_UI_DISPLAY_IRQ_NORMAL_FLAG(handle) = 1U;
        }
    } else {
        progress = OPEN_CFW_UI_DISPLAY_IRQ_PROGRESS_POINTER(handle);
        if (progress != (volatile unsigned int *)0) {
            *progress =
                OPEN_CFW_UI_DISPLAY_IRQ_PROGRESS_BASE(handle)
                - OPEN_CFW_UI_DISPLAY_IRQ_FIFO_POSITION(instance);
        }
        if ((status & 0x40U) != 0U) {
            OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL_BIT6(handle);
        }
        if ((status & 0x1000U) != 0U) {
            OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL_BIT12(handle);
        }
        if ((status & 0x0800U) != 0U) {
            callback = OPEN_CFW_UI_DISPLAY_IRQ_CALLBACK(handle);
            if (
                callback
                    != (open_cfw_ui_display_irq_callback_fn)0
            ) {
                result = OPEN_CFW_UI_DISPLAY_IRQ_CALLBACK_RESULT(
                    instance,
                    status
                );
                callback(
                    result,
                    OPEN_CFW_UI_DISPLAY_IRQ_CALLBACK_CONTEXT(handle)
                );
                OPEN_CFW_UI_DISPLAY_IRQ_CALLBACK(handle) =
                    (open_cfw_ui_display_irq_callback_fn)0;
            }
            OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL_FINISH(handle);
        }
        OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL(handle) = 0U;
    }
    return 1U;
}
