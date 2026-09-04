/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the G2 BLE-status callback facade. Stock
 * EasyLogger calls in the null-callback branches are diagnostic-only and are
 * omitted; callback-list registration, removal, and dispatch are preserved.
 */

#include <stdint.h>

#if !defined(OPEN_CFW_CB_BLE_STATUS_REGISTER_ONLY) && \
    !defined(OPEN_CFW_CB_BLE_STATUS_UNREGISTER_ONLY) && \
    !defined(OPEN_CFW_CB_BLE_STATUS_NOTIFY_ONLY)
#define OPEN_CFW_CB_BLE_STATUS_ALL 1
#endif

#ifndef OPEN_CFW_CB_BLE_STATUS_LIST
#define OPEN_CFW_CB_BLE_STATUS_LIST ((void *)(uintptr_t)0x20073f6cu)
#endif

#ifndef OPEN_CFW_CB_BLE_STATUS_REGISTER
uint32_t open_cfw_callback_mgr_register(void *list, uintptr_t callback);
#define OPEN_CFW_CB_BLE_STATUS_REGISTER(list, callback) \
    open_cfw_callback_mgr_register((list), (callback))
#endif

#ifndef OPEN_CFW_CB_BLE_STATUS_UNREGISTER
void open_cfw_callback_mgr_unregister(void *list, uintptr_t callback);
#define OPEN_CFW_CB_BLE_STATUS_UNREGISTER(list, callback) \
    open_cfw_callback_mgr_unregister((list), (callback))
#endif

#ifndef OPEN_CFW_CB_BLE_STATUS_DISPATCH
void open_cfw_callback_mgr_notify(void *list, uint32_t event, uintptr_t value);
#define OPEN_CFW_CB_BLE_STATUS_DISPATCH(list, event, value) \
    open_cfw_callback_mgr_notify((list), (event), (uintptr_t)(value))
#endif

#if defined(OPEN_CFW_CB_BLE_STATUS_ALL) || \
    defined(OPEN_CFW_CB_BLE_STATUS_REGISTER_ONLY)
uint32_t open_cfw_cb_ble_status_register(uintptr_t callback)
{
    if (callback == (uintptr_t)0u) {
        return 0u;
    }
    return OPEN_CFW_CB_BLE_STATUS_REGISTER(
        OPEN_CFW_CB_BLE_STATUS_LIST, callback);
}
#endif

#if defined(OPEN_CFW_CB_BLE_STATUS_ALL) || \
    defined(OPEN_CFW_CB_BLE_STATUS_UNREGISTER_ONLY)
void open_cfw_cb_ble_status_unregister(uintptr_t callback)
{
    if (callback != (uintptr_t)0u) {
        OPEN_CFW_CB_BLE_STATUS_UNREGISTER(
            OPEN_CFW_CB_BLE_STATUS_LIST, callback);
    }
}
#endif

#if defined(OPEN_CFW_CB_BLE_STATUS_ALL) || \
    defined(OPEN_CFW_CB_BLE_STATUS_NOTIFY_ONLY)
uint32_t open_cfw_cb_ble_status_notify(uint32_t event, uint32_t status)
{
    OPEN_CFW_CB_BLE_STATUS_DISPATCH(
        OPEN_CFW_CB_BLE_STATUS_LIST, event, &status);
    return status;
}
#endif
