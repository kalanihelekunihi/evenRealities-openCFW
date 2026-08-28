/* SPDX-License-Identifier: MIT */

#include <stdint.h>
#include <string.h>

#include "../../components/shared/easylogger/runtime_easylogger_async_consumer_candidate.h"

enum { OPEN_CFW_TEST_EASYLOGGER_CONSUMER_RECORDS = 300U };

volatile open_cfw_easylogger_async_queue_u8
    open_cfw_retained_easylogger_async_ready;
volatile open_cfw_easylogger_async_queue_u8
    open_cfw_retained_easylogger_async_default_metadata;
volatile open_cfw_easylogger_async_queue_u8
    open_cfw_retained_easylogger_async_primary_enabled;
open_cfw_easylogger_async_consumer_callback volatile
    open_cfw_retained_easylogger_async_primary_callback;
volatile open_cfw_easylogger_async_queue_u8
    open_cfw_retained_easylogger_async_secondary_enabled;
open_cfw_easylogger_async_consumer_callback volatile
    open_cfw_retained_easylogger_async_secondary_callback;
struct open_cfw_easylogger_async_queue_statistics
    open_cfw_retained_easylogger_async_queue_statistics;

struct open_cfw_easylogger_async_queue_record
    open_cfw_test_easylogger_consumer_records[
        OPEN_CFW_TEST_EASYLOGGER_CONSUMER_RECORDS
    ];
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_consumer_record_count;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_consumer_dequeue_index;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_consumer_recycle_count;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_consumer_callback_count;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_consumer_callback_bytes;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_consumer_callback_checksum;

struct open_cfw_easylogger_async_queue_record *
open_cfw_easylogger_async_queue_record_dequeue(void)
{
    if (
        open_cfw_test_easylogger_consumer_dequeue_index >=
            open_cfw_test_easylogger_consumer_record_count
    ) {
        return (struct open_cfw_easylogger_async_queue_record *)0;
    }
    return &open_cfw_test_easylogger_consumer_records[
        open_cfw_test_easylogger_consumer_dequeue_index++
    ];
}

void open_cfw_easylogger_async_queue_record_recycle(
    struct open_cfw_easylogger_async_queue_record *record
)
{
    (void)record;
    open_cfw_test_easylogger_consumer_recycle_count++;
}

static void open_cfw_test_easylogger_consumer_callback(
    const open_cfw_easylogger_async_queue_u8 *payload,
    open_cfw_easylogger_async_queue_u32 length
)
{
    open_cfw_easylogger_async_queue_u32 index;
    open_cfw_test_easylogger_consumer_callback_count++;
    open_cfw_test_easylogger_consumer_callback_bytes += length;
    for (index = 0U; index < length; index++) {
        open_cfw_test_easylogger_consumer_callback_checksum += payload[index];
    }
}

#include "../../components/shared/easylogger/runtime_easylogger_async_consumer_candidate.c"

void open_cfw_test_easylogger_consumer_reset(
    open_cfw_easylogger_async_queue_u32 count
)
{
    memset(
        open_cfw_test_easylogger_consumer_records,
        0,
        sizeof(open_cfw_test_easylogger_consumer_records)
    );
    memset(
        &open_cfw_retained_easylogger_async_queue_statistics,
        0,
        sizeof(open_cfw_retained_easylogger_async_queue_statistics)
    );
    open_cfw_test_easylogger_consumer_record_count = count;
    open_cfw_test_easylogger_consumer_dequeue_index = 0U;
    open_cfw_test_easylogger_consumer_recycle_count = 0U;
    open_cfw_test_easylogger_consumer_callback_count = 0U;
    open_cfw_test_easylogger_consumer_callback_bytes = 0U;
    open_cfw_test_easylogger_consumer_callback_checksum = 0U;
    open_cfw_retained_easylogger_async_ready = 1U;
    open_cfw_retained_easylogger_async_default_metadata = 1U;
    open_cfw_retained_easylogger_async_primary_enabled = 1U;
    open_cfw_retained_easylogger_async_primary_callback =
        open_cfw_test_easylogger_consumer_callback;
    open_cfw_retained_easylogger_async_secondary_enabled = 0U;
    open_cfw_retained_easylogger_async_secondary_callback =
        (open_cfw_easylogger_async_consumer_callback)0;
}

void open_cfw_test_easylogger_consumer_set_record(
    open_cfw_easylogger_async_queue_u32 index,
    open_cfw_easylogger_async_queue_u16 metadata,
    const open_cfw_easylogger_async_queue_u8 *payload,
    open_cfw_easylogger_async_queue_u16 length,
    open_cfw_easylogger_async_queue_u8 level
)
{
    struct open_cfw_easylogger_async_queue_record *record =
        &open_cfw_test_easylogger_consumer_records[index];
    record->metadata = metadata;
    record->length = length;
    record->level = level;
    if (length != 0U) {
        memcpy(record->payload, payload, length);
    }
    record->payload[length] = 0U;
}

open_cfw_easylogger_async_queue_u32
open_cfw_test_easylogger_consumer_drain(void)
{
    return open_cfw_easylogger_async_record_drain();
}

open_cfw_easylogger_async_queue_u32
open_cfw_test_easylogger_consumer_configure_primary(
    open_cfw_easylogger_async_queue_u8 enabled,
    open_cfw_easylogger_async_queue_u32 install_callback
)
{
    return open_cfw_easylogger_async_primary_callback_configure(
        enabled,
        install_callback != 0U
            ? open_cfw_test_easylogger_consumer_callback
            : (open_cfw_easylogger_async_consumer_callback)0
    );
}

open_cfw_easylogger_async_queue_u32
open_cfw_test_easylogger_consumer_configure_secondary(
    open_cfw_easylogger_async_queue_u8 enabled,
    open_cfw_easylogger_async_queue_u32 install_callback
)
{
    return open_cfw_easylogger_async_secondary_callback_configure(
        enabled,
        install_callback != 0U
            ? open_cfw_test_easylogger_consumer_callback
            : (open_cfw_easylogger_async_consumer_callback)0
    );
}
