/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for the bounded variadic string-scanner adapter.
 */

typedef unsigned int (*open_cfw_test_scan_string_reader_function)(
    const unsigned char **,
    unsigned int,
    int
);

int open_cfw_test_scan_string_core(
    open_cfw_test_scan_string_reader_function reader,
    const unsigned char **cursor,
    const char *format,
    void **arguments,
    int secure
);

#define OPEN_CFW_SCAN_STRING_CORE( \
    reader, cursor, format, arguments, secure \
) \
    open_cfw_test_scan_string_core( \
        (reader), \
        (cursor), \
        (format), \
        (arguments), \
        (secure) \
    )
#define OPEN_CFW_SCAN_STRING_ARGUMENT_CURSOR(arguments) \
    ((void *)(arguments))

unsigned int open_cfw_test_scan_string_calls;
__UINTPTR_TYPE__ open_cfw_test_scan_string_reader;
__UINTPTR_TYPE__ open_cfw_test_scan_string_cursor;
__UINTPTR_TYPE__ open_cfw_test_scan_string_input;
__UINTPTR_TYPE__ open_cfw_test_scan_string_format;
__UINTPTR_TYPE__ open_cfw_test_scan_string_arguments;
int open_cfw_test_scan_string_secure;
int open_cfw_test_scan_string_result;
int open_cfw_test_scan_string_argument_values[4];

void open_cfw_test_scan_string_reset(void)
{
    unsigned int index;

    open_cfw_test_scan_string_calls = 0U;
    open_cfw_test_scan_string_reader = 0U;
    open_cfw_test_scan_string_cursor = 0U;
    open_cfw_test_scan_string_input = 0U;
    open_cfw_test_scan_string_format = 0U;
    open_cfw_test_scan_string_arguments = 0U;
    open_cfw_test_scan_string_secure = -1;
    open_cfw_test_scan_string_result = 0;
    for (index = 0U; index < 4U; ++index) {
        open_cfw_test_scan_string_argument_values[index] = 0;
    }
}

int open_cfw_test_scan_string_core(
    open_cfw_test_scan_string_reader_function reader,
    const unsigned char **cursor,
    const char *format,
    void **arguments,
    int secure
)
{
    __builtin_va_list copy;
#if defined(__APPLE__) && defined(__aarch64__)
    __builtin_va_list source = (__builtin_va_list)*arguments;
#else
    __builtin_va_list *source = (__builtin_va_list *)*arguments;
#endif
    unsigned int index;

    ++open_cfw_test_scan_string_calls;
    open_cfw_test_scan_string_reader =
        (__UINTPTR_TYPE__)reader;
    open_cfw_test_scan_string_cursor =
        (__UINTPTR_TYPE__)cursor;
    open_cfw_test_scan_string_input =
        (__UINTPTR_TYPE__)*cursor;
    open_cfw_test_scan_string_format =
        (__UINTPTR_TYPE__)format;
    open_cfw_test_scan_string_arguments =
        (__UINTPTR_TYPE__)*arguments;
    open_cfw_test_scan_string_secure = secure;

#if defined(__APPLE__) && defined(__aarch64__)
    __builtin_va_copy(copy, source);
#else
    __builtin_va_copy(copy, *source);
#endif
    for (index = 0U; index < 4U; ++index) {
        open_cfw_test_scan_string_argument_values[index] =
            __builtin_va_arg(copy, int);
    }
    __builtin_va_end(copy);
    return open_cfw_test_scan_string_result;
}

#include "../../components/apollo_main/core_overlay/scan_string.c"
