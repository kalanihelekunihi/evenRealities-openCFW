/*
 * SPDX-License-Identifier: MIT
 *
 * Host substitutions for the EasyLogger tracepoint timer bootstrap.
 */

#include <stdint.h>
#include <string.h>

typedef __UINTPTR_TYPE__ open_cfw_test_tracepoint_bootstrap_uintptr;
typedef void (*open_cfw_test_tracepoint_bootstrap_callback)(void *);

void *open_cfw_test_tracepoint_bootstrap_timer_handle;
unsigned int open_cfw_test_tracepoint_bootstrap_create_null;
unsigned int open_cfw_test_tracepoint_bootstrap_timer_storage;
unsigned int open_cfw_test_tracepoint_bootstrap_created_handle_storage;

unsigned int open_cfw_test_tracepoint_bootstrap_create_calls;
unsigned int open_cfw_test_tracepoint_bootstrap_setup_calls;
unsigned int open_cfw_test_tracepoint_bootstrap_begin_calls;
unsigned int open_cfw_test_tracepoint_bootstrap_fatal_calls;
unsigned int open_cfw_test_tracepoint_bootstrap_callback_calls;

unsigned int open_cfw_test_tracepoint_bootstrap_period;
unsigned int open_cfw_test_tracepoint_bootstrap_auto_reload;
unsigned int open_cfw_test_tracepoint_bootstrap_identifier;
open_cfw_test_tracepoint_bootstrap_uintptr
    open_cfw_test_tracepoint_bootstrap_callback_argument;
open_cfw_test_tracepoint_bootstrap_uintptr
    open_cfw_test_tracepoint_bootstrap_storage_argument;
open_cfw_test_tracepoint_bootstrap_uintptr
    open_cfw_test_tracepoint_bootstrap_callback_timer_argument;
open_cfw_test_tracepoint_bootstrap_uintptr
    open_cfw_test_tracepoint_bootstrap_handle_seen_by_create;
open_cfw_test_tracepoint_bootstrap_uintptr
    open_cfw_test_tracepoint_bootstrap_handle_seen_by_setup;
open_cfw_test_tracepoint_bootstrap_uintptr
    open_cfw_test_tracepoint_bootstrap_handle_seen_by_begin;

char open_cfw_test_tracepoint_bootstrap_name[32];
unsigned int open_cfw_test_tracepoint_bootstrap_events[16];
unsigned int open_cfw_test_tracepoint_bootstrap_event_count;

static open_cfw_test_tracepoint_bootstrap_callback
    open_cfw_test_tracepoint_bootstrap_captured_callback;

enum {
    OPEN_CFW_TEST_TRACEPOINT_BOOTSTRAP_EVENT_CREATE = 1,
    OPEN_CFW_TEST_TRACEPOINT_BOOTSTRAP_EVENT_SETUP = 2,
    OPEN_CFW_TEST_TRACEPOINT_BOOTSTRAP_EVENT_BEGIN = 3,
    OPEN_CFW_TEST_TRACEPOINT_BOOTSTRAP_EVENT_FATAL = 4,
    OPEN_CFW_TEST_TRACEPOINT_BOOTSTRAP_EVENT_CALLBACK = 5
};

static void open_cfw_test_tracepoint_bootstrap_record(
    unsigned int event
)
{
    if (open_cfw_test_tracepoint_bootstrap_event_count < 16U) {
        open_cfw_test_tracepoint_bootstrap_events[
            open_cfw_test_tracepoint_bootstrap_event_count
        ] = event;
    }
    open_cfw_test_tracepoint_bootstrap_event_count += 1U;
}

void open_cfw_test_tracepoint_bootstrap_reset(void)
{
    open_cfw_test_tracepoint_bootstrap_timer_handle = NULL;
    open_cfw_test_tracepoint_bootstrap_create_null = 0U;
    open_cfw_test_tracepoint_bootstrap_create_calls = 0U;
    open_cfw_test_tracepoint_bootstrap_setup_calls = 0U;
    open_cfw_test_tracepoint_bootstrap_begin_calls = 0U;
    open_cfw_test_tracepoint_bootstrap_fatal_calls = 0U;
    open_cfw_test_tracepoint_bootstrap_callback_calls = 0U;
    open_cfw_test_tracepoint_bootstrap_period = 0U;
    open_cfw_test_tracepoint_bootstrap_auto_reload = 0U;
    open_cfw_test_tracepoint_bootstrap_identifier = 0U;
    open_cfw_test_tracepoint_bootstrap_callback_argument = 0U;
    open_cfw_test_tracepoint_bootstrap_storage_argument = 0U;
    open_cfw_test_tracepoint_bootstrap_callback_timer_argument = 0U;
    open_cfw_test_tracepoint_bootstrap_handle_seen_by_create = 0U;
    open_cfw_test_tracepoint_bootstrap_handle_seen_by_setup = 0U;
    open_cfw_test_tracepoint_bootstrap_handle_seen_by_begin = 0U;
    open_cfw_test_tracepoint_bootstrap_event_count = 0U;
    open_cfw_test_tracepoint_bootstrap_captured_callback = NULL;
    memset(
        open_cfw_test_tracepoint_bootstrap_name,
        0,
        sizeof(open_cfw_test_tracepoint_bootstrap_name)
    );
    memset(
        open_cfw_test_tracepoint_bootstrap_events,
        0,
        sizeof(open_cfw_test_tracepoint_bootstrap_events)
    );
}

void open_cfw_test_tracepoint_bootstrap_set_existing_handle(
    unsigned int present
)
{
    open_cfw_test_tracepoint_bootstrap_timer_handle =
        present != 0U
            ? (void *)
                &open_cfw_test_tracepoint_bootstrap_created_handle_storage
            : NULL;
}

unsigned int open_cfw_test_tracepoint_bootstrap_has_handle(void)
{
    return open_cfw_test_tracepoint_bootstrap_timer_handle != NULL
        ? 1U
        : 0U;
}

unsigned int
open_cfw_test_tracepoint_bootstrap_storage_argument_matches(void)
{
    return open_cfw_test_tracepoint_bootstrap_storage_argument
            == (open_cfw_test_tracepoint_bootstrap_uintptr)
                &open_cfw_test_tracepoint_bootstrap_timer_storage
        ? 1U
        : 0U;
}

static void *open_cfw_test_tracepoint_bootstrap_timer_create(
    const char *name,
    unsigned int period,
    unsigned int auto_reload,
    unsigned int identifier,
    open_cfw_test_tracepoint_bootstrap_callback callback,
    void *storage
)
{
    open_cfw_test_tracepoint_bootstrap_record(
        OPEN_CFW_TEST_TRACEPOINT_BOOTSTRAP_EVENT_CREATE
    );
    open_cfw_test_tracepoint_bootstrap_create_calls += 1U;
    open_cfw_test_tracepoint_bootstrap_handle_seen_by_create =
        (open_cfw_test_tracepoint_bootstrap_uintptr)
            open_cfw_test_tracepoint_bootstrap_timer_handle;
    open_cfw_test_tracepoint_bootstrap_period = period;
    open_cfw_test_tracepoint_bootstrap_auto_reload = auto_reload;
    open_cfw_test_tracepoint_bootstrap_identifier = identifier;
    open_cfw_test_tracepoint_bootstrap_callback_argument =
        (open_cfw_test_tracepoint_bootstrap_uintptr)callback;
    open_cfw_test_tracepoint_bootstrap_storage_argument =
        (open_cfw_test_tracepoint_bootstrap_uintptr)storage;
    open_cfw_test_tracepoint_bootstrap_captured_callback = callback;
    (void)strncpy(
        open_cfw_test_tracepoint_bootstrap_name,
        name,
        sizeof(open_cfw_test_tracepoint_bootstrap_name) - 1U
    );
    if (open_cfw_test_tracepoint_bootstrap_create_null != 0U) {
        return NULL;
    }
    return &open_cfw_test_tracepoint_bootstrap_created_handle_storage;
}

static void open_cfw_test_tracepoint_bootstrap_retained_setup(void)
{
    open_cfw_test_tracepoint_bootstrap_record(
        OPEN_CFW_TEST_TRACEPOINT_BOOTSTRAP_EVENT_SETUP
    );
    open_cfw_test_tracepoint_bootstrap_setup_calls += 1U;
    open_cfw_test_tracepoint_bootstrap_handle_seen_by_setup =
        (open_cfw_test_tracepoint_bootstrap_uintptr)
            open_cfw_test_tracepoint_bootstrap_timer_handle;
}

static void open_cfw_test_tracepoint_bootstrap_fail_stop(void)
{
    open_cfw_test_tracepoint_bootstrap_record(
        OPEN_CFW_TEST_TRACEPOINT_BOOTSTRAP_EVENT_FATAL
    );
    open_cfw_test_tracepoint_bootstrap_fatal_calls += 1U;
}

void open_cfw_tracepoint_defer_timer_callback(void *timer)
{
    open_cfw_test_tracepoint_bootstrap_record(
        OPEN_CFW_TEST_TRACEPOINT_BOOTSTRAP_EVENT_CALLBACK
    );
    open_cfw_test_tracepoint_bootstrap_callback_calls += 1U;
    open_cfw_test_tracepoint_bootstrap_callback_timer_argument =
        (open_cfw_test_tracepoint_bootstrap_uintptr)timer;
}

void open_cfw_tracepoint_defer_begin(void)
{
    open_cfw_test_tracepoint_bootstrap_record(
        OPEN_CFW_TEST_TRACEPOINT_BOOTSTRAP_EVENT_BEGIN
    );
    open_cfw_test_tracepoint_bootstrap_begin_calls += 1U;
    open_cfw_test_tracepoint_bootstrap_handle_seen_by_begin =
        (open_cfw_test_tracepoint_bootstrap_uintptr)
            open_cfw_test_tracepoint_bootstrap_timer_handle;
}

void open_cfw_test_tracepoint_bootstrap_invoke_callback(void *timer)
{
    if (open_cfw_test_tracepoint_bootstrap_captured_callback != NULL) {
        open_cfw_test_tracepoint_bootstrap_captured_callback(timer);
    }
}

#define OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_CREATE( \
    name, period, auto_reload, identifier, callback, storage \
) \
    open_cfw_test_tracepoint_bootstrap_timer_create( \
        (name), \
        (period), \
        (auto_reload), \
        (identifier), \
        (callback), \
        (storage) \
    )
#define OPEN_CFW_TRACEPOINT_BOOTSTRAP_RETAINED_SETUP() \
    open_cfw_test_tracepoint_bootstrap_retained_setup()
#define OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_HANDLE \
    open_cfw_test_tracepoint_bootstrap_timer_handle
#define OPEN_CFW_TRACEPOINT_BOOTSTRAP_TIMER_STORAGE \
    ((void *)&open_cfw_test_tracepoint_bootstrap_timer_storage)
#define OPEN_CFW_TRACEPOINT_BOOTSTRAP_FAIL_STOP() \
    open_cfw_test_tracepoint_bootstrap_fail_stop()

#include "../../components/apollo_main/core_overlay/tracepoint_bootstrap.c"
