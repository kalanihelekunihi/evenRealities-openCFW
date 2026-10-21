/* SPDX-License-Identifier: MIT
 * Filesystem NOR calls bind to stock program/erase entries.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_boot_nor_prog(uint32_t address,
    const void *source, uint32_t length)
{
    __asm__ volatile("b.w opencfw_provider_420b0c");
}

__attribute__((naked)) uint32_t opencfw_boot_nor_erase(uint32_t address)
{
    __asm__ volatile("b.w opencfw_provider_420a08");
}
