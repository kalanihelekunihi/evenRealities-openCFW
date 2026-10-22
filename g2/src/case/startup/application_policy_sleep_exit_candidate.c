/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800cc0c scheduler sleep-exit and wake processing.
 */
#include <stdint.h>
extern void case_policy_scheduler_lock(void);
extern uint32_t case_policy_scheduler_unlock(void);
extern void case_policy_task_unlink(uint32_t link);
extern void case_policy_task_list_insert(uint32_t list,uint32_t link);
extern uint32_t case_policy_task_reschedule(void);
extern void case_policy_task_wake_cleanup(void); /* 0xb260 */
extern uint32_t case_policy_task_pended(void); /* 0xca78 */
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
/* Stock 0x0800CC0C (case_policy_task_sleep_exit) */
uint32_t case_policy_task_sleep_exit(void)
{
    uint32_t scheduler=0x20000128u;
    if(rd(scheduler+0x30u)==0u)native_fault();
    case_policy_scheduler_lock();
    wr(scheduler+0x30u,rd(scheduler+0x30u)-1u);
    uint32_t switched=0u,last_task=0u;
    if(rd(scheduler+0x30u)==0u && rd(scheduler+8u)!=0u){
        uint32_t waiting=0x2000147cu;
        while(rd(waiting)!=0u){
            last_task=rd(rd(waiting+12u)+12u);
            case_policy_task_unlink(last_task+24u);
            case_policy_task_unlink(last_task+4u);
            uint32_t priority=rd(last_task+44u);
            if(priority>rd(scheduler+16u))wr(scheduler+16u,priority);
            case_policy_task_list_insert(0x20000ff4u+priority*20u,last_task+4u);
            if(priority>=rd(rd(scheduler)+44u))wr(scheduler+28u,1u);
        }
        if(last_task!=0u)case_policy_task_wake_cleanup();
        uint32_t count=rd(scheduler+24u);
        for(uint32_t i=0u;i<count;++i)
            if(case_policy_task_pended()!=0u)wr(scheduler+28u,1u);
        wr(scheduler+24u,0u);
        if(rd(scheduler+28u)!=0u){switched=1u;(void)case_policy_task_reschedule();}
    }
    (void)case_policy_scheduler_unlock();
    return switched;
}
