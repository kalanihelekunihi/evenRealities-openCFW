#include "app_ble_discovery_host.h"

#include <stddef.h>

enum {
    TEST_DISCOVERY_REMOVE = 1,
    TEST_DISCOVERY_RECORD_LOOKUP,
    TEST_DISCOVERY_RECORD_STATE,
    TEST_DISCOVERY_RECORD_RESET,
    TEST_DISCOVERY_ALLOCATE,
    TEST_DISCOVERY_SEND,
    TEST_DISCOVERY_ROLE,
    TEST_DISCOVERY_BEGIN,
    TEST_DISCOVERY_FAIL,
    TEST_DISCOVERY_PHONE_READY,
    TEST_DISCOVERY_CONFIGURE,
    TEST_DISCOVERY_STATE_SET,
    TEST_DISCOVERY_SERVICE_BEGIN,
    TEST_DISCOVERY_DATABASE_HASH,
    TEST_DISCOVERY_ANCS,
    TEST_DISCOVERY_SIGNAL,
    TEST_DISCOVERY_REPORT_HANDLES,
};

uint8_t open_cfw_test_discovery_context[128];
uint8_t open_cfw_test_discovery_record[8];
uint8_t open_cfw_test_discovery_message[12];
uint16_t open_cfw_test_discovery_ancs_handles[5];
uint16_t open_cfw_test_discovery_reported_handles[5];
uint8_t open_cfw_test_discovery_role_value;
uint8_t open_cfw_test_discovery_task_id;
uint8_t open_cfw_test_discovery_record_present;
uint8_t open_cfw_test_discovery_allocate_success;
int open_cfw_test_discovery_ancs_result;
unsigned int open_cfw_test_discovery_event_count;
unsigned int open_cfw_test_discovery_events[32];
uintptr_t open_cfw_test_discovery_arguments[32][6];

static void record_event(
    unsigned int event, uintptr_t a0, uintptr_t a1, uintptr_t a2,
    uintptr_t a3, uintptr_t a4, uintptr_t a5
)
{
    unsigned int index = open_cfw_test_discovery_event_count++;
    open_cfw_test_discovery_events[index] = event;
    open_cfw_test_discovery_arguments[index][0] = a0;
    open_cfw_test_discovery_arguments[index][1] = a1;
    open_cfw_test_discovery_arguments[index][2] = a2;
    open_cfw_test_discovery_arguments[index][3] = a3;
    open_cfw_test_discovery_arguments[index][4] = a4;
    open_cfw_test_discovery_arguments[index][5] = a5;
}

void open_cfw_test_discovery_reset(void)
{
    unsigned int row;
    unsigned int column;

    for (row = 0U; row < 128U; ++row) {
        open_cfw_test_discovery_context[row] = 0U;
    }
    for (row = 0U; row < 12U; ++row) {
        open_cfw_test_discovery_message[row] = 0U;
    }
    for (row = 0U; row < 5U; ++row) {
        open_cfw_test_discovery_ancs_handles[row] = (uint16_t)(row + 1U);
        open_cfw_test_discovery_reported_handles[row] = 0U;
    }
    for (row = 0U; row < 32U; ++row) {
        open_cfw_test_discovery_events[row] = 0U;
        for (column = 0U; column < 6U; ++column) {
            open_cfw_test_discovery_arguments[row][column] = 0U;
        }
    }
    open_cfw_test_discovery_role_value = 0U;
    open_cfw_test_discovery_task_id = 9U;
    open_cfw_test_discovery_record_present = 1U;
    open_cfw_test_discovery_allocate_success = 1U;
    open_cfw_test_discovery_ancs_result = 1;
    open_cfw_test_discovery_event_count = 0U;
}

void open_cfw_test_discovery_remove_delayed(void *callback)
{
    record_event(TEST_DISCOVERY_REMOVE, (uintptr_t)callback, 0, 0, 0, 0, 0);
}

void *open_cfw_test_discovery_connection_record(uint8_t connection_id)
{
    record_event(TEST_DISCOVERY_RECORD_LOOKUP, connection_id, 0, 0, 0, 0, 0);
    return open_cfw_test_discovery_record_present != 0U
        ? open_cfw_test_discovery_record : NULL;
}

void open_cfw_test_discovery_record_state_set(void *record, uint8_t state)
{
    record_event(TEST_DISCOVERY_RECORD_STATE, (uintptr_t)record, state, 0, 0, 0, 0);
}

void open_cfw_test_discovery_record_reset(void *record, uint8_t state)
{
    record_event(TEST_DISCOVERY_RECORD_RESET, (uintptr_t)record, state, 0, 0, 0, 0);
}

void *open_cfw_test_discovery_message_allocate(uint16_t size)
{
    record_event(TEST_DISCOVERY_ALLOCATE, size, 0, 0, 0, 0, 0);
    return open_cfw_test_discovery_allocate_success != 0U
        ? open_cfw_test_discovery_message : NULL;
}

void open_cfw_test_discovery_message_send(uint8_t task_id, void *message)
{
    record_event(TEST_DISCOVERY_SEND, task_id, (uintptr_t)message, 0, 0, 0, 0);
}

uint8_t open_cfw_test_discovery_role(uint8_t connection_id)
{
    record_event(TEST_DISCOVERY_ROLE, connection_id, 0, 0, 0, 0, 0);
    return open_cfw_test_discovery_role_value;
}

void open_cfw_test_discovery_begin(
    uint8_t connection_id, uint8_t count, volatile uint8_t *handles
)
{
    record_event(TEST_DISCOVERY_BEGIN, connection_id, count,
                 (uintptr_t)handles, 0, 0, 0);
}

void open_cfw_test_discovery_fail(uint8_t connection_id)
{
    record_event(TEST_DISCOVERY_FAIL, connection_id, 0, 0, 0, 0, 0);
}

void open_cfw_test_discovery_phone_ready(uint8_t connection_id)
{
    record_event(TEST_DISCOVERY_PHONE_READY, connection_id, 0, 0, 0, 0, 0);
}

void open_cfw_test_discovery_configure(
    uint8_t connection_id, const void *configuration
)
{
    record_event(TEST_DISCOVERY_CONFIGURE, connection_id,
                 (uintptr_t)configuration, 0, 0, 0, 0);
}

void open_cfw_test_discovery_state_set(uint8_t connection_id, uint8_t state)
{
    record_event(TEST_DISCOVERY_STATE_SET, connection_id, state, 0, 0, 0, 0);
}

void open_cfw_test_discovery_service_begin(
    uint8_t connection_id, uint8_t state, uint8_t service,
    const void *uuid, uint8_t handle_count, volatile uint8_t *handles
)
{
    record_event(TEST_DISCOVERY_SERVICE_BEGIN, connection_id, state, service,
                 (uintptr_t)uuid, handle_count, (uintptr_t)handles);
}

void open_cfw_test_discovery_database_hash(
    uint8_t connection_id, const void *configuration
)
{
    record_event(TEST_DISCOVERY_DATABASE_HASH, connection_id,
                 (uintptr_t)configuration, 0, 0, 0, 0);
}

int open_cfw_test_discovery_ancs(
    uint8_t connection_id, const void *configuration
)
{
    record_event(TEST_DISCOVERY_ANCS, connection_id,
                 (uintptr_t)configuration, 0, 0, 0, 0);
    return open_cfw_test_discovery_ancs_result;
}

void open_cfw_test_discovery_product_signal(uint32_t signal)
{
    record_event(TEST_DISCOVERY_SIGNAL, signal, 0, 0, 0, 0, 0);
}

void open_cfw_test_discovery_report_handles(const void *handles, uint8_t count)
{
    const uint16_t *values = (const uint16_t *)handles;
    unsigned int index;

    for (index = 0U; index < count && index < 5U; ++index) {
        open_cfw_test_discovery_reported_handles[index] = values[index];
    }
    record_event(TEST_DISCOVERY_REPORT_HANDLES, (uintptr_t)handles,
                 count, 0, 0, 0, 0);
}
