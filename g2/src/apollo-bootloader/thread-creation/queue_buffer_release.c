/* SPDX-License-Identifier: MIT. Source candidate for stock 0x418c1e.
 * Releasing the final inherited-mutex reference restores the current task's
 * effective priority and moves its ready-list node back to its base priority.
 */
#include "queue_buffer_release.h"
#include "timer_wait.h"

#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define CURRENT_TCB  UINT32_C(0x20027134)
#define READY_HIGHEST UINT32_C(0x2002714c)
#define READY_LISTS UINT32_C(0x20024870)

extern uint32_t opencfw_bl_mask_interrupts(void);

static _Noreturn void queue_buffer_release_fatal(void)
{
    (void)opencfw_bl_mask_interrupts();
    WORD(UINT32_MAX) = 0u;
    for (;;)
        __asm__ volatile("b ." ::: "memory");
}

uint32_t opencfw_boot_queue_buffer_release(uint32_t *thread)
{
    if (thread == 0)
        return 0u;
    if ((uint32_t)(uintptr_t)thread != WORD(CURRENT_TCB) ||
        thread[25] == 0u)
        queue_buffer_release_fatal();

    --thread[25];
    const uint32_t effective_priority = thread[11];
    const uint32_t base_priority = thread[24];
    if (effective_priority == base_priority || thread[25] != 0u)
        return 0u;

    (void)opencfw_boot_list_unlink(thread + 1);
    thread[11] = base_priority;
    thread[6] = 56u - base_priority;

    if (WORD(READY_HIGHEST) < base_priority)
        WORD(READY_HIGHEST) = base_priority;

    uint32_t *const ready = (uint32_t *)(uintptr_t)
        (READY_LISTS + base_priority * 20u);
    uint32_t *const anchor = (uint32_t *)(uintptr_t)ready[1];
    uint32_t *const previous = (uint32_t *)(uintptr_t)anchor[2];
    thread[2] = (uint32_t)(uintptr_t)anchor;
    thread[3] = (uint32_t)(uintptr_t)previous;
    previous[1] = (uint32_t)(uintptr_t)(thread + 1);
    anchor[2] = (uint32_t)(uintptr_t)(thread + 1);
    thread[5] = (uint32_t)(uintptr_t)ready;
    ready[0] = ready[0] + 1u;
    return 1u;
}
