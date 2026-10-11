/* SPDX-License-Identifier: MIT
 * Platform-finish instance configuration binds to stock Thumb 0x42cc35.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_bl_instance_configure(uint32_t handle,
    uint32_t configuration)
{
    __asm__ volatile("b.w opencfw_boot_context_configure");
}
