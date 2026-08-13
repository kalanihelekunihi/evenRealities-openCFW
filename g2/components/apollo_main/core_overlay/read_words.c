/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Bounded Apollo510 word-copy helper adapted from AmbiqSuite SDK 5.1.0
 * and the reviewed G2 2.2.6.10 stock wrapper at
 * 0x0048086A...0x00480871.
 */

#ifndef OPEN_CFW_READ_WORDS_READ32
#define OPEN_CFW_READ_WORDS_READ32(source) (*(source))
#endif

#ifndef OPEN_CFW_READ_WORDS_WRITE32
#define OPEN_CFW_READ_WORDS_WRITE32(destination, value) \
    (*(destination) = (value))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_read_words wrapper and its private ITCM implementation. The
 * do/while shape deliberately preserves the stock nonzero-count contract:
 * a zero count underflows and is not treated as a no-op.
 */
__attribute__((used, noinline))
void open_cfw_read_words(
    const volatile unsigned int *source,
    volatile unsigned int *destination,
    unsigned int word_count
)
{
    do {
        unsigned int value = OPEN_CFW_READ_WORDS_READ32(source);
        ++source;
        OPEN_CFW_READ_WORDS_WRITE32(destination, value);
        ++destination;
    } while (--word_count != 0U);
}

#undef OPEN_CFW_READ_WORDS_WRITE32
#undef OPEN_CFW_READ_WORDS_READ32

