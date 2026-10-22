/* SPDX-License-Identifier: MIT
 * Stock image-A XIP soft-float binary64 entries (toolchain libgcc fp-bit):
 *   0x10209a6c..0x10209aa4 gx8002_fixunsdfsi   (__fixunsdfsi)
 *   0x1020a09c..0x1020a0cc gx8002_adddf3       (__adddf3)
 *   0x1020a0cc..0x1020a104 gx8002_subdf3       (__subdf3)
 *   0x1020a108..0x1020a308 gx8002_muldf3_fixed (__muldf3, pool 0x1020a304)
 *   0x1020a308..0x1020a420 gx8002_divdf3_fixed (__divdf3, pool 0x1020a41c)
 *   0x1020a420..0x1020a460 gx8002_gedf2        (__gedf2)
 *   0x1020a460..0x1020a4d0 gx8002_fixdfsi      (__fixdfsi)
 *   0x1020a4d0..0x1020a528 gx8002_floatunsidf  (__floatunsidf)
 * Doubles travel as r0:r1 / r2:r3 word pairs (CK804EF has no double FPU).
 * Every entry unpacks to the five-word parts record {class, sign,
 * exponent, fraction low, fraction high}; classes are 0/1 NaN, 2 zero,
 * 3 number (implicit one at fraction bit 60, eight guard bits), 4 infinity.
 * The pinned C-SKY GCC 6.3 ck803/hard-fp libgcc.a objects are
 * byte-identical to these stock bodies modulo relocations.
 */
#include <stdint.h>

enum {
    PARTS_CLASS = 0,
    PARTS_SIGN = 1,
    PARTS_EXPONENT = 2,
    PARTS_FRACTION_LOW = 3,
    PARTS_FRACTION_HIGH = 4,
};
enum { CLASS_ZERO = 2u, CLASS_NUMBER = 3u, CLASS_INFINITY = 4u };

extern void gx8002_xip_unpack_double_1020a704(const uint32_t input[2],
                                              uint32_t parts[5]);
extern uint64_t gx8002_xip_pack_double_1020a574(const uint32_t parts[5]);
extern const uint32_t *gx8002_xip_fpadd_parts_10209dd8(
    const uint32_t first[5], const uint32_t second[5], uint32_t result[5]);
extern int32_t gx8002_xip_fpcmp_parts_1020a7e8(const uint32_t first[5],
                                               const uint32_t second[5]);
extern uint64_t __muldi3(uint64_t a, uint64_t b); /* 0x1020a528 */
/* ROM 0x1020bd08: the all-zero signalling NaN parts record (libgcc
 * __thenan_df), currently a file-static in resident_xip_fpadd_parts.c. */
extern const uint32_t gx8002_fpadd_parts_nan[5];

static uint64_t fraction_of(const uint32_t parts[5])
{
    return ((uint64_t)parts[PARTS_FRACTION_HIGH] << 32) |
           parts[PARTS_FRACTION_LOW];
}

static void set_fraction(uint32_t parts[5], uint64_t fraction)
{
    parts[PARTS_FRACTION_LOW] = (uint32_t)fraction;
    parts[PARTS_FRACTION_HIGH] = (uint32_t)(fraction >> 32);
}

static void unpack_words(uint32_t low, uint32_t high, uint32_t parts[5])
{
    const uint32_t words[2] = {low, high};
    gx8002_xip_unpack_double_1020a704(words, parts);
}

static uint64_t add_parts(uint32_t a_low, uint32_t a_high, uint32_t b_low,
                          uint32_t b_high, uint32_t negate_second)
{
    uint32_t first[5];
    uint32_t second[5];
    uint32_t sum[5];
    unpack_words(a_low, a_high, first);
    unpack_words(b_low, b_high, second);
    second[PARTS_SIGN] ^= negate_second;
    return gx8002_xip_pack_double_1020a574(
        gx8002_xip_fpadd_parts_10209dd8(first, second, sum));
}

uint64_t gx8002_adddf3(uint32_t a_low, uint32_t a_high,
                       uint32_t b_low, uint32_t b_high)
{
    return add_parts(a_low, a_high, b_low, b_high, 0u);
}

uint64_t gx8002_subdf3(uint32_t a_low, uint32_t a_high,
                       uint32_t b_low, uint32_t b_high)
{
    return add_parts(a_low, a_high, b_low, b_high, 1u);
}

/* Round-half-even correction shared by multiply and divide: a result
 * exactly on the guard midpoint with nonzero residue is rounded here so
 * that the packer does not round it a second time. */
static uint64_t round_guard(uint64_t fraction, uint32_t residue_nonzero)
{
    if ((fraction & UINT64_C(0xff)) == UINT64_C(0x80) &&
        (fraction & UINT64_C(0x100)) == 0u && residue_nonzero) {
        fraction += UINT64_C(0x80);
        fraction &= ~UINT64_C(0xff);
    }
    return fraction;
}

uint64_t gx8002_muldf3_fixed(uint32_t a_low, uint32_t a_high,
                             uint32_t b_low, uint32_t b_high)
{
    uint32_t a[5];
    uint32_t b[5];
    uint32_t product[5];
    unpack_words(a_low, a_high, a);
    unpack_words(b_low, b_high, b);

    if (a[PARTS_CLASS] < 2u) {
        a[PARTS_SIGN] = a[PARTS_SIGN] != b[PARTS_SIGN];
        return gx8002_xip_pack_double_1020a574(a);
    }
    if (b[PARTS_CLASS] < 2u) {
        b[PARTS_SIGN] = a[PARTS_SIGN] != b[PARTS_SIGN];
        return gx8002_xip_pack_double_1020a574(b);
    }
    if (a[PARTS_CLASS] == CLASS_INFINITY) {
        if (b[PARTS_CLASS] == CLASS_ZERO)
            return gx8002_xip_pack_double_1020a574(gx8002_fpadd_parts_nan);
        a[PARTS_SIGN] = a[PARTS_SIGN] != b[PARTS_SIGN];
        return gx8002_xip_pack_double_1020a574(a);
    }
    if (b[PARTS_CLASS] == CLASS_INFINITY) {
        if (a[PARTS_CLASS] == CLASS_ZERO)
            return gx8002_xip_pack_double_1020a574(gx8002_fpadd_parts_nan);
        b[PARTS_SIGN] = a[PARTS_SIGN] != b[PARTS_SIGN];
        return gx8002_xip_pack_double_1020a574(b);
    }
    if (a[PARTS_CLASS] == CLASS_ZERO) {
        a[PARTS_SIGN] = a[PARTS_SIGN] != b[PARTS_SIGN];
        return gx8002_xip_pack_double_1020a574(a);
    }
    if (b[PARTS_CLASS] == CLASS_ZERO) {
        b[PARTS_SIGN] = a[PARTS_SIGN] != b[PARTS_SIGN];
        return gx8002_xip_pack_double_1020a574(b);
    }

    /* 64x64 -> 128 long-hand product from four __muldi3 calls on
     * zero-extended 32-bit limbs (native call order kept). */
    const uint64_t a_lo = a[PARTS_FRACTION_LOW];
    const uint64_t a_hi = a[PARTS_FRACTION_HIGH];
    const uint64_t b_lo = b[PARTS_FRACTION_LOW];
    const uint64_t b_hi = b[PARTS_FRACTION_HIGH];
    const uint64_t low_low = __muldi3(b_lo, a_lo);
    const uint64_t high_low = __muldi3(b_hi, a_lo);
    const uint64_t high_high = __muldi3(a_hi, b_hi);
    const uint64_t low_high = __muldi3(a_hi, b_lo);

    const uint64_t cross = low_high + high_low;
    uint64_t high = cross < high_low ? (UINT64_C(1) << 32) : 0u;
    const uint64_t low = low_low + (cross << 32);
    if (low < low_low)
        ++high;
    high += high_high + (cross >> 32);

    int32_t exponent = (int32_t)a[PARTS_EXPONENT] +
                       (int32_t)b[PARTS_EXPONENT] + 4;
    product[PARTS_SIGN] = a[PARTS_SIGN] != b[PARTS_SIGN];
    uint64_t residue = low;
    if (high >= (UINT64_C(1) << 61)) {
        do {
            ++exponent;
            if ((high & 1u) != 0u)
                residue = (residue >> 1) | (UINT64_C(1) << 63);
            high >>= 1;
        } while (high >= (UINT64_C(1) << 61));
    } else if (high < (UINT64_C(1) << 60)) {
        do {
            --exponent;
            high <<= 1;
            if ((residue & (UINT64_C(1) << 63)) != 0u)
                high |= 1u;
            residue <<= 1;
        } while (high < (UINT64_C(1) << 60));
    }
    product[PARTS_EXPONENT] = (uint32_t)exponent;
    high = round_guard(high, residue != 0u);
    set_fraction(product, high);
    product[PARTS_CLASS] = CLASS_NUMBER;
    return gx8002_xip_pack_double_1020a574(product);
}

uint64_t gx8002_divdf3_fixed(uint32_t a_low, uint32_t a_high,
                             uint32_t b_low, uint32_t b_high)
{
    uint32_t a[5];
    uint32_t b[5];
    unpack_words(a_low, a_high, a);
    unpack_words(b_low, b_high, b);

    if (a[PARTS_CLASS] < 2u)
        return gx8002_xip_pack_double_1020a574(a);
    if (b[PARTS_CLASS] < 2u)
        return gx8002_xip_pack_double_1020a574(b);
    a[PARTS_SIGN] ^= b[PARTS_SIGN];
    if (a[PARTS_CLASS] == CLASS_INFINITY || a[PARTS_CLASS] == CLASS_ZERO) {
        if (a[PARTS_CLASS] == b[PARTS_CLASS])
            return gx8002_xip_pack_double_1020a574(gx8002_fpadd_parts_nan);
        return gx8002_xip_pack_double_1020a574(a);
    }
    if (b[PARTS_CLASS] == CLASS_INFINITY) {
        set_fraction(a, 0u);
        a[PARTS_EXPONENT] = 0u;
        return gx8002_xip_pack_double_1020a574(a);
    }
    if (b[PARTS_CLASS] == CLASS_ZERO) {
        a[PARTS_CLASS] = CLASS_INFINITY;
        return gx8002_xip_pack_double_1020a574(a);
    }

    uint64_t numerator = fraction_of(a);
    const uint64_t denominator = fraction_of(b);
    a[PARTS_EXPONENT] -= b[PARTS_EXPONENT];
    if (numerator < denominator) {
        numerator <<= 1;
        --a[PARTS_EXPONENT];
    }
    /* Restoring division, one quotient bit per step from bit 60 down
     * (native loop counter 61). */
    uint64_t bit = UINT64_C(1) << 60;
    uint64_t quotient = 0u;
    for (uint32_t step = 61u; step != 0u; --step) {
        if (numerator >= denominator) {
            quotient |= bit;
            numerator -= denominator;
        }
        bit >>= 1;
        numerator <<= 1;
    }
    set_fraction(a, round_guard(quotient, numerator != 0u));
    return gx8002_xip_pack_double_1020a574(a);
}

int32_t gx8002_gedf2(uint32_t a_low, uint32_t a_high,
                     uint32_t b_low, uint32_t b_high)
{
    uint32_t a[5];
    uint32_t b[5];
    unpack_words(a_low, a_high, a);
    unpack_words(b_low, b_high, b);
    if (a[PARTS_CLASS] < 2u || b[PARTS_CLASS] < 2u)
        return -1; /* unordered compares false */
    return gx8002_xip_fpcmp_parts_1020a7e8(a, b);
}

int32_t gx8002_fixdfsi(uint32_t low, uint32_t high)
{
    uint32_t value[5];
    unpack_words(low, high, value);
    if (value[PARTS_CLASS] <= CLASS_ZERO)
        return 0; /* NaN and zero */
    if (value[PARTS_CLASS] == CLASS_INFINITY)
        return (int32_t)(UINT32_C(0x7fffffff) + (value[PARTS_SIGN] != 0u));
    const int32_t exponent = (int32_t)value[PARTS_EXPONENT];
    if (exponent < 0)
        return 0;
    if (exponent >= 31)
        return (int32_t)(UINT32_C(0x7fffffff) + (value[PARTS_SIGN] != 0u));
    const uint32_t magnitude =
        (uint32_t)(fraction_of(value) >> (uint32_t)(60 - exponent));
    return value[PARTS_SIGN] != 0u ? (int32_t)(0u - magnitude)
                                   : (int32_t)magnitude;
}

uint64_t gx8002_floatunsidf(uint32_t value)
{
    /* Zero leaves exponent and fraction unwritten, as in stock. */
    uint32_t parts[5];
    parts[PARTS_SIGN] = 0u;
    if (value == 0u) {
        parts[PARTS_CLASS] = CLASS_ZERO;
        return gx8002_xip_pack_double_1020a574(parts);
    }
    const uint32_t shift = (uint32_t)__builtin_clz(value) + 29u;
    parts[PARTS_CLASS] = CLASS_NUMBER;
    parts[PARTS_EXPONENT] = 60u - shift;
    set_fraction(parts, (uint64_t)value << shift);
    return gx8002_xip_pack_double_1020a574(parts);
}

/* 2^31 is compared and subtracted as the double 0x41e00000:00000000. */
uint32_t gx8002_fixunsdfsi(uint32_t low, uint32_t high)
{
    if (gx8002_gedf2(low, high, 0u, UINT32_C(0x41e00000)) < 0)
        return (uint32_t)gx8002_fixdfsi(low, high);
    const uint64_t reduced = gx8002_subdf3(low, high, 0u, UINT32_C(0x41e00000));
    return (uint32_t)gx8002_fixdfsi((uint32_t)reduced,
                                    (uint32_t)(reduced >> 32)) +
           UINT32_C(0x80000000);
}
