/* SPDX-License-Identifier: MIT
 * Image-B analog controls at 0x100051d8, 0x10008048..0x100080dc,
 * and 0x10008134.
 * All seven DAT literals resolve in the pinned image-B payload to base
 * 0xa0005080. Native offsets +8/+0x10/+0x14 give three MMIO registers.
 */
#include <stdint.h>

#define GX8002_IMAGE_B_ANALOG_88 (*(volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005088))
#define GX8002_IMAGE_B_ANALOG_90 (*(volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005090))
#define GX8002_IMAGE_B_ANALOG_94 (*(volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005094))
#define GX8002_IMAGE_B_ANALOG_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0005000) + (offset)))

void gx8002_image_b_analog_config_update_100051d8(void)
{
    GX8002_IMAGE_B_ANALOG_WORD(0x40u) = 0x59u;
    GX8002_IMAGE_B_ANALOG_WORD(0x44u) = 0x59u;
    GX8002_IMAGE_B_ANALOG_WORD(0x48u) = 0x59u;
    GX8002_IMAGE_B_ANALOG_WORD(0x4cu) = 0x59u;
}

int32_t gx8002_image_b_analog_pga_itrim_10008048(uint32_t value)
{
    uint32_t bounded = value < 0x3fu ? value : 0x3fu;
    GX8002_IMAGE_B_ANALOG_88 =
        (GX8002_IMAGE_B_ANALOG_88 & 0xc0u) | (bounded & 0xffu);
    return 0;
}

int32_t gx8002_image_b_analog_pga_bypass_10008064(uint32_t value)
{
    GX8002_IMAGE_B_ANALOG_88 =
        (GX8002_IMAGE_B_ANALOG_88 & 0xbfu) | ((value & 3u) << 6);
    return 0;
}

int32_t gx8002_image_b_analog_pga_enable_1000807c(uint32_t value)
{
    GX8002_IMAGE_B_ANALOG_90 =
        (GX8002_IMAGE_B_ANALOG_90 & 0xbfu) | ((value & 3u) << 6);
    return 0;
}

int32_t gx8002_image_b_analog_adc_sample_clock_10008094(uint32_t value)
{
    GX8002_IMAGE_B_ANALOG_94 =
        (value & 0xffu) | (GX8002_IMAGE_B_ANALOG_94 & 0xfeu);
    return 0;
}

int32_t gx8002_image_b_analog_adc_out_clock_100080ac(uint32_t value)
{
    GX8002_IMAGE_B_ANALOG_94 =
        (GX8002_IMAGE_B_ANALOG_94 & 0xfdu) |
        ((value & 0x7fu) << 1);
    return 0;
}

int32_t gx8002_image_b_analog_adc_input_100080c4(uint32_t value)
{
    GX8002_IMAGE_B_ANALOG_94 =
        (GX8002_IMAGE_B_ANALOG_94 & 0xfbu) |
        ((value & 0x3fu) << 2);
    return 0;
}

int32_t gx8002_image_b_analog_adc_reset_100080dc(uint32_t value)
{
    GX8002_IMAGE_B_ANALOG_94 =
        (GX8002_IMAGE_B_ANALOG_94 & 0xf7u) |
        ((value & 0x1fu) << 3);
    return 0;
}

uint32_t gx8002_image_b_analog_ldo_digital_control_10008134(void)
{
    uint32_t value = GX8002_IMAGE_B_ANALOG_WORD(0x58u) & 0xffu;
    return (value & 4u) != 0u ? 1u + ((value >> 1) & 1u) : 0u;
}
