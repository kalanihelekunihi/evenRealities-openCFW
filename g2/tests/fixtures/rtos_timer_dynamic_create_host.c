/*
 * SPDX-License-Identifier: MIT
 */

typedef __UINTPTR_TYPE__ open_cfw_test_rtos_timer_dynamic_uintptr;

unsigned int open_cfw_test_rtos_timer_dynamic_events[8];
unsigned int open_cfw_test_rtos_timer_dynamic_event_count;
unsigned int open_cfw_test_rtos_timer_dynamic_allocate_calls;
unsigned int open_cfw_test_rtos_timer_dynamic_allocate_size;
unsigned int open_cfw_test_rtos_timer_dynamic_initialize_calls;
open_cfw_test_rtos_timer_dynamic_uintptr
    open_cfw_test_rtos_timer_dynamic_initialize_fields[6];
unsigned int open_cfw_test_rtos_timer_dynamic_enabled;
unsigned char open_cfw_test_rtos_timer_dynamic_object[44];
unsigned char open_cfw_test_rtos_timer_dynamic_byte40_at_initialize;

static void open_cfw_test_rtos_timer_dynamic_record(unsigned int event)
{
    open_cfw_test_rtos_timer_dynamic_events[
        open_cfw_test_rtos_timer_dynamic_event_count++
    ] = event;
}

void open_cfw_test_rtos_timer_dynamic_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_dynamic_event_count = 0U;
    open_cfw_test_rtos_timer_dynamic_allocate_calls = 0U;
    open_cfw_test_rtos_timer_dynamic_allocate_size = 0U;
    open_cfw_test_rtos_timer_dynamic_initialize_calls = 0U;
    open_cfw_test_rtos_timer_dynamic_enabled = 0U;
    open_cfw_test_rtos_timer_dynamic_byte40_at_initialize = 0U;
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_rtos_timer_dynamic_events[index] = 0U;
    }
    for (index = 0U; index < 6U; ++index) {
        open_cfw_test_rtos_timer_dynamic_initialize_fields[index] = 0U;
    }
    for (index = 0U; index < 44U; ++index) {
        open_cfw_test_rtos_timer_dynamic_object[index] = 0xA5U;
    }
}

static void *open_cfw_test_rtos_timer_dynamic_allocate(unsigned int size)
{
    open_cfw_test_rtos_timer_dynamic_record(1U);
    ++open_cfw_test_rtos_timer_dynamic_allocate_calls;
    open_cfw_test_rtos_timer_dynamic_allocate_size = size;
    if (open_cfw_test_rtos_timer_dynamic_enabled == 0U) {
        return (void *)0;
    }
    return open_cfw_test_rtos_timer_dynamic_object;
}

static void open_cfw_test_rtos_timer_dynamic_initialize(
    const void *name,
    unsigned int period_ticks,
    unsigned int periodic,
    const void *callback_context,
    const void *callback,
    void *object
)
{
    open_cfw_test_rtos_timer_dynamic_record(2U);
    ++open_cfw_test_rtos_timer_dynamic_initialize_calls;
    open_cfw_test_rtos_timer_dynamic_byte40_at_initialize =
        ((unsigned char *)object)[0x28U];
    open_cfw_test_rtos_timer_dynamic_initialize_fields[0] =
        (open_cfw_test_rtos_timer_dynamic_uintptr)name;
    open_cfw_test_rtos_timer_dynamic_initialize_fields[1] = period_ticks;
    open_cfw_test_rtos_timer_dynamic_initialize_fields[2] = periodic;
    open_cfw_test_rtos_timer_dynamic_initialize_fields[3] =
        (open_cfw_test_rtos_timer_dynamic_uintptr)callback_context;
    open_cfw_test_rtos_timer_dynamic_initialize_fields[4] =
        (open_cfw_test_rtos_timer_dynamic_uintptr)callback;
    open_cfw_test_rtos_timer_dynamic_initialize_fields[5] =
        (open_cfw_test_rtos_timer_dynamic_uintptr)object;
}

#define OPEN_CFW_RTOS_TIMER_DYNAMIC_ALLOCATE(size) \
    open_cfw_test_rtos_timer_dynamic_allocate(size)
#define OPEN_CFW_RTOS_TIMER_DYNAMIC_INITIALIZE(...) \
    open_cfw_test_rtos_timer_dynamic_initialize(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/rtos_timer_dynamic_create.c"
