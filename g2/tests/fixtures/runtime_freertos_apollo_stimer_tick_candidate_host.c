/* SPDX-License-Identifier: MIT */

#include <stdint.h>
#include <string.h>

#include "../../components/shared/freertos/runtime_freertos_apollo_stimer_tick_candidate.h"

volatile uint32_t open_cfw_retained_freertos_stimer_last_compare;
volatile uint32_t open_cfw_retained_freertos_stimer_counts_per_tick;
volatile uint32_t open_cfw_retained_freertos_interrupt_control_state;

uint32_t open_cfw_test_freertos_stimer_tick_events[64];
uint32_t open_cfw_test_freertos_stimer_tick_arguments[64];
uint32_t open_cfw_test_freertos_stimer_tick_event_count;
uint32_t open_cfw_test_freertos_stimer_tick_counter;
uint32_t open_cfw_test_freertos_stimer_tick_status;
uint32_t open_cfw_test_freertos_stimer_tick_results[32];
uint32_t open_cfw_test_freertos_stimer_tick_result_count;
uint32_t open_cfw_test_freertos_stimer_tick_result_index;

static void open_cfw_test_freertos_stimer_tick_note(
    uint32_t event,
    uint32_t argument
)
{
    uint32_t index = open_cfw_test_freertos_stimer_tick_event_count++;
    open_cfw_test_freertos_stimer_tick_events[index] = event;
    open_cfw_test_freertos_stimer_tick_arguments[index] = argument;
}

uint32_t open_cfw_retained_freertos_stimer_counter_get(void)
{
    open_cfw_test_freertos_stimer_tick_note(1U, 0U);
    return open_cfw_test_freertos_stimer_tick_counter;
}

void open_cfw_retained_freertos_stimer_compare_delta_set(
    uint32_t compare,
    uint32_t delta
)
{
    open_cfw_test_freertos_stimer_tick_note(2U, compare);
    open_cfw_test_freertos_stimer_tick_note(3U, delta);
}

uint32_t open_cfw_retained_freertos_interrupt_mask_set(void)
{
    open_cfw_test_freertos_stimer_tick_note(4U, 0U);
    return 0xA5U;
}

void open_cfw_retained_freertos_interrupt_mask_clear(uint32_t mask)
{
    open_cfw_test_freertos_stimer_tick_note(6U, mask);
}

int open_cfw_freertos_task_increment_tick(void)
{
    uint32_t result = 0U;
    if (open_cfw_test_freertos_stimer_tick_result_index <
        open_cfw_test_freertos_stimer_tick_result_count) {
        result = open_cfw_test_freertos_stimer_tick_results[
            open_cfw_test_freertos_stimer_tick_result_index
        ];
    }
    open_cfw_test_freertos_stimer_tick_result_index++;
    open_cfw_test_freertos_stimer_tick_note(5U, result);
    return (int)result;
}

uint32_t open_cfw_retained_freertos_stimer_interrupt_status_get(
    uint32_t enabled_only
)
{
    open_cfw_test_freertos_stimer_tick_note(7U, enabled_only);
    return open_cfw_test_freertos_stimer_tick_status;
}

void open_cfw_retained_freertos_stimer_interrupt_clear(uint32_t interrupts)
{
    open_cfw_test_freertos_stimer_tick_note(8U, interrupts);
}

#include "../../components/shared/freertos/runtime_freertos_apollo_stimer_tick_candidate.c"

void open_cfw_test_freertos_stimer_tick_reset(
    uint32_t last_compare,
    uint32_t counts_per_tick,
    uint32_t counter,
    uint32_t status
)
{
    memset(open_cfw_test_freertos_stimer_tick_events, 0,
           sizeof(open_cfw_test_freertos_stimer_tick_events));
    memset(open_cfw_test_freertos_stimer_tick_arguments, 0,
           sizeof(open_cfw_test_freertos_stimer_tick_arguments));
    memset(open_cfw_test_freertos_stimer_tick_results, 0,
           sizeof(open_cfw_test_freertos_stimer_tick_results));
    open_cfw_test_freertos_stimer_tick_event_count = 0U;
    open_cfw_test_freertos_stimer_tick_counter = counter;
    open_cfw_test_freertos_stimer_tick_status = status;
    open_cfw_test_freertos_stimer_tick_result_count = 0U;
    open_cfw_test_freertos_stimer_tick_result_index = 0U;
    open_cfw_retained_freertos_stimer_last_compare = last_compare;
    open_cfw_retained_freertos_stimer_counts_per_tick = counts_per_tick;
    open_cfw_retained_freertos_interrupt_control_state = 0U;
}

void open_cfw_test_freertos_stimer_tick_set_result(
    uint32_t index,
    uint32_t result
)
{
    open_cfw_test_freertos_stimer_tick_results[index] = result;
    if (open_cfw_test_freertos_stimer_tick_result_count <= index) {
        open_cfw_test_freertos_stimer_tick_result_count = index + 1U;
    }
}
