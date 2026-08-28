/*
 * SPDX-License-Identifier: MIT
 *
 * RTOS event-group clear-from-ISR submission wrapper matched to stock entry
 * 0x0047ED52.
 */

typedef void (*open_cfw_rtos_event_group_clear_from_isr_callback)(
    void *parameter,
    unsigned int value
);

void open_cfw_rtos_event_group_clear_callback(
    void *group,
    unsigned int bits_to_clear
);

int open_cfw_rtos_timer_pend_from_isr(
    open_cfw_rtos_event_group_clear_from_isr_callback function,
    void *parameter,
    unsigned int value,
    int *higher_priority_task_woken
);

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_FROM_ISR_PEND
#define OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_FROM_ISR_PEND( \
    function, parameter, value, higher_priority_task_woken \
) \
    open_cfw_rtos_timer_pend_from_isr( \
        (function), \
        (parameter), \
        (value), \
        (higher_priority_task_woken) \
    )
#endif

__attribute__((used, noinline))
int open_cfw_rtos_event_group_clear_from_isr(
    void *group,
    unsigned int bits_to_clear
)
{
    open_cfw_rtos_event_group_clear_from_isr_callback callback =
        open_cfw_rtos_event_group_clear_callback;

    return OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_FROM_ISR_PEND(
        callback,
        group,
        bits_to_clear,
        (int *)0
    );
}

#undef OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_FROM_ISR_PEND
