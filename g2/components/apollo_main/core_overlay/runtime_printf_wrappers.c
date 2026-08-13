/*
 * SPDX-License-Identifier: MIT
 *
 * Copyright (c) 2014-2019 Marco Paland
 *
 * Source recovery of the two consecutive mpaland public wrappers:
 *   0x00483FD0...0x00483FE9  snprintf_
 *   0x00483FEA...0x00483FFB  vsnprintf_
 */

#ifndef OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
#define OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
typedef void (*open_cfw_runtime_ntoa_output_fn)(
    char,
    void *,
    unsigned int,
    unsigned int
);
#endif

#ifndef OPEN_CFW_RUNTIME_PRINTF_BUFFER_OUTPUT
void open_cfw_runtime_printf_buffer_output(
    char value,
    void *buffer,
    unsigned int index,
    unsigned int capacity
)
    __asm__("open_cfw_runtime_bounded_byte_store");
#define OPEN_CFW_RUNTIME_PRINTF_BUFFER_OUTPUT \
    open_cfw_runtime_printf_buffer_output
#endif

#ifndef OPEN_CFW_RUNTIME_PRINTF_VSNPRINTF
int open_cfw_runtime_printf_vsnprintf(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    unsigned int maximum_length,
    const unsigned char *format,
    __builtin_va_list arguments
)
    __asm__("open_cfw_runtime_vsnprintf");

#define OPEN_CFW_RUNTIME_PRINTF_VSNPRINTF( \
    output, buffer, maximum_length, format, arguments \
) \
    open_cfw_runtime_printf_vsnprintf( \
        (output), \
        (buffer), \
        (maximum_length), \
        (format), \
        (arguments) \
    )
#endif

__attribute__((used, noinline))
int open_cfw_runtime_snprintf(
    unsigned char *buffer,
    unsigned int count,
    const unsigned char *format,
    ...
)
{
    __builtin_va_list arguments;
    int result;

    __builtin_va_start(arguments, format);
    result = OPEN_CFW_RUNTIME_PRINTF_VSNPRINTF(
        OPEN_CFW_RUNTIME_PRINTF_BUFFER_OUTPUT,
        buffer,
        count,
        format,
        arguments
    );
    __builtin_va_end(arguments);
    return result;
}

__attribute__((used, noinline))
int open_cfw_runtime_vsnprintf_wrapper(
    unsigned char *buffer,
    unsigned int count,
    const unsigned char *format,
    __builtin_va_list arguments
)
{
    return OPEN_CFW_RUNTIME_PRINTF_VSNPRINTF(
        OPEN_CFW_RUNTIME_PRINTF_BUFFER_OUTPUT,
        buffer,
        count,
        format,
        arguments
    );
}

#undef OPEN_CFW_RUNTIME_PRINTF_BUFFER_OUTPUT
#undef OPEN_CFW_RUNTIME_PRINTF_VSNPRINTF
