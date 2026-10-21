/* SPDX-License-Identifier: MIT */
#include "gpio_config.h"
/* Original data at0x78ee48; decoded from the authenticated Apollo artifact.
 * Volatile raw cfg member retains an actual load, including in diagnostics.
 */
const volatile am_hal_gpio_pincfg_t opencfw_radio_pin138_idle_config={.GP={.cfg=3u}};
/* Reconstructed from0x52dd7c; stock ignores both statuses and returns void. */
void opencfw_radio_gpio_idle_pins(void)
{
    (void)am_hal_gpio_state_write(93u, AM_HAL_GPIO_OUTPUT_CLEAR);
    am_hal_gpio_pincfg_t config;
    config.GP.cfg=opencfw_radio_pin138_idle_config.GP.cfg;
    (void)am_hal_gpio_pinconfig(138u, config);
}
