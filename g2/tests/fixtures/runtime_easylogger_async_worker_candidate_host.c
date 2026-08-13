/* SPDX-License-Identifier: GPL-3.0-only */

#include <stdint.h>
#include <string.h>

#include "../../components/shared/easylogger/runtime_easylogger_async_worker_candidate.h"

enum { OPEN_CFW_TEST_EASYLOGGER_WORKER_EVENTS = 32U };

open_cfw_easylogger_async_cmsis_id
    open_cfw_retained_easylogger_async_event_flags;
uint32_t open_cfw_test_easylogger_worker_order[OPEN_CFW_TEST_EASYLOGGER_WORKER_EVENTS];
uint32_t open_cfw_test_easylogger_worker_order_count;
uint32_t open_cfw_test_easylogger_worker_clear_masks[4];
uintptr_t open_cfw_test_easylogger_worker_clear_handles[4];
uint32_t open_cfw_test_easylogger_worker_clear_count;
uint32_t open_cfw_test_easylogger_worker_new_returns_null;
uint32_t open_cfw_test_easylogger_worker_new_count;
uint32_t open_cfw_test_easylogger_worker_thread_count;
uint32_t open_cfw_test_easylogger_worker_diagnostic_count;
const char *open_cfw_test_easylogger_worker_last_diagnostic;
void (*open_cfw_test_easylogger_worker_thread_entry)(void *);
void *open_cfw_test_easylogger_worker_thread_argument;
struct open_cfw_easylogger_async_thread_attributes
    open_cfw_test_easylogger_worker_thread_attributes;

static void open_cfw_test_easylogger_worker_note(uint32_t event)
{
    open_cfw_test_easylogger_worker_order[
        open_cfw_test_easylogger_worker_order_count++
    ] = event;
}

open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_async_record_drain(void)
{
    open_cfw_test_easylogger_worker_note(1U);
    return 7U;
}

open_cfw_easylogger_async_queue_u32
open_cfw_retained_easylogger_event_flags_wait(
    open_cfw_easylogger_async_cmsis_id event_flags,
    open_cfw_easylogger_async_queue_u32 flags,
    open_cfw_easylogger_async_queue_u32 options,
    open_cfw_easylogger_async_queue_u32 timeout
)
{
    (void)event_flags;
    (void)flags;
    (void)options;
    (void)timeout;
    return 0U;
}

open_cfw_easylogger_async_queue_u32
open_cfw_retained_easylogger_event_flags_clear(
    open_cfw_easylogger_async_cmsis_id event_flags,
    open_cfw_easylogger_async_queue_u32 flags
)
{
    uint32_t index = open_cfw_test_easylogger_worker_clear_count++;
    open_cfw_test_easylogger_worker_clear_handles[index] =
        (uintptr_t)event_flags;
    open_cfw_test_easylogger_worker_clear_masks[index] = flags;
    open_cfw_test_easylogger_worker_note(100U + flags);
    return flags;
}

open_cfw_easylogger_async_cmsis_id
open_cfw_retained_easylogger_event_flags_new(const void *attributes)
{
    (void)attributes;
    open_cfw_test_easylogger_worker_new_count++;
    if (open_cfw_test_easylogger_worker_new_returns_null != 0U) {
        return (open_cfw_easylogger_async_cmsis_id)0;
    }
    return (open_cfw_easylogger_async_cmsis_id)(uintptr_t)0x12345678U;
}

open_cfw_easylogger_async_cmsis_id
open_cfw_retained_easylogger_thread_new(
    void (*entry)(void *),
    void *argument,
    const struct open_cfw_easylogger_async_thread_attributes *attributes
)
{
    open_cfw_test_easylogger_worker_thread_count++;
    open_cfw_test_easylogger_worker_thread_entry = entry;
    open_cfw_test_easylogger_worker_thread_argument = argument;
    open_cfw_test_easylogger_worker_thread_attributes = *attributes;
    return (open_cfw_easylogger_async_cmsis_id)(uintptr_t)0x87654321U;
}

void open_cfw_retained_easylogger_diagnostic(const char *message)
{
    open_cfw_test_easylogger_worker_diagnostic_count++;
    open_cfw_test_easylogger_worker_last_diagnostic = message;
}

#define OPEN_CFW_TEST_HANDLER(name, value) \
    void name(void) { open_cfw_test_easylogger_worker_note(value); }

OPEN_CFW_TEST_HANDLER(open_cfw_retained_easylogger_kv_event_diagnostic, 4U)
OPEN_CFW_TEST_HANDLER(open_cfw_retained_easylogger_database_event_handler, 2U)
OPEN_CFW_TEST_HANDLER(open_cfw_retained_easylogger_upload_event_handler, 8U)
OPEN_CFW_TEST_HANDLER(open_cfw_retained_easylogger_settings_save_handler, 40U)
OPEN_CFW_TEST_HANDLER(open_cfw_retained_easylogger_history_save_handler, 41U)
OPEN_CFW_TEST_HANDLER(open_cfw_retained_easylogger_onboarding_save_handler, 42U)
OPEN_CFW_TEST_HANDLER(open_cfw_retained_easylogger_device_save_handler, 43U)
OPEN_CFW_TEST_HANDLER(open_cfw_retained_easylogger_user_save_handler, 44U)
OPEN_CFW_TEST_HANDLER(open_cfw_retained_easylogger_contacts_save_handler, 45U)
OPEN_CFW_TEST_HANDLER(open_cfw_retained_easylogger_preferences_save_handler, 46U)

#include "../../components/shared/easylogger/runtime_easylogger_async_worker_candidate.c"

void open_cfw_test_easylogger_worker_reset(uint32_t new_returns_null)
{
    memset(open_cfw_test_easylogger_worker_order, 0,
           sizeof(open_cfw_test_easylogger_worker_order));
    memset(open_cfw_test_easylogger_worker_clear_masks, 0,
           sizeof(open_cfw_test_easylogger_worker_clear_masks));
    memset(open_cfw_test_easylogger_worker_clear_handles, 0,
           sizeof(open_cfw_test_easylogger_worker_clear_handles));
    memset(&open_cfw_test_easylogger_worker_thread_attributes, 0,
           sizeof(open_cfw_test_easylogger_worker_thread_attributes));
    open_cfw_retained_easylogger_async_event_flags =
        (open_cfw_easylogger_async_cmsis_id)(uintptr_t)0xCAFEBABEU;
    open_cfw_test_easylogger_worker_order_count = 0U;
    open_cfw_test_easylogger_worker_clear_count = 0U;
    open_cfw_test_easylogger_worker_new_returns_null = new_returns_null;
    open_cfw_test_easylogger_worker_new_count = 0U;
    open_cfw_test_easylogger_worker_thread_count = 0U;
    open_cfw_test_easylogger_worker_diagnostic_count = 0U;
    open_cfw_test_easylogger_worker_last_diagnostic = (const char *)0;
    open_cfw_test_easylogger_worker_thread_entry = (void (*)(void *))0;
    open_cfw_test_easylogger_worker_thread_argument = (void *)0;
}
