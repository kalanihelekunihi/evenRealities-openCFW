/* SPDX-License-Identifier: MIT
 * CASE native 0x0800c0e0 timer queue wait bridge.
 */
#include <stdint.h>
extern void case_policy_scheduler_lock(void); /* 0xbffc */
extern uint32_t case_policy_scheduler_unlock(void); /* 0xc014 */
extern void case_boot_timer_event_wait(uint32_t queue_event,uint32_t ticks,uint32_t option); /* 0xc19c */
extern void case_policy_queue_wait_cleanup(uint32_t queue); /* existing 0xb374 */
static uint8_t rb(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
static void wb(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
/* Stock 0x0800C0E0 (case_normalize_context) */
void case_boot_timer_queue_wait(uint32_t queue,uint32_t ticks,uint32_t option)
{
    case_policy_scheduler_lock();
    if((int8_t)rb(queue+68u)==-1)wb(queue+68u,0u);
    if((int8_t)rb(queue+69u)==-1)wb(queue+69u,0u);
    (void)case_policy_scheduler_unlock();
    if(rd(queue+56u)==0u)case_boot_timer_event_wait(queue+36u,ticks,option);
    case_policy_queue_wait_cleanup(queue);
}
