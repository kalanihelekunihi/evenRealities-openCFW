/* SPDX-License-Identifier: MIT
 * Manager message publisher binds to stock Thumb 0x42dca3.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_provider_42dca2(const void *message)
{
    __asm__ volatile("b.w opencfw_boot_dfu_send");
}
