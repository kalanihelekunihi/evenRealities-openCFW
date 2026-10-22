/* SPDX-License-Identifier: MIT
 * Native CASE 0xc15c, 0xc178, 0xc948, 0xb080, 0xca4c queue wait helpers.
 */
#include <stdint.h>
extern void case_policy_scheduler_lock(void);
extern uint32_t case_policy_scheduler_unlock(void);
extern void case_policy_task_list_insert_sorted(uint32_t list,uint32_t task_link); /* 0xbfb0 */
extern void case_policy_task_sleep_enqueue(uint32_t timeout,uint32_t mode); /* 0xabb0 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
uint32_t case_policy_scheduler_mode(void)
{
    if(rd(0x20000128u+20u)==0u)return 1u;
    return rd(0x20000128u+48u)!=0u?0u:2u;
}
void case_policy_queue_wait_snapshot(uint32_t *snapshot)
{
    snapshot[0]=rd(0x20000128u+32u);
    snapshot[1]=rd(0x20000128u+12u);
}
uint32_t case_policy_queue_wait_eligible(uint32_t queue)
{
    case_policy_scheduler_lock();
    uint32_t result=rd(queue+56u)==rd(queue+60u);
    (void)case_policy_scheduler_unlock();
    return result;
}
/* Stock 0x0800C178 (case_policy_queue_wait_register) */
void case_policy_queue_wait_register(uint32_t list,uint32_t timeout)
{
    if(list==0u)native_fault();
    case_policy_task_list_insert_sorted(list,rd(0x20000128u)+24u);
    case_policy_task_sleep_enqueue(timeout,1u);
}
/* Stock 0x0800C948 (case_policy_queue_wait_elapsed) */
uint32_t case_policy_queue_wait_elapsed(uint32_t *snapshot,uint32_t *timeout)
{
    if(snapshot==0 || timeout==0)native_fault();
    case_policy_scheduler_lock();
    uint32_t now=rd(0x20000128u+12u),before=snapshot[1],remaining=*timeout;
    uint32_t result;
    if(remaining==UINT32_MAX)result=0u;
    else if(snapshot[0]!=rd(0x20000128u+32u) && before<=now)result=1u;
    else if(remaining>now-before){*timeout=remaining-(now-before);case_policy_queue_wait_snapshot(snapshot);result=0u;}
    else {*timeout=0u;result=1u;}
    (void)case_policy_scheduler_unlock();
    return result;
}
