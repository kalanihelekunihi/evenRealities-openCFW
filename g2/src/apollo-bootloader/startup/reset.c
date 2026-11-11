/* SPDX-License-Identifier: MIT
 * Bootloader reset and process-stack entries. MSPLIM and PSPLIM must be set
 * before any C frame exists, and the PSP seal is pushed on the live stack.
 * Both entry labels share one literal pool, so they stay in this naked C body.
 */
#include <stdint.h>

__attribute__((naked, used, section(".text")))
void opencfw_boot_reset_entry(void)
{
    __asm__ volatile (
        "ldr r0, =0x2007d000\n\t"
        "msr msplim, r0\n\t"
        "msr psplim, r0\n\t"
        "bl opencfw_boot_stack_entry\n\t"
        "bx lr\n\t"
        ".global opencfw_boot_stack_entry\n\t"
        ".type opencfw_boot_stack_entry, %function\n\t"
        ".thumb_func\n\t"
        "opencfw_boot_stack_entry:\n\t"
        "ldr r0, =0xfef5eda5\n\t"
        "mov r1, r0\n\t"
        "push {r0, r1}\n\t"
        "mov r0, sp\n\t"
        "msr psp, r0\n\t"
        "nop.w\n\t"
        "bl opencfw_boot_fpu_init\n\t"
        "bl opencfw_boot_system_entry\n\t"
        ".ltorg\n\t"
    );
}
