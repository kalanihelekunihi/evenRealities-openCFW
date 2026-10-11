/* SPDX-License-Identifier: MIT
 * Platform-finish interrupt-enable entry binds to stock Thumb 0x42c63b.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_bl_context_interrupt_enable(
    uint32_t handle, uint32_t mask)
{
    __asm__ volatile("b.w opencfw_boot_context_interrupt_enable");
}
