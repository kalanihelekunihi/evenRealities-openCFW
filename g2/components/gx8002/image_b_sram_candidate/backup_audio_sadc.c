/* SPDX-License-Identifier: MIT
 * Image-B SADC input path 0x1000532c. All eight analog leaves are already
 * source-owned in backup_analog_controls.c; call order follows native BSRs.
 */
#include <stdint.h>

extern void gx8002_image_b_platform_gate_10003be8(uint32_t module, uint32_t enabled);
extern int32_t gx8002_image_b_analog_adc_reset_100080dc(uint32_t value);
extern int32_t gx8002_image_b_analog_pga_bypass_10008064(uint32_t value);
extern int32_t gx8002_image_b_analog_pga_enable_1000807c(uint32_t value);
extern int32_t gx8002_image_b_analog_adc_sample_clock_10008094(uint32_t value);
extern int32_t gx8002_image_b_analog_adc_out_clock_100080ac(uint32_t value);
extern int32_t gx8002_image_b_analog_adc_input_100080c4(uint32_t value);
extern int32_t gx8002_image_b_analog_pga_itrim_10008048(uint32_t value);

#define SADC_CONTROL (*(volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00000))
#define SADC_STATE (*(volatile uint32_t *)(uintptr_t)UINT32_C(0x20017624))

int32_t gx8002_image_b_sadc_input_1000532c(uint32_t pga_enabled)
{
    gx8002_image_b_platform_gate_10003be8(7u, 1u);
    (void)gx8002_image_b_analog_adc_reset_100080dc(0u);
    (void)gx8002_image_b_analog_pga_bypass_10008064(pga_enabled == 0u);
    (void)gx8002_image_b_analog_pga_enable_1000807c(pga_enabled);
    (void)gx8002_image_b_analog_adc_sample_clock_10008094(1u);
    (void)gx8002_image_b_analog_adc_out_clock_100080ac(0u);
    (void)gx8002_image_b_analog_adc_input_100080c4(pga_enabled == 0u);
    (void)gx8002_image_b_analog_pga_itrim_10008048(0u);
    (void)gx8002_image_b_analog_adc_reset_100080dc(1u);
    SADC_CONTROL = SADC_CONTROL | (1u << 6);
    SADC_STATE = SADC_STATE | 1u;
    return 0;
}
