/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the BLE connection-global initializer.
 */

volatile unsigned char open_cfw_test_ble_globals_endpoint;
void *open_cfw_test_ble_globals_connection;
void *open_cfw_test_ble_globals_state;
const volatile unsigned short *open_cfw_test_ble_globals_defaults;

#define OPEN_CFW_BLE_GLOBALS_ENDPOINT \
    open_cfw_test_ble_globals_endpoint
#define OPEN_CFW_BLE_GLOBALS_CONNECTION \
    open_cfw_test_ble_globals_connection
#define OPEN_CFW_BLE_GLOBALS_STATE \
    open_cfw_test_ble_globals_state
#define OPEN_CFW_BLE_GLOBALS_DEFAULTS \
    open_cfw_test_ble_globals_defaults

#include "../../components/apollo_main/core_overlay/ble_connection_globals.c"

void open_cfw_test_ble_globals_reset(void)
{
    open_cfw_test_ble_globals_endpoint = 0U;
    open_cfw_test_ble_globals_connection = (void *)0;
    open_cfw_test_ble_globals_state = (void *)0;
    open_cfw_test_ble_globals_defaults =
        (const volatile unsigned short *)0;
}
