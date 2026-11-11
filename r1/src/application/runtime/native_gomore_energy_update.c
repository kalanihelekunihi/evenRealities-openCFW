/* Stock 0x5f56c: energy update over the consolidated C primitives. */
#include <stdint.h>

#include "../../vendor/gomore_primitives/gomore_primitives.h"

extern float r1_native_expf(float);
extern float r1_native_logf(float);
extern double r1_native_log(double);

uint32_t r1_gomore_stage_5f56c_native(
    uint32_t state_address, uint32_t elapsed_seconds,
    uint32_t current_address, uint32_t profile_address,
    uint32_t upper_address, uint32_t lower_address,
    uint32_t settings_address, uint32_t metric_address,
    uint32_t auxiliary_address, uint32_t control_address,
    uint32_t secondary_address, uint32_t output_address)
{
    return gomore_primitives_energy_update(
        (gomore_primitives_energy_update_state *)(uintptr_t)state_address,
        (int32_t)elapsed_seconds,
        *(const float *)(uintptr_t)current_address,
        (const void *)(uintptr_t)profile_address, 64u,
        *(const float *)(uintptr_t)upper_address,
        *(const float *)(uintptr_t)lower_address,
        (const float *)(uintptr_t)settings_address,
        *(const float *)(uintptr_t)metric_address,
        *(const float *)(uintptr_t)auxiliary_address,
        *(const int8_t *)(uintptr_t)(control_address + 1u),
        *(const float *)(uintptr_t)secondary_address,
        r1_native_expf, r1_native_logf, r1_native_log,
        &gomore_primitives_energy_table_defaults,
        (gomore_primitives_energy_update_output *)(uintptr_t)output_address);
}
