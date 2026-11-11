/* SPDX-License-Identifier: MIT
 * Native CASE event peek 0x0800a816 and queue receive paths 0xc44c/0xc4cc.
 */
#include <stdint.h>
extern void case_policy_scheduler_lock(void); /* 0xbffc */
extern uint32_t case_policy_scheduler_unlock(void); /* 0xc014 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
/* Dedup (0x0800c44c): case_policy_event_receive is an alias of xEventGroupClearBits (glue/event_clear_task.c). */
extern uint32_t case_policy_event_receive(uint32_t event,uint32_t mask);
uint32_t case_policy_event_receive_irq(uint32_t event)
{
    uint32_t primask;
    __asm__ volatile("mrs %0, primask\ncpsid i":"=r"(primask)::"memory");
    uint32_t prior=rd(event);
    __asm__ volatile("msr primask, %0"::"r"(primask):"memory");
    return prior;
}
/* Stock 0x0800A816 (osEventFlagsGet) */
uint32_t case_policy_event_peek(uint32_t event)
{
    if(event==0u)return 0u;
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr":"=r"(ipsr));
    return ipsr!=0u?case_policy_event_receive_irq(event):case_policy_event_receive(event,0u);
}
