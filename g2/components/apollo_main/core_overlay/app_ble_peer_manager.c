/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room implementation of the G2 Cordio application peer-manager
 * adapter. Diagnostic logging from the retained object is intentionally
 * omitted; connection lookup and unpair sequencing are preserved.
 */
#include "app_ble_peer_manager.h"

#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_APP_BLE_PEER_MANAGER_PENDING_PEER
#define OPEN_CFW_APP_BLE_PEER_MANAGER_PENDING_PEER \
    ((volatile uint8_t *)(uintptr_t)0x200003D8U)
#endif

#ifndef OPEN_CFW_APP_BLE_PEER_MANAGER_CONNECTION_RECORDS
#define OPEN_CFW_APP_BLE_PEER_MANAGER_CONNECTION_RECORDS \
    ((volatile uint8_t *)(uintptr_t)0x200717B0U)
#endif

#ifndef OPEN_CFW_APP_BLE_PEER_MANAGER_DM_CONN_PEER_ADDR
const uint8_t *open_cfw_retained_dm_conn_peer_addr(uint8_t connection_id);
#define OPEN_CFW_APP_BLE_PEER_MANAGER_DM_CONN_PEER_ADDR(connection_id) \
    open_cfw_retained_dm_conn_peer_addr((connection_id))
#endif

#ifndef OPEN_CFW_APP_BLE_PEER_MANAGER_BDA_CMP
int open_cfw_retained_bda_cmp(
    const uint8_t *left, const uint8_t *right
);
#define OPEN_CFW_APP_BLE_PEER_MANAGER_BDA_CMP(left, right) \
    open_cfw_retained_bda_cmp((left), (right))
#endif

#ifndef OPEN_CFW_APP_BLE_PEER_MANAGER_ACTIVE_CONN_ID
uint8_t open_cfw_retained_app_master_active_conn_id(void);
#define OPEN_CFW_APP_BLE_PEER_MANAGER_ACTIVE_CONN_ID() \
    open_cfw_retained_app_master_active_conn_id()
#endif

#ifndef OPEN_CFW_APP_BLE_PEER_MANAGER_AUTH_MODE_SET
void open_cfw_retained_app_master_auth_mode_set(uint8_t mode);
#define OPEN_CFW_APP_BLE_PEER_MANAGER_AUTH_MODE_SET(mode) \
    open_cfw_retained_app_master_auth_mode_set((mode))
#endif

#ifndef OPEN_CFW_APP_BLE_PEER_MANAGER_RESET_RETRY
void open_cfw_retained_app_master_reset_retry(void);
#define OPEN_CFW_APP_BLE_PEER_MANAGER_RESET_RETRY() \
    open_cfw_retained_app_master_reset_retry()
#endif

#ifndef OPEN_CFW_APP_BLE_PEER_MANAGER_REMOVE_DELAYED
void open_cfw_retained_event_loop_remove_delayed(void *callback);
#define OPEN_CFW_APP_BLE_PEER_MANAGER_REMOVE_DELAYED(callback) \
    open_cfw_retained_event_loop_remove_delayed((callback))
#endif

#ifndef OPEN_CFW_APP_BLE_PEER_MANAGER_SET_TARGET
void open_cfw_retained_app_master_set_target_addr_name(
    const uint8_t *address, const char *name, uint8_t connect
);
#define OPEN_CFW_APP_BLE_PEER_MANAGER_SET_TARGET(address, name, connect) \
    open_cfw_retained_app_master_set_target_addr_name( \
        (address), (name), (connect) \
    )
#endif

#ifndef OPEN_CFW_APP_BLE_PEER_MANAGER_UNPAIR_ADDR
void open_cfw_retained_app_master_unpair_dev_event(const uint8_t *peer);
#define OPEN_CFW_APP_BLE_PEER_MANAGER_UNPAIR_ADDR(peer) \
    open_cfw_retained_app_master_unpair_dev_event((peer))
#endif

#ifndef OPEN_CFW_APP_BLE_PEER_MANAGER_UNPAIR_CONN
void open_cfw_retained_app_master_unpair_conn_id_event(uint8_t connection_id);
#define OPEN_CFW_APP_BLE_PEER_MANAGER_UNPAIR_CONN(connection_id) \
    open_cfw_retained_app_master_unpair_conn_id_event((connection_id))
#endif

#ifndef OPEN_CFW_APP_BLE_PEER_MANAGER_RECONNECT_CALLBACK_ADDRESS
#define OPEN_CFW_APP_BLE_PEER_MANAGER_RECONNECT_CALLBACK_ADDRESS 0x004A1B61U
#endif

#ifndef OPEN_CFW_APP_BLE_PEER_MANAGER_UNPAIR_CALLBACK_ADDRESS
#define OPEN_CFW_APP_BLE_PEER_MANAGER_UNPAIR_CALLBACK_ADDRESS 0x004A23ADU
#endif

#if defined(OPEN_CFW_APP_BLE_PEER_MANAGER_FIND_ONLY)
#define OPEN_CFW_APP_BLE_PEER_MANAGER_SELECTOR 1
#elif defined(OPEN_CFW_APP_BLE_PEER_MANAGER_CLEAR_ONLY)
#define OPEN_CFW_APP_BLE_PEER_MANAGER_SELECTOR 2
#elif defined(OPEN_CFW_APP_BLE_PEER_MANAGER_GET_ONLY)
#define OPEN_CFW_APP_BLE_PEER_MANAGER_SELECTOR 3
#elif defined(OPEN_CFW_APP_BLE_PEER_MANAGER_UNPAIR_ONLY)
#define OPEN_CFW_APP_BLE_PEER_MANAGER_SELECTOR 4
#elif !defined(OPEN_CFW_APP_BLE_PEER_MANAGER_SELECTOR)
#define OPEN_CFW_APP_BLE_PEER_MANAGER_SELECTOR 0
#endif

#define OPEN_CFW_APP_BLE_PEER_MANAGER_BUILD(number) \
    (OPEN_CFW_APP_BLE_PEER_MANAGER_SELECTOR == 0 || \
     OPEN_CFW_APP_BLE_PEER_MANAGER_SELECTOR == (number))

#if defined(__arm__) || defined(__thumb__)
__asm__(
    ".type open_cfw_app_ble_peer_manager_find_conn_id_by_addr,%function\n"
    ".type open_cfw_app_master_sec_clear_addr,%function\n"
    ".type open_cfw_app_master_sec_get_addr,%function\n"
    ".type open_cfw_app_ble_master_peer_mgr_unpair_dev,%function\n"
);
#endif

#if OPEN_CFW_APP_BLE_PEER_MANAGER_BUILD(1)
__attribute__((used, noinline))
uint8_t open_cfw_app_ble_peer_manager_find_conn_id_by_addr(
    const uint8_t *address
)
{
    unsigned int index;

    if (address == NULL) {
        return 0U;
    }
    for (index = 0U; index < 3U; ++index) {
        uint8_t connection_id =
            OPEN_CFW_APP_BLE_PEER_MANAGER_CONNECTION_RECORDS[
                index * 48U + 4U
            ];
        if (connection_id != 0U) {
            const uint8_t *peer =
                OPEN_CFW_APP_BLE_PEER_MANAGER_DM_CONN_PEER_ADDR(
                    connection_id
                );
            if (peer != NULL &&
                    OPEN_CFW_APP_BLE_PEER_MANAGER_BDA_CMP(peer, address) != 0) {
                return connection_id;
            }
        }
    }
    return 0U;
}
#endif

#if OPEN_CFW_APP_BLE_PEER_MANAGER_BUILD(2)
__attribute__((used, noinline))
void open_cfw_app_master_sec_clear_addr(void)
{
    unsigned int index;

    for (index = 0U; index < 7U; ++index) {
        OPEN_CFW_APP_BLE_PEER_MANAGER_PENDING_PEER[index] = 0U;
    }
    OPEN_CFW_APP_BLE_PEER_MANAGER_PENDING_PEER[6] = UINT8_MAX;
}
#endif

#if OPEN_CFW_APP_BLE_PEER_MANAGER_BUILD(3)
__attribute__((used, noinline))
uint8_t *open_cfw_app_master_sec_get_addr(void)
{
    return (uint8_t *)(uintptr_t)OPEN_CFW_APP_BLE_PEER_MANAGER_PENDING_PEER;
}
#endif

#if OPEN_CFW_APP_BLE_PEER_MANAGER_BUILD(4)
__attribute__((used, noinline))
void open_cfw_app_ble_master_peer_mgr_unpair_dev(
    uint8_t address_type, const uint8_t *address
)
{
    uint8_t disconnected_target[8];
    char empty_name[1];
    uint8_t connection_id;
    unsigned int index;

    if (address == NULL) {
        return;
    }
    for (index = 0U; index < 6U; ++index) {
        OPEN_CFW_APP_BLE_PEER_MANAGER_PENDING_PEER[index] = address[index];
    }
    OPEN_CFW_APP_BLE_PEER_MANAGER_PENDING_PEER[6] = address_type;

    connection_id = OPEN_CFW_APP_BLE_PEER_MANAGER_ACTIVE_CONN_ID();
    if (connection_id == 0U) {
        connection_id =
            open_cfw_app_ble_peer_manager_find_conn_id_by_addr(address);
    }

    if (connection_id != 0U) {
        OPEN_CFW_APP_BLE_PEER_MANAGER_RESET_RETRY();
        OPEN_CFW_APP_BLE_PEER_MANAGER_REMOVE_DELAYED(
            (void *)(uintptr_t)
                OPEN_CFW_APP_BLE_PEER_MANAGER_RECONNECT_CALLBACK_ADDRESS
        );
        OPEN_CFW_APP_BLE_PEER_MANAGER_UNPAIR_CONN(connection_id);
        return;
    }

    OPEN_CFW_APP_BLE_PEER_MANAGER_AUTH_MODE_SET(0U);
    OPEN_CFW_APP_BLE_PEER_MANAGER_RESET_RETRY();
    OPEN_CFW_APP_BLE_PEER_MANAGER_REMOVE_DELAYED(
        (void *)(uintptr_t)
            OPEN_CFW_APP_BLE_PEER_MANAGER_RECONNECT_CALLBACK_ADDRESS
    );
    OPEN_CFW_APP_BLE_PEER_MANAGER_REMOVE_DELAYED(
        (void *)(uintptr_t)
            OPEN_CFW_APP_BLE_PEER_MANAGER_UNPAIR_CALLBACK_ADDRESS
    );
    for (index = 0U; index < 6U; ++index) {
        disconnected_target[index] = UINT8_MAX;
    }
    disconnected_target[6] = 0U;
    disconnected_target[7] = 0U;
    empty_name[0] = '\0';
    OPEN_CFW_APP_BLE_PEER_MANAGER_SET_TARGET(
        disconnected_target, empty_name, 0U
    );
    OPEN_CFW_APP_BLE_PEER_MANAGER_UNPAIR_ADDR(
        (const uint8_t *)(uintptr_t)
            OPEN_CFW_APP_BLE_PEER_MANAGER_PENDING_PEER
    );
}
#endif
