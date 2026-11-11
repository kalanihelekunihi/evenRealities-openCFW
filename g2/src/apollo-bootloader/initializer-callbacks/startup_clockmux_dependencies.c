/* SPDX-License-Identifier: MIT. Clockmux-specific source ABI adapters. */
#include <stdint.h>
#include "../clock-manager/clock_class_provider2.h"
/* Stock 0x41ca5c/0x41caa2: upstream SDK 5.0.0 am_hal_pwrctrl_syspll_enable/disable. */
extern uint32_t am_hal_pwrctrl_syspll_enable(void);
extern uint32_t am_hal_pwrctrl_syspll_disable(void);
uint64_t opencfw_legacy_gpio_mode(uint32_t mode,uint8_t *state)
{
    /* Clockmux reaches only selectors2/4; their original paths do not consume
     * incomingR2/R3. Other selector paths are outside this context proof. */
    return opencfw_bl_radio_mode_apply((uint8_t)mode,(const uint32_t *)(const void *)state,0u,0u);
}
uint64_t opencfw_low_power_prepare(void)
{
    (void)am_hal_pwrctrl_syspll_enable();
    return 0; /* Ignored by this caller; no standalone original return claim. */
}
uint64_t opencfw_low_power_finish(void)
{
    (void)am_hal_pwrctrl_syspll_disable();
    return 0; /* Ignored by this caller; no standalone original return claim. */
}
