/* SPDX-License-Identifier: MIT
 * Startup's void(uint32_t) entry binds to stock Thumb 0x41f847.
 */
#include <stdint.h>

__attribute__((naked)) void opencfw_provider_41f846(uint32_t selector)
{
    __asm__ volatile("b.w opencfw_boot_platform_configure");
}
