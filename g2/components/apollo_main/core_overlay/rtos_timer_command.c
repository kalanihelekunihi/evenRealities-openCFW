/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * RTOS timer command submission matched to stock entry 0x0047E7B0.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_command_uintptr;

struct open_cfw_rtos_timer_command_message {
    int command_id;
    unsigned int optional_value;
    unsigned int timer;
};

typedef unsigned int (*open_cfw_rtos_timer_command_scheduler_function)(void);
typedef unsigned int (*open_cfw_rtos_timer_command_task_send_function)(
    void *,
    const struct open_cfw_rtos_timer_command_message *,
    unsigned int,
    unsigned int
);
typedef unsigned int (*open_cfw_rtos_timer_command_isr_send_function)(
    void *,
    const struct open_cfw_rtos_timer_command_message *,
    unsigned int *,
    unsigned int
);
typedef void (*open_cfw_rtos_timer_command_lock_function)(void);

#ifndef OPEN_CFW_RTOS_TIMER_COMMAND_QUEUE
#define OPEN_CFW_RTOS_TIMER_COMMAND_QUEUE() \
    ((void *)(open_cfw_rtos_timer_command_uintptr) \
        (*(volatile unsigned int *) \
            (open_cfw_rtos_timer_command_uintptr)0x20074AB0U))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_COMMAND_SCHEDULER_STATE
#define OPEN_CFW_RTOS_TIMER_COMMAND_SCHEDULER_STATE() \
    (((open_cfw_rtos_timer_command_scheduler_function) \
        (open_cfw_rtos_timer_command_uintptr)0x004558A5U)())
#endif

#ifndef OPEN_CFW_RTOS_TIMER_COMMAND_TASK_SEND
#define OPEN_CFW_RTOS_TIMER_COMMAND_TASK_SEND( \
    queue, message, ticks_to_wait, copy_position \
) \
    (((open_cfw_rtos_timer_command_task_send_function) \
        (open_cfw_rtos_timer_command_uintptr)0x004417EFU)( \
            queue, message, ticks_to_wait, copy_position))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_COMMAND_ISR_SEND
#define OPEN_CFW_RTOS_TIMER_COMMAND_ISR_SEND( \
    queue, message, higher_priority_task_woken, copy_position \
) \
    (((open_cfw_rtos_timer_command_isr_send_function) \
        (open_cfw_rtos_timer_command_uintptr)0x00441953U)( \
            queue, message, higher_priority_task_woken, copy_position))
#endif

#ifndef OPEN_CFW_RTOS_TIMER_COMMAND_FAIL_STOP
#define OPEN_CFW_RTOS_TIMER_COMMAND_FAIL_STOP() \
    do { \
        ((open_cfw_rtos_timer_command_lock_function) \
            (open_cfw_rtos_timer_command_uintptr)0x005FA0A5U)(); \
        *(volatile unsigned int *) \
            (open_cfw_rtos_timer_command_uintptr) \
            (~(open_cfw_rtos_timer_command_uintptr)0U) = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

__attribute__((used, noinline))
unsigned int open_cfw_rtos_timer_command(
    const void *timer,
    int command_id,
    unsigned int optional_value,
    unsigned int *higher_priority_task_woken,
    unsigned int ticks_to_wait
)
{
    struct open_cfw_rtos_timer_command_message message;
    void *queue;

    if (timer == (const void *)0) {
        OPEN_CFW_RTOS_TIMER_COMMAND_FAIL_STOP();
        return 0U;
    }

    queue = OPEN_CFW_RTOS_TIMER_COMMAND_QUEUE();
    if (queue == (void *)0) {
        return 0U;
    }

    message.command_id = command_id;
    message.optional_value = optional_value;
    message.timer =
        (unsigned int)(open_cfw_rtos_timer_command_uintptr)timer;

    if (command_id < 6) {
        unsigned int effective_ticks_to_wait = 0U;

        if (OPEN_CFW_RTOS_TIMER_COMMAND_SCHEDULER_STATE() == 2U) {
            effective_ticks_to_wait = ticks_to_wait;
        }
        return OPEN_CFW_RTOS_TIMER_COMMAND_TASK_SEND(
            queue,
            &message,
            effective_ticks_to_wait,
            0U
        );
    }

    return OPEN_CFW_RTOS_TIMER_COMMAND_ISR_SEND(
        queue,
        &message,
        higher_priority_task_woken,
        0U
    );
}

#undef OPEN_CFW_RTOS_TIMER_COMMAND_FAIL_STOP
#undef OPEN_CFW_RTOS_TIMER_COMMAND_ISR_SEND
#undef OPEN_CFW_RTOS_TIMER_COMMAND_TASK_SEND
#undef OPEN_CFW_RTOS_TIMER_COMMAND_SCHEDULER_STATE
#undef OPEN_CFW_RTOS_TIMER_COMMAND_QUEUE
