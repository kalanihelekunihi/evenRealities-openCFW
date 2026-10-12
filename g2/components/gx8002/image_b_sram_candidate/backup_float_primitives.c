/* SPDX-License-Identifier: MIT
 * Native image-B 0x10011298 and 0x100112c4, instruction checked.
 * 0x11298 constructs binary32 0x7fc00000. 0x112c4 clears only bit 31.
 */
#include <stdint.h>
typedef union { float f; uint32_t u; } gx_float_word;
float gx8002_image_b_quiet_nan_10011298(void)
{
    gx_float_word v; v.u = UINT32_C(0x7fc00000); return v.f;
}
float gx8002_image_b_fabsf_100112c4(float x)
{
    gx_float_word v; v.f = x; v.u &= UINT32_C(0x7fffffff); return v.f;
}
/* This is also the ordinary C math ABI used by the compiled power core. */
float fabsf(float x)
{
    return gx8002_image_b_fabsf_100112c4(x);
}
