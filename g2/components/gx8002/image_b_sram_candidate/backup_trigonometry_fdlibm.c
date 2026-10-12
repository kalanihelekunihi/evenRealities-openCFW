/* Image-B native 0x1000fb14 (cos), 0x1000fbb0 (sin), and their
 * 0x1000ded0/0x1000dee0/0x1000df0c float adapters.
 * Control flow and threshold derive from pinned Android bionic
 * libm/src/s_sin.c and s_cos.c (a27d2baa0c1a2ec70f47ea9199b1dd6762c8a349),
 * with the 0x3fe921fb stock comparison confirmed in native instructions.
 * Historical symbol names below are retained for callers, but the address
 * 0xfb14 follows cos and 0xfbb0 follows sin. The one-frame native table
 * oracle exposed the original swapped attribution.
 * Copyright (C) 1993 Sun Microsystems, Inc. All rights reserved.
 * Developed at SunPro. Permission to use, copy, modify and distribute is
 * freely granted provided this notice is preserved.
 */
#include <stdint.h>

typedef union { double value; uint64_t bits; } image_b_binary64;

extern double gx8002_image_b_kernel_sin_10010f50(double x, double y, int tail);
extern double gx8002_image_b_kernel_cos_1001106c(double x, double y);
extern int gx8002_image_b_reduce_pi_over_two_1000fcfc(double x, double y[2]);

double gx8002_image_b_sin_double_1000fb14(double x)
{
    image_b_binary64 word = {.value = x};
    uint32_t ix = (uint32_t)(word.bits >> 32) & UINT32_C(0x7fffffff);
    if (ix <= UINT32_C(0x3fe921fb)) {
        if (ix < UINT32_C(0x3e400000) && (int)x == 0)
            return 1.0;
        return gx8002_image_b_kernel_cos_1001106c(x, 0.0);
    }
    if (ix >= UINT32_C(0x7ff00000)) return x - x;
    double y[2];
    int quadrant = gx8002_image_b_reduce_pi_over_two_1000fcfc(x, y) & 3;
    switch (quadrant) {
    case 0: return gx8002_image_b_kernel_cos_1001106c(y[0], y[1]);
    case 1: return -gx8002_image_b_kernel_sin_10010f50(y[0], y[1], 1);
    case 2: return -gx8002_image_b_kernel_cos_1001106c(y[0], y[1]);
    default: return gx8002_image_b_kernel_sin_10010f50(y[0], y[1], 1);
    }
}

double gx8002_image_b_cos_double_1000fbb0(double x)
{
    image_b_binary64 word = {.value = x};
    uint32_t ix = (uint32_t)(word.bits >> 32) & UINT32_C(0x7fffffff);
    if (ix <= UINT32_C(0x3fe921fb)) {
        if (ix < UINT32_C(0x3e400000) && (int)x == 0)
            return x;
        return gx8002_image_b_kernel_sin_10010f50(x, 0.0, 0);
    }
    if (ix >= UINT32_C(0x7ff00000)) return x - x;
    double y[2];
    int quadrant = gx8002_image_b_reduce_pi_over_two_1000fcfc(x, y) & 3;
    switch (quadrant) {
    case 0: return gx8002_image_b_kernel_sin_10010f50(y[0], y[1], 1);
    case 1: return gx8002_image_b_kernel_cos_1001106c(y[0], y[1]);
    case 2: return -gx8002_image_b_kernel_sin_10010f50(y[0], y[1], 1);
    default: return -gx8002_image_b_kernel_cos_1001106c(y[0], y[1]);
    }
}

float gx8002_image_b_sin_float_1000ded0(float x)
{
    return (float)gx8002_image_b_sin_double_1000fb14((double)x);
}

void gx8002_image_b_sin_float_array_1000dee0(float *output,
                                                const float *input, int count)
{
    for (int i = 0; i < count; ++i)
        output[i] = gx8002_image_b_sin_float_1000ded0(input[i]);
}

void gx8002_image_b_cos_float_array_1000df0c(float *output,
                                                const float *input, int count)
{
    for (int i = 0; i < count; ++i)
        output[i] = (float)gx8002_image_b_cos_double_1000fbb0((double)input[i]);
}
