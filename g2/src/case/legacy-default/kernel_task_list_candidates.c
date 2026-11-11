/* SPDX-License-Identifier: MIT
 * Queue wait/wake and mutex release from fixed CASE stock entries
 * 0x0800c178, 0x0800cba0 and 0x0800cb38. Task delay and scheduler tick
 * remain distinct typed contracts.
 */
#include <stdint.h>
extern _Noreturn void case_kernel_invariant_failure(uint32_t condition);
extern void case_kernel_list_insert_tail(uint32_t list,uint32_t item);
extern uint32_t case_kernel_list_remove(uint32_t item);
extern void case_kernel_list_insert_ordered(uint32_t list,uint32_t item);
extern void case_kernel_task_delay(uint32_t ticks,uint32_t allow_indefinite); /* 0x0800abb0 */
static volatile uint32_t *words(uint32_t address)
{return (volatile uint32_t *)(uintptr_t)address;}
#define SCHED 0x20000128u
#define READY 0x20000ff4u
#define PENDING 0x2000147cu

void case_queue_wait(uint32_t list,uint32_t ticks)
{
    if(list==0u)case_kernel_invariant_failure(9u);
    uint32_t task=words(SCHED)[0];
    case_kernel_list_insert_ordered(list,task+0x18u);
    case_kernel_task_delay(ticks,1u);
}

/* Dedup (0x0800cba0): case_queue_wake is an alias of case_boot_pool_wake_waiter (startup/application_boot_pool_wake_waiter_candidate.c). */
extern uint32_t case_queue_wake(uint32_t *list);

/* Dedup (0x0800cb38): case_kernel_mutex_release is an alias of case_policy_task_notify_resume (startup/application_policy_task_notify_resume_candidate.c). */
extern uint32_t case_kernel_mutex_release(uint32_t task);
/* Dedup (0x0800c178): case_policy_queue_wait_register (was startup/application_policy_queue_wait_helpers_candidate.c). */
__typeof__(case_queue_wait) case_policy_queue_wait_register __attribute__((alias("case_queue_wait")));
