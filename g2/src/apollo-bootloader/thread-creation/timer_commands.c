/* SPDX-License-Identifier: MIT. Source reconstruction of stock
 * 0x419546 (timer queue command drain), 0x419508 (timer list insertion), and
 * 0x4193de (auto-reload catch-up). Command records are four 32-bit words.
 * Timer expiry (0x419406) and list rollover (0x41965c) remain providers.
 */
#include "timer_commands.h"
#include "queue_receive.h"
#include "timer_wait.h"
#include <stddef.h>

#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define TIMER_STATE(timer) (*(volatile uint8_t *)((uintptr_t)(timer) + 0x28u))

extern uint32_t opencfw_bl_mask_interrupts(void);
extern void opencfw_bl_rtos_free(uintptr_t address);

static _Noreturn void timer_fatal(void)
{
    (void)opencfw_bl_mask_interrupts();
    WORD(UINT32_MAX) = 0u;
    for (;;)
        __asm__ volatile("b ." ::: "memory");
}

/* Stock 0x419508: choose the current or wrapped timer list, or report that
 * the deadline has already elapsed. The comparison order is significant at
 * UINT32 wrap boundaries. */
uint32_t opencfw_boot_timer_insert(uint32_t *timer, uint32_t deadline,
                                   uint32_t now, uint32_t delta)
{
    timer[1] = deadline;
    timer[4] = (uintptr_t)timer;
    if (now < deadline) {
        if (now < delta && delta <= deadline)
            return 1u;
        opencfw_boot_list_insert_sorted(
            (uint32_t *)(uintptr_t)WORD(0x20027178), timer + 1);
    } else if (now - delta < timer[6]) {
        opencfw_boot_list_insert_sorted(
            (uint32_t *)(uintptr_t)WORD(0x2002717c), timer + 1);
    } else {
        return 1u;
    }
    return 0u;
}

/* Stock 0x4193de invokes the timer callback once per elapsed period until
 * insertion succeeds. The final callback after the command itself remains
 * in the caller, matching the two separate call sites in the image. */
void opencfw_boot_timer_reload(uint32_t *timer, uint32_t deadline,
                              uint32_t now)
{
    for (;;) {
        uint32_t period = timer[6];
        if (!opencfw_boot_timer_insert(timer, deadline + period, now, deadline))
            break;
        deadline += timer[6];
        ((void (*)(uint32_t *))(uintptr_t)timer[8])(timer);
    }
}

static void timer_callback(uint32_t *timer)
{
    ((void (*)(uint32_t *))(uintptr_t)timer[8])(timer);
}

void opencfw_bl_timer_process_commands(void)
{
    uint32_t message[4];
    uint32_t *queue = (uint32_t *)(uintptr_t)WORD(0x20027180);

    while (opencfw_bl_kernel_queue_get_blocking(queue, message, 0u)) {
        int32_t command = (int32_t)message[0];
        if (command < 0) {
            ((void (*)(uint32_t, uint32_t))(uintptr_t)message[1])(
                message[2], message[3]);
            continue;
        }

        uint32_t *timer = (uint32_t *)(uintptr_t)message[2];
        if (timer[5] != 0u)
            (void)opencfw_boot_list_unlink(timer + 1);

        uint32_t wrapped = 0u;
        uint32_t now = opencfw_boot_timer_sample_time(&wrapped);
        (void)wrapped;

        switch ((uint32_t)command) {
        case 1u:
        case 2u:
        case 6u:
        case 7u: {
            TIMER_STATE(timer) |= 1u;
            uint32_t deadline = timer[6] + message[1];
            if (!opencfw_boot_timer_insert(timer, deadline, now, message[1]))
                break;
            if (TIMER_STATE(timer) & 4u)
                opencfw_boot_timer_reload(timer, deadline, now);
            else
                TIMER_STATE(timer) &= (uint8_t)~1u;
            timer_callback(timer);
            break;
        }
        case 3u:
        case 8u:
            TIMER_STATE(timer) &= (uint8_t)~1u;
            break;
        case 4u:
        case 9u: {
            TIMER_STATE(timer) |= 1u;
            timer[6] = message[1];
            if (timer[6] == 0u)
                timer_fatal();
            uint32_t deadline = now + timer[6];
            (void)opencfw_boot_timer_insert(timer, deadline, now, now);
            break;
        }
        case 5u:
            if (TIMER_STATE(timer) & 2u)
                TIMER_STATE(timer) &= (uint8_t)~1u;
            else
                opencfw_bl_rtos_free((uintptr_t)timer);
            break;
        default:
            break;
        }
    }
}
