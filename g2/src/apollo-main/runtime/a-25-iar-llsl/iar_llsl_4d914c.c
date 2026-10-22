/* IAR AEABI runtime helper __aeabi_llsl (64-bit logical shift left), linked
 * into the Apollo main image between app_ble_peer_mgr.c and nanopb pb_common.c.
 * Native 0x4d914c..0x4d916e; no source path is retained.
 *
 * Stock truncates the count to 8 bits (uxtb) and uses ARM register-shift
 * semantics, so counts 64..255 yield 0. Integer only (profile g2-apollo-main-2). */
#include <stdint.h>

uint64_t aeabi_llsl_4d914c(uint64_t value, uint32_t count)
{
    uint32_t n = (uint8_t)count;
    uint32_t lo = (uint32_t)value;
    uint32_t hi = (uint32_t)(value >> 32);
    if (n >= 32u) {
        n -= 32u;
        return (uint64_t)(n < 32u ? lo << n : 0u) << 32;
    }
    if (n != 0u) {
        hi = (hi << n) | (lo >> (32u - n));
        lo <<= n;
    }
    return ((uint64_t)hi << 32) | lo;
}
