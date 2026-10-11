/* SPDX-License-Identifier: MIT
 * Historical source-image alias of stock 0x41b8ec (8 bytes). The selected
 * authored assembly provider implements that exact PRIMASK save/disable ABI.
 */
#include <stdint.h>
extern uint32_t opencfw_boot_control_critical_save(void);

uint32_t opencfw_bl_critical_save(void)
{
    return opencfw_boot_control_critical_save();
}
