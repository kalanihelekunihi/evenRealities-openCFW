/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded BLE message-transmit lifecycle hooks matched to stock
 * 0x00475308...0x00475333.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_msgtx_runtime_uintptr;

#define OPEN_CFW_BLE_MSGTX_STATE_DEFAULT_ADDRESS 0x20004020U
#define OPEN_CFW_BLE_MSGTX_QUEUE_CAPACITY 150U
#define OPEN_CFW_BLE_MSGTX_QUEUE_ITEM_SIZE 4U

typedef struct {
    unsigned int reserved_0;
    unsigned int reserved_4;
    unsigned int thread;
    unsigned int queue;
} open_cfw_ble_msgtx_runtime_state;

#ifndef OPEN_CFW_BLE_MSGTX_RUNTIME_STATE_ADDRESS
#define OPEN_CFW_BLE_MSGTX_RUNTIME_STATE_ADDRESS \
    OPEN_CFW_BLE_MSGTX_STATE_DEFAULT_ADDRESS
#endif

#ifndef OPEN_CFW_BLE_MSGTX_QUEUE_NEW
typedef void *(*open_cfw_ble_msgtx_queue_new_function)(
    unsigned int,
    unsigned int,
    const void *
);
#define OPEN_CFW_BLE_MSGTX_QUEUE_NEW(count, size, attributes) \
    (((open_cfw_ble_msgtx_queue_new_function)0x00449A33U)( \
        (count), \
        (size), \
        (attributes) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_QUEUE_FAILURE
typedef void (*open_cfw_ble_msgtx_failure_function)(void);
#define OPEN_CFW_BLE_MSGTX_QUEUE_FAILURE() \
    do { \
        ((open_cfw_ble_msgtx_failure_function)0x005FA0A5U)(); \
        *(volatile unsigned int *) \
            (open_cfw_ble_msgtx_runtime_uintptr)0xFFFFFFFFU = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

__attribute__((used, noinline))
void open_cfw_ble_msgtx_application_initialize(void)
{
}

__attribute__((used, noinline))
void open_cfw_ble_msgtx_queue_initialize(void)
{
    volatile open_cfw_ble_msgtx_runtime_state *state =
        (volatile open_cfw_ble_msgtx_runtime_state *)
            (open_cfw_ble_msgtx_runtime_uintptr)
                OPEN_CFW_BLE_MSGTX_RUNTIME_STATE_ADDRESS;

    state->queue = (unsigned int)(open_cfw_ble_msgtx_runtime_uintptr)
        OPEN_CFW_BLE_MSGTX_QUEUE_NEW(
            OPEN_CFW_BLE_MSGTX_QUEUE_CAPACITY,
            OPEN_CFW_BLE_MSGTX_QUEUE_ITEM_SIZE,
            (const void *)0
        );
    if (state->queue == 0U) {
        OPEN_CFW_BLE_MSGTX_QUEUE_FAILURE();
        return;
    }
}

__attribute__((used, noinline))
void open_cfw_ble_msgtx_thread_initialize(void)
{
}
