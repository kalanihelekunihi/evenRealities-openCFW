/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stdlib.h>

static uint32_t register_calls;
static uint32_t unregister_calls;
static uint32_t dispatch_calls;
static void *observed_list;
static uintptr_t observed_callback;
static uint32_t observed_event;

static uint32_t host_register(void *list, uintptr_t callback)
{
    register_calls++;
    observed_list = list;
    observed_callback = callback;
    return 7u;
}

static void host_unregister(void *list, uintptr_t callback)
{
    unregister_calls++;
    observed_list = list;
    observed_callback = callback;
}

static void host_dispatch(void *list, uint32_t event, uintptr_t value)
{
    dispatch_calls++;
    observed_list = list;
    observed_event = event;
    *(uint32_t *)value = 0xa55a5aa5u;
}

#define OPEN_CFW_CB_BLE_STATUS_LIST ((void *)(uintptr_t)0x12345678u)
#define OPEN_CFW_CB_BLE_STATUS_REGISTER(list, callback) \
    host_register((list), (callback))
#define OPEN_CFW_CB_BLE_STATUS_UNREGISTER(list, callback) \
    host_unregister((list), (callback))
#define OPEN_CFW_CB_BLE_STATUS_DISPATCH(list, event, value) \
    host_dispatch((list), (event), (uintptr_t)(value))
#include "../../components/apollo_main/core_overlay/cb_ble_status.c"

static void require(int condition)
{
    if (!condition) {
        abort();
    }
}

int main(void)
{
    require(open_cfw_cb_ble_status_register((uintptr_t)0u) == 0u);
    require(register_calls == 0u);

    require(open_cfw_cb_ble_status_register((uintptr_t)0x10203041u) == 7u);
    require(register_calls == 1u);
    require(observed_list == OPEN_CFW_CB_BLE_STATUS_LIST);
    require(observed_callback == (uintptr_t)0x10203041u);

    open_cfw_cb_ble_status_unregister((uintptr_t)0u);
    require(unregister_calls == 0u);
    open_cfw_cb_ble_status_unregister((uintptr_t)0x50607081u);
    require(unregister_calls == 1u);
    require(observed_list == OPEN_CFW_CB_BLE_STATUS_LIST);
    require(observed_callback == (uintptr_t)0x50607081u);

    require(open_cfw_cb_ble_status_notify(19u, 3u) == 0xa55a5aa5u);
    require(dispatch_calls == 1u);
    require(observed_list == OPEN_CFW_CB_BLE_STATUS_LIST);
    require(observed_event == 19u);
    return 0;
}
