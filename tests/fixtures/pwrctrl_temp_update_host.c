#include <stdint.h>

uint32_t open_cfw_test_pwrctrl_temp_status;
uint32_t open_cfw_test_pwrctrl_temp_lower_bits;
uint32_t open_cfw_test_pwrctrl_temp_higher_bits;
uint32_t open_cfw_test_pwrctrl_temp_call_count;
uint32_t open_cfw_test_pwrctrl_temp_stimulus;
uint32_t open_cfw_test_pwrctrl_temp_enabled;
uint32_t open_cfw_test_pwrctrl_temp_input_bits;

union open_cfw_test_pwrctrl_temp_float_bits {
    float floating;
    uint32_t bits;
};

static uint32_t
open_cfw_test_pwrctrl_temp_spot_update(
    uint32_t stimulus,
    uint32_t enabled,
    void *arguments
)
{
    float *parameters = (float *)arguments;
    union open_cfw_test_pwrctrl_temp_float_bits value;

    open_cfw_test_pwrctrl_temp_stimulus = stimulus;
    open_cfw_test_pwrctrl_temp_enabled = enabled;
    value.floating = parameters[0];
    open_cfw_test_pwrctrl_temp_input_bits = value.bits;
    value.bits = open_cfw_test_pwrctrl_temp_lower_bits;
    parameters[1] = value.floating;
    value.bits = open_cfw_test_pwrctrl_temp_higher_bits;
    parameters[2] = value.floating;
    ++open_cfw_test_pwrctrl_temp_call_count;
    return open_cfw_test_pwrctrl_temp_status;
}

#define OPEN_CFW_PWRCTRL_TEMP_SPOT_UPDATE(stimulus, enabled, arguments) \
    open_cfw_test_pwrctrl_temp_spot_update( \
        (stimulus), \
        (enabled), \
        (arguments) \
    )

#include "../../components/apollo_main/core_overlay/pwrctrl_temp_update.c"

uint32_t
open_cfw_test_pwrctrl_temp_call(
    uint32_t temperature_bits,
    uint32_t *threshold_bits
)
{
    union open_cfw_test_pwrctrl_temp_float_bits temperature;
    struct open_cfw_pwrctrl_temp_thresholds thresholds;
    union open_cfw_test_pwrctrl_temp_float_bits value;
    uint32_t result;

    temperature.bits = temperature_bits;
    value.bits = threshold_bits[0];
    thresholds.low = value.floating;
    value.bits = threshold_bits[1];
    thresholds.high = value.floating;
    result = open_cfw_pwrctrl_temp_update(
        temperature.floating,
        &thresholds
    );
    value.floating = thresholds.low;
    threshold_bits[0] = value.bits;
    value.floating = thresholds.high;
    threshold_bits[1] = value.bits;
    return result;
}

void
open_cfw_test_pwrctrl_temp_reset(
    uint32_t status,
    uint32_t lower_bits,
    uint32_t higher_bits
)
{
    open_cfw_test_pwrctrl_temp_status = status;
    open_cfw_test_pwrctrl_temp_lower_bits = lower_bits;
    open_cfw_test_pwrctrl_temp_higher_bits = higher_bits;
    open_cfw_test_pwrctrl_temp_call_count = 0U;
    open_cfw_test_pwrctrl_temp_stimulus = 0xFFFFFFFFU;
    open_cfw_test_pwrctrl_temp_enabled = 0xFFFFFFFFU;
    open_cfw_test_pwrctrl_temp_input_bits = 0U;
}
