/* IAR DLIB double-precision fmod, firmware 2.2.6.10. No source path is
 * retained (hand-written library assembly in stock).
 * Native 0x57dc40..0x57dc53 (hard-float entry) and 0x57dc54..0x57ddfb
 * (integer core); the EDOM path tail-calls the veneer 0x577c34, which
 * jumps to the errno setter 0x439ca4 (errno 33, preserves r0..r3).
 *
 * The core works on raw IEEE-754 words: x in r1:r0, y in r3:r2, result in
 * r1:r0 with the sign of x. Finite operands are reduced by long division in
 * 11-bit chunks, each step estimating the quotient from the high words with
 * one add-back correction. Stock special cases (kept here):
 *   - x Inf or NaN: high word forced to 0x7fffffff, low word of x kept,
 *     no EDOM;
 *   - y == 0 (x finite): same NaN pattern, EDOM;
 *   - y Inf/NaN: only the high word is tested, so y with high word
 *     0x7ff00000 (Inf, or a NaN whose payload is all in the low word)
 *     returns x; any other y NaN returns the NaN pattern; no EDOM;
 *   - |y| >= |x|: returns x, or a signed zero when |y| == |x|.
 *
 * Double-precision hard-float ABI: profile g2-apollo-main-20. */
#include <stdbool.h>
#include <stdint.h>

#define IAR_VFP __attribute__((pcs("aapcs-vfp")))

#define FMOD_SIGN 0x80000000u
#define FMOD_EXP_MAX 0x7ff
#define FMOD_HIDDEN 0x00100000u
#define FMOD_FRAC_HI 0x000fffffu
#define FMOD_INF_HI2 0xffe00000u /* high word of Inf shifted left by one */
#define FMOD_NAN_HI 0x7fffffffu
#define FMOD_CHUNK 11u

extern void audio_uart_float_domain_error_439ca4(void); /* errno = EDOM, via veneer 0x577c34 */

uint64_t iar_fmod_bits_57dc54(uint64_t x, uint64_t y);

static uint64_t fmod_make(uint32_t hi, uint32_t lo)
{
    return ((uint64_t)hi << 32) | lo;
}

/* ARM register shifts: an amount of 32 or more yields 0. */
static uint32_t fmod_lsl(uint32_t value, uint32_t amount)
{
    amount &= 0xffu;
    return amount >= 32u ? 0u : value << amount;
}

static uint32_t fmod_lsr(uint32_t value, uint32_t amount)
{
    amount &= 0xffu;
    return amount >= 32u ? 0u : value >> amount;
}

static uint32_t fmod_clz(uint32_t value)
{
    return value != 0u ? (uint32_t)__builtin_clz(value) : 32u;
}

/* Shift a 64-bit mantissa so its leading one lands on bit 52; returns the
 * shift. Used for subnormal operands (stock 0x57dd76 / 0x57ddaa). */
static uint32_t fmod_normalize(uint32_t *hi, uint32_t *lo)
{
    uint32_t shift = fmod_clz(*hi);

    if (*hi == 0u)
        shift += fmod_clz(*lo);
    shift -= FMOD_CHUNK;
    if (shift >= 32u)
        *hi = fmod_lsl(*lo, shift - 32u);
    else
        *hi = fmod_lsl(*hi, shift) | fmod_lsr(*lo, 32u - shift);
    *lo = fmod_lsl(*lo, shift);
    return shift;
}

/* (hi:lo) = ((hi:lo) << shift) mod (dh:dl): quotient estimate from the high
 * words (udiv), multiply-subtract, one add-back when the result borrows.
 * Returns true when the new high word is zero (stock Z flag). */
static bool fmod_reduce(uint32_t *hi, uint32_t *lo, uint32_t dh, uint32_t dl, uint32_t shift)
{
    uint32_t h = fmod_lsl(*hi, shift) | fmod_lsr(*lo, 32u - shift);
    uint32_t l = fmod_lsl(*lo, shift);
    uint32_t q = h / dh;
    uint64_t product = (uint64_t)dl * q;
    uint64_t numerator;
    uint64_t rest;

    h -= dh * q;
    numerator = fmod_make(h, l);
    rest = numerator - product;
    if (numerator < product)
        rest += fmod_make(dh, dl);
    *hi = (uint32_t)(rest >> 32);
    *lo = (uint32_t)rest;
    return *hi == 0u;
}

/* Stock 0x57dddc: zero divisor, Inf or NaN operand. */
static uint64_t fmod_special(uint32_t xh, uint32_t xl, uint32_t yh2)
{
    uint32_t hi = xh;
    bool carry;
    bool zero;

    if ((xh << 1) >= FMOD_INF_HI2) {
        carry = true;
        zero = (xh << 1) == FMOD_INF_HI2;
        hi = FMOD_NAN_HI;
    } else {
        carry = yh2 >= FMOD_INF_HI2;
        zero = yh2 == FMOD_INF_HI2;
    }
    if (!zero)
        hi = FMOD_NAN_HI;
    if (!carry)
        audio_uart_float_domain_error_439ca4();
    return fmod_make(hi, xl);
}

uint64_t iar_fmod_bits_57dc54(uint64_t x, uint64_t y)
{
    uint32_t xl = (uint32_t)x;
    uint32_t xh = (uint32_t)(x >> 32);
    uint32_t yl = (uint32_t)y;
    uint32_t yh2 = (uint32_t)(y >> 32) << 1; /* |y| high word, shifted */
    uint32_t sign = xh & FMOD_SIGN;
    int32_t ex = (int32_t)((xh >> 20) & 0x7ffu);
    int32_t ey = (int32_t)(yh2 >> 21);
    uint32_t mh;
    uint32_t ml = xl;
    uint32_t dh;
    uint32_t dl = yl;
    int32_t remaining;
    uint32_t shift;
    bool high_zero;

    if (ey == 0 || ex == FMOD_EXP_MAX || ey == FMOD_EXP_MAX) {
        if ((yh2 | yl) == 0u || ex == FMOD_EXP_MAX || ey == FMOD_EXP_MAX)
            return fmod_special(xh, xl, yh2);
    }
    /* |y| >= |x|: x itself, or a signed zero on equality (0x57dd10). */
    if (yh2 > (xh << 1) || (yh2 == (xh << 1) && yl >= xl)) {
        if (yh2 == (xh << 1) && yl == xl)
            return fmod_make(sign, 0u);
        return x;
    }
    if (ey == 0) {
        /* Subnormal y (x may be normal or subnormal). */
        dh = yh2 >> 1;
        ey = 1 - (int32_t)fmod_normalize(&dh, &dl);
        if (ex != 0) {
            mh = (xh & FMOD_FRAC_HI) | FMOD_HIDDEN;
        } else {
            mh = xh & ~FMOD_SIGN;
            ex = 1 - (int32_t)fmod_normalize(&mh, &ml);
        }
    } else {
        dh = ((yh2 >> 1) & FMOD_FRAC_HI) | FMOD_HIDDEN;
        mh = (xh & FMOD_FRAC_HI) | FMOD_HIDDEN;
    }

    remaining = ex - ey - (int32_t)FMOD_CHUNK;
    while (remaining > 0) {
        (void)fmod_reduce(&mh, &ml, dh, dl, FMOD_CHUNK);
        if ((mh | ml) == 0u)
            return fmod_make(sign, 0u);
        remaining -= (int32_t)FMOD_CHUNK;
    }
    high_zero = fmod_reduce(&mh, &ml, dh, dl, (uint32_t)(remaining + (int32_t)FMOD_CHUNK));
    if (high_zero) {
        mh = ml;
        ey -= 32;
        ml = 0u;
    }
    if (mh == 0u)
        return fmod_make(sign, 0u);

    shift = fmod_clz(mh);
    mh = fmod_lsl(mh, shift) | fmod_lsr(ml, 32u - shift);
    ml = fmod_lsl(ml, shift);
    ey = ey - (int32_t)shift + 10;
    if (ey >= 0) {
        uint32_t lo = (ml >> 11) | (mh << 21);
        uint32_t hi = (sign | (mh >> 11)) + ((uint32_t)ey << 20);
        return fmod_make(hi, lo);
    }

    /* Subnormal result: shift right with the stock round-half-even carry
     * chain (never inexact for fmod, kept for fidelity). */
    shift = (uint32_t)(11 - ey);
    if ((int32_t)shift - 32 < 0) {
        uint32_t back = 32u - shift;
        uint32_t lost = fmod_lsl(ml, back);
        uint32_t carry_in = (ml >> shift) & 1u; /* C from LSLS r3, r2 */
        uint32_t into_lo = fmod_lsl(mh, back);
        uint32_t lo = ml >> shift;
        uint32_t hi = mh >> shift;
        uint32_t round = lost >= FMOD_SIGN + (1u - carry_in) ? 1u : 0u;
        uint64_t sum = (uint64_t)lo + into_lo + round;

        return fmod_make(hi + sign + (uint32_t)(sum >> 32), (uint32_t)sum);
    }
    if ((int32_t)shift > 64)
        return fmod_make(sign, 0u);
    {
        uint32_t right = shift - 32u;
        uint32_t left = 32u - right;
        uint32_t sticky = ml >> 1;
        uint32_t lo = fmod_lsr(mh, right);
        uint32_t spill = fmod_lsl(mh, left);
        /* C from LSLS.W r6, r1, r5; a zero shift keeps C from LSRS r3, r0, #1. */
        uint32_t carry_in = left == 0u ? (ml & 1u) : ((mh >> right) & 1u);
        uint32_t round;
        uint64_t sum;

        sticky |= spill;
        round = sticky >= FMOD_SIGN + (1u - carry_in) ? 1u : 0u;
        sum = (uint64_t)lo + spill + round;
        return fmod_make(sign + (uint32_t)(sum >> 32), (uint32_t)sum);
    }
}

/* Stock 0x57dc40: VFP entry, d0 = x, d1 = y, result in d0. */
IAR_VFP double iar_fmod_57dc40(double x, double y)
{
    union {
        double d;
        uint64_t u;
    } a = {.d = x}, b = {.d = y}, r;

    r.u = iar_fmod_bits_57dc54(a.u, b.u);
    return r.d;
}
