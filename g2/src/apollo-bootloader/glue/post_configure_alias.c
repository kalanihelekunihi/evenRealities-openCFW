/* SPDX-License-Identifier: MIT
 * Post-bringup caller's `opencfw_bl_post_configure` is the stock 0x422ba8
 * power-apply entry. The selected runtime.c guard and selected UART
 * configure continuation own the accepted object path. Stock 0x422ba8
 * saves incoming R3 and restores it into R1 at every return while R0
 * carries status.
 */
#include <stdint.h>

__attribute__((naked)) uint64_t opencfw_bl_post_configure(uint32_t *object,
                                                           uint32_t operation,
                                                           uint32_t enable)
{
    __asm__ volatile("push {r3, lr}\n"
                     "bl opencfw_boot_control_power_apply\n"
                     "pop {r1, pc}");
}
