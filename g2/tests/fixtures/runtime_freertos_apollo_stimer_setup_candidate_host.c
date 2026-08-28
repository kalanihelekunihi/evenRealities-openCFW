/* SPDX-License-Identifier: MIT */

#include <stdint.h>
#include <string.h>

#include "../../components/shared/freertos/runtime_freertos_apollo_stimer_setup_candidate.h"

volatile open_cfw_freertos_stimer_u32
    open_cfw_retained_freertos_stimer_last_compare;
volatile open_cfw_freertos_stimer_u32
    open_cfw_retained_freertos_stimer_counts_per_tick;
volatile open_cfw_freertos_stimer_u32
    open_cfw_retained_freertos_stimer_max_suppressed_ticks;

uint32_t open_cfw_test_freertos_stimer_events[12];
uint32_t open_cfw_test_freertos_stimer_event_count;
uint32_t open_cfw_test_freertos_stimer_arguments[12];
uint32_t open_cfw_test_freertos_stimer_saved_configuration;
uint32_t open_cfw_test_freertos_stimer_counter;

static void open_cfw_test_freertos_stimer_note(
    uint32_t event,
    uint32_t argument
)
{
    uint32_t index = open_cfw_test_freertos_stimer_event_count++;
    open_cfw_test_freertos_stimer_events[index] = event;
    open_cfw_test_freertos_stimer_arguments[index] = argument;
}

void open_cfw_retained_freertos_stimer_interrupt_enable(uint32_t interrupts)
{
    open_cfw_test_freertos_stimer_note(1U, interrupts);
}

void open_cfw_retained_freertos_nvic_priority_set(
    uint32_t interrupt,
    uint32_t priority
)
{
    open_cfw_test_freertos_stimer_note(2U, interrupt);
    open_cfw_test_freertos_stimer_note(3U, priority);
}

void open_cfw_retained_freertos_nvic_enable(uint32_t interrupt)
{
    open_cfw_test_freertos_stimer_note(4U, interrupt);
}

uint32_t open_cfw_retained_freertos_stimer_config(uint32_t configuration)
{
    open_cfw_test_freertos_stimer_note(5U, configuration);
    return open_cfw_test_freertos_stimer_saved_configuration;
}

uint32_t open_cfw_retained_freertos_stimer_counter_get(void)
{
    open_cfw_test_freertos_stimer_note(6U, 0U);
    return open_cfw_test_freertos_stimer_counter;
}

void open_cfw_retained_freertos_stimer_compare_delta_set(
    uint32_t compare,
    uint32_t delta
)
{
    open_cfw_test_freertos_stimer_note(7U, compare);
    open_cfw_test_freertos_stimer_note(8U, delta);
}

#include "../../components/shared/freertos/runtime_freertos_apollo_stimer_setup_candidate.c"

void open_cfw_test_freertos_stimer_reset(
    uint32_t saved_configuration,
    uint32_t counter
)
{
    memset(open_cfw_test_freertos_stimer_events, 0,
           sizeof(open_cfw_test_freertos_stimer_events));
    memset(open_cfw_test_freertos_stimer_arguments, 0,
           sizeof(open_cfw_test_freertos_stimer_arguments));
    open_cfw_test_freertos_stimer_event_count = 0U;
    open_cfw_test_freertos_stimer_saved_configuration = saved_configuration;
    open_cfw_test_freertos_stimer_counter = counter;
    open_cfw_retained_freertos_stimer_last_compare = 0U;
    open_cfw_retained_freertos_stimer_counts_per_tick = 0U;
    open_cfw_retained_freertos_stimer_max_suppressed_ticks = 0U;
}
