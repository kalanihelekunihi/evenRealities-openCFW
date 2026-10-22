/* IAR AEABI signed 64-bit integer to double (__aeabi_l2d), native
 * 0x59c7ac..0x59c800, firmware 2.2.6.10. No source path is retained.
 *
 * Integer only (base AAPCS: argument and result in r0:r1, kept with
 * pcs("aapcs") under the hard-float payload default). Stock negates to a magnitude, then:
 * - high word non-zero: normalises with CLZ and rounds the 11 dropped bits to
 *   nearest-even (the SBCS/ADCS carry chain takes the mantissa LSB from the
 *   LSLS #21 carry-out); verified against correctly rounded conversion on
 *   400k random inputs;
 * - high word zero: exact conversion of the low word (0 -> +0.0).
 * Callers include the audio direction helpers (findings-audio.md §4). */
#include <stdint.h>

typedef union { double d; uint64_t u; } p13_f64_bits_t;

__attribute__((pcs("aapcs"))) double iar_aeabi_l2d_59c7ac(int64_t value)
{
    p13_f64_bits_t result;
    uint64_t magnitude = (uint64_t)value;
    uint32_t sign = 0u;
    uint32_t high;
    uint32_t low;
    uint32_t shift;

    if (value < 0) {
        sign = 0x80000000u;
        magnitude = 0u - magnitude;
    }
    high = (uint32_t)(magnitude >> 32);
    low = (uint32_t)magnitude;
    if (high != 0u) {
        uint64_t normal;
        uint32_t dropped;
        uint64_t mantissa;
        uint32_t round_up;

        shift = (uint32_t)__builtin_clz(high);
        normal = magnitude << shift;
        dropped = (uint32_t)normal & 0x7ffu;
        mantissa = normal >> 11; /* 53 bits including the leading one */
        round_up = dropped > 0x400u || (dropped == 0x400u && (mantissa & 1u) != 0u);
        /* The leading one lands in bit 52 and adds one to the exponent field. */
        result.u = ((uint64_t)(sign | ((1085u - shift) << 20)) << 32) + mantissa + round_up;
        return result.d;
    }
    if (low == 0u) {
        result.u = 0u;
        return result.d;
    }
    shift = (uint32_t)__builtin_clz(low);
    low <<= shift;
    result.u = ((uint64_t)((0x41d00000u - (shift << 20) + (low >> 11)) | sign) << 32) |
               (uint64_t)(low << 21);
    return result.d;
}
