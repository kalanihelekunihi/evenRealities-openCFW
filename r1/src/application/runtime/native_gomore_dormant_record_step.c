/* Stock 0x721b4: one dormant speed and heart-rate estimator cycle. */
#include <stddef.h>
#include <stdint.h>

#include "../../vendor/gomore_primitives/gomore_primitives.h"

extern float r1_native_atanf(float);
extern float r1_native_cosf(float);
extern float r1_native_sinf(float);
extern float r1_native_powf(float, float);
extern float r1_native_atan2f(float, float);
extern float r1_native_sqrtf(float);
extern float r1_native_logf(float);
extern float r1_native_expf(float);

_Static_assert(sizeof(gomore_primitives_dormant_estimator_record) == 36u,
               "stock dormant record size");
_Static_assert(offsetof(gomore_primitives_dormant_estimator_record,
                        trailing_total_energy) == 32u,
               "stock dormant trailing float offset");

static void solve_quadratic(float a, float b, float c, void *state)
{
    (void)gomore_primitives_positive_quadratic_roots(
        a, b, c, (float *)((uint8_t *)state + 0x18u), r1_native_powf);
}

static void solve_cubic(float a, float b, float c, float d, void *state)
{
    (void)gomore_primitives_cubic_candidates(
        a, b, c, d, state, 0x2cu,
        r1_native_powf, r1_native_atan2f, r1_native_sqrtf,
        r1_native_logf, r1_native_expf, r1_native_cosf,
        r1_native_sinf);
}

static float reduce_root(float primary, float secondary, float auxiliary,
                         void *state, int32_t mode)
{
    float result = 0.0f;
    (void)gomore_primitives_dormant_root_reduce(
        primary, secondary, auxiliary, state, 0x2Cu, mode,
        r1_native_atanf, r1_native_cosf, r1_native_powf, &result);
    return result;
}

static float finalize_root(float reduced, float auxiliary, void *state,
                           int32_t mode)
{
    float result = 0.0f;
    (void)gomore_primitives_dormant_root_resolve(
        reduced, auxiliary, state, 0x2Cu, mode, r1_native_powf,
        solve_quadratic, solve_cubic, &result);
    return result;
}

static void accumulate_ratio(
    void *state, const gomore_primitives_dormant_ratio_input *input)
{
    uint8_t *const bytes = state;
    (void)gomore_primitives_dormant_ratio_accumulator(
        (gomore_primitives_dormant_ratio_accumulator_state *)(void *)
            (bytes + 0x210u),
        input, bytes[0x0du], r1_native_powf);
}

int32_t r1_gomore_dormant_record_step_native(void *state, void *record)
{
    const gomore_primitives_dormant_estimator_record *source = record;
    gomore_primitives_dormant_cycle_input input = {
        .sample_index = (int32_t)source->sample_index,
        .raw_heart_rate = source->selected_heart_rate,
        .selected_speed = source->selected_speed,
        .auxiliary_speed = source->current_auxiliary,
        .copied_auxiliary_1 = source->copied_auxiliary_1,
        .copied_auxiliary_2 = source->copied_auxiliary_2,
        .auxiliary = (gomore_primitives_dormant_cycle_auxiliary *)
            (source->configuration + 2),
        .trailing_total_energy = source->trailing_total_energy,
    };
    const gomore_primitives_dormant_cycle_providers providers = {
        .arctangent = r1_native_atanf,
        .cosine = r1_native_cosf,
        .sine = r1_native_sinf,
        .power = r1_native_powf,
        .reduce = reduce_root,
        .finalize = finalize_root,
        .filter_heart_rate =
            gomore_primitives_dormant_heart_rate_filter_update,
        .accumulate_ratio = accumulate_ratio,
    };
    int32_t result = -1016;
    if (!gomore_primitives_dormant_estimator_cycle(
            state, GOMORE_PRIMITIVES_DORMANT_ESTIMATOR_STATE_BYTES,
            &input, &providers, &result)) {
        return -1;
    }
    return result;
}
