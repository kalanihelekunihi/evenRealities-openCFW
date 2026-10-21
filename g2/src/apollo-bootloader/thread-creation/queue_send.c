/* SPDX-License-Identifier: MIT. Source candidate for stock 0x419ec0 and
 * its directly required ring-buffer copy helper 0x41a4a6. */
#include "queue_send.h"
#include "queue_receive.h"
#include "timer_wait.h"
#include <stddef.h>

#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_bl_mask_interrupts(void);
extern void opencfw_bl_kernel_enter(void);
extern void opencfw_bl_kernel_exit(void);
extern void opencfw_bl_scheduler_suspend(void);
extern uint32_t opencfw_bl_scheduler_resume(void);
extern void opencfw_bl_kernel_reschedule(void);
extern uint32_t opencfw_bl_queue_runtime_mode(void);
extern uint32_t opencfw_bl_remove_event_waiter(uint32_t *anchor);
extern uint32_t opencfw_boot_queue_buffer_release(uint32_t *buffer);

static _Noreturn void queue_send_fatal(void)
{
    (void)opencfw_bl_mask_interrupts();
    WORD(UINT32_MAX) = 0u;
    for (;;)
        __asm__ volatile("b ." ::: "memory");
}

static void byte_copy(void *destination, const void *source, uint32_t count)
{
    volatile uint8_t *to = (volatile uint8_t *)destination;
    const volatile uint8_t *from = (const volatile uint8_t *)source;
    for (uint32_t i = 0; i < count; ++i)
        to[i] = from[i];
}

/* 0x41a4a6. mode 0 appends at the current write pointer; other modes
 * reserve from the preceding end of the ring. Mode 2 replaces the oldest
 * item when full by decrementing count before the common increment. */
uint32_t opencfw_boot_queue_copy_in(uint32_t *queue, const void *message,
                                    uint32_t mode)
{
    uint32_t count = queue[14];
    uint32_t result = 0u;
    const uint32_t item_size = queue[16];
    if (item_size == 0u) {
        if (queue[0] == 0u) {
            result = opencfw_boot_queue_buffer_release(
                (uint32_t *)(uintptr_t)queue[2]);
            queue[2] = 0u;
        }
    } else if (mode == 0u) {
        uint32_t *write_cursor = &queue[1];
        byte_copy((void *)(uintptr_t)*write_cursor, message, item_size);
        *write_cursor += item_size;
        if (*write_cursor >= queue[2])
            *write_cursor = queue[0];
    } else {
        uint32_t *write_cursor = &queue[3];
        const uint32_t previous = *write_cursor;
        byte_copy((void *)(uintptr_t)previous, message, item_size);
        *write_cursor = previous - item_size;
        if (*write_cursor < queue[0])
            *write_cursor = queue[2] - item_size;
        if (mode == 2u && count != 0u)
            --count;
    }
    queue[14] = count + 1u;
    return result;
}

static uint32_t queue_is_full(uint32_t *queue)
{
    opencfw_bl_kernel_enter();
    const uint32_t full = queue[14] == queue[15];
    opencfw_bl_kernel_exit();
    return full;
}

uint32_t opencfw_bl_kernel_queue_put_blocking(uint32_t *queue,
                                               const void *message,
                                               uint32_t timeout_ticks,
                                               uint32_t mode)
{
    if (queue == NULL)
        queue_send_fatal();
    if (message == NULL && queue[16] != 0u)
        queue_send_fatal();
    if (mode == 2u && queue[15] != 1u)
        queue_send_fatal();
    if (opencfw_bl_queue_runtime_mode() == 0u && timeout_ticks != 0u)
        queue_send_fatal();

    uint32_t timeout_state[2];
    uint32_t captured = 0u;
    for (;;) {
        opencfw_bl_kernel_enter();
        uint32_t count = queue[14];
        if (count < queue[15] || mode == 2u) {
            (void)opencfw_boot_queue_copy_in(queue, message, mode);
            if (queue[9] != 0u &&
                opencfw_bl_remove_event_waiter(queue + 9) != 0u)
                opencfw_bl_kernel_reschedule();
            opencfw_bl_kernel_exit();
            return 1u;
        }
        if (timeout_ticks == 0u) {
            opencfw_bl_kernel_exit();
            return 0u;
        }

        if (!captured) {
            opencfw_boot_timeout_capture(timeout_state);
            captured = 1u;
        }

        opencfw_bl_kernel_exit();
        opencfw_bl_scheduler_suspend();
        opencfw_bl_kernel_enter();
        volatile int8_t *const locks = (volatile int8_t *)(void *)queue + 0x44;
        if (locks[0] == -1)
            locks[0] = 0;
        if (locks[1] == -1)
            locks[1] = 0;
        opencfw_bl_kernel_exit();

        if (opencfw_boot_timeout_check(timeout_state, &timeout_ticks) != 0u) {
            opencfw_boot_timer_queue_unlock(queue);
            (void)opencfw_bl_scheduler_resume();
            return 0u;
        }

        if (queue_is_full(queue)) {
            opencfw_boot_wait_list_sorted(queue + 4, timeout_ticks);
            opencfw_boot_timer_queue_unlock(queue);
            if (opencfw_bl_scheduler_resume() == 0u)
                opencfw_bl_kernel_reschedule();
            continue;
        }

        opencfw_boot_timer_queue_unlock(queue);
        (void)opencfw_bl_scheduler_resume();
    }
}
