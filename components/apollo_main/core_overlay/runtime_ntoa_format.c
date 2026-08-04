/*
 * SPDX-License-Identifier: MIT
 *
 * Copyright (c) 2014 Marco Paland
 *
 * Bounded source recovery of the integer formatting helper used by the G2
 * 2.2.6.10 firmware at 0x004830DA. The control flow is derived from
 * mpaland/printf commit d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e.
 */

typedef __UINT32_TYPE__ open_cfw_runtime_ntoa_word;
#ifndef OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
#define OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
typedef void (*open_cfw_runtime_ntoa_output_fn)(
    char character,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length
);
#endif

enum open_cfw_runtime_ntoa_flag {
    OPEN_CFW_RUNTIME_NTOA_ZERO_PAD = 1U << 0U,
    OPEN_CFW_RUNTIME_NTOA_LEFT = 1U << 1U,
    OPEN_CFW_RUNTIME_NTOA_PLUS = 1U << 2U,
    OPEN_CFW_RUNTIME_NTOA_SPACE = 1U << 3U,
    OPEN_CFW_RUNTIME_NTOA_HASH = 1U << 4U,
    OPEN_CFW_RUNTIME_NTOA_UPPERCASE = 1U << 5U,
    OPEN_CFW_RUNTIME_NTOA_PRECISION = 1U << 10U
};

#define OPEN_CFW_RUNTIME_NTOA_FORMAT_BUFFER_SIZE 32U

#ifndef OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE
open_cfw_runtime_ntoa_word open_cfw_runtime_format_out_reverse(
    open_cfw_runtime_ntoa_output_fn output_callback,
    void *buffer,
    open_cfw_runtime_ntoa_word index,
    open_cfw_runtime_ntoa_word maximum_length,
    const char *reverse_buffer,
    open_cfw_runtime_ntoa_word length,
    open_cfw_runtime_ntoa_word width,
    open_cfw_runtime_ntoa_word flags
);
#define OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE( \
    output_callback, \
    buffer, \
    index, \
    maximum_length, \
    reverse_buffer, \
    length, \
    width, \
    flags \
) \
    open_cfw_runtime_format_out_reverse( \
        (output_callback), \
        (buffer), \
        (index), \
        (maximum_length), \
        (reverse_buffer), \
        (length), \
        (width), \
        (flags) \
    )
#endif

__attribute__((used, noinline))
open_cfw_runtime_ntoa_word open_cfw_runtime_ntoa_format(
    open_cfw_runtime_ntoa_output_fn output_callback,
    void *buffer,
    open_cfw_runtime_ntoa_word index,
    open_cfw_runtime_ntoa_word maximum_length,
    char *reverse_buffer,
    open_cfw_runtime_ntoa_word length,
    _Bool negative,
    open_cfw_runtime_ntoa_word base,
    open_cfw_runtime_ntoa_word precision,
    open_cfw_runtime_ntoa_word width,
    open_cfw_runtime_ntoa_word flags
)
{
    if ((flags & OPEN_CFW_RUNTIME_NTOA_LEFT) == 0U) {
        if (
            width != 0U
            && (flags & OPEN_CFW_RUNTIME_NTOA_ZERO_PAD) != 0U
            && (
                negative != 0U
                || (
                    flags
                    & (
                        OPEN_CFW_RUNTIME_NTOA_PLUS
                        | OPEN_CFW_RUNTIME_NTOA_SPACE
                    )
                ) != 0U
            )
        ) {
            width -= 1U;
        }

        while (
            length < precision
            && length < OPEN_CFW_RUNTIME_NTOA_FORMAT_BUFFER_SIZE
        ) {
            reverse_buffer[length] = '0';
            length += 1U;
        }

        while (
            (flags & OPEN_CFW_RUNTIME_NTOA_ZERO_PAD) != 0U
            && length < width
            && length < OPEN_CFW_RUNTIME_NTOA_FORMAT_BUFFER_SIZE
        ) {
            reverse_buffer[length] = '0';
            length += 1U;
        }
    }

    if ((flags & OPEN_CFW_RUNTIME_NTOA_HASH) != 0U) {
        if (
            (flags & OPEN_CFW_RUNTIME_NTOA_PRECISION) == 0U
            && length != 0U
            && (length == precision || length == width)
        ) {
            length -= 1U;
            if (length != 0U && base == 16U) {
                length -= 1U;
            }
        }

        if (
            base == 16U
            && (flags & OPEN_CFW_RUNTIME_NTOA_UPPERCASE) == 0U
            && length < OPEN_CFW_RUNTIME_NTOA_FORMAT_BUFFER_SIZE
        ) {
            reverse_buffer[length] = 'x';
            length += 1U;
        }
        else if (
            base == 16U
            && (flags & OPEN_CFW_RUNTIME_NTOA_UPPERCASE) != 0U
            && length < OPEN_CFW_RUNTIME_NTOA_FORMAT_BUFFER_SIZE
        ) {
            reverse_buffer[length] = 'X';
            length += 1U;
        }
        else if (
            base == 2U
            && length < OPEN_CFW_RUNTIME_NTOA_FORMAT_BUFFER_SIZE
        ) {
            reverse_buffer[length] = 'b';
            length += 1U;
        }

        if (length < OPEN_CFW_RUNTIME_NTOA_FORMAT_BUFFER_SIZE) {
            reverse_buffer[length] = '0';
            length += 1U;
        }
    }

    if (length < OPEN_CFW_RUNTIME_NTOA_FORMAT_BUFFER_SIZE) {
        if (negative != 0U) {
            reverse_buffer[length] = '-';
            length += 1U;
        }
        else if ((flags & OPEN_CFW_RUNTIME_NTOA_PLUS) != 0U) {
            reverse_buffer[length] = '+';
            length += 1U;
        }
        else if ((flags & OPEN_CFW_RUNTIME_NTOA_SPACE) != 0U) {
            reverse_buffer[length] = ' ';
            length += 1U;
        }
    }

    return OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE(
        output_callback,
        buffer,
        index,
        maximum_length,
        reverse_buffer,
        length,
        width,
        flags
    );
}

#undef OPEN_CFW_RUNTIME_NTOA_FORMAT_BUFFER_SIZE
