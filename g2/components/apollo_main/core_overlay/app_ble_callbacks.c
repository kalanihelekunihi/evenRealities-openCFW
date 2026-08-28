/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room product BLE callback surface reconstructed from stock
 * 0x004B7478...0x004B75CD.
 */

typedef __UINTPTR_TYPE__ open_cfw_app_ble_callback_uintptr;

#define OPEN_CFW_APP_BLE_CONTROL_ADDRESS 0x200727F0U
#define OPEN_CFW_APP_BLE_HANDLER_OFFSET 0x56U
#define OPEN_CFW_APP_BLE_DM_VARIABLE_EVENT 0x26U
#define OPEN_CFW_APP_BLE_DELAYED_EVENT 0xBCU

#ifndef OPEN_CFW_APP_BLE_CONTROL
#define OPEN_CFW_APP_BLE_CONTROL \
    ((volatile unsigned char *)(open_cfw_app_ble_callback_uintptr) \
        OPEN_CFW_APP_BLE_CONTROL_ADDRESS)
#endif

#ifndef OPEN_CFW_APP_BLE_CALL0
typedef void (*open_cfw_app_ble_call0_function)(void);
#define OPEN_CFW_APP_BLE_CALL0(address) \
    (((open_cfw_app_ble_call0_function)((address) | 1U))())
#endif

#ifndef OPEN_CFW_APP_BLE_DM_EVENT_SIZE
typedef unsigned int (*open_cfw_app_ble_dm_event_size_function)(const void *);
#define OPEN_CFW_APP_BLE_DM_EVENT_SIZE(event) \
    (((open_cfw_app_ble_dm_event_size_function)0x004D2ACDU)((event)))
#endif

#ifndef OPEN_CFW_APP_BLE_ALLOCATE
typedef void *(*open_cfw_app_ble_allocate_function)(unsigned int);
#define OPEN_CFW_APP_BLE_ALLOCATE(size) \
    (((open_cfw_app_ble_allocate_function)0x004BF99FU)((size)))
#endif

#ifndef OPEN_CFW_APP_BLE_COPY
typedef void *(*open_cfw_app_ble_copy_function)(void *, const void *, unsigned int);
#define OPEN_CFW_APP_BLE_COPY(destination, source, size) \
    (((open_cfw_app_ble_copy_function)0x00439BE5U)( \
        (destination), (source), (size)))
#endif

#ifndef OPEN_CFW_APP_BLE_LOAD_POINTER
#define OPEN_CFW_APP_BLE_LOAD_POINTER(base, offset) \
    ((const void *)(open_cfw_app_ble_callback_uintptr) \
        *(const unsigned int *)((const unsigned char *)(base) + (offset)))
#endif

#ifndef OPEN_CFW_APP_BLE_STORE_POINTER
#define OPEN_CFW_APP_BLE_STORE_POINTER(base, offset, value) \
    (*(unsigned int *)((unsigned char *)(base) + (offset)) = \
        (unsigned int)(open_cfw_app_ble_callback_uintptr)(value))
#endif

#ifndef OPEN_CFW_APP_BLE_MESSAGE_SEND
typedef void (*open_cfw_app_ble_message_send_function)(unsigned int, void *);
#define OPEN_CFW_APP_BLE_MESSAGE_SEND(handler, message) \
    (((open_cfw_app_ble_message_send_function)0x004BF9BBU)( \
        (handler), (message)))
#endif

#ifndef OPEN_CFW_APP_BLE_CCC_LOOKUP
typedef void *(*open_cfw_app_ble_ccc_lookup_function)(unsigned int);
#define OPEN_CFW_APP_BLE_CCC_LOOKUP(connection) \
    (((open_cfw_app_ble_ccc_lookup_function)0x004BB07DU)((connection)))
#endif

#ifndef OPEN_CFW_APP_BLE_CONNECTION_ACTIVE
typedef unsigned int (*open_cfw_app_ble_connection_active_function)(unsigned int);
#define OPEN_CFW_APP_BLE_CONNECTION_ACTIVE(connection) \
    (((open_cfw_app_ble_connection_active_function)0x004BAD27U)((connection)))
#endif

#ifndef OPEN_CFW_APP_BLE_CCC_UPDATE
typedef void (*open_cfw_app_ble_ccc_update_function)(void *, unsigned int, unsigned int);
#define OPEN_CFW_APP_BLE_CCC_UPDATE(state, index, value) \
    (((open_cfw_app_ble_ccc_update_function)0x0047B3E3U)( \
        (state), (index), (value)))
#endif

#ifndef OPEN_CFW_APP_BLE_TIMER_RELEASE
typedef void (*open_cfw_app_ble_timer_release_function)(void *);
#define OPEN_CFW_APP_BLE_TIMER_RELEASE(callback) \
    (((open_cfw_app_ble_timer_release_function)0x00476ACFU)((callback)))
#endif

#ifndef OPEN_CFW_APP_BLE_TIMER_START
typedef void (*open_cfw_app_ble_timer_start_function)(void *, unsigned int, unsigned int);
#define OPEN_CFW_APP_BLE_TIMER_START(callback, argument, milliseconds) \
    (((open_cfw_app_ble_timer_start_function)0x0047697FU)( \
        (callback), (argument), (milliseconds)))
#endif

static unsigned int open_cfw_app_ble_handler_id(void)
{
    return OPEN_CFW_APP_BLE_CONTROL[OPEN_CFW_APP_BLE_HANDLER_OFFSET];
}

__attribute__((used, noinline))
void open_cfw_app_ble_subsystem_initialize(void)
{
    OPEN_CFW_APP_BLE_CALL0(0x00503B76U);
    OPEN_CFW_APP_BLE_CALL0(0x004B3C02U);
    OPEN_CFW_APP_BLE_CALL0(0x00534866U);
    OPEN_CFW_APP_BLE_CALL0(0x00532E52U);
}

__attribute__((used, noinline))
void open_cfw_app_ble_dm_callback(const void *event_pointer)
{
    const unsigned char *event = (const unsigned char *)event_pointer;
    unsigned int event_size = OPEN_CFW_APP_BLE_DM_EVENT_SIZE(event_pointer);
    unsigned int extra_size = event[2] == OPEN_CFW_APP_BLE_DM_VARIABLE_EVENT
        ? event[8]
        : 0U;
    unsigned char *copy = (unsigned char *)OPEN_CFW_APP_BLE_ALLOCATE(
        (unsigned short)(event_size + extra_size)
    );

    if (copy == (unsigned char *)0) {
        return;
    }
    OPEN_CFW_APP_BLE_COPY(copy, event, (unsigned short)event_size);
    if (event[2] == OPEN_CFW_APP_BLE_DM_VARIABLE_EVENT) {
        void *payload = copy + (unsigned short)event_size;
        OPEN_CFW_APP_BLE_STORE_POINTER(copy, 4U, payload);
        OPEN_CFW_APP_BLE_COPY(
            payload,
            OPEN_CFW_APP_BLE_LOAD_POINTER(event, 4U),
            (unsigned short)extra_size
        );
    }
    OPEN_CFW_APP_BLE_MESSAGE_SEND(open_cfw_app_ble_handler_id(), copy);
}

__attribute__((used, noinline))
void open_cfw_app_ble_att_callback(const void *event_pointer)
{
    const unsigned char *event = (const unsigned char *)event_pointer;
    unsigned int value_length = *(const unsigned short *)(event + 8);
    unsigned char *copy = (unsigned char *)OPEN_CFW_APP_BLE_ALLOCATE(
        (unsigned short)(value_length + 16U)
    );

    if (copy == (unsigned char *)0) {
        return;
    }
    OPEN_CFW_APP_BLE_COPY(copy, event, 16U);
    OPEN_CFW_APP_BLE_STORE_POINTER(copy, 4U, copy + 16);
    OPEN_CFW_APP_BLE_COPY(
        copy + 16,
        OPEN_CFW_APP_BLE_LOAD_POINTER(event, 4U),
        (unsigned short)value_length
    );
    OPEN_CFW_APP_BLE_MESSAGE_SEND(open_cfw_app_ble_handler_id(), copy);
}

__attribute__((used, noinline))
void open_cfw_app_ble_ccc_callback(const void *event_pointer)
{
    const unsigned char *event = (const unsigned char *)event_pointer;
    unsigned int connection = *(const unsigned short *)event;
    unsigned char *copy;

    if (*(const unsigned short *)(event + 4) != 0U) {
        void *state = OPEN_CFW_APP_BLE_CCC_LOOKUP((unsigned char)connection);
        if (state != (void *)0 &&
            OPEN_CFW_APP_BLE_CONNECTION_ACTIVE((unsigned char)connection) != 0U) {
            OPEN_CFW_APP_BLE_CCC_UPDATE(
                state,
                event[8],
                *(const unsigned short *)(event + 6)
            );
        }
    }

    copy = (unsigned char *)OPEN_CFW_APP_BLE_ALLOCATE(10U);
    if (copy == (unsigned char *)0) {
        return;
    }
    OPEN_CFW_APP_BLE_COPY(copy, event, 10U);
    OPEN_CFW_APP_BLE_MESSAGE_SEND(open_cfw_app_ble_handler_id(), copy);
}

__attribute__((used, noinline))
void open_cfw_app_ble_delayed_start_callback(void *message)
{
    void *event;

    (void)message;
    OPEN_CFW_APP_BLE_TIMER_RELEASE(open_cfw_app_ble_delayed_start_callback);
    event = OPEN_CFW_APP_BLE_ALLOCATE(12U);
    if (event != (void *)0) {
        ((unsigned char *)event)[2] = OPEN_CFW_APP_BLE_DELAYED_EVENT;
        OPEN_CFW_APP_BLE_MESSAGE_SEND(open_cfw_app_ble_handler_id(), event);
        OPEN_CFW_APP_BLE_TIMER_START(
            open_cfw_app_ble_delayed_start_callback,
            0U,
            10000U
        );
    } else {
        OPEN_CFW_APP_BLE_TIMER_START(
            open_cfw_app_ble_delayed_start_callback,
            0U,
            20000U
        );
    }
}
