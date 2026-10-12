/* SPDX-License-Identifier: MIT
 * Native CASE 0xc478 IRQ callback dispatch and 0xcd80 task event send.
 */
#include <stdint.h>
extern void vEventGroupClearBitsCallback(void *event_group,uint32_t bits);
extern uint32_t case_policy_irq_event_dispatch(uint32_t descriptor,uint32_t event,uint32_t bits,uint32_t option); /* 0xce0c */
extern uint32_t case_policy_task_lookup(uint32_t task); /* 0xca4c */
extern uint32_t case_policy_task_message_send(uint32_t scheduler,const uint32_t *args,uint32_t timeout,uint32_t option,uint32_t meta); /* 0xc686 */
extern uint32_t case_policy_task_message_special(uint32_t task,const uint32_t *args,uint32_t option,uint32_t unused,uint32_t meta); /* 0xc7a8 */
uint32_t case_policy_event_irq_apply(uint32_t event,uint32_t bits)
{return case_policy_irq_event_dispatch((uint32_t)(uintptr_t)vEventGroupClearBitsCallback,event,bits,0u);}
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
uint32_t case_policy_task_event_send(uint32_t task,uint32_t op,uint32_t value,uint32_t option,uint32_t timeout)
{
    if(task==0u)native_fault();
    uint32_t scheduler=*(volatile uint32_t *)(uintptr_t)0x20000164u;
    if(scheduler==0u)return 0u;
    uint32_t args[3]={op,value,task};
    if((int32_t)op<6){
        if(case_policy_task_lookup(task)!=2u)
            return case_policy_task_message_send(scheduler,args,0u,0u,op);
        return case_policy_task_message_send(scheduler,args,timeout,0u,op);
    }
    return case_policy_task_message_special(scheduler,args,option,0u,op);
}
