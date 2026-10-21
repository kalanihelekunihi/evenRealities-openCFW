/* SPDX-License-Identifier: MIT
 * Historical Thumb provider 0x41e266 for the selected startup caller.
 * Branching preserves the original one-argument callable ABI.
 */
#include <stdint.h>

__attribute__((naked)) void opencfw_provider_41e266(uint32_t clean_after)
{
    __asm__ volatile("b.w opencfw_boot_dcache_enable");
}
