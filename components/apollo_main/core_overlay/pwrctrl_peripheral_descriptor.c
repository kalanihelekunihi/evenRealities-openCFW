/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 peripheral-power descriptor adaptation from AmbiqSuite
 * SDK 5.1.0. The reviewed stock helper, callers, table, and host behavioral
 * evidence are recorded in EVIDENCE.md.
 */

typedef struct open_cfw_pwrctrl_peripheral_descriptor {
    unsigned int power_enable_register;
    unsigned int peripheral_enable_mask;
    unsigned int power_status_register;
    unsigned int peripheral_status_mask;
} open_cfw_pwrctrl_peripheral_descriptor;

_Static_assert(
    sizeof(open_cfw_pwrctrl_peripheral_descriptor) == 16U,
    "Apollo510 peripheral-power descriptor ABI must remain 16 bytes"
);

#define OPEN_CFW_PWRCTRL_PERIPHERAL_COUNT 34U
#define OPEN_CFW_PWRCTRL_STATUS_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_STATUS_INVALID_ARGUMENT 6U

/*
 * Source-owned form of the shipped am_hal_pwrctrl_peripheral_control table.
 * The record order is the public Apollo510 am_hal_pwrctrl_periph_e order:
 * IOS0, IOM0..7, UART0..3, ADC, MSPI0..3, GFX, DISP, DISPPHY, CRYPTO,
 * SDIO0..1, USB, USBPHY, DEBUG, OTP, IOSFD0..1, PDM0, I2S0..1, AUDADC.
 */
static const open_cfw_pwrctrl_peripheral_descriptor
open_cfw_pwrctrl_peripheral_descriptors[
    OPEN_CFW_PWRCTRL_PERIPHERAL_COUNT
] = {
    {0x40021004U, 0x00000001U, 0x40021008U, 0x30000001U},
    {0x40021004U, 0x10000000U, 0x40021008U, 0x30000001U},
    {0x40021004U, 0x20000000U, 0x40021008U, 0x30000001U},
    {0x40021004U, 0x00000002U, 0x40021008U, 0x0000001EU},
    {0x40021004U, 0x00000004U, 0x40021008U, 0x0000001EU},
    {0x40021004U, 0x00000008U, 0x40021008U, 0x0000001EU},
    {0x40021004U, 0x00000010U, 0x40021008U, 0x0000001EU},
    {0x40021004U, 0x00000020U, 0x40021008U, 0x000001E0U},
    {0x40021004U, 0x00000040U, 0x40021008U, 0x000001E0U},
    {0x40021004U, 0x00000080U, 0x40021008U, 0x000001E0U},
    {0x40021004U, 0x00000100U, 0x40021008U, 0x000001E0U},
    {0x40021004U, 0x00000200U, 0x40021008U, 0x00001E00U},
    {0x40021004U, 0x00000400U, 0x40021008U, 0x00001E00U},
    {0x40021004U, 0x00000800U, 0x40021008U, 0x00001E00U},
    {0x40021004U, 0x00001000U, 0x40021008U, 0x00001E00U},
    {0x40021004U, 0x00002000U, 0x40021008U, 0x00002000U},
    {0x40021004U, 0x00004000U, 0x40021008U, 0x00004000U},
    {0x40021004U, 0x00008000U, 0x40021008U, 0x00008000U},
    {0x40021004U, 0x00010000U, 0x40021008U, 0x00010000U},
    {0x40021004U, 0x00020000U, 0x40021008U, 0x00020000U},
    {0x40021004U, 0x00040000U, 0x40021008U, 0x00040000U},
    {0x40021004U, 0x00080000U, 0x40021008U, 0x00080000U},
    {0x40021004U, 0x00100000U, 0x40021008U, 0x00100000U},
    {0x40021004U, 0x00200000U, 0x40021008U, 0x00200000U},
    {0x40021004U, 0x00400000U, 0x40021008U, 0x00400000U},
    {0x40021004U, 0x00800000U, 0x40021008U, 0x00800000U},
    {0x40021004U, 0x01000000U, 0x40021008U, 0x01000000U},
    {0x40021004U, 0x02000000U, 0x40021008U, 0x02000000U},
    {0x40021004U, 0x04000000U, 0x40021008U, 0x04000000U},
    {0x40021004U, 0x08000000U, 0x40021008U, 0x08000000U},
    {0x4002100CU, 0x00000004U, 0x40021010U, 0x00000004U},
    {0x4002100CU, 0x00000040U, 0x40021010U, 0x000000C0U},
    {0x4002100CU, 0x00000080U, 0x40021010U, 0x000000C0U},
    {0x4002100CU, 0x00000400U, 0x40021010U, 0x00000400U},
};

/*
 * ABI-compatible source replacement for AmbiqSuite's private am_get_pwrctrl
 * helper at 0x0047EF18...0x0047EF37.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_peripheral_descriptor_get(
    open_cfw_pwrctrl_peripheral_descriptor *descriptor,
    unsigned int peripheral
)
{
    const open_cfw_pwrctrl_peripheral_descriptor *source;

    if (
        descriptor == (open_cfw_pwrctrl_peripheral_descriptor *)0
        || peripheral >= OPEN_CFW_PWRCTRL_PERIPHERAL_COUNT
    ) {
        return OPEN_CFW_PWRCTRL_STATUS_INVALID_ARGUMENT;
    }

    source = &open_cfw_pwrctrl_peripheral_descriptors[peripheral];
    descriptor->power_enable_register = source->power_enable_register;
    descriptor->peripheral_enable_mask = source->peripheral_enable_mask;
    descriptor->power_status_register = source->power_status_register;
    descriptor->peripheral_status_mask = source->peripheral_status_mask;

    return OPEN_CFW_PWRCTRL_STATUS_SUCCESS;
}

#undef OPEN_CFW_PWRCTRL_STATUS_INVALID_ARGUMENT
#undef OPEN_CFW_PWRCTRL_STATUS_SUCCESS
#undef OPEN_CFW_PWRCTRL_PERIPHERAL_COUNT
