/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source reimplementation of the stock Apollo application memory
 * comparator at 0x004751C8...0x0047522F.
 */

typedef __UINTPTR_TYPE__ open_cfw_uintptr;

static __attribute__((always_inline)) inline unsigned int
open_cfw_memory_compare_reverse_word(unsigned int value)
{
    return
        ((value & 0x000000FFU) << 24U) |
        ((value & 0x0000FF00U) << 8U) |
        ((value & 0x00FF0000U) >> 8U) |
        ((value & 0xFF000000U) >> 24U);
}

/*
 * The stock function has standard memcmp ordering with two observable return
 * conventions:
 *
 * - byte paths return the exact unsigned-byte difference;
 * - an aligned 32-bit mismatch returns -1 or 1 after byte-order reversal.
 *
 * Keeping that distinction makes this replacement ABI-compatible even for
 * callers that inspect the magnitude rather than only the sign.
 */
__attribute__((used, noinline))
int open_cfw_memory_compare(
    const void *left_value,
    const void *right_value,
    unsigned int length
)
{
    const unsigned char *left =
        (const unsigned char *)left_value;
    const unsigned char *right =
        (const unsigned char *)right_value;

#pragma clang loop unroll(disable)
    while (((open_cfw_uintptr)left & 3U) != 0U) {
        int difference;

        if (length == 0U) {
            return 0;
        }
        difference = (int)*left - (int)*right;
        if (difference != 0) {
            return difference;
        }
        ++left;
        ++right;
        --length;
    }

    if (((open_cfw_uintptr)right & 3U) == 0U) {
#pragma clang loop unroll(disable)
        while (length >= 4U) {
            unsigned int left_word =
                *(const unsigned int *)(const void *)left;
            unsigned int right_word =
                *(const unsigned int *)(const void *)right;

            if (left_word != right_word) {
                left_word =
                    open_cfw_memory_compare_reverse_word(left_word);
                right_word =
                    open_cfw_memory_compare_reverse_word(right_word);
                return left_word < right_word ? -1 : 1;
            }
            left += 4;
            right += 4;
            length -= 4U;
        }
    }

#pragma clang loop unroll(disable)
    while (length != 0U) {
        int difference = (int)*left - (int)*right;

        if (difference != 0) {
            return difference;
        }
        ++left;
        ++right;
        --length;
    }

    return 0;
}
