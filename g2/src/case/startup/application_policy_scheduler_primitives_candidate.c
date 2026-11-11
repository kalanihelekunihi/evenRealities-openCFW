/* SPDX-License-Identifier: MIT
 * Native CASE 0xbffc, 0xc014, 0xc0a0, 0xc380 scheduler primitives.
 */
#include <stdint.h>
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i");for(;;){}}
void case_policy_scheduler_lock(void)
{
    volatile uint32_t *depth=(volatile uint32_t *)(uintptr_t)0x2000019cu;
    __asm__ volatile("cpsid i" ::: "memory");
    *depth=*depth+1u;
    __asm__ volatile("dsb\nisb" ::: "memory");
}
/* Stock 0x0800C014 (case_policy_scheduler_unlock) */
uint32_t case_policy_scheduler_unlock(void)
{
    volatile uint32_t *depth=(volatile uint32_t *)(uintptr_t)0x2000019cu;
    if(*depth==0u)native_fault();
    uint32_t next=*depth-1u;
    *depth=next;
    if(next==0u)__asm__ volatile("cpsie i" ::: "memory");
    return next;
}
uint32_t case_policy_task_reschedule(void)
{
    *(volatile uint32_t *)(uintptr_t)0xe000ed04u=0x10000000u;
    __asm__ volatile("dsb\nisb" ::: "memory");
    return 0x10000000u;
}
void case_policy_task_sleep_enter(void)
{
    volatile uint32_t *depth=(volatile uint32_t *)(uintptr_t)0x20000158u;
    *depth=*depth+1u;
}
/* Dedup (0x0800bffc): case_kernel_enter (was legacy-default/kernel_small_leaves_candidate.c). */
__typeof__(case_policy_scheduler_lock) case_kernel_enter __attribute__((alias("case_policy_scheduler_lock")));
/* Dedup (0x0800bffc): case_enter_critical (was glue/critical_providers.c). */
__typeof__(case_policy_scheduler_lock) case_enter_critical __attribute__((alias("case_policy_scheduler_lock")));
/* Dedup (0x0800c014): case_kernel_exit (was legacy-default/kernel_small_leaves_candidate.c). */
void case_kernel_exit(void) __attribute__((alias("case_policy_scheduler_unlock")));
/* Dedup (0x0800c014): case_exit_critical (was glue/critical_providers.c). */
void case_exit_critical(void) __attribute__((alias("case_policy_scheduler_unlock")));
/* Dedup (0x0800c0a0): case_kernel_yield (was legacy-default/kernel_irq_yield_candidate.c). */
void case_kernel_yield(void) __attribute__((alias("case_policy_task_reschedule")));
/* Dedup (0x0800c0a0): case_yield_request (was glue/yield_request.c). */
__typeof__(case_policy_task_reschedule) case_yield_request __attribute__((alias("case_policy_task_reschedule")));
/* Dedup (0x0800c380): case_kernel_scheduler_suspend (was legacy-default/kernel_queue_small_state_candidate.c). */
__typeof__(case_policy_task_sleep_enter) case_kernel_scheduler_suspend __attribute__((alias("case_policy_task_sleep_enter")));
/* Dedup (0x0800c380): case_suspend_scheduler (was glue/suspend_scheduler.c). */
__typeof__(case_policy_task_sleep_enter) case_suspend_scheduler __attribute__((alias("case_policy_task_sleep_enter")));
