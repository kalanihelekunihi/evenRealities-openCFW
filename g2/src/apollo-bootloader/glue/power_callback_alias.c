/* SPDX-License-Identifier: MIT
 * Power guard caller binds to stock Thumb 0x41cd1b.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_boot_power_control(uint32_t id,
    uint32_t enabled, uint32_t *value)
{
    __asm__ volatile("b.w opencfw_boot_power_callback");
}
