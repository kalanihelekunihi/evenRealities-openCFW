/* SPDX-License-Identifier: MIT
 * Stock 0x0800b374 deferred queue event release. The wake operation
 * retains its own typed task-list contract.
 */
#include <stdint.h>
extern void case_kernel_enter(void);
extern void case_kernel_exit(void);
extern uint32_t case_queue_wake(uint32_t *list);
extern void case_kernel_request_yield(void); /* stock 0x0800c16c */

/* Dedup (0x0800b374): case_queue_unlock is an alias of case_policy_queue_wait_cleanup (startup/application_policy_queue_wait_cleanup_candidate.c). */
extern void case_queue_unlock(uint32_t queue);

/* Stock 0x0800C16C (case_kernel_request_yield) */
void case_kernel_request_yield(void)
{
    *(volatile uint32_t *)(uintptr_t)0x20000144u=1u;
}
