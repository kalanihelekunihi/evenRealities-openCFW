/* SPDX-License-Identifier: MIT */

#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <string.h>

typedef struct syspll_config {
    uint8_t reference_select;
    uint8_t vco_select;
    uint8_t fraction_mode;
    uint8_t reference_divider;
    uint8_t post_divider_1;
    uint8_t post_divider_2;
    uint16_t feedback_divider_integer;
    uint32_t feedback_divider_fraction;
} syspll_config;

uint32_t open_cfw_bootloader_syspll_min_fvco_427040(
    syspll_config *output,
    uint32_t reference_hz,
    uint32_t output_hz,
    uint32_t minimum_vco_hz);

const uint8_t open_cfw_host_syspll_postdiv_table[50] = {
    0x00, 0x11, 0x21, 0x31, 0x41, 0x51, 0x61, 0x71, 0x42, 0x33,
    0x52, 0x62, 0x62, 0x72, 0x72, 0x53, 0x44, 0x63, 0x63, 0x54,
    0x54, 0x73, 0x64, 0x64, 0x64, 0x55, 0x74, 0x74, 0x74, 0x65,
    0x65, 0x75, 0x75, 0x75, 0x75, 0x75, 0x66, 0x76, 0x76, 0x76,
    0x76, 0x76, 0x76, 0x77, 0x77, 0x77, 0x77, 0x77, 0x77, 0x77,
};

static float gcd_result;
static uint32_t selector_status;
static uint8_t selector_mode;
static uint8_t selector_refdiv;
static unsigned gcd_calls;
static unsigned selector_calls;
static float observed_reference_mhz;
static float observed_vco_mhz;

float open_cfw_bootloader_float_gcd_426d48(float first, float second)
{
    ++gcd_calls;
    assert(first > 0.0f && second > 0.0f);
    return gcd_result;
}

uint32_t open_cfw_bootloader_float_encoding_select_426f6c(
    syspll_config *output, float reference_mhz, float vco_mhz)
{
    ++selector_calls;
    observed_reference_mhz = reference_mhz;
    observed_vco_mhz = vco_mhz;
    if (selector_status == 0U) {
        assert(output != NULL);
        output->fraction_mode = selector_mode;
        output->reference_divider = selector_refdiv;
    }
    return selector_status;
}

static void reset_stubs(float gcd, uint32_t status, uint8_t mode, uint8_t refdiv)
{
    gcd_result = gcd;
    selector_status = status;
    selector_mode = mode;
    selector_refdiv = refdiv;
    gcd_calls = 0U;
    selector_calls = 0U;
    observed_reference_mhz = -1.0f;
    observed_vco_mhz = -1.0f;
}

static syspll_config fresh_config(void)
{
    syspll_config output;
    memset(&output, 0xa5, sizeof(output));
    return output;
}

int main(void)
{
    syspll_config output;

    reset_stubs(2.0f, 0U, 1U, 4U);
    output = fresh_config();
    assert(open_cfw_bootloader_syspll_min_fvco_427040(
               &output, 32000000U, 120000000U, 60000000U) == 0U);
    assert(gcd_calls == 1U && selector_calls == 1U);
    assert(observed_reference_mhz == 32.0f && observed_vco_mhz == 120.0f);
    assert(output.post_divider_1 == 1U && output.post_divider_2 == 1U);

    reset_stubs(2.0f, 0U, 1U, 4U);
    output = fresh_config();
    assert(open_cfw_bootloader_syspll_min_fvco_427040(
               &output, 32000000U, 20000000U, 60000000U) == 0U);
    assert(observed_vco_mhz == 60.0f);
    assert(output.post_divider_1 == 3U && output.post_divider_2 == 1U);

    reset_stubs(2.0f, 0U, 1U, 4U);
    output = fresh_config();
    assert(open_cfw_bootloader_syspll_min_fvco_427040(
               &output, 32000000U, 1000000U, 60000000U) == 5U);
    assert(selector_calls == 0U);

    reset_stubs(-1.0f, 0U, 1U, 4U);
    output = fresh_config();
    assert(open_cfw_bootloader_syspll_min_fvco_427040(
               &output, 32000000U, 20000000U, 60000000U) == 0U);
    assert(observed_vco_mhz == 120.0f);
    assert(output.post_divider_1 == 6U && output.post_divider_2 == 1U);

    reset_stubs(2.0f, 1U, 1U, 4U);
    output = fresh_config();
    assert(open_cfw_bootloader_syspll_min_fvco_427040(
               &output, 32000000U, 20000000U, 60000000U) == 1U);
    assert(output.post_divider_1 == 0xa5U && output.post_divider_2 == 0xa5U);

    reset_stubs(2.0f, 0U, 0U, 4U);
    output = fresh_config();
    assert(open_cfw_bootloader_syspll_min_fvco_427040(
               &output, 32000000U, 20000000U, 60000000U) == 5U);
    assert(output.post_divider_1 == 0xa5U && output.post_divider_2 == 0xa5U);

    reset_stubs(2.0f, 0U, 1U, 32U);
    output = fresh_config();
    assert(open_cfw_bootloader_syspll_min_fvco_427040(
               &output, 32000000U, 20000000U, 60000000U) == 0U);
    assert(output.post_divider_1 == 3U && output.post_divider_2 == 1U);
    return 0;
}
