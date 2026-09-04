#ifndef OPEN_CFW_APP_BLE_DISCOVERY_HOST_H
#define OPEN_CFW_APP_BLE_DISCOVERY_HOST_H

#include <stdint.h>

extern uint8_t open_cfw_test_discovery_context[128];
extern uint8_t open_cfw_test_discovery_record[8];
extern uint8_t open_cfw_test_discovery_message[12];
extern uint16_t open_cfw_test_discovery_ancs_handles[5];
extern uint16_t open_cfw_test_discovery_reported_handles[5];
extern uint8_t open_cfw_test_discovery_role_value;
extern uint8_t open_cfw_test_discovery_task_id;
extern uint8_t open_cfw_test_discovery_record_present;
extern uint8_t open_cfw_test_discovery_allocate_success;
extern int open_cfw_test_discovery_ancs_result;
extern unsigned int open_cfw_test_discovery_event_count;
extern unsigned int open_cfw_test_discovery_events[32];
extern uintptr_t open_cfw_test_discovery_arguments[32][6];

void open_cfw_test_discovery_reset(void);
void open_cfw_test_discovery_remove_delayed(void *callback);
void *open_cfw_test_discovery_connection_record(uint8_t connection_id);
void open_cfw_test_discovery_record_state_set(void *record, uint8_t state);
void open_cfw_test_discovery_record_reset(void *record, uint8_t state);
void *open_cfw_test_discovery_message_allocate(uint16_t size);
void open_cfw_test_discovery_message_send(uint8_t task_id, void *message);
uint8_t open_cfw_test_discovery_role(uint8_t connection_id);
void open_cfw_test_discovery_begin(
    uint8_t connection_id, uint8_t count, volatile uint8_t *handles
);
void open_cfw_test_discovery_fail(uint8_t connection_id);
void open_cfw_test_discovery_phone_ready(uint8_t connection_id);
void open_cfw_test_discovery_configure(
    uint8_t connection_id, const void *configuration
);
void open_cfw_test_discovery_state_set(
    uint8_t connection_id, uint8_t state
);
void open_cfw_test_discovery_service_begin(
    uint8_t connection_id, uint8_t state, uint8_t service,
    const void *uuid, uint8_t handle_count, volatile uint8_t *handles
);
void open_cfw_test_discovery_database_hash(
    uint8_t connection_id, const void *configuration
);
int open_cfw_test_discovery_ancs(
    uint8_t connection_id, const void *configuration
);
void open_cfw_test_discovery_product_signal(uint32_t signal);
void open_cfw_test_discovery_report_handles(
    const void *handles, uint8_t count
);

#define OPEN_CFW_APP_BLE_DISCOVERY_CONTEXT() \
    open_cfw_test_discovery_context
#define OPEN_CFW_APP_BLE_DISCOVERY_RING_CONFIG() \
    ((const void *)(uintptr_t)0x1818U)
#define OPEN_CFW_APP_BLE_DISCOVERY_ANCS_CONFIG() \
    ((const void *)open_cfw_test_discovery_ancs_handles)
#define OPEN_CFW_APP_BLE_DISCOVERY_GATT_CONFIG() \
    ((const void *)(uintptr_t)0x2020U)
#define OPEN_CFW_APP_BLE_DISCOVERY_DATABASE_HASH_CONFIG() \
    ((const void *)(uintptr_t)0x2424U)
#define OPEN_CFW_APP_BLE_DISCOVERY_TASK_ID() \
    open_cfw_test_discovery_task_id
#define OPEN_CFW_APP_BLE_DISCOVERY_REMOVE_DELAYED(callback) \
    open_cfw_test_discovery_remove_delayed((callback))
#define OPEN_CFW_APP_BLE_DISCOVERY_CONNECTION_RECORD(connection_id) \
    open_cfw_test_discovery_connection_record((connection_id))
#define OPEN_CFW_APP_BLE_DISCOVERY_RECORD_STATE_SET(record, state) \
    open_cfw_test_discovery_record_state_set((record), (state))
#define OPEN_CFW_APP_BLE_DISCOVERY_RECORD_RESET(record, state) \
    open_cfw_test_discovery_record_reset((record), (state))
#define OPEN_CFW_APP_BLE_DISCOVERY_MESSAGE_ALLOCATE(size) \
    open_cfw_test_discovery_message_allocate((size))
#define OPEN_CFW_APP_BLE_DISCOVERY_MESSAGE_SEND(task_id, message) \
    open_cfw_test_discovery_message_send((task_id), (message))
#define OPEN_CFW_APP_BLE_DISCOVERY_ROLE(connection_id) \
    open_cfw_test_discovery_role((connection_id))
#define OPEN_CFW_APP_BLE_DISCOVERY_BEGIN(connection_id, count, handles) \
    open_cfw_test_discovery_begin((connection_id), (count), (handles))
#define OPEN_CFW_APP_BLE_DISCOVERY_FAIL(connection_id) \
    open_cfw_test_discovery_fail((connection_id))
#define OPEN_CFW_APP_BLE_DISCOVERY_PHONE_READY(connection_id) \
    open_cfw_test_discovery_phone_ready((connection_id))
#define OPEN_CFW_APP_BLE_DISCOVERY_CONFIGURE(connection_id, configuration) \
    open_cfw_test_discovery_configure((connection_id), (configuration))
#define OPEN_CFW_APP_BLE_DISCOVERY_STATE_SET(connection_id, state) \
    open_cfw_test_discovery_state_set((connection_id), (state))
#define OPEN_CFW_APP_BLE_DISCOVERY_SERVICE_BEGIN( \
    connection_id, state, service, uuid, handle_count, handles \
) \
    open_cfw_test_discovery_service_begin( \
        (connection_id), (state), (service), (uuid), (handle_count), (handles) \
    )
#define OPEN_CFW_APP_BLE_DISCOVERY_DATABASE_HASH( \
    connection_id, configuration \
) \
    open_cfw_test_discovery_database_hash((connection_id), (configuration))
#define OPEN_CFW_APP_BLE_DISCOVERY_ANCS(connection_id, configuration) \
    open_cfw_test_discovery_ancs((connection_id), (configuration))
#define OPEN_CFW_APP_BLE_DISCOVERY_PRODUCT_SIGNAL(signal) \
    open_cfw_test_discovery_product_signal((signal))
#define OPEN_CFW_APP_BLE_DISCOVERY_REPORT_HANDLES(handles, count) \
    open_cfw_test_discovery_report_handles((handles), (count))

#endif
