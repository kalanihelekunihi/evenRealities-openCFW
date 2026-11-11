#include <stdint.h>
#include "gomore_primitives/gomore_primitives.h"

uint32_t r1_gomore_stage_60b80_native(
    uint32_t state, uint32_t elapsed, uint32_t time,
    uint32_t utc_offset, uint32_t minute, uint32_t lower,
    uint32_t activity, uint32_t ring, uint32_t unused,
    uint32_t quality, uint32_t output)
{
    (void)unused;
    const uint8_t *activity_record = (const uint8_t *)(uintptr_t)activity;
    const uint8_t *lower_record = (const uint8_t *)(uintptr_t)lower;
    const uint8_t *quality_record = (const uint8_t *)(uintptr_t)quality;
    const float *preceding = (const float *)(uintptr_t)(state - 4u);
    const gomore_primitives_sleep_cycle_input input = {
        .elapsed_seconds = elapsed,
        .current_time = *(const uint32_t *)(uintptr_t)time,
        .utc_offset_minutes = *(const int16_t *)(uintptr_t)utc_offset,
        .minute_sample = *(const float *)(uintptr_t)(minute + 4u),
        .ring_sample = *(const float *)(uintptr_t)ring,
        .input_active = activity_record[5] != 0u,
        .upper_flag = activity_record[4] == 1u,
        .lower_flag = lower_record[12] == 1u,
        .quality_flag4 = quality_record[4] != 0u,
        .quality_flag6 = quality_record[6] != 0u,
        .preceding_fraction = *preceding,
    };
    (void)gomore_primitives_sleep_cycle_update(
        (gomore_primitives_sleep_cycle_state *)(uintptr_t)state,
        &input,
        (gomore_primitives_sleep_interval_result *)(uintptr_t)output);
    return 0u;
}
