/* SPDX-License-Identifier: MIT. Reconstructs stock 41872c/4189a2.
 * Event-list removal, suspended pending-ready insertion, ready insertion,
 * and yield ordering follow the private ARM32 layout proven in the image. */
#include "event_waiter_wake.h"
#include "timer_wait.h"
#include <stdint.h>

#define WORD(address) (*(volatile uint32_t *)(uintptr_t)(address))

extern uint32_t opencfw_bl_mask_interrupts(void);
extern void opencfw_boot_next_unblock_refresh(void);

static void owner_fatal(void)
{
    (void)opencfw_bl_mask_interrupts();
    WORD(UINT32_MAX) = 0u;
    for (;;)
        __asm volatile("b ." ::: "memory");
}

static void insert_before_index(uint32_t *list, uint32_t *item)
{
    uint32_t *const index = (uint32_t *)(uintptr_t)list[1];
    uint32_t *const previous = (uint32_t *)(uintptr_t)index[2];
    item[1] = (uintptr_t)index;
    item[2] = (uintptr_t)previous;
    previous[1] = (uintptr_t)item;
    index[2] = (uintptr_t)item;
    item[4] = (uintptr_t)list;
    ++list[0];
}

uint32_t opencfw_bl_remove_event_waiter(uint32_t *list)
{
    uint32_t *const event_item = (uint32_t *)(uintptr_t)list[3];
    uint32_t *const thread = (uint32_t *)(uintptr_t)event_item[3];
    if (thread == 0)
        owner_fatal();

    (void)opencfw_boot_list_unlink(event_item);
    if (WORD(0x2002716cu) == 0u) {
        (void)opencfw_boot_list_unlink(thread + 1);

        const uint32_t priority = thread[11];
        if (WORD(0x2002714cu) < priority)
            WORD(0x2002714cu) = priority;

        uint32_t *const ready =
            (uint32_t *)(uintptr_t)(0x20024870u + 20u * priority);
        insert_before_index(ready, thread + 1);
        opencfw_boot_next_unblock_refresh();
    } else {
        uint32_t *const pending = (uint32_t *)(uintptr_t)0x20026f5cu;
        insert_before_index(pending, event_item);
    }

    uint32_t *const current =
        (uint32_t *)(uintptr_t)WORD(0x20027134u);
    if (thread[11] > current[11]) {
        WORD(0x20027158u) = 1u;
        return 1u;
    }
    return 0u;
}

void opencfw_bl_missed_yield(void)
{
    WORD(0x20027158u) = 1u;
}
