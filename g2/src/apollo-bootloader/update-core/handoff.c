/* SPDX-License-Identifier: MIT
 * Stock vector handoff at 0x42dc90. The naked C entry retains the exact
 * architectural transition: set VTOR, load MSP, and branch to the next
 * image's reset vector. No C stack frame may be used after loading MSP.
 */
#include <stdint.h>

__attribute__((naked, used, section(".text.opencfw_boot_vector_handoff")))
void opencfw_boot_vector_handoff(uintptr_t vector_base)
{
    __asm__ volatile (
        "movw r1, #0xed08\n\t"
        "movt r1, #0xe000\n\t"
        "str r0, [r1]\n\t"
        "ldr sp, [r0]\n\t"
        "ldr r1, [r0, #4]\n\t"
        "bx r1\n\t"
    );
}
