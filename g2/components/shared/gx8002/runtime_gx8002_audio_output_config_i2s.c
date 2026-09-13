/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_out/gx_audio_out_v2.h>
extern void open_cfw_gx8002_aout_i2s_config(volatile uint32_t *, const volatile uint32_t *);
extern void open_cfw_gx8002_aout_set_lodac(void);
_Static_assert(sizeof(GX_AUDIO_OUT_I2S)==12,"Public I2S ABI");
/* Package e1f0: preserve copy order and untouched internal configuration. */
int open_cfw_gx8002_aout_config_i2s(void *handle, const GX_AUDIO_OUT_I2S *config)
{
    if (!config) return -1;
    volatile uint32_t *state=*(volatile uint32_t *volatile *)((uintptr_t)handle+48);
    state[5]=config->pcm_length;
    __asm__ volatile ("" ::: "memory");
    state[6]=config->data_format;
    __asm__ volatile ("" ::: "memory");
    state[8]=config->bclk;
    open_cfw_gx8002_aout_i2s_config((volatile uint32_t *)0xa0b00000u,state+2);
    open_cfw_gx8002_aout_set_lodac();
    return 0;
}
