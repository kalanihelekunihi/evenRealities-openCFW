/*
 * SPDX-License-Identifier: MIT
 *
 * Host substitutions for the source-owned mpaland integer converters.
 */

typedef __UINT64_TYPE__ open_cfw_test_runtime_ntoa_u64;
#ifndef OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
#define OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
typedef void (*open_cfw_runtime_ntoa_output_fn)(
    char,
    void *,
    unsigned int,
    unsigned int
);
#endif

struct open_cfw_aeabi_divmod_result;

static void open_cfw_test_runtime_ntoa_divmod_u64(
    open_cfw_test_runtime_ntoa_u64 value,
    open_cfw_test_runtime_ntoa_u64 base,
    struct open_cfw_aeabi_divmod_result *result
);
static unsigned int open_cfw_test_runtime_ntoa_format(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length,
    char *digits,
    unsigned int digit_count,
    _Bool negative,
    unsigned int base,
    unsigned int precision,
    unsigned int width,
    unsigned int flags
);

#define OPEN_CFW_RUNTIME_NTOA_DIVMOD_U64(value, base, result) \
    open_cfw_test_runtime_ntoa_divmod_u64( \
        (value), \
        (base), \
        (result) \
    )
#define OPEN_CFW_RUNTIME_NTOA_FORMAT( \
    output, \
    buffer, \
    index, \
    maximum_length, \
    digits, \
    digit_count, \
    negative, \
    base, \
    precision, \
    width, \
    flags \
) \
    open_cfw_test_runtime_ntoa_format( \
        (output), \
        (buffer), \
        (index), \
        (maximum_length), \
        (digits), \
        (digit_count), \
        (negative), \
        (base), \
        (precision), \
        (width), \
        (flags) \
    )

#include "../../components/apollo_main/core_overlay/runtime_ntoa_integer.c"

enum {
    OPEN_CFW_TEST_RUNTIME_NTOA_DIVISION_CAPACITY = 32U
};

unsigned char open_cfw_test_runtime_ntoa_output_buffer[16];
unsigned int open_cfw_test_runtime_ntoa_format_calls;
__UINTPTR_TYPE__ open_cfw_test_runtime_ntoa_observed_output;
__UINTPTR_TYPE__ open_cfw_test_runtime_ntoa_observed_buffer;
unsigned int open_cfw_test_runtime_ntoa_observed_index;
unsigned int open_cfw_test_runtime_ntoa_observed_maximum_length;
unsigned char open_cfw_test_runtime_ntoa_observed_digits[32];
unsigned int open_cfw_test_runtime_ntoa_observed_digit_count;
unsigned int open_cfw_test_runtime_ntoa_observed_negative;
unsigned int open_cfw_test_runtime_ntoa_observed_base;
unsigned int open_cfw_test_runtime_ntoa_observed_precision;
unsigned int open_cfw_test_runtime_ntoa_observed_width;
unsigned int open_cfw_test_runtime_ntoa_observed_flags;
unsigned int open_cfw_test_runtime_ntoa_format_return;

unsigned int open_cfw_test_runtime_ntoa_division_calls;
open_cfw_test_runtime_ntoa_u64
    open_cfw_test_runtime_ntoa_division_value[
        OPEN_CFW_TEST_RUNTIME_NTOA_DIVISION_CAPACITY
    ];
open_cfw_test_runtime_ntoa_u64
    open_cfw_test_runtime_ntoa_division_base[
        OPEN_CFW_TEST_RUNTIME_NTOA_DIVISION_CAPACITY
    ];
open_cfw_test_runtime_ntoa_u64
    open_cfw_test_runtime_ntoa_division_quotient[
        OPEN_CFW_TEST_RUNTIME_NTOA_DIVISION_CAPACITY
    ];
open_cfw_test_runtime_ntoa_u64
    open_cfw_test_runtime_ntoa_division_remainder[
        OPEN_CFW_TEST_RUNTIME_NTOA_DIVISION_CAPACITY
    ];

static void open_cfw_test_runtime_ntoa_output(
    char character,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length
)
{
    (void)character;
    (void)buffer;
    (void)index;
    (void)maximum_length;
}

static void open_cfw_test_runtime_ntoa_divmod_u64(
    open_cfw_test_runtime_ntoa_u64 value,
    open_cfw_test_runtime_ntoa_u64 base,
    struct open_cfw_aeabi_divmod_result *result
)
{
    unsigned int index =
        open_cfw_test_runtime_ntoa_division_calls;
    open_cfw_test_runtime_ntoa_u64 quotient = value / base;
    open_cfw_test_runtime_ntoa_u64 remainder = value % base;

    if (index < OPEN_CFW_TEST_RUNTIME_NTOA_DIVISION_CAPACITY) {
        open_cfw_test_runtime_ntoa_division_value[index] = value;
        open_cfw_test_runtime_ntoa_division_base[index] = base;
        open_cfw_test_runtime_ntoa_division_quotient[index] = quotient;
        open_cfw_test_runtime_ntoa_division_remainder[index] =
            remainder;
    }
    open_cfw_test_runtime_ntoa_division_calls = index + 1U;

    result->quotient_low = (unsigned int)quotient;
    result->quotient_high = (unsigned int)(quotient >> 32U);
    result->remainder_low = (unsigned int)remainder;
    result->remainder_high = (unsigned int)(remainder >> 32U);
}

static unsigned int open_cfw_test_runtime_ntoa_format(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length,
    char *digits,
    unsigned int digit_count,
    _Bool negative,
    unsigned int base,
    unsigned int precision,
    unsigned int width,
    unsigned int flags
)
{
    unsigned int digit_index;

    open_cfw_test_runtime_ntoa_format_calls += 1U;
    open_cfw_test_runtime_ntoa_observed_output =
        (__UINTPTR_TYPE__)output;
    open_cfw_test_runtime_ntoa_observed_buffer =
        (__UINTPTR_TYPE__)buffer;
    open_cfw_test_runtime_ntoa_observed_index = index;
    open_cfw_test_runtime_ntoa_observed_maximum_length =
        maximum_length;
    open_cfw_test_runtime_ntoa_observed_digit_count = digit_count;
    open_cfw_test_runtime_ntoa_observed_negative =
        negative ? 1U : 0U;
    open_cfw_test_runtime_ntoa_observed_base = base;
    open_cfw_test_runtime_ntoa_observed_precision = precision;
    open_cfw_test_runtime_ntoa_observed_width = width;
    open_cfw_test_runtime_ntoa_observed_flags = flags;

    for (
        digit_index = 0U;
        digit_index < digit_count
            && digit_index < OPEN_CFW_RUNTIME_NTOA_BUFFER_SIZE;
        digit_index += 1U
    ) {
        open_cfw_test_runtime_ntoa_observed_digits[digit_index] =
            (unsigned char)digits[digit_index];
    }
    return open_cfw_test_runtime_ntoa_format_return;
}

void open_cfw_test_runtime_ntoa_reset(unsigned int return_value)
{
    unsigned int index;

    for (index = 0U; index < 16U; index += 1U) {
        open_cfw_test_runtime_ntoa_output_buffer[index] = 0xC3U;
    }
    for (
        index = 0U;
        index < OPEN_CFW_RUNTIME_NTOA_BUFFER_SIZE;
        index += 1U
    ) {
        open_cfw_test_runtime_ntoa_observed_digits[index] = 0xA5U;
        open_cfw_test_runtime_ntoa_division_value[index] = 0U;
        open_cfw_test_runtime_ntoa_division_base[index] = 0U;
        open_cfw_test_runtime_ntoa_division_quotient[index] = 0U;
        open_cfw_test_runtime_ntoa_division_remainder[index] = 0U;
    }
    open_cfw_test_runtime_ntoa_format_calls = 0U;
    open_cfw_test_runtime_ntoa_observed_output = 0U;
    open_cfw_test_runtime_ntoa_observed_buffer = 0U;
    open_cfw_test_runtime_ntoa_observed_index = 0U;
    open_cfw_test_runtime_ntoa_observed_maximum_length = 0U;
    open_cfw_test_runtime_ntoa_observed_digit_count = 0U;
    open_cfw_test_runtime_ntoa_observed_negative = 0U;
    open_cfw_test_runtime_ntoa_observed_base = 0U;
    open_cfw_test_runtime_ntoa_observed_precision = 0U;
    open_cfw_test_runtime_ntoa_observed_width = 0U;
    open_cfw_test_runtime_ntoa_observed_flags = 0U;
    open_cfw_test_runtime_ntoa_format_return = return_value;
    open_cfw_test_runtime_ntoa_division_calls = 0U;
}

unsigned int open_cfw_test_runtime_ntoa_execute_long(
    unsigned int value,
    unsigned int negative,
    unsigned int base,
    unsigned int precision,
    unsigned int width,
    unsigned int flags,
    unsigned int index,
    unsigned int maximum_length
)
{
    return open_cfw_runtime_ntoa_long(
        open_cfw_test_runtime_ntoa_output,
        open_cfw_test_runtime_ntoa_output_buffer,
        index,
        maximum_length,
        value,
        negative != 0U,
        base,
        precision,
        width,
        flags
    );
}

unsigned int open_cfw_test_runtime_ntoa_execute_long_long(
    unsigned int value_low,
    unsigned int value_high,
    unsigned int negative,
    unsigned int base_low,
    unsigned int base_high,
    unsigned int precision,
    unsigned int width,
    unsigned int flags,
    unsigned int index,
    unsigned int maximum_length
)
{
    return open_cfw_runtime_ntoa_long_long(
        open_cfw_test_runtime_ntoa_output,
        open_cfw_test_runtime_ntoa_output_buffer,
        index,
        maximum_length,
        open_cfw_runtime_ntoa_join(value_low, value_high),
        negative != 0U,
        open_cfw_runtime_ntoa_join(base_low, base_high),
        precision,
        width,
        flags
    );
}
