/* SPDX-License-Identifier: MIT
 * Native CASE 0xa7d2 event clear and 0xaaf0 task event signal wrappers.
 */
#include <stdint.h>
extern uint32_t case_policy_event_receive(uint32_t event,uint32_t mask); /* 0xc44c */
extern uint32_t case_policy_event_receive_irq(uint32_t event); /* 0xc4cc */
extern uint32_t case_policy_event_irq_apply(uint32_t event,uint32_t bits); /* 0xc478 */
extern uint32_t case_policy_task_event_send(uint32_t task,uint32_t op,uint32_t value,uint32_t option,uint32_t timeout); /* 0xcd80 */
/* Stock 0x0800A7D2 (osEventFlagsClear) */
int32_t case_policy_event_clear(uint32_t event,uint32_t mask)
{
    if(event==0u || (mask>>24)!=0u)return -4;
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr":"=r"(ipsr));
    if(ipsr==0u)return (int32_t)case_policy_event_receive(event,mask);
    uint32_t prior=case_policy_event_receive_irq(event);
    if(case_policy_event_irq_apply(event,mask)==0u)return -3;
    return (int32_t)prior;
}
/* Stock 0x0800AAF0 (osTimerStart) */
int32_t case_policy_event_signal(uint32_t task,uint32_t value)
{
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr":"=r"(ipsr));
    if(ipsr!=0u)return -6;
    if(task==0u)return -4;
    return case_policy_task_event_send(task,4u,value,0u,0u)==1u?0:-3;
}
