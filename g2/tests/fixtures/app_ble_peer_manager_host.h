#ifndef OPEN_CFW_APP_BLE_PEER_MANAGER_HOST_H
#define OPEN_CFW_APP_BLE_PEER_MANAGER_HOST_H

#include <stdint.h>

extern uint8_t open_cfw_test_peer_pending[7];
extern uint8_t open_cfw_test_peer_records[144];
extern uint8_t open_cfw_test_peer_addresses[256][6];
extern uint8_t open_cfw_test_peer_address_valid[256];
extern uint8_t open_cfw_test_peer_active_connection;
extern uint8_t open_cfw_test_peer_target[8];
extern uint8_t open_cfw_test_peer_target_connect;
extern uint8_t open_cfw_test_peer_unpair_connection;
extern uint8_t open_cfw_test_peer_unpair_address[7];
extern uintptr_t open_cfw_test_peer_removed_callbacks[2];
extern unsigned int open_cfw_test_peer_event_count;
extern unsigned int open_cfw_test_peer_events[8];
extern unsigned int open_cfw_test_peer_find_calls;
extern unsigned int open_cfw_test_peer_compare_calls;
extern unsigned int open_cfw_test_peer_auth_mode_calls;
extern unsigned int open_cfw_test_peer_reset_calls;
extern unsigned int open_cfw_test_peer_remove_calls;
extern unsigned int open_cfw_test_peer_set_target_calls;
extern unsigned int open_cfw_test_peer_unpair_addr_calls;
extern unsigned int open_cfw_test_peer_unpair_conn_calls;

void open_cfw_test_peer_reset(void);
const uint8_t *open_cfw_test_peer_addr(uint8_t connection_id);
int open_cfw_test_peer_cmp(const uint8_t *left, const uint8_t *right);
uint8_t open_cfw_test_peer_active_conn_id(void);
void open_cfw_test_peer_auth_mode_set(uint8_t mode);
void open_cfw_test_peer_reset_retry(void);
void open_cfw_test_peer_remove_delayed(void *callback);
void open_cfw_test_peer_set_target(
    const uint8_t *address, const char *name, uint8_t connect
);
void open_cfw_test_peer_unpair_addr(const uint8_t *peer);
void open_cfw_test_peer_unpair_conn(uint8_t connection_id);

#define OPEN_CFW_APP_BLE_PEER_MANAGER_PENDING_PEER \
    open_cfw_test_peer_pending
#define OPEN_CFW_APP_BLE_PEER_MANAGER_CONNECTION_RECORDS \
    open_cfw_test_peer_records
#define OPEN_CFW_APP_BLE_PEER_MANAGER_DM_CONN_PEER_ADDR(connection_id) \
    open_cfw_test_peer_addr((connection_id))
#define OPEN_CFW_APP_BLE_PEER_MANAGER_BDA_CMP(left, right) \
    open_cfw_test_peer_cmp((left), (right))
#define OPEN_CFW_APP_BLE_PEER_MANAGER_ACTIVE_CONN_ID() \
    open_cfw_test_peer_active_conn_id()
#define OPEN_CFW_APP_BLE_PEER_MANAGER_AUTH_MODE_SET(mode) \
    open_cfw_test_peer_auth_mode_set((mode))
#define OPEN_CFW_APP_BLE_PEER_MANAGER_RESET_RETRY() \
    open_cfw_test_peer_reset_retry()
#define OPEN_CFW_APP_BLE_PEER_MANAGER_REMOVE_DELAYED(callback) \
    open_cfw_test_peer_remove_delayed((callback))
#define OPEN_CFW_APP_BLE_PEER_MANAGER_SET_TARGET(address, name, connect) \
    open_cfw_test_peer_set_target((address), (name), (connect))
#define OPEN_CFW_APP_BLE_PEER_MANAGER_UNPAIR_ADDR(peer) \
    open_cfw_test_peer_unpair_addr((peer))
#define OPEN_CFW_APP_BLE_PEER_MANAGER_UNPAIR_CONN(connection_id) \
    open_cfw_test_peer_unpair_conn((connection_id))
#define OPEN_CFW_APP_BLE_PEER_MANAGER_RECONNECT_CALLBACK_ADDRESS 0x1111U
#define OPEN_CFW_APP_BLE_PEER_MANAGER_UNPAIR_CALLBACK_ADDRESS 0x2222U

#endif
