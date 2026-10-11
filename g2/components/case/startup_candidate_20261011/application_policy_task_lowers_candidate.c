/* SPDX-License-Identifier: MIT
 * Native CASE scheduler descendants 0x0800c128 and 0x0800c228.
 */
#include <stdint.h>
extern void case_policy_task_sleep_enter(void); /* 0xc380 */
extern void case_policy_task_sleep_enqueue(uint32_t ticks,uint32_t mode); /* 0xabb0 */
extern uint32_t case_policy_task_sleep_exit(void); /* 0xcc0c */
extern uint32_t case_policy_task_reschedule(void); /* 0xc0a0 */
extern void case_policy_scheduler_lock(void); /* 0xbffc */
extern uint32_t case_policy_task_valid(uint32_t task); /* 0xb330 */
extern void case_policy_task_unlink(uint32_t link); /* 0xbf2c */
extern void case_policy_task_list_insert(uint32_t list,uint32_t link); /* 0xbfe2 */
extern uint32_t case_policy_scheduler_unlock(void); /* 0xc014 */

static __attribute__((noreturn)) void case_policy_native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
static uint32_t read32(uint32_t address)
{return *(volatile uint32_t *)(uintptr_t)address;}

uint32_t case_policy_task_sleep(uint32_t ticks)
{
    uint32_t result=0u;
    if(ticks!=0u){
        if(read32(0x20000158u)!=0u)case_policy_native_fault();
        case_policy_task_sleep_enter();
        case_policy_task_sleep_enqueue(ticks,0u);
        result=case_policy_task_sleep_exit();
    }
    if(result==0u)result=case_policy_task_reschedule();
    return result;
}

uint32_t case_policy_task_cancel_core(uint32_t task)
{
    if(task==0u)case_policy_native_fault();
    volatile uint32_t *scheduler=(volatile uint32_t *)(uintptr_t)0x20000128u;
    if(task==scheduler[0])return task;
    case_policy_scheduler_lock();
    if(case_policy_task_valid(task)!=0u){
        case_policy_task_unlink(task+4u);
        uint32_t priority=read32(task+0x2cu);
        if(priority>scheduler[4])scheduler[4]=priority;
        case_policy_task_list_insert(0x20000ff4u+priority*20u,task+4u);
        if(priority>=read32(scheduler[0]+0x2cu))case_policy_task_reschedule();
    }
    return case_policy_scheduler_unlock();
}
