/* IAR DLIB truncf leaf (no source path retained).
 * Native 0x59f510..0x59f53c: VFP entry 0x59f510 and bit-pattern core 0x59f520.
 * The only caller is 0x59c746 (translate UI code).
 *
 * Integer only, same convention as runtime/p-01-iar-runtime: the float is moved
 * as its bit pattern, so the unit builds with profile g2-apollo-main-2. */
#include <stdint.h>

typedef union { float f; uint32_t u; } p14_f32_bits_t;

/* truncf core on the IEEE single bit pattern (r0 in, r0 out): |x| < 1 gives a
 * signed zero; exponents of 2^23 and above (integral, Inf, NaN) pass through. */
uint32_t truncf_bits_59f520(uint32_t bits)
{
    int32_t e = (int32_t)((bits >> 23) & 0xffu) - 126;

    if (e <= 0)
        return bits & 0x80000000u;
    if (e >= 24)
        return bits;
    return bits & ~(0x00ffffffu >> (uint32_t)e);
}

/* truncf (VFP entry: moves s0 to r0, calls the core, moves r0 back to s0).
 * Hard-float entry ABI, as stock. */
__attribute__((pcs("aapcs-vfp"))) float truncf_59f510(float value)
{
    p14_f32_bits_t v = { .f = value };

    v.u = truncf_bits_59f520(v.u);
    return v.f;
}
