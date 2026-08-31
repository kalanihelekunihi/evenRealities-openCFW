/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_math_provider.h"

_Static_assert(sizeof(void *) == 4, "G2 pointer ABI changed");
_Static_assert(sizeof(float) == 4, "G2 binary32 ABI changed");
_Static_assert(sizeof(double) == 8, "G2 binary64 ABI changed");

float open_cfw_math_probe_acosf(float value) { return acosf(value); }
float open_cfw_math_probe_atan2f(float y, float x) { return atan2f(y, x); }
float open_cfw_math_probe_atanf(float value) { return atanf(value); }
double open_cfw_math_probe_fmod(double x, double y) { return fmod(x, y); }
float open_cfw_math_probe_fmodf(float x, float y) { return fmodf(x, y); }

void open_cfw_math_provider_abi_probe(void)
{
    float (*arc_cosine)(float) = acosf;
    float (*arc_tangent2)(float, float) = atan2f;
    float (*arc_tangent)(float) = atanf;
    double (*double_modulus)(double, double) = fmod;
    float (*float_modulus)(float, float) = fmodf;

    (void)arc_cosine;
    (void)arc_tangent2;
    (void)arc_tangent;
    (void)double_modulus;
    (void)float_modulus;
}
