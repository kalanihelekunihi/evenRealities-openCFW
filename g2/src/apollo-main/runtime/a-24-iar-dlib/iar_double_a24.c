/* IAR runtime binary64 helpers, firmware 2.2.6.10, native 0x4d4138..0x4d4365.
 * IAR DLIB has no public source; written from the disassembly. Needs the
 * double-precision FPU: profile g2-apollo-main-20.
 *
 *   0x4d4138 frexp (hard-float: x in d0, int * in r0)
 *   0x4d4150 frexp (soft-float: x in r0:r1, int * in r2)
 *   0x4d415c frexp core on the bit pattern
 *   0x4d41c0 __aeabi_cdcmple shape: compares a (r0:r1) with b (r2:r3) into APSR
 *   0x4d41f4 ldexp (soft-float) -> 0x4d4208
 *   0x4d4208 ldexp/scalbn core (hard-float: x in d0, n in r0)
 *   0x4d42f8 d2iz, 0x4d4306 i2d, 0x4d4314 dsub, 0x4d4326 ddiv, 0x4d4338 d2uiz,
 *   0x4d4346 ui2d, 0x4d4354 dmul: soft-float AEABI wrappers around one VFP op.
 * Suffixed names avoid clashing with compiler-rt __aeabi_* symbols. */
#include <stdint.h>
#include <stddef.h>

#define IAR_VFP __attribute__((pcs("aapcs-vfp")))

extern void audio_uart_ring_errno_range_set_439cb2(void); /* errno = ERANGE (34) */

static uint64_t double_bits(double value)
{
    union { double d; uint64_t u; } v = { .d = value };
    return v.u;
}

static double bits_double(uint64_t bits)
{
    union { uint64_t u; double d; } v = { .u = bits };
    return v.d;
}

static double make_double(uint32_t hi, uint32_t lo)
{
    return bits_double(((uint64_t)hi << 32) | lo);
}

/* frexp on the bit pattern. Stock returns the fraction in r0:r1 and the
 * exponent in r2 (a private convention); here the exponent goes through
 * `exponent`. Zero, Inf and NaN come back unchanged with exponent 0. */
uint64_t iar_frexp_bits_4d415c(uint64_t bits, int32_t *exponent)
{
    uint32_t lo = (uint32_t)bits;
    uint32_t hi = (uint32_t)(bits >> 32);
    uint32_t field = (hi >> 20) & 0x7ffu;
    uint32_t sign;
    uint32_t shift;

    if (field != 0u) {
        if ((hi << 1) >= 0xffe00000u) {
            *exponent = 0;
            return bits;
        }
        *exponent = (int32_t)(field - 0x3feu);
        hi -= (field - 0x3feu) << 20;
        return ((uint64_t)hi << 32) | lo;
    }
    if ((lo | (hi << 1)) == 0u) {
        *exponent = 0;
        return bits;
    }
    /* Subnormal: move the leading one to bit 52, then bias to [0.5, 1). */
    sign = hi & 0x80000000u;
    hi &= ~sign;
    shift = (hi != 0u ? (uint32_t)__builtin_clz(hi) : 32u + (uint32_t)__builtin_clz(lo)) - 11u;
    if (shift >= 32u) {
        hi = lo << (shift - 32u);
        hi |= sign;
        lo = 0u;
    } else {
        hi = (hi << shift) | sign | (lo >> (32u - shift));
        lo <<= shift;
    }
    *exponent = -(int32_t)shift - 1021;
    hi += 0x3fdu << 20;
    return ((uint64_t)hi << 32) | lo;
}

IAR_VFP double frexp_4d4138(double value, int32_t *exponent)
{
    return bits_double(iar_frexp_bits_4d415c(double_bits(value), exponent));
}

__attribute__((pcs("aapcs"))) double frexp_softfp_4d4150(double value, int32_t *exponent)
{
    return bits_double(iar_frexp_bits_4d415c(double_bits(value), exponent));
}

/* Result only in the condition flags (C clear: a < b, Z: equal, C=1 Z=0 for
 * a NaN with a nonzero upper mantissa), so the body is the stock instruction
 * sequence. For two non-negative operands only b is NaN-screened. */
__attribute__((naked, noinline)) void iar_aeabi_cdcmple_4d41c0(void)
{
    __asm__ volatile(
        "orr.w ip, r1, r3\n\t"
        "orrs.w ip, r0, ip, lsl #1\n\t" /* C = sign(a)|sign(b) */
        "orrs.w ip, r2, ip\n\t"         /* Z = both are +-0 */
        "mov.w ip, #0x200000\n\t"
        "bcc 1f\n\t"
        "beq 0f\n\t"
        "cmn.w ip, r1, lsl #1\n\t"      /* a NaN screen */
        "itt ls\n\t"
        "cmnls.w ip, r3, lsl #1\n\t"    /* b NaN screen */
        "cmpls r3, r1\n\t"              /* negative: compare b with a */
        "it eq\n\t"
        "cmpeq r2, r0\n"
        "0:\n\t"
        "bx lr\n"
        "1:\n\t"
        "cmn.w ip, r3, lsl #1\n\t"
        "bhi 0b\n\t"
        "cmp r1, r3\n\t"
        "it eq\n\t"
        "cmpeq r0, r2\n\t"
        "bx lr\n");
}

/* x * 2^-shift for shift < 55 with the cumulative exception flags and trap
 * enables cleared; ERANGE when the multiply underflows. The caller's FPSCR is
 * restored afterwards. */
static double scale_down(double value, uint32_t shift)
{
    uint32_t saved;
    uint32_t status;
    double factor = make_double((0x3ffu - shift) << 20, 0u);
    double result;

    __asm__ volatile("vmrs %0, fpscr" : "=r"(saved));
    __asm__ volatile("vmsr fpscr, %0" : : "r"(saved & ~0x1f1fu));
    __asm__ volatile("vmul.f64 %P0, %P1, %P2" : "=w"(result) : "w"(value), "w"(factor));
    __asm__ volatile("vmrs %0, fpscr" : "=r"(status));
    __asm__ volatile("vmsr fpscr, %0" : : "r"(saved));
    if ((status & 0x8u) != 0u) /* UFC */
        audio_uart_ring_errno_range_set_439cb2();
    return result;
}

static double signed_zero(uint32_t hi)
{
    audio_uart_ring_errno_range_set_439cb2();
    return make_double(hi & 0x80000000u, 0u);
}

/* x * 2^n. Overflow gives +-Inf and ERANGE; a result below the normal range
 * goes through scale_down; a shift of 55 or more gives a signed zero and
 * ERANGE. Stock quirk kept: a subnormal x with n >= 1020 is multiplied by
 * 2^1009 but the remaining shift is n - 1016, and the overflow test then
 * counts one more than the exponent sum. */
IAR_VFP double dscale_4d4208(double value, int32_t n)
{
    uint64_t bits = double_bits(value);
    uint32_t lo = (uint32_t)bits;
    uint32_t hi = (uint32_t)(bits >> 32);
    uint32_t field = (hi >> 20) & 0x7ffu;
    uint32_t amount;
    uint32_t sum;

    if (n >= 0) {
        amount = (uint32_t)n;
        if (field == 0u) {
            if ((lo | (hi << 1)) == 0u)
                return value;
            if (amount < 0x3fcu)
                return value * make_double((amount + 0x3ffu) << 20, 0u);
            value = value * make_double(0x7f000000u, 0u);
            amount -= 0x3f8u;
            bits = double_bits(value);
            lo = (uint32_t)bits;
            hi = (uint32_t)(bits >> 32);
            sum = amount + ((hi << 1) >> 21) + 1u;
        } else {
            if (field == 0x7ffu)
                return value;
            sum = field + amount;
        }
        if (sum >= 0x7ffu) {
            value = make_double((hi & 0x80000000u) | 0x7ff00000u, 0u);
            audio_uart_ring_errno_range_set_439cb2();
            return value;
        }
        return make_double(hi + (amount << 20), lo);
    }

    amount = 0u - (uint32_t)n;
    if (field == 0u) {
        if ((lo | (hi << 1)) == 0u)
            return value;
        if (amount >= 55u)
            return signed_zero(hi);
        return scale_down(value, amount);
    }
    if (field == 0x7ffu)
        return value;
    if (amount < field)
        return make_double(hi - (amount << 20), lo);
    /* Drop to the smallest normal exponent, then scale the rest. */
    field -= 1u;
    amount -= field;
    hi -= field << 20;
    if (amount >= 55u)
        return signed_zero(hi);
    return scale_down(make_double(hi, lo), amount);
}

__attribute__((pcs("aapcs"))) double ldexp_4d41f4(double value, int32_t n)
{
    return dscale_4d4208(value, n);
}

__attribute__((pcs("aapcs"))) int32_t aeabi_d2iz_4d42f8(double value)
{
    return (int32_t)value;
}

__attribute__((pcs("aapcs"))) double aeabi_i2d_4d4306(int32_t value)
{
    return (double)value;
}

__attribute__((pcs("aapcs"))) double aeabi_dsub_4d4314(double a, double b)
{
    return a - b;
}

__attribute__((pcs("aapcs"))) double aeabi_ddiv_4d4326(double a, double b)
{
    return a / b;
}

__attribute__((pcs("aapcs"))) uint32_t aeabi_d2uiz_4d4338(double value)
{
    return (uint32_t)value;
}

__attribute__((pcs("aapcs"))) double aeabi_ui2d_4d4346(uint32_t value)
{
    return (double)value;
}

__attribute__((pcs("aapcs"))) double aeabi_dmul_4d4354(double a, double b)
{
    return a * b;
}
