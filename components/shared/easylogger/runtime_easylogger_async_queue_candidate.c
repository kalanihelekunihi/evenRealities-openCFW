/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room reconstruction of the G2 downstream EasyLogger lock-free
 * fixed-record allocator, recycler, and Michael-Scott enqueue operation.
 * This candidate is deliberately not part of a production manifest.
 */

#include "runtime_easylogger_async_queue_candidate.h"

#if defined(__clang__) || defined(__GNUC__)
#define OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_NOINLINE __attribute__((noinline))
#else
#define OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_NOINLINE
#endif

static __inline__ struct open_cfw_easylogger_async_queue_record *
open_cfw_easylogger_async_queue_record_from_address(
    open_cfw_easylogger_async_queue_u32 address
)
{
#if defined(OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_HOST_ORACLE)
    return open_cfw_easylogger_async_queue_host_record_from_address(address);
#else
    return (struct open_cfw_easylogger_async_queue_record *)
        (open_cfw_easylogger_async_queue_uintptr)address;
#endif
}

static __inline__ open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_async_queue_address_from_record(
    const struct open_cfw_easylogger_async_queue_record *record
)
{
#if defined(OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_HOST_ORACLE)
    return open_cfw_easylogger_async_queue_host_address_from_record(record);
#else
    return (open_cfw_easylogger_async_queue_u32)
        (open_cfw_easylogger_async_queue_uintptr)record;
#endif
}

static __inline__ void open_cfw_easylogger_async_queue_note_success(
    open_cfw_easylogger_async_queue_u32 attempts,
    volatile open_cfw_easylogger_async_queue_u32 *retry_total,
    volatile open_cfw_easylogger_async_queue_u32 *attempt_maximum
)
{
    open_cfw_easylogger_async_queue_u32 total = *retry_total;
    open_cfw_easylogger_async_queue_u32 maximum = *attempt_maximum;

    *retry_total = total + attempts - 1U;
    if (maximum < attempts) {
        *attempt_maximum = attempts;
    }
}

OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_NOINLINE
void open_cfw_easylogger_atomic_store_adapter(
    volatile open_cfw_easylogger_async_queue_u32 *object,
    open_cfw_easylogger_async_queue_u32 value
)
{
    open_cfw_retained_easylogger_atomic_store_primitive(object, value);
}

OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_NOINLINE
open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_atomic_load_adapter(
    const volatile open_cfw_easylogger_async_queue_u32 *object
)
{
    return open_cfw_retained_easylogger_atomic_load_primitive(object);
}

OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_NOINLINE
open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_atomic_compare_exchange_adapter(
    volatile open_cfw_easylogger_async_queue_u32 *object,
    open_cfw_easylogger_async_queue_u32 *expected,
    open_cfw_easylogger_async_queue_u32 desired
)
{
    open_cfw_easylogger_async_queue_u32 local_expected = *expected;
    open_cfw_easylogger_async_queue_u32 result =
        open_cfw_retained_easylogger_atomic_compare_exchange_strong_primitive(
            object,
            &local_expected,
            desired
        );

    if (result == 0U) {
        *expected = local_expected;
    }
    return result & 0xFFU;
}

struct open_cfw_easylogger_async_queue_record *
open_cfw_easylogger_async_queue_record_allocate(void)
{
    struct open_cfw_easylogger_async_queue_record *record;
    open_cfw_easylogger_async_queue_u32 head;
    open_cfw_easylogger_async_queue_u32 next;
    open_cfw_easylogger_async_queue_u32 attempts = 0U;

    for (;;) {
        head = open_cfw_easylogger_atomic_load_adapter(
            &open_cfw_retained_easylogger_async_free_head
        );
        if (head == 0U) {
            open_cfw_retained_easylogger_async_queue_statistics
                .failed_operation_count++;
            return (struct open_cfw_easylogger_async_queue_record *)0;
        }

        record = open_cfw_easylogger_async_queue_record_from_address(head);
        next = open_cfw_easylogger_atomic_load_adapter(&record->next);
        attempts++;
        if (
            attempts >
                OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_ALLOCATE_RETRY_LIMIT
        ) {
            open_cfw_retained_easylogger_async_queue_statistics
                .retry_limit_count++;
            open_cfw_retained_easylogger_async_queue_statistics
                .failed_operation_count++;
            return (struct open_cfw_easylogger_async_queue_record *)0;
        }

        if (
            open_cfw_easylogger_atomic_compare_exchange_adapter(
                &open_cfw_retained_easylogger_async_free_head,
                &head,
                next
            ) != 0U
        ) {
            break;
        }
    }

    open_cfw_easylogger_async_queue_note_success(
        attempts,
        &open_cfw_retained_easylogger_async_queue_statistics
            .allocate_retry_total,
        &open_cfw_retained_easylogger_async_queue_statistics
            .allocate_attempt_maximum
    );
    /* Stock calls the inner store directly for state, but its typed adapter
     * for the intrusive next link.  Keep that distinction observable. */
    open_cfw_retained_easylogger_atomic_store_primitive(&record->state, 1U);
    open_cfw_easylogger_atomic_store_adapter(&record->next, 0U);
    return record;
}

OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_NOINLINE
void open_cfw_easylogger_async_queue_record_recycle(
    struct open_cfw_easylogger_async_queue_record *record
)
{
    open_cfw_easylogger_async_queue_u32 head;
    open_cfw_easylogger_async_queue_u32 address;
    open_cfw_easylogger_async_queue_u32 attempts = 0U;

    if (record == (struct open_cfw_easylogger_async_queue_record *)0) {
        return;
    }

    open_cfw_retained_easylogger_atomic_store_primitive(&record->state, 0U);
    address = open_cfw_easylogger_async_queue_address_from_record(record);

    for (;;) {
        head = open_cfw_easylogger_atomic_load_adapter(
            &open_cfw_retained_easylogger_async_free_head
        );
        open_cfw_easylogger_atomic_store_adapter(&record->next, head);
        attempts++;
        if (
            attempts >
                OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_ALLOCATE_RETRY_LIMIT
        ) {
            open_cfw_retained_easylogger_async_queue_statistics
                .retry_limit_count++;
            return;
        }

        if (
            open_cfw_easylogger_atomic_compare_exchange_adapter(
                &open_cfw_retained_easylogger_async_free_head,
                &head,
                address
            ) != 0U
        ) {
            break;
        }
    }

    open_cfw_easylogger_async_queue_note_success(
        attempts,
        &open_cfw_retained_easylogger_async_queue_statistics
            .recycle_retry_total,
        &open_cfw_retained_easylogger_async_queue_statistics
            .recycle_attempt_maximum
    );
}

open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_async_queue_record_enqueue(
    struct open_cfw_easylogger_async_queue_record *record
)
{
    struct open_cfw_easylogger_async_queue_record *tail_record;
    open_cfw_easylogger_async_queue_u32 address;
    open_cfw_easylogger_async_queue_u32 tail;
    open_cfw_easylogger_async_queue_u32 next;
    open_cfw_easylogger_async_queue_u32 observed_tail;
    open_cfw_easylogger_async_queue_u32 expected;
    open_cfw_easylogger_async_queue_u32 attempts = 0U;

    if (record == (struct open_cfw_easylogger_async_queue_record *)0) {
        return 0U;
    }

    address = open_cfw_easylogger_async_queue_address_from_record(record);
    open_cfw_retained_easylogger_atomic_store_primitive(&record->state, 2U);
    open_cfw_easylogger_atomic_store_adapter(&record->next, 0U);

    for (;;) {
        tail = open_cfw_easylogger_atomic_load_adapter(
            &open_cfw_retained_easylogger_async_queue_tail
        );
        tail_record = open_cfw_easylogger_async_queue_record_from_address(
            tail
        );
        next = open_cfw_easylogger_atomic_load_adapter(&tail_record->next);
        attempts++;
        if (
            attempts > OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_ENQUEUE_RETRY_LIMIT
        ) {
            open_cfw_retained_easylogger_async_queue_statistics
                .retry_limit_count++;
            open_cfw_retained_easylogger_async_queue_statistics
                .failed_operation_count++;
            open_cfw_easylogger_async_queue_record_recycle(record);
            return 0U;
        }

        observed_tail = open_cfw_easylogger_atomic_load_adapter(
            &open_cfw_retained_easylogger_async_queue_tail
        );
        if (tail != observed_tail) {
            continue;
        }

        if (next != 0U) {
            expected = tail;
            (void)open_cfw_easylogger_atomic_compare_exchange_adapter(
                &open_cfw_retained_easylogger_async_queue_tail,
                &expected,
                next
            );
            continue;
        }

        expected = next;
        if (
            open_cfw_easylogger_atomic_compare_exchange_adapter(
                &tail_record->next,
                &expected,
                address
            ) != 0U
        ) {
            break;
        }
    }

    open_cfw_easylogger_async_queue_note_success(
        attempts,
        &open_cfw_retained_easylogger_async_queue_statistics
            .enqueue_retry_total,
        &open_cfw_retained_easylogger_async_queue_statistics
            .enqueue_attempt_maximum
    );
    expected = tail;
    (void)open_cfw_easylogger_atomic_compare_exchange_adapter(
        &open_cfw_retained_easylogger_async_queue_tail,
        &expected,
        address
    );
    return 1U;
}

#undef OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_NOINLINE
