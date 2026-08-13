/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 system-PLL disable adaptation from AmbiqSuite SDK 5.1.0.
 * Reviewed stock and SDK evidence is recorded in EVIDENCE.md.
 */

typedef __UINTPTR_TYPE__ open_cfw_pwrctrl_syspll_disable_uintptr;

#define OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_CHIP_REVISION_ADDRESS 0x4002000CU
#define OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_D2ASPARE_ADDRESS 0x400201B0U
#define OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_PLLCTL0_ADDRESS 0x400204D8U

#define OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_REVISION_MASK 0x000000FFU
#define OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_REVISION_B1 0x00000022U
#define OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_ISOLATION_MASK 0x00200000U
#define OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_VDDF_POWER_DOWN_MASK 0x80000000U
#define OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_VDDH_POWER_DOWN_MASK 0x40000000U
#define OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_STATUS_SUCCESS 0U

#define OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_IRQ_DISABLE_ENTRY 0x00473941U
#define OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_DELAY_US_ENTRY 0x004807A1U

#ifndef OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_READ32
#define OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_READ32(address) \
    (*(const volatile unsigned int *)( \
        open_cfw_pwrctrl_syspll_disable_uintptr)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_WRITE32
#define OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_WRITE32(address, value) \
    (*(volatile unsigned int *)( \
        open_cfw_pwrctrl_syspll_disable_uintptr)(address) = (value))
#endif

#ifndef OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_IRQ_DISABLE
typedef unsigned int (
    *open_cfw_pwrctrl_syspll_disable_irq_disable_function
)(void);
#define OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_IRQ_DISABLE() \
    (((open_cfw_pwrctrl_syspll_disable_irq_disable_function) \
        OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_IRQ_DISABLE_ENTRY)())
#endif

#ifndef OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_IRQ_RESTORE
static __attribute__((always_inline)) inline void
open_cfw_pwrctrl_syspll_disable_irq_restore_target(unsigned int primask)
{
    __asm__ volatile (
        "msr primask, %0"
        :
        : "r" (primask)
        : "memory"
    );
}
#define OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_IRQ_RESTORE(primask) \
    open_cfw_pwrctrl_syspll_disable_irq_restore_target(primask)
#endif

#ifndef OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_DELAY_US
typedef void (
    *open_cfw_pwrctrl_syspll_disable_delay_us_function
)(unsigned int);
#define OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_DELAY_US(microseconds) \
    (((open_cfw_pwrctrl_syspll_disable_delay_us_function) \
        OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_DELAY_US_ENTRY)((microseconds)))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_pwrctrl_syspll_disable at 0x0048009E...0x004800DD.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_syspll_disable(void)
{
    unsigned int primask;
    unsigned int revision;
    unsigned int value;

    primask = OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_IRQ_DISABLE();

    value = OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_READ32(
        OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_PLLCTL0_ADDRESS
    );
    OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_WRITE32(
        OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_PLLCTL0_ADDRESS,
        value | OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_VDDF_POWER_DOWN_MASK
    );

    value = OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_READ32(
        OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_PLLCTL0_ADDRESS
    );
    OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_WRITE32(
        OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_PLLCTL0_ADDRESS,
        value | OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_VDDH_POWER_DOWN_MASK
    );

    revision = OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_READ32(
        OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_CHIP_REVISION_ADDRESS
    ) & OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_REVISION_MASK;

    if (revision >= OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_REVISION_B1) {
        OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_DELAY_US(1U);
        value = OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_READ32(
            OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_D2ASPARE_ADDRESS
        );
        OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_WRITE32(
            OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_D2ASPARE_ADDRESS,
            value | OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_ISOLATION_MASK
        );
    }

    OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_IRQ_RESTORE(primask);
    return OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_STATUS_SUCCESS;
}

#undef OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_DELAY_US
#undef OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_IRQ_RESTORE
#undef OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_IRQ_DISABLE
#undef OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_WRITE32
#undef OPEN_CFW_PWRCTRL_SYSPLL_DISABLE_READ32
