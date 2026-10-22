/* SPDX-License-Identifier: MIT
 * CASE native 0x0800c19c task event-list wait.
 */
#include <stdint.h>
extern void case_policy_task_list_insert(uint32_t list,uint32_t link); /* 0xbfe2 */
extern void case_policy_task_sleep_enqueue(uint32_t ticks,uint32_t mode); /* 0xabb0 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
/* Stock 0x0800C19C (case_boot_timer_event_wait) */
void case_boot_timer_event_wait(uint32_t event_list,uint32_t ticks,uint32_t indefinite)
{
    if(event_list==0u)native_fault();
    case_policy_task_list_insert(event_list,rd(0x20000128u)+24u);
    case_policy_task_sleep_enqueue(indefinite!=0u?UINT32_MAX:ticks,indefinite);
}
