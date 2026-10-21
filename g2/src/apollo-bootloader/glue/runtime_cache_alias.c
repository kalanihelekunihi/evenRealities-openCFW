/* SPDX-License-Identifier: MIT
 * Update-core runtime call is stock Thumb 0x41e349 cache maintenance.
 */
#include <stdint.h>

__attribute__((naked)) void opencfw_boot_runtime_call(uint32_t range, uint32_t operation)
{
    __asm__ volatile("b.w opencfw_boot_cache_maintain");
}
