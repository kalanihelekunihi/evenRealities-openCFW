/* SPDX-License-Identifier: MIT
 * Historical stock entry 0x4160b0. Selected startup caller uses void(void);
 * branch directly to the reviewed C lifecycle provider.
 */
#include <stdint.h>

__attribute__((naked)) void opencfw_provider_4160b0(void)
{
    __asm__ volatile("b.w opencfw_boot_kernel_start");
}
