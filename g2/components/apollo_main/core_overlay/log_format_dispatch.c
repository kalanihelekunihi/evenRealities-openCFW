/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the G2 2.2.6.10 application-wide variadic logging
 * wrapper at 0x004733EE.
 */

typedef void (*open_cfw_log_format_handler_fn)(void *context);

typedef unsigned int (*open_cfw_log_format_vformat_fn)(
    char *destination,
    const char *format,
    void *arguments
);

#ifndef OPEN_CFW_LOG_FORMAT_HANDLER
#define OPEN_CFW_LOG_FORMAT_HANDLER() \
    (*(open_cfw_log_format_handler_fn *)(void *)0x200742F0U)
#endif

#ifndef OPEN_CFW_LOG_FORMAT_CONTEXT
#define OPEN_CFW_LOG_FORMAT_CONTEXT ((void *)0x2006B930U)
#endif

#ifndef OPEN_CFW_LOG_FORMAT_ARGUMENT_CURSOR
#define OPEN_CFW_LOG_FORMAT_ARGUMENT_CURSOR(arguments) ((arguments).__ap)
#endif

#ifndef OPEN_CFW_LOG_FORMAT_VFORMAT
#define OPEN_CFW_LOG_FORMAT_VFORMAT(destination, format, arguments) \
    (((open_cfw_log_format_vformat_fn)0x00473037U)( \
        (char *)(destination), \
        (format), \
        (void *)(arguments) \
    ))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_log_format_dispatch(const char *format, ...)
{
    open_cfw_log_format_handler_fn handler =
        OPEN_CFW_LOG_FORMAT_HANDLER();
    __builtin_va_list arguments;
    unsigned int result;

    if (handler == (open_cfw_log_format_handler_fn)0) {
        return 0U;
    }
    __builtin_va_start(arguments, format);
    result = OPEN_CFW_LOG_FORMAT_VFORMAT(
        OPEN_CFW_LOG_FORMAT_CONTEXT,
        format,
        OPEN_CFW_LOG_FORMAT_ARGUMENT_CURSOR(arguments)
    );
    __builtin_va_end(arguments);
    handler = OPEN_CFW_LOG_FORMAT_HANDLER();
    handler(OPEN_CFW_LOG_FORMAT_CONTEXT);
    return result;
}
