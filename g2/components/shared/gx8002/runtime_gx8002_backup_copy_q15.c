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
#if defined(__csky__)
    /* Explicit paired load and hardware loops preserve both the two-read
     * ordering and the original envelope. All operands are symbolic source.
     * r12/r13 hold the loaded pair; r3 is the hardware-loop count. */
    __asm__ volatile (
        "lsri r3, %2, 2\n\t"
        "bez r3, .Lq15_tail_%=\n\t"
        ".Lq15_words_%=:\n\t"
        "pldbi.d r12, (%0)\n\t"
        "stbi.w r12, (%1)\n\t"
        ".Lq15_words_end_%=:\n\t"
        "stbi.w r13, (%1)\n\t"
        "bloop r3, .Lq15_words_%=, .Lq15_words_end_%=\n\t"
        ".Lq15_tail_%=:\n\t"
        "andi r3, %2, 3\n\t"
        "bez r3, .Lq15_done_%=\n\t"
        ".Lq15_halves_%=:\n\t"
        "ldbi.h r12, (%0)\n\t"
        ".Lq15_halves_end_%=:\n\t"
        "stbi.h r12, (%1)\n\t"
        "bloop r3, .Lq15_halves_%=, .Lq15_halves_end_%=\n\t"
        ".Lq15_done_%=:\n\t"
        : "+&r" (input), "+&r" (output)
        : "r" (count)
        : "r3", "r12", "r13", "memory");
#else
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
#endif
}
