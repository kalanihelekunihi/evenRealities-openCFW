/*
 * SPDX-License-Identifier: MIT
 *
 * RTOS event-group set-from-ISR submission wrapper matched to stock entry
 * 0x0047EE4A.
 */

typedef void (*open_cfw_rtos_event_group_set_from_isr_callback)(
    void *parameter,
    unsigned int value
);

void open_cfw_rtos_event_group_set_callback(
    void *group,
    unsigned int bits_to_set
);

int open_cfw_rtos_timer_pend_from_isr(
    open_cfw_rtos_event_group_set_from_isr_callback function,
    void *parameter,
    unsigned int value,
    int *higher_priority_task_woken
);

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_SET_FROM_ISR_PEND
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_FROM_ISR_PEND( \
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
int open_cfw_rtos_event_group_set_from_isr(
    void *group,
    unsigned int bits_to_set,
    int *higher_priority_task_woken
)
{
    open_cfw_rtos_event_group_set_from_isr_callback callback =
        open_cfw_rtos_event_group_set_callback;

    return OPEN_CFW_RTOS_EVENT_GROUP_SET_FROM_ISR_PEND(
        callback,
        group,
        bits_to_set,
        higher_priority_task_woken
    );
}

#undef OPEN_CFW_RTOS_EVENT_GROUP_SET_FROM_ISR_PEND
