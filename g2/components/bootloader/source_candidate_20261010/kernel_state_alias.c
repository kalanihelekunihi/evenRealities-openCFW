/* SPDX-License-Identifier: MIT
 * Stock 0x416088 kernel-state alias. Original pop {r1,pc} returns incoming
 * R7 in R1; the selected C provider supplies the R0 state result.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_bl_kernel_state(void)
{
    __asm__ volatile("push {r7, lr}\n"
                     "bl opencfw_boot_kernel_state\n"
                     "pop {r1, pc}");
}
