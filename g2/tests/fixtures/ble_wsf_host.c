#include <stddef.h>
#include <string.h>

#include "ble_wsf_host.h"

open_cfw_test_ble_wsf_state open_cfw_test_ble_wsf_state_words;
unsigned int open_cfw_test_ble_wsf_events[128];
unsigned int open_cfw_test_ble_wsf_event_count;
unsigned int open_cfw_test_ble_wsf_tick;
unsigned int open_cfw_test_ble_wsf_acquire_calls;
unsigned int open_cfw_test_ble_wsf_acquire_failures;
unsigned int open_cfw_test_ble_wsf_semaphore_value;
int open_cfw_test_ble_wsf_release_result;

static void record(unsigned int value)
{
    if (open_cfw_test_ble_wsf_event_count < 128U) {
        open_cfw_test_ble_wsf_events[open_cfw_test_ble_wsf_event_count++] = value;
    }
}

void open_cfw_test_ble_wsf_reset(void)
{
    memset(&open_cfw_test_ble_wsf_state_words, 0,
        sizeof(open_cfw_test_ble_wsf_state_words));
    memset(open_cfw_test_ble_wsf_events, 0,
        sizeof(open_cfw_test_ble_wsf_events));
    open_cfw_test_ble_wsf_event_count = 0U;
    open_cfw_test_ble_wsf_tick = 0U;
    open_cfw_test_ble_wsf_acquire_calls = 0U;
    open_cfw_test_ble_wsf_acquire_failures = 0U;
    open_cfw_test_ble_wsf_semaphore_value = 1U;
    open_cfw_test_ble_wsf_release_result = 0;
}

void *open_cfw_test_ble_wsf_semaphore_new(
    unsigned int maximum,
    unsigned int initial,
    const void *attributes
)
{
    (void)attributes;
    record(0x10000000U | (maximum << 8) | initial);
    open_cfw_test_ble_wsf_semaphore_value = initial;
    return (void *)0x1234;
}

void open_cfw_test_ble_wsf_fatal(void) { record(0xF0000000U); }
void open_cfw_test_ble_wsf_resource_initialize(void) { record(0x11000000U); }
void open_cfw_test_ble_wsf_resource_deinitialize(void) { record(0x12000000U); }
void open_cfw_test_ble_wsf_app_start(void) { record(0x13000000U); }
void open_cfw_test_ble_wsf_dispatcher(void) { record(0x14000000U); }
void open_cfw_test_ble_wsf_stage_enter(unsigned int index)
{
    record(0x15000000U | index);
}
void open_cfw_test_ble_wsf_stage_ready(unsigned int index)
{
    record(0x16000000U | index);
}

void *open_cfw_test_ble_wsf_thread_new(
    void (*entry)(void *),
    void *argument,
    const void *attributes
)
{
    (void)entry;
    (void)argument;
    (void)attributes;
    record(0x17000000U);
    return (void *)0x5678;
}

void open_cfw_test_ble_wsf_thread_terminate(void *thread)
{
    record(0x18000000U | ((unsigned int)(size_t)thread & 0xFFFFU));
}

int open_cfw_test_ble_wsf_semaphore_acquire(void *semaphore, unsigned int timeout)
{
    (void)semaphore;
    record(0x20000000U | timeout);
    ++open_cfw_test_ble_wsf_acquire_calls;
    if (open_cfw_test_ble_wsf_acquire_calls <=
        open_cfw_test_ble_wsf_acquire_failures) {
        return -2;
    }
    if (open_cfw_test_ble_wsf_semaphore_value != 0U) {
        --open_cfw_test_ble_wsf_semaphore_value;
        return 0;
    }
    return -2;
}

unsigned int open_cfw_test_ble_wsf_kernel_tick(void)
{
    return open_cfw_test_ble_wsf_tick;
}

unsigned int open_cfw_test_ble_wsf_delay(unsigned int ticks)
{
    open_cfw_test_ble_wsf_tick += ticks;
    record(0x21000000U | ticks);
    return 0U;
}

unsigned int open_cfw_test_ble_wsf_semaphore_count(void *semaphore)
{
    (void)semaphore;
    return open_cfw_test_ble_wsf_semaphore_value;
}

int open_cfw_test_ble_wsf_semaphore_release(void *semaphore)
{
    (void)semaphore;
    record(0x22000000U | ((unsigned int)open_cfw_test_ble_wsf_release_result & 0xFFFFU));
    if (open_cfw_test_ble_wsf_release_result == 0) {
        open_cfw_test_ble_wsf_semaphore_value = 1U;
    }
    return open_cfw_test_ble_wsf_release_result;
}

void open_cfw_test_ble_wsf_resource_diagnostic(
    unsigned int maximum,
    unsigned int initial
)
{
    record(0x30000000U | (maximum << 8) | initial);
}

void open_cfw_test_ble_wsf_wait_bound_diagnostic(void)
{
    record(0x31000000U);
}

void open_cfw_test_ble_wsf_wait_result_diagnostic(
    unsigned int elapsed,
    unsigned int retries
)
{
    record(0x32000000U | ((elapsed & 0xFFFU) << 8) | (retries & 0xFFU));
}

void open_cfw_test_ble_wsf_release_failure_diagnostic(
    int status,
    unsigned int count
)
{
    record(0x33000000U | (((unsigned int)status & 0xFFU) << 8) | count);
}

void open_cfw_test_ble_wsf_already_full_diagnostic(unsigned int count)
{
    record(0x34000000U | count);
}

unsigned int open_cfw_test_ble_wsf_task_loop_continue(void)
{
    return 0U;
}
