/* Native image-B 0x100109c0..0x10010b93, float exponential.
 * Source lead: Sun fdlibm e_expf.c, Android bionic a27d2baa blob
 * 4e06556b9377ccd3b700e83ad869ba8122b077e6. Sun permission notice:
 * Copyright (C) 1993 Sun Microsystems, Inc.; permission to copy, modify,
 * and distribute freely is granted provided this notice is preserved.
 * The reduction/threshold constants below follow the native image-B pool,
 * which differs from that upstream file. Native SHA256:
 * d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
#include <stdint.h>

typedef union { uint32_t bits; float number; } gx_exp_word;
static float gx_exp_float(uint32_t bits)
{
    gx_exp_word v;
    v.bits = bits;
    return v.number;
}
static uint32_t gx_exp_bits(float x)
{
    gx_exp_word v;
    v.number = x;
    return v.bits;
}

float gx8002_image_b_expf_100109c0(float argument)
{
    float x = argument;
    uint32_t bits = gx_exp_bits(x);
    uint32_t magnitude = bits & UINT32_C(0x7fffffff);
    uint32_t sign = bits >> 31;
    const float huge = gx_exp_float(UINT32_C(0x7149f2ca));
    const float one = 1.0f;
    const float ln2_hi = gx_exp_float(UINT32_C(0x3f317180));
    const float ln2_lo = gx_exp_float(UINT32_C(0x3717f7d1));
    float hi = 0.0f, lo = 0.0f, c, t;
    int32_t k = 0;

    if (magnitude >= UINT32_C(0x42b17218)) {
        if (magnitude > UINT32_C(0x7f800000)) return x + x;
        if (magnitude == UINT32_C(0x7f800000))
            return sign ? 0.0f : x;
        if (x > gx_exp_float(UINT32_C(0x42b17217)))
            return huge * huge;
        if (x < gx_exp_float(UINT32_C(0xc2cff1b5)))
            return 0.0f;
    }

    if (magnitude > UINT32_C(0x3eb17218)) {
        if (magnitude < UINT32_C(0x3f851592)) {
            hi = x - (sign ? -ln2_hi : ln2_hi);
            lo = sign ? -ln2_lo : ln2_lo;
            k = sign ? -1 : 1;
        } else {
            k = (int32_t)(gx_exp_float(UINT32_C(0x3fb8aa3b)) * x +
                          (sign ? -0.5f : 0.5f));
            t = (float)k;
            hi = x - t * ln2_hi;
            lo = t * ln2_lo;
        }
        x = hi - lo;
    } else if (magnitude < UINT32_C(0x31800000)) {
        if (huge + x > one) return one + x;
    }

    t = x * x;
    c = x - t * (gx_exp_float(UINT32_C(0x3e2aaaab)) +
        t * (gx_exp_float(UINT32_C(0xbb360b61)) +
        t * (gx_exp_float(UINT32_C(0x388ab355)) +
        t * (gx_exp_float(UINT32_C(0xb5ddea0e)) +
             t * gx_exp_float(UINT32_C(0x3331bb4c))))));
    if (k == 0) return one - ((x * c) / (c - 2.0f) - x);

    float y = one - ((lo - (x * c) / (2.0f - c)) - hi);
    uint32_t ybits = gx_exp_bits(y);
    if (k >= -125) {
        return gx_exp_float(ybits + ((uint32_t)k << 23));
    }
    y = gx_exp_float(ybits + ((uint32_t)(k + 100) << 23));
    return y * gx_exp_float(UINT32_C(0x0d800000));
}
