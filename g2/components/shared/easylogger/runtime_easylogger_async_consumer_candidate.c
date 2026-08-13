/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room reconstruction of the G2 downstream EasyLogger callback setters
 * and at-most-256-record consumer drain. This candidate is deliberately not a
 * production input.
 */

#include "runtime_easylogger_async_consumer_candidate.h"

open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_async_primary_callback_configure(
    open_cfw_easylogger_async_queue_u8 enabled,
    open_cfw_easylogger_async_consumer_callback callback
)
{
    open_cfw_retained_easylogger_async_primary_enabled = enabled;
    open_cfw_retained_easylogger_async_primary_callback = callback;
    return 0U;
}

open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_async_secondary_callback_configure(
    open_cfw_easylogger_async_queue_u8 enabled,
    open_cfw_easylogger_async_consumer_callback callback
)
{
    open_cfw_retained_easylogger_async_secondary_enabled = enabled;
    open_cfw_retained_easylogger_async_secondary_callback = callback;
    return 0U;
}

void open_cfw_easylogger_async_default_metadata_set(
    open_cfw_easylogger_async_queue_u8 metadata
)
{
    open_cfw_retained_easylogger_async_default_metadata = metadata;
}

open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_async_record_drain(void)
{
    open_cfw_easylogger_async_queue_u32 processed = 0U;
    open_cfw_easylogger_async_queue_u32 iteration;

    if (open_cfw_retained_easylogger_async_ready == 0U) {
        return 0U;
    }

    for (iteration = 0U; iteration < 256U; iteration++) {
        struct open_cfw_easylogger_async_queue_record *record =
            open_cfw_easylogger_async_queue_record_dequeue();

        if (record == (struct open_cfw_easylogger_async_queue_record *)0) {
            break;
        }
        if (
            ((open_cfw_easylogger_async_queue_u8)record->metadata & 1U) != 0U
            && open_cfw_retained_easylogger_async_primary_enabled != 0U
            && open_cfw_retained_easylogger_async_primary_callback !=
                (open_cfw_easylogger_async_consumer_callback)0
        ) {
            open_cfw_retained_easylogger_async_primary_callback(
                record->payload,
                (open_cfw_easylogger_async_queue_u32)record->length
            );
        }

        open_cfw_easylogger_async_queue_record_recycle(record);
        processed++;
        open_cfw_retained_easylogger_async_queue_statistics
            .drained_record_count++;
    }
    return processed;
}
