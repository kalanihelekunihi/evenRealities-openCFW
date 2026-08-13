#ifndef OPEN_CFW_TEST_APP_BLE_HOST_H
#define OPEN_CFW_TEST_APP_BLE_HOST_H

#include <stddef.h>
#include <stdint.h>

extern unsigned char open_cfw_test_app_ble_control[128];
extern unsigned char open_cfw_test_app_ble_runtime_state[16];
extern unsigned char open_cfw_test_app_ble_address[6];
extern unsigned int open_cfw_test_app_ble_smp_config;
extern unsigned int open_cfw_test_app_ble_app_config;
extern const void *open_cfw_test_app_ble_input_payload;
extern unsigned int open_cfw_test_app_ble_connection_role;
extern unsigned int open_cfw_test_app_ble_ring_connection;
extern unsigned char open_cfw_test_app_ble_processor_features;
extern unsigned int open_cfw_test_app_ble_processor_tick;
extern unsigned int open_cfw_test_app_ble_query_004bb9bc;
extern unsigned int open_cfw_test_app_ble_query_0052c914;
extern unsigned int open_cfw_test_app_ble_tick_count;

void open_cfw_test_app_ble_call0(unsigned int address);
void open_cfw_test_app_ble_call1(unsigned int address, uintptr_t argument0);
void open_cfw_test_app_ble_call2(
    unsigned int address,
    uintptr_t argument0,
    uintptr_t argument1
);
void open_cfw_test_app_ble_call3(
    unsigned int address,
    uintptr_t argument0,
    uintptr_t argument1,
    uintptr_t argument2
);
unsigned int open_cfw_test_app_ble_handler_allocate(void *callback);
unsigned int open_cfw_test_app_ble_buffer_initialize(
    unsigned int size,
    void *memory,
    unsigned int count,
    const void *descriptors
);
void open_cfw_test_app_ble_buffer_diagnostic(unsigned int result);
unsigned int open_cfw_test_app_ble_dm_event_size(const void *event);
void *open_cfw_test_app_ble_allocate(unsigned int size);
void *open_cfw_test_app_ble_copy(void *destination, const void *source, unsigned int size);
void open_cfw_test_app_ble_message_send(unsigned int handler, void *message);
void *open_cfw_test_app_ble_ccc_lookup(unsigned int connection);
unsigned int open_cfw_test_app_ble_connection_active(unsigned int connection);
void open_cfw_test_app_ble_ccc_update(void *state, unsigned int index, unsigned int value);
void open_cfw_test_app_ble_timer_release(void *callback);
void open_cfw_test_app_ble_timer_start(
    void *callback,
    unsigned int argument,
    unsigned int milliseconds
);
unsigned int open_cfw_test_app_ble_get_connection_role(unsigned int connection);
unsigned int open_cfw_test_app_ble_get_ring_connection(void);
unsigned int open_cfw_test_app_ble_get_query_004bb9bc(void);
unsigned int open_cfw_test_app_ble_get_query_0052c914(void);
unsigned int open_cfw_test_app_ble_get_tick_count(void);
void open_cfw_test_app_ble_handler_diagnostic(void *message, unsigned int role);
const void *open_cfw_test_app_ble_load_pointer(const void *base, unsigned int offset);
void open_cfw_test_app_ble_store_pointer(void *base, unsigned int offset, const void *value);

#define OPEN_CFW_APP_BLE_CONTROL (open_cfw_test_app_ble_control)
#define OPEN_CFW_APP_BLE_STARTUP_CONTROL (open_cfw_test_app_ble_control)
#define OPEN_CFW_APP_BLE_RUNTIME_STATE (open_cfw_test_app_ble_runtime_state)
#define OPEN_CFW_APP_BLE_SMP_CONFIG_DESTINATION (&open_cfw_test_app_ble_smp_config)
#define OPEN_CFW_APP_BLE_APP_CONFIG_DESTINATION (&open_cfw_test_app_ble_app_config)
#define OPEN_CFW_APP_BLE_ADDRESS_POINTER (open_cfw_test_app_ble_address)
#define OPEN_CFW_APP_BLE_CALL0(address) open_cfw_test_app_ble_call0((address))
#define OPEN_CFW_APP_BLE_CALL1(address, argument0) \
    open_cfw_test_app_ble_call1((address), (uintptr_t)(argument0))
#define OPEN_CFW_APP_BLE_CALL2(address, argument0, argument1) \
    open_cfw_test_app_ble_call2( \
        (address), (uintptr_t)(argument0), (uintptr_t)(argument1))
#define OPEN_CFW_APP_BLE_CALL3(address, argument0, argument1, argument2) \
    open_cfw_test_app_ble_call3( \
        (address), (uintptr_t)(argument0), (uintptr_t)(argument1), \
        (uintptr_t)(argument2))
#define OPEN_CFW_APP_BLE_HANDLER_ALLOCATE(callback) \
    open_cfw_test_app_ble_handler_allocate((void *)(callback))
#define OPEN_CFW_APP_BLE_BUFFER_INITIALIZE(size, memory, count, descriptors) \
    open_cfw_test_app_ble_buffer_initialize((size), (memory), (count), (descriptors))
#define OPEN_CFW_APP_BLE_BUFFER_DIAGNOSTIC(result) \
    open_cfw_test_app_ble_buffer_diagnostic((result))
#define OPEN_CFW_APP_BLE_DM_EVENT_SIZE(event) \
    open_cfw_test_app_ble_dm_event_size((event))
#define OPEN_CFW_APP_BLE_ALLOCATE(size) open_cfw_test_app_ble_allocate((size))
#define OPEN_CFW_APP_BLE_COPY(destination, source, size) \
    open_cfw_test_app_ble_copy((destination), (source), (size))
#define OPEN_CFW_APP_BLE_MESSAGE_SEND(handler, message) \
    open_cfw_test_app_ble_message_send((handler), (message))
#define OPEN_CFW_APP_BLE_CCC_LOOKUP(connection) \
    open_cfw_test_app_ble_ccc_lookup((connection))
#define OPEN_CFW_APP_BLE_CONNECTION_ACTIVE(connection) \
    open_cfw_test_app_ble_connection_active((connection))
#define OPEN_CFW_APP_BLE_CCC_UPDATE(state, index, value) \
    open_cfw_test_app_ble_ccc_update((state), (index), (value))
#define OPEN_CFW_APP_BLE_TIMER_RELEASE(callback) \
    open_cfw_test_app_ble_timer_release((void *)(callback))
#define OPEN_CFW_APP_BLE_TIMER_START(callback, argument, milliseconds) \
    open_cfw_test_app_ble_timer_start( \
        (void *)(callback), (argument), (milliseconds))
#define OPEN_CFW_APP_BLE_LOAD_POINTER(base, offset) \
    open_cfw_test_app_ble_load_pointer((base), (offset))
#define OPEN_CFW_APP_BLE_STORE_POINTER(base, offset, value) \
    open_cfw_test_app_ble_store_pointer((base), (offset), (value))
#define OPEN_CFW_APP_BLE_CONNECTION_ROLE(connection) \
    open_cfw_test_app_ble_get_connection_role((connection))
#define OPEN_CFW_APP_BLE_RING_CONNECTION_ACTIVE() \
    open_cfw_test_app_ble_get_ring_connection()
#define OPEN_CFW_APP_BLE_PROCESSOR_CONTROL (open_cfw_test_app_ble_control)
#define OPEN_CFW_APP_BLE_PROCESSOR_FEATURES \
    (&open_cfw_test_app_ble_processor_features)
#define OPEN_CFW_APP_BLE_PROCESSOR_TICK \
    (&open_cfw_test_app_ble_processor_tick)
#define OPEN_CFW_APP_BLE_QUERY_004BB9BC() \
    open_cfw_test_app_ble_get_query_004bb9bc()
#define OPEN_CFW_APP_BLE_QUERY_0052C914() \
    open_cfw_test_app_ble_get_query_0052c914()
#define OPEN_CFW_APP_BLE_TICK_COUNT() open_cfw_test_app_ble_get_tick_count()
#define OPEN_CFW_APP_BLE_HANDLER_DIAGNOSTIC(message, role) \
    open_cfw_test_app_ble_handler_diagnostic((message), (role))

#endif
