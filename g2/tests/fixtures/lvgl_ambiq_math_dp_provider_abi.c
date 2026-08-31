/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_math_dp_provider.h"

_Static_assert(sizeof(void *) == 4, "G2 pointer ABI changed");
_Static_assert(sizeof(float) == 4, "G2 binary32 ABI changed");
_Static_assert(sizeof(double) == 8, "G2 binary64 ABI changed");

float open_cfw_math_dp_probe_cosf(float value) { return cosf(value); }
float open_cfw_math_dp_probe_sinf(float value) { return sinf(value); }
double open_cfw_math_dp_probe_sqrt(double value) { return sqrt(value); }
float open_cfw_math_dp_probe_tanf(float value) { return tanf(value); }

void open_cfw_math_dp_provider_abi_probe(void)
{
    float (*cosine)(float) = cosf;
    float (*sine)(float) = sinf;
    double (*square_root)(double) = sqrt;
    float (*tangent)(float) = tanf;

    (void)cosine;
    (void)sine;
    (void)square_root;
    (void)tangent;
}
