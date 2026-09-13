/* SPDX-License-Identifier: MIT */
/* Binary32 sign operations recovered from stock register-level behavior.
 * Bit operations preserve payloads, signed zero and signaling NaN encodings. */
#include <stdint.h>
_Static_assert(sizeof(float) == sizeof(uint32_t), "binary32 storage required");
float open_cfw_gx8002_copy_float_sign(float magnitude, float sign)
{
    union { float f; uint32_t u; } x = { .f = magnitude }, y = { .f = sign };
    x.u = (x.u & UINT32_C(0x7fffffff)) | (y.u & UINT32_C(0x80000000));
    return x.f;
}
float open_cfw_gx8002_float_absolute(float value)
{
    union { float f; uint32_t u; } x = { .f = value };
    x.u &= UINT32_C(0x7fffffff);
    return x.f;
}
