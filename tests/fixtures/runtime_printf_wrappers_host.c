/*
 * SPDX-License-Identifier: MIT
 *
 * Host fixture for the source-owned snprintf_/vsnprintf_ wrappers.
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

static void open_cfw_test_runtime_printf_buffer_output(
    char,
    void *,
    unsigned int,
    unsigned int
);
static int open_cfw_test_runtime_printf_vsnprintf(
    open_cfw_runtime_ntoa_output_fn,
    void *,
    unsigned int,
    const unsigned char *,
    __builtin_va_list
);

#define OPEN_CFW_RUNTIME_PRINTF_BUFFER_OUTPUT \
    open_cfw_test_runtime_printf_buffer_output
#define OPEN_CFW_RUNTIME_PRINTF_VSNPRINTF( \
    output, buffer, maximum_length, format, arguments \
) \
    open_cfw_test_runtime_printf_vsnprintf( \
        (output), (buffer), (maximum_length), (format), (arguments) \
    )

#include "../../components/apollo_main/core_overlay/runtime_printf_wrappers.c"

unsigned char open_cfw_test_runtime_printf_buffer[32];
static const unsigned char open_cfw_test_runtime_printf_format[] =
    "%d:%x:%c";
unsigned int open_cfw_test_runtime_printf_calls;
__UINTPTR_TYPE__ open_cfw_test_runtime_printf_output;
__UINTPTR_TYPE__ open_cfw_test_runtime_printf_observed_buffer;
__UINTPTR_TYPE__ open_cfw_test_runtime_printf_observed_format;
unsigned int open_cfw_test_runtime_printf_maximum_length;
int open_cfw_test_runtime_printf_argument[3];
int open_cfw_test_runtime_printf_return;

static void open_cfw_test_runtime_printf_buffer_output(
    char character,
    void *buffer,
    unsigned int index,
    unsigned int capacity
)
{
    (void)character;
    (void)buffer;
    (void)index;
    (void)capacity;
}

static int open_cfw_test_runtime_printf_vsnprintf(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    unsigned int maximum_length,
    const unsigned char *format,
    __builtin_va_list arguments
)
{
    unsigned int index;

    open_cfw_test_runtime_printf_calls += 1U;
    open_cfw_test_runtime_printf_output = (__UINTPTR_TYPE__)output;
    open_cfw_test_runtime_printf_observed_buffer =
        (__UINTPTR_TYPE__)buffer;
    open_cfw_test_runtime_printf_observed_format =
        (__UINTPTR_TYPE__)format;
    open_cfw_test_runtime_printf_maximum_length = maximum_length;
    for (index = 0U; index < 3U; index += 1U) {
        open_cfw_test_runtime_printf_argument[index] =
            __builtin_va_arg(arguments, int);
    }
    return open_cfw_test_runtime_printf_return;
}

void open_cfw_test_runtime_printf_reset(int return_value)
{
    unsigned int index;

    for (index = 0U; index < 32U; index += 1U) {
        open_cfw_test_runtime_printf_buffer[index] = 0xC3U;
    }
    open_cfw_test_runtime_printf_calls = 0U;
    open_cfw_test_runtime_printf_output = 0U;
    open_cfw_test_runtime_printf_observed_buffer = 0U;
    open_cfw_test_runtime_printf_observed_format = 0U;
    open_cfw_test_runtime_printf_maximum_length = 0U;
    open_cfw_test_runtime_printf_argument[0] = 0;
    open_cfw_test_runtime_printf_argument[1] = 0;
    open_cfw_test_runtime_printf_argument[2] = 0;
    open_cfw_test_runtime_printf_return = return_value;
}

int open_cfw_test_runtime_printf_execute_snprintf(
    unsigned int count,
    int first,
    int second,
    int third
)
{
    return open_cfw_runtime_snprintf(
        open_cfw_test_runtime_printf_buffer,
        count,
        open_cfw_test_runtime_printf_format,
        first,
        second,
        third
    );
}

int open_cfw_test_runtime_printf_execute_vsnprintf(
    unsigned int count,
    ...
)
{
    __builtin_va_list arguments;
    int result;

    __builtin_va_start(arguments, count);
    result = open_cfw_runtime_vsnprintf_wrapper(
        open_cfw_test_runtime_printf_buffer,
        count,
        open_cfw_test_runtime_printf_format,
        arguments
    );
    __builtin_va_end(arguments);
    return result;
}
