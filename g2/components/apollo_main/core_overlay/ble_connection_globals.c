/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded BLE connection-global initializer matched to stock entry
 * 0x004780DC.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_globals_uintptr;

#ifndef OPEN_CFW_BLE_GLOBALS_ENDPOINT
#define OPEN_CFW_BLE_GLOBALS_ENDPOINT \
    (*(volatile unsigned char *)0x20074F8EU)
#endif
#ifndef OPEN_CFW_BLE_GLOBALS_CONNECTION
#define OPEN_CFW_BLE_GLOBALS_CONNECTION \
    (*(void *volatile *)0x20074338U)
#endif
#ifndef OPEN_CFW_BLE_GLOBALS_STATE
#define OPEN_CFW_BLE_GLOBALS_STATE \
    (*(void *volatile *)0x2007433CU)
#endif
#ifndef OPEN_CFW_BLE_GLOBALS_DEFAULTS
#define OPEN_CFW_BLE_GLOBALS_DEFAULTS \
    (*(const volatile unsigned short *volatile *)0x2007435CU)
#endif
#ifndef OPEN_CFW_BLE_GLOBALS_DEFAULTS_TABLE
#define OPEN_CFW_BLE_GLOBALS_DEFAULTS_TABLE \
    ((const volatile unsigned short *) \
        (open_cfw_ble_globals_uintptr)0x00784EB0U)
#endif

void open_cfw_ble_connection_initialize_globals(
    unsigned char endpoint,
    void *connection,
    void *state
)
{
    OPEN_CFW_BLE_GLOBALS_ENDPOINT = endpoint;
    OPEN_CFW_BLE_GLOBALS_CONNECTION = connection;
    OPEN_CFW_BLE_GLOBALS_STATE = state;
    OPEN_CFW_BLE_GLOBALS_DEFAULTS = OPEN_CFW_BLE_GLOBALS_DEFAULTS_TABLE;
}
