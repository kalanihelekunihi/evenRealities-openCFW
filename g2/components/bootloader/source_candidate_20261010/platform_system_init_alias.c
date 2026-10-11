/* SPDX-License-Identifier: MIT
 * Startup system-entry platform init binds to stock Thumb 0x41b863.
 */
#include <stdint.h>

__attribute__((naked)) void opencfw_boot_platform_system_init(uint32_t argument)
{
    __asm__ volatile("b.w opencfw_boot_main_init");
}
