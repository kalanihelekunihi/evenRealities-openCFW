/* SPDX-License-Identifier: MIT
 * Platform-finish context claim binds to stock Thumb 0x42c4c7.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_bl_context_claim(uint32_t module,
    uint32_t *output)
{
    __asm__ volatile("b.w opencfw_boot_context_claim");
}
