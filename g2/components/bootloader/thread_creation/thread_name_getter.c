/* SPDX-License-Identifier: MIT
 * Locked Apollo510 thread-name accessor at 0x418372. The null argument uses
 * the current TCB slot at 0x20027134; a missing current TCB invokes the
 * native fatal policy. No task-name buffer contents are synthesized here.
 */
#include <stdint.h>

extern uint32_t opencfw_bl_mask_interrupts(void);

const char *opencfw_boot_thread_name_get(const void *task)
{
    if (task == 0)
        task = (const void *)(uintptr_t)
            *(volatile const uint32_t *)(uintptr_t)UINT32_C(0x20027134);
    if (task == 0) {
        (void)opencfw_bl_mask_interrupts();
        *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
        for (;;)
            __asm__ volatile("b ." ::: "memory");
    }
    return (const char *)task + 0x34;
}
