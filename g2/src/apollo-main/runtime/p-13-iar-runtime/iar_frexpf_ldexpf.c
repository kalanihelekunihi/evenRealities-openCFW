/* IAR DLIB binary32 exponent helpers frexpf / ldexpf, native
 * 0x59d244..0x59d350, firmware 2.2.6.10. No source path is retained.
 *
 * Hard-float ABI (value in s0, result in s0); the bit work is integer. Needs
 * a single-precision FPU: profile g2-apollo-main-3.
 *
 * frexpf (0x59d244) wraps _internal_frexpf_bits (0x59d258), which takes the
 * float bits in r0 and returns the fraction bits in r0 and the exponent in r1
 * (a 64-bit return). Zero, Inf and NaN come back unchanged with exponent 0.
 *
 * ldexpf (0x59d28c) adds n to the exponent field directly when the result
 * stays normal. Overflow returns +/-Inf and tail-calls the ERANGE setter
 * 0x439cb2. A result that becomes subnormal or zero is produced by one VMUL by
 * 2^-k (k <= 25; larger k gives a signed zero without ERANGE) with the
 * cumulative flags and trap enables cleared; ERANGE is set only when that
 * multiply raises Underflow, and the caller's FPSCR is then restored, so the
 * multiply's own flags are discarded. A subnormal input with n > 0 is scaled
 * by 2^n (n <= 127) or by 2^127 before re-entering the normal path. */
#include <stdint.h>

#define IAR_VFP __attribute__((pcs("aapcs-vfp")))

extern void audio_uart_ring_errno_range_set_439cb2(void); /* errno = ERANGE (34) */

static uint32_t float_bits(float value)
{
    union { float f; uint32_t u; } v = { .f = value };
    return v.u;
}

static float bits_float(uint32_t bits)
{
    union { uint32_t u; float f; } v = { .u = bits };
    return v.f;
}

uint64_t _internal_frexpf_bits(uint32_t bits)
{
    uint32_t exponent_field = (bits >> 23) & 0xffu;
    uint32_t sign;
    uint32_t shift;

    if (exponent_field == 0u) {
        if ((bits << 1) == 0u)
            return bits; /* +/-0, exponent 0 */
        sign = bits & 0x80000000u;
        bits <<= 9;
        shift = (uint32_t)__builtin_clz(bits);
        bits <<= shift;
        /* The leading one lands in bit 23: exponent field 125 + 1 = 126. */
        bits = (sign | (bits >> 8)) + 0x3e800000u;
        return ((uint64_t)(0u - (shift + 126u)) << 32) | bits;
    }
    if (exponent_field == 0xffu)
        return bits; /* Inf/NaN, exponent 0 */
    exponent_field -= 126u;
    return ((uint64_t)exponent_field << 32) | (bits - (exponent_field << 23));
}

IAR_VFP float frexpf(float value, int *exponent)
{
    uint64_t parts = _internal_frexpf_bits(float_bits(value));

    *exponent = (int)(uint32_t)(parts >> 32);
    return bits_float((uint32_t)parts);
}

static float vfp_mul(float a, float b)
{
    float result;

    __asm__ volatile("vmul.f32 %0, %1, %2" : "=t"(result) : "t"(a), "t"(b));
    return result;
}

/* 0x59d2d0: final right scaling by 2^-shift into the subnormal range. */
static float ldexpf_scale_down(float value, uint32_t shift)
{
    uint32_t saved;
    uint32_t status;
    float result;

    if (shift > 25u)
        return bits_float(float_bits(value) & 0x80000000u);
    __asm__ volatile("vmrs %0, fpscr" : "=r"(saved));
    __asm__ volatile("vmsr fpscr, %0" : : "r"(saved & ~0x1f1fu));
    result = vfp_mul(value, bits_float((127u - shift) << 23));
    __asm__ volatile("vmrs %0, fpscr" : "=r"(status));
    __asm__ volatile("vmsr fpscr, %0" : : "r"(saved));
    if ((status & 0x8u) != 0u) /* UFC */
        audio_uart_ring_errno_range_set_439cb2();
    return result;
}

IAR_VFP float ldexpf(float value, int n)
{
    uint32_t bits = float_bits(value);
    uint32_t exponent_field = (bits >> 23) & 0xffu;
    uint32_t amount = (uint32_t)n;

    if (n >= 0) {
        if (exponent_field == 0u) {
            if ((bits << 1) == 0u)
                return value;
            if (amount <= 127u)
                return vfp_mul(value, bits_float((amount + 127u) << 23));
            value = vfp_mul(value, bits_float(0x7f000000u)); /* 2^127 */
            amount -= 127u;
            bits = float_bits(value);
            exponent_field = (bits >> 23) & 0xffu;
        } else if (exponent_field == 0xffu) {
            return value;
        }
        if (exponent_field + amount >= 0xffu) {
            value = bits_float(((bits >> 23) | 0xffu) << 23); /* +/-Inf */
            audio_uart_ring_errno_range_set_439cb2();
            return value;
        }
        return bits_float(bits + (amount << 23));
    }

    amount = 0u - amount;
    if (exponent_field == 0u) {
        if ((bits << 1) == 0u)
            return value;
        return ldexpf_scale_down(value, amount);
    }
    if (exponent_field == 0xffu)
        return value;
    if (amount < exponent_field)
        return bits_float(bits - (amount << 23));
    /* Drop to the smallest normal exponent, then scale the rest. */
    exponent_field -= 1u;
    amount -= exponent_field;
    return ldexpf_scale_down(bits_float(bits - (exponent_field << 23)), amount);
}
