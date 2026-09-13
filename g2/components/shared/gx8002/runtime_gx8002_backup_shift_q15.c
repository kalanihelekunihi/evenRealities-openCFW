/* SPDX-License-Identifier: MIT */
/* Recovered package 0x47a00: signed Q15 shift, count in halfwords.
 * Negative shift: saturated negation followed by five-bit PASR count.
 * Nonnegative shift: signed saturating left shift. Scalar arithmetic avoids
 * overflowing C shifts. Two word loads precede the two block stores. */
#include <stdint.h>
#include <limits.h>
typedef uint32_t alias_word __attribute__((may_alias));
static inline uint16_t shift_sample(uint16_t raw, int32_t shift)
{
    int32_t value = (int16_t)raw;
    if (shift < 0) {
        uint32_t magnitude = shift == INT32_MIN ? INT32_MAX : (uint32_t)-shift;
        uint32_t bits = magnitude & 31u;
        /* Explicit sign extension, independent of signed right-shift rules. */
        return (uint16_t)(value < 0 ? ~((uint32_t)~value >> bits)
                                   : (uint32_t)value >> bits);
    }
    if (shift >= 16) return value < 0 ? 0x8000u : value > 0 ? 0x7fffu : 0;
    int32_t result = value * (int32_t)(1u << (uint32_t)shift);
    if (result > 32767) result = 32767;
    if (result < -32768) result = -32768;
    return (uint16_t)result;
}
static __attribute__((noinline)) uint32_t shift_word(uint32_t value, int32_t shift)
{
    return (uint32_t)shift_sample((uint16_t)value, shift) |
           (uint32_t)shift_sample((uint16_t)(value >> 16), shift) << 16;
}
void open_cfw_gx8002_backup_shift_q15(const int16_t *input, int32_t shift,
                                     int16_t *output, uint32_t count)
{
    const volatile alias_word *src = (const volatile alias_word *)input;
    volatile alias_word *dst = (volatile alias_word *)output;
    uint32_t groups = count >> 2;
    while (groups--) {
        uint32_t a = src[0], b = src[1];
        dst[0] = shift_word(a, shift);
        dst[1] = shift_word(b, shift);
        src += 2; dst += 2;
    }
    const volatile uint16_t *half_src = (const volatile uint16_t *)src;
    volatile uint16_t *half_dst = (volatile uint16_t *)dst;
    uint32_t tail = count & 3u;
    while (tail--) *half_dst++ = shift_sample(*half_src++, shift);
}
