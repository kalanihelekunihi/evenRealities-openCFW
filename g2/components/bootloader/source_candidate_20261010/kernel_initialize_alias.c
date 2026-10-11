/* SPDX-License-Identifier: MIT
 * Historical stock entry 0x416058. Selected caller declares void(void),
 * while original status remains in R0 and incoming R7 returns in R1.
 */
#include <stdint.h>

__attribute__((naked)) void opencfw_provider_416058(void)
{
    __asm__ volatile("push {r7, lr}\n"
                     "bl opencfw_boot_kernel_initialize\n"
                     "pop {r1, pc}");
}
