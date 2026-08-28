/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the downstream G2 EasyLogger CMSIS event
 * worker. This candidate deliberately remains outside production routing.
 */

#include "runtime_easylogger_async_worker_candidate.h"

enum {
    OPEN_CFW_EASYLOGGER_ASYNC_LOG_EVENT = 0x01U,
    OPEN_CFW_EASYLOGGER_ASYNC_DATABASE_EVENT = 0x02U,
    OPEN_CFW_EASYLOGGER_ASYNC_PERSIST_EVENT = 0x04U,
    OPEN_CFW_EASYLOGGER_ASYNC_UPLOAD_EVENT = 0x08U,
    OPEN_CFW_EASYLOGGER_ASYNC_EVENT_MASK = 0x0FU,
    OPEN_CFW_EASYLOGGER_ASYNC_WAIT_ANY = 0x02U,
    OPEN_CFW_EASYLOGGER_ASYNC_WAIT_FOREVER = 0xFFFFFFFFU,
    OPEN_CFW_EASYLOGGER_ASYNC_STACK_SIZE = 0x800U,
    OPEN_CFW_EASYLOGGER_ASYNC_PRIORITY = 0x17U,
};

const char open_cfw_easylogger_async_worker_thread_name[] =
    "elog_async_handler_thread";
const char open_cfw_easylogger_async_worker_start_message[] =
    "elog_async_handler_thread_handler start\n";
const char open_cfw_easylogger_async_event_create_failure_message[] =
    "Failed to create elog_async_handler_thread EventFlags\n";

extern open_cfw_easylogger_async_queue_u32
open_cfw_retained_easylogger_event_flags_wait(
    open_cfw_easylogger_async_cmsis_id event_flags,
    open_cfw_easylogger_async_queue_u32 flags,
    open_cfw_easylogger_async_queue_u32 options,
    open_cfw_easylogger_async_queue_u32 timeout
);

extern open_cfw_easylogger_async_queue_u32
open_cfw_retained_easylogger_event_flags_clear(
    open_cfw_easylogger_async_cmsis_id event_flags,
    open_cfw_easylogger_async_queue_u32 flags
);

extern open_cfw_easylogger_async_cmsis_id
open_cfw_retained_easylogger_event_flags_new(const void *attributes);

extern open_cfw_easylogger_async_cmsis_id
open_cfw_retained_easylogger_thread_new(
    void (*entry)(void *),
    void *argument,
    const struct open_cfw_easylogger_async_thread_attributes *attributes
);

extern void open_cfw_retained_easylogger_diagnostic(const char *message);
extern void open_cfw_retained_easylogger_kv_event_diagnostic(void);
extern void open_cfw_retained_easylogger_database_event_handler(void);
extern void open_cfw_retained_easylogger_upload_event_handler(void);
extern void open_cfw_retained_easylogger_settings_save_handler(void);
extern void open_cfw_retained_easylogger_history_save_handler(void);
extern void open_cfw_retained_easylogger_onboarding_save_handler(void);
extern void open_cfw_retained_easylogger_device_save_handler(void);
extern void open_cfw_retained_easylogger_user_save_handler(void);
extern void open_cfw_retained_easylogger_contacts_save_handler(void);
extern void open_cfw_retained_easylogger_preferences_save_handler(void);

void open_cfw_easylogger_async_event_dispatch(
    open_cfw_easylogger_async_queue_u32 flags
)
{
    if ((flags & OPEN_CFW_EASYLOGGER_ASYNC_LOG_EVENT) != 0U) {
        (void)open_cfw_easylogger_async_record_drain();
        (void)open_cfw_retained_easylogger_event_flags_clear(
            open_cfw_retained_easylogger_async_event_flags,
            OPEN_CFW_EASYLOGGER_ASYNC_LOG_EVENT
        );
    }

    if ((flags & OPEN_CFW_EASYLOGGER_ASYNC_DATABASE_EVENT) != 0U) {
        open_cfw_retained_easylogger_database_event_handler();
        (void)open_cfw_retained_easylogger_event_flags_clear(
            open_cfw_retained_easylogger_async_event_flags,
            OPEN_CFW_EASYLOGGER_ASYNC_DATABASE_EVENT
        );
    }

    if ((flags & OPEN_CFW_EASYLOGGER_ASYNC_UPLOAD_EVENT) != 0U) {
        open_cfw_retained_easylogger_upload_event_handler();
        (void)open_cfw_retained_easylogger_event_flags_clear(
            open_cfw_retained_easylogger_async_event_flags,
            OPEN_CFW_EASYLOGGER_ASYNC_UPLOAD_EVENT
        );
    }

    if ((flags & OPEN_CFW_EASYLOGGER_ASYNC_PERSIST_EVENT) != 0U) {
        open_cfw_retained_easylogger_kv_event_diagnostic();
        open_cfw_retained_easylogger_settings_save_handler();
        open_cfw_retained_easylogger_history_save_handler();
        open_cfw_retained_easylogger_onboarding_save_handler();
        open_cfw_retained_easylogger_device_save_handler();
        open_cfw_retained_easylogger_user_save_handler();
        open_cfw_retained_easylogger_contacts_save_handler();
        open_cfw_retained_easylogger_preferences_save_handler();
        (void)open_cfw_retained_easylogger_event_flags_clear(
            open_cfw_retained_easylogger_async_event_flags,
            OPEN_CFW_EASYLOGGER_ASYNC_PERSIST_EVENT
        );
    }
}

void open_cfw_easylogger_async_event_worker(void *argument)
{
    (void)argument;
    open_cfw_retained_easylogger_diagnostic(
        open_cfw_easylogger_async_worker_start_message
    );

    for (;;) {
        open_cfw_easylogger_async_queue_u32 flags =
            open_cfw_retained_easylogger_event_flags_wait(
                open_cfw_retained_easylogger_async_event_flags,
                OPEN_CFW_EASYLOGGER_ASYNC_EVENT_MASK,
                OPEN_CFW_EASYLOGGER_ASYNC_WAIT_ANY,
                OPEN_CFW_EASYLOGGER_ASYNC_WAIT_FOREVER
            );
        open_cfw_easylogger_async_event_dispatch(flags);
    }
}

void open_cfw_easylogger_async_event_worker_initialize(void)
{
    const struct open_cfw_easylogger_async_thread_attributes attributes = {
        open_cfw_easylogger_async_worker_thread_name,
        0U,
        (void *)0,
        0U,
        (void *)0,
        OPEN_CFW_EASYLOGGER_ASYNC_STACK_SIZE,
        OPEN_CFW_EASYLOGGER_ASYNC_PRIORITY,
        0U,
        0U,
    };

    open_cfw_retained_easylogger_async_event_flags =
        open_cfw_retained_easylogger_event_flags_new((const void *)0);
    if (open_cfw_retained_easylogger_async_event_flags ==
        (open_cfw_easylogger_async_cmsis_id)0) {
        open_cfw_retained_easylogger_diagnostic(
            open_cfw_easylogger_async_event_create_failure_message
        );
        return;
    }

    (void)open_cfw_retained_easylogger_thread_new(
        open_cfw_easylogger_async_event_worker,
        (void *)0,
        &attributes
    );
}
