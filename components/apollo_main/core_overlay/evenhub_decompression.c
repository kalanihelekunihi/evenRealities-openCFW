/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded EvenHub image-decompression adapters for the Even Realities G2
 * 2.2.6.10 Apollo510B application. Exact stock boundaries, callers, and
 * behavior are recorded in EVIDENCE.md.
 */

int open_cfw_lz4_decompress_safe_legacy(
    const unsigned char *input,
    unsigned char *output,
    int input_length,
    int output_capacity
);

#ifndef OPEN_CFW_EVENHUB_MODE2_DECODE
#define OPEN_CFW_EVENHUB_MODE2_DECODE( \
    input, \
    output, \
    input_length, \
    output_capacity \
) \
    (open_cfw_lz4_decompress_safe_legacy( \
        (input), \
        (output), \
        (int)(input_length), \
        (int)(output_capacity) \
    ))
#endif

/*
 * ABI-compatible source replacement for stock 0x004E0C0C...0x004E0C33.
 * This adapter validates all four arguments, restores the LZ4 decoder's
 * argument order, and maps every non-positive result to zero.
 */
__attribute__((used, noinline))
unsigned int open_cfw_evenhub_mode2_decompress_legacy(
    const unsigned char *input,
    unsigned int input_length,
    unsigned char *output,
    unsigned int output_capacity
)
{
    int result;

    if (
        input == (const unsigned char *)0 ||
        input_length == 0U ||
        output == (unsigned char *)0 ||
        output_capacity == 0U
    ) {
        return 0U;
    }

    result = OPEN_CFW_EVENHUB_MODE2_DECODE(
        input,
        output,
        input_length,
        output_capacity
    );
    return result < 1 ? 0U : (unsigned int)result;
}

/*
 * ABI-compatible source replacement for stock 0x004E0C3C...0x004E0C9F.
 * The stream is a sequence of byte pairs: repeat count, then repeated value.
 * An odd trailing byte is ignored. Output truncates exactly at capacity.
 */
__attribute__((used, noinline))
unsigned int open_cfw_evenhub_rle_decode(
    const unsigned char *input,
    unsigned int input_length,
    unsigned char *output,
    unsigned int output_capacity
)
{
    unsigned int input_offset = 0U;
    unsigned int output_offset = 0U;

    if (
        input == (const unsigned char *)0 ||
        input_length == 0U ||
        output == (unsigned char *)0 ||
        output_capacity == 0U
    ) {
        return 0U;
    }

    while (input_offset < input_length) {
        unsigned int count;
        unsigned int repeat_index;
        unsigned char value;

        if (input_offset + 1U >= input_length) {
            return output_offset;
        }

        count = input[input_offset++];
        value = input[input_offset++];
        if (output_capacity < output_offset + count) {
            count = output_capacity - output_offset;
            for (repeat_index = 0U; repeat_index < count; ++repeat_index) {
                output[output_offset++] = value;
            }
            return output_offset;
        }

        for (repeat_index = 0U; repeat_index < count; ++repeat_index) {
            output[output_offset++] = value;
        }
    }

    return output_offset;
}

/*
 * Stock 0x004E0C34 is a public wrapper around the RLE implementation and has
 * three direct callers. Keep that boundary independently replaceable.
 */
__attribute__((used, noinline))
unsigned int open_cfw_evenhub_rle_decompress(
    const unsigned char *input,
    unsigned int input_length,
    unsigned char *output,
    unsigned int output_capacity
)
{
    return open_cfw_evenhub_rle_decode(
        input,
        input_length,
        output,
        output_capacity
    );
}
