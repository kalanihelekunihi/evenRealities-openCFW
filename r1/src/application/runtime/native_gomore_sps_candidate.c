/* Stock 0x5ef1c: accelerometer-derived SPS candidate update. */
#include <stddef.h>
#include <stdint.h>

#include "../../vendor/gomore_primitives/gomore_primitives.h"

extern double r1_native_sqrt(double);

/* The numeric models used by stock providers at 0x68de0 and 0x69e94. */
static const gomore_primitives_affine_reciprocal_model4 state1_model = {
    {0x1.7cdc1cp-8f, -0x1.2a552p-2f, -0x1.005072p+13f,
     0x1.8d9b9ap-12f, 0x1.32facap-12f, 0x1.86ebap+6f},
};

static const gomore_primitives_linear_model3 state2_model = {
    {0x1.5b5acp+7f, 0x1.5e5cf6p+7f, 0x1.be0f7ap+10f},
    {0x1.7211fap+2f, 0x1.8e2672p+3f, 0x1.3048cap+8f},
    {0x1.b57c9ep-1f, 0x1.1dcaaep+0f, 0x1.88827ap+0f},
    0x1.63dd9cp+3f,
};

static float state2_primary(const float *values)
{
    return gomore_primitives_linear_model3_evaluate(values, &state2_model);
}

static float state2_secondary(const float *values)
{
    return gomore_primitives_sps_secondary_model(values, r1_native_sqrt);
}

static float state1_primary(const float *values)
{
    return gomore_primitives_affine_reciprocal_model4_evaluate(
        values, &state1_model);
}

static float state1_secondary(const float *values)
{
    float result = 0x1.ccd56cp-5f * values[0];
    result += -0x1.b74262p-7f * values[1];
    result += 0x1.677dbep-8f * values[2];
    return result + -0x1.ea6b7p-1f;
}

static float adjust_candidate(float primary, void *state)
{
    const gomore_primitives_sps_model_state *model = state;
    return gomore_primitives_linear_evaluate(
        primary, model->calibration_slope, model->calibration_intercept);
}

static void commit_candidate(void *state, float primary, float secondary)
{
    (void)gomore_primitives_accumulate_pair(state,
        sizeof(gomore_primitives_sps_model_state), primary, secondary);
}

uint32_t r1_gomore_stage_5ef1c_native(
    uint32_t state_address, uint32_t elapsed_updates,
    uint32_t features_address, uint32_t motion_address,
    uint32_t height_address, uint32_t output_address)
{
    static const gomore_primitives_sps_candidate_providers providers = {
        .state2_primary = state2_primary,
        .state2_secondary = state2_secondary,
        .state1_primary = state1_primary,
        .state1_secondary = state1_secondary,
        .adjust = adjust_candidate,
        .commit = commit_candidate,
    };
    const float height = *(const float *)(uintptr_t)height_address;
    (void)gomore_primitives_sps_accelerometer_candidate_update(
        (gomore_primitives_sps_candidate_state *)(uintptr_t)state_address,
        elapsed_updates,
        (const gomore_primitives_sps_features *)(uintptr_t)features_address,
        (const gomore_primitives_sps_motion *)(uintptr_t)motion_address,
        height, &providers,
        (gomore_primitives_sps_candidate_output *)(uintptr_t)output_address);
    return 0u;
}
