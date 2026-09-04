/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_APP_BLE_PEER_MANAGER_H
#define OPEN_CFW_APP_BLE_PEER_MANAGER_H

#include <stdint.h>

uint8_t open_cfw_app_ble_peer_manager_find_conn_id_by_addr(
    const uint8_t *address
);
void open_cfw_app_master_sec_clear_addr(void);
uint8_t *open_cfw_app_master_sec_get_addr(void);
void open_cfw_app_ble_master_peer_mgr_unpair_dev(
    uint8_t address_type, const uint8_t *address
);

#endif
