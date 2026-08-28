/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room BLE message-receive queue dispatcher, flag router, exit, and
 * clear routines reconstructed from stock 0x0048EEAC...0x0048F125.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_msgrx_dispatch_uintptr;

#define OPEN_CFW_BLE_MSGRX_STATE_ADDRESS 0x20003FFCU
#define OPEN_CFW_BLE_MSGRX_QUEUE_FLAG 0x00400000U
#define OPEN_CFW_BLE_MSGRX_EXIT_FLAG 0x00800000U
#define OPEN_CFW_BLE_MSGRX_STAGE_INDEX 7U

typedef struct {
    unsigned int reserved_0;
    unsigned int reserved_4;
    unsigned int thread;
    unsigned int queue;
} open_cfw_ble_msgrx_dispatch_state;

typedef struct {
    unsigned int type;
    unsigned int length;
    unsigned char payload[];
} open_cfw_ble_msgrx_record;

#ifndef OPEN_CFW_BLE_MSGRX_DISPATCH_STATE
#define OPEN_CFW_BLE_MSGRX_DISPATCH_STATE \
    ((volatile open_cfw_ble_msgrx_dispatch_state *) \
        (open_cfw_ble_msgrx_dispatch_uintptr)OPEN_CFW_BLE_MSGRX_STATE_ADDRESS)
#endif

#ifndef OPEN_CFW_BLE_MSGRX_QUEUE_GET
typedef unsigned int (*open_cfw_ble_msgrx_queue_get_function)(
    void *,
    void *,
    unsigned char *,
    unsigned int
);
#define OPEN_CFW_BLE_MSGRX_QUEUE_GET(queue, record, priority, timeout) \
    (((open_cfw_ble_msgrx_queue_get_function)0x00449B3DU)( \
        (queue), (record), (priority), (timeout)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_QUEUE_COUNT
typedef unsigned int (*open_cfw_ble_msgrx_queue_count_function)(void *);
#define OPEN_CFW_BLE_MSGRX_QUEUE_COUNT(queue) \
    (((open_cfw_ble_msgrx_queue_count_function)0x00449BC9U)((queue)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_FREE
typedef void (*open_cfw_ble_msgrx_free_function)(void *);
#define OPEN_CFW_BLE_MSGRX_FREE(pointer) \
    (((open_cfw_ble_msgrx_free_function)0x00474D17U)((pointer)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_STAGE_EXIT
typedef void (*open_cfw_ble_msgrx_stage_exit_function)(unsigned int);
#define OPEN_CFW_BLE_MSGRX_STAGE_EXIT(index) \
    (((open_cfw_ble_msgrx_stage_exit_function)0x004C9C3DU)((index)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_DELAY
typedef unsigned int (*open_cfw_ble_msgrx_delay_function)(unsigned int);
#define OPEN_CFW_BLE_MSGRX_DELAY(ticks) \
    (((open_cfw_ble_msgrx_delay_function)0x00449377U)((ticks)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_ROUTE_80
typedef void (*open_cfw_ble_msgrx_route_80_function)(
    const void *,
    unsigned int
);
#define OPEN_CFW_BLE_MSGRX_ROUTE_80(payload, length) \
    (((open_cfw_ble_msgrx_route_80_function)0x004D83D9U)( \
        (payload), (length)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_ROUTE_C0
typedef void (*open_cfw_ble_msgrx_route_typed_function)(
    unsigned int,
    const void *,
    unsigned int
);
#define OPEN_CFW_BLE_MSGRX_ROUTE_C0(type, payload, length) \
    (((open_cfw_ble_msgrx_route_typed_function)0x00448671U)( \
        (type), (payload), (length)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_ROUTE_C4
#define OPEN_CFW_BLE_MSGRX_ROUTE_C4(type, payload, length) \
    (((open_cfw_ble_msgrx_route_typed_function)0x00458B61U)( \
        (type), (payload), (length)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_ROUTE_200
typedef void (*open_cfw_ble_msgrx_route_200_function)(
    unsigned int,
    const void *
);
#define OPEN_CFW_BLE_MSGRX_ROUTE_200(selector, payload) \
    (((open_cfw_ble_msgrx_route_200_function)0x004D9011U)( \
        (selector), (payload)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_ROUTE_400
typedef void (*open_cfw_ble_msgrx_route_400_function)(void);
#define OPEN_CFW_BLE_MSGRX_ROUTE_400() \
    (((open_cfw_ble_msgrx_route_400_function)0x00458C5FU)())
#endif

#ifndef OPEN_CFW_BLE_MSGRX_HEXDUMP
#define OPEN_CFW_BLE_MSGRX_HEXDUMP(payload, length) ((void)0)
#endif

__attribute__((used, noinline))
void open_cfw_ble_msgrx_queue_drain(void)
{
    volatile open_cfw_ble_msgrx_dispatch_state *state =
        OPEN_CFW_BLE_MSGRX_DISPATCH_STATE;
    open_cfw_ble_msgrx_record *record = (open_cfw_ble_msgrx_record *)0;

    while (OPEN_CFW_BLE_MSGRX_QUEUE_GET(
        (void *)(open_cfw_ble_msgrx_dispatch_uintptr)state->queue,
        &record,
        (unsigned char *)0,
        0U
    ) == 0U) {
        if (record == (open_cfw_ble_msgrx_record *)0) {
            continue;
        }

        if (record->type == 0x80U) {
            OPEN_CFW_BLE_MSGRX_ROUTE_80(
                record->payload,
                (unsigned short)record->length
            );
        } else if (record->type >= 0xC0U && record->type <= 0xC3U) {
            OPEN_CFW_BLE_MSGRX_ROUTE_C0(
                (unsigned char)record->type,
                record->payload,
                (unsigned short)record->length
            );
        } else if (record->type >= 0xC4U && record->type <= 0xC7U) {
            OPEN_CFW_BLE_MSGRX_ROUTE_C4(
                (unsigned char)record->type,
                record->payload,
                (unsigned short)record->length
            );
        } else if (record->type == 0x200U) {
            OPEN_CFW_BLE_MSGRX_HEXDUMP(record->payload, 16U);
            OPEN_CFW_BLE_MSGRX_ROUTE_200(3U, record->payload);
        } else if (record->type == 0x400U) {
            OPEN_CFW_BLE_MSGRX_ROUTE_400();
        }

        OPEN_CFW_BLE_MSGRX_FREE(record);
        record = (open_cfw_ble_msgrx_record *)0;
    }
}

__attribute__((used, noinline))
void open_cfw_ble_msgrx_exit(void)
{
    OPEN_CFW_BLE_MSGRX_STAGE_EXIT(OPEN_CFW_BLE_MSGRX_STAGE_INDEX);
    for (;;) {
        OPEN_CFW_BLE_MSGRX_DELAY(0xFFFFFFFFU);
    }
}

__attribute__((used, noinline))
void open_cfw_ble_msgrx_dispatch_flags(unsigned int flags)
{
    if ((flags & OPEN_CFW_BLE_MSGRX_QUEUE_FLAG) != 0U) {
        open_cfw_ble_msgrx_queue_drain();
    }
    if ((flags & OPEN_CFW_BLE_MSGRX_EXIT_FLAG) != 0U) {
        open_cfw_ble_msgrx_exit();
    }
}

__attribute__((used, noinline))
unsigned int open_cfw_ble_msgrx_queue_clear(void)
{
    volatile open_cfw_ble_msgrx_dispatch_state *state =
        OPEN_CFW_BLE_MSGRX_DISPATCH_STATE;
    open_cfw_ble_msgrx_record *record = (open_cfw_ble_msgrx_record *)0;
    unsigned int freed = 0U;

    if (state->queue == 0U) {
        return 0U;
    }

    (void)OPEN_CFW_BLE_MSGRX_QUEUE_COUNT(
        (void *)(open_cfw_ble_msgrx_dispatch_uintptr)state->queue
    );
    while (OPEN_CFW_BLE_MSGRX_QUEUE_GET(
        (void *)(open_cfw_ble_msgrx_dispatch_uintptr)state->queue,
        &record,
        (unsigned char *)0,
        0U
    ) == 0U && record != (open_cfw_ble_msgrx_record *)0) {
        OPEN_CFW_BLE_MSGRX_FREE(record);
        record = (open_cfw_ble_msgrx_record *)0;
        ++freed;
    }
    (void)OPEN_CFW_BLE_MSGRX_QUEUE_COUNT(
        (void *)(open_cfw_ble_msgrx_dispatch_uintptr)state->queue
    );
    return freed;
}
