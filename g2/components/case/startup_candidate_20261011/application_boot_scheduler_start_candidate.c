/* SPDX-License-Identifier: MIT
 * Native CASE scheduler start gate 0x0800a900.
 */
#include <stdint.h>
extern void case_boot_scheduler_activate(void); /* 0xc284 */
int32_t case_boot_scheduler_start(void)
{
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr":"=r"(ipsr));
    if(ipsr!=0u)return -6;
    volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)0x20000178u;
    if(*state!=1u)return -1;
    volatile uint32_t *priority=(volatile uint32_t *)(uintptr_t)0xe000ed1cu;
    *priority=*priority&0x00ffffffu;
    *state=2u;
    case_boot_scheduler_activate();
    return 0;
}
