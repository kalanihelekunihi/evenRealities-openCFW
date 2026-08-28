/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 Apollo display submit operation-one
 * backend at 0x0058E49E. The exact stock boundary, polling state, and
 * behavioral evidence are recorded in EVIDENCE.md.
 */

unsigned int open_cfw_ui_display_operation_three(
    void *handle,
    const void *descriptor
);
void open_cfw_ui_display_event_service(void *handle);

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_ONE_BUSY
#define OPEN_CFW_UI_DISPLAY_OPERATION_ONE_BUSY(handle) \
    (((volatile unsigned char *)(handle))[0x11AU])
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_ONE_LIMIT
#define OPEN_CFW_UI_DISPLAY_OPERATION_ONE_LIMIT(descriptor) \
    (*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(descriptor) + 0x0CU \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_ONE_START
#define OPEN_CFW_UI_DISPLAY_OPERATION_ONE_START(handle, descriptor) \
    open_cfw_ui_display_operation_three((handle), (descriptor))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_ONE_SERVICE
#define OPEN_CFW_UI_DISPLAY_OPERATION_ONE_SERVICE(handle) \
    open_cfw_ui_display_event_service(handle)
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_ONE_DELAY
#define OPEN_CFW_UI_DISPLAY_OPERATION_ONE_DELAY(duration) \
    (((void (*)(unsigned int))0x004807A1U)(duration))
#endif

/*
 * Stock ABI at 0x0058E49E. A descriptor limit of UINT32_MAX waits until the
 * event-side busy byte clears; a finite limit cancels and returns four when
 * the post-service poll count reaches that value.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_display_operation_one(
    void *handle,
    const void *descriptor
)
{
    unsigned int polls = 0U;
    unsigned int result = OPEN_CFW_UI_DISPLAY_OPERATION_ONE_START(
        handle,
        descriptor
    );

    if (result != 0U) {
        return result;
    }

    while (OPEN_CFW_UI_DISPLAY_OPERATION_ONE_BUSY(handle) != 0U) {
        OPEN_CFW_UI_DISPLAY_OPERATION_ONE_SERVICE(handle);
        OPEN_CFW_UI_DISPLAY_OPERATION_ONE_DELAY(1000U);
        if (
            OPEN_CFW_UI_DISPLAY_OPERATION_ONE_LIMIT(descriptor)
                != 0xFFFFFFFFU
        ) {
            ++polls;
            if (
                polls
                    == OPEN_CFW_UI_DISPLAY_OPERATION_ONE_LIMIT(descriptor)
            ) {
                OPEN_CFW_UI_DISPLAY_OPERATION_ONE_BUSY(handle) = 0U;
                return 4U;
            }
        }
    }
    return 0U;
}
