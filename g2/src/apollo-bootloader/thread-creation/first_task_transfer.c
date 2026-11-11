/* SPDX-License-Identifier: MIT
 * Stock first-task transfer at 0x41b2e0. MSP is reloaded from the active
 * vector table before SVC enters the first task, so this naked C entry must
 * not use a C frame or attempt to return through its original stack.
 */
#include <stdint.h>

__attribute__((naked, used, section(".text")))
void opencfw_boot_first_task_transfer(void)
{
    __asm__ volatile (
        "ldr r0, =0xe000ed08\n\t"
        "ldr r0, [r0]\n\t"
        "ldr r0, [r0]\n\t"
        "msr msp, r0\n\t"
        "cpsie i\n\t"
        "cpsie f\n\t"
        "dsb sy\n\t"
        "isb sy\n\t"
        "svc #2\n\t"
        "b opencfw_bl_mask_interrupts\n\t"
    );
}
