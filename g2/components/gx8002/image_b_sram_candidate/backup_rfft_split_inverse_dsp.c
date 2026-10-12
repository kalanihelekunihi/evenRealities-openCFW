/* Loaded image-B inverse RFFT split 0x1000f068..0x1000f0be.
 * Named C-SKY DSPv2 instructions preserve the stock saturating packed
 * arithmetic.  The pinned SDK scalar lowering differs by one Q15 count
 * in the full IMCRA oracle, so this source owns the native instruction
 * sequence without embedding any executable bytes.
 */
#include <stdint.h>

void gx8002_image_b_split_rifft_q15_1000f068(
    const int16_t *source, uint32_t length, const int16_t *coefficient,
    int16_t *destination, uint32_t modifier)
{
    const uint32_t *left = (const uint32_t *)(const void *)source;
    const uint32_t *right = (const uint32_t *)(const void *)(source + 2u * length);
    uint32_t *output = (uint32_t *)(void *)destination;
    const uint32_t *table = (const uint32_t *)(const void *)coefficient;
    for (uint32_t i = 0; i < length; ++i) {
        uint32_t a = *table;
        uint32_t b, tmp;
        uint32_t base = UINT32_C(0x8000);
        __asm__ volatile("psub.16 %0, %1, %2" : "=r"(b) : "r"(base), "r"(a));
        __asm__ volatile("pabs.s16.s %0, %1" : "=r"(tmp) : "r"(b));
        __asm__ volatile("pkg %0, %1, 0, %2, 16"
                         : "=r"(b) : "r"(tmp), "r"(b));
        uint32_t input_left = *left++;
        uint32_t input_right = *right--;
        uint32_t real, imag, packed;
        __asm__ volatile("mulcs.s16 %0, %1, %2"
                         : "=r"(real) : "r"(input_right), "r"(b));
        __asm__ volatile("mulcax.s16.s %0, %1, %2"
                         : "=r"(imag) : "r"(input_right), "r"(b));
        __asm__ volatile("mulaca.s16.s %0, %1, %2"
                         : "+r"(real) : "r"(input_left), "r"(a));
        __asm__ volatile("pneg.s16.s %0, %1" : "+r"(imag) : "r"(imag));
        __asm__ volatile("mulacsx.s16.s %0, %1, %2"
                         : "+r"(imag) : "r"(a), "r"(input_left));
        __asm__ volatile("pkghh %0, %1, %2"
                         : "=r"(packed) : "r"(real), "r"(imag));
        *output++ = packed;
        table += modifier;
    }
}
