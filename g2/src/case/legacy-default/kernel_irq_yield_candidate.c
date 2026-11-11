/* SPDX-License-Identifier: MIT
 * Stock 0x080000f4, 0x080000fc and 0x0800c0a0. These are architecture
 * operations and an architected SCB write, with no product configuration.
 */
#include <stdint.h>

uint32_t case_kernel_irq_save(void)
{
    uint32_t primask;
    __asm__ volatile("mrs %0, primask\n\tcpsid i" : "=r"(primask) :: "memory");
    return primask;
}

void case_kernel_irq_restore(uint32_t primask)
{
    __asm__ volatile("msr primask, %0" :: "r"(primask) : "memory");
}

/* Dedup (0x0800c0a0): case_kernel_yield is an alias of case_policy_task_reschedule (startup/application_policy_scheduler_primitives_candidate.c). */
extern void case_kernel_yield(void);
/* Dedup (0x080000f4): case_mask_save (was glue/mask_providers.c). */
__typeof__(case_kernel_irq_save) case_mask_save __attribute__((alias("case_kernel_irq_save")));
/* Dedup (0x080000fc): case_mask_restore (was glue/mask_providers.c). */
__typeof__(case_kernel_irq_restore) case_mask_restore __attribute__((alias("case_kernel_irq_restore")));
