/* SPDX-License-Identifier: MIT
 * Native CASE 0xbb74 refresh, 0xab26 task reset and 0xcde4 task check.
 */
#include <stdint.h>
extern void case_policy_scheduler_lock(void);
extern uint32_t case_policy_scheduler_unlock(void);
extern uint32_t case_policy_task_event_send(uint32_t task,uint32_t op,uint32_t value,uint32_t option,uint32_t timeout); /* 0xcd80 */
extern int32_t case_policy_event_signal(uint32_t task,uint32_t value); /* 0xaaf0 */
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
uint32_t case_policy_task_active(uint32_t task) /* 0xcde4 */
{
    if(task==0u)native_fault();
    case_policy_scheduler_lock();
    uint32_t result=*(volatile uint8_t *)(uintptr_t)(task+40u)&1u;
    (void)case_policy_scheduler_unlock();
    return result;
}
int32_t case_policy_task_reset(uint32_t task) /* 0xab26 */
{
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr":"=r"(ipsr));
    if(ipsr!=0u)return -6;
    if(task==0u)return -4;
    if(case_policy_task_active(task)==0u)return -3;
    return case_policy_task_event_send(task,3u,0u,0u,0u)==1u?0:-1;
}
void case_policy_refresh(void) /* 0xbb74 */
{
    uint32_t task=*(volatile uint32_t *)(uintptr_t)0x200000ccu;
    (void)case_policy_task_reset(task);
    (void)case_policy_event_signal(task,1000u);
}
