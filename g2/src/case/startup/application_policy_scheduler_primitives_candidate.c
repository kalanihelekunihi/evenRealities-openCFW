/* SPDX-License-Identifier: MIT
 * Native CASE 0xbffc, 0xc014, 0xc0a0, 0xc380 scheduler primitives.
 */
#include <stdint.h>
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
void case_policy_scheduler_lock(void)
{
    volatile uint32_t *depth=(volatile uint32_t *)(uintptr_t)0x2000019cu;
    __asm__ volatile("cpsid i" ::: "memory");
    *depth=*depth+1u;
    __asm__ volatile("dsb\nisb" ::: "memory");
}
/* Stock 0x0800C014 (case_policy_scheduler_unlock) */
uint32_t case_policy_scheduler_unlock(void)
{
    volatile uint32_t *depth=(volatile uint32_t *)(uintptr_t)0x2000019cu;
    if(*depth==0u)native_fault();
    uint32_t next=*depth-1u;
    *depth=next;
    if(next==0u)__asm__ volatile("cpsie i" ::: "memory");
    return next;
}
uint32_t case_policy_task_reschedule(void)
{
    *(volatile uint32_t *)(uintptr_t)0xe000ed04u=0x10000000u;
    __asm__ volatile("dsb\nisb" ::: "memory");
    return 0x10000000u;
}
void case_policy_task_sleep_enter(void)
{
    volatile uint32_t *depth=(volatile uint32_t *)(uintptr_t)0x20000158u;
    *depth=*depth+1u;
}
