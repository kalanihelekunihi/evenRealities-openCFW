/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800b260 wake-list deadline update.
 */
#include <stdint.h>
void case_policy_task_wake_cleanup(void)
{
    volatile uint32_t *scheduler=(volatile uint32_t *)(uintptr_t)0x20000128u;
    uint32_t list=scheduler[13];
    if(*(volatile uint32_t *)(uintptr_t)list!=0u){
        uint32_t node=*(volatile uint32_t *)(uintptr_t)(list+12u);
        uint32_t task=*(volatile uint32_t *)(uintptr_t)(node+12u);
        scheduler[10]=*(volatile uint32_t *)(uintptr_t)(task+4u);
    }else scheduler[10]=0xffffffffu;
}
/* Dedup (0x0800b260): case_reset_next_unblock (was scheduler-list/resume.c). */
__typeof__(case_policy_task_wake_cleanup) case_reset_next_unblock __attribute__((alias("case_policy_task_wake_cleanup")));
