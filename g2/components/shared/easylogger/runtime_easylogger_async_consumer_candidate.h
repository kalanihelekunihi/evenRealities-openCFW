/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production-excluded clean-room candidate for the G2 EasyLogger downstream
 * callback setters and bounded fixed-record drain.
 */

#ifndef OPEN_CFW_RUNTIME_EASYLOGGER_ASYNC_CONSUMER_CANDIDATE_H
#define OPEN_CFW_RUNTIME_EASYLOGGER_ASYNC_CONSUMER_CANDIDATE_H

#include "runtime_easylogger_async_queue_candidate.h"

typedef void (*open_cfw_easylogger_async_consumer_callback)(
    const open_cfw_easylogger_async_queue_u8 *payload,
    open_cfw_easylogger_async_queue_u32 length
);

extern volatile open_cfw_easylogger_async_queue_u8
    open_cfw_retained_easylogger_async_primary_enabled;
extern open_cfw_easylogger_async_consumer_callback volatile
    open_cfw_retained_easylogger_async_primary_callback;
extern volatile open_cfw_easylogger_async_queue_u8
    open_cfw_retained_easylogger_async_secondary_enabled;
extern open_cfw_easylogger_async_consumer_callback volatile
    open_cfw_retained_easylogger_async_secondary_callback;

open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_async_primary_callback_configure(
    open_cfw_easylogger_async_queue_u8 enabled,
    open_cfw_easylogger_async_consumer_callback callback
);

open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_async_secondary_callback_configure(
    open_cfw_easylogger_async_queue_u8 enabled,
    open_cfw_easylogger_async_consumer_callback callback
);

void open_cfw_easylogger_async_default_metadata_set(
    open_cfw_easylogger_async_queue_u8 metadata
);

open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_async_record_drain(void);

#endif
