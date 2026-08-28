/*
 * SPDX-License-Identifier: MIT
 *
 * Deterministic host schedule oracle for the G2 EasyLogger lock-free queue
 * candidate.  Synthetic 32-bit tokens preserve the target pointer ABI on
 * 64-bit hosts.  Every injected CAS conflict first performs a real competing
 * word mutation; the retained strong primitive itself never fails spuriously.
 */

#include <stdint.h>
#include <string.h>

#define OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_HOST_ORACLE 1
#define open_cfw_retained_easylogger_async_record_pool \
    open_cfw_test_easylogger_async_queue_pool
#include "../../components/shared/easylogger/runtime_easylogger_async_queue_candidate.h"

enum {
    OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_COUNT = 256U,
    OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE = 0x202D3FC8U,
    OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_STRIDE = 0x110U,
    OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_NEVER = 0xFFFFFFFFU
};

volatile open_cfw_easylogger_async_queue_u32
    open_cfw_retained_easylogger_async_free_head;
volatile open_cfw_easylogger_async_queue_u32
    open_cfw_retained_easylogger_async_queue_head;
volatile open_cfw_easylogger_async_queue_u32
    open_cfw_retained_easylogger_async_queue_tail;
struct open_cfw_easylogger_async_queue_statistics
    open_cfw_retained_easylogger_async_queue_statistics;

struct open_cfw_easylogger_async_queue_record
    open_cfw_test_easylogger_async_queue_pool[
        OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_COUNT
    ];

open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_primitive_load_calls;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_primitive_store_calls;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_primitive_cas_calls;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_state_store_calls;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_next_store_calls;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_free_cas_calls;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_link_cas_calls;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_tail_cas_calls;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_head_cas_calls;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_tail_load_calls;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_head_load_calls;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_free_failures_remaining;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_link_failures_remaining;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_tail_failures_remaining;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_head_failures_remaining;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_tail_mutate_on_load;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_tail_mutate_value;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_tail_snapshot_conflicts_remaining;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_head_snapshot_conflicts_remaining;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_competing_mutation_count;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_bad_address_count;

static open_cfw_easylogger_async_queue_u32
open_cfw_test_easylogger_async_queue_record_index(
    const struct open_cfw_easylogger_async_queue_record *record
)
{
    open_cfw_easylogger_async_queue_u32 index;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_COUNT;
        index++
    ) {
        if (record == &open_cfw_test_easylogger_async_queue_pool[index]) {
            return index;
        }
    }
    open_cfw_test_easylogger_async_queue_bad_address_count++;
    return OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_COUNT;
}

struct open_cfw_easylogger_async_queue_record *
open_cfw_easylogger_async_queue_host_record_from_address(
    open_cfw_easylogger_async_queue_u32 address
)
{
    open_cfw_easylogger_async_queue_u32 delta;
    open_cfw_easylogger_async_queue_u32 index;

    if (address < OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE) {
        open_cfw_test_easylogger_async_queue_bad_address_count++;
        return &open_cfw_test_easylogger_async_queue_pool[0];
    }
    delta = address - OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE;
    if ((delta % OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_STRIDE) != 0U) {
        open_cfw_test_easylogger_async_queue_bad_address_count++;
        return &open_cfw_test_easylogger_async_queue_pool[0];
    }
    index = delta / OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_STRIDE;
    if (index >= OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_COUNT) {
        open_cfw_test_easylogger_async_queue_bad_address_count++;
        return &open_cfw_test_easylogger_async_queue_pool[0];
    }
    return &open_cfw_test_easylogger_async_queue_pool[index];
}

open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_async_queue_host_address_from_record(
    const struct open_cfw_easylogger_async_queue_record *record
)
{
    open_cfw_easylogger_async_queue_u32 index =
        open_cfw_test_easylogger_async_queue_record_index(record);
    if (index >= OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_COUNT) {
        return 0U;
    }
    return OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE +
        index * OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_STRIDE;
}

static open_cfw_easylogger_async_queue_u32
open_cfw_test_easylogger_async_queue_is_record_word(
    const volatile open_cfw_easylogger_async_queue_u32 *object,
    open_cfw_easylogger_async_queue_u32 word_offset
)
{
    open_cfw_easylogger_async_queue_u32 index;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_COUNT;
        index++
    ) {
        const volatile open_cfw_easylogger_async_queue_u32 *candidate =
            word_offset == 0U
                ? &open_cfw_test_easylogger_async_queue_pool[index].next
                : &open_cfw_test_easylogger_async_queue_pool[index].state;
        if (object == candidate) {
            return 1U;
        }
    }
    return 0U;
}

void open_cfw_retained_easylogger_atomic_store_primitive(
    volatile open_cfw_easylogger_async_queue_u32 *object,
    open_cfw_easylogger_async_queue_u32 value
)
{
    open_cfw_test_easylogger_async_queue_primitive_store_calls++;
    if (open_cfw_test_easylogger_async_queue_is_record_word(object, 4U)) {
        open_cfw_test_easylogger_async_queue_state_store_calls++;
    } else if (
        open_cfw_test_easylogger_async_queue_is_record_word(object, 0U)
    ) {
        open_cfw_test_easylogger_async_queue_next_store_calls++;
    }
    *object = value;
}

open_cfw_easylogger_async_queue_u32
open_cfw_retained_easylogger_atomic_load_primitive(
    const volatile open_cfw_easylogger_async_queue_u32 *object
)
{
    open_cfw_test_easylogger_async_queue_primitive_load_calls++;
    if (object == &open_cfw_retained_easylogger_async_queue_tail) {
        open_cfw_test_easylogger_async_queue_tail_load_calls++;
        if (
            open_cfw_test_easylogger_async_queue_tail_mutate_on_load != 0U &&
            open_cfw_test_easylogger_async_queue_tail_load_calls ==
                open_cfw_test_easylogger_async_queue_tail_mutate_on_load
        ) {
            open_cfw_retained_easylogger_async_queue_tail =
                open_cfw_test_easylogger_async_queue_tail_mutate_value;
        }
        if (
            (open_cfw_test_easylogger_async_queue_tail_load_calls & 1U) == 0U
            && open_cfw_test_easylogger_async_queue_tail_snapshot_conflicts_remaining
                != 0U
        ) {
            if (
                open_cfw_test_easylogger_async_queue_tail_snapshot_conflicts_remaining
                    != OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_NEVER
            ) {
                open_cfw_test_easylogger_async_queue_tail_snapshot_conflicts_remaining--;
            }
            open_cfw_retained_easylogger_async_queue_tail =
                open_cfw_retained_easylogger_async_queue_tail ==
                        OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE
                    ? OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE +
                        2U * OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_STRIDE
                    : OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE;
            open_cfw_test_easylogger_async_queue_competing_mutation_count++;
        }
    } else if (object == &open_cfw_retained_easylogger_async_queue_head) {
        open_cfw_test_easylogger_async_queue_head_load_calls++;
        if (
            (open_cfw_test_easylogger_async_queue_head_load_calls & 1U) == 0U
            && open_cfw_test_easylogger_async_queue_head_snapshot_conflicts_remaining
                != 0U
        ) {
            if (
                open_cfw_test_easylogger_async_queue_head_snapshot_conflicts_remaining
                    != OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_NEVER
            ) {
                open_cfw_test_easylogger_async_queue_head_snapshot_conflicts_remaining--;
            }
            open_cfw_retained_easylogger_async_queue_head =
                open_cfw_retained_easylogger_async_queue_head ==
                        OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE
                    ? OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE +
                        2U * OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_STRIDE
                    : OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE;
            open_cfw_test_easylogger_async_queue_competing_mutation_count++;
        }
    }
    return *object;
}

static open_cfw_easylogger_async_queue_u32
open_cfw_test_easylogger_async_queue_take_conflict(
    open_cfw_easylogger_async_queue_u32 *remaining
)
{
    if (*remaining == 0U) {
        return 0U;
    }
    if (*remaining != OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_NEVER) {
        (*remaining)--;
    }
    return 1U;
}

open_cfw_easylogger_async_queue_u32
open_cfw_retained_easylogger_atomic_compare_exchange_strong_primitive(
    volatile open_cfw_easylogger_async_queue_u32 *object,
    open_cfw_easylogger_async_queue_u32 *expected,
    open_cfw_easylogger_async_queue_u32 desired
)
{
    open_cfw_easylogger_async_queue_u32 inject_conflict = 0U;
    open_cfw_easylogger_async_queue_u32 conflict_kind = 0U;
    open_cfw_easylogger_async_queue_u32 original;
    open_cfw_easylogger_async_queue_u32 competing;

    open_cfw_test_easylogger_async_queue_primitive_cas_calls++;
    if (object == &open_cfw_retained_easylogger_async_free_head) {
        conflict_kind = 1U;
        open_cfw_test_easylogger_async_queue_free_cas_calls++;
        inject_conflict = open_cfw_test_easylogger_async_queue_take_conflict(
            &open_cfw_test_easylogger_async_queue_free_failures_remaining
        );
    } else if (object == &open_cfw_retained_easylogger_async_queue_tail) {
        conflict_kind = 2U;
        open_cfw_test_easylogger_async_queue_tail_cas_calls++;
        inject_conflict = open_cfw_test_easylogger_async_queue_take_conflict(
            &open_cfw_test_easylogger_async_queue_tail_failures_remaining
        );
    } else if (object == &open_cfw_retained_easylogger_async_queue_head) {
        conflict_kind = 4U;
        open_cfw_test_easylogger_async_queue_head_cas_calls++;
        inject_conflict = open_cfw_test_easylogger_async_queue_take_conflict(
            &open_cfw_test_easylogger_async_queue_head_failures_remaining
        );
    } else if (open_cfw_test_easylogger_async_queue_is_record_word(object, 0U)) {
        conflict_kind = 3U;
        open_cfw_test_easylogger_async_queue_link_cas_calls++;
        inject_conflict = open_cfw_test_easylogger_async_queue_take_conflict(
            &open_cfw_test_easylogger_async_queue_link_failures_remaining
        );
    }

    original = *object;
    if (inject_conflict != 0U) {
        if (conflict_kind == 1U) {
            competing = original ==
                    OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE +
                        2U * OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_STRIDE
                ? OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE +
                    3U * OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_STRIDE
                : OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE +
                    2U * OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_STRIDE;
        } else if (conflict_kind == 2U) {
            competing = original == OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE
                ? OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE +
                    2U * OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_STRIDE
                : OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE;
        } else if (conflict_kind == 3U) {
            competing = original ==
                    OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE +
                        3U * OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_STRIDE
                ? OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE +
                    2U * OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_STRIDE
                : OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE +
                    3U * OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_STRIDE;
        } else {
            competing = original == OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE
                ? OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE +
                    2U * OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_STRIDE
                : OPEN_CFW_TEST_EASYLOGGER_ASYNC_QUEUE_POOL_BASE;
        }
        *object = competing;
        open_cfw_test_easylogger_async_queue_competing_mutation_count++;
    }

    if (*object != *expected) {
        *expected = *object;
        if (inject_conflict != 0U) {
            /* A competing operation transitions the word back after the
             * failed strong CAS, providing a deterministic ABA schedule. */
            *object = original;
        }
        return 0U;
    }
    *object = desired;
    return 1U;
}

#include "../../components/shared/easylogger/runtime_easylogger_async_queue_candidate.c"

/* Compile the corrected level-less builder against the real queue candidate,
 * not a mock enqueue.  The two independently recovered record declarations
 * are required to remain layout-compatible until a later authorized refactor
 * can move them into a single production-neutral ABI header. */
#include "../../components/shared/easylogger/runtime_easylogger_hexdump_seams.c"

_Static_assert(
    sizeof(struct open_cfw_easylogger_hexdump_record) ==
        sizeof(struct open_cfw_easylogger_async_queue_record),
    "EasyLogger builder/queue record sizes diverged"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_easylogger_hexdump_record, payload) ==
        __builtin_offsetof(struct open_cfw_easylogger_async_queue_record, payload),
    "EasyLogger builder/queue payload offsets diverged"
);

volatile open_cfw_easylogger_hexdump_seam_u8
    open_cfw_retained_easylogger_async_ready = 1U;
volatile open_cfw_easylogger_hexdump_seam_u8
    open_cfw_retained_easylogger_async_default_metadata = 0x42U;
open_cfw_easylogger_async_queue_u32
    open_cfw_test_easylogger_async_queue_diagnostic_calls;

struct open_cfw_easylogger_hexdump_record *
open_cfw_retained_easylogger_async_record_allocate(void)
{
    return (struct open_cfw_easylogger_hexdump_record *)
        open_cfw_easylogger_async_queue_record_allocate();
}

open_cfw_easylogger_hexdump_seam_u32
open_cfw_retained_easylogger_async_record_enqueue(
    struct open_cfw_easylogger_hexdump_record *record
)
{
    return open_cfw_easylogger_async_queue_record_enqueue(
        (struct open_cfw_easylogger_async_queue_record *)record
    );
}

void open_cfw_retained_easylogger_async_diagnostic(const char *message)
{
    (void)message;
    open_cfw_test_easylogger_async_queue_diagnostic_calls++;
}

void open_cfw_test_easylogger_async_queue_reset(
    open_cfw_easylogger_async_queue_u32 free_head,
    open_cfw_easylogger_async_queue_u32 queue_tail
)
{
    memset(
        open_cfw_test_easylogger_async_queue_pool,
        0,
        sizeof(open_cfw_test_easylogger_async_queue_pool)
    );
    memset(
        &open_cfw_retained_easylogger_async_queue_statistics,
        0,
        sizeof(open_cfw_retained_easylogger_async_queue_statistics)
    );
    open_cfw_retained_easylogger_async_free_head = free_head;
    open_cfw_retained_easylogger_async_queue_head = queue_tail;
    open_cfw_retained_easylogger_async_queue_tail = queue_tail;
    open_cfw_test_easylogger_async_queue_primitive_load_calls = 0U;
    open_cfw_test_easylogger_async_queue_primitive_store_calls = 0U;
    open_cfw_test_easylogger_async_queue_primitive_cas_calls = 0U;
    open_cfw_test_easylogger_async_queue_state_store_calls = 0U;
    open_cfw_test_easylogger_async_queue_next_store_calls = 0U;
    open_cfw_test_easylogger_async_queue_free_cas_calls = 0U;
    open_cfw_test_easylogger_async_queue_link_cas_calls = 0U;
    open_cfw_test_easylogger_async_queue_tail_cas_calls = 0U;
    open_cfw_test_easylogger_async_queue_head_cas_calls = 0U;
    open_cfw_test_easylogger_async_queue_tail_load_calls = 0U;
    open_cfw_test_easylogger_async_queue_head_load_calls = 0U;
    open_cfw_test_easylogger_async_queue_free_failures_remaining = 0U;
    open_cfw_test_easylogger_async_queue_link_failures_remaining = 0U;
    open_cfw_test_easylogger_async_queue_tail_failures_remaining = 0U;
    open_cfw_test_easylogger_async_queue_head_failures_remaining = 0U;
    open_cfw_test_easylogger_async_queue_tail_mutate_on_load = 0U;
    open_cfw_test_easylogger_async_queue_tail_mutate_value = 0U;
    open_cfw_test_easylogger_async_queue_tail_snapshot_conflicts_remaining = 0U;
    open_cfw_test_easylogger_async_queue_head_snapshot_conflicts_remaining = 0U;
    open_cfw_test_easylogger_async_queue_competing_mutation_count = 0U;
    open_cfw_test_easylogger_async_queue_bad_address_count = 0U;
    open_cfw_test_easylogger_async_queue_diagnostic_calls = 0U;
    open_cfw_retained_easylogger_async_ready = 1U;
    open_cfw_retained_easylogger_async_default_metadata = 0x42U;
}

void open_cfw_test_easylogger_async_queue_set_record(
    open_cfw_easylogger_async_queue_u32 token,
    open_cfw_easylogger_async_queue_u32 next,
    open_cfw_easylogger_async_queue_u32 state
)
{
    struct open_cfw_easylogger_async_queue_record *record =
        open_cfw_easylogger_async_queue_host_record_from_address(token);
    record->next = next;
    record->state = state;
}

void open_cfw_test_easylogger_async_queue_schedule(
    open_cfw_easylogger_async_queue_u32 free_failures,
    open_cfw_easylogger_async_queue_u32 link_failures,
    open_cfw_easylogger_async_queue_u32 tail_failures,
    open_cfw_easylogger_async_queue_u32 tail_mutate_on_load,
    open_cfw_easylogger_async_queue_u32 tail_mutate_value,
    open_cfw_easylogger_async_queue_u32 tail_snapshot_conflicts
)
{
    open_cfw_test_easylogger_async_queue_free_failures_remaining =
        free_failures;
    open_cfw_test_easylogger_async_queue_link_failures_remaining =
        link_failures;
    open_cfw_test_easylogger_async_queue_tail_failures_remaining =
        tail_failures;
    open_cfw_test_easylogger_async_queue_tail_mutate_on_load =
        tail_mutate_on_load;
    open_cfw_test_easylogger_async_queue_tail_mutate_value =
        tail_mutate_value;
    open_cfw_test_easylogger_async_queue_tail_snapshot_conflicts_remaining =
        tail_snapshot_conflicts;
}

void open_cfw_test_easylogger_async_queue_dequeue_schedule(
    open_cfw_easylogger_async_queue_u32 head_failures,
    open_cfw_easylogger_async_queue_u32 head_snapshot_conflicts
)
{
    open_cfw_test_easylogger_async_queue_head_failures_remaining =
        head_failures;
    open_cfw_test_easylogger_async_queue_head_snapshot_conflicts_remaining =
        head_snapshot_conflicts;
}

open_cfw_easylogger_async_queue_u32
open_cfw_test_easylogger_async_queue_allocate(void)
{
    struct open_cfw_easylogger_async_queue_record *record =
        open_cfw_easylogger_async_queue_record_allocate();
    if (record == (struct open_cfw_easylogger_async_queue_record *)0) {
        return 0U;
    }
    return open_cfw_easylogger_async_queue_host_address_from_record(record);
}

void open_cfw_test_easylogger_async_queue_recycle(
    open_cfw_easylogger_async_queue_u32 token
)
{
    struct open_cfw_easylogger_async_queue_record *record =
        (token == 0U)
            ? (struct open_cfw_easylogger_async_queue_record *)0
            : open_cfw_easylogger_async_queue_host_record_from_address(token);
    open_cfw_easylogger_async_queue_record_recycle(record);
}

open_cfw_easylogger_async_queue_u32
open_cfw_test_easylogger_async_queue_enqueue(
    open_cfw_easylogger_async_queue_u32 token
)
{
    struct open_cfw_easylogger_async_queue_record *record =
        (token == 0U)
            ? (struct open_cfw_easylogger_async_queue_record *)0
            : open_cfw_easylogger_async_queue_host_record_from_address(token);
    return open_cfw_easylogger_async_queue_record_enqueue(record);
}

void open_cfw_test_easylogger_async_queue_pool_initialize(void)
{
    open_cfw_easylogger_async_queue_pool_initialize();
}

void open_cfw_test_easylogger_async_queue_dummy_reset(void)
{
    open_cfw_easylogger_async_queue_reset();
}

open_cfw_easylogger_async_queue_u32
open_cfw_test_easylogger_async_queue_initialize(void)
{
    return open_cfw_easylogger_async_queue_initialize();
}

open_cfw_easylogger_async_queue_u32
open_cfw_test_easylogger_async_queue_dequeue(void)
{
    struct open_cfw_easylogger_async_queue_record *record =
        open_cfw_easylogger_async_queue_record_dequeue();
    if (record == (struct open_cfw_easylogger_async_queue_record *)0) {
        return 0U;
    }
    return open_cfw_easylogger_async_queue_host_address_from_record(record);
}

open_cfw_easylogger_async_queue_u32
open_cfw_test_easylogger_async_queue_build_level_less(
    const char *buffer,
    open_cfw_easylogger_async_queue_u32 length,
    open_cfw_easylogger_async_queue_u32 metadata
)
{
    return open_cfw_g2_easylogger_async_record_build_level_less(
        buffer,
        length,
        metadata
    );
}

void open_cfw_test_easylogger_async_queue_probe_bad_address(
    open_cfw_easylogger_async_queue_u32 token
)
{
    (void)open_cfw_easylogger_async_queue_host_record_from_address(token);
}
