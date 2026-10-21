/* SPDX-License-Identifier: MIT
 * Historical stock Thumb entry 0x41d1c1. The selected platform-control
 * callers use void(uint32_t); preserve R0 and branch to the reviewed body.
 */
#include <stdint.h>

__attribute__((naked)) void opencfw_boot_control_delay_us(uint32_t microseconds)
{
    __asm__ volatile("b.w opencfw_boot_delay_us_math");
}
