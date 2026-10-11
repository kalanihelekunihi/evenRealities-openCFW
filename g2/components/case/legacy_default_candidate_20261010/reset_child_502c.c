/* SPDX-License-Identifier: MIT
 * Source-owned stock 0x0800502c reset request. Physical reset is not tested.
 */
#include <stdint.h>
__attribute__((noreturn)) uint32_t case_legacy_reset_first(uint32_t prior)
{
    (void)prior;
    __asm__ volatile("dsb sy" ::: "memory");
    *(volatile uint32_t *)(uintptr_t)0xe000ed0cu=0x05fa0004u;
    __asm__ volatile("dsb sy" ::: "memory");
    for(;;)__asm__ volatile("nop" ::: "memory");
}
