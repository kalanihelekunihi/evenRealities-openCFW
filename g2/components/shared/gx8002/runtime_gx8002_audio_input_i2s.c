/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_in/gx_audio_in_v2.h>
extern void open_cfw_gx8002_platform_gate(uint32_t,uint32_t);
extern volatile uint32_t open_cfw_gx8002_audio_input_state;

/* Register layout is qualified against the pinned C-SKY compiler. */
typedef struct {
    uint32_t reserved0:2, bit2:1, bit3:1, pcm_length:4;
    uint32_t data_format:3, fsync_mode:1, reserved1:4;
    uint32_t clock_mode:1, tdm:1, bclk:2, bit20:1, sample_rate:2;
    uint32_t reserved2:7, enable:1, reserved3:1;
} i2s_input_register;
_Static_assert(sizeof(GX_AUDIO_IN_INPUT_I2S)==24,"I2S input ABI");

/* Recovered package0xd454. Each field assignment is a separate volatile RMW. */
int open_cfw_gx8002_audio_input_i2s(GX_AUDIO_IN_INPUT_I2S parameter)
{
    open_cfw_gx8002_platform_gate(2,1);
    volatile i2s_input_register *input=(volatile i2s_input_register *)(uintptr_t)0xa0a00004u;
    input->pcm_length=parameter.i2s.pcm_length;
    input->data_format=parameter.i2s.data_format;
    input->clock_mode=parameter.i2s.clk_mode;
    input->bclk=parameter.i2s.bclk_sel;
    input->sample_rate=parameter.i2s.i2s_fs;
    input->tdm=(uint32_t)parameter.i2s.data_format>=3u;
    input->fsync_mode=parameter.fsync_mode;
    input->bit20=0;
    input->bit2=0;
    input->bit3=0;
    input->enable=1;
    open_cfw_gx8002_audio_input_state|=4u;
    return 0;
}
