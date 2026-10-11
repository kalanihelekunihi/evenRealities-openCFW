/* SPDX-License-Identifier: MIT
 * Native CASE 0xa8d8 single-start service latch.
 */
#include <stdint.h>
int32_t case_boot_service_start(void)
{
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr":"=r"(ipsr));
    if(ipsr!=0u)return -6;
    volatile uint32_t *latch=(volatile uint32_t *)(uintptr_t)0x20000178u;
    if(*latch!=0u)return -1;
    *latch=1u;
    return 0;
}
