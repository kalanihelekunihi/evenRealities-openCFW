/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_math_provider.h"

#include <assert.h>
#include <math.h>
#include <stdint.h>

typedef union test_double_bits {
    double value;
    uint64_t bits;
} test_double_bits;

typedef union test_float_bits {
    float value;
    uint32_t bits;
} test_float_bits;

int main(void)
{
    test_double_bits double_result;
    test_float_bits float_result;

    assert(atanf(0.0F) == 0.0F);
    assert(atanf(-0.0F) == -0.0F);
    assert(atanf(1.0F) > 0.7853980F && atanf(1.0F) < 0.7853983F);
    assert(atanf(INFINITY) > 1.57F && atanf(INFINITY) < 1.58F);
    assert(isnan(atanf(NAN)));

    assert(atan2f(0.0F, 1.0F) == 0.0F);
    assert(atan2f(1.0F, 0.0F) > 1.57F);
    assert(atan2f(-1.0F, 0.0F) < -1.57F);
    assert(atan2f(0.0F, -1.0F) > 3.14F);
    assert(isnan(atan2f(NAN, 1.0F)));

    assert(acosf(1.0F) == 0.0F);
    assert(acosf(0.0F) > 1.57F && acosf(0.0F) < 1.58F);
    assert(acosf(-1.0F) > 3.14F);
    assert(isnan(acosf(1.0001F)));

    assert(fmod(5.5, 2.0) == 1.5);
    assert(fmod(-5.5, 2.0) == -1.5);
    assert(fmodf(5.5F, 2.0F) == 1.5F);
    assert(fmodf(-5.5F, 2.0F) == -1.5F);
    double_result.value = fmod(-4.0, 2.0);
    float_result.value = fmodf(-4.0F, 2.0F);
    assert(double_result.bits == UINT64_C(0x8000000000000000));
    assert(float_result.bits == UINT32_C(0x80000000));
    assert(isnan(fmod(1.0, 0.0)));
    assert(isnan(fmodf(1.0F, 0.0F)));
    assert(isnan(fmod(INFINITY, 2.0)));
    assert(isnan(fmodf(INFINITY, 2.0F)));

    return 0;
}
