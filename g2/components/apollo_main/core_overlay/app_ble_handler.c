/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room registered product BLE WSF handler reconstructed from stock
 * _bleCommHandler at 0x004B7D32...0x004B7E73.
 */

typedef __UINTPTR_TYPE__ open_cfw_app_ble_handler_uintptr;

#ifndef OPEN_CFW_APP_BLE_CALL0
typedef void (*open_cfw_app_ble_handler_call0_function)(void);
#define OPEN_CFW_APP_BLE_CALL0(address) \
    (((open_cfw_app_ble_handler_call0_function)((address) | 1U))())
#endif
#ifndef OPEN_CFW_APP_BLE_CALL1
typedef void (*open_cfw_app_ble_handler_call1_function)(
    open_cfw_app_ble_handler_uintptr
);
#define OPEN_CFW_APP_BLE_CALL1(address, argument0) \
    (((open_cfw_app_ble_handler_call1_function)((address) | 1U))( \
        (open_cfw_app_ble_handler_uintptr)(argument0)))
#endif
#ifndef OPEN_CFW_APP_BLE_CALL2
typedef void (*open_cfw_app_ble_handler_call2_function)(
    open_cfw_app_ble_handler_uintptr,
    open_cfw_app_ble_handler_uintptr
);
#define OPEN_CFW_APP_BLE_CALL2(address, argument0, argument1) \
    (((open_cfw_app_ble_handler_call2_function)((address) | 1U))( \
        (open_cfw_app_ble_handler_uintptr)(argument0), \
        (open_cfw_app_ble_handler_uintptr)(argument1)))
#endif

#ifndef OPEN_CFW_APP_BLE_CONNECTION_ROLE
typedef unsigned int (*open_cfw_app_ble_connection_role_function)(unsigned int);
#define OPEN_CFW_APP_BLE_CONNECTION_ROLE(connection) \
    (((open_cfw_app_ble_connection_role_function)0x004B73C5U)((connection)))
#endif

#ifndef OPEN_CFW_APP_BLE_RING_CONNECTION_ACTIVE
typedef unsigned int (*open_cfw_app_ble_ring_connection_function)(void);
#define OPEN_CFW_APP_BLE_RING_CONNECTION_ACTIVE() \
    (((open_cfw_app_ble_ring_connection_function)0x0046EF61U)())
#endif

#ifndef OPEN_CFW_APP_BLE_HANDLER_DIAGNOSTIC
#define OPEN_CFW_APP_BLE_HANDLER_DIAGNOSTIC(message, role) \
    do { \
        (void)(message); \
        (void)(role); \
    } while (0)
#endif

void open_cfw_app_ble_process_message(void *message);

__attribute__((used, noinline))
void open_cfw_app_ble_handler(unsigned int handler_id, void *message_pointer)
{
    unsigned char *message = (unsigned char *)message_pointer;
    unsigned int event;
    unsigned int connection;
    unsigned int role;

    if (message == (unsigned char *)0) {
        return;
    }
    event = message[2];
    if (event >= 2U && event < 0x19U) {
        OPEN_CFW_APP_BLE_CALL1(0x00532924U, message);
        OPEN_CFW_APP_BLE_CALL1(0x0053484CU, message);
    } else if (event >= 0x20U && event < 0x7CU) {
        connection = *(const unsigned short *)message;
        role = OPEN_CFW_APP_BLE_CONNECTION_ROLE((unsigned char)connection);
        OPEN_CFW_APP_BLE_HANDLER_DIAGNOSTIC(message, role);

        if (connection == 0U || role == 0U) {
            OPEN_CFW_APP_BLE_CALL1(0x00503B92U, message);
            OPEN_CFW_APP_BLE_CALL1(0x00503C32U, message);
        }
        if (connection == 0U || role == 1U) {
            if (OPEN_CFW_APP_BLE_RING_CONNECTION_ACTIVE() == 0U ||
                event != 0x22U) {
                OPEN_CFW_APP_BLE_CALL1(0x004B3CA4U, message);
            }
            OPEN_CFW_APP_BLE_CALL1(0x004B45B0U, message);
        }
        OPEN_CFW_APP_BLE_CALL1(0x005322BCU, message);
    }

    open_cfw_app_ble_process_message(message);
    OPEN_CFW_APP_BLE_CALL2(0x0046EF74U, (unsigned char)handler_id, message);
    OPEN_CFW_APP_BLE_CALL2(0x004A19C0U, (unsigned char)handler_id, message);
}
