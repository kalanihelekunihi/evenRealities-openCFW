/* SPDX-License-Identifier: MIT
 * Platform-finish retry entry binds to stock Thumb 0x43048f.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_bl_config_retry(uint32_t index)
{
    __asm__ volatile("b.w opencfw_boot_context_retry");
}
