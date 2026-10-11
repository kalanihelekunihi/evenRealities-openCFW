#include <stdint.h>

/* Stock 0x0059823c integer-only double-to-unsigned-64 runtime helper.
 * The caller supplies a finite nonnegative fraction scaled by 2^32. */
uint64_t __aeabi_d2ulz(double value) {
    uint64_t bits;
    __builtin_memcpy(&bits, &value, sizeof bits);
    uint32_t const sign = (uint32_t)(bits >> 63);
    uint32_t const encoded = (uint32_t)((bits >> 52) & 0x7ffu);
    if (sign != 0u)
        return 0u;
    if (encoded < 1023u)
        return 0u;
    if (encoded >= 1087u)
        return UINT64_MAX;
    uint32_t const shift = encoded - 1023u;
    uint64_t const significand = (1ull << 52) | (bits & 0x000fffffffffffffull);
    return shift >= 52u ? significand << (shift - 52u)
                        : significand >> (52u - shift);
}
