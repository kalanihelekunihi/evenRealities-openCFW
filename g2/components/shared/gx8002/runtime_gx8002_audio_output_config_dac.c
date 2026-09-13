/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>
#include <gx_audio_out/gx_audio_out_v2.h>
extern void open_cfw_gx8002_aout_dac_config(volatile uint32_t *, const volatile void *);
_Static_assert(sizeof(GX_AUDIO_OUT_DAC)==24,"Public DAC ABI");
/* Package e21c. Only named fields copied; padding and internal extension at
 * offsets24..35 persist from the existing configuration. */
int open_cfw_gx8002_aout_config_dac(void *handle, const GX_AUDIO_OUT_DAC *config)
{
    if (!config) return -1;
    uintptr_t state=*(volatile uintptr_t *)((uintptr_t)handle+0x30u);
    volatile GX_AUDIO_OUT_DAC *saved=(volatile GX_AUDIO_OUT_DAC *)(state+0x30u);
    __asm__ volatile ("" ::: "memory");
    saved->lp_enable=config->lp_enable;
    __asm__ volatile ("" ::: "memory");
    saved->lp_num=config->lp_num;
    __asm__ volatile ("" ::: "memory");
    saved->lp_value=config->lp_value;
    __asm__ volatile ("" ::: "memory");
    saved->lp_detect_channel=config->lp_detect_channel;
    __asm__ volatile ("" ::: "memory");
    saved->hp_enable=config->hp_enable;
    __asm__ volatile ("" ::: "memory");
    saved->hp_num=config->hp_num;
    __asm__ volatile ("" ::: "memory");
    saved->hp_value=config->hp_value;
    __asm__ volatile ("" ::: "memory");
    saved->hp_detect_channel=config->hp_detect_channel;
    open_cfw_gx8002_aout_dac_config((volatile uint32_t *)0xa0b00000u,saved);
    return 0;
}
