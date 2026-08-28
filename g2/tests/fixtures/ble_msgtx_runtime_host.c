/*
 * SPDX-License-Identifier: MIT
 *
 * Native state, queue-backend, and failure fixture for the BLE
 * message-transmit lifecycle hooks.
 */

struct open_cfw_test_ble_msgtx_runtime_state_type {
    unsigned int reserved_0;
    unsigned int reserved_4;
    unsigned int thread;
    unsigned int queue;
};

struct open_cfw_test_ble_msgtx_runtime_state_type
    open_cfw_test_ble_msgtx_runtime_state;
unsigned int open_cfw_test_ble_msgtx_queue_result;
unsigned int open_cfw_test_ble_msgtx_queue_calls;
unsigned int open_cfw_test_ble_msgtx_queue_capacity;
unsigned int open_cfw_test_ble_msgtx_queue_item_size;
unsigned int open_cfw_test_ble_msgtx_queue_attributes;
unsigned int open_cfw_test_ble_msgtx_failure_calls;

void open_cfw_test_ble_msgtx_runtime_reset(void)
{
    open_cfw_test_ble_msgtx_runtime_state.reserved_0 = 0x11111111U;
    open_cfw_test_ble_msgtx_runtime_state.reserved_4 = 0x22222222U;
    open_cfw_test_ble_msgtx_runtime_state.thread = 0x33333333U;
    open_cfw_test_ble_msgtx_runtime_state.queue = 0x44444444U;
    open_cfw_test_ble_msgtx_queue_result = 0U;
    open_cfw_test_ble_msgtx_queue_calls = 0U;
    open_cfw_test_ble_msgtx_queue_capacity = 0U;
    open_cfw_test_ble_msgtx_queue_item_size = 0U;
    open_cfw_test_ble_msgtx_queue_attributes = 0U;
    open_cfw_test_ble_msgtx_failure_calls = 0U;
}

void *open_cfw_test_ble_msgtx_queue_new(
    unsigned int count,
    unsigned int size,
    const void *attributes
)
{
    ++open_cfw_test_ble_msgtx_queue_calls;
    open_cfw_test_ble_msgtx_queue_capacity = count;
    open_cfw_test_ble_msgtx_queue_item_size = size;
    open_cfw_test_ble_msgtx_queue_attributes =
        (unsigned int)(__UINTPTR_TYPE__)attributes;
    return (void *)(__UINTPTR_TYPE__)open_cfw_test_ble_msgtx_queue_result;
}

void open_cfw_test_ble_msgtx_queue_failure(void)
{
    ++open_cfw_test_ble_msgtx_failure_calls;
}

#define OPEN_CFW_BLE_MSGTX_RUNTIME_STATE_ADDRESS \
    ((__UINTPTR_TYPE__)&open_cfw_test_ble_msgtx_runtime_state)
#define OPEN_CFW_BLE_MSGTX_QUEUE_NEW(count, size, attributes) \
    open_cfw_test_ble_msgtx_queue_new((count), (size), (attributes))
#define OPEN_CFW_BLE_MSGTX_QUEUE_FAILURE() \
    open_cfw_test_ble_msgtx_queue_failure()

#include "../../components/apollo_main/core_overlay/ble_msgtx_runtime.c"
