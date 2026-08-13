/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * RTOS timer pended-callback ISR submission matched to stock entry
 * 0x0047EB4A.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtos_timer_pend_from_isr_uintptr;

typedef void (*open_cfw_rtos_timer_pended_function)(
    void *parameter,
    unsigned int value
);

typedef int (*open_cfw_rtos_timer_pend_from_isr_send_function)(
    void *queue,
    const void *message,
    int *higher_priority_task_woken,
    unsigned int copy_position
);

struct open_cfw_rtos_timer_pend_from_isr_message {
    int command;
    open_cfw_rtos_timer_pended_function function;
    void *parameter;
    unsigned int value;
};

#ifndef OPEN_CFW_RTOS_TIMER_PEND_FROM_ISR_READ_QUEUE
#define OPEN_CFW_RTOS_TIMER_PEND_FROM_ISR_READ_QUEUE() \
    (*(void *volatile *) \
        (open_cfw_rtos_timer_pend_from_isr_uintptr)0x20074AB0U)
#endif

#ifndef OPEN_CFW_RTOS_TIMER_PEND_FROM_ISR_SEND
#define OPEN_CFW_RTOS_TIMER_PEND_FROM_ISR_SEND( \
    queue, message, higher_priority_task_woken, copy_position \
) \
    (((open_cfw_rtos_timer_pend_from_isr_send_function) \
        (open_cfw_rtos_timer_pend_from_isr_uintptr)0x00441953U)( \
            (queue), \
            (message), \
            (higher_priority_task_woken), \
            (copy_position)))
#endif

__attribute__((used, noinline))
int open_cfw_rtos_timer_pend_from_isr(
    open_cfw_rtos_timer_pended_function function,
    void *parameter,
    unsigned int value,
    int *higher_priority_task_woken
)
{
    struct open_cfw_rtos_timer_pend_from_isr_message message;
    void *queue;

    message.command = -2;
    message.function = function;
    message.parameter = parameter;
    message.value = value;
    queue = OPEN_CFW_RTOS_TIMER_PEND_FROM_ISR_READ_QUEUE();
    return OPEN_CFW_RTOS_TIMER_PEND_FROM_ISR_SEND(
        queue,
        &message,
        higher_priority_task_woken,
        0U
    );
}

#undef OPEN_CFW_RTOS_TIMER_PEND_FROM_ISR_SEND
#undef OPEN_CFW_RTOS_TIMER_PEND_FROM_ISR_READ_QUEUE
