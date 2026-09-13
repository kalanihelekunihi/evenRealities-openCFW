/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_in/gx_audio_in_v2.h>
extern void open_cfw_gx8002_platform_gate(uint32_t,uint32_t);
extern volatile uint32_t open_cfw_gx8002_audio_output_state;
typedef struct {
    uint32_t pcm_length:2, data_format:2, clock_mode:1, bclk:1;
    uint32_t sample_rate:2, left_source:4, right_source:4, bit16:1;
    uint32_t reserved:13, bit30:1, bit31:1;
} i2s_output_register;
_Static_assert(sizeof(GX_AUDIO_IN_OUTPUT_I2S)==28,"I2S output ABI");

/* Recovered package 0xd7b4. Clock gating precedes validation; state
 * publication precedes the final output-control write. */
int open_cfw_gx8002_audio_output_i2s(GX_AUDIO_IN_OUTPUT_I2S parameter)
{
    open_cfw_gx8002_platform_gate(2,1);
    if ((uint32_t)parameter.i2s.bclk_sel>=2u ||
        (uint32_t)parameter.i2s.data_format>=3u ||
        parameter.i2s.pcm_length==PCM_LENGTH_32BIT) return -1;
    volatile i2s_output_register *output=(volatile i2s_output_register *)(uintptr_t)0xa0a00008u;
    output->pcm_length=parameter.i2s.pcm_length;
    output->data_format=parameter.i2s.data_format;
    output->clock_mode=parameter.i2s.clk_mode;
    output->bclk=parameter.i2s.bclk_sel;
    output->sample_rate=parameter.i2s.i2s_fs;
    output->left_source=parameter.left_source;
    output->right_source=parameter.right_source;
    output->bit31=0;
    output->bit30=1;
    open_cfw_gx8002_audio_output_state|=8u;
    output->bit16=1;
    return 0;
}
