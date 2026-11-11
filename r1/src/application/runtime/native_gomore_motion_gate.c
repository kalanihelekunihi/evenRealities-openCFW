/* Stock 0x5f264: native motion bucket and weighted gate boundary. */
#include <stdint.h>
#include "../../vendor/gomore_primitives/gomore_primitives.h"

/* Eighteen non-executable Float32 weights at stock 0xbd2e4. */
static const float motion_weights[18] = {
    -0x1.e9c8bep-7f, -0x1.60e6c8p-7f, -0x1.7557c8p-7f,
    -0x1.84ac2ap-7f, -0x1.6cb0dap-7f, -0x1.5cdaecp-7f,
    -0x1.5576eep-7f, -0x1.786694p-7f, -0x1.b82162p-7f,
    -0x1.862476p-7f, -0x1.7a093ap-7f, -0x1.a4a38ap-7f,
    -0x1.a1719cp-7f, -0x1.f2a28ep-7f, -0x1.257e4ap-6f,
    -0x1.b3f04cp-6f, -0x1.24145p-5f, -0x1.1b1494p-4f,
};

uint32_t r1_gomore_stage_5f264_native(uint32_t state_address,
                                       uint32_t elapsed_seconds,
                                       uint32_t timestamp_address,
                                       uint32_t sample_address,
                                       uint32_t output_address)
{
    gomore_primitives_motion_gate_state *state =
        (gomore_primitives_motion_gate_state *)(uintptr_t)state_address;
    const uint32_t timestamp =
        *(volatile const uint32_t *)(uintptr_t)timestamp_address;
    const float sample =
        *(volatile const float *)(uintptr_t)sample_address;
    gomore_primitives_motion_gate_output *output =
        (gomore_primitives_motion_gate_output *)(uintptr_t)output_address;
    (void)gomore_primitives_motion_gate_accumulate(
        state, elapsed_seconds, timestamp, sample, motion_weights, output);
    return 0u;
}
