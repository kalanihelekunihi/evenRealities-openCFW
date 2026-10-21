/* Native image-B 0x1000f84c..0x1000faa9, binary64 exponential.
 * Adapted from Sun fdlibm e_exp.c, Android bionic a27d2baa blob.
 * Copyright (C) 1993 Sun Microsystems, Inc. All rights reserved.
 * Developed at SunPro, a Sun Microsystems, Inc. business. Permission to
 * use, copy, modify, and distribute this software is freely granted,
 * provided this notice is preserved.
 * Original image SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
#include <stdint.h>

typedef union { uint64_t bits; double number; } gx_exp_double_word;
static double gx_exp_double(uint64_t bits)
{
    gx_exp_double_word value;
    value.bits = bits;
    return value.number;
}
static uint64_t gx_exp_double_bits(double number)
{
    gx_exp_double_word value;
    value.number = number;
    return value.bits;
}

double gx8002_image_b_exp_double_1000f84c(double argument)
{
    double x = argument;
    uint64_t word = gx_exp_double_bits(x);
    uint32_t high = (uint32_t)(word >> 32);
    uint32_t magnitude = high & UINT32_C(0x7fffffff);
    uint32_t sign = high >> 31;
    const double huge = gx_exp_double(UINT64_C(0x7e37e43c8800759c));
    const double two_minus_1000 = gx_exp_double(UINT64_C(0x0170000000000000));
    const double ln2_hi = gx_exp_double(UINT64_C(0x3fe62e42fee00000));
    const double ln2_lo = gx_exp_double(UINT64_C(0x3dea39ef35793c76));
    double hi = 0.0, lo = 0.0, t, c;
    int32_t k = 0;

    if (magnitude >= UINT32_C(0x40862e42)) {
        if (magnitude >= UINT32_C(0x7ff00000)) {
            if (((magnitude & UINT32_C(0xfffff)) | (uint32_t)word) != 0u)
                return x + x;
            return sign ? 0.0 : x;
        }
        if (x > gx_exp_double(UINT64_C(0x40862e42fefa39ef)))
            return huge * huge;
        if (x < gx_exp_double(UINT64_C(0xc0874910d52d3051)))
            return two_minus_1000 * two_minus_1000;
    }

    if (magnitude > UINT32_C(0x3fd62e42)) {
        if (magnitude < UINT32_C(0x3ff0a2b2)) {
            hi = x - (sign ? -ln2_hi : ln2_hi);
            lo = sign ? -ln2_lo : ln2_lo;
            k = sign ? -1 : 1;
        } else {
            k = (int32_t)(gx_exp_double(UINT64_C(0x3ff71547652b82fe)) * x +
                          (sign ? -0.5 : 0.5));
            t = (double)k;
            hi = x - t * ln2_hi;
            lo = t * ln2_lo;
        }
        x = hi - lo;
    } else if (magnitude < UINT32_C(0x3e300000)) {
        if (huge + x > 1.0) return 1.0 + x;
    }

    t = x * x;
    c = x - t * (gx_exp_double(UINT64_C(0x3fc555555555553e)) +
        t * (gx_exp_double(UINT64_C(0xbf66c16c16bebd93)) +
        t * (gx_exp_double(UINT64_C(0x3f11566aaf25de2c)) +
        t * (gx_exp_double(UINT64_C(0xbebbbd41c5d26bf1)) +
             t * gx_exp_double(UINT64_C(0x3e66376972bea4d0))))));
    if (k == 0) return 1.0 - ((x * c) / (c - 2.0) - x);

    double y = 1.0 - ((lo - (x * c) / (2.0 - c)) - hi);
    uint64_t ybits = gx_exp_double_bits(y);
    if (k >= -1021) {
        return gx_exp_double(ybits + ((uint64_t)(uint32_t)k << 52));
    }
    y = gx_exp_double(ybits + ((uint64_t)(uint32_t)(k + 1000) << 52));
    return y * two_minus_1000;
}
