/* SPDX-License-Identifier: MIT
 * Native Touch 0x7e14..0x7e26. The historical name remains for oracle entry cuts;
 * this body now performs the actual stock reset-request register sequence.
 * It does not preserve AIRCR fields that the original unconditionally replaces.
 */
#include <stdint.h>
/* Stock 0x00007E14 (NVIC_SystemReset) */
__attribute__((noinline,noreturn)) void touch_reset_boundary(void)
{
    __asm__ volatile("dsb sy" ::: "memory");
    *(volatile uint32_t *)(uintptr_t)0xe000ed0cu=0x05fa0004u;
    __asm__ volatile("dsb sy" ::: "memory");
    for (;;) __asm__ volatile("nop" ::: "memory");
}
