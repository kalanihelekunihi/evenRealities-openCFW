/*
 * SPDX-License-Identifier: MIT
 *
 * Host oracle for the source-owned FreeRTOS private queue-state helpers.
 */

static void open_cfw_test_queue_state_enter_critical(void);
static void open_cfw_test_queue_state_exit_critical(void);

#define OPEN_CFW_FREERTOS_QUEUE_STATE_ENTER_CRITICAL() \
    open_cfw_test_queue_state_enter_critical()
#define OPEN_CFW_FREERTOS_QUEUE_STATE_EXIT_CRITICAL() \
    open_cfw_test_queue_state_exit_critical()

#include \
    "../../components/apollo_main/core_overlay/runtime_freertos_queue_state.c"

enum {
    OPEN_CFW_TEST_QUEUE_STATE_EVENT_ENTER = 1,
    OPEN_CFW_TEST_QUEUE_STATE_EVENT_EXIT = 2,
    OPEN_CFW_TEST_QUEUE_STATE_EVENT_CAPACITY = 8
};

unsigned int open_cfw_test_queue_state_event_count;
unsigned int open_cfw_test_queue_state_events[
    OPEN_CFW_TEST_QUEUE_STATE_EVENT_CAPACITY
];
unsigned int open_cfw_test_queue_state_critical_depth;
unsigned int open_cfw_test_queue_state_max_critical_depth;
unsigned int open_cfw_test_queue_state_mutate_on_enter;
unsigned int open_cfw_test_queue_state_mutated_messages;

static struct open_cfw_queue_state_control
open_cfw_test_queue_state_control;

static void open_cfw_test_queue_state_log(unsigned int event)
{
    unsigned int index = open_cfw_test_queue_state_event_count;

    if (index < OPEN_CFW_TEST_QUEUE_STATE_EVENT_CAPACITY) {
        open_cfw_test_queue_state_events[index] = event;
    }
    open_cfw_test_queue_state_event_count = index + 1U;
}

static void open_cfw_test_queue_state_enter_critical(void)
{
    open_cfw_test_queue_state_critical_depth++;
    if (
        open_cfw_test_queue_state_critical_depth >
        open_cfw_test_queue_state_max_critical_depth
    ) {
        open_cfw_test_queue_state_max_critical_depth =
            open_cfw_test_queue_state_critical_depth;
    }
    open_cfw_test_queue_state_log(
        OPEN_CFW_TEST_QUEUE_STATE_EVENT_ENTER
    );
    if (open_cfw_test_queue_state_mutate_on_enter != 0U) {
        open_cfw_test_queue_state_control.messages_waiting =
            open_cfw_test_queue_state_mutated_messages;
    }
}

static void open_cfw_test_queue_state_exit_critical(void)
{
    open_cfw_test_queue_state_log(
        OPEN_CFW_TEST_QUEUE_STATE_EVENT_EXIT
    );
    open_cfw_test_queue_state_critical_depth--;
}

void open_cfw_test_queue_state_reset(
    unsigned int messages_waiting,
    unsigned int length
)
{
    unsigned int index;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_QUEUE_STATE_EVENT_CAPACITY;
        ++index
    ) {
        open_cfw_test_queue_state_events[index] = 0U;
    }
    open_cfw_test_queue_state_event_count = 0U;
    open_cfw_test_queue_state_critical_depth = 0U;
    open_cfw_test_queue_state_max_critical_depth = 0U;
    open_cfw_test_queue_state_mutate_on_enter = 0U;
    open_cfw_test_queue_state_mutated_messages = 0U;
    open_cfw_test_queue_state_control.messages_waiting =
        messages_waiting;
    open_cfw_test_queue_state_control.length = length;
}

void open_cfw_test_queue_state_set_enter_mutation(
    unsigned int enabled,
    unsigned int messages_waiting
)
{
    open_cfw_test_queue_state_mutate_on_enter = enabled;
    open_cfw_test_queue_state_mutated_messages = messages_waiting;
}

void *open_cfw_test_queue_state_pointer(void)
{
    return &open_cfw_test_queue_state_control;
}
