/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 buck/LDO dynamic override adaptation from AmbiqSuite
 * SDK 5.1.0. Reviewed stock and SDK evidence is recorded in EVIDENCE.md.
 */

typedef __UINTPTR_TYPE__ open_cfw_pwrctrl_buck_ldo_update_uintptr;

#define OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_VRCTRL 0x40020060U
#define OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_SIMOBUCK_OVER 0x00010000U
#define OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_CORE_OVER 0x00000001U
#define OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_MEM_OVER 0x00000020U

#ifndef OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_READ32
#define OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_READ32(address) \
    (*(const volatile unsigned int *)( \
        open_cfw_pwrctrl_buck_ldo_update_uintptr)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_WRITE32
#define OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_WRITE32(address, value) \
    (*(volatile unsigned int *)( \
        open_cfw_pwrctrl_buck_ldo_update_uintptr)(address) = (value))
#endif

static void
open_cfw_pwrctrl_buck_ldo_update_bit(
    unsigned int mask,
    unsigned int enabled
)
{
    unsigned int value = OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_READ32(
        OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_VRCTRL
    );

    value &= ~mask;
    if ((enabled & 1U) != 0U) {
        value |= mask;
    }
    OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_WRITE32(
        OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_VRCTRL,
        value
    );
}

/*
 * ABI-compatible source replacement for AmbiqSuite's private
 * buck_ldo_update_override at 0x0047FE6C...0x0047FE93.
 */
__attribute__((used, noinline))
void open_cfw_pwrctrl_buck_ldo_update_override(unsigned int enable)
{
    open_cfw_pwrctrl_buck_ldo_update_bit(
        OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_SIMOBUCK_OVER,
        enable
    );
    open_cfw_pwrctrl_buck_ldo_update_bit(
        OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_CORE_OVER,
        enable
    );
    open_cfw_pwrctrl_buck_ldo_update_bit(
        OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_MEM_OVER,
        enable
    );
}

#undef OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_WRITE32
#undef OPEN_CFW_PWRCTRL_BUCK_LDO_UPDATE_READ32
