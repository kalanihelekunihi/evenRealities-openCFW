/* SPDX-License-Identifier: MIT */
#include <stdint.h>
/* gx_audio_in_get_distance_noise_smooth: deployed audio register read. */
uint32_t open_cfw_gx8002_distance_noise(void)
{
    return *(volatile uint32_t *)(uintptr_t)0xa0a001b8u;
}
