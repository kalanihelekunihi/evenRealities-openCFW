/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the G2 2.2.6.10 Apollo display submit
 * operation-three backend at 0x0058E50A. The exact stock boundary,
 * descriptor field, and behavioral evidence are recorded in EVIDENCE.md.
 */

unsigned int open_cfw_ui_display_event_begin(
    void *handle,
    const void *descriptor
);
void open_cfw_ui_display_event_service(void *handle);

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_THREE_COMPLETION
#define OPEN_CFW_UI_DISPLAY_OPERATION_THREE_COMPLETION(descriptor) \
    (*(volatile unsigned int * const *)(const void *)( \
        (const unsigned char *)(descriptor) + 8U \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_THREE_BEGIN
#define OPEN_CFW_UI_DISPLAY_OPERATION_THREE_BEGIN(handle, descriptor) \
    open_cfw_ui_display_event_begin((handle), (descriptor))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_THREE_SERVICE
#define OPEN_CFW_UI_DISPLAY_OPERATION_THREE_SERVICE(handle) \
    open_cfw_ui_display_event_service(handle)
#endif

/*
 * Stock ABI at 0x0058E50A. The optional completion word is cleared before
 * beginning the event-side operation. A successful begin is serviced once,
 * while every begin result is returned unchanged.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_display_operation_three(
    void *handle,
    const void *descriptor
)
{
    volatile unsigned int *completion =
        OPEN_CFW_UI_DISPLAY_OPERATION_THREE_COMPLETION(descriptor);
    unsigned int result;

    if (completion != (volatile unsigned int *)0) {
        *completion = 0U;
    }

    result = OPEN_CFW_UI_DISPLAY_OPERATION_THREE_BEGIN(handle, descriptor);
    if (result == 0U) {
        OPEN_CFW_UI_DISPLAY_OPERATION_THREE_SERVICE(handle);
    }
    return result;
}
