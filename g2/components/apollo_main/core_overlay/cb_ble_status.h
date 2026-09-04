/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_CB_BLE_STATUS_H
#define OPEN_CFW_CB_BLE_STATUS_H

#include <stdint.h>

uint32_t open_cfw_cb_ble_status_register(uintptr_t callback);
void open_cfw_cb_ble_status_unregister(uintptr_t callback);
uint32_t open_cfw_cb_ble_status_notify(uint32_t event, uint32_t status);

#endif
