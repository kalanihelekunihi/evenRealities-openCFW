/* SPDX-License-Identifier: MIT
 * Post-bringup caller's `opencfw_bl_post_configure` is the stock 0x422ba8
 * power-apply entry. The selected runtime.c guard and selected UART
 * configure continuation own the accepted object path. A Thumb branch
 * preserves all three argument registers and the returned status.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_bl_post_configure(uint32_t *object,
                                                           uint32_t operation,
                                                           uint32_t enable)
{
    __asm__ volatile("b.w opencfw_boot_control_power_apply");
}
