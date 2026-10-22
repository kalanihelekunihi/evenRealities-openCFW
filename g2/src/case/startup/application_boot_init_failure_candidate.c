/* SPDX-License-Identifier: MIT
 * Native CASE 0x3e90 failure policy: disable interrupts and hold.
 */
#include <stdint.h>
/* Stock 0x08003E90 (case_fail_stop) */
__attribute__((noreturn)) void case_boot_init_failure(void)
{
    __asm__ volatile("cpsid i\n1: b 1b" ::: "memory");
    __builtin_unreachable();
}
