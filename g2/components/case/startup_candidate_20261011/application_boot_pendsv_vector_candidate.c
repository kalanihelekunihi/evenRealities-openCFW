/* SPDX-License-Identifier: MIT
 * CASE 0x08000102 PendSV architectural context switch. Native PSP, callee
 * register save/restore, PRIMASK window, and EXC_RETURN are preserved.
 */
#include <stdint.h>
extern void case_policy_task_wake_dispatch(void); /* 0xc390 */
__attribute__((naked)) void case_vector_pendsv_0102(void)
{
    __asm__ volatile(
        "mrs r0, psp\n"
        "ldr r3, =0x20000128\n"
        "ldr r2, [r3]\n"
        "subs r0, #32\n"
        "str r0, [r2]\n"
        "stmia r0!, {r4-r7}\n"
        "mov r4, r8\n"
        "mov r5, r9\n"
        "mov r6, r10\n"
        "mov r7, r11\n"
        "stmia r0!, {r4-r7}\n"
        "push {r3, lr}\n"
        "cpsid i\n"
        "bl case_policy_task_wake_dispatch\n"
        "cpsie i\n"
        "pop {r2, r3}\n"
        "ldr r1, [r2]\n"
        "ldr r0, [r1]\n"
        "adds r0, #16\n"
        "ldmia r0!, {r4-r7}\n"
        "mov r8, r4\n"
        "mov r9, r5\n"
        "mov r10, r6\n"
        "mov r11, r7\n"
        "msr psp, r0\n"
        "subs r0, #32\n"
        "ldmia r0!, {r4-r7}\n"
        "bx r3\n");
}
