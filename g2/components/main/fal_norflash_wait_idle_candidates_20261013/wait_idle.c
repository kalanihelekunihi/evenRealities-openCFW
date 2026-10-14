/* SPDX-License-Identifier: MIT
 * Main 0x4703ba: fixed 500-tick wait wrapper for the MX25U controller.
 * The status polling implementation at 0x470368 remains a lower contract.
 */
#include <stdint.h>

extern uint32_t g2_norflash_wait_status_470368(uint32_t timeout_ticks);

uint32_t g2_norflash_wait_idle_4703ba(void)
{
    return g2_norflash_wait_status_470368(500u);
}
