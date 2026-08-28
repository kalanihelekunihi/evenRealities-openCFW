/*
 * SPDX-License-Identifier: MIT
 *
 * Native state and backend fixture for BLE message-transmit setup and thread
 * lifecycle.
 */

struct open_cfw_test_ble_msgtx_lifecycle_state_type {
    unsigned int reserved_0;
    unsigned int reserved_4;
    unsigned int thread;
    unsigned int queue;
};

struct open_cfw_test_ble_msgtx_lifecycle_state_type
    open_cfw_test_ble_msgtx_lifecycle_state;
unsigned int open_cfw_test_ble_msgtx_stage_enter_calls;
unsigned int open_cfw_test_ble_msgtx_stage_enter_index;
unsigned int open_cfw_test_ble_msgtx_stage_leave_calls;
unsigned int open_cfw_test_ble_msgtx_stage_leave_index;
unsigned int open_cfw_test_ble_msgtx_thread_new_result;
unsigned int open_cfw_test_ble_msgtx_thread_new_calls;
unsigned int open_cfw_test_ble_msgtx_thread_new_entry;
unsigned int open_cfw_test_ble_msgtx_thread_new_argument;
unsigned int open_cfw_test_ble_msgtx_thread_new_attributes;
unsigned int open_cfw_test_ble_msgtx_thread_terminate_calls;
unsigned int open_cfw_test_ble_msgtx_thread_terminate_argument;
unsigned int open_cfw_test_ble_msgtx_thread_failure_calls;

void open_cfw_test_ble_msgtx_lifecycle_reset(void)
{
    open_cfw_test_ble_msgtx_lifecycle_state.reserved_0 = 0x11111111U;
    open_cfw_test_ble_msgtx_lifecycle_state.reserved_4 = 0x22222222U;
    open_cfw_test_ble_msgtx_lifecycle_state.thread = 0x33333333U;
    open_cfw_test_ble_msgtx_lifecycle_state.queue = 0x44444444U;
    open_cfw_test_ble_msgtx_stage_enter_calls = 0U;
    open_cfw_test_ble_msgtx_stage_enter_index = 0U;
    open_cfw_test_ble_msgtx_stage_leave_calls = 0U;
    open_cfw_test_ble_msgtx_stage_leave_index = 0U;
    open_cfw_test_ble_msgtx_thread_new_result = 0U;
    open_cfw_test_ble_msgtx_thread_new_calls = 0U;
    open_cfw_test_ble_msgtx_thread_new_entry = 0U;
    open_cfw_test_ble_msgtx_thread_new_argument = 0U;
    open_cfw_test_ble_msgtx_thread_new_attributes = 0U;
    open_cfw_test_ble_msgtx_thread_terminate_calls = 0U;
    open_cfw_test_ble_msgtx_thread_terminate_argument = 0U;
    open_cfw_test_ble_msgtx_thread_failure_calls = 0U;
}

void open_cfw_test_ble_msgtx_stage_enter(unsigned int index)
{
    ++open_cfw_test_ble_msgtx_stage_enter_calls;
    open_cfw_test_ble_msgtx_stage_enter_index = index;
}

void open_cfw_test_ble_msgtx_stage_leave(unsigned int index)
{
    ++open_cfw_test_ble_msgtx_stage_leave_calls;
    open_cfw_test_ble_msgtx_stage_leave_index = index;
}

void *open_cfw_test_ble_msgtx_thread_new(
    void *entry,
    void *argument,
    const void *attributes
)
{
    ++open_cfw_test_ble_msgtx_thread_new_calls;
    open_cfw_test_ble_msgtx_thread_new_entry =
        (unsigned int)(__UINTPTR_TYPE__)entry;
    open_cfw_test_ble_msgtx_thread_new_argument =
        (unsigned int)(__UINTPTR_TYPE__)argument;
    open_cfw_test_ble_msgtx_thread_new_attributes =
        (unsigned int)(__UINTPTR_TYPE__)attributes;
    return (void *)(__UINTPTR_TYPE__)
        open_cfw_test_ble_msgtx_thread_new_result;
}

void open_cfw_test_ble_msgtx_thread_terminate(void *thread)
{
    ++open_cfw_test_ble_msgtx_thread_terminate_calls;
    open_cfw_test_ble_msgtx_thread_terminate_argument =
        (unsigned int)(__UINTPTR_TYPE__)thread;
}

void open_cfw_test_ble_msgtx_thread_failure(void)
{
    ++open_cfw_test_ble_msgtx_thread_failure_calls;
}

#define OPEN_CFW_BLE_MSGTX_LIFECYCLE_STATE \
    ((volatile open_cfw_ble_msgtx_lifecycle_state *) \
        &open_cfw_test_ble_msgtx_lifecycle_state)
#define OPEN_CFW_BLE_MSGTX_STAGE_ENTER_BACKEND(index) \
    open_cfw_test_ble_msgtx_stage_enter((index))
#define OPEN_CFW_BLE_MSGTX_STAGE_LEAVE_BACKEND(index) \
    open_cfw_test_ble_msgtx_stage_leave((index))
#define OPEN_CFW_BLE_MSGTX_THREAD_NEW(entry, argument, attributes) \
    open_cfw_test_ble_msgtx_thread_new((entry), (argument), (attributes))
#define OPEN_CFW_BLE_MSGTX_THREAD_TERMINATE(thread) \
    open_cfw_test_ble_msgtx_thread_terminate((thread))
#define OPEN_CFW_BLE_MSGTX_THREAD_FAILURE() \
    open_cfw_test_ble_msgtx_thread_failure()

#include "../../components/apollo_main/core_overlay/ble_msgtx_thread_lifecycle.c"
