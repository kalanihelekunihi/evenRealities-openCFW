/* SPDX-License-Identifier: MIT
 * Native analog byte-register setters 0x10205e34/50/68/80/98/b0/c8.
 * Device uses word accesses but each native write zero-extends the low byte.
 */
#include <stdint.h>

static volatile uint32_t *const analog =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005080);

static void update_byte(uint32_t offset, uint32_t clear_mask, uint32_t bits)
{
    uint32_t current = analog[offset / 4u];
    analog[offset / 4u] = ((current & clear_mask) | bits) & 0xffu;
}

uint32_t gx8002_xip_analog_pga_itrim_10205e34(uint32_t value)
{
    if (value > 63u) value = 63u;
    update_byte(8u, 0xc0u, value);
    return 0u;
}

uint32_t gx8002_xip_analog_pga_bypass_10205e50(uint32_t value)
{
    update_byte(8u, 0xbfu, value << 6u);
    return 0u;
}

uint32_t gx8002_xip_analog_pga_enable_10205e68(uint32_t value)
{
    update_byte(0x10u, 0xbfu, value << 6u);
    return 0u;
}

uint32_t gx8002_xip_analog_adc_sample_clk_10205e80(uint32_t value)
{
    update_byte(0x14u, 0xfeu, value);
    return 0u;
}

uint32_t gx8002_xip_analog_adc_out_clk_10205e98(uint32_t value)
{
    update_byte(0x14u, 0xfdu, value << 1u);
    return 0u;
}

uint32_t gx8002_xip_analog_adc_input_select_10205eb0(uint32_t value)
{
    update_byte(0x14u, 0xfbu, value << 2u);
    return 0u;
}

uint32_t gx8002_xip_analog_adc_rstn_10205ec8(uint32_t value)
{
    update_byte(0x14u, 0xf7u, value << 3u);
    return 0u;
}
