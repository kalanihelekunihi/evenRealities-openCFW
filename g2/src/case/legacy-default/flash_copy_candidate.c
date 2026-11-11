/* SPDX-License-Identifier: MIT
 * Stock 0x08003f38 RAM-to-flash copy body. The 64-word transfer, controller
 * status wait, and interrupt masking are source-owned; persistence is not.
 */
#include <stdint.h>
/* Stock 0x08003F38 (case_copy64_protected) */
void case_flash_copy_operation(uint32_t address,uint32_t source)
{
    volatile uint32_t *const control=(volatile uint32_t *)(uintptr_t)0x40022014u;
    volatile uint32_t *const status=(volatile uint32_t *)(uintptr_t)0x40022010u;
    volatile uint32_t *destination=(volatile uint32_t *)(uintptr_t)address;
    const uint32_t *input=(const uint32_t *)(uintptr_t)source;
    uint32_t primask;
    *control=*control|0x40000u;
    __asm__ volatile("mrs %0, primask" : "=r"(primask) :: "memory");
    __asm__ volatile("cpsid i" ::: "memory");
    for(uint32_t i=0;i<64u;++i) destination[i]=input[i];
    while((*status&0x30000u)!=0u){}
    __asm__ volatile("msr primask, %0" :: "r"(primask) : "memory");
}
