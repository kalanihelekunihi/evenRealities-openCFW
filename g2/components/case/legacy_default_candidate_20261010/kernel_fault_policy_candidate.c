/* SPDX-License-Identifier: MIT
 * Fixed stock invalid-state behavior at queue, mutex and critical-section
 * sites: mask interrupts, then branch forever. This reproduces the decoded
 * architectural fault policy; it is not a guessed success return.
 */
#include <stdint.h>

_Noreturn void case_kernel_invariant_failure(uint32_t condition)
{
    (void)condition;
    __asm__ volatile("cpsid i\n1: b 1b" ::: "memory");
    __builtin_unreachable();
}

_Noreturn void case_kernel_nesting_underflow(void)
{
    __asm__ volatile("cpsid i\n1: b 1b" ::: "memory");
    __builtin_unreachable();
}
