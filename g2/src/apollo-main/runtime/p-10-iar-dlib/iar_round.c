/* IAR DLIB round(): VFP-convention wrapper 0x58f970..0x58f97f around the
 * integer bit kernel 0x58f980..0x58f9d1 (double passed in R0:R1). Callers are
 * the product-test protocol handlers (0x572394, 0x5791a0, 0x57bd06, ...).
 *
 * Halfway cases round away from zero: |x| < 0.5 gives +-0, 0.5 <= |x| < 1 gives
 * +-1, exponents >= 52 (including Inf/NaN) return x unchanged; otherwise half an
 * ulp of the integer boundary is added and the fraction bits are cleared.
 * The wrapper needs a double-precision FPU (profile g2-apollo-main-20). */
#include <stdint.h>

#define IAR_VFP __attribute__((pcs("aapcs-vfp")))

uint64_t iar_round_bits_58f980(uint64_t x)
{
    uint32_t lo = (uint32_t)x;
    uint32_t hi = (uint32_t)(x >> 32);
    int32_t e = (int32_t)((hi >> 20) & 0x7ffu) - 0x3fe;
    if (e <= 0) {
        hi &= 0x80000000u;
        if (e == 0)
            hi |= 0x3ff00000u; /* +-1.0 */
        lo = 0u;
    } else if (e < 53) {
        if (e - 21 >= 0) {
            uint32_t mask = 0xffffffffu >> (uint32_t)(e - 21);
            lo &= ~(mask >> 1);
            uint32_t sum = lo + mask;
            hi += sum < lo;
            lo = sum & ~mask;
        } else {
            uint32_t mask = 0x001fffffu >> (uint32_t)e;
            hi &= ~(mask >> 1);
            hi += mask;
            hi &= ~mask;
            lo = 0u;
        }
    }
    return (uint64_t)hi << 32 | lo;
}

IAR_VFP double iar_round_58f970(double x)
{
    union {
        double d;
        uint64_t u;
    } v = {x};
    v.u = iar_round_bits_58f980(v.u);
    return v.d;
}
