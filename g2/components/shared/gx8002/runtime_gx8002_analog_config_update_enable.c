/* SPDX-License-Identifier: MIT */
/* Recovered GX8002 analog config-update-enable leaf.
 * Decoded from the authenticated gx_analog_config_update_enable SDK/firmware
 * match (NationalChip lvp_kws drivers_lib/misc/grus/misc.o, declared in
 * include/driver/misc.h: "enable the analog parameter update function;
 * call before configuring analog parameters"). It writes the documented
 * magic strobe value 89 to each of the four PMU analog trim registers at
 * 0xa0005040..0xa000504c, in ascending offset order.
 */
#include <stdint.h>

void open_cfw_gx8002_analog_config_update_enable(void)
{
    volatile uint32_t *base = (volatile uint32_t *)0xa0005000U;
    base[0x40 / 4] = 89U;
    base[0x44 / 4] = 89U;
    base[0x48 / 4] = 89U;
    base[0x4c / 4] = 89U;
}
