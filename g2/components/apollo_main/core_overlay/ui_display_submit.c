/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 Apollo display-operation submit
 * dispatcher at 0x0058E3F8. The exact stock boundary, handle signature, and
 * operation mapping are recorded in EVIDENCE.md.
 */

unsigned int open_cfw_ui_display_operation_zero(
    void *handle,
    const void *descriptor
);
unsigned int open_cfw_ui_display_operation_one(
    void *handle,
    const void *descriptor
);
unsigned int open_cfw_ui_display_operation_start(
    void *handle,
    const void *descriptor
);
unsigned int open_cfw_ui_display_operation_three(
    void *handle,
    const void *descriptor
);

#define OPEN_CFW_UI_DISPLAY_SUBMIT_HANDLE_MASK 0x01FFFFFFU
#define OPEN_CFW_UI_DISPLAY_SUBMIT_HANDLE_SIGNATURE 0x01EA9E06U

#ifndef OPEN_CFW_UI_DISPLAY_SUBMIT_HANDLE_WORD
#define OPEN_CFW_UI_DISPLAY_SUBMIT_HANDLE_WORD(handle) \
    (*(const volatile unsigned int *)(handle))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION
#define OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION(descriptor) \
    (((const unsigned char *)(descriptor))[0x34U])
#endif

#ifndef OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION_ZERO
#define OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION_ZERO(handle, descriptor) \
    open_cfw_ui_display_operation_zero( \
        (handle), \
        (descriptor) \
    )
#endif

#ifndef OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION_ONE
#define OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION_ONE(handle, descriptor) \
    open_cfw_ui_display_operation_one( \
        (handle), \
        (descriptor) \
    )
#endif

#ifndef OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION_TWO
#define OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION_TWO(handle, descriptor) \
    open_cfw_ui_display_operation_start( \
        (handle), \
        (descriptor) \
    )
#endif

#ifndef OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION_THREE
#define OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION_THREE(handle, descriptor) \
    open_cfw_ui_display_operation_three( \
        (handle), \
        (descriptor) \
    )
#endif

/*
 * Stock ABI at 0x0058E3F8. High handle flag bits are ignored, while the
 * low-25-bit signature and descriptor operation byte select the exact result.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_display_submit(
    void *handle,
    const void *descriptor
)
{
    unsigned int operation;

    if (handle == (void *)0) {
        return 2U;
    }
    if (
        (
            OPEN_CFW_UI_DISPLAY_SUBMIT_HANDLE_WORD(handle)
                & OPEN_CFW_UI_DISPLAY_SUBMIT_HANDLE_MASK
        ) != OPEN_CFW_UI_DISPLAY_SUBMIT_HANDLE_SIGNATURE
    ) {
        return 2U;
    }

    operation = OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION(descriptor);
    if (operation == 0U) {
        return OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION_ZERO(
            handle,
            descriptor
        );
    }
    if (operation == 1U) {
        return OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION_ONE(
            handle,
            descriptor
        );
    }
    if (operation == 2U) {
        return OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION_TWO(
            handle,
            descriptor
        );
    }
    if (operation == 3U) {
        return OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION_THREE(
            handle,
            descriptor
        );
    }
    return 1U;
}
