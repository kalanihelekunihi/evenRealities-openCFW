/* Native image-B 0x10011194. Sun fdlibm scalbnf adapted from glibc-2.3
 * sysdeps/ieee754/flt-32/s_scalbnf.c, commit
 * 451c8c22c68df72324fb61b462e24e4778c5fe23.
 * Native branches/constants including +/-50000, two25, twom25 and signed
 * huge/tiny agree with the pinned source and native ISA.
 */
/*
 * Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
 * Developed at SunPro, a Sun Microsystems, Inc. business.
 * Permission to use, copy, modify, and distribute this software is freely
 * granted, provided that this notice is preserved.
 */
#include <stdint.h>
typedef union { float f; uint32_t u; } gx_scale_word;
static float gx_scale_sign(float magnitude, float sign_source)
{
    gx_scale_word m, s; m.f=magnitude; s.f=sign_source;
    m.u=(m.u & UINT32_C(0x7fffffff)) | (s.u & UINT32_C(0x80000000));
    return m.f;
}
float gx8002_image_b_scalbnf_10011194(float x, int n)
{
    const float two25=3.355443200e+07f, twom25=2.9802322388e-08f;
    const float huge=1.0e+30f, tiny=1.0e-30f;
    gx_scale_word w; w.f=x;
    int32_t k=(int32_t)((w.u & UINT32_C(0x7f800000)) >> 23);
    if(k==0) {
        if ((w.u & UINT32_C(0x7fffffff))==0) return x;
        x*=two25; w.f=x;
        k=(int32_t)((w.u & UINT32_C(0x7f800000)) >> 23)-25;
    }
    if(k==0xff) return x+x;
    k+=n;
    if(n>50000 || k>0xfe) return huge*gx_scale_sign(huge,x);
    if(n< -50000) return tiny*gx_scale_sign(tiny,x);
    if(k>0) { w.u=(w.u&UINT32_C(0x807fffff))|((uint32_t)k<<23); return w.f; }
    if(k<=-25) return tiny*gx_scale_sign(tiny,x);
    k+=25;
    w.u=(w.u&UINT32_C(0x807fffff))|((uint32_t)k<<23);
    return w.f*twom25;
}
