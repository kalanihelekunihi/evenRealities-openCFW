/* SPDX-License-Identifier: MIT
 * Native CASE 0x080000cc first PSP task handoff. The stack frame ABI is
 * architectural and must be linked with the matching task-frame creator.
 */
#include <stdint.h>
/* Stock 0x080000CC (vPortStartFirstTask) */
__attribute__((naked,noreturn)) void case_boot_context_switch(void)
{
    __asm__ volatile(
        "ldr r3, =0x20000128\n"
        "ldr r1, [r3]\n"
        "ldr r0, [r1]\n"
        "adds r0, #32\n"
        "msr psp, r0\n"
        "movs r0, #2\n"
        "msr control, r0\n"
        "isb\n"
        "pop {r0, r1, r2, r3, r4, r5}\n"
        "mov lr, r5\n"
        "pop {r3}\n"
        "pop {r2}\n"
        "cpsie i\n"
        "bx r3\n");
}
