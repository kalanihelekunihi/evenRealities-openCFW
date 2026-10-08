/* SPDX-License-Identifier: MIT
 * Source leaf for locked register getter at 0x41d90e.
 * The read is an indexed MMIO access; no GPIO configuration is involved.
 */
#include <stdint.h>

enum { POWER_REGISTER_BASE = 0x40010000u, POWER_REGISTER_COUNT = 0xe0u };

uint32_t opencfw_bl_power_register_read(uint32_t register_id,
                                        uint32_t *value_out)
{
    if (register_id >= POWER_REGISTER_COUNT)
        return 5u;
    if (value_out == 0)
        return 6u;

    *value_out = *(volatile uint32_t *)(uintptr_t)(POWER_REGISTER_BASE +
                                                   register_id * 4u);
    return 0u;
}
