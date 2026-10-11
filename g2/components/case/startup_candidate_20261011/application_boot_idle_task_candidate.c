/* SPDX-License-Identifier: MIT
 * Native CASE idle task at 0x0800ae5c; intentionally nonreturning.
 */
#include <stdint.h>
extern void case_boot_idle_maintenance(void); /* 0xace4 */
extern uint32_t case_policy_task_reschedule(void); /* 0xc0a0 */
__attribute__((noreturn)) void case_boot_idle_task_entry(void *arg)
{
    (void)arg;
    volatile uint32_t *ready=(volatile uint32_t *)(uintptr_t)0x20000ff4u;
    for(;;){
        case_boot_idle_maintenance();
        if(*ready>1u)(void)case_policy_task_reschedule();
    }
}
