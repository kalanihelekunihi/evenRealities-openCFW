/* SPDX-License-Identifier: MIT
 * Platform-finish NVIC entry binds to stock Thumb 0x430471.
 */
#include <stdint.h>

__attribute__((naked)) void opencfw_bl_context_nvic_enable(uint32_t interrupt)
{
    __asm__ volatile("b.w opencfw_boot_context_nvic_enable");
}
