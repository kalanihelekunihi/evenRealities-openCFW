/* SPDX-License-Identifier: MIT */
#define OPEN_CFW_EVENT_FLAGS_SERVICE_HOST 1
#include "../../components/bootloader/core_overlay/runtime_event_flags_service_41fe62.c"

static open_cfw_event_word handle_value;
static open_cfw_event_word create_result;
static open_cfw_event_u32 acquire_result;
static open_cfw_event_u32 release_result;
static open_cfw_event_u32 create_calls;
static open_cfw_event_u32 acquire_calls;
static open_cfw_event_u32 release_calls;
static open_cfw_event_u32 log_calls;
static open_cfw_event_word acquire_handle;
static open_cfw_event_u32 acquire_timeout;
static open_cfw_event_word release_handle;
static open_cfw_event_word log_arguments[6];
static open_cfw_event_u32 config_token;

open_cfw_event_word *open_cfw_event_flags_host_handle(void)
{
    return &handle_value;
}

const void *open_cfw_event_flags_host_config(void)
{
    return &config_token;
}

open_cfw_event_word open_cfw_event_flags_host_create(const void *config)
{
    create_calls++;
    if (config != &config_token) {
        return 0U;
    }
    return create_result;
}

open_cfw_event_u32 open_cfw_event_flags_host_acquire(
    open_cfw_event_word handle,
    open_cfw_event_u32 timeout)
{
    acquire_calls++;
    acquire_handle = handle;
    acquire_timeout = timeout;
    return acquire_result;
}

open_cfw_event_u32 open_cfw_event_flags_host_release(
    open_cfw_event_word handle)
{
    release_calls++;
    release_handle = handle;
    return release_result;
}

void open_cfw_event_flags_host_log(
    open_cfw_event_u32 level,
    open_cfw_event_word tag,
    open_cfw_event_word file,
    open_cfw_event_word function,
    open_cfw_event_u32 line,
    open_cfw_event_word format)
{
    log_calls++;
    log_arguments[0] = level;
    log_arguments[1] = tag;
    log_arguments[2] = file;
    log_arguments[3] = function;
    log_arguments[4] = line;
    log_arguments[5] = format;
}

void open_cfw_event_flags_fixture_reset(
    open_cfw_event_word initial_handle,
    open_cfw_event_word next_create,
    open_cfw_event_u32 next_acquire,
    open_cfw_event_u32 next_release)
{
    open_cfw_event_u32 index;

    handle_value = initial_handle;
    create_result = next_create;
    acquire_result = next_acquire;
    release_result = next_release;
    create_calls = 0U;
    acquire_calls = 0U;
    release_calls = 0U;
    log_calls = 0U;
    acquire_handle = 0U;
    acquire_timeout = 0U;
    release_handle = 0U;
    for (index = 0U; index < 6U; ++index) {
        log_arguments[index] = 0U;
    }
}

open_cfw_event_word open_cfw_event_flags_fixture_handle(void)
{
    return handle_value;
}

open_cfw_event_u32 open_cfw_event_flags_fixture_count(open_cfw_event_u32 kind)
{
    if (kind == 0U) {
        return create_calls;
    }
    if (kind == 1U) {
        return acquire_calls;
    }
    if (kind == 2U) {
        return release_calls;
    }
    return log_calls;
}

open_cfw_event_word open_cfw_event_flags_fixture_observed(
    open_cfw_event_u32 kind)
{
    if (kind == 0U) {
        return acquire_handle;
    }
    if (kind == 1U) {
        return acquire_timeout;
    }
    return release_handle;
}

open_cfw_event_word open_cfw_event_flags_fixture_log(
    open_cfw_event_u32 index)
{
    return index < 6U ? log_arguments[index] : 0U;
}
