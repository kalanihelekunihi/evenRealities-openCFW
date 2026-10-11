/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800c2f8 task notification core.
 */
#include <stdint.h>
extern void case_policy_scheduler_lock(void);
extern uint32_t case_policy_scheduler_unlock(void);
extern void case_policy_task_unlink(uint32_t link);
extern void case_policy_task_list_insert(uint32_t list,uint32_t link);
extern void case_policy_task_wake_cleanup(void);
extern uint32_t case_policy_task_reschedule(void);
extern void case_policy_task_wake_dispatch(void); /* 0xc390 */
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
void case_policy_task_notify_core(uint32_t task)
{
    uint32_t scheduler=0x20000128u;
    case_policy_scheduler_lock();
    if(task==0u)task=rd(scheduler);
    case_policy_task_unlink(task+4u);
    if(rd(task+40u)!=0u)case_policy_task_unlink(task+24u);
    case_policy_task_list_insert(0x200014a4u,task+4u);
    volatile uint8_t *flag=(volatile uint8_t *)(uintptr_t)(task+0x58u);
    if(*flag==1u)*flag=0u;
    (void)case_policy_scheduler_unlock();
    if(rd(scheduler+20u)!=0u){
        case_policy_scheduler_lock();
        case_policy_task_wake_cleanup();
        (void)case_policy_scheduler_unlock();
    }
    if(task==rd(scheduler)){
        if(rd(scheduler+20u)!=0u){
            if(rd(scheduler+48u)!=0u)native_fault();
            (void)case_policy_task_reschedule();
        }else if(rd(0x200014a4u)==rd(scheduler+8u))wr(scheduler,0u);
        else case_policy_task_wake_dispatch();
    }
}
