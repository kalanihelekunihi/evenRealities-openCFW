/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room product BLE message processor reconstructed from stock
 * bleProcMsg at 0x004B75CE...0x004B7D31.
 */

typedef __UINTPTR_TYPE__ open_cfw_app_ble_processor_uintptr;

#define OPEN_CFW_APP_BLE_PROCESSOR_CONTROL_ADDRESS 0x200727F0U
#define OPEN_CFW_APP_BLE_PROCESSOR_TICK_ADDRESS 0x200742F4U
#define OPEN_CFW_APP_BLE_PROCESSOR_FEATURE_ADDRESS 0x0078C9A4U

#ifndef OPEN_CFW_APP_BLE_PROCESSOR_CONTROL
#define OPEN_CFW_APP_BLE_PROCESSOR_CONTROL \
    ((volatile unsigned char *)(open_cfw_app_ble_processor_uintptr) \
        OPEN_CFW_APP_BLE_PROCESSOR_CONTROL_ADDRESS)
#endif
#ifndef OPEN_CFW_APP_BLE_PROCESSOR_TICK
#define OPEN_CFW_APP_BLE_PROCESSOR_TICK \
    ((volatile unsigned int *)(open_cfw_app_ble_processor_uintptr) \
        OPEN_CFW_APP_BLE_PROCESSOR_TICK_ADDRESS)
#endif
#ifndef OPEN_CFW_APP_BLE_PROCESSOR_FEATURES
#define OPEN_CFW_APP_BLE_PROCESSOR_FEATURES \
    ((const volatile unsigned char *)(open_cfw_app_ble_processor_uintptr) \
        OPEN_CFW_APP_BLE_PROCESSOR_FEATURE_ADDRESS)
#endif

#ifndef OPEN_CFW_APP_BLE_CALL0
typedef void (*open_cfw_app_ble_processor_call0_function)(void);
#define OPEN_CFW_APP_BLE_CALL0(address) \
    (((open_cfw_app_ble_processor_call0_function)((address) | 1U))())
#endif
#ifndef OPEN_CFW_APP_BLE_CALL1
typedef void (*open_cfw_app_ble_processor_call1_function)(
    open_cfw_app_ble_processor_uintptr
);
#define OPEN_CFW_APP_BLE_CALL1(address, argument0) \
    (((open_cfw_app_ble_processor_call1_function)((address) | 1U))( \
        (open_cfw_app_ble_processor_uintptr)(argument0)))
#endif
#ifndef OPEN_CFW_APP_BLE_CALL2
typedef void (*open_cfw_app_ble_processor_call2_function)(
    open_cfw_app_ble_processor_uintptr,
    open_cfw_app_ble_processor_uintptr
);
#define OPEN_CFW_APP_BLE_CALL2(address, argument0, argument1) \
    (((open_cfw_app_ble_processor_call2_function)((address) | 1U))( \
        (open_cfw_app_ble_processor_uintptr)(argument0), \
        (open_cfw_app_ble_processor_uintptr)(argument1)))
#endif

#ifndef OPEN_CFW_APP_BLE_CONNECTION_ROLE
typedef unsigned int (*open_cfw_app_ble_processor_connection_role_function)(
    unsigned int
);
#define OPEN_CFW_APP_BLE_CONNECTION_ROLE(connection) \
    (((open_cfw_app_ble_processor_connection_role_function)0x004B73C5U)( \
        (connection)))
#endif
#ifndef OPEN_CFW_APP_BLE_CCC_LOOKUP
typedef void *(*open_cfw_app_ble_processor_ccc_lookup_function)(unsigned int);
#define OPEN_CFW_APP_BLE_CCC_LOOKUP(connection) \
    (((open_cfw_app_ble_processor_ccc_lookup_function)0x004BB07DU)( \
        (connection)))
#endif
#ifndef OPEN_CFW_APP_BLE_TIMER_RELEASE
typedef void (*open_cfw_app_ble_processor_timer_release_function)(void *);
#define OPEN_CFW_APP_BLE_TIMER_RELEASE(callback) \
    (((open_cfw_app_ble_processor_timer_release_function)0x00476ACFU)( \
        (callback)))
#endif
#ifndef OPEN_CFW_APP_BLE_TIMER_START
typedef void (*open_cfw_app_ble_processor_timer_start_function)(
    void *, unsigned int, unsigned int
);
#define OPEN_CFW_APP_BLE_TIMER_START(callback, argument, milliseconds) \
    (((open_cfw_app_ble_processor_timer_start_function)0x0047697FU)( \
        (callback), (argument), (milliseconds)))
#endif
#ifndef OPEN_CFW_APP_BLE_QUERY_004BB9BC
typedef unsigned int (*open_cfw_app_ble_processor_query_004bb9bc_function)(void);
#define OPEN_CFW_APP_BLE_QUERY_004BB9BC() \
    (((open_cfw_app_ble_processor_query_004bb9bc_function)0x004BB9BDU)())
#endif
#ifndef OPEN_CFW_APP_BLE_QUERY_0052C914
typedef unsigned int (*open_cfw_app_ble_processor_query_0052c914_function)(void);
#define OPEN_CFW_APP_BLE_QUERY_0052C914() \
    (((open_cfw_app_ble_processor_query_0052c914_function)0x0052C915U)())
#endif
#ifndef OPEN_CFW_APP_BLE_TICK_COUNT
typedef unsigned int (*open_cfw_app_ble_processor_tick_count_function)(void);
#define OPEN_CFW_APP_BLE_TICK_COUNT() \
    (((open_cfw_app_ble_processor_tick_count_function)0x004490CDU)())
#endif

#ifndef OPEN_CFW_APP_BLE_PROCESSOR_DIAGNOSTIC
#define OPEN_CFW_APP_BLE_PROCESSOR_DIAGNOSTIC(event, message) \
    do { \
        (void)(event); \
        (void)(message); \
    } while (0)
#endif

#define OPEN_CFW_APP_BLE_TIMER_TOKEN(address) \
    ((void *)(open_cfw_app_ble_processor_uintptr)(address))

static unsigned int open_cfw_app_ble_clear_ccc_state(unsigned int connection)
{
    void *state = OPEN_CFW_APP_BLE_CCC_LOOKUP(connection);

    if (state != (void *)0) {
        OPEN_CFW_APP_BLE_CALL2(0x0047B488U, state, 0U);
        OPEN_CFW_APP_BLE_CALL2(0x0047B3CCU, state, 0U);
        return 1U;
    }
    return 0U;
}

__attribute__((used, noinline))
void open_cfw_app_ble_process_message(void *message_pointer)
{
    unsigned char *message = (unsigned char *)message_pointer;
    unsigned int connection = *(const unsigned short *)message;
    unsigned int event = message[2];
    unsigned int notification = 0U;
    void *reconnect_timer = OPEN_CFW_APP_BLE_TIMER_TOKEN(0x004BB92DU);
    void *connection_timer = OPEN_CFW_APP_BLE_TIMER_TOKEN(0x005354C3U);

    switch (event) {
    case 0x12U:
        OPEN_CFW_APP_BLE_CALL0(0x004D0C36U);
        if (message[3] != 0U) {
            OPEN_CFW_APP_BLE_PROCESSOR_DIAGNOSTIC(event, message);
        }
        break;
    case 0x15U:
        break;
    case 0x20U:
        OPEN_CFW_APP_BLE_CALL1(0x0052C6C0U, 1U);
        if ((*OPEN_CFW_APP_BLE_PROCESSOR_FEATURES & 0x08U) != 0U) {
            OPEN_CFW_APP_BLE_CALL0(0x005348ECU);
        } else {
            OPEN_CFW_APP_BLE_CALL0(0x0053527CU);
        }
        notification = 1U;
        break;
    case 0x27U:
        if (OPEN_CFW_APP_BLE_CONNECTION_ROLE(connection) == 1U) {
            OPEN_CFW_APP_BLE_CALL1(0x004BB9B4U, 0U);
            OPEN_CFW_APP_BLE_CALL1(0x004BBF44U, 0U);
        }
        OPEN_CFW_APP_BLE_CALL0(0x004D0C36U);
        if (open_cfw_app_ble_clear_ccc_state(connection) != 0U) {
            OPEN_CFW_APP_BLE_PROCESSOR_DIAGNOSTIC(event, message);
        }
        notification = 8U;
        break;
    case 0x28U:
        *OPEN_CFW_APP_BLE_PROCESSOR_TICK = 0U;
        OPEN_CFW_APP_BLE_CALL0(0x004D0C36U);
        OPEN_CFW_APP_BLE_TIMER_RELEASE(connection_timer);
        OPEN_CFW_APP_BLE_TIMER_RELEASE(
            OPEN_CFW_APP_BLE_TIMER_TOKEN(0x004B81B9U)
        );
        if (OPEN_CFW_APP_BLE_CONNECTION_ROLE(connection) == 1U) {
            OPEN_CFW_APP_BLE_CALL1(0x004BB9B4U, 0U);
        }
        OPEN_CFW_APP_BLE_PROCESSOR_DIAGNOSTIC(event, message);
        notification = 9U;
        break;
    case 0x2AU:
        OPEN_CFW_APP_BLE_CALL0(0x005348ECU);
        OPEN_CFW_APP_BLE_PROCESSOR_DIAGNOSTIC(event, message);
        if (OPEN_CFW_APP_BLE_CCC_LOOKUP(connection) != (void *)0) {
            OPEN_CFW_APP_BLE_CALL0(0x0047C084U);
            OPEN_CFW_APP_BLE_CALL0(0x0047BC30U);
        }
        notification = 10U;
        break;
    case 0x2BU:
        OPEN_CFW_APP_BLE_TIMER_RELEASE(reconnect_timer);
        OPEN_CFW_APP_BLE_TIMER_START(reconnect_timer, 0U, 10U);
        OPEN_CFW_APP_BLE_CALL0(0x005348ECU);
        OPEN_CFW_APP_BLE_PROCESSOR_DIAGNOSTIC(event, message);
        OPEN_CFW_APP_BLE_CALL2(0x0047C568U, connection, message[3]);
        notification = 11U;
        break;
    case 0x2CU:
        open_cfw_app_ble_clear_ccc_state(connection);
        if (connection != 0U &&
            OPEN_CFW_APP_BLE_CONNECTION_ROLE(connection) == 1U) {
            OPEN_CFW_APP_BLE_TIMER_RELEASE(connection_timer);
            OPEN_CFW_APP_BLE_TIMER_START(connection_timer, connection, 1000U);
        }
        OPEN_CFW_APP_BLE_CALL1(0x004B82E8U, 1U);
        if (OPEN_CFW_APP_BLE_QUERY_004BB9BC() == 0U) {
            OPEN_CFW_APP_BLE_CALL1(0x004BB9B4U, 1U);
        } else {
            OPEN_CFW_APP_BLE_TIMER_RELEASE(reconnect_timer);
            OPEN_CFW_APP_BLE_TIMER_START(reconnect_timer, 1U, 200U);
            OPEN_CFW_APP_BLE_TIMER_START(reconnect_timer, 1U, 1000U);
            OPEN_CFW_APP_BLE_TIMER_START(reconnect_timer, 1U, 2000U);
        }
        *OPEN_CFW_APP_BLE_PROCESSOR_TICK = OPEN_CFW_APP_BLE_TICK_COUNT();
        if (OPEN_CFW_APP_BLE_CONNECTION_ROLE(connection) == 0U) {
            OPEN_CFW_APP_BLE_CALL1(0x004C543EU, 0x10U);
        }
        OPEN_CFW_APP_BLE_PROCESSOR_DIAGNOSTIC(event, message);
        notification = 12U;
        break;
    case 0x2DU:
        notification = 13U;
        break;
    case 0x2EU:
        OPEN_CFW_APP_BLE_CALL1(0x004BAFDAU, message);
        break;
    case 0x34U:
        OPEN_CFW_APP_BLE_CALL1(0x005348FCU, message + 4);
        if (OPEN_CFW_APP_BLE_QUERY_0052C914() != 0U) {
            OPEN_CFW_APP_BLE_CALL0(0x0053527CU);
        }
        break;
    case 0x35U:
        OPEN_CFW_APP_BLE_CALL1(0x004BB030U, message);
        break;
    case 0x3CU:
    case 0x46U:
        OPEN_CFW_APP_BLE_PROCESSOR_DIAGNOSTIC(event, message);
        break;
    case 0x79U:
        notification = 30U;
        break;
    case 0xA5U:
        OPEN_CFW_APP_BLE_PROCESSOR_DIAGNOSTIC(event, message);
        if (connection != 0U) {
            OPEN_CFW_APP_BLE_CALL1(0x00531D60U, connection);
        }
        break;
    case 0xA6U:
        OPEN_CFW_APP_BLE_CALL1(0x004B48A6U, 0U);
        OPEN_CFW_APP_BLE_CALL0(0x004B3026U);
        break;
    case 0xBCU:
        OPEN_CFW_APP_BLE_PROCESSOR_DIAGNOSTIC(event, message);
        OPEN_CFW_APP_BLE_CALL0(0x0046F32CU);
        if (OPEN_CFW_APP_BLE_PROCESSOR_CONTROL[0x55] != 0U) {
            OPEN_CFW_APP_BLE_TIMER_RELEASE(
                OPEN_CFW_APP_BLE_TIMER_TOKEN(0x004BC419U)
            );
            OPEN_CFW_APP_BLE_CALL1(0x004BC418U, 0U);
            OPEN_CFW_APP_BLE_TIMER_RELEASE(
                OPEN_CFW_APP_BLE_TIMER_TOKEN(0x004722CDU)
            );
            OPEN_CFW_APP_BLE_TIMER_START(
                OPEN_CFW_APP_BLE_TIMER_TOKEN(0x004722CDU),
                0U,
                10000U
            );
        }
        break;
    default:
        break;
    }

    if (notification != 0U) {
        OPEN_CFW_APP_BLE_CALL1(0x004BD054U, notification);
    }
}
