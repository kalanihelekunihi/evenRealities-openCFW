/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 peripheral-disable domain-mask helper adaptation from
 * AmbiqSuite SDK 5.1.0. Reviewed evidence is recorded in EVIDENCE.md.
 */

typedef struct open_cfw_pwrctrl_disable_mask_descriptor {
    unsigned int power_enable_register;
    unsigned int peripheral_enable_mask;
    unsigned int power_status_register;
    unsigned int peripheral_status_mask;
} open_cfw_pwrctrl_disable_mask_descriptor;

#define OPEN_CFW_PWRCTRL_DISABLE_MASK_HCPA_STATUS 0x30000001U
#define OPEN_CFW_PWRCTRL_DISABLE_MASK_HCPB_STATUS 0x0000001EU
#define OPEN_CFW_PWRCTRL_DISABLE_MASK_HCPC_STATUS 0x000001E0U
#define OPEN_CFW_PWRCTRL_DISABLE_MASK_I2S_STATUS 0x000000C0U
#define OPEN_CFW_PWRCTRL_DISABLE_MASK_IOS_STATUS 0x00001E00U

#ifndef OPEN_CFW_PWRCTRL_DISABLE_MASK_READ
#define OPEN_CFW_PWRCTRL_DISABLE_MASK_READ(address) \
    (*(const volatile unsigned int *)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_DISABLE_MASK_DESCRIPTOR_GET
unsigned int open_cfw_pwrctrl_disable_mask_descriptor_get_target(
    void *,
    unsigned int
) __asm__("open_cfw_pwrctrl_peripheral_descriptor_get");
#define OPEN_CFW_PWRCTRL_DISABLE_MASK_DESCRIPTOR_GET( \
    descriptor, peripheral \
) \
    open_cfw_pwrctrl_disable_mask_descriptor_get_target( \
        (descriptor), (peripheral) \
    )
#endif

__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_periph_disable_mask_check(
    unsigned int peripheral
)
{
    open_cfw_pwrctrl_disable_mask_descriptor descriptor;
    unsigned int group_mask;

    if (
        OPEN_CFW_PWRCTRL_DISABLE_MASK_DESCRIPTOR_GET(
            &descriptor,
            peripheral & 0xFFU
        ) != 0U
    ) {
        return 1U;
    }

    switch (descriptor.peripheral_status_mask) {
        case OPEN_CFW_PWRCTRL_DISABLE_MASK_HCPA_STATUS:
            group_mask = OPEN_CFW_PWRCTRL_DISABLE_MASK_HCPA_STATUS;
            break;
        case OPEN_CFW_PWRCTRL_DISABLE_MASK_HCPB_STATUS:
            group_mask = OPEN_CFW_PWRCTRL_DISABLE_MASK_HCPB_STATUS;
            break;
        case OPEN_CFW_PWRCTRL_DISABLE_MASK_HCPC_STATUS:
            group_mask = OPEN_CFW_PWRCTRL_DISABLE_MASK_HCPC_STATUS;
            break;
        case OPEN_CFW_PWRCTRL_DISABLE_MASK_I2S_STATUS:
            group_mask = OPEN_CFW_PWRCTRL_DISABLE_MASK_I2S_STATUS;
            break;
        case OPEN_CFW_PWRCTRL_DISABLE_MASK_IOS_STATUS:
            group_mask = OPEN_CFW_PWRCTRL_DISABLE_MASK_IOS_STATUS;
            break;
        default:
            return 1U;
    }

    if (
        (
            OPEN_CFW_PWRCTRL_DISABLE_MASK_READ(
                descriptor.power_enable_register
            ) & group_mask
        ) != 0U
        && (
            OPEN_CFW_PWRCTRL_DISABLE_MASK_READ(
                descriptor.power_enable_register
            ) & descriptor.peripheral_enable_mask
        ) == 0U
    ) {
        return 0U;
    }

    return 1U;
}
