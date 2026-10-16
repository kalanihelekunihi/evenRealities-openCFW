/* Native semantic_set_motion_period, 0x4a4ec0..0x4a4ed0. */
#include <stdint.h>

uint32_t audio_hub_motion_period_cell;   /* stock RAM 0x20000e68 */
uint32_t audio_hub_motion_duration_cell; /* stock RAM 0x20000e6c */

uint32_t audio_hub_semantic_motion_period_4a4ec0(uint32_t period,
                                                   uint32_t duration)
{
    audio_hub_motion_period_cell = period;
    audio_hub_motion_duration_cell = duration;
    return 0u;
}
