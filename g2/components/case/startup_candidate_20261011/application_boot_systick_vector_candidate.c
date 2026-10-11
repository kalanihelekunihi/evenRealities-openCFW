/* SPDX-License-Identifier: MIT
 * CASE 0x08008420 SysTick vector and 0x0800c5ac tick-yield wrapper.
 */
#include <stdint.h>
extern uint32_t case_policy_task_lookup(uint32_t mode); /* 0xca4c */
extern uint32_t case_kernel_irq_save(void); /* 0x00f4 */
extern void case_kernel_irq_restore(uint32_t token); /* 0x00fc */
extern uint32_t case_policy_task_pended(void); /* 0xca78 */
void case_boot_systick_dispatch(void)
{
    uint32_t token=case_kernel_irq_save();
    if(case_policy_task_pended()!=0u)
        *(volatile uint32_t *)(uintptr_t)0xe000ed04u=0x10000000u;
    case_kernel_irq_restore(token);
}
void case_vector_systick_8420(void)
{
    uint32_t control=*(volatile uint32_t *)(uintptr_t)0xe000e010u;
    if(case_policy_task_lookup(control)!=1u)case_boot_systick_dispatch();
}
