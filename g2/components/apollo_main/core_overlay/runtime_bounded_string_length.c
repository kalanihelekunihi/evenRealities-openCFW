/*
 * SPDX-License-Identifier: MIT
 *
 * Portable source replacement for the optimized bounded string-length leaf
 * at 0x0048D4E8...0x0048D53D in the G2 2.2.6.10 firmware.
 *
 * The stock implementation aligns the cursor, scans words with the standard
 * zero-byte test, and finishes bytewise. It returns zero for a null pointer
 * and performs no load for a zero maximum. Its pipelined next-word load can,
 * however, read up to three bytes beyond the logical maximum even though
 * those bytes do not affect the returned length.
 *
 * This source preserves the return-value contract while deliberately
 * eliminating that overread. It is therefore not fault- or timing-equivalent;
 * retain the stock helper wherever exact memory-access behavior is required.
 */

typedef __UINT32_TYPE__ open_cfw_runtime_bounded_string_length_word;

_Static_assert(
    sizeof(open_cfw_runtime_bounded_string_length_word) == 4U,
    "bounded string-length word width changed"
);

__attribute__((used, noinline, minsize))
open_cfw_runtime_bounded_string_length_word
open_cfw_runtime_bounded_string_length(
    const char *string,
    open_cfw_runtime_bounded_string_length_word maximum_length
)
{
    open_cfw_runtime_bounded_string_length_word length = 0U;

    if (string == (const char *)0) {
        return 0U;
    }
    while (length < maximum_length && string[length] != '\0') {
        length += 1U;
    }
    return length;
}
