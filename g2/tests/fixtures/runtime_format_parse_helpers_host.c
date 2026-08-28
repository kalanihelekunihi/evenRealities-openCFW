/*
 * SPDX-License-Identifier: MIT
 *
 * Host adapter and digit-query trace for the formatting parser helpers.
 */

unsigned int open_cfw_test_runtime_parse_digit_query_count;
unsigned int open_cfw_test_runtime_parse_digit_queries[128];

static unsigned int open_cfw_test_runtime_parse_is_digit(
    unsigned int value
)
{
    unsigned int index = open_cfw_test_runtime_parse_digit_query_count;
    unsigned int byte = (unsigned char)value;

    if (index < 128U) {
        open_cfw_test_runtime_parse_digit_queries[index] = byte;
    }
    open_cfw_test_runtime_parse_digit_query_count = index + 1U;
    return byte >= (unsigned int)'0' && byte <= (unsigned int)'9';
}

#define OPEN_CFW_RUNTIME_FORMAT_PARSE_IS_DIGIT(value) \
    open_cfw_test_runtime_parse_is_digit((value))

#include "../../components/apollo_main/core_overlay/runtime_format_parse_helpers.c"

unsigned int open_cfw_test_runtime_parse_decimal_execute(
    const unsigned char *input,
    unsigned int *consumed
)
{
    const unsigned char *cursor = input;
    unsigned int result = open_cfw_runtime_parse_decimal(&cursor);

    *consumed = (unsigned int)(cursor - input);
    return result;
}

void open_cfw_test_runtime_parse_reset(void)
{
    unsigned int index;

    open_cfw_test_runtime_parse_digit_query_count = 0U;
    for (index = 0U; index < 128U; index += 1U) {
        open_cfw_test_runtime_parse_digit_queries[index] = 0U;
    }
}
