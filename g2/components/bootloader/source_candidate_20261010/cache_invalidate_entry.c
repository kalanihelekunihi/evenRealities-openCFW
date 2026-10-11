/* SPDX-License-Identifier: MIT
 * Clock-mux source calls stock Thumb 0x41e349 with (NULL, 1).
 * This entry preserves R0/R1 and the selected cache body's R0 result.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_cache_invalidate(
    const volatile void *range, uint32_t clean_too)
{
    __asm__ volatile("b.w opencfw_boot_cache_maintain");
}
