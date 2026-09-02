/* SPDX-License-Identifier: MIT */

#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <string.h>

typedef struct float_select_output {
    uint8_t reserved_0;
    uint8_t high_rate;
    uint8_t ratio_encoding;
    uint8_t scale;
    uint8_t reserved_4[2];
    uint16_t integer;
    uint32_t fraction;
} float_select_output;

uint32_t open_cfw_bootloader_float_encoding_select_426f6c(
    float_select_output *output, float first, float second);

static uint32_t ratio_result;
static uint32_t multiplier_result;
static unsigned ratio_calls;
static unsigned multiplier_calls;

uint32_t open_cfw_bootloader_float_ratio_426db4(
    uint8_t *scale, uint16_t *integer, float first, float second)
{
    assert(first == 12.5f || isnan(first));
    assert(second == 120.0f || second == 240.0f || second == 960.0f
           || isnan(second));
    ++ratio_calls;
    if (ratio_result != 0U) {
        *scale = 7U;
        *integer = 321U;
    }
    return ratio_result;
}

uint32_t open_cfw_bootloader_float_multiplier_426eac(
    uint8_t *scale,
    uint16_t *integer,
    uint32_t *fraction,
    float first,
    float second)
{
    assert(first == 12.5f || isnan(first));
    assert(second == 120.0f || second == 240.0f || second == 960.0f
           || isnan(second));
    ++multiplier_calls;
    if (multiplier_result != 0U) {
        *scale = 9U;
        *integer = 22U;
        *fraction = 0x123456U;
    }
    return multiplier_result;
}

static float_select_output fresh_output(void)
{
    float_select_output output;

    memset(&output, 0xa5, sizeof(output));
    return output;
}

static void reset_stubs(uint32_t ratio, uint32_t multiplier)
{
    ratio_result = ratio;
    multiplier_result = multiplier;
    ratio_calls = 0U;
    multiplier_calls = 0U;
}

int main(void)
{
    float_select_output output;

    reset_stubs(1U, 1U);
    assert(open_cfw_bootloader_float_encoding_select_426f6c(
               NULL, 12.5f, 120.0f) == 6U);
    assert(ratio_calls == 0U && multiplier_calls == 0U);

    output = fresh_output();
    assert(open_cfw_bootloader_float_encoding_select_426f6c(
               &output, 12.5f, 59.0f) == 5U);
    assert(open_cfw_bootloader_float_encoding_select_426f6c(
               &output, 12.5f, 0x1.e00002p+9f) == 5U);
    assert(ratio_calls == 0U && multiplier_calls == 0U);

    reset_stubs(1U, 0U);
    output = fresh_output();
    assert(open_cfw_bootloader_float_encoding_select_426f6c(
               &output, 12.5f, 240.0f) == 0U);
    assert(ratio_calls == 1U && multiplier_calls == 0U);
    assert(output.reserved_0 == 0xa5U);
    assert(output.high_rate == 1U && output.ratio_encoding == 1U);
    assert(output.scale == 7U && output.integer == 321U);
    assert(output.fraction == 0U);
    assert(output.reserved_4[0] == 0xa5U && output.reserved_4[1] == 0xa5U);

    reset_stubs(0U, 1U);
    output = fresh_output();
    assert(open_cfw_bootloader_float_encoding_select_426f6c(
               &output, 12.5f, 120.0f) == 0U);
    assert(ratio_calls == 1U && multiplier_calls == 1U);
    assert(output.high_rate == 0U && output.ratio_encoding == 0U);
    assert(output.scale == 9U && output.integer == 22U);
    assert(output.fraction == 0x123456U);

    reset_stubs(0U, 0U);
    output = fresh_output();
    assert(open_cfw_bootloader_float_encoding_select_426f6c(
               &output, 12.5f, 960.0f) == 1U);
    assert(ratio_calls == 1U && multiplier_calls == 1U);
    assert(memcmp(&output, &(float_select_output){
        .reserved_0 = 0xa5U,
        .high_rate = 0xa5U,
        .ratio_encoding = 0xa5U,
        .scale = 0xa5U,
        .reserved_4 = {0xa5U, 0xa5U},
        .integer = 0xa5a5U,
        .fraction = 0xa5a5a5a5U,
    }, sizeof(output)) == 0);

    reset_stubs(1U, 0U);
    output = fresh_output();
    assert(open_cfw_bootloader_float_encoding_select_426f6c(
               &output, NAN, NAN) == 0U);
    assert(output.high_rate == 0U);
    return 0;
}
