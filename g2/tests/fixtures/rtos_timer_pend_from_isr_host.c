/*
 * SPDX-License-Identifier: MIT
 */

typedef __UINTPTR_TYPE__ open_cfw_test_rtos_timer_pend_uintptr;

unsigned int open_cfw_test_rtos_timer_pend_events[8];
unsigned int open_cfw_test_rtos_timer_pend_event_count;
unsigned int open_cfw_test_rtos_timer_pend_queue_reads;
unsigned int open_cfw_test_rtos_timer_pend_send_calls;
open_cfw_test_rtos_timer_pend_uintptr
    open_cfw_test_rtos_timer_pend_queue_value;
open_cfw_test_rtos_timer_pend_uintptr
    open_cfw_test_rtos_timer_pend_last_queue;
open_cfw_test_rtos_timer_pend_uintptr
    open_cfw_test_rtos_timer_pend_last_function;
open_cfw_test_rtos_timer_pend_uintptr
    open_cfw_test_rtos_timer_pend_last_parameter;
open_cfw_test_rtos_timer_pend_uintptr
    open_cfw_test_rtos_timer_pend_last_woken;
int open_cfw_test_rtos_timer_pend_last_command;
unsigned int open_cfw_test_rtos_timer_pend_last_value;
unsigned int open_cfw_test_rtos_timer_pend_last_copy_position;
int open_cfw_test_rtos_timer_pend_send_result;

static void open_cfw_test_rtos_timer_pend_record(unsigned int event)
{
    open_cfw_test_rtos_timer_pend_events[
        open_cfw_test_rtos_timer_pend_event_count++
    ] = event;
}

void open_cfw_test_rtos_timer_pend_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_pend_event_count = 0U;
    open_cfw_test_rtos_timer_pend_queue_reads = 0U;
    open_cfw_test_rtos_timer_pend_send_calls = 0U;
    open_cfw_test_rtos_timer_pend_queue_value = 0U;
    open_cfw_test_rtos_timer_pend_last_queue = 0U;
    open_cfw_test_rtos_timer_pend_last_function = 0U;
    open_cfw_test_rtos_timer_pend_last_parameter = 0U;
    open_cfw_test_rtos_timer_pend_last_woken = 0U;
    open_cfw_test_rtos_timer_pend_last_command = 0;
    open_cfw_test_rtos_timer_pend_last_value = 0U;
    open_cfw_test_rtos_timer_pend_last_copy_position = 0U;
    open_cfw_test_rtos_timer_pend_send_result = 0;
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_rtos_timer_pend_events[index] = 0U;
    }
}

void open_cfw_test_rtos_timer_pend_set_queue(
    open_cfw_test_rtos_timer_pend_uintptr value
)
{
    open_cfw_test_rtos_timer_pend_queue_value = value;
}

void open_cfw_test_rtos_timer_pend_set_send_result(int value)
{
    open_cfw_test_rtos_timer_pend_send_result = value;
}

static void *open_cfw_test_rtos_timer_pend_read_queue(void)
{
    open_cfw_test_rtos_timer_pend_record(10U);
    ++open_cfw_test_rtos_timer_pend_queue_reads;
    return (void *)open_cfw_test_rtos_timer_pend_queue_value;
}

static int open_cfw_test_rtos_timer_pend_send(
    void *queue,
    const void *message_pointer,
    int *higher_priority_task_woken,
    unsigned int copy_position
);

#define OPEN_CFW_RTOS_TIMER_PEND_FROM_ISR_READ_QUEUE() \
    open_cfw_test_rtos_timer_pend_read_queue()
#define OPEN_CFW_RTOS_TIMER_PEND_FROM_ISR_SEND( \
    queue, message, higher_priority_task_woken, copy_position \
) \
    open_cfw_test_rtos_timer_pend_send( \
        (queue), \
        (message), \
        (higher_priority_task_woken), \
        (copy_position) \
    )

#include "../../components/apollo_main/core_overlay/rtos_timer_pend_from_isr.c"

static int open_cfw_test_rtos_timer_pend_send(
    void *queue,
    const void *message_pointer,
    int *higher_priority_task_woken,
    unsigned int copy_position
)
{
    const struct open_cfw_rtos_timer_pend_from_isr_message *message =
        (const struct open_cfw_rtos_timer_pend_from_isr_message *)
            message_pointer;

    open_cfw_test_rtos_timer_pend_record(20U);
    ++open_cfw_test_rtos_timer_pend_send_calls;
    open_cfw_test_rtos_timer_pend_last_queue =
        (open_cfw_test_rtos_timer_pend_uintptr)queue;
    open_cfw_test_rtos_timer_pend_last_command = message->command;
    open_cfw_test_rtos_timer_pend_last_function =
        (open_cfw_test_rtos_timer_pend_uintptr)message->function;
    open_cfw_test_rtos_timer_pend_last_parameter =
        (open_cfw_test_rtos_timer_pend_uintptr)message->parameter;
    open_cfw_test_rtos_timer_pend_last_value = message->value;
    open_cfw_test_rtos_timer_pend_last_woken =
        (open_cfw_test_rtos_timer_pend_uintptr)higher_priority_task_woken;
    open_cfw_test_rtos_timer_pend_last_copy_position = copy_position;
    return open_cfw_test_rtos_timer_pend_send_result;
}

int open_cfw_test_rtos_timer_pend_call(
    open_cfw_rtos_timer_pended_function function,
    void *parameter,
    unsigned int value,
    int *higher_priority_task_woken
)
{
    return open_cfw_rtos_timer_pend_from_isr(
        function,
        parameter,
        value,
        higher_priority_task_woken
    );
}
