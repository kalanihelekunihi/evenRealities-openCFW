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
{__asm__ volatile("cpsid i");for(;;){}}
/* Dedup (0x0800ca4c): case_policy_scheduler_mode is an alias of case_policy_task_lookup (startup/application_policy_event_scheduler_helpers_candidate.c). */
extern uint32_t case_policy_scheduler_mode(void);
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
/* Dedup (0x0800c178): case_policy_queue_wait_register is an alias of case_queue_wait (legacy-default/kernel_task_list_candidates.c). */
extern void case_policy_queue_wait_register(uint32_t list,uint32_t timeout);
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
/* Dedup (0x0800b080): case_queue_is_active (was legacy-default/kernel_queue_small_state_candidate.c). */
__typeof__(case_policy_queue_wait_eligible) case_queue_is_active __attribute__((alias("case_policy_queue_wait_eligible")));
/* Dedup (0x0800c15c): case_kernel_timeout_start (was legacy-default/kernel_queue_small_state_candidate.c). */
__typeof__(case_policy_queue_wait_snapshot) case_kernel_timeout_start __attribute__((alias("case_policy_queue_wait_snapshot")));
/* Dedup (0x0800c948): case_kernel_timeout_check (was legacy-default/kernel_queue_small_state_candidate.c). */
uint32_t case_kernel_timeout_check(uint32_t snapshot[2],uint32_t *ticks) __attribute__((alias("case_policy_queue_wait_elapsed")));
