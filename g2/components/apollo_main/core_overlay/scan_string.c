/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded string-input scanner adapter matched to the stock wrapper at
 * 0x00475FC0 and its computed input callback at 0x00439BC6.
 */

typedef unsigned int (*open_cfw_scan_string_reader_function)(
    const unsigned char **cursor,
    unsigned int value,
    int read
);

typedef int (*open_cfw_scan_string_core_function)(
    open_cfw_scan_string_reader_function reader,
    const unsigned char **cursor,
    const char *format,
    void **arguments,
    int secure
);

#ifndef OPEN_CFW_SCAN_STRING_CORE
#define OPEN_CFW_SCAN_STRING_CORE( \
    reader, cursor, format, arguments, secure \
) \
    (((open_cfw_scan_string_core_function)0x004D1639U)( \
        (reader), \
        (cursor), \
        (format), \
        (arguments), \
        (secure) \
    ))
#endif

#ifndef OPEN_CFW_SCAN_STRING_ARGUMENT_CURSOR
#define OPEN_CFW_SCAN_STRING_ARGUMENT_CURSOR(arguments) \
    ((void *)(arguments).__ap)
#endif

__attribute__((used, noinline))
unsigned int open_cfw_scan_string_reader(
    const unsigned char **cursor,
    unsigned int value,
    int read
)
{
    const unsigned char *current = *cursor;

    if (read == 0) {
        *cursor = current - 1;
        return value;
    }
    if (*current == 0U) {
        return 0xFFFFFFFFU;
    }

    *cursor = current + 1;
    return *current;
}

__attribute__((used, noinline))
int open_cfw_scan_string(const char *input, const char *format, ...)
{
    const unsigned char *cursor = (const unsigned char *)input;
    __builtin_va_list arguments;
    void *argument_cursor;
    int result;

    __builtin_va_start(arguments, format);
    argument_cursor = OPEN_CFW_SCAN_STRING_ARGUMENT_CURSOR(arguments);
    result = OPEN_CFW_SCAN_STRING_CORE(
        open_cfw_scan_string_reader,
        &cursor,
        format,
        &argument_cursor,
        0
    );
    __builtin_va_end(arguments);
    return result;
}
