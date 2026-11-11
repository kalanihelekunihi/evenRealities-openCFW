/* SPDX-License-Identifier: MIT
 * Cortex-M55 SVC and PendSV architectural entry. The naked C body keeps
 * stack selection, PSP/PSPLIM/CONTROL, FP context and EXC_RETURN operations
 * in explicit Thumb instructions before any ordinary C function is called.
 * The three entry labels share the stock literal pool and source ordering.
 */
#include <stdint.h>

__attribute__((naked, used, section(".text")))
void opencfw_boot_svc_entry(void)
{
    __asm__ volatile (
        "tst lr, #4\n\t"
        "ite eq\n\t"
        "mrseq r0, msp\n\t"
        "mrsne r0, psp\n\t"
        "b opencfw_boot_svc_dispatch\n\t"
        ".global opencfw_boot_first_task_restore\n\t"
        ".type opencfw_boot_first_task_restore, %function\n\t"
        ".thumb_func\n\t"
        "opencfw_boot_first_task_restore:\n\t"
        "ldr r2, =0x20027134\n\t"
        "ldr r1, [r2]\n\t"
        "ldr r0, [r1]\n\t"
        "ldm r0!, {r1, r2}\n\t"
        "msr psplim, r1\n\t"
        "movs r1, #2\n\t"
        "msr control, r1\n\t"
        "adds r0, #32\n\t"
        "msr psp, r0\n\t"
        "isb sy\n\t"
        "mov r0, #0\n\t"
        "msr basepri, r0\n\t"
        "bx r2\n\t"
        ".global opencfw_boot_pendsv_entry\n\t"
        ".type opencfw_boot_pendsv_entry, %function\n\t"
        ".thumb_func\n\t"
        "opencfw_boot_pendsv_entry:\n\t"
        "mrs r0, psp\n\t"
        "tst lr, #16\n\t"
        "it eq\n\t"
        "vstmdbeq r0!, {s16-s31}\n\t"
        "mrs r2, psplim\n\t"
        "mov r3, lr\n\t"
        "stmdb r0!, {r2-r11}\n\t"
        "ldr r2, =0x20027134\n\t"
        "ldr r1, [r2]\n\t"
        "str r0, [r1]\n\t"
        "mov r0, #48\n\t"
        "msr basepri, r0\n\t"
        "dsb sy\n\t"
        "isb sy\n\t"
        "bl opencfw_boot_thread_select\n\t"
        "mov r0, #0\n\t"
        "msr basepri, r0\n\t"
        "ldr r2, =0x20027134\n\t"
        "ldr r1, [r2]\n\t"
        "ldr r0, [r1]\n\t"
        "ldm r0!, {r2-r11}\n\t"
        "tst r3, #16\n\t"
        "it eq\n\t"
        "vldmiaeq r0!, {s16-s31}\n\t"
        "msr psplim, r2\n\t"
        "msr psp, r0\n\t"
        "bx r3\n\t"
        ".ltorg\n\t"
    );
}
