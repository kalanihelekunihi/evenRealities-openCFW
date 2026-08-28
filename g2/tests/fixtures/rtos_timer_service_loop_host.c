/*
 * SPDX-License-Identifier: MIT
 */

unsigned int open_cfw_test_rtos_timer_service_loop_events[64];
unsigned int open_cfw_test_rtos_timer_service_loop_event_count;
unsigned int open_cfw_test_rtos_timer_service_loop_query_calls;
unsigned int open_cfw_test_rtos_timer_service_loop_wait_calls;
unsigned int open_cfw_test_rtos_timer_service_loop_command_calls;
unsigned int open_cfw_test_rtos_timer_service_loop_continue_calls;
unsigned int open_cfw_test_rtos_timer_service_loop_iteration_limit;
unsigned int open_cfw_test_rtos_timer_service_loop_expiries[16];
unsigned int open_cfw_test_rtos_timer_service_loop_empty_values[16];
unsigned int open_cfw_test_rtos_timer_service_loop_wait_expiries[16];
unsigned int open_cfw_test_rtos_timer_service_loop_wait_empty_values[16];

static void open_cfw_test_rtos_timer_service_loop_record(
    unsigned int event
)
{
    open_cfw_test_rtos_timer_service_loop_events[
        open_cfw_test_rtos_timer_service_loop_event_count++
    ] = event;
}

void open_cfw_test_rtos_timer_service_loop_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_service_loop_event_count = 0U;
    open_cfw_test_rtos_timer_service_loop_query_calls = 0U;
    open_cfw_test_rtos_timer_service_loop_wait_calls = 0U;
    open_cfw_test_rtos_timer_service_loop_command_calls = 0U;
    open_cfw_test_rtos_timer_service_loop_continue_calls = 0U;
    open_cfw_test_rtos_timer_service_loop_iteration_limit = 1U;
    for (index = 0U; index < 64U; ++index) {
        open_cfw_test_rtos_timer_service_loop_events[index] = 0U;
    }
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_rtos_timer_service_loop_expiries[index] = 0U;
        open_cfw_test_rtos_timer_service_loop_empty_values[index] = 0U;
        open_cfw_test_rtos_timer_service_loop_wait_expiries[index] = 0U;
        open_cfw_test_rtos_timer_service_loop_wait_empty_values[index] =
            0U;
    }
}

static unsigned int open_cfw_test_rtos_timer_service_loop_query(
    unsigned int *empty
)
{
    unsigned int index =
        open_cfw_test_rtos_timer_service_loop_query_calls;

    open_cfw_test_rtos_timer_service_loop_record(10U);
    *empty =
        open_cfw_test_rtos_timer_service_loop_empty_values[index];
    ++open_cfw_test_rtos_timer_service_loop_query_calls;
    return open_cfw_test_rtos_timer_service_loop_expiries[index];
}

static void open_cfw_test_rtos_timer_service_loop_wait(
    unsigned int expiry,
    unsigned int empty
)
{
    unsigned int index =
        open_cfw_test_rtos_timer_service_loop_wait_calls;

    open_cfw_test_rtos_timer_service_loop_record(20U);
    open_cfw_test_rtos_timer_service_loop_wait_expiries[index] = expiry;
    open_cfw_test_rtos_timer_service_loop_wait_empty_values[index] =
        empty;
    ++open_cfw_test_rtos_timer_service_loop_wait_calls;
}

static void open_cfw_test_rtos_timer_service_loop_commands(void)
{
    open_cfw_test_rtos_timer_service_loop_record(30U);
    ++open_cfw_test_rtos_timer_service_loop_command_calls;
}

static unsigned int open_cfw_test_rtos_timer_service_loop_continue(void)
{
    open_cfw_test_rtos_timer_service_loop_record(40U);
    ++open_cfw_test_rtos_timer_service_loop_continue_calls;
    return (
        open_cfw_test_rtos_timer_service_loop_continue_calls <
        open_cfw_test_rtos_timer_service_loop_iteration_limit
    );
}

#define OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_QUERY(empty) \
    open_cfw_test_rtos_timer_service_loop_query(empty)
#define OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_WAIT(expiry, empty) \
    open_cfw_test_rtos_timer_service_loop_wait(expiry, empty)
#define OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_COMMANDS() \
    open_cfw_test_rtos_timer_service_loop_commands()
#define OPEN_CFW_RTOS_TIMER_SERVICE_LOOP_CONTINUE() \
    open_cfw_test_rtos_timer_service_loop_continue()

#include "../../components/apollo_main/core_overlay/rtos_timer_service_loop.c"
