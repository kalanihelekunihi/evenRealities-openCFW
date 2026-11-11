/* Stock 0x61198: native step accumulator around the shared C primitive. */
#include <stdint.h>
#include "../../vendor/gomore_primitives/gomore_primitives.h"

extern void r1_gomore_log_native(uint32_t, uint32_t, const char *, ...);

uint32_t r1_gomore_stage_61198_native(uint32_t state_address,
                                       uint32_t scale,
                                       uint32_t input_address,
                                       uint32_t unused,
                                       uint32_t output_address)
{
    (void)unused;
    gomore_primitives_step_accumulator *state =
        (gomore_primitives_step_accumulator *)(uintptr_t)state_address;
    const uint8_t *input = (const uint8_t *)(uintptr_t)input_address;
    float *output = (float *)(uintptr_t)output_address;
    (void)gomore_primitives_step_accumulate(state, scale, input[2], output);
    r1_gomore_log_native(17u, 2u, "[Step]=%f", (double)*output);
    return 0u;
}
