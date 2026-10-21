/* SPDX-License-Identifier: MIT
 * Platform-finish context enable binds to stock Thumb 0x42c539.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_bl_context_enable(uint32_t handle)
{
    __asm__ volatile("b.w opencfw_boot_context_enable");
}
