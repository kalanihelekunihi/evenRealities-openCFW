/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 system-PLL state query adapted from AmbiqSuite SDK 5.1.0.
 * Reviewed stock and SDK evidence is recorded in EVIDENCE.md.
 */

typedef __UINTPTR_TYPE__ open_cfw_pwrctrl_syspll_enabled_uintptr;

#define OPEN_CFW_PWRCTRL_SYSPLL_ENABLED_PLLCTL0_ADDRESS 0x400204D8U
#define OPEN_CFW_PWRCTRL_SYSPLL_ENABLED_VDDF_POWER_DOWN_MASK 0x80000000U
#define OPEN_CFW_PWRCTRL_SYSPLL_ENABLED_STATUS_SUCCESS 0U

#ifndef OPEN_CFW_PWRCTRL_SYSPLL_ENABLED_READ32
#define OPEN_CFW_PWRCTRL_SYSPLL_ENABLED_READ32(address) \
    (*(const volatile unsigned int *)( \
        open_cfw_pwrctrl_syspll_enabled_uintptr)(address))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_pwrctrl_syspll_enabled at 0x004800E4...0x004800F3.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_syspll_enabled(_Bool *enabled)
{
    unsigned int pll_control;

    pll_control = OPEN_CFW_PWRCTRL_SYSPLL_ENABLED_READ32(
        OPEN_CFW_PWRCTRL_SYSPLL_ENABLED_PLLCTL0_ADDRESS
    );
    *enabled = (
        pll_control
        & OPEN_CFW_PWRCTRL_SYSPLL_ENABLED_VDDF_POWER_DOWN_MASK
    ) == 0U;

    return OPEN_CFW_PWRCTRL_SYSPLL_ENABLED_STATUS_SUCCESS;
}

#undef OPEN_CFW_PWRCTRL_SYSPLL_ENABLED_READ32
