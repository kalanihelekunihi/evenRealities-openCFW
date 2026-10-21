/* SPDX-License-Identifier: MIT
 * DFU flag APIs bind to stock Thumb 0x41623b and 0x4162c5.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_boot_dfu_flags_set(uint32_t thread,
    uint32_t flags)
{
    __asm__ volatile("b.w opencfw_provider_41623a");
}

__attribute__((naked)) uint64_t opencfw_boot_dfu_flags_wait(uint32_t mask,
    uint32_t options, uint32_t timeout, uint32_t opaque)
{
    __asm__ volatile("b.w opencfw_provider_4162c4");
}
