#include <stdlib.h>
#include <string.h>

#include "app_ble_host.h"

unsigned char open_cfw_test_app_ble_control[128];
unsigned char open_cfw_test_app_ble_runtime_state[16];
unsigned char open_cfw_test_app_ble_address[6];
unsigned int open_cfw_test_app_ble_smp_config;
unsigned int open_cfw_test_app_ble_app_config;
const void *open_cfw_test_app_ble_input_payload;
unsigned int open_cfw_test_app_ble_connection_role;
unsigned int open_cfw_test_app_ble_ring_connection;
unsigned char open_cfw_test_app_ble_processor_features;
unsigned int open_cfw_test_app_ble_processor_tick;
unsigned int open_cfw_test_app_ble_query_004bb9bc;
unsigned int open_cfw_test_app_ble_query_0052c914;
unsigned int open_cfw_test_app_ble_tick_count;

unsigned int open_cfw_test_app_ble_event_address[256];
uintptr_t open_cfw_test_app_ble_event_argument0[256];
uintptr_t open_cfw_test_app_ble_event_argument1[256];
uintptr_t open_cfw_test_app_ble_event_argument2[256];
unsigned int open_cfw_test_app_ble_event_count;
unsigned int open_cfw_test_app_ble_dm_size;
unsigned int open_cfw_test_app_ble_last_allocation;
unsigned int open_cfw_test_app_ble_last_handler;
unsigned int open_cfw_test_app_ble_last_message_size;
unsigned char open_cfw_test_app_ble_last_message[256];
unsigned int open_cfw_test_app_ble_allocate_fail;
unsigned int open_cfw_test_app_ble_ccc_lookup_enabled;
unsigned int open_cfw_test_app_ble_connection_enabled;
unsigned int open_cfw_test_app_ble_ccc_index;
unsigned int open_cfw_test_app_ble_ccc_value;
unsigned int open_cfw_test_app_ble_buffer_result;
unsigned int open_cfw_test_app_ble_next_handler;

static void record(
    unsigned int address,
    uintptr_t argument0,
    uintptr_t argument1,
    uintptr_t argument2
)
{
    unsigned int index = open_cfw_test_app_ble_event_count++;
    if (index < 256U) {
        open_cfw_test_app_ble_event_address[index] = address;
        open_cfw_test_app_ble_event_argument0[index] = argument0;
        open_cfw_test_app_ble_event_argument1[index] = argument1;
        open_cfw_test_app_ble_event_argument2[index] = argument2;
    }
}

void open_cfw_test_app_ble_reset(void)
{
    memset(open_cfw_test_app_ble_control, 0, sizeof(open_cfw_test_app_ble_control));
    memset(open_cfw_test_app_ble_runtime_state, 0,
        sizeof(open_cfw_test_app_ble_runtime_state));
    memset(open_cfw_test_app_ble_address, 0, sizeof(open_cfw_test_app_ble_address));
    memset(open_cfw_test_app_ble_event_address, 0,
        sizeof(open_cfw_test_app_ble_event_address));
    memset(open_cfw_test_app_ble_event_argument0, 0,
        sizeof(open_cfw_test_app_ble_event_argument0));
    memset(open_cfw_test_app_ble_event_argument1, 0,
        sizeof(open_cfw_test_app_ble_event_argument1));
    memset(open_cfw_test_app_ble_event_argument2, 0,
        sizeof(open_cfw_test_app_ble_event_argument2));
    memset(open_cfw_test_app_ble_last_message, 0,
        sizeof(open_cfw_test_app_ble_last_message));
    open_cfw_test_app_ble_smp_config = 0U;
    open_cfw_test_app_ble_app_config = 0U;
    open_cfw_test_app_ble_input_payload = NULL;
    open_cfw_test_app_ble_event_count = 0U;
    open_cfw_test_app_ble_dm_size = 12U;
    open_cfw_test_app_ble_last_allocation = 0U;
    open_cfw_test_app_ble_last_handler = 0U;
    open_cfw_test_app_ble_last_message_size = 0U;
    open_cfw_test_app_ble_allocate_fail = 0U;
    open_cfw_test_app_ble_ccc_lookup_enabled = 1U;
    open_cfw_test_app_ble_connection_enabled = 1U;
    open_cfw_test_app_ble_ccc_index = 0U;
    open_cfw_test_app_ble_ccc_value = 0U;
    open_cfw_test_app_ble_buffer_result = 0x2940U;
    open_cfw_test_app_ble_next_handler = 0x40U;
    open_cfw_test_app_ble_connection_role = 0U;
    open_cfw_test_app_ble_ring_connection = 0U;
    open_cfw_test_app_ble_processor_features = 0U;
    open_cfw_test_app_ble_processor_tick = 0U;
    open_cfw_test_app_ble_query_004bb9bc = 0U;
    open_cfw_test_app_ble_query_0052c914 = 0U;
    open_cfw_test_app_ble_tick_count = 0x12345678U;
}

void open_cfw_test_app_ble_call0(unsigned int address)
{
    record(address, 0U, 0U, 0U);
}

void open_cfw_test_app_ble_call1(unsigned int address, uintptr_t argument0)
{
    record(address, argument0, 0U, 0U);
}

void open_cfw_test_app_ble_call2(
    unsigned int address,
    uintptr_t argument0,
    uintptr_t argument1
)
{
    record(address, argument0, argument1, 0U);
}

void open_cfw_test_app_ble_call3(
    unsigned int address,
    uintptr_t argument0,
    uintptr_t argument1,
    uintptr_t argument2
)
{
    record(address, argument0, argument1, argument2);
}

unsigned int open_cfw_test_app_ble_handler_allocate(void *callback)
{
    unsigned int result = open_cfw_test_app_ble_next_handler++;
    record(0x0052B980U, (uintptr_t)callback, result, 0U);
    return result;
}

unsigned int open_cfw_test_app_ble_buffer_initialize(
    unsigned int size,
    void *memory,
    unsigned int count,
    const void *descriptors
)
{
    record(0x00530364U, size, (uintptr_t)memory,
        ((uintptr_t)count << 32) | (uintptr_t)descriptors);
    return open_cfw_test_app_ble_buffer_result;
}

void open_cfw_test_app_ble_buffer_diagnostic(unsigned int result)
{
    record(0xD0000000U, result, 0U, 0U);
}

unsigned int open_cfw_test_app_ble_dm_event_size(const void *event)
{
    (void)event;
    return open_cfw_test_app_ble_dm_size;
}

void *open_cfw_test_app_ble_allocate(unsigned int size)
{
    open_cfw_test_app_ble_last_allocation = size;
    if (open_cfw_test_app_ble_allocate_fail != 0U) {
        return NULL;
    }
    return calloc(1U, size);
}

void *open_cfw_test_app_ble_copy(void *destination, const void *source, unsigned int size)
{
    return memcpy(destination, source, size);
}

void open_cfw_test_app_ble_message_send(unsigned int handler, void *message)
{
    unsigned int size = open_cfw_test_app_ble_last_allocation;
    if (size > sizeof(open_cfw_test_app_ble_last_message)) {
        size = sizeof(open_cfw_test_app_ble_last_message);
    }
    open_cfw_test_app_ble_last_handler = handler;
    open_cfw_test_app_ble_last_message_size = size;
    memcpy(open_cfw_test_app_ble_last_message, message, size);
    free(message);
}

void *open_cfw_test_app_ble_ccc_lookup(unsigned int connection)
{
    record(0x004BB07CU, connection, 0U, 0U);
    return open_cfw_test_app_ble_ccc_lookup_enabled != 0U
        ? (void *)0xCAFE
        : NULL;
}

unsigned int open_cfw_test_app_ble_connection_active(unsigned int connection)
{
    record(0x004BAD26U, connection, 0U, 0U);
    return open_cfw_test_app_ble_connection_enabled;
}

void open_cfw_test_app_ble_ccc_update(void *state, unsigned int index, unsigned int value)
{
    record(0x0047B3E2U, (uintptr_t)state, index, value);
    open_cfw_test_app_ble_ccc_index = index;
    open_cfw_test_app_ble_ccc_value = value;
}

void open_cfw_test_app_ble_timer_release(void *callback)
{
    record(0x00476ACEU, (uintptr_t)callback, 0U, 0U);
}

void open_cfw_test_app_ble_timer_start(
    void *callback,
    unsigned int argument,
    unsigned int milliseconds
)
{
    record(0x0047697EU, (uintptr_t)callback, argument, milliseconds);
}

const void *open_cfw_test_app_ble_load_pointer(const void *base, unsigned int offset)
{
    (void)base;
    (void)offset;
    return open_cfw_test_app_ble_input_payload;
}

void open_cfw_test_app_ble_store_pointer(void *base, unsigned int offset, const void *value)
{
    memcpy((unsigned char *)base + offset, &value, sizeof(value));
}

unsigned int open_cfw_test_app_ble_get_connection_role(unsigned int connection)
{
    record(0x004B73C4U, connection, 0U, 0U);
    return open_cfw_test_app_ble_connection_role;
}

unsigned int open_cfw_test_app_ble_get_ring_connection(void)
{
    record(0x0046EF60U, 0U, 0U, 0U);
    return open_cfw_test_app_ble_ring_connection;
}

unsigned int open_cfw_test_app_ble_get_query_004bb9bc(void)
{
    record(0x004BB9BCU, 0U, 0U, 0U);
    return open_cfw_test_app_ble_query_004bb9bc;
}

unsigned int open_cfw_test_app_ble_get_query_0052c914(void)
{
    record(0x0052C914U, 0U, 0U, 0U);
    return open_cfw_test_app_ble_query_0052c914;
}

unsigned int open_cfw_test_app_ble_get_tick_count(void)
{
    record(0x004490CCU, 0U, 0U, 0U);
    return open_cfw_test_app_ble_tick_count;
}

void open_cfw_test_app_ble_handler_diagnostic(void *message, unsigned int role)
{
    record(0xD1000000U, (uintptr_t)message, role, 0U);
}
