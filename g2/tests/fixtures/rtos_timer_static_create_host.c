/*
 * SPDX-License-Identifier: GPL-3.0-only
 */

typedef __UINTPTR_TYPE__ open_cfw_test_rtos_timer_static_uintptr;

unsigned int open_cfw_test_rtos_timer_static_events[8];
unsigned int open_cfw_test_rtos_timer_static_event_count;
unsigned int open_cfw_test_rtos_timer_static_object_size;
unsigned int open_cfw_test_rtos_timer_static_fail_stop_calls;
unsigned int open_cfw_test_rtos_timer_static_initialize_calls;
open_cfw_test_rtos_timer_static_uintptr
    open_cfw_test_rtos_timer_static_initialize_fields[6];
unsigned char open_cfw_test_rtos_timer_static_object[44];
unsigned char open_cfw_test_rtos_timer_static_byte40_at_initialize;

static void open_cfw_test_rtos_timer_static_record(unsigned int event)
{
    open_cfw_test_rtos_timer_static_events[
        open_cfw_test_rtos_timer_static_event_count++
    ] = event;
}

void open_cfw_test_rtos_timer_static_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_static_event_count = 0U;
    open_cfw_test_rtos_timer_static_object_size = 44U;
    open_cfw_test_rtos_timer_static_fail_stop_calls = 0U;
    open_cfw_test_rtos_timer_static_initialize_calls = 0U;
    open_cfw_test_rtos_timer_static_byte40_at_initialize = 0U;
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_rtos_timer_static_events[index] = 0U;
    }
    for (index = 0U; index < 6U; ++index) {
        open_cfw_test_rtos_timer_static_initialize_fields[index] = 0U;
    }
    for (index = 0U; index < 44U; ++index) {
        open_cfw_test_rtos_timer_static_object[index] = 0xA5U;
    }
}

static void open_cfw_test_rtos_timer_static_fail_stop(void)
{
    open_cfw_test_rtos_timer_static_record(1U);
    ++open_cfw_test_rtos_timer_static_fail_stop_calls;
}

static void open_cfw_test_rtos_timer_static_initialize(
    const void *name,
    unsigned int period_ticks,
    unsigned int periodic,
    const void *callback_context,
    const void *callback,
    void *object
)
{
    open_cfw_test_rtos_timer_static_record(2U);
    ++open_cfw_test_rtos_timer_static_initialize_calls;
    open_cfw_test_rtos_timer_static_byte40_at_initialize =
        ((unsigned char *)object)[0x28U];
    open_cfw_test_rtos_timer_static_initialize_fields[0] =
        (open_cfw_test_rtos_timer_static_uintptr)name;
    open_cfw_test_rtos_timer_static_initialize_fields[1] = period_ticks;
    open_cfw_test_rtos_timer_static_initialize_fields[2] = periodic;
    open_cfw_test_rtos_timer_static_initialize_fields[3] =
        (open_cfw_test_rtos_timer_static_uintptr)callback_context;
    open_cfw_test_rtos_timer_static_initialize_fields[4] =
        (open_cfw_test_rtos_timer_static_uintptr)callback;
    open_cfw_test_rtos_timer_static_initialize_fields[5] =
        (open_cfw_test_rtos_timer_static_uintptr)object;
}

#define OPEN_CFW_RTOS_TIMER_STATIC_OBJECT_SIZE() \
    open_cfw_test_rtos_timer_static_object_size
#define OPEN_CFW_RTOS_TIMER_STATIC_FAIL_STOP() \
    open_cfw_test_rtos_timer_static_fail_stop()
#define OPEN_CFW_RTOS_TIMER_STATIC_INITIALIZE(...) \
    open_cfw_test_rtos_timer_static_initialize(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/rtos_timer_static_create.c"
