/* SPDX-License-Identifier: MIT
 * Native CASE 0x01d8 fill, 0xbfaa link reset, 0xb4c0 task frame,
 * and 0xb31c task-return fault policy.
 */
#include <stdint.h>
void case_boot_task_fill(uint32_t address,uint32_t count,uint8_t value)
{volatile uint8_t *p=(volatile uint8_t *)(uintptr_t)address;for(uint32_t i=0u;i<count;++i)p[i]=value;}
void case_boot_task_link_reset(uint32_t link)
{*(volatile uint32_t *)(uintptr_t)(link+16u)=0u;}
__attribute__((noreturn)) void case_boot_task_return(void)
{
    volatile uint32_t *depth=(volatile uint32_t *)(uintptr_t)0x2000019cu;
    /* Stock 0xb31c has distinct overflow and ordinary fatal PC loops.
     * Both disable interrupts; retain the branch for fault-site identity. */
    if((*depth+1u)==0u){
        __asm__ volatile("cpsid i\n1: b 1b" ::: "memory");
        __builtin_unreachable();
    }
    __asm__ volatile("cpsid i\n2: b 2b" ::: "memory");
    __builtin_unreachable();
}
uint32_t case_boot_task_frame(uint32_t top,void (*entry)(void *),void *arg)
{
    uint32_t *stack=(uint32_t *)(uintptr_t)top;
    *--stack=0x01000000u;
    *--stack=(uint32_t)(uintptr_t)entry;
    *--stack=(uint32_t)(uintptr_t)case_boot_task_return;
    stack-=5u;
    *stack=(uint32_t)(uintptr_t)arg;
    stack-=8u;
    return (uint32_t)(uintptr_t)stack;
}
