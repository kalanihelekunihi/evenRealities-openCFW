/* SPDX-License-Identifier: MIT
 * Historical Thumb provider 0x41ac44, reviewed CPACR/barrier assembly body.
 * Branching retains its original input and return register behavior.
 */
#include <stdint.h>

__attribute__((naked)) void opencfw_provider_41ac44(void)
{
    __asm__ volatile("b.w opencfw_boot_coprocessor_enable");
}
