/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_math_dp_provider.h"

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

    assert(cosf(0.0F) == 1.0F);
    assert(cosf(-0.0F) == 1.0F);
    assert(isnan(cosf(INFINITY)));
    assert(isnan(cosf(NAN)));

    float_result.value = sinf(-0.0F);
    assert(float_result.bits == UINT32_C(0x80000000));
    assert(sinf(0.0F) == 0.0F);
    assert(isnan(sinf(-INFINITY)));
    assert(isnan(sinf(NAN)));

    float_result.value = tanf(-0.0F);
    assert(float_result.bits == UINT32_C(0x80000000));
    assert(tanf(0.0F) == 0.0F);
    assert(isnan(tanf(INFINITY)));
    assert(isnan(tanf(NAN)));

    assert(sqrt(0.0) == 0.0);
    double_result.value = sqrt(-0.0);
    assert(double_result.bits == UINT64_C(0x8000000000000000));
    assert(sqrt(4.0) == 2.0);
    assert(sqrt(INFINITY) == INFINITY);
    assert(isnan(sqrt(-1.0)));
    assert(isnan(sqrt(NAN)));

    return 0;
}
