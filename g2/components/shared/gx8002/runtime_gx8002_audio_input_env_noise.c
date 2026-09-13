/* SPDX-License-Identifier: MIT */
/* Recovered LvpAuidoInQueryEnvNoise; preserves stock counter-reset behavior. */
#include <stdint.h>
#include <lvp_context.h>
extern unsigned int gx_audio_in_get_distance_noise_smooth(void);
#define COUNTERS ((volatile uint32_t *)0x2002dfac)
int open_cfw_gx8002_audio_input_env_noise(LVP_CONTEXT *context)
{
    unsigned int noise = gx_audio_in_get_distance_noise_smooth();
    unsigned int value;
    if (noise > 66060288) {
        uint32_t count = COUNTERS[0] + 1u;
        COUNTERS[0] = count;
        if ((int32_t)count > 150) {
            COUNTERS[1] = 0; COUNTERS[2] = 0;
            context->env_noise = 2; COUNTERS[3] = 2;
            return 0;
        }
    } else if (noise > 6291456) {
        uint32_t count = COUNTERS[1] + 1u;
        COUNTERS[1] = count;
        if ((int32_t)count > 50) {
            COUNTERS[0] = 0; COUNTERS[2] = 0;
            context->env_noise = 1; COUNTERS[3] = 1;
            return 0;
        }
    } else {
        uint32_t count = COUNTERS[2] + 1u;
        COUNTERS[2] = count;
        if ((int32_t)count > 150) {
            /* Stock clears low again here, whereas upstream clears mid. */
            COUNTERS[0] = 0; COUNTERS[2] = 0;
            context->env_noise = 0; COUNTERS[3] = 0;
            return 0;
        }
    }
    value = COUNTERS[3];
    context->env_noise = value;
    return 0;
}
