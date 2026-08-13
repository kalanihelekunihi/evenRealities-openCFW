/*
 * SPDX-License-Identifier: BSD-2-Clause
 *
 * Bounded decompression-only adaptation of LZ4 1.9.4's
 * LZ4_decompress_safe/LZ4_decompress_generic path for the Even Realities G2
 * 2.2.6.10 Apollo510B application.
 *
 * Copyright (C) 2011-2020, Yann Collet.
 *
 * The complete retained license is in LICENSE-LZ4-BSD-2-Clause. Upstream
 * provenance and the reviewed stock boundary are recorded in EVIDENCE.md.
 */

/*
 * Decode one independent LZ4 block without a dictionary. The public ABI and
 * positive/negative result contract match upstream LZ4_decompress_safe:
 * return the decompressed byte count, or a negative value for malformed input
 * or insufficient output capacity.
 *
 * This implementation deliberately uses bounded byte copies. That is slower
 * than upstream's wild-copy fast paths, but avoids unaligned accesses and
 * speculative writes beyond the caller's output capacity on Apollo510B.
 */
__attribute__((used, noinline))
int open_cfw_lz4_decompress_safe_legacy(
    const unsigned char *input,
    unsigned char *output,
    int input_length,
    int output_capacity
)
{
    unsigned int input_offset = 0U;
    unsigned int output_offset = 0U;
    unsigned int input_limit;
    unsigned int output_limit;

    if (input == (const unsigned char *)0 || output_capacity < 0) {
        return -1;
    }

    /*
     * LZ4 represents an empty block as one zero token. The EvenHub adapter
     * rejects zero capacities before this boundary, but retain the upstream
     * entry behavior for completeness.
     */
    if (output_capacity == 0) {
        return (
            input_length == 1 &&
            input[0] == 0U
        ) ? 0 : -1;
    }
    if (
        output == (unsigned char *)0 ||
        input_length <= 0
    ) {
        return -1;
    }

    input_limit = (unsigned int)input_length;
    output_limit = (unsigned int)output_capacity;

    for (;;) {
        unsigned int token;
        unsigned int literal_length;
        unsigned int match_length;
        unsigned int offset;

        if (input_offset >= input_limit) {
            return -((int)input_offset) - 1;
        }
        token = input[input_offset++];
        literal_length = token >> 4;

        if (literal_length == 15U) {
            unsigned int extension;

            do {
                if (input_offset >= input_limit) {
                    return -((int)input_offset) - 1;
                }
                extension = input[input_offset++];
                if (literal_length > 0xFFFFFFFFU - extension) {
                    return -((int)input_offset) - 1;
                }
                literal_length += extension;
            } while (extension == 255U);
        }

        if (
            literal_length > input_limit - input_offset ||
            literal_length > output_limit - output_offset
        ) {
            return -((int)input_offset) - 1;
        }

        while (literal_length != 0U) {
            output[output_offset++] = input[input_offset++];
            --literal_length;
        }

        /* A full block must end with its final literal-only sequence. */
        if (input_offset == input_limit) {
            return (int)output_offset;
        }

        /*
         * A non-final sequence needs a two-byte offset, a following token, and
         * at least five final literals. This is the LZ4 block end constraint
         * enforced by the upstream safe decoder.
         */
        if (input_limit - input_offset < 8U) {
            return -((int)input_offset) - 1;
        }

        offset = (unsigned int)input[input_offset];
        offset |= (unsigned int)input[input_offset + 1U] << 8;
        input_offset += 2U;
        if (offset == 0U || offset > output_offset) {
            return -((int)input_offset) - 1;
        }

        match_length = token & 15U;
        if (match_length == 15U) {
            unsigned int extension;

            do {
                /*
                 * Leave a complete final token plus five literal bytes. The
                 * stock use has no prefix or external dictionary.
                 */
                if (input_limit - input_offset <= 6U) {
                    return -((int)input_offset) - 1;
                }
                extension = input[input_offset++];
                if (match_length > 0xFFFFFFFFU - extension) {
                    return -((int)input_offset) - 1;
                }
                match_length += extension;
            } while (extension == 255U);
        }
        if (match_length > 0xFFFFFFFFU - 4U) {
            return -((int)input_offset) - 1;
        }
        match_length += 4U;

        if (
            match_length > output_limit - output_offset ||
            output_limit - output_offset - match_length < 5U
        ) {
            return -((int)input_offset) - 1;
        }

        /*
         * Forward byte copies intentionally preserve LZ4 overlap semantics
         * for short offsets.
         */
        while (match_length != 0U) {
            output[output_offset] = output[output_offset - offset];
            ++output_offset;
            --match_length;
        }
    }
}
