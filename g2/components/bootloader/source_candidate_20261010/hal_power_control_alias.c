/* SPDX-License-Identifier: MIT
 * NOR/HAL three-word power operation binds to stock Thumb 0x426809.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_hal_power_control(uint32_t handle,
    uint32_t operation, uint32_t retain)
{
    __asm__ volatile("b.w opencfw_bl_power_control");
}
