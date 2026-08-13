/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room BLE receive-record construction and enqueue reconstructed from
 * stock Thread_MsgRxFromBle at 0x0048F12C...0x0048F323.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_msgrx_enqueue_uintptr;

#define OPEN_CFW_BLE_MSGRX_STATE_ADDRESS 0x20003FFCU
#define OPEN_CFW_BLE_MSGRX_QUEUE_FLAG 0x00400000U
#define OPEN_CFW_BLE_MSGRX_QUEUE_TIMEOUT 500U

typedef struct {
    unsigned int reserved_0;
    unsigned int reserved_4;
    unsigned int thread;
    unsigned int queue;
} open_cfw_ble_msgrx_enqueue_state;

typedef struct {
    unsigned int type;
    unsigned int length;
    unsigned char payload[];
} open_cfw_ble_msgrx_enqueue_record;

#ifndef OPEN_CFW_BLE_MSGRX_ENQUEUE_STATE
#define OPEN_CFW_BLE_MSGRX_ENQUEUE_STATE \
    ((volatile open_cfw_ble_msgrx_enqueue_state *) \
        (open_cfw_ble_msgrx_enqueue_uintptr)OPEN_CFW_BLE_MSGRX_STATE_ADDRESS)
#endif

#ifndef OPEN_CFW_BLE_MSGRX_ALLOCATE
typedef void *(*open_cfw_ble_msgrx_allocate_function)(unsigned int);
#define OPEN_CFW_BLE_MSGRX_ALLOCATE(size) \
    (((open_cfw_ble_msgrx_allocate_function)0x00474CD3U)((size)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_FREE
typedef void (*open_cfw_ble_msgrx_enqueue_free_function)(void *);
#define OPEN_CFW_BLE_MSGRX_FREE(pointer) \
    (((open_cfw_ble_msgrx_enqueue_free_function)0x00474D17U)((pointer)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_MEMSET
typedef void *(*open_cfw_ble_msgrx_memset_function)(
    void *,
    int,
    unsigned int
);
#define OPEN_CFW_BLE_MSGRX_MEMSET(destination, value, length) \
    (((open_cfw_ble_msgrx_memset_function)0x0043C0E5U)( \
        (destination), (value), (length)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_MEMCPY
typedef void *(*open_cfw_ble_msgrx_memcpy_function)(
    void *,
    const void *,
    unsigned int
);
#define OPEN_CFW_BLE_MSGRX_MEMCPY(destination, source, length) \
    (((open_cfw_ble_msgrx_memcpy_function)0x00439BE5U)( \
        (destination), (source), (length)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_QUEUE_COUNT
typedef unsigned int (*open_cfw_ble_msgrx_enqueue_queue_count_function)(
    void *
);
#define OPEN_CFW_BLE_MSGRX_QUEUE_COUNT(queue) \
    (((open_cfw_ble_msgrx_enqueue_queue_count_function)0x00449BC9U)((queue)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_QUEUE_CAPACITY
typedef unsigned int (*open_cfw_ble_msgrx_enqueue_queue_capacity_function)(
    void *
);
#define OPEN_CFW_BLE_MSGRX_QUEUE_CAPACITY(queue) \
    (((open_cfw_ble_msgrx_enqueue_queue_capacity_function)0x00449BBDU)( \
        (queue)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_QUEUE_PUT
typedef unsigned int (*open_cfw_ble_msgrx_queue_put_function)(
    void *,
    const void *,
    unsigned char,
    unsigned int
);
#define OPEN_CFW_BLE_MSGRX_QUEUE_PUT(queue, record, priority, timeout) \
    (((open_cfw_ble_msgrx_queue_put_function)0x00449ABFU)( \
        (queue), (record), (priority), (timeout)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_THREAD_FLAGS_SET
typedef unsigned int (*open_cfw_ble_msgrx_thread_flags_function)(
    void *,
    unsigned int
);
#define OPEN_CFW_BLE_MSGRX_THREAD_FLAGS_SET(thread, flags) \
    (((open_cfw_ble_msgrx_thread_flags_function)0x00449239U)( \
        (thread), (flags)))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_ble_msgrx_enqueue(
    unsigned int type,
    const void *payload,
    unsigned short length
)
{
    volatile open_cfw_ble_msgrx_enqueue_state *state =
        OPEN_CFW_BLE_MSGRX_ENQUEUE_STATE;
    open_cfw_ble_msgrx_enqueue_record *record;
    unsigned int result;
    unsigned int allocation_size;

    if (payload == (const void *)0 || state->queue == 0U) {
        return 0xFFFFFFFFU;
    }

    allocation_size = ((unsigned int)length + 11U) & ~3U;
    record = (open_cfw_ble_msgrx_enqueue_record *)
        OPEN_CFW_BLE_MSGRX_ALLOCATE(allocation_size);
    if (record == (open_cfw_ble_msgrx_enqueue_record *)0) {
        return 0xFFFFFFFFU;
    }

    OPEN_CFW_BLE_MSGRX_MEMSET(record->payload, 0, (unsigned int)length);
    record->type = type;
    record->length = (unsigned int)length;
    OPEN_CFW_BLE_MSGRX_MEMCPY(
        record->payload,
        payload,
        (unsigned int)length
    );

    (void)OPEN_CFW_BLE_MSGRX_QUEUE_COUNT(
        (void *)(open_cfw_ble_msgrx_enqueue_uintptr)state->queue
    );
    (void)OPEN_CFW_BLE_MSGRX_QUEUE_CAPACITY(
        (void *)(open_cfw_ble_msgrx_enqueue_uintptr)state->queue
    );
    result = OPEN_CFW_BLE_MSGRX_QUEUE_PUT(
        (void *)(open_cfw_ble_msgrx_enqueue_uintptr)state->queue,
        &record,
        0U,
        OPEN_CFW_BLE_MSGRX_QUEUE_TIMEOUT
    );
    if (result == 0U) {
        (void)OPEN_CFW_BLE_MSGRX_THREAD_FLAGS_SET(
            (void *)(open_cfw_ble_msgrx_enqueue_uintptr)state->thread,
            OPEN_CFW_BLE_MSGRX_QUEUE_FLAG
        );
        return 0U;
    }

    OPEN_CFW_BLE_MSGRX_FREE(record);
    return 0xFFFFFFFFU;
}
