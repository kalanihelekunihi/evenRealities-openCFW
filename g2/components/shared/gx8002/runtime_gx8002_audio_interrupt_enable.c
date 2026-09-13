/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_in/gx_audio_in_v2.h>
/* Recovered package 0xdd44. Status clear precedes enable, follows disable. */
int open_cfw_gx8002_audio_interrupt_enable(GX_AUDIO_IN_IRQ_TYPE type,unsigned int enable)
{
    volatile uint32_t *registers=(volatile uint32_t *)(uintptr_t)0xa0a00100u;
    if (enable) {
        registers[1]=(uint32_t)type;
        registers[0]|=(uint32_t)type;
    } else {
        registers[0]&=~(uint32_t)type;
        registers[1]=(uint32_t)type;
    }
    return 0;
}
