/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern void open_cfw_gx8002_platform_gate(uint32_t,uint32_t);
extern void gx_mdelay(uint32_t);
extern volatile uint32_t open_cfw_gx8002_audio_input_state;

/* Bitfield layout is checked for the pinned C-SKY compiler by decoded traces. */
typedef struct { uint32_t low:10, field:6, high:16; } pdm_gain_register;
typedef struct { uint32_t low:9, polarity:1, middle:4, enable:1, high:17; } pdm_control_register;

/* Recovered package 0xd408; only the input's low bit selects clock polarity. */
int open_cfw_gx8002_audio_input_pdm(uint32_t polarity)
{
    open_cfw_gx8002_platform_gate(8,1);
    volatile uint32_t *audio=(volatile uint32_t *)(uintptr_t)0xa0a00000u;
    ((volatile pdm_gain_register *)&audio[10])->field=0;
    ((volatile pdm_gain_register *)&audio[11])->field=0;
    ((volatile pdm_control_register *)audio)->polarity=polarity;
    ((volatile pdm_control_register *)audio)->enable=1;
    open_cfw_gx8002_audio_input_state|=2u;
    gx_mdelay(10);
    return 0;
}
