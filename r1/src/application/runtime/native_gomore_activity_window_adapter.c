#include <stdint.h>
#include "gomore_primitives/gomore_primitives.h"

extern float r1_native_sqrtf(float);
extern float r1_native_powf(float, float);

static void activity_statistics(const float *values, uint32_t count,
                                uint32_t radius, float output[4])
{
    (void)gomore_primitives_peak_statistics(values, count, radius, output,
                                             r1_native_powf, r1_native_sqrtf);
}

uint32_t r1_gomore_stage_6138c_native(float quality, uint32_t state_address,
                                      uint32_t axis_record_address,
                                      uint32_t sample_record_address,
                                      uint32_t output_address)
{
    const uint8_t *axis_record=(const uint8_t *)(uintptr_t)axis_record_address;
    const uint8_t *sample_record=(const uint8_t *)(uintptr_t)sample_record_address;
    const gomore_primitives_activity_window_input input={
        .samples=*(const float *const *)(const void *)sample_record,
        .sample_count=*(const int16_t *)(const void *)(sample_record+4),
        .channel_count=sample_record[6],
    };
    const gomore_primitives_activity_window_providers providers={
        .axes={
            *(const float *const *)(const void *)(axis_record+0),
            *(const float *const *)(const void *)(axis_record+4),
            *(const float *const *)(const void *)(axis_record+8),
        },
        .alternate_conditioning=axis_record[12]!=0,
        .square_root=r1_native_sqrtf,
        .statistics=activity_statistics,
    };
    float differences[249];
    (void)gomore_primitives_activity_window_update(
        (gomore_primitives_activity_window_state *)(uintptr_t)state_address,
        quality,&input,&providers,differences,249,
        (gomore_primitives_activity_window_output *)(uintptr_t)output_address);
    return 0;
}
