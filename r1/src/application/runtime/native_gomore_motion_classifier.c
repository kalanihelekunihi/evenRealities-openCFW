/* Stock 0x5f4b6: native motion-classifier boundary. */
#include <stddef.h>
#include <stdint.h>
#include "../../vendor/gomore_primitives/gomore_primitives.h"

uint32_t r1_gomore_stage_5f4b6_native(uint32_t state_address,
                                       uint32_t elapsed_seconds,
                                       uint32_t source_address,
                                       uint32_t unused,
                                       uint32_t features_address,
                                       uint32_t output_address)
{
    (void)unused;
    (void)gomore_primitives_motion_classifier_update(
        (uint8_t *)(uintptr_t)state_address, 17u, elapsed_seconds,
        (const uint8_t *)(uintptr_t)source_address, 13u,
        (const uint8_t *)(uintptr_t)features_address, 62u,
        (uint8_t *)(uintptr_t)output_address, 3u, NULL);
    return 0u;
}
