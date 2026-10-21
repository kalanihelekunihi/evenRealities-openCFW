/* SPDX-License-Identifier: MIT
 * Main-init allocator entry binds to stock Thumb 0x41fd71.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_provider_41fd70(void)
{
    __asm__ volatile("b.w opencfw_boot_allocator_init");
}
