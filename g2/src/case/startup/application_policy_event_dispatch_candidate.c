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
/* Stock 0x0800CD80 (case_policy_task_event_send, FreeRTOS
 * xTimerGenericCommand). Native code writes three message words into a
 * 16-byte queue item and leaves the fourth as an ambient stack word; it is 0
 * here. The from-ISR path's fifth argument is the stack word stock leaves
 * there (message word 0, the command id >= 6, so never 0). */
uint32_t case_policy_task_event_send(uint32_t task,uint32_t op,uint32_t value,uint32_t option,uint32_t timeout)
{
    if(task==0u){
        __asm__ volatile("cpsid i" ::: "memory");
        for(;;){}
    }
    uint32_t queue=*(volatile uint32_t *)(uintptr_t)0x20000164u;
    if(queue==0u)return 0u;
    uint32_t message[4];
    message[0]=op;message[1]=value;message[2]=task;message[3]=0u;
    if((int32_t)op>=6)
        return case_policy_task_message_special(queue,message,option,0u,op);
    uint32_t wait=case_policy_task_lookup(task)==2u ? timeout : 0u;
    return case_policy_task_message_send(*(volatile uint32_t *)(uintptr_t)0x20000164u,
                                         message,wait,0u,0u);
}
/* Dedup (0x0800cd80): case_task_signal (was legacy-default/task_kernel_candidates.c). */
__typeof__(case_policy_task_event_send) case_task_signal __attribute__((alias("case_policy_task_event_send")));
