/* SPDX-License-Identifier: MIT */

#include <assert.h>
#include <stdint.h>

float open_cfw_bootloader_float_gcd_426d48(float first, float second);

static unsigned floor_calls;

float open_cfw_bootloader_floorf_427c90(float value)
{
    int32_t integer = (int32_t)value;

    floor_calls++;
    if ((float)integer > value) {
        integer--;
    }
    return (float)integer;
}

static float absolute(float value)
{
    return value < 0.0f ? -value : value;
}

int main(void)
{
    float result;

    floor_calls = 0U;
    result = open_cfw_bootloader_float_gcd_426d48(12.0f, 8.0f);
    assert(absolute(result - 4.0f) < 0x1p-20f);
    assert(floor_calls == 2U);

    floor_calls = 0U;
    result = open_cfw_bootloader_float_gcd_426d48(6.0f, 18.0f);
    assert(absolute(result - 6.0f) < 0x1p-20f);
    assert(floor_calls == 1U);

    floor_calls = 0U;
    result = open_cfw_bootloader_float_gcd_426d48(3.5f, 0x1p-24f);
    assert(result == 3.5f);
    assert(floor_calls == 0U);

    return 0;
}
