/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the G2 2.2.6.10 Apollo shared display-operation
 * start helper at 0x0058E4E8. The exact stock boundary, descriptor field, and
 * behavioral evidence are recorded in EVIDENCE.md.
 */

typedef void (*open_cfw_ui_display_operation_start_service_fn)(void *handle);

unsigned int open_cfw_ui_display_operation_begin(
    void *handle,
    const void *descriptor
);
void open_cfw_ui_display_operation_service(void *handle);

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_START_COMPLETION
#define OPEN_CFW_UI_DISPLAY_OPERATION_START_COMPLETION(descriptor) \
    (*(volatile unsigned int * const *)(const void *)( \
        (const unsigned char *)(descriptor) + 8U \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_START_BEGIN
#define OPEN_CFW_UI_DISPLAY_OPERATION_START_BEGIN(handle, descriptor) \
    open_cfw_ui_display_operation_begin((handle), (descriptor))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_START_SERVICE
#define OPEN_CFW_UI_DISPLAY_OPERATION_START_SERVICE(handle) \
    open_cfw_ui_display_operation_service(handle)
#endif

/*
 * Stock ABI at 0x0058E4E8. The optional completion word is cleared before the
 * lower-level begin call. A successful begin is followed by one service call.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_display_operation_start(
    void *handle,
    const void *descriptor
)
{
    volatile unsigned int *completion =
        OPEN_CFW_UI_DISPLAY_OPERATION_START_COMPLETION(descriptor);
    unsigned int result;

    if (completion != (volatile unsigned int *)0) {
        *completion = 0U;
    }

    result = OPEN_CFW_UI_DISPLAY_OPERATION_START_BEGIN(handle, descriptor);
    if (result == 0U) {
        OPEN_CFW_UI_DISPLAY_OPERATION_START_SERVICE(handle);
    }
    return result;
}
