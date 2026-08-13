/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Standalone host substitutions for the retained G2 EasyLogger async seams.
 */

#include <stdint.h>
#include <string.h>

enum {
    OPEN_CFW_TEST_EASYLOGGER_ASYNC_EVENT_BUILD = 1U,
    OPEN_CFW_TEST_EASYLOGGER_ASYNC_EVENT_NOTIFY = 2U
};

uint32_t open_cfw_test_easylogger_async_build_calls;
uintptr_t open_cfw_test_easylogger_async_build_buffer;
uint32_t open_cfw_test_easylogger_async_build_length;
uint32_t open_cfw_test_easylogger_async_build_metadata;
uint32_t open_cfw_test_easylogger_async_build_level;
uint32_t open_cfw_test_easylogger_async_build_result;
uint32_t open_cfw_test_easylogger_async_set_calls;
uintptr_t open_cfw_test_easylogger_async_set_handle;
uint32_t open_cfw_test_easylogger_async_set_flags;
uint32_t open_cfw_test_easylogger_async_set_result;
uint32_t open_cfw_test_easylogger_async_mutate_handle_during_build;
void *open_cfw_test_easylogger_async_mutated_handle;
uint32_t open_cfw_test_easylogger_async_event_count;
uint32_t open_cfw_test_easylogger_async_events[4];

void * volatile open_cfw_retained_easylogger_async_event_flags;

static void open_cfw_test_easylogger_async_record_event(uint32_t event)
{
    if (open_cfw_test_easylogger_async_event_count < 4U) {
        open_cfw_test_easylogger_async_events[
            open_cfw_test_easylogger_async_event_count
        ] = event;
    }
    open_cfw_test_easylogger_async_event_count++;
}

uint32_t open_cfw_g2_easylogger_async_record_build_single_owner(
    const char *buffer,
    uint32_t length,
    uint32_t metadata,
    uint32_t level
)
{
    open_cfw_test_easylogger_async_record_event(
        OPEN_CFW_TEST_EASYLOGGER_ASYNC_EVENT_BUILD
    );
    open_cfw_test_easylogger_async_build_calls++;
    open_cfw_test_easylogger_async_build_buffer = (uintptr_t)buffer;
    open_cfw_test_easylogger_async_build_length = length;
    open_cfw_test_easylogger_async_build_metadata = metadata;
    open_cfw_test_easylogger_async_build_level = level;
    if (open_cfw_test_easylogger_async_mutate_handle_during_build != 0U) {
        open_cfw_retained_easylogger_async_event_flags =
            open_cfw_test_easylogger_async_mutated_handle;
    }
    return open_cfw_test_easylogger_async_build_result;
}

uint32_t open_cfw_retained_os_event_flags_set(
    void *event_flags,
    uint32_t flags
)
{
    open_cfw_test_easylogger_async_record_event(
        OPEN_CFW_TEST_EASYLOGGER_ASYNC_EVENT_NOTIFY
    );
    open_cfw_test_easylogger_async_set_calls++;
    open_cfw_test_easylogger_async_set_handle = (uintptr_t)event_flags;
    open_cfw_test_easylogger_async_set_flags = flags;
    return open_cfw_test_easylogger_async_set_result;
}

#include "../../components/apollo_main/core_overlay/runtime_easylogger_async_submit.c"

void open_cfw_test_easylogger_async_reset(
    uintptr_t event_handle,
    uint32_t build_result,
    uint32_t set_result
)
{
    open_cfw_test_easylogger_async_build_calls = 0U;
    open_cfw_test_easylogger_async_build_buffer = 0U;
    open_cfw_test_easylogger_async_build_length = 0U;
    open_cfw_test_easylogger_async_build_metadata = 0U;
    open_cfw_test_easylogger_async_build_level = 0U;
    open_cfw_test_easylogger_async_build_result = build_result;
    open_cfw_test_easylogger_async_set_calls = 0U;
    open_cfw_test_easylogger_async_set_handle = 0U;
    open_cfw_test_easylogger_async_set_flags = 0U;
    open_cfw_test_easylogger_async_set_result = set_result;
    open_cfw_test_easylogger_async_mutate_handle_during_build = 0U;
    open_cfw_test_easylogger_async_mutated_handle = (void *)0;
    open_cfw_test_easylogger_async_event_count = 0U;
    memset(
        open_cfw_test_easylogger_async_events,
        0,
        sizeof(open_cfw_test_easylogger_async_events)
    );
    open_cfw_retained_easylogger_async_event_flags =
        (void *)event_handle;
}

void open_cfw_test_easylogger_async_set_build_handle_mutation(
    uintptr_t event_handle
)
{
    open_cfw_test_easylogger_async_mutated_handle = (void *)event_handle;
    open_cfw_test_easylogger_async_mutate_handle_during_build = 1U;
}
