/* Stock 0x81040: refine a staged sleep interval in place. */
#include <stddef.h>
#include <stdint.h>

#include "../../vendor/gomore_primitives/gomore_primitives.h"

void r1_gomore_sleep_stage_refine_native(
    uint32_t configuration_word0, uint32_t configuration_word1,
    uint32_t configuration_word2, uint32_t stages_address,
    uint32_t start_timestamp, uint32_t end_timestamp,
    volatile int32_t *stage_count)
{
    if (stage_count == NULL || stages_address == 0u || *stage_count <= 0) {
        return;
    }

    const uint32_t words[3] = {
        configuration_word0, configuration_word1, configuration_word2
    };
    uint8_t configuration[12];
    for (size_t index = 0u; index < sizeof(configuration); ++index) {
        configuration[index] = (uint8_t)(
            words[index / 4u] >> (8u * (index % 4u)));
    }

    size_t count = (size_t)*stage_count;
    if (gomore_primitives_sleep_stage_refine(
            configuration, (int8_t *)(uintptr_t)stages_address,
            count, &count, end_timestamp - start_timestamp)) {
        *stage_count = (int32_t)count;
    }
}
