/* SPDX-License-Identifier: MIT. Clockmux-specific source ABI adapters. */
#include <stdint.h>
#include "../clock_manager/clock_class_provider2.h"
#include "../clock_manager/clock_class_provider6.h"
uint64_t opencfw_legacy_gpio_mode(uint32_t mode,uint8_t *state)
{
    /* Clockmux reaches only selectors2/4; their original paths do not consume
     * incomingR2/R3. Other selector paths are outside this context proof. */
    return opencfw_bl_radio_mode_apply((uint8_t)mode,(const uint32_t *)(const void *)state,0u,0u);
}
uint64_t opencfw_low_power_prepare(void)
{
    opencfw_boot_syspll_power_initialize_for_clockmux();
    return 0; /* Ignored by this caller; no standalone original return claim. */
}
uint64_t opencfw_low_power_finish(void)
{
    opencfw_boot_syspll_power_restore_for_clockmux();
    return 0; /* Ignored by this caller; no standalone original return claim. */
}
