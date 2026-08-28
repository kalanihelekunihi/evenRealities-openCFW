/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room BLE message-receive queue and no-op hooks reconstructed from
 * stock 0x0048EE28...0x0048EE53.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_msgrx_runtime_uintptr;

#define OPEN_CFW_BLE_MSGRX_STATE_ADDRESS 0x20003FFCU
#define OPEN_CFW_BLE_MSGRX_QUEUE_ITEM_COUNT 150U
#define OPEN_CFW_BLE_MSGRX_QUEUE_ITEM_SIZE 4U

typedef struct {
    unsigned int reserved_0;
    unsigned int reserved_4;
    unsigned int thread;
    unsigned int queue;
} open_cfw_ble_msgrx_runtime_state;

#ifndef OPEN_CFW_BLE_MSGRX_RUNTIME_STATE
#define OPEN_CFW_BLE_MSGRX_RUNTIME_STATE \
    ((volatile open_cfw_ble_msgrx_runtime_state *) \
        (open_cfw_ble_msgrx_runtime_uintptr)OPEN_CFW_BLE_MSGRX_STATE_ADDRESS)
#endif

#ifndef OPEN_CFW_BLE_MSGRX_QUEUE_NEW
typedef void *(*open_cfw_ble_msgrx_queue_new_function)(
    unsigned int,
    unsigned int,
    const void *
);
#define OPEN_CFW_BLE_MSGRX_QUEUE_NEW(count, size, attributes) \
    (((open_cfw_ble_msgrx_queue_new_function)0x00449A33U)( \
        (count), (size), (attributes)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_QUEUE_FAILURE
typedef void (*open_cfw_ble_msgrx_failure_function)(void);
#define OPEN_CFW_BLE_MSGRX_QUEUE_FAILURE() \
    do { \
        ((open_cfw_ble_msgrx_failure_function)0x005FA0A5U)(); \
        *(volatile unsigned int *) \
            (open_cfw_ble_msgrx_runtime_uintptr)0xFFFFFFFFU = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

__attribute__((used, noinline))
void open_cfw_ble_msgrx_application_initialize(void)
{
}

__attribute__((used, noinline))
void open_cfw_ble_msgrx_queue_initialize(void)
{
    volatile open_cfw_ble_msgrx_runtime_state *state =
        OPEN_CFW_BLE_MSGRX_RUNTIME_STATE;

    state->queue = (unsigned int)(open_cfw_ble_msgrx_runtime_uintptr)
        OPEN_CFW_BLE_MSGRX_QUEUE_NEW(
            OPEN_CFW_BLE_MSGRX_QUEUE_ITEM_COUNT,
            OPEN_CFW_BLE_MSGRX_QUEUE_ITEM_SIZE,
            (const void *)0
        );
    if (state->queue == 0U) {
        OPEN_CFW_BLE_MSGRX_QUEUE_FAILURE();
    }
}

__attribute__((used, noinline))
void open_cfw_ble_msgrx_thread_initialize(void)
{
}
