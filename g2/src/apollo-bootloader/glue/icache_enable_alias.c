/* SPDX-License-Identifier: MIT
 * Historical Thumb provider 0x41e1e8 for the selected startup caller.
 * Branching preserves its no-argument callable ABI.
 */
#include <stdint.h>

__attribute__((naked)) void opencfw_provider_41e1e8(void)
{
    __asm__ volatile("b.w opencfw_boot_icache_enable");
}
