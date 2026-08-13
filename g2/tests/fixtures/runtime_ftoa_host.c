/*
 * SPDX-License-Identifier: MIT
 *
 * Host observations for the source-owned mpaland fixed-point converter.
 */

#include <string.h>

#ifndef OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
#define OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
typedef void (*open_cfw_runtime_ntoa_output_fn)(
    char,
    void *,
    unsigned int,
    unsigned int
);
#endif

static unsigned int open_cfw_test_runtime_ftoa_out_reverse(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length,
    const char *reverse_buffer,
    unsigned int length,
    unsigned int width,
    unsigned int flags
);
static unsigned int open_cfw_test_runtime_ftoa_etoa(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length,
    double value,
    unsigned int precision,
    unsigned int width,
    unsigned int flags
);

#define OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE( \
    output, \
    buffer, \
    index, \
    maximum_length, \
    reverse_buffer, \
    length, \
    width, \
    flags \
) \
    open_cfw_test_runtime_ftoa_out_reverse( \
        (output), \
        (buffer), \
        (index), \
        (maximum_length), \
        (reverse_buffer), \
        (length), \
        (width), \
        (flags) \
    )
#define OPEN_CFW_RUNTIME_FTOA_ETOA( \
    output, \
    buffer, \
    index, \
    maximum_length, \
    value, \
    precision, \
    width, \
    flags \
) \
    open_cfw_test_runtime_ftoa_etoa( \
        (output), \
        (buffer), \
        (index), \
        (maximum_length), \
        (value), \
        (precision), \
        (width), \
        (flags) \
    )

#include "../../components/apollo_main/core_overlay/runtime_ftoa.c"

unsigned int open_cfw_test_runtime_ftoa_out_calls;
unsigned int open_cfw_test_runtime_ftoa_etoa_calls;
__UINTPTR_TYPE__ open_cfw_test_runtime_ftoa_output_token;
__UINTPTR_TYPE__ open_cfw_test_runtime_ftoa_buffer_token;
unsigned int open_cfw_test_runtime_ftoa_index;
unsigned int open_cfw_test_runtime_ftoa_maximum_length;
unsigned int open_cfw_test_runtime_ftoa_length;
unsigned int open_cfw_test_runtime_ftoa_width;
unsigned int open_cfw_test_runtime_ftoa_flags;
unsigned char open_cfw_test_runtime_ftoa_reverse[32];
unsigned long long open_cfw_test_runtime_ftoa_etoa_value_bits;
unsigned int open_cfw_test_runtime_ftoa_out_return;
unsigned int open_cfw_test_runtime_ftoa_etoa_return;

static unsigned long long open_cfw_test_runtime_ftoa_bits(double value)
{
    union {
        double floating;
        unsigned long long bits;
    } representation;

    representation.floating = value;
    return representation.bits;
}

static unsigned int open_cfw_test_runtime_ftoa_out_reverse(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length,
    const char *reverse_buffer,
    unsigned int length,
    unsigned int width,
    unsigned int flags
)
{
    unsigned int character;

    open_cfw_test_runtime_ftoa_out_calls += 1U;
    open_cfw_test_runtime_ftoa_output_token = (__UINTPTR_TYPE__)output;
    open_cfw_test_runtime_ftoa_buffer_token = (__UINTPTR_TYPE__)buffer;
    open_cfw_test_runtime_ftoa_index = index;
    open_cfw_test_runtime_ftoa_maximum_length = maximum_length;
    open_cfw_test_runtime_ftoa_length = length;
    open_cfw_test_runtime_ftoa_width = width;
    open_cfw_test_runtime_ftoa_flags = flags;
    for (
        character = 0U;
        character < length && character < 32U;
        character += 1U
    ) {
        open_cfw_test_runtime_ftoa_reverse[character] =
            (unsigned char)reverse_buffer[character];
    }
    return open_cfw_test_runtime_ftoa_out_return;
}

static unsigned int open_cfw_test_runtime_ftoa_etoa(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length,
    double value,
    unsigned int precision,
    unsigned int width,
    unsigned int flags
)
{
    open_cfw_test_runtime_ftoa_etoa_calls += 1U;
    open_cfw_test_runtime_ftoa_output_token = (__UINTPTR_TYPE__)output;
    open_cfw_test_runtime_ftoa_buffer_token = (__UINTPTR_TYPE__)buffer;
    open_cfw_test_runtime_ftoa_index = index;
    open_cfw_test_runtime_ftoa_maximum_length = maximum_length;
    open_cfw_test_runtime_ftoa_etoa_value_bits =
        open_cfw_test_runtime_ftoa_bits(value);
    open_cfw_test_runtime_ftoa_width = width;
    open_cfw_test_runtime_ftoa_flags = flags;
    open_cfw_test_runtime_ftoa_length = precision;
    return open_cfw_test_runtime_ftoa_etoa_return;
}

void open_cfw_test_runtime_ftoa_reset(
    unsigned int out_return,
    unsigned int etoa_return
)
{
    open_cfw_test_runtime_ftoa_out_calls = 0U;
    open_cfw_test_runtime_ftoa_etoa_calls = 0U;
    open_cfw_test_runtime_ftoa_output_token = 0U;
    open_cfw_test_runtime_ftoa_buffer_token = 0U;
    open_cfw_test_runtime_ftoa_index = 0U;
    open_cfw_test_runtime_ftoa_maximum_length = 0U;
    open_cfw_test_runtime_ftoa_length = 0U;
    open_cfw_test_runtime_ftoa_width = 0U;
    open_cfw_test_runtime_ftoa_flags = 0U;
    open_cfw_test_runtime_ftoa_etoa_value_bits = 0U;
    open_cfw_test_runtime_ftoa_out_return = out_return;
    open_cfw_test_runtime_ftoa_etoa_return = etoa_return;
    memset(open_cfw_test_runtime_ftoa_reverse, 0xA5, 32U);
}
