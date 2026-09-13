/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "runtime_gx8002_analog.h"
extern void open_cfw_gx8002_platform_gate(uint32_t,uint32_t);
extern volatile uint32_t open_cfw_gx8002_audio_input_state;

/* Recovered package0xd3a4. SDK relocations identify the analog helpers.
 * Preserve the original PGA input value; only bypass/input selection normalize. */
int open_cfw_gx8002_audio_input_sadc(uint32_t pga)
{
    open_cfw_gx8002_platform_gate(7,1);
    gx_analog_set_adc_rstn(0);
    gx_analog_set_pga_bypass(!pga);
    gx_analog_set_pga_enable(pga);
    gx_analog_set_adc_sample_clk_sel(1);
    gx_analog_set_adc_out_at_clk(0);
    gx_analog_set_adc_in_sel(!pga);
    gx_analog_set_pga_itrim(0);
    gx_analog_set_adc_rstn(1);
    *(volatile uint32_t *)(uintptr_t)0xa0a00000u |= 64u;
    open_cfw_gx8002_audio_input_state |= 1u;
    return 0;
}
