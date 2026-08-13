/* SPDX-License-Identifier: GPL-3.0-only */

#include <stdint.h>
#include <string.h>

#include "../../components/shared/freertos/runtime_freertos_apollo_tickless_candidate.h"

volatile uint32_t open_cfw_retained_freertos_stimer_last_compare;
volatile uint32_t open_cfw_retained_freertos_stimer_counts_per_tick;
volatile uint32_t open_cfw_retained_freertos_stimer_max_suppressed_ticks;

uint32_t open_cfw_test_freertos_tickless_events[32];
uint32_t open_cfw_test_freertos_tickless_arguments[32];
uint32_t open_cfw_test_freertos_tickless_event_count;
int32_t open_cfw_test_freertos_tickless_confirm_status;
uint32_t open_cfw_test_freertos_tickless_pre_result;
uint32_t open_cfw_test_freertos_tickless_counters[2];
uint32_t open_cfw_test_freertos_tickless_counter_index;

static void open_cfw_test_freertos_tickless_note(
    uint32_t event,
    uint32_t argument
)
{
    uint32_t index = open_cfw_test_freertos_tickless_event_count++;
    open_cfw_test_freertos_tickless_events[index] = event;
    open_cfw_test_freertos_tickless_arguments[index] = argument;
}

void open_cfw_retained_freertos_global_interrupt_disable(void)
{
    open_cfw_test_freertos_tickless_note(1U, 0U);
}

void open_cfw_retained_freertos_global_interrupt_enable(void)
{
    open_cfw_test_freertos_tickless_note(11U, 0U);
}

int open_cfw_retained_freertos_confirm_sleep_mode_status(void)
{
    open_cfw_test_freertos_tickless_note(2U, 0U);
    return open_cfw_test_freertos_tickless_confirm_status;
}

uint32_t open_cfw_retained_freertos_stimer_counter_get(void)
{
    uint32_t value = open_cfw_test_freertos_tickless_counters[
        open_cfw_test_freertos_tickless_counter_index++
    ];
    open_cfw_test_freertos_tickless_note(3U, value);
    return value;
}

void open_cfw_retained_freertos_stimer_compare_delta_set(
    uint32_t compare,
    uint32_t delta
)
{
    open_cfw_test_freertos_tickless_note(4U, compare);
    open_cfw_test_freertos_tickless_note(5U, delta);
}

uint32_t open_cfw_retained_freertos_pre_sleep_processing(uint32_t ticks)
{
    open_cfw_test_freertos_tickless_note(6U, ticks);
    return open_cfw_test_freertos_tickless_pre_result;
}

void open_cfw_retained_freertos_wait_for_interrupt(void)
{
    open_cfw_test_freertos_tickless_note(7U, 0U);
}

void open_cfw_retained_freertos_post_sleep_processing(uint32_t ticks)
{
    open_cfw_test_freertos_tickless_note(8U, ticks);
}

void open_cfw_retained_freertos_stimer_interrupt_clear(uint32_t interrupts)
{
    open_cfw_test_freertos_tickless_note(9U, interrupts);
}

void open_cfw_retained_freertos_nvic_pending_clear(uint32_t interrupt)
{
    open_cfw_test_freertos_tickless_note(10U, interrupt);
}

void open_cfw_freertos_task_step_tick(uint32_t ticks)
{
    open_cfw_test_freertos_tickless_note(12U, ticks);
}

#include "../../components/shared/freertos/runtime_freertos_apollo_tickless_candidate.c"

void open_cfw_test_freertos_tickless_reset(
    uint32_t last_compare,
    uint32_t counts_per_tick,
    uint32_t max_suppressed_ticks,
    int32_t confirm_status,
    uint32_t pre_result,
    uint32_t before_counter,
    uint32_t after_counter
)
{
    memset(open_cfw_test_freertos_tickless_events, 0,
           sizeof(open_cfw_test_freertos_tickless_events));
    memset(open_cfw_test_freertos_tickless_arguments, 0,
           sizeof(open_cfw_test_freertos_tickless_arguments));
    open_cfw_test_freertos_tickless_event_count = 0U;
    open_cfw_test_freertos_tickless_confirm_status = confirm_status;
    open_cfw_test_freertos_tickless_pre_result = pre_result;
    open_cfw_test_freertos_tickless_counters[0] = before_counter;
    open_cfw_test_freertos_tickless_counters[1] = after_counter;
    open_cfw_test_freertos_tickless_counter_index = 0U;
    open_cfw_retained_freertos_stimer_last_compare = last_compare;
    open_cfw_retained_freertos_stimer_counts_per_tick = counts_per_tick;
    open_cfw_retained_freertos_stimer_max_suppressed_ticks =
        max_suppressed_ticks;
}
