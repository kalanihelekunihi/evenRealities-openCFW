/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 peripheral-power enabled-state query adaptation from
 * AmbiqSuite SDK 5.1.0. Reviewed evidence is recorded in EVIDENCE.md.
 */

typedef struct open_cfw_pwrctrl_enabled_descriptor {
    unsigned int power_enable_register;
    unsigned int peripheral_enable_mask;
    unsigned int power_status_register;
    unsigned int peripheral_status_mask;
} open_cfw_pwrctrl_enabled_descriptor;

_Static_assert(
    sizeof(open_cfw_pwrctrl_enabled_descriptor) == 16U,
    "Apollo510 peripheral-power descriptor ABI must remain 16 bytes"
);

#define OPEN_CFW_PWRCTRL_ENABLED_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_ENABLED_INVALID_ARGUMENT 6U

#ifndef OPEN_CFW_PWRCTRL_ENABLED_READ
#define OPEN_CFW_PWRCTRL_ENABLED_READ(address) \
    (*(const volatile unsigned int *)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_ENABLED_DESCRIPTOR_GET
unsigned int open_cfw_pwrctrl_enabled_descriptor_get_target(
    void *,
    unsigned int
) __asm__("open_cfw_pwrctrl_peripheral_descriptor_get");
#define OPEN_CFW_PWRCTRL_ENABLED_DESCRIPTOR_GET(descriptor, peripheral) \
    open_cfw_pwrctrl_enabled_descriptor_get_target( \
        (descriptor), (peripheral) \
    )
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_pwrctrl_periph_enabled at 0x0047F90C...0x0047F941.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_periph_enabled(
    unsigned int peripheral,
    unsigned char *enabled
)
{
    open_cfw_pwrctrl_enabled_descriptor descriptor;
    unsigned int result;

    if (enabled == (unsigned char *)0) {
        return OPEN_CFW_PWRCTRL_ENABLED_INVALID_ARGUMENT;
    }

    *enabled = 0U;
    result = OPEN_CFW_PWRCTRL_ENABLED_DESCRIPTOR_GET(
        &descriptor,
        peripheral & 0xFFU
    );
    if (result == OPEN_CFW_PWRCTRL_ENABLED_SUCCESS) {
        *enabled = (
            OPEN_CFW_PWRCTRL_ENABLED_READ(
                descriptor.power_status_register
            ) & descriptor.peripheral_status_mask
        ) != 0U;
    }

    return result;
}
