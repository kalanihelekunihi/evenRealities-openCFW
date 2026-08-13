/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production-excluded clean-room candidate for the G2 EasyLogger fixed-record
 * pool initialization, dummy queue, allocator, recycler, enqueue, dequeue,
 * and state-initialization cluster.
 */

#ifndef OPEN_CFW_RUNTIME_EASYLOGGER_ASYNC_QUEUE_CANDIDATE_H
#define OPEN_CFW_RUNTIME_EASYLOGGER_ASYNC_QUEUE_CANDIDATE_H

typedef __UINT8_TYPE__ open_cfw_easylogger_async_queue_u8;
typedef __UINT16_TYPE__ open_cfw_easylogger_async_queue_u16;
typedef __UINT32_TYPE__ open_cfw_easylogger_async_queue_u32;
typedef __UINTPTR_TYPE__ open_cfw_easylogger_async_queue_uintptr;

enum {
    OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_RECORD_BYTES = 0x110U,
    OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_RECORD_COUNT = 256U,
    OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_INITIAL_DUMMY_INDEX = 255U,
    OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_ALLOCATE_RETRY_LIMIT = 1000U,
    OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_ENQUEUE_RETRY_LIMIT = 10000U,
    OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_DEQUEUE_RETRY_LIMIT = 10000U
};

struct open_cfw_easylogger_async_queue_record {
    volatile open_cfw_easylogger_async_queue_u32 next;
    volatile open_cfw_easylogger_async_queue_u32 state;
    open_cfw_easylogger_async_queue_u16 length;
    open_cfw_easylogger_async_queue_u16 metadata;
    open_cfw_easylogger_async_queue_u8 level;
    open_cfw_easylogger_async_queue_u8 payload[256];
    open_cfw_easylogger_async_queue_u8 padding[3];
};

/*
 * The names describe observed use, not an upstream ABI.  Reserved words are
 * retained so every recovered offset in the 48-byte G2 statistics block is
 * explicit and statically checked.
 */
struct open_cfw_easylogger_async_queue_statistics {
    volatile open_cfw_easylogger_async_queue_u32 drained_record_count;
    volatile open_cfw_easylogger_async_queue_u32 failed_operation_count;
    volatile open_cfw_easylogger_async_queue_u32 reserved_08;
    volatile open_cfw_easylogger_async_queue_u32 allocate_retry_total;
    volatile open_cfw_easylogger_async_queue_u32 allocate_attempt_maximum;
    volatile open_cfw_easylogger_async_queue_u32 recycle_retry_total;
    volatile open_cfw_easylogger_async_queue_u32 recycle_attempt_maximum;
    volatile open_cfw_easylogger_async_queue_u32 enqueue_retry_total;
    volatile open_cfw_easylogger_async_queue_u32 enqueue_attempt_maximum;
    volatile open_cfw_easylogger_async_queue_u32 dequeue_retry_total;
    volatile open_cfw_easylogger_async_queue_u32 dequeue_attempt_maximum;
    volatile open_cfw_easylogger_async_queue_u32 retry_limit_count;
};

_Static_assert(
    sizeof(struct open_cfw_easylogger_async_queue_record) == 0x110U,
    "G2 EasyLogger async record stride changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_easylogger_async_queue_record, next) ==
        0x00U,
    "G2 EasyLogger async next offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_easylogger_async_queue_record, state) ==
        0x04U,
    "G2 EasyLogger async state offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_easylogger_async_queue_record, length) ==
        0x08U,
    "G2 EasyLogger async length offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_async_queue_statistics,
        drained_record_count
    ) == 0x00U,
    "G2 EasyLogger async drained-count offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_async_queue_statistics,
        dequeue_retry_total
    ) == 0x24U,
    "G2 EasyLogger async dequeue-total offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_async_queue_statistics,
        dequeue_attempt_maximum
    ) == 0x28U,
    "G2 EasyLogger async dequeue-maximum offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_async_queue_record,
        metadata
    ) == 0x0AU,
    "G2 EasyLogger async metadata offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_easylogger_async_queue_record, level) ==
        0x0CU,
    "G2 EasyLogger async level offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_async_queue_record,
        payload
    ) == 0x0DU,
    "G2 EasyLogger async payload offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_async_queue_record,
        padding
    ) == 0x10DU,
    "G2 EasyLogger async padding offset changed"
);

_Static_assert(
    sizeof(struct open_cfw_easylogger_async_queue_statistics) == 0x30U,
    "G2 EasyLogger async statistics size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_async_queue_statistics,
        failed_operation_count
    ) == 0x04U,
    "G2 EasyLogger async failure statistic offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_async_queue_statistics,
        allocate_retry_total
    ) == 0x0CU,
    "G2 EasyLogger async allocate-total offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_async_queue_statistics,
        allocate_attempt_maximum
    ) == 0x10U,
    "G2 EasyLogger async allocate-maximum offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_async_queue_statistics,
        recycle_retry_total
    ) == 0x14U,
    "G2 EasyLogger async recycle-total offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_async_queue_statistics,
        recycle_attempt_maximum
    ) == 0x18U,
    "G2 EasyLogger async recycle-maximum offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_async_queue_statistics,
        enqueue_retry_total
    ) == 0x1CU,
    "G2 EasyLogger async enqueue-total offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_async_queue_statistics,
        enqueue_attempt_maximum
    ) == 0x20U,
    "G2 EasyLogger async enqueue-maximum offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_async_queue_statistics,
        retry_limit_count
    ) == 0x2CU,
    "G2 EasyLogger async retry-limit offset changed"
);

extern volatile open_cfw_easylogger_async_queue_u32
    open_cfw_retained_easylogger_async_free_head;
extern volatile open_cfw_easylogger_async_queue_u32
    open_cfw_retained_easylogger_async_queue_head;
extern volatile open_cfw_easylogger_async_queue_u32
    open_cfw_retained_easylogger_async_queue_tail;
extern struct open_cfw_easylogger_async_queue_statistics
    open_cfw_retained_easylogger_async_queue_statistics;
extern struct open_cfw_easylogger_async_queue_record
    open_cfw_retained_easylogger_async_record_pool[
        OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_RECORD_COUNT
    ];
extern volatile open_cfw_easylogger_async_queue_u8
    open_cfw_retained_easylogger_async_ready;
extern volatile open_cfw_easylogger_async_queue_u8
    open_cfw_retained_easylogger_async_default_metadata;

/*
 * Retained inner primitives at 0x004488EC, 0x004488F4, and 0x004488FC.
 * The strong compare/exchange never fails spuriously and updates expected
 * when the observed word differs.
 */
extern void open_cfw_retained_easylogger_atomic_store_primitive(
    volatile open_cfw_easylogger_async_queue_u32 *object,
    open_cfw_easylogger_async_queue_u32 value
);
extern open_cfw_easylogger_async_queue_u32
open_cfw_retained_easylogger_atomic_load_primitive(
    const volatile open_cfw_easylogger_async_queue_u32 *object
);
extern open_cfw_easylogger_async_queue_u32
open_cfw_retained_easylogger_atomic_compare_exchange_strong_primitive(
    volatile open_cfw_easylogger_async_queue_u32 *object,
    open_cfw_easylogger_async_queue_u32 *expected,
    open_cfw_easylogger_async_queue_u32 desired
);

/* Source adapters matching the typed wrappers at 0x00448930..0x0044895E. */
void open_cfw_easylogger_atomic_store_adapter(
    volatile open_cfw_easylogger_async_queue_u32 *object,
    open_cfw_easylogger_async_queue_u32 value
);
open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_atomic_load_adapter(
    const volatile open_cfw_easylogger_async_queue_u32 *object
);
open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_atomic_compare_exchange_adapter(
    volatile open_cfw_easylogger_async_queue_u32 *object,
    open_cfw_easylogger_async_queue_u32 *expected,
    open_cfw_easylogger_async_queue_u32 desired
);

#if defined(OPEN_CFW_EASYLOGGER_ASYNC_QUEUE_HOST_ORACLE)
extern struct open_cfw_easylogger_async_queue_record *
open_cfw_easylogger_async_queue_host_record_from_address(
    open_cfw_easylogger_async_queue_u32 address
);
extern open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_async_queue_host_address_from_record(
    const struct open_cfw_easylogger_async_queue_record *record
);
#endif

void open_cfw_easylogger_async_queue_pool_initialize(void);
void open_cfw_easylogger_async_queue_reset(void);
open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_async_queue_initialize(void);

struct open_cfw_easylogger_async_queue_record *
open_cfw_easylogger_async_queue_record_allocate(void);

void open_cfw_easylogger_async_queue_record_recycle(
    struct open_cfw_easylogger_async_queue_record *record
);

/*
 * A nonnull argument is consumed on every return: success transfers it to
 * the queue; retry exhaustion invokes the source-local recycler exactly once.
 */
open_cfw_easylogger_async_queue_u32
open_cfw_easylogger_async_queue_record_enqueue(
    struct open_cfw_easylogger_async_queue_record *record
);

struct open_cfw_easylogger_async_queue_record *
open_cfw_easylogger_async_queue_record_dequeue(void);

#endif
