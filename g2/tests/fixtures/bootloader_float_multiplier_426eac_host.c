/* SPDX-License-Identifier: MIT */

#include <assert.h>
#include <math.h>
#include <stdint.h>

uint32_t open_cfw_bootloader_float_multiplier_426eac(
    uint8_t *scale_output,
    uint16_t *integer_output,
    uint32_t *fraction_output,
    float first,
    float second);

float open_cfw_bootloader_floorf_427c90(float value)
{
    return floorf(value);
}

float open_cfw_bootloader_fmodf_427ccc(float value, float modulus)
{
    return fmodf(value, modulus);
}

float open_cfw_bootloader_roundf_427d98(float value)
{
    return roundf(value);
}

float open_cfw_bootloader_ceilf_427dd0(float value)
{
    return ceilf(value);
}

static void expect_success(float first,
                           float second,
                           uint8_t expected_scale,
                           uint16_t expected_integer,
                           uint32_t expected_fraction)
{
    uint8_t scale = 0xa5U;
    uint16_t integer = 0xa5a5U;
    uint32_t fraction = 0xa5a5a5a5U;

    assert(open_cfw_bootloader_float_multiplier_426eac(
        &scale, &integer, &fraction, first, second) == 1U);
    assert(scale == expected_scale);
    assert(integer == expected_integer);
    assert(fraction == expected_fraction);
}

static void expect_failure(float first, float second)
{
    uint8_t scale = 0xa5U;
    uint16_t integer = 0xa5a5U;
    uint32_t fraction = 0xa5a5a5a5U;

    assert(open_cfw_bootloader_float_multiplier_426eac(
        &scale, &integer, &fraction, first, second) == 0U);
    assert(scale == 0xa5U);
    assert(integer == 0xa5a5U);
    assert(fraction == 0xa5a5a5a5U);
}

int main(void)
{
    expect_success(1.0f, 10.0f, 1U, 10U, 0U);
    expect_success(4.0f, 45.0f, 1U, 11U, 0x00400000U);
    expect_success(8.0f, 3.0f, 27U, 10U, 0x00200000U);
    expect_success(64.0f, 13.0f, 50U, 10U, 0x00280000U);

    expect_failure(1.0f, 0.1f);
    expect_failure(1.0f, 100.0f);
    expect_failure(0.0f, 1.0f);
    expect_failure(-1.0f, 10.0f);
    return 0;
}
