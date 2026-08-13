/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 reverse-output formatter at
 * 0x0048306C...0x004830D9.
 *
 * Semantics follow mpaland/printf _out_rev at commit
 * d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e. Firmware size, callback, and
 * pointer carriers are 32-bit; index arithmetic deliberately wraps.
 */

typedef unsigned int open_cfw_runtime_format_out_reverse_word;
#ifndef OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
#define OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
typedef void (*open_cfw_runtime_ntoa_output_fn)(
    char,
    void *,
    open_cfw_runtime_format_out_reverse_word,
    open_cfw_runtime_format_out_reverse_word
);
#endif

_Static_assert(
    sizeof(open_cfw_runtime_format_out_reverse_word) == 4U,
    "reverse-output formatter word width changed"
);

#define OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE_FLAG_ZEROPAD (1U << 0U)
#define OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE_FLAG_LEFT (1U << 1U)

#ifndef OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE_CALL_OUTPUT
#define OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE_CALL_OUTPUT( \
    callback, \
    character, \
    buffer, \
    index, \
    maximum_length \
) \
    ((callback)( \
            (char)(character), \
            (void *)(buffer), \
            (index), \
            (maximum_length) \
        ))
#endif

__attribute__((used, noinline))
open_cfw_runtime_format_out_reverse_word
open_cfw_runtime_format_out_reverse(
    open_cfw_runtime_ntoa_output_fn output_callback,
    void *buffer,
    open_cfw_runtime_format_out_reverse_word index,
    open_cfw_runtime_format_out_reverse_word maximum_length,
    const char *reverse_buffer,
    open_cfw_runtime_format_out_reverse_word length,
    open_cfw_runtime_format_out_reverse_word width,
    open_cfw_runtime_format_out_reverse_word flags
)
{
    open_cfw_runtime_format_out_reverse_word start_index = index;

    if (
        (flags & OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE_FLAG_LEFT) == 0U
        && (
            flags
            & OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE_FLAG_ZEROPAD
        ) == 0U
    ) {
        open_cfw_runtime_format_out_reverse_word iterator;

        for (iterator = length; iterator < width; iterator += 1U) {
            OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE_CALL_OUTPUT(
                output_callback,
                (open_cfw_runtime_format_out_reverse_word)' ',
                buffer,
                index,
                maximum_length
            );
            index += 1U;
        }
    }

    while (length != 0U) {
        length -= 1U;
        OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE_CALL_OUTPUT(
            output_callback,
            (open_cfw_runtime_format_out_reverse_word)reverse_buffer[length],
            buffer,
            index,
            maximum_length
        );
        index += 1U;
    }

    if (
        (flags & OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE_FLAG_LEFT) != 0U
    ) {
        while (index - start_index < width) {
            OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE_CALL_OUTPUT(
                output_callback,
                (open_cfw_runtime_format_out_reverse_word)' ',
                buffer,
                index,
                maximum_length
            );
            index += 1U;
        }
    }
    return index;
}

#undef OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE_CALL_OUTPUT
#undef OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE_FLAG_LEFT
#undef OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE_FLAG_ZEROPAD
