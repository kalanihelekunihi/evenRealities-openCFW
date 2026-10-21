/* SPDX-License-Identifier: MIT. Readable candidate for stock 0x41866a. */
#include "flags_runtime.h"
#include <stddef.h>

#define OPENCFW_KERNEL_READY_WORD UINT32_C(0x2002716c)
#define OPENCFW_CURRENT_TCB_WORD  UINT32_C(0x20027134)

/* Implemented by the scheduler component; the test intercepts this ABI. */
extern void opencfw_boot_task_block(uint32_t timeout_ticks,
                                    uint32_t suspend_indefinitely);
extern uint32_t opencfw_bl_mask_interrupts(void);
extern uint32_t opencfw_provider_41602a(void);
extern uint32_t opencfw_bl_queue_runtime_mode(void);
extern void opencfw_bl_scheduler_suspend(void);
extern uint32_t opencfw_bl_scheduler_resume(void);
extern void opencfw_bl_kernel_reschedule(void);
extern void opencfw_bl_kernel_enter(void);
extern void opencfw_bl_kernel_exit(void);

static _Noreturn void flags_fatal(void)
{
    (void)opencfw_bl_mask_interrupts();
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    for (;;)
        __asm__ volatile("b ." ::: "memory");
}

uint32_t opencfw_provider_418d7a(void)
{
    volatile uint32_t *const tcb = (volatile uint32_t *)(uintptr_t)
        *(volatile const uint32_t *)(uintptr_t)OPENCFW_CURRENT_TCB_WORD;
    const uint32_t previous = tcb[6];
    tcb[6] = 0x38u - tcb[11];
    return previous;
}

typedef struct {
    uint32_t reserved[6];
    uint32_t flags;
    uint32_t wait_previous;
    uint32_t wait_next;
    uint32_t opaque;
    uint32_t wait_object;
} opencfw_tcb_prefix_t;

typedef struct {
    uint32_t flags;
    uint32_t waiter_count;
    uint32_t wait_anchor;
} opencfw_event_flags_prefix_t;

_Static_assert(offsetof(opencfw_tcb_prefix_t, flags) == 24, "flags offset");
_Static_assert(offsetof(opencfw_tcb_prefix_t, wait_previous) == 28,
               "wait-list previous offset");
_Static_assert(offsetof(opencfw_tcb_prefix_t, wait_next) == 32,
               "wait-list next offset");
_Static_assert(offsetof(opencfw_tcb_prefix_t, wait_object) == 40,
               "wait object offset");
_Static_assert(offsetof(opencfw_event_flags_prefix_t, waiter_count) == 4,
               "waiter count offset");
_Static_assert(offsetof(opencfw_event_flags_prefix_t, wait_anchor) == 8,
               "wait anchor offset");

void opencfw_provider_41866a(uint32_t *waiter_count, uint32_t wait_flags,
                             uint32_t timeout_ticks)
{
    if (waiter_count == 0 ||
        *(volatile const uint32_t *)(uintptr_t)OPENCFW_KERNEL_READY_WORD == 0u) {
        flags_fatal();
    }

    volatile uint32_t *const current_tcb =
        (volatile uint32_t *)(uintptr_t)
            *(volatile const uint32_t *)(uintptr_t)OPENCFW_CURRENT_TCB_WORD;
    volatile uint32_t *const anchor =
        (volatile uint32_t *)(uintptr_t)waiter_count[1];
    volatile opencfw_tcb_prefix_t *const tcb =
        (volatile opencfw_tcb_prefix_t *)(void *)current_tcb;
    volatile uint32_t *const waiter =
        (volatile uint32_t *)(void *)&tcb->flags;
    const uint32_t next = anchor[2];

    waiter[0] = wait_flags | UINT32_C(0x80000000);
    waiter[1] = (uint32_t)(uintptr_t)anchor;
    waiter[2] = next;
    ((volatile uint32_t *)(uintptr_t)next)[1] = (uint32_t)(uintptr_t)waiter;
    anchor[2] = (uint32_t)(uintptr_t)waiter;
    tcb->wait_object = (uint32_t)(uintptr_t)waiter_count;
    *waiter_count = *waiter_count + 1u;

    opencfw_boot_task_block(timeout_ticks, 1u);
}

static uint32_t event_flags_satisfied(uint32_t current, uint32_t mask,
                                     uint32_t wait_all)
{
    return wait_all != 0u ? (current & mask) == mask
                          : (current & mask) != 0u;
}

uint32_t opencfw_provider_4199dc(uint32_t *event_flags, uint32_t mask,
                                 uint32_t clear_on_exit, uint32_t wait_all,
                                 uint32_t timeout_ticks)
{
    if (event_flags == 0 || mask == 0u || (mask & UINT32_C(0xff000000)) != 0u ||
        (opencfw_bl_queue_runtime_mode() == 0u && timeout_ticks != 0u)) {
        flags_fatal();
    }

    opencfw_bl_scheduler_suspend();
    uint32_t observed = *event_flags;
    if (event_flags_satisfied(observed, mask, wait_all) != 0u) {
        if (clear_on_exit != 0u)
            *event_flags = observed & ~mask;
        (void)opencfw_bl_scheduler_resume();
        return observed;
    }
    if (timeout_ticks == 0u) {
        (void)opencfw_bl_scheduler_resume();
        return observed;
    }

    uint32_t waiter_flags = mask;
    if (clear_on_exit != 0u)
        waiter_flags |= UINT32_C(0x01000000);
    if (wait_all != 0u)
        waiter_flags |= UINT32_C(0x04000000);
    opencfw_provider_41866a((uint32_t *)(void *)(event_flags + 1),
                            waiter_flags, timeout_ticks);

    if (opencfw_bl_scheduler_resume() == 0u)
        opencfw_bl_kernel_reschedule();
    const uint32_t wait_state = opencfw_provider_418d7a();
    if ((wait_state & UINT32_C(0x02000000)) != 0u)
        return wait_state & UINT32_C(0x00ffffff);

    opencfw_bl_kernel_enter();
    observed = *event_flags;
    if (event_flags_satisfied(observed, mask, wait_all) != 0u &&
        clear_on_exit != 0u)
        *event_flags = observed & ~mask;
    opencfw_bl_kernel_exit();
    return observed & UINT32_C(0x00ffffff);
}

uint32_t opencfw_provider_416590(uint32_t *event_flags, uint32_t mask,
                                 uint32_t options, uint32_t timeout_ticks)
{
    if (event_flags == 0 || (mask & UINT32_C(0xff000000)) != 0u)
        return UINT32_C(0xfffffffc);

    if (opencfw_provider_41602a() != 0u)
        return timeout_ticks == 0u ? UINT32_C(0xfffffffa)
                                   : UINT32_C(0xfffffffc);

    const uint32_t clear_on_exit = (options & 2u) == 0u;
    const uint32_t wait_all = options & 1u;
    const uint32_t observed = opencfw_provider_4199dc(event_flags, mask,
        clear_on_exit, wait_all, timeout_ticks);
    const uint32_t matched = wait_all != 0u
        ? (observed & mask) == mask
        : (observed & mask) != 0u;
    if (matched)
        return observed;
    return timeout_ticks == 0u ? UINT32_C(0xfffffffd)
                               : UINT32_C(0xfffffffe);
}
