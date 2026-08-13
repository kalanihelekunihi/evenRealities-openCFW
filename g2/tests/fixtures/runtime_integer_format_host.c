/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host adapter for the source-owned G2 integer-formatting helper.
 */

#define OPEN_CFW_TEST_INTEGER_FORMAT_BASE 0x20000000U
#define OPEN_CFW_TEST_INTEGER_FORMAT_SCRATCH_OFFSET 32U

static unsigned char open_cfw_test_integer_format_memory[128];

static unsigned char *open_cfw_test_integer_format_pointer_to_bytes(
    unsigned int pointer
);
static unsigned int open_cfw_test_integer_format_bytes_to_pointer(
    unsigned char *bytes
);
static unsigned int open_cfw_test_integer_format_ascii_fold(
    unsigned int value
);
struct open_cfw_aeabi_divmod_result;
static void open_cfw_test_integer_format_divmod(
    unsigned int dividend_low,
    unsigned int dividend_high,
    unsigned int divisor_low,
    unsigned int divisor_high,
    struct open_cfw_aeabi_divmod_result *result
);

#define OPEN_CFW_INTEGER_FORMAT_POINTER_TYPE unsigned int
#define OPEN_CFW_INTEGER_FORMAT_POINTER_TO_BYTES(value) \
    open_cfw_test_integer_format_pointer_to_bytes(value)
#define OPEN_CFW_INTEGER_FORMAT_BYTES_TO_POINTER(value) \
    open_cfw_test_integer_format_bytes_to_pointer(value)
#define OPEN_CFW_INTEGER_FORMAT_POINTER_ADDRESS(value) (value)
#define OPEN_CFW_INTEGER_FORMAT_ASCII_FOLD(value) \
    open_cfw_test_integer_format_ascii_fold(value)
#define OPEN_CFW_INTEGER_FORMAT_DIVMOD( \
    dividend_low, \
    dividend_high, \
    divisor_low, \
    divisor_high, \
    result \
) \
    open_cfw_test_integer_format_divmod( \
        (dividend_low), \
        (dividend_high), \
        (divisor_low), \
        (divisor_high), \
        (result) \
    )

#include "../../components/apollo_main/core_overlay/runtime_integer_format.c"

static struct open_cfw_integer_format_context
    open_cfw_test_integer_format_state;

unsigned int open_cfw_test_integer_format_ascii_calls;
unsigned int open_cfw_test_integer_format_ascii_input;
unsigned int open_cfw_test_integer_format_divmod_calls;
unsigned int open_cfw_test_integer_format_last_divisor_low;
unsigned int open_cfw_test_integer_format_last_divisor_high;

static unsigned char *open_cfw_test_integer_format_pointer_to_bytes(
    unsigned int pointer
)
{
    return open_cfw_test_integer_format_memory
        + (pointer - OPEN_CFW_TEST_INTEGER_FORMAT_BASE);
}

static unsigned int open_cfw_test_integer_format_bytes_to_pointer(
    unsigned char *bytes
)
{
    return OPEN_CFW_TEST_INTEGER_FORMAT_BASE
        + (unsigned int)(
            bytes - open_cfw_test_integer_format_memory
        );
}

static unsigned int open_cfw_test_integer_format_ascii_fold(
    unsigned int value
)
{
    open_cfw_test_integer_format_ascii_calls += 1U;
    open_cfw_test_integer_format_ascii_input = value;
    return value | 0x20U;
}

static void open_cfw_test_integer_format_divmod(
    unsigned int dividend_low,
    unsigned int dividend_high,
    unsigned int divisor_low,
    unsigned int divisor_high,
    struct open_cfw_aeabi_divmod_result *result
)
{
    unsigned long long dividend =
        ((unsigned long long)dividend_high << 32U) | dividend_low;
    unsigned long long divisor =
        ((unsigned long long)divisor_high << 32U) | divisor_low;
    unsigned long long quotient = dividend / divisor;
    unsigned long long remainder = dividend % divisor;

    open_cfw_test_integer_format_divmod_calls += 1U;
    open_cfw_test_integer_format_last_divisor_low = divisor_low;
    open_cfw_test_integer_format_last_divisor_high = divisor_high;
    result->quotient_low = (unsigned int)quotient;
    result->quotient_high = (unsigned int)(quotient >> 32U);
    result->remainder_low = (unsigned int)remainder;
    result->remainder_high = (unsigned int)(remainder >> 32U);
}

void open_cfw_test_integer_format_reset(
    unsigned int value_low,
    unsigned int value_high,
    unsigned int digit_limit_offset,
    unsigned int prefix_length,
    unsigned int zero_padding,
    int precision,
    int field_width,
    unsigned int flags
)
{
    unsigned int index;

    for (index = 0U; index < sizeof(open_cfw_test_integer_format_memory);
         index += 1U) {
        open_cfw_test_integer_format_memory[index] = 0xa5U;
    }

    open_cfw_test_integer_format_state.value =
        ((open_cfw_integer_format_u64)value_high << 32U) | value_low;
    open_cfw_test_integer_format_state.reserved_08 = 0x08080808U;
    open_cfw_test_integer_format_state.digits =
        OPEN_CFW_TEST_INTEGER_FORMAT_BASE
        + OPEN_CFW_TEST_INTEGER_FORMAT_SCRATCH_OFFSET
        + digit_limit_offset;
    open_cfw_test_integer_format_state.scratch =
        OPEN_CFW_TEST_INTEGER_FORMAT_BASE
        + OPEN_CFW_TEST_INTEGER_FORMAT_SCRATCH_OFFSET;
    open_cfw_test_integer_format_state.prefix_length = prefix_length;
    open_cfw_test_integer_format_state.digit_length = 0x18181818U;
    open_cfw_test_integer_format_state.reserved_1c = 0x1c1c1c1cU;
    open_cfw_test_integer_format_state.zero_padding = zero_padding;
    open_cfw_test_integer_format_state.reserved_24 = 0x24242424U;
    open_cfw_test_integer_format_state.reserved_28 = 0x28282828U;
    open_cfw_test_integer_format_state.reserved_2c = 0x2c2c2c2cU;
    open_cfw_test_integer_format_state.precision = precision;
    open_cfw_test_integer_format_state.field_width = field_width;
    open_cfw_test_integer_format_state.flags = (unsigned short)flags;
    open_cfw_test_integer_format_ascii_calls = 0U;
    open_cfw_test_integer_format_ascii_input = 0U;
    open_cfw_test_integer_format_divmod_calls = 0U;
    open_cfw_test_integer_format_last_divisor_low = 0U;
    open_cfw_test_integer_format_last_divisor_high = 0U;
}

void open_cfw_test_integer_format_execute(unsigned int specifier)
{
    open_cfw_integer_format(
        &open_cfw_test_integer_format_state,
        specifier
    );
}

void *open_cfw_test_integer_format_context(void)
{
    return &open_cfw_test_integer_format_state;
}

unsigned char *open_cfw_test_integer_format_scratch(void)
{
    return open_cfw_test_integer_format_memory
        + OPEN_CFW_TEST_INTEGER_FORMAT_SCRATCH_OFFSET;
}
