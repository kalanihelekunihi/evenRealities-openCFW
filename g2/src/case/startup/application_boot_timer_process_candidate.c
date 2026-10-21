/* SPDX-License-Identifier: MIT
 * CASE native 0x0800b1fc timer service wait/process decision.
 */
#include <stdint.h>
extern void case_policy_task_sleep_enter(void); /* 0xc380 */
extern uint32_t case_policy_task_sleep_exit(void); /* 0xcc0c */
extern uint32_t case_boot_timer_now(uint32_t *overflow); /* 0xb284 */
extern void case_boot_timer_process_due(uint32_t deadline,uint32_t now); /* 0xb0a0 */
extern void case_boot_timer_queue_wait(uint32_t queue,uint32_t ticks,uint32_t may_block); /* 0xc0e0 */
extern uint32_t case_policy_task_reschedule(void); /* 0xc0a0 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
void case_boot_timer_process(uint32_t deadline,uint32_t wait_flag)
{
    case_policy_task_sleep_enter();
    uint32_t overflow;
    uint32_t now=case_boot_timer_now(&overflow);
    if(overflow!=0u){(void)case_policy_task_sleep_exit();return;}
    if(wait_flag==0u && deadline<=now){
        (void)case_policy_task_sleep_exit();
        case_boot_timer_process_due(deadline,now);
        return;
    }
    uint32_t scheduler=0x20000164u;
    uint32_t may_block=wait_flag;
    if(wait_flag!=0u)may_block=rd(rd(scheduler+16u))==0u;
    case_boot_timer_queue_wait(rd(scheduler),deadline-now,may_block);
    if(case_policy_task_sleep_exit()==0u)(void)case_policy_task_reschedule();
}
