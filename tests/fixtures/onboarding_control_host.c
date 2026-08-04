/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host substitutions for the protobuf onboarding control-state update.
 */

#include <stdint.h>
#include <string.h>

typedef __UINTPTR_TYPE__ open_cfw_test_onboarding_control_uintptr;

unsigned char open_cfw_test_onboarding_control_state[3];
unsigned int open_cfw_test_onboarding_control_mutex_storage_a;
unsigned int open_cfw_test_onboarding_control_mutex_storage_b;
void *open_cfw_test_onboarding_control_mutex;

unsigned int open_cfw_test_onboarding_control_acquire_result;
unsigned int open_cfw_test_onboarding_control_release_result;
unsigned int open_cfw_test_onboarding_control_change_mutex_on_acquire;
unsigned int open_cfw_test_onboarding_control_acquire_calls;
unsigned int open_cfw_test_onboarding_control_release_calls;
unsigned int open_cfw_test_onboarding_control_wait_ticks;
open_cfw_test_onboarding_control_uintptr
    open_cfw_test_onboarding_control_acquire_mutex;
open_cfw_test_onboarding_control_uintptr
    open_cfw_test_onboarding_control_release_mutex;
unsigned char open_cfw_test_onboarding_control_state_seen_by_acquire[3];
unsigned char open_cfw_test_onboarding_control_state_seen_by_release[3];
unsigned int open_cfw_test_onboarding_control_events[8];
unsigned int open_cfw_test_onboarding_control_event_count;

enum {
    OPEN_CFW_TEST_ONBOARDING_CONTROL_EVENT_ACQUIRE = 1,
    OPEN_CFW_TEST_ONBOARDING_CONTROL_EVENT_RELEASE = 2
};

static void open_cfw_test_onboarding_control_record(
    unsigned int event
)
{
    if (open_cfw_test_onboarding_control_event_count < 8U) {
        open_cfw_test_onboarding_control_events[
            open_cfw_test_onboarding_control_event_count
        ] = event;
    }
    open_cfw_test_onboarding_control_event_count += 1U;
}

void open_cfw_test_onboarding_control_reset(void)
{
    open_cfw_test_onboarding_control_state[0] = 7U;
    open_cfw_test_onboarding_control_state[1] = 9U;
    open_cfw_test_onboarding_control_state[2] = 11U;
    open_cfw_test_onboarding_control_mutex =
        &open_cfw_test_onboarding_control_mutex_storage_a;
    open_cfw_test_onboarding_control_acquire_result = 0U;
    open_cfw_test_onboarding_control_release_result = 0U;
    open_cfw_test_onboarding_control_change_mutex_on_acquire = 0U;
    open_cfw_test_onboarding_control_acquire_calls = 0U;
    open_cfw_test_onboarding_control_release_calls = 0U;
    open_cfw_test_onboarding_control_wait_ticks = 0U;
    open_cfw_test_onboarding_control_acquire_mutex = 0U;
    open_cfw_test_onboarding_control_release_mutex = 0U;
    open_cfw_test_onboarding_control_event_count = 0U;
    memset(
        open_cfw_test_onboarding_control_state_seen_by_acquire,
        0,
        sizeof(open_cfw_test_onboarding_control_state_seen_by_acquire)
    );
    memset(
        open_cfw_test_onboarding_control_state_seen_by_release,
        0,
        sizeof(open_cfw_test_onboarding_control_state_seen_by_release)
    );
    memset(
        open_cfw_test_onboarding_control_events,
        0,
        sizeof(open_cfw_test_onboarding_control_events)
    );
}

unsigned int open_cfw_test_onboarding_control_acquire_uses_a(void)
{
    return open_cfw_test_onboarding_control_acquire_mutex
            == (open_cfw_test_onboarding_control_uintptr)
                &open_cfw_test_onboarding_control_mutex_storage_a
        ? 1U
        : 0U;
}

unsigned int open_cfw_test_onboarding_control_release_uses_b(void)
{
    return open_cfw_test_onboarding_control_release_mutex
            == (open_cfw_test_onboarding_control_uintptr)
                &open_cfw_test_onboarding_control_mutex_storage_b
        ? 1U
        : 0U;
}

static unsigned int open_cfw_test_onboarding_control_mutex_acquire(
    void *mutex,
    unsigned int wait_ticks
)
{
    open_cfw_test_onboarding_control_record(
        OPEN_CFW_TEST_ONBOARDING_CONTROL_EVENT_ACQUIRE
    );
    open_cfw_test_onboarding_control_acquire_calls += 1U;
    open_cfw_test_onboarding_control_acquire_mutex =
        (open_cfw_test_onboarding_control_uintptr)mutex;
    open_cfw_test_onboarding_control_wait_ticks = wait_ticks;
    memcpy(
        open_cfw_test_onboarding_control_state_seen_by_acquire,
        open_cfw_test_onboarding_control_state,
        sizeof(open_cfw_test_onboarding_control_state)
    );
    if (
        open_cfw_test_onboarding_control_change_mutex_on_acquire
        != 0U
    ) {
        open_cfw_test_onboarding_control_mutex =
            &open_cfw_test_onboarding_control_mutex_storage_b;
    }
    return open_cfw_test_onboarding_control_acquire_result;
}

static unsigned int open_cfw_test_onboarding_control_mutex_release(
    void *mutex
)
{
    open_cfw_test_onboarding_control_record(
        OPEN_CFW_TEST_ONBOARDING_CONTROL_EVENT_RELEASE
    );
    open_cfw_test_onboarding_control_release_calls += 1U;
    open_cfw_test_onboarding_control_release_mutex =
        (open_cfw_test_onboarding_control_uintptr)mutex;
    memcpy(
        open_cfw_test_onboarding_control_state_seen_by_release,
        open_cfw_test_onboarding_control_state,
        sizeof(open_cfw_test_onboarding_control_state)
    );
    return open_cfw_test_onboarding_control_release_result;
}

#define OPEN_CFW_ONBOARDING_CONTROL_STATE \
    open_cfw_test_onboarding_control_state
#define OPEN_CFW_ONBOARDING_CONTROL_MUTEX \
    open_cfw_test_onboarding_control_mutex
#define OPEN_CFW_ONBOARDING_CONTROL_MUTEX_ACQUIRE(mutex, wait_ticks) \
    open_cfw_test_onboarding_control_mutex_acquire( \
        (mutex), \
        (wait_ticks) \
    )
#define OPEN_CFW_ONBOARDING_CONTROL_MUTEX_RELEASE(mutex) \
    open_cfw_test_onboarding_control_mutex_release((mutex))

#include "../../components/apollo_main/core_overlay/onboarding_control.c"
