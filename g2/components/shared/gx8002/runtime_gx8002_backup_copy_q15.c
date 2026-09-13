/* SPDX-License-Identifier: MIT */
/* Recovered package 0x47ac0: count is halfwords. Four-sample blocks load
 * both words before storing either. Preserve this order for overlapping
 * buffers; this routine is not a general memmove. Word alignment applies
 * when a four-sample block is present, as in the original implementation. */
#include <stdint.h>
typedef uint32_t alias_word __attribute__((may_alias));
void open_cfw_gx8002_backup_copy_q15(const int16_t *input, int16_t *output,
                                    uint32_t count)
{
    const volatile alias_word *src = (const volatile alias_word *)input;
    volatile alias_word *dst = (volatile alias_word *)output;
    uint32_t groups = count >> 2;
    while (groups--) {
        uint32_t first = src[0], second = src[1];
        dst[0] = first;
        dst[1] = second;
        src += 2;
        dst += 2;
    }
    const volatile uint16_t *half_src = (const volatile uint16_t *)src;
    volatile uint16_t *half_dst = (volatile uint16_t *)dst;
    uint32_t tail = count & 3u;
    while (tail--) *half_dst++ = *half_src++;
}
