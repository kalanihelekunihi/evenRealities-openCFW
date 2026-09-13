/* SPDX-License-Identifier: MIT */
/* Reconstructed binary32 scaling at backup 0x49ad4.
 * Keep exceptional arithmetic observable. Upstream lineage is not yet pinned. */
#include <stdint.h>
extern float open_cfw_gx8002_copy_float_sign(float, float);
float open_cfw_gx8002_scale_float(float x, int n)
{
    union { float f; uint32_t u; } value = { .f = x };
    uint32_t magnitude = value.u & UINT32_C(0x7fffffff);
    int exponent;
    volatile float tiny = 1.0e-30f, huge = 1.0e30f;
    if (!magnitude) return x;
    if (magnitude >= UINT32_C(0x7f800000)) return x + x;
    if (magnitude < UINT32_C(0x00800000)) {
        value.f *= 0x1p25f;
        if (n < -50000) return value.f * tiny;
        exponent = (int)((value.u >> 23) & 255) - 25;
    } else exponent = (int)(magnitude >> 23);
    /* Stock adds in a 32-bit register. Avoid signed-overflow UB in C. */
    exponent = (int32_t)((uint32_t)exponent + (uint32_t)n);
    if (exponent > 254)
        return huge * open_cfw_gx8002_copy_float_sign(huge, value.f);
    if (exponent > 0) {
        value.u = (value.u & UINT32_C(0x807fffff)) | ((uint32_t)exponent << 23);
        return value.f;
    }
    if (exponent < -22) {
        if (n > 50000) return huge * open_cfw_gx8002_copy_float_sign(huge, value.f);
        return tiny * open_cfw_gx8002_copy_float_sign(tiny, value.f);
    }
    value.u = (value.u & UINT32_C(0x807fffff)) | ((uint32_t)(exponent + 25) << 23);
    return value.f * 0x1p-25f;
}
