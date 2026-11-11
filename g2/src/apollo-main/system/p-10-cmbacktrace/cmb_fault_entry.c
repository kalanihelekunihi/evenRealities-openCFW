/* SPDX-License-Identifier: MIT
 * CmBacktrace HardFault entry, adapted from Armink/CmBacktrace 73714489.
 * The naked C function passes the fault LR and active MSP to the library
 * before entering its terminal fault loop. A C frame would change the MSP
 * observed by cm_backtrace_fault, so these instructions remain explicit.
 */

__attribute__((naked, used, aligned(4), section(".text")))
void HardFault_Handler(void)
{
    __asm__ volatile (
        "mov r0, lr\n\t"
        "mov r1, sp\n\t"
        "bl cm_backtrace_fault\n\t"
        "1: bl 1b\n\t"
    );
}
