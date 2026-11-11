#include <stdint.h>
#include <stdbool.h>
#include "gomore_primitives/gomore_primitives.h"
extern float r1_native_floorf(float);
extern float r1_native_sqrtf(float);
uint32_t r1_gomore_stage_5f3d8_native(uint32_t state, uint32_t mode,
                                      uint32_t input, uint32_t output)
{
    const uint8_t *record=(const uint8_t *)(uintptr_t)input;
    const float *channels[3]={
        *(const float *const *)(const void *)(record+0),
        *(const float *const *)(const void *)(record+4),
        *(const float *const *)(const void *)(record+8),
    };
    return (uint32_t)gomore_primitives_sleep_motion_feature(
        (gomore_primitives_sleep_motion_state *)(uintptr_t)state,
        mode,channels,record[12]!=0u,(float *)(uintptr_t)output,
        r1_native_floorf,r1_native_sqrtf);
}
