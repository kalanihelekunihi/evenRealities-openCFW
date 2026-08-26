/* SPDX-License-Identifier: Apache-2.0 */

/* G2 Cordio slave application-framework resolution and DM dispatch leaves. */

typedef unsigned char open_cfw_app_slave_u8;
typedef unsigned short open_cfw_app_slave_u16;
typedef unsigned int open_cfw_app_slave_u32;

typedef void (*open_cfw_app_slave_callback_t)(void *);

enum {
    OPEN_CFW_APP_SLAVE_CONNECTION_MAX = 3,
    OPEN_CFW_APP_SLAVE_CONNECTION_STRIDE = 0x30,
    OPEN_CFW_APP_SLAVE_DB_HANDLE_OFFSET = 0,
    OPEN_CFW_APP_SLAVE_CONNECTION_ID_OFFSET = 4,
    OPEN_CFW_APP_SLAVE_PENDING_LTK_OFFSET = 0x6C,
    OPEN_CFW_APP_SLAVE_RESOLUTION_HANDLE_OFFSET = 0x70,
    OPEN_CFW_APP_SLAVE_RESOLUTION_ACTIVE_OFFSET = 0x74,
    OPEN_CFW_APP_SLAVE_CALLBACK_OFFSET = 0x78,
    OPEN_CFW_APP_SLAVE_DATABASE_KEY_IRK = 4,
    OPEN_CFW_APP_SLAVE_DATABASE_KEY_CSRK = 8,
    OPEN_CFW_APP_SLAVE_CLIENT_CHANGE_UNAWARE = 3,
    OPEN_CFW_APP_SLAVE_HCI_SUCCESS = 0,
    OPEN_CFW_APP_SLAVE_HCI_AUTH_FAILURE = 5,
    OPEN_CFW_APP_SLAVE_DM_RESET_COMPLETE = 0x20,
    OPEN_CFW_APP_SLAVE_DM_CONNECTION_OPEN = 0x27,
    OPEN_CFW_APP_SLAVE_DM_CONNECTION_CLOSE = 0x28,
    OPEN_CFW_APP_SLAVE_DM_CONNECTION_UPDATE = 0x29,
    OPEN_CFW_APP_SLAVE_DM_RESOLVED_ADDRESS = 0x37,
    OPEN_CFW_APP_SLAVE_DM_REMOTE_CONNECTION_PARAMETER = 0x40,
    OPEN_CFW_APP_SLAVE_DM_DIAGNOSTIC_41 = 0x41,
    OPEN_CFW_APP_SLAVE_DM_ADV_SET_STOP = 0x48,
    OPEN_CFW_APP_SLAVE_DM_VENDOR_57 = 0x57,
    OPEN_CFW_APP_SLAVE_DM_RESET_EXTENSION = 0x79
};

#ifdef OPEN_CFW_CORDIO_APP_SLAVE_PRODUCTION
#define OPEN_CFW_APP_SLAVE_STATE \
    ((volatile open_cfw_app_slave_u8 *)0x200719C8U)
#define OPEN_CFW_APP_SLAVE_CONNECTION_STATE \
    ((volatile open_cfw_app_slave_u8 *)0x200717B0U)
#define OPEN_CFW_APP_SLAVE_SECURITY_CONFIG \
    (*(volatile open_cfw_app_slave_u8 * volatile *)0x20074358U)
#define OPEN_CFW_APP_SLAVE_DATABASE_READY \
    (*(volatile open_cfw_app_slave_u8 *)0x20074F93U)
#define OPEN_CFW_APP_SLAVE_CALLBACK \
    (*(open_cfw_app_slave_callback_t volatile *)0x20071A40U)
#else
extern volatile open_cfw_app_slave_u8 open_cfw_app_slave_runtime_state[0x80];
extern volatile open_cfw_app_slave_u8
    open_cfw_app_slave_connection_state[
        OPEN_CFW_APP_SLAVE_CONNECTION_MAX
        * OPEN_CFW_APP_SLAVE_CONNECTION_STRIDE
    ];
extern volatile open_cfw_app_slave_u8 *open_cfw_app_slave_security_config;
extern volatile open_cfw_app_slave_u8 open_cfw_app_slave_database_ready;
extern open_cfw_app_slave_callback_t open_cfw_app_slave_callback;
#define OPEN_CFW_APP_SLAVE_STATE open_cfw_app_slave_runtime_state
#define OPEN_CFW_APP_SLAVE_CONNECTION_STATE open_cfw_app_slave_connection_state
#define OPEN_CFW_APP_SLAVE_SECURITY_CONFIG open_cfw_app_slave_security_config
#define OPEN_CFW_APP_SLAVE_DATABASE_READY open_cfw_app_slave_database_ready
#define OPEN_CFW_APP_SLAVE_CALLBACK open_cfw_app_slave_callback
#endif

void open_cfw_mram_sync_records(void);
open_cfw_app_slave_u32 open_cfw_app_database_get_next_record(
    open_cfw_app_slave_u32
);
open_cfw_app_slave_u8 *open_cfw_app_slave_database_get_key(
    open_cfw_app_slave_u32, open_cfw_app_slave_u8, open_cfw_app_slave_u8 *
);
open_cfw_app_slave_u8 *open_cfw_cordio_dm_connection_peer_address(
    open_cfw_app_slave_u8
);
void open_cfw_cordio_dm_priv_resolve_address(
    open_cfw_app_slave_u8 *, open_cfw_app_slave_u8 *, open_cfw_app_slave_u16
);
void open_cfw_cordio_atts_ccc_initialize_table(
    open_cfw_app_slave_u8, open_cfw_app_slave_u16 *
);
void open_cfw_app_database_get_csf_record(
    open_cfw_app_slave_u32, open_cfw_app_slave_u8 *, open_cfw_app_slave_u8 **
);
void open_cfw_cordio_atts_csf_connection_open(
    open_cfw_app_slave_u8, open_cfw_app_slave_u8, open_cfw_app_slave_u8 *
);
void open_cfw_cordio_gatt_send_service_changed_indication(
    open_cfw_app_slave_u8, open_cfw_app_slave_u16, open_cfw_app_slave_u16
);
void open_cfw_cordio_atts_set_csrk(
    open_cfw_app_slave_u8, open_cfw_app_slave_u8 *, open_cfw_app_slave_u8
);
void open_cfw_cordio_atts_set_sign_counter(
    open_cfw_app_slave_u8, open_cfw_app_slave_u32
);
void open_cfw_app_slave_security_respond_ltk_internal(
    volatile open_cfw_app_slave_u8 *
);
void open_cfw_app_slave_reset_event_internal(
    const void *, volatile open_cfw_app_slave_u8 *
);
void open_cfw_app_slave_connection_open_event_internal(
    const void *, volatile open_cfw_app_slave_u8 *
);
void open_cfw_app_slave_connection_close_event_internal(
    const void *, volatile open_cfw_app_slave_u8 *
);
void open_cfw_app_slave_remote_parameter_event_internal(
    const void *, volatile open_cfw_app_slave_u8 *
);
void open_cfw_app_slave_reset_extension_internal(open_cfw_app_slave_u8);
void open_cfw_app_slave_advertising_reset_internal(void);

#ifndef OPEN_CFW_CORDIO_APP_SLAVE_PRODUCTION
open_cfw_app_slave_u16 *open_cfw_app_slave_test_ccc_table(
    open_cfw_app_slave_u32
);
open_cfw_app_slave_u32 open_cfw_app_slave_test_sign_counter(
    open_cfw_app_slave_u32
);
#endif

void open_cfw_app_slave_resolve_address(const void *);
void open_cfw_app_slave_resolved_address_event(
    const void *, volatile open_cfw_app_slave_u8 *
);
void open_cfw_app_slave_process_dm_message(void *);

#if !defined(OPEN_CFW_CORDIO_APP_SLAVE_RESOLVE_ADDRESS_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_SLAVE_RESOLVED_EVENT_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_SLAVE_PROCESS_DM_ONLY)
#define OPEN_CFW_CORDIO_APP_SLAVE_BUILD_ALL 1
#endif

static __attribute__((always_inline, unused)) inline open_cfw_app_slave_u16
open_cfw_app_slave_load_u16(const volatile open_cfw_app_slave_u8 *value)
{
    return (open_cfw_app_slave_u16)value[0]
        | (open_cfw_app_slave_u16)(
            (open_cfw_app_slave_u16)value[1] << 8U
        );
}

static __attribute__((always_inline, unused)) inline open_cfw_app_slave_u32
open_cfw_app_slave_load_u32(const volatile open_cfw_app_slave_u8 *value)
{
    return (open_cfw_app_slave_u32)value[0]
        | ((open_cfw_app_slave_u32)value[1] << 8U)
        | ((open_cfw_app_slave_u32)value[2] << 16U)
        | ((open_cfw_app_slave_u32)value[3] << 24U);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_app_slave_store_u32(
    volatile open_cfw_app_slave_u8 *value, open_cfw_app_slave_u32 data
)
{
    value[0] = (open_cfw_app_slave_u8)data;
    value[1] = (open_cfw_app_slave_u8)(data >> 8U);
    value[2] = (open_cfw_app_slave_u8)(data >> 16U);
    value[3] = (open_cfw_app_slave_u8)(data >> 24U);
}

static __attribute__((always_inline, unused)) inline volatile open_cfw_app_slave_u8 *
open_cfw_app_slave_connection(open_cfw_app_slave_u8 connection_id)
{
    return OPEN_CFW_APP_SLAVE_CONNECTION_STATE
        + (open_cfw_app_slave_u32)(connection_id - 1U)
            * OPEN_CFW_APP_SLAVE_CONNECTION_STRIDE;
}

static __attribute__((always_inline, unused)) inline open_cfw_app_slave_u16 *
open_cfw_app_slave_ccc_table(open_cfw_app_slave_u32 record)
{
#ifdef OPEN_CFW_CORDIO_APP_SLAVE_PRODUCTION
    return (open_cfw_app_slave_u16 *)(record + 0x6CU);
#else
    return open_cfw_app_slave_test_ccc_table(record);
#endif
}

static __attribute__((always_inline, unused)) inline open_cfw_app_slave_u32
open_cfw_app_slave_sign_counter(open_cfw_app_slave_u32 record)
{
#ifdef OPEN_CFW_CORDIO_APP_SLAVE_PRODUCTION
    return *(volatile open_cfw_app_slave_u32 *)(record + 0x80U);
#else
    return open_cfw_app_slave_test_sign_counter(record);
#endif
}

static __attribute__((always_inline, unused)) inline void
open_cfw_app_slave_begin_resolution(
    open_cfw_app_slave_u16 parameter,
    volatile open_cfw_app_slave_u8 *connection,
    open_cfw_app_slave_u32 previous_record
)
{
    open_cfw_app_slave_u32 record = previous_record;
    open_cfw_app_slave_u8 *key;
    open_cfw_app_slave_u8 *address;
    do {
        record = open_cfw_app_database_get_next_record(record);
        open_cfw_app_slave_store_u32(
            OPEN_CFW_APP_SLAVE_STATE
                + OPEN_CFW_APP_SLAVE_RESOLUTION_HANDLE_OFFSET,
            record
        );
        if (record == 0U) {
            return;
        }
        key = open_cfw_app_slave_database_get_key(
            record, OPEN_CFW_APP_SLAVE_DATABASE_KEY_IRK,
            (open_cfw_app_slave_u8 *)0
        );
    } while (key == (open_cfw_app_slave_u8 *)0);
    address = open_cfw_cordio_dm_connection_peer_address(
        connection[OPEN_CFW_APP_SLAVE_CONNECTION_ID_OFFSET]
    );
    if (address != (open_cfw_app_slave_u8 *)0) {
        open_cfw_cordio_dm_priv_resolve_address(address, key, parameter);
        OPEN_CFW_APP_SLAVE_STATE[
            OPEN_CFW_APP_SLAVE_RESOLUTION_ACTIVE_OFFSET
        ] = 1U;
    }
}

#if defined(OPEN_CFW_CORDIO_APP_SLAVE_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_SLAVE_RESOLVE_ADDRESS_ONLY)
void open_cfw_app_slave_resolve_address(const void *message)
{
    const volatile open_cfw_app_slave_u8 *event =
        (const volatile open_cfw_app_slave_u8 *)message;
    open_cfw_app_slave_u16 parameter;
    volatile open_cfw_app_slave_u8 *connection;
    if (event == (const volatile open_cfw_app_slave_u8 *)0
        || OPEN_CFW_APP_SLAVE_STATE[
            OPEN_CFW_APP_SLAVE_RESOLUTION_ACTIVE_OFFSET
        ] != 0U) {
        return;
    }
    parameter = open_cfw_app_slave_load_u16(event);
    if (parameter == 0U || parameter > OPEN_CFW_APP_SLAVE_CONNECTION_MAX) {
        return;
    }
    connection = open_cfw_app_slave_connection(
        (open_cfw_app_slave_u8)parameter
    );
    open_cfw_mram_sync_records();
    open_cfw_app_slave_begin_resolution(parameter, connection, 0U);
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_SLAVE_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_SLAVE_RESOLVED_EVENT_ONLY)
void open_cfw_app_slave_resolved_address_event(
    const void *message, volatile open_cfw_app_slave_u8 *connection
)
{
    const volatile open_cfw_app_slave_u8 *event =
        (const volatile open_cfw_app_slave_u8 *)message;
    open_cfw_app_slave_u32 record;
    open_cfw_app_slave_u8 *key;
    open_cfw_app_slave_u8 *csf = (open_cfw_app_slave_u8 *)0;
    open_cfw_app_slave_u8 change_aware = 0U;
    open_cfw_app_slave_u8 connection_id;
    if (event == (const volatile open_cfw_app_slave_u8 *)0
        || connection == (volatile open_cfw_app_slave_u8 *)0
        || OPEN_CFW_APP_SLAVE_STATE[
            OPEN_CFW_APP_SLAVE_RESOLUTION_ACTIVE_OFFSET
        ] == 0U) {
        return;
    }
    connection_id = connection[OPEN_CFW_APP_SLAVE_CONNECTION_ID_OFFSET];
    record = open_cfw_app_slave_load_u32(
        OPEN_CFW_APP_SLAVE_STATE
            + OPEN_CFW_APP_SLAVE_RESOLUTION_HANDLE_OFFSET
    );
    if (event[3] == OPEN_CFW_APP_SLAVE_HCI_SUCCESS) {
        OPEN_CFW_APP_SLAVE_DATABASE_READY = 1U;
        open_cfw_app_slave_store_u32(
            connection + OPEN_CFW_APP_SLAVE_DB_HANDLE_OFFSET, record
        );
        if (record != 0U) {
            open_cfw_cordio_atts_ccc_initialize_table(
                connection_id, open_cfw_app_slave_ccc_table(record)
            );
            open_cfw_app_database_get_csf_record(
                record, &change_aware, &csf
            );
            open_cfw_cordio_atts_csf_connection_open(
                connection_id, change_aware, csf
            );
            if (change_aware == OPEN_CFW_APP_SLAVE_CLIENT_CHANGE_UNAWARE) {
                open_cfw_cordio_gatt_send_service_changed_indication(
                    connection_id, 1U, 0xFFFFU
                );
            }
            key = open_cfw_app_slave_database_get_key(
                record, OPEN_CFW_APP_SLAVE_DATABASE_KEY_CSRK,
                (open_cfw_app_slave_u8 *)0
            );
            if (key != (open_cfw_app_slave_u8 *)0) {
                open_cfw_cordio_atts_set_csrk(connection_id, key, 0U);
                open_cfw_cordio_atts_set_sign_counter(
                    connection_id,
                    open_cfw_app_slave_sign_counter(record)
                );
            }
        }
        if (OPEN_CFW_APP_SLAVE_STATE[
                OPEN_CFW_APP_SLAVE_PENDING_LTK_OFFSET
            ] != 0U) {
            open_cfw_app_slave_security_respond_ltk_internal(connection);
            OPEN_CFW_APP_SLAVE_STATE[
                OPEN_CFW_APP_SLAVE_PENDING_LTK_OFFSET
            ] = 0U;
        }
    } else if (event[3] == OPEN_CFW_APP_SLAVE_HCI_AUTH_FAILURE
               && record != 0U) {
        open_cfw_app_slave_begin_resolution(
            open_cfw_app_slave_load_u16(event), connection, record
        );
        if (OPEN_CFW_APP_SLAVE_STATE[
                OPEN_CFW_APP_SLAVE_RESOLUTION_ACTIVE_OFFSET
            ] != 0U) {
            return;
        }
    }
    OPEN_CFW_APP_SLAVE_STATE[
        OPEN_CFW_APP_SLAVE_RESOLUTION_ACTIVE_OFFSET
    ] = 0U;
    if (open_cfw_app_slave_load_u32(
            connection + OPEN_CFW_APP_SLAVE_DB_HANDLE_OFFSET
        ) == 0U
        && OPEN_CFW_APP_SLAVE_SECURITY_CONFIG
            != (volatile open_cfw_app_slave_u8 *)0
        && OPEN_CFW_APP_SLAVE_SECURITY_CONFIG[4] != 0U) {
        open_cfw_app_slave_security_respond_ltk_internal(connection);
    }
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_SLAVE_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_SLAVE_PROCESS_DM_ONLY)
void open_cfw_app_slave_process_dm_message(void *message)
{
    volatile open_cfw_app_slave_u8 *event =
        (volatile open_cfw_app_slave_u8 *)message;
    volatile open_cfw_app_slave_u8 *connection =
        (volatile open_cfw_app_slave_u8 *)0;
    open_cfw_app_slave_callback_t callback;
    open_cfw_app_slave_u16 parameter;
    if (event == (volatile open_cfw_app_slave_u8 *)0) {
        return;
    }
    parameter = open_cfw_app_slave_load_u16(event);
    if (parameter != 0U && parameter <= OPEN_CFW_APP_SLAVE_CONNECTION_MAX) {
        connection = open_cfw_app_slave_connection(
            (open_cfw_app_slave_u8)parameter
        );
    }
    switch (event[2]) {
    case OPEN_CFW_APP_SLAVE_DM_RESET_COMPLETE:
        open_cfw_app_slave_reset_event_internal(message, connection);
        return;
    case OPEN_CFW_APP_SLAVE_DM_CONNECTION_OPEN:
        if (connection != (volatile open_cfw_app_slave_u8 *)0) {
            open_cfw_app_slave_connection_open_event_internal(
                message, connection
            );
        }
        return;
    case OPEN_CFW_APP_SLAVE_DM_CONNECTION_CLOSE:
        if (connection != (volatile open_cfw_app_slave_u8 *)0) {
            open_cfw_app_slave_connection_close_event_internal(
                message, connection
            );
        }
        return;
    case OPEN_CFW_APP_SLAVE_DM_CONNECTION_UPDATE:
        return;
    case OPEN_CFW_APP_SLAVE_DM_RESOLVED_ADDRESS:
        if (connection != (volatile open_cfw_app_slave_u8 *)0) {
            open_cfw_app_slave_resolved_address_event(message, connection);
        }
        return;
    case OPEN_CFW_APP_SLAVE_DM_REMOTE_CONNECTION_PARAMETER:
        if (connection != (volatile open_cfw_app_slave_u8 *)0) {
            open_cfw_app_slave_remote_parameter_event_internal(
                message, connection
            );
        }
        return;
    case OPEN_CFW_APP_SLAVE_DM_DIAGNOSTIC_41:
    case OPEN_CFW_APP_SLAVE_DM_ADV_SET_STOP:
    case OPEN_CFW_APP_SLAVE_DM_VENDOR_57:
        return;
    case OPEN_CFW_APP_SLAVE_DM_RESET_EXTENSION:
        open_cfw_app_slave_reset_extension_internal(0U);
        open_cfw_app_slave_advertising_reset_internal();
        return;
    default:
        break;
    }
    callback = OPEN_CFW_APP_SLAVE_CALLBACK;
    if (callback != (open_cfw_app_slave_callback_t)0) {
        callback(message);
    }
}
#endif
