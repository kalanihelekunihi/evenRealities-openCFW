/* SPDX-License-Identifier: MIT */

#include <assert.h>
#include <math.h>
#include <stdint.h>

uint32_t open_cfw_bootloader_float_ratio_426db4(
    uint8_t *first_ratio, uint16_t *second_ratio, float first, float second);

static float forced_divisor;

float open_cfw_bootloader_float_gcd_426d48(float first, float second)
{
    (void)first;
    (void)second;
    return forced_divisor;
}

float open_cfw_bootloader_fmodf_427ccc(float value, float modulus)
{
    return fmodf(value, modulus);
}

float open_cfw_bootloader_roundf_427d98(float value)
{
    return roundf(value);
}

static void expect_success(float first, float second,
                           uint8_t expected_first, uint16_t expected_second)
{
    uint8_t first_ratio = 0xA5U;
    uint16_t second_ratio = 0x5AA5U;

    forced_divisor = 1.0f;
    assert(open_cfw_bootloader_float_ratio_426db4(
               &first_ratio, &second_ratio, first, second) == 1U);
    assert(first_ratio == expected_first);
    assert(second_ratio == expected_second);
}

static void expect_failure(float first, float second, float divisor)
{
    uint8_t first_ratio = 0xA5U;
    uint16_t second_ratio = 0x5AA5U;

    forced_divisor = divisor;
    assert(open_cfw_bootloader_float_ratio_426db4(
               &first_ratio, &second_ratio, first, second) == 0U);
    assert(first_ratio == 0xA5U);
    assert(second_ratio == 0x5AA5U);
}

int main(void)
{
    expect_success(16.0f, 9.0f, 16U, 9U);
    expect_success(3.0f, 2.0f, 6U, 4U);
    expect_success(1.0f, 1.0f, 4U, 4U);
    expect_success(63.0f, 960.0f, 63U, 960U);

    expect_failure(16.0f, 9.0f, 0x1p-24f);
    expect_failure(3.25f, 4.0f, 1.0f);
    expect_failure(63.0f, 961.0f, 1.0f);
    expect_failure(64.0f, 960.0f, 1.0f);
    expect_failure(0.0f, 4.0f, 1.0f);
    return 0;
}
