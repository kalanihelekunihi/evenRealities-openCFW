/* SPDX-License-Identifier: MIT */
#include <stdint.h>

/* Recovered package 0xd354; authenticated SDK _pcm_channel_setting.isra.0.
 * Hardware callers provide a valid PCM channel; channel+11 must be below32. */
int open_cfw_gx8002_pcm_channel_setting(uint32_t channel,uint32_t left,
                                      uint32_t right,uint32_t size,uint32_t control)
{
    if (size&127u) return -1;
    if ((left|right)&7u) return -1;
    volatile uint32_t *base=(volatile uint32_t *)(uintptr_t)(0xa0a00000u+channel*36u);
    base[0x44]=control;
    base[0x45]=left;
    base[0x47]=right;
    base[0x48]=size;
    *(volatile uint32_t *)(uintptr_t)0xa0a00104u=1u<<(channel+11u);
    return 0;
}
