/* SPDX-License-Identifier: MIT
 * Native CASE 0xca4c scheduler mode and 0xce0c IRQ event packet.
 */
#include <stdint.h>
extern uint32_t case_policy_task_message_special(uint32_t scheduler,const uint32_t *args,uint32_t option,uint32_t unused,uint32_t meta); /* 0xc7a8 */
uint32_t case_policy_task_lookup(uint32_t ignored)
{
    (void)ignored;
    volatile uint32_t *scheduler=(volatile uint32_t *)(uintptr_t)0x20000128u;
    if(scheduler[5]==0u)return 1u;
    return scheduler[12]==0u?2u:0u;
}
/* Stock 0x0800CE0C (case_policy_irq_event_dispatch) */
uint32_t case_policy_irq_event_dispatch(uint32_t descriptor,uint32_t event,uint32_t bits,uint32_t option)
{
    uint32_t args[4]={0xfffffffeu,descriptor,event,bits};
    uint32_t scheduler=*(volatile uint32_t *)(uintptr_t)0x20000164u;
    return case_policy_task_message_special(scheduler,args,option,0u,0xfffffffeu);
}
