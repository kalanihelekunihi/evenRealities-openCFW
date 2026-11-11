/* Stock 0x61274: native activity accumulator around the shared C primitive. */
#include <stdint.h>
#include "../../vendor/gomore_primitives/gomore_primitives.h"

uint32_t r1_gomore_stage_61274_native(uint32_t state_cell_address,
                                       uint32_t elapsed_updates,
                                       uint32_t seconds_address,
                                       uint32_t timezone_address,
                                       uint32_t step_address,
                                       uint32_t energy_address,
                                       uint32_t speed_address,
                                       uint32_t output_address)
{
    (void)elapsed_updates;
    const uint32_t state_address =
        *(const uint32_t *)(uintptr_t)state_cell_address;
    gomore_primitives_activity_accumulator_state *state =
        (gomore_primitives_activity_accumulator_state *)(uintptr_t)state_address;
    const uint32_t seconds = *(const uint32_t *)(uintptr_t)seconds_address;
    const int16_t timezone = *(const int16_t *)(uintptr_t)timezone_address;
    const float step = *(const float *)(uintptr_t)step_address;
    const gomore_primitives_energy_update_output *energy =
        (const gomore_primitives_energy_update_output *)(uintptr_t)energy_address;
    const float speed = *(const float *)(uintptr_t)speed_address;
    gomore_primitives_activity_accumulator_output *output =
        (gomore_primitives_activity_accumulator_output *)(uintptr_t)output_address;
    (void)gomore_primitives_activity_accumulate(state, seconds, timezone,
                                                step, energy, speed, output);
    return 0u;
}
