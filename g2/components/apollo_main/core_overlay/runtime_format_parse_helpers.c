/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacements for the G2 2.2.6.10 formatting helper cluster:
 *   0x00483028...0x0048302F  bounded output-byte store
 *   0x00483030...0x00483031  no-op output callback
 *   0x00483032...0x00483043  ASCII digit predicate
 *   0x00483044...0x0048306B  unsigned decimal parser
 */

typedef unsigned int open_cfw_runtime_format_parse_word;

_Static_assert(
    sizeof(open_cfw_runtime_format_parse_word) == 4U,
    "format helper word width changed"
);

__attribute__((used, noinline))
void open_cfw_runtime_bounded_byte_store(
    open_cfw_runtime_format_parse_word value,
    unsigned char *buffer,
    open_cfw_runtime_format_parse_word index,
    open_cfw_runtime_format_parse_word capacity
)
{
    if (index < capacity) {
        buffer[index] = (unsigned char)value;
    }
}

__attribute__((used, noinline))
void open_cfw_runtime_noop_output(
    open_cfw_runtime_format_parse_word value,
    unsigned char *buffer,
    open_cfw_runtime_format_parse_word index,
    open_cfw_runtime_format_parse_word capacity
)
{
    (void)value;
    (void)buffer;
    (void)index;
    (void)capacity;
}

__attribute__((used, noinline))
open_cfw_runtime_format_parse_word open_cfw_runtime_ascii_is_digit(
    open_cfw_runtime_format_parse_word value
)
{
    unsigned int byte = (unsigned char)value;

    return byte >= (unsigned int)'0' && byte <= (unsigned int)'9';
}

#ifndef OPEN_CFW_RUNTIME_FORMAT_PARSE_IS_DIGIT
#define OPEN_CFW_RUNTIME_FORMAT_PARSE_IS_DIGIT(value) \
    open_cfw_runtime_ascii_is_digit((value))
#endif

__attribute__((used, noinline))
open_cfw_runtime_format_parse_word open_cfw_runtime_parse_decimal(
    const unsigned char **cursor
)
{
    open_cfw_runtime_format_parse_word result = 0U;

    while (
        OPEN_CFW_RUNTIME_FORMAT_PARSE_IS_DIGIT(
            (open_cfw_runtime_format_parse_word)**cursor
        ) != 0U
    ) {
        const unsigned char *current = *cursor;

        *cursor = current + 1;
        result = 10U * result + (open_cfw_runtime_format_parse_word)(
            *current - (unsigned char)'0'
        );
    }
    return result;
}

#undef OPEN_CFW_RUNTIME_FORMAT_PARSE_IS_DIGIT
