/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 Apollo display submit operation-zero
 * backend at 0x0058E454. The exact stock boundary, polling state, and
 * behavioral evidence are recorded in EVIDENCE.md.
 */

typedef unsigned int (*open_cfw_ui_display_operation_zero_start_fn)(
    void *handle,
    const void *descriptor
);
typedef void (*open_cfw_ui_display_operation_zero_service_fn)(void *handle);
unsigned int open_cfw_ui_display_operation_start(
    void *handle,
    const void *descriptor
);
void open_cfw_ui_display_operation_service(void *handle);

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_BUSY
#define OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_BUSY(handle) \
    (((volatile unsigned char *)(handle))[0x119U])
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_LIMIT
#define OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_LIMIT(descriptor) \
    (*(const volatile unsigned int *)(const void *)( \
        (const unsigned char *)(descriptor) + 0x0CU \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_START
#define OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_START(handle, descriptor) \
    open_cfw_ui_display_operation_start( \
        (handle), \
        (descriptor) \
    )
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_SERVICE
#define OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_SERVICE(handle) \
    open_cfw_ui_display_operation_service(handle)
#endif

#ifndef OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_DELAY
#define OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_DELAY(duration) \
    (((void (*)(unsigned int))0x004807A1U)(duration))
#endif

/*
 * Stock ABI at 0x0058E454. A descriptor limit of UINT32_MAX waits until the
 * handle's operation-zero busy byte clears; a finite limit cancels and
 * returns four when the post-service poll count reaches that value.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_display_operation_zero(
    void *handle,
    const void *descriptor
)
{
    unsigned int polls = 0U;
    unsigned int result = OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_START(
        handle,
        descriptor
    );

    if (result != 0U) {
        return result;
    }

    while (OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_BUSY(handle) != 0U) {
        OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_SERVICE(handle);
        OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_DELAY(1000U);
        if (
            OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_LIMIT(descriptor)
                != 0xFFFFFFFFU
        ) {
            ++polls;
            if (
                polls
                    == OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_LIMIT(descriptor)
            ) {
                OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_BUSY(handle) = 0U;
                return 4U;
            }
        }
    }
    return 0U;
}
