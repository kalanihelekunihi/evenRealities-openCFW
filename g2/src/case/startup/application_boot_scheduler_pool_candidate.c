/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800c5d0 scheduler pool-create wrapper.
 */
#include <stdint.h>
extern void case_boot_pool_initialize(uint32_t count,uint32_t stride,
                                      uint32_t storage,uint32_t flags,
                                      uint32_t region); /* 0xae74 */
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
/* Stock 0x0800C5D0 (case_boot_scheduler_pool) */
uint32_t case_boot_scheduler_pool(uint32_t count,uint32_t stride,uint32_t storage,
                                  uint32_t region,uint32_t flags)
{
    if(count==0u || region==0u || ((storage==0u)!=(stride==0u)))native_fault();
    *(volatile uint8_t *)(uintptr_t)(region+0x46u)=1u;
    case_boot_pool_initialize(count,stride,storage,flags,region);
    return region;
}
