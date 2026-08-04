/*
 * SPDX-License-Identifier: MIT
 *
 * Host composition and observing seams for the source-owned _vsnprintf core.
 */

#include <stdarg.h>
#include <stdint.h>

#include "../../components/apollo_main/core_overlay/runtime_format_parse_helpers.c"
#include "../../components/apollo_main/core_overlay/runtime_format_out_reverse.c"
#include "../../components/apollo_main/core_overlay/runtime_ntoa_format.c"

#define OPEN_CFW_RUNTIME_NTOA_DIVMOD_U64(value, base, result) \
    do { \
        (result)->quotient_low = (unsigned int)((value) / (base)); \
        (result)->quotient_high = \
            (unsigned int)(((value) / (base)) >> 32U); \
        (result)->remainder_low = (unsigned int)((value) % (base)); \
        (result)->remainder_high = 0U; \
    } while (0)
#include "../../components/apollo_main/core_overlay/runtime_ntoa_integer.c"
#undef OPEN_CFW_RUNTIME_NTOA_DIVMOD_U64

#include "../../components/apollo_main/core_overlay/runtime_bounded_string_length.c"
#include "../../components/apollo_main/core_overlay/runtime_strnlen_s.c"
#include "../../components/apollo_main/core_overlay/runtime_etoa.c"
#include "../../components/apollo_main/core_overlay/runtime_ftoa.c"

static void open_cfw_test_runtime_vsnprintf_noop(
    char character,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length
)
{
    open_cfw_runtime_noop_output(
        (unsigned char)character,
        (unsigned char *)buffer,
        index,
        maximum_length
    );
}

#define OPEN_CFW_RUNTIME_VSNPRINTF_NOOP_OUTPUT \
    open_cfw_test_runtime_vsnprintf_noop
#define OPEN_CFW_RUNTIME_VSNPRINTF_STRING_LENGTH(string, maximum_length) \
    open_cfw_runtime_strnlen_s((string), (maximum_length))
#include "../../components/apollo_main/core_overlay/runtime_vsnprintf.c"

unsigned int open_cfw_test_runtime_vsnprintf_event_count;
unsigned int open_cfw_test_runtime_vsnprintf_characters[512];
unsigned int open_cfw_test_runtime_vsnprintf_indices[512];
unsigned int open_cfw_test_runtime_vsnprintf_maximum_lengths[512];
uintptr_t open_cfw_test_runtime_vsnprintf_buffers[512];

static void open_cfw_test_runtime_vsnprintf_store(
    char character,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length
)
{
    open_cfw_runtime_bounded_byte_store(
        (unsigned char)character,
        (unsigned char *)buffer,
        index,
        maximum_length
    );
}

static void open_cfw_test_runtime_vsnprintf_observe(
    char character,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length
)
{
    unsigned int event = open_cfw_test_runtime_vsnprintf_event_count;

    if (event < 512U) {
        open_cfw_test_runtime_vsnprintf_characters[event] =
            (unsigned char)character;
        open_cfw_test_runtime_vsnprintf_indices[event] = index;
        open_cfw_test_runtime_vsnprintf_maximum_lengths[event] =
            maximum_length;
        open_cfw_test_runtime_vsnprintf_buffers[event] =
            (uintptr_t)buffer;
    }
    open_cfw_test_runtime_vsnprintf_event_count = event + 1U;
}

void open_cfw_test_runtime_vsnprintf_reset(void)
{
    unsigned int index;

    open_cfw_test_runtime_vsnprintf_event_count = 0U;
    for (index = 0U; index < 512U; index += 1U) {
        open_cfw_test_runtime_vsnprintf_characters[index] = 0U;
        open_cfw_test_runtime_vsnprintf_indices[index] = 0U;
        open_cfw_test_runtime_vsnprintf_maximum_lengths[index] = 0U;
        open_cfw_test_runtime_vsnprintf_buffers[index] = 0U;
    }
}

unsigned int open_cfw_test_runtime_vsnprintf_magnitude_s32(int value)
{
    return open_cfw_runtime_vsnprintf_magnitude_s32(value);
}

uint64_t open_cfw_test_runtime_vsnprintf_magnitude_s64(int64_t value)
{
    return open_cfw_runtime_vsnprintf_magnitude_s64(value);
}

int open_cfw_test_runtime_vsnprintf_buffer(
    unsigned char *buffer,
    unsigned int maximum_length,
    const unsigned char *format,
    ...
)
{
    va_list arguments;
    int result;

    va_start(arguments, format);
    result = open_cfw_runtime_vsnprintf(
        open_cfw_test_runtime_vsnprintf_store,
        buffer,
        maximum_length,
        format,
        arguments
    );
    va_end(arguments);
    return result;
}

int open_cfw_test_runtime_vsnprintf_observer(
    uintptr_t buffer,
    unsigned int maximum_length,
    const unsigned char *format,
    ...
)
{
    va_list arguments;
    int result;

    va_start(arguments, format);
    result = open_cfw_runtime_vsnprintf(
        open_cfw_test_runtime_vsnprintf_observe,
        (unsigned char *)buffer,
        maximum_length,
        format,
        arguments
    );
    va_end(arguments);
    return result;
}

static int open_cfw_test_runtime_vsnprintf_outer(
    open_cfw_runtime_ntoa_output_fn output,
    unsigned char *buffer,
    unsigned int maximum_length,
    const unsigned char *format,
    ...
)
{
    va_list arguments;
    int result;

    va_start(arguments, format);
    result = open_cfw_runtime_vsnprintf(
        output,
        buffer,
        maximum_length,
        format,
        arguments
    );
    va_end(arguments);
    return result;
}

int open_cfw_test_runtime_vsnprintf_nested_buffer(
    unsigned char *buffer,
    unsigned int maximum_length,
    const unsigned char *nested_format,
    int outer_value,
    ...
)
{
    va_list nested_arguments;
    struct open_cfw_runtime_vsnprintf_recursive recursive;
    int result;

    va_start(nested_arguments, outer_value);
    recursive.format = nested_format;
    recursive.arguments = &nested_arguments;
    result = open_cfw_test_runtime_vsnprintf_outer(
        open_cfw_test_runtime_vsnprintf_store,
        buffer,
        maximum_length,
        (const unsigned char *)"A%100.2PVZ%d",
        &recursive,
        outer_value
    );
    va_end(nested_arguments);
    return result;
}

int open_cfw_test_runtime_vsnprintf_nested_observer(
    uintptr_t buffer,
    unsigned int maximum_length,
    const unsigned char *nested_format,
    int outer_value,
    ...
)
{
    va_list nested_arguments;
    struct open_cfw_runtime_vsnprintf_recursive recursive;
    int result;

    va_start(nested_arguments, outer_value);
    recursive.format = nested_format;
    recursive.arguments = &nested_arguments;
    result = open_cfw_test_runtime_vsnprintf_outer(
        open_cfw_test_runtime_vsnprintf_observe,
        (unsigned char *)buffer,
        maximum_length,
        (const unsigned char *)"A%100.2PVZ%d",
        &recursive,
        outer_value
    );
    va_end(nested_arguments);
    return result;
}

int open_cfw_test_runtime_vsnprintf_nested_lowercase(
    unsigned char *buffer,
    unsigned int maximum_length,
    const unsigned char *nested_format,
    int outer_value,
    ...
)
{
    va_list nested_arguments;
    struct open_cfw_runtime_vsnprintf_recursive recursive;
    int result;

    va_start(nested_arguments, outer_value);
    recursive.format = nested_format;
    recursive.arguments = &nested_arguments;
    result = open_cfw_test_runtime_vsnprintf_outer(
        open_cfw_test_runtime_vsnprintf_store,
        buffer,
        maximum_length,
        (const unsigned char *)"A%pVZ%d",
        &recursive,
        outer_value
    );
    va_end(nested_arguments);
    return result;
}
