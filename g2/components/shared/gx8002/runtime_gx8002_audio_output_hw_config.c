/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>
/* Layout reconstructed from the allocation, PCM, I2S and DAC consumers.
 * Register-position names retain unresolved hardware semantics explicitly. */
typedef struct {
    uint32_t unused0,field9,clock_ratio,pcm_length,data_format,unused5;
    uint32_t bclk,field15,field14,fixed_enable;
} output_i2s_settings;
typedef struct {
    uint32_t enable;
    uint8_t count,padding;
    uint16_t value,channel,padding2;
} output_threshold;
typedef struct {
    uint32_t control_bit1,control_bit0;
    output_i2s_settings i2s;
    output_threshold low,high;
    uint32_t extra_enable,extra_field23,extra_field16;
} output_hw_settings;
_Static_assert(sizeof(output_threshold)==12,"Threshold layout");
_Static_assert(offsetof(output_hw_settings,i2s)==8,"I2S offset");
_Static_assert(offsetof(output_hw_settings,low)==48,"DAC offset");
_Static_assert(offsetof(output_hw_settings,extra_enable)==72,"DAC extension");
_Static_assert(sizeof(output_hw_settings)==84,"Settings size");
/* Mutable: configuration routines update these settings before applying them. */
output_hw_settings open_cfw_gx8002_aout_hw_settings = {
    .control_bit1=0,.control_bit0=1,
    .i2s={.unused5=1},
    .low={.enable=0,.count=3,.value=0xff0f,.channel=3},
    .high={.enable=0,.count=3,.value=0xfff0,.channel=3},
    .extra_enable=0,.extra_field23=4,.extra_field16=0
};
void *open_cfw_gx8002_aout_select_hw_config(unsigned int selector)
{
    (void)selector;
    return &open_cfw_gx8002_aout_hw_settings;
}
