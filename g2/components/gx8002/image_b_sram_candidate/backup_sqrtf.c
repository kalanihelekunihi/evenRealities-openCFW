/* Native image-B 0x10010bcc, source reduced from its bit-by-bit ISA.
 * Algorithm originates in Sun fdlibm e_sqrtf.c (Sun notice preserved below).
 * The native binary uses fixed nearest-even final rounding on the remainder.
 * Image SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
/*
 * Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
 * Developed at SunPro, a Sun Microsystems, Inc. business.
 * Permission to use, copy, modify, and distribute this software is freely
 * granted, provided that this notice is preserved.
 */
#include <stdint.h>
typedef union { float f; uint32_t u; } gx_sqrt_word;
float gx8002_image_b_sqrtf_10010bcc(float x)
{
    gx_sqrt_word w; w.f = x;
    uint32_t ax = w.u & UINT32_C(0x7fffffff);
    if (ax >= UINT32_C(0x7f800000)) return x*x+x;
    if (ax == 0) return x;
    if (w.u & UINT32_C(0x80000000)) return (x-x)/(x-x);

    int32_t exp = (int32_t)(w.u >> 23);
    uint32_t mant = w.u;
    if (exp == 0) {
        int32_t shifts = 0;
        while (!(mant & UINT32_C(0x00800000))) { mant <<= 1; ++shifts; }
        exp -= shifts - 1;
    }
    exp -= 127;
    mant = (mant & UINT32_C(0x007fffff)) | UINT32_C(0x00800000);
    if (exp & 1) mant += mant;
    exp >>= 1;
    mant += mant;
    uint32_t q = 0, sum = 0, bit = UINT32_C(0x01000000);
    while (bit) {
        uint32_t t = sum + bit;
        if (t <= mant) { sum = t + bit; mant -= t; q += bit; }
        mant += mant;
        bit >>= 1;
    }
    /* Native 0x10010c36..0x10010c3e: one-bit tie-even increment. */
    if (mant) q = (q + 1u) & ~UINT32_C(1);
    w.u = (q >> 1) + UINT32_C(0x3f000000) + ((uint32_t)exp << 23);
    return w.f;
}
