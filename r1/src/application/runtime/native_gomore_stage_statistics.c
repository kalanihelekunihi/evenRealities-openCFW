/* Stock 0x69128: twelve-word sleep-stage statistics. */
#include <stdint.h>
#include "../../vendor/gomore_primitives/gomore_primitives.h"

void r1_gomore_stage_statistics_native(uint32_t stages_address,
                                       uint32_t start_timestamp,
                                       uint32_t end_timestamp,
                                       uint32_t packed,
                                       volatile void *metrics)
{
    (void)gomore_primitives_sleep_stage_statistics(
        (const uint8_t *)(uintptr_t)stages_address,
        packed ? 720u : 2880u,
        start_timestamp,end_timestamp,packed!=0u,
        (float *)(uintptr_t)metrics);
}
