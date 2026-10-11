/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800ca78 scheduler tick, delayed queue and ready checks.
 */
#include <stdint.h>
extern void case_policy_task_unlink(uint32_t link);
extern void case_policy_task_list_insert(uint32_t list,uint32_t link);
extern void case_policy_task_wake_cleanup(void);
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
uint32_t case_policy_task_pended(void)
{
    uint32_t scheduler=0x20000128u;
    uint32_t changed=0u;
    if(rd(scheduler+0x30u)!=0u){wr(scheduler+24u,rd(scheduler+24u)+1u);return 0u;}
    uint32_t tick=rd(scheduler+12u)+1u;wr(scheduler+12u,tick);
    if(tick==0u){
        uint32_t current_list=rd(scheduler+52u);
        if(rd(current_list)!=0u)native_fault();
        uint32_t overflow_list=rd(scheduler+56u);
        wr(scheduler+52u,overflow_list);wr(scheduler+56u,current_list);
        wr(scheduler+32u,rd(scheduler+32u)+1u);
        case_policy_task_wake_cleanup();
    }
    while(tick>=rd(scheduler+40u)){
        uint32_t list=rd(scheduler+52u);
        if(rd(list)==0u){wr(scheduler+40u,0xffffffffu);break;}
        uint32_t task=rd(rd(list+12u)+12u);
        uint32_t due=rd(task+4u);
        if(tick<due){wr(scheduler+40u,due);break;}
        case_policy_task_unlink(task+4u);
        if(rd(task+40u)!=0u)case_policy_task_unlink(task+24u);
        uint32_t priority=rd(task+44u);
        if(priority>rd(scheduler+16u))wr(scheduler+16u,priority);
        case_policy_task_list_insert(0x20000ff4u+priority*20u,task+4u);
        if(priority>=rd(rd(scheduler)+44u))changed=1u;
    }
    uint32_t current_priority=rd(rd(scheduler)+44u);
    if(rd(0x20000ff4u+current_priority*20u)>1u)changed=1u;
    if(rd(scheduler+28u)!=0u)changed=1u;
    return changed;
}
