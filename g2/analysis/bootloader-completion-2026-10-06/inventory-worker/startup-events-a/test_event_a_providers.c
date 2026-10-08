/* SPDX-License-Identifier: MIT. Test-only cuts for unresolved lower helpers. */
#include "startup_events_a.h"

volatile uint32_t event_a_test_temperature_calls;
volatile uint32_t event_a_test_temperature_args[4];
volatile uint32_t event_a_test_sequence_calls;
volatile uint32_t event_a_test_sequence_args[2];
volatile uint32_t event_a_test_sequence_status;
volatile uint32_t event_a_test_sequence_selector;
volatile uint32_t event_a_test_dispatch_calls;
volatile uint32_t event_a_test_dispatch_args[4];

void event_a_temperature_transition_separate(uint32_t new_major,
    uint32_t old_major, uint32_t new_minor, uint32_t old_minor)
{
    event_a_test_temperature_calls++;
    event_a_test_temperature_args[0] = new_major;
    event_a_test_temperature_args[1] = old_major;
    event_a_test_temperature_args[2] = new_minor;
    event_a_test_temperature_args[3] = old_minor;
}

uint32_t event_a_state_transition_sequence(uint32_t from_state,
    uint32_t to_state, uint8_t *selector)
{
    event_a_test_sequence_calls++;
    event_a_test_sequence_args[0] = from_state;
    event_a_test_sequence_args[1] = to_state;
    *selector = (uint8_t)event_a_test_sequence_selector;
    return event_a_test_sequence_status;
}

void event_a_test_dispatch_target(uint32_t new_major, uint32_t middle_major,
    uint32_t new_minor, uint32_t old_minor)
{
    event_a_test_dispatch_calls++;
    event_a_test_dispatch_args[0] = new_major;
    event_a_test_dispatch_args[1] = middle_major;
    event_a_test_dispatch_args[2] = new_minor;
    event_a_test_dispatch_args[3] = old_minor;
}
