/* SPDX-License-Identifier: GPL-3.0-or-later */

typedef void (*open_cfw_bootloader_log_handler_fn)(void *context);

#ifndef OPEN_CFW_BOOTLOADER_LOG_HANDLER
#define OPEN_CFW_BOOTLOADER_LOG_HANDLER() \
    (*(open_cfw_bootloader_log_handler_fn *)(void *)0x200270CCU)
#endif

#ifndef OPEN_CFW_BOOTLOADER_LOG_CONTEXT
#define OPEN_CFW_BOOTLOADER_LOG_CONTEXT ((char *)(void *)0x20024CD0U)
#endif

#ifndef OPEN_CFW_BOOTLOADER_LOG_ARGUMENT_CURSOR
#define OPEN_CFW_BOOTLOADER_LOG_ARGUMENT_CURSOR(arguments) ((arguments).__ap)
#endif

#ifndef OPEN_CFW_BOOTLOADER_LOG_VFORMAT
#define OPEN_CFW_BOOTLOADER_LOG_VFORMAT(output, format, arguments) \
    open_cfw_bootloader_format_core((output), (format), (arguments))
#endif

unsigned int open_cfw_bootloader_format_core(
    char *output,
    const char *format,
    void *argument_cursor
);

__attribute__((used, noinline))
unsigned int open_cfw_bootloader_log_dispatch(const char *format, ...)
{
    open_cfw_bootloader_log_handler_fn handler =
        OPEN_CFW_BOOTLOADER_LOG_HANDLER();
    __builtin_va_list arguments;
    unsigned int result;

    if (handler == (open_cfw_bootloader_log_handler_fn)0) {
        return 0U;
    }
    __builtin_va_start(arguments, format);
    result = OPEN_CFW_BOOTLOADER_LOG_VFORMAT(
        OPEN_CFW_BOOTLOADER_LOG_CONTEXT,
        format,
        OPEN_CFW_BOOTLOADER_LOG_ARGUMENT_CURSOR(arguments)
    );
    __builtin_va_end(arguments);
    handler = OPEN_CFW_BOOTLOADER_LOG_HANDLER();
    handler(OPEN_CFW_BOOTLOADER_LOG_CONTEXT);
    return result;
}
