/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Display callback wrapper replacement for the Even Realities G2 2.2.6.10
 * Apollo510B application. The exact stock boundary, dynamic SRAM target, and
 * behavioral evidence are recorded in EVIDENCE.md.
 */

typedef void (*open_cfw_ui_display_callback_target_fn)(void *context);

unsigned int open_cfw_strlen(const char *text);
unsigned int open_cfw_ui_display_sink(
    unsigned int selector,
    const void *buffer,
    unsigned int length
);

#ifndef OPEN_CFW_UI_DISPLAY_CALLBACK_TARGET
#define OPEN_CFW_UI_DISPLAY_CALLBACK_TARGET \
    (*(volatile open_cfw_ui_display_callback_target_fn *)0x200742F0U)
#endif

#ifndef OPEN_CFW_UI_DISPLAY_HANDLER_LENGTH
#define OPEN_CFW_UI_DISPLAY_HANDLER_LENGTH(buffer) \
    open_cfw_strlen((const char *)(buffer))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_HANDLER_SINK
#define OPEN_CFW_UI_DISPLAY_HANDLER_SINK(selector, buffer, length) \
    open_cfw_ui_display_sink( \
        (selector), \
        (buffer), \
        (length) \
    )
#endif

/*
 * Stock ABI at 0x00444684. The registered callback receives two arguments,
 * discards the first, and forwards the second to the current dynamic handler.
 * The stock saved-r7 return is incidental and ignored by the callback owner.
 */
__attribute__((used, noinline))
void open_cfw_ui_display_callback(
    void *unused,
    void *context
)
{
    open_cfw_ui_display_callback_target_fn target =
        OPEN_CFW_UI_DISPLAY_CALLBACK_TARGET;

    (void)unused;
    target(context);
}

/*
 * Stock ABI at 0x00472C7C. This is the sole writer recovered for the dynamic
 * handler word used by the callback and generic formatting dispatcher.
 */
__attribute__((used, noinline))
void open_cfw_ui_display_handler_set(
    open_cfw_ui_display_callback_target_fn target
)
{
    OPEN_CFW_UI_DISPLAY_CALLBACK_TARGET = target;
}

/*
 * Stock ABI at 0x005415C2. The handler computes the buffer length and submits
 * selector one, the original buffer, and that exact length to the sink.
 */
__attribute__((used, noinline))
void open_cfw_ui_display_handler(const void *buffer)
{
    unsigned int length = OPEN_CFW_UI_DISPLAY_HANDLER_LENGTH(buffer);

    OPEN_CFW_UI_DISPLAY_HANDLER_SINK(1U, buffer, length);
}
