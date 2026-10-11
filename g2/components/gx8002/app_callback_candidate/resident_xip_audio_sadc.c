/* SPDX-License-Identifier: MIT
 * Native SADC input root 0x10203e18, with real analog-register children.
 */
#include <stdint.h>

extern void gx8002_resident_platform_gate_25080(uint32_t, uint32_t);
extern void gx8002_xip_analog_adc_rstn_10205ec8(uint32_t);
extern void gx8002_xip_analog_pga_bypass_10205e50(uint32_t);
extern void gx8002_xip_analog_pga_enable_10205e68(uint32_t);
extern void gx8002_xip_analog_adc_sample_clk_10205e80(uint32_t);
extern void gx8002_xip_analog_adc_out_clk_10205e98(uint32_t);
extern void gx8002_xip_analog_adc_input_select_10205eb0(uint32_t);
extern void gx8002_xip_analog_pga_itrim_10205e34(uint32_t);

uint32_t gx8002_xip_audio_input_sadc_10203e18(uint32_t enabled)
{
    gx8002_resident_platform_gate_25080(7u, 1u);
    gx8002_xip_analog_adc_rstn_10205ec8(0u);
    gx8002_xip_analog_pga_bypass_10205e50(enabled == 0u ? 1u : 0u);
    gx8002_xip_analog_pga_enable_10205e68(enabled);
    gx8002_xip_analog_adc_sample_clk_10205e80(1u);
    gx8002_xip_analog_adc_out_clk_10205e98(0u);
    gx8002_xip_analog_adc_input_select_10205eb0(enabled == 0u ? 1u : 0u);
    gx8002_xip_analog_pga_itrim_10205e34(0u);
    gx8002_xip_analog_adc_rstn_10205ec8(1u);
    volatile uint32_t *const ain =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00000);
    *ain |= UINT32_C(1) << 6u;
    volatile uint32_t *const channels =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027330);
    *channels |= 1u;
    return 0u;
}
