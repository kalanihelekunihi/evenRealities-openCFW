/* SPDX-License-Identifier: MIT
 * Historical Thumb provider 0x41ac5a. The reviewed native assembly retains
 * PRIMASK and the unusual incoming-register return convention.
 */
#include <stdint.h>

__attribute__((naked)) void opencfw_provider_41ac5a(uint32_t mode)
{
    __asm__ volatile("b.w opencfw_boot_fp_lazy_mode");
}
