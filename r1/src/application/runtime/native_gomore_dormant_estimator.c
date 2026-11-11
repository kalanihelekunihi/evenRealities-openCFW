/* Stock 0x5feb8: dormant estimator mode gate and record composition. */
#include <stdint.h>

#include "../../vendor/gomore_primitives/gomore_primitives.h"

/* Stock's fixed pointer cell cannot be reused in the source link: that RAM
 * address is occupied by a source-owned IQS table. */
volatile uint32_t r1_gomore_dormant_active_state;

extern int32_t r1_gomore_dormant_record_step_native(void *, void *);

uint32_t r1_gomore_stage_5feb8_native(
    uint32_t state_address, uint32_t elapsed_updates,
    uint32_t current_time_address, uint32_t selected_heart_rate_address,
    uint32_t selected_speed_address, uint32_t profile_address,
    uint32_t auxiliary_address, uint32_t total_energy_address,
    uint32_t output_address)
{
    r1_gomore_dormant_active_state = state_address;
    return (uint32_t)gomore_primitives_dormant_estimator_update(
        (void *)(uintptr_t)state_address,
        GOMORE_PRIMITIVES_DORMANT_ESTIMATOR_STATE_BYTES,
        elapsed_updates,
        (const uint32_t *)(uintptr_t)current_time_address,
        (const float *)(uintptr_t)selected_heart_rate_address,
        (const float *)(uintptr_t)selected_speed_address,
        (const float *)(uintptr_t)profile_address,
        (const float *)(uintptr_t)auxiliary_address,
        (const float *)(uintptr_t)total_energy_address,
        (void *)(uintptr_t)output_address,
        GOMORE_PRIMITIVES_DORMANT_ESTIMATOR_OUTPUT_BYTES,
        r1_gomore_dormant_record_step_native);
}
