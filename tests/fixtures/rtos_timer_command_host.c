/*
 * SPDX-License-Identifier: GPL-3.0-only
 */

typedef __UINTPTR_TYPE__ open_cfw_test_rtos_timer_command_uintptr;

unsigned int open_cfw_test_rtos_timer_command_events[16];
unsigned int open_cfw_test_rtos_timer_command_event_count;
unsigned int open_cfw_test_rtos_timer_command_queue_load_calls;
unsigned int open_cfw_test_rtos_timer_command_scheduler_calls;
unsigned int open_cfw_test_rtos_timer_command_task_send_calls;
unsigned int open_cfw_test_rtos_timer_command_isr_send_calls;
unsigned int open_cfw_test_rtos_timer_command_fail_stop_calls;
unsigned int open_cfw_test_rtos_timer_command_scheduler_state;
unsigned int open_cfw_test_rtos_timer_command_task_result;
unsigned int open_cfw_test_rtos_timer_command_isr_result;
unsigned int open_cfw_test_rtos_timer_command_message[3];
unsigned int open_cfw_test_rtos_timer_command_ticks_to_wait;
unsigned int open_cfw_test_rtos_timer_command_copy_position;
void *open_cfw_test_rtos_timer_command_queue;
void *open_cfw_test_rtos_timer_command_observed_queue;
unsigned int *open_cfw_test_rtos_timer_command_higher_priority_task_woken;

static void open_cfw_test_rtos_timer_command_record(unsigned int event)
{
    open_cfw_test_rtos_timer_command_events[
        open_cfw_test_rtos_timer_command_event_count++
    ] = event;
}

void open_cfw_test_rtos_timer_command_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_command_event_count = 0U;
    open_cfw_test_rtos_timer_command_queue_load_calls = 0U;
    open_cfw_test_rtos_timer_command_scheduler_calls = 0U;
    open_cfw_test_rtos_timer_command_task_send_calls = 0U;
    open_cfw_test_rtos_timer_command_isr_send_calls = 0U;
    open_cfw_test_rtos_timer_command_fail_stop_calls = 0U;
    open_cfw_test_rtos_timer_command_scheduler_state = 2U;
    open_cfw_test_rtos_timer_command_task_result = 0U;
    open_cfw_test_rtos_timer_command_isr_result = 0U;
    open_cfw_test_rtos_timer_command_ticks_to_wait = 0U;
    open_cfw_test_rtos_timer_command_copy_position = 0U;
    open_cfw_test_rtos_timer_command_queue = (void *)0;
    open_cfw_test_rtos_timer_command_observed_queue = (void *)0;
    open_cfw_test_rtos_timer_command_higher_priority_task_woken =
        (unsigned int *)0;
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_rtos_timer_command_events[index] = 0U;
    }
    for (index = 0U; index < 3U; ++index) {
        open_cfw_test_rtos_timer_command_message[index] = 0U;
    }
}

static void *open_cfw_test_rtos_timer_command_load_queue(void)
{
    open_cfw_test_rtos_timer_command_record(1U);
    ++open_cfw_test_rtos_timer_command_queue_load_calls;
    return open_cfw_test_rtos_timer_command_queue;
}

static unsigned int open_cfw_test_rtos_timer_command_scheduler(void)
{
    open_cfw_test_rtos_timer_command_record(2U);
    ++open_cfw_test_rtos_timer_command_scheduler_calls;
    return open_cfw_test_rtos_timer_command_scheduler_state;
}

static void open_cfw_test_rtos_timer_command_copy_message(
    const void *message
)
{
    const unsigned int *words = (const unsigned int *)message;

    open_cfw_test_rtos_timer_command_message[0] = words[0];
    open_cfw_test_rtos_timer_command_message[1] = words[1];
    open_cfw_test_rtos_timer_command_message[2] = words[2];
}

static unsigned int open_cfw_test_rtos_timer_command_task_send(
    void *queue,
    const void *message,
    unsigned int ticks_to_wait,
    unsigned int copy_position
)
{
    open_cfw_test_rtos_timer_command_record(3U);
    ++open_cfw_test_rtos_timer_command_task_send_calls;
    open_cfw_test_rtos_timer_command_observed_queue = queue;
    open_cfw_test_rtos_timer_command_copy_message(message);
    open_cfw_test_rtos_timer_command_ticks_to_wait = ticks_to_wait;
    open_cfw_test_rtos_timer_command_copy_position = copy_position;
    return open_cfw_test_rtos_timer_command_task_result;
}

static unsigned int open_cfw_test_rtos_timer_command_isr_send(
    void *queue,
    const void *message,
    unsigned int *higher_priority_task_woken,
    unsigned int copy_position
)
{
    open_cfw_test_rtos_timer_command_record(4U);
    ++open_cfw_test_rtos_timer_command_isr_send_calls;
    open_cfw_test_rtos_timer_command_observed_queue = queue;
    open_cfw_test_rtos_timer_command_copy_message(message);
    open_cfw_test_rtos_timer_command_higher_priority_task_woken =
        higher_priority_task_woken;
    open_cfw_test_rtos_timer_command_copy_position = copy_position;
    return open_cfw_test_rtos_timer_command_isr_result;
}

static void open_cfw_test_rtos_timer_command_fail_stop(void)
{
    open_cfw_test_rtos_timer_command_record(40U);
    ++open_cfw_test_rtos_timer_command_fail_stop_calls;
}

#define OPEN_CFW_RTOS_TIMER_COMMAND_QUEUE() \
    open_cfw_test_rtos_timer_command_load_queue()
#define OPEN_CFW_RTOS_TIMER_COMMAND_SCHEDULER_STATE() \
    open_cfw_test_rtos_timer_command_scheduler()
#define OPEN_CFW_RTOS_TIMER_COMMAND_TASK_SEND( \
    queue, message, ticks_to_wait, copy_position \
) \
    open_cfw_test_rtos_timer_command_task_send( \
        queue, message, ticks_to_wait, copy_position \
    )
#define OPEN_CFW_RTOS_TIMER_COMMAND_ISR_SEND( \
    queue, message, higher_priority_task_woken, copy_position \
) \
    open_cfw_test_rtos_timer_command_isr_send( \
        queue, message, higher_priority_task_woken, copy_position \
    )
#define OPEN_CFW_RTOS_TIMER_COMMAND_FAIL_STOP() \
    open_cfw_test_rtos_timer_command_fail_stop()

#include "../../components/apollo_main/core_overlay/rtos_timer_command.c"
