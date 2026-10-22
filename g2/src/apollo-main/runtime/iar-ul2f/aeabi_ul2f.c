/* IAR runtime library __aeabi_ul2f (unsigned 64-bit integer to float, round
 * to nearest even). Native 0x55b2a4..0x55b2eb, linked between the health
 * protobuf service and driver\touch\drv_cy8c4046fni.c.
 *
 * The 64-bit value arrives in r0 (low) / r1 (high) and the float bits are
 * returned in r0. Stock normalises the top 32 significant bits with a
 * sticky bit for any discarded low bits, then rounds with one sbcs/adc pair:
 * bias 189 - clz accounts for the leading one carried into the exponent. */
#include <stdint.h>

static uint32_t clz32(uint32_t v)
{
    return (uint32_t)__builtin_clz(v); /* v != 0 at every call site */
}

static uint32_t pack(uint32_t exponent, uint32_t m)
{
    uint32_t bits = (exponent << 23) + (m >> 8);
    uint32_t low = m & 0xffu;
    if (low > 0x80u || (low == 0x80u && (m & 0x100u)))
        bits++;
    return bits;
}

uint32_t aeabi_ul2f_55b2a4(uint32_t lo, uint32_t hi)
{
    if (hi != 0u) {
        uint32_t n = clz32(hi);
        uint32_t m = n ? (hi << n) | (lo >> (32u - n)) : hi;
        if ((lo << n) != 0u)
            m |= 1u; /* sticky: any low bits left over */
        return pack(189u - n, m);
    }
    if (lo == 0u)
        return 0u;
    uint32_t n = clz32(lo);
    return pack(157u - n, lo << n);
}
