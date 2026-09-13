/* SPDX-License-Identifier: MIT */
/* Recovered Q15 fill helper at codec package 0x47aec. Count is halfwords.
 * Preserve two word stores per four samples, followed by halfword stores.
 * Four-sample blocks require the same word alignment as the stock helper. */
#include <stdint.h>
typedef uint32_t alias_word __attribute__((may_alias));
void open_cfw_gx8002_backup_fill_q15(uint32_t value, int16_t *output,
                                    uint32_t count)
{
    uint32_t groups = count >> 2;
    if (groups) {
        uint32_t packed = (value & 0xffffu) * 0x10001u;
        volatile alias_word *words = (volatile alias_word *)output;
        do {
            *words++ = packed;
            *words++ = packed;
        } while (--groups);
        output = (int16_t *)words;
    }
    uint32_t tail = count & 3u;
    volatile uint16_t *halfwords = (volatile uint16_t *)output;
    while (tail--) *halfwords++ = (uint16_t)value;
}
