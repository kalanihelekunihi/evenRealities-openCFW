/* SPDX-License-Identifier: Apache-2.0 */

/*
 * Cordio application-framework UI, connection, and server core for G2.
 *
 * The public behavior comes from the authenticated AmbiqSuite/Packetcraft
 * application framework.  The state addresses, connection-control-block
 * layout, delayed connection-update policy, and UI event values below were
 * recovered from the authenticated G2 2.2.6.10 image.  Every public entry is
 * selectable as an isolated overlay leaf.
 */

typedef unsigned char open_cfw_app_core_u8;
typedef unsigned short open_cfw_app_core_u16;
typedef unsigned int open_cfw_app_core_u32;

typedef char open_cfw_app_core_u16_is_two_bytes[
    sizeof(open_cfw_app_core_u16) == 2U ? 1 : -1
];
typedef char open_cfw_app_core_u32_is_four_bytes[
    sizeof(open_cfw_app_core_u32) == 4U ? 1 : -1
];

typedef void (*open_cfw_app_ui_callback_t)(
    open_cfw_app_core_u8, open_cfw_app_core_u32
);

typedef struct {
    open_cfw_app_core_u16 parameter;
    open_cfw_app_core_u8 event;
    open_cfw_app_core_u8 status;
    open_cfw_app_core_u8 *value;
} open_cfw_app_server_event_t;

enum {
    OPEN_CFW_APP_CONNECTION_MAX = 3,
    OPEN_CFW_APP_CONNECTION_CB_STRIDE = 0x30,
    OPEN_CFW_APP_CONNECTION_DB_HANDLE_OFFSET = 0,
    OPEN_CFW_APP_CONNECTION_BONDED_OFFSET = 5,
    OPEN_CFW_APP_CONNECTION_TIMER_OFFSET = 0x20,
    OPEN_CFW_APP_TIMER_PARAMETER_OFFSET = 8,
    OPEN_CFW_APP_TIMER_EVENT_OFFSET = 10,
    OPEN_CFW_APP_TIMER_HANDLER_OFFSET = 12,
    OPEN_CFW_APP_CONNECTION_UPDATE_EVENT = 2,
    OPEN_CFW_APP_CONNECTION_UPDATE_DELAY_MS = 30,
    OPEN_CFW_APP_UI_PASSKEY_EVENT = 15,
    OPEN_CFW_APP_UI_CONFIRM_EVENT = 16,
    OPEN_CFW_APP_DATABASE_HASH_LENGTH = 16,
    OPEN_CFW_APP_DATABASE_HANDLE_NONE = 0,
    OPEN_CFW_APP_DATABASE_KEY_IRK = 4,
    OPEN_CFW_APP_CLIENT_CHANGE_UNAWARE = 3,
    OPEN_CFW_APP_ATT_HANDLE_START = 1,
    OPEN_CFW_APP_ATT_HANDLE_MAX = 0xFFFF
};

#ifdef OPEN_CFW_CORDIO_APP_CORE_PRODUCTION
#define OPEN_CFW_APP_CONNECTION_STATE \
    ((volatile open_cfw_app_core_u8 *)0x200717B0U)
#define OPEN_CFW_APP_HANDLER_ID \
    (*(volatile open_cfw_app_core_u8 *)0x20074F92U)
#define OPEN_CFW_APP_UI_CALLBACK \
    (*(open_cfw_app_ui_callback_t volatile *)0x20073F64U)
#else
extern volatile open_cfw_app_core_u8
    open_cfw_app_core_connection_state[
        OPEN_CFW_APP_CONNECTION_MAX * OPEN_CFW_APP_CONNECTION_CB_STRIDE
    ];
extern volatile open_cfw_app_core_u8 open_cfw_app_core_handler_id;
extern open_cfw_app_ui_callback_t open_cfw_app_core_ui_callback;
#define OPEN_CFW_APP_CONNECTION_STATE open_cfw_app_core_connection_state
#define OPEN_CFW_APP_HANDLER_ID open_cfw_app_core_handler_id
#define OPEN_CFW_APP_UI_CALLBACK open_cfw_app_core_ui_callback
#endif

int open_cfw_cordio_hci_ll_privacy_supported(void);
open_cfw_app_core_u8 *open_cfw_app_database_get_key(
    open_cfw_app_core_u32, open_cfw_app_core_u8, open_cfw_app_core_u8 *
);
open_cfw_app_core_u8 *open_cfw_cordio_dm_security_get_local_irk(void);
void open_cfw_cordio_dm_priv_add_device_to_resolving_list(
    open_cfw_app_core_u8, open_cfw_app_core_u8 *, open_cfw_app_core_u8 *,
    open_cfw_app_core_u8 *, open_cfw_app_core_u8, open_cfw_app_core_u16
);
void open_cfw_cordio_wsf_timer_start_ms(void *, open_cfw_app_core_u32);
open_cfw_app_core_u8 *open_cfw_app_database_hash_get(void);
void open_cfw_app_database_hash_set(open_cfw_app_core_u8 *);
void open_cfw_app_database_set_clients_change_aware_state(
    open_cfw_app_core_u32, open_cfw_app_core_u8
);
void open_cfw_cordio_atts_set_clients_change_awareness_state(
    open_cfw_app_core_u8, open_cfw_app_core_u8
);
void open_cfw_cordio_gatt_send_service_changed_indication(
    open_cfw_app_core_u8, open_cfw_app_core_u16, open_cfw_app_core_u16
);

void open_cfw_app_ui_action(open_cfw_app_core_u8);
void open_cfw_app_ui_display_passkey(open_cfw_app_core_u32);
void open_cfw_app_ui_display_confirm_value(open_cfw_app_core_u32);
int open_cfw_app_check_bonded(open_cfw_app_core_u8);
void open_cfw_app_add_device_to_resolving_list(
    const void *, open_cfw_app_core_u8
);
void open_cfw_app_connection_update_timer_start(open_cfw_app_core_u8);
void open_cfw_app_server_handle_database_hash_update(
    open_cfw_app_server_event_t *
);

#if !defined(OPEN_CFW_CORDIO_APP_CORE_UI_ACTION_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_CORE_UI_PASSKEY_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_CORE_UI_CONFIRM_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_CORE_CHECK_BONDED_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_CORE_ADD_RESOLVING_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_CORE_UPDATE_TIMER_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_CORE_SERVER_HASH_ONLY)
#define OPEN_CFW_CORDIO_APP_CORE_BUILD_ALL 1
#endif

static __attribute__((always_inline, unused)) inline open_cfw_app_core_u16
open_cfw_app_core_load_u16(const volatile open_cfw_app_core_u8 *value)
{
    return (open_cfw_app_core_u16)value[0]
        | (open_cfw_app_core_u16)(
            (open_cfw_app_core_u16)value[1] << 8U
        );
}

static __attribute__((always_inline, unused)) inline open_cfw_app_core_u32
open_cfw_app_core_load_u32(const volatile open_cfw_app_core_u8 *value)
{
    return (open_cfw_app_core_u32)value[0]
        | ((open_cfw_app_core_u32)value[1] << 8U)
        | ((open_cfw_app_core_u32)value[2] << 16U)
        | ((open_cfw_app_core_u32)value[3] << 24U);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_app_core_store_u16(
    volatile open_cfw_app_core_u8 *value, open_cfw_app_core_u16 data
)
{
    value[0] = (open_cfw_app_core_u8)data;
    value[1] = (open_cfw_app_core_u8)(data >> 8U);
}

static __attribute__((always_inline, unused)) inline volatile open_cfw_app_core_u8 *
open_cfw_app_core_connection(open_cfw_app_core_u8 connection_id)
{
    return OPEN_CFW_APP_CONNECTION_STATE
        + ((open_cfw_app_core_u32)(connection_id - 1U)
            * OPEN_CFW_APP_CONNECTION_CB_STRIDE);
}

static __attribute__((always_inline, unused)) inline int
open_cfw_app_core_connection_id_valid(open_cfw_app_core_u8 connection_id)
{
    return connection_id != 0U
        && connection_id <= OPEN_CFW_APP_CONNECTION_MAX;
}

static __attribute__((always_inline, unused)) inline void
open_cfw_app_core_ui_notify(
    open_cfw_app_core_u8 event, open_cfw_app_core_u32 value
)
{
    open_cfw_app_ui_callback_t callback = OPEN_CFW_APP_UI_CALLBACK;
    if (callback != (open_cfw_app_ui_callback_t)0) {
        callback(event, value);
    }
}

#if defined(OPEN_CFW_CORDIO_APP_CORE_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_CORE_UI_ACTION_ONLY)
void open_cfw_app_ui_action(open_cfw_app_core_u8 event)
{
    open_cfw_app_core_ui_notify(event, 0U);
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_CORE_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_CORE_UI_PASSKEY_ONLY)
void open_cfw_app_ui_display_passkey(open_cfw_app_core_u32 passkey)
{
    open_cfw_app_core_ui_notify(OPEN_CFW_APP_UI_PASSKEY_EVENT, passkey);
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_CORE_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_CORE_UI_CONFIRM_ONLY)
void open_cfw_app_ui_display_confirm_value(open_cfw_app_core_u32 confirm)
{
    open_cfw_app_core_ui_notify(OPEN_CFW_APP_UI_CONFIRM_EVENT, confirm);
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_CORE_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_CORE_CHECK_BONDED_ONLY)
int open_cfw_app_check_bonded(open_cfw_app_core_u8 connection_id)
{
    if (!open_cfw_app_core_connection_id_valid(connection_id)) {
        return 0;
    }
    return open_cfw_app_core_connection(connection_id)[
        OPEN_CFW_APP_CONNECTION_BONDED_OFFSET
    ] != 0U;
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_CORE_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_CORE_ADD_RESOLVING_ONLY)
void open_cfw_app_add_device_to_resolving_list(
    const void *message, open_cfw_app_core_u8 connection_id
)
{
    volatile open_cfw_app_core_u8 *connection;
    open_cfw_app_core_u8 *peer_key;
    open_cfw_app_core_u8 *local_irk;
    open_cfw_app_core_u32 database_handle;
    open_cfw_app_core_u16 parameter;

    if (message == (const void *)0
        || !open_cfw_app_core_connection_id_valid(connection_id)
        || !open_cfw_cordio_hci_ll_privacy_supported()) {
        return;
    }
    connection = open_cfw_app_core_connection(connection_id);
    database_handle = open_cfw_app_core_load_u32(
        connection + OPEN_CFW_APP_CONNECTION_DB_HANDLE_OFFSET
    );
    if (database_handle == OPEN_CFW_APP_DATABASE_HANDLE_NONE) {
        return;
    }
    peer_key = open_cfw_app_database_get_key(
        database_handle, OPEN_CFW_APP_DATABASE_KEY_IRK,
        (open_cfw_app_core_u8 *)0
    );
    if (peer_key == (open_cfw_app_core_u8 *)0) {
        return;
    }
    local_irk = open_cfw_cordio_dm_security_get_local_irk();
    if (local_irk == (open_cfw_app_core_u8 *)0) {
        return;
    }
    parameter = open_cfw_app_core_load_u16(
        (const volatile open_cfw_app_core_u8 *)message
    );
    open_cfw_cordio_dm_priv_add_device_to_resolving_list(
        peer_key[0x16U], peer_key + 0x10U, peer_key, local_irk, 1U,
        parameter
    );
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_CORE_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_CORE_UPDATE_TIMER_ONLY)
void open_cfw_app_connection_update_timer_start(
    open_cfw_app_core_u8 connection_id
)
{
    volatile open_cfw_app_core_u8 *timer;
    if (!open_cfw_app_core_connection_id_valid(connection_id)) {
        return;
    }
    timer = open_cfw_app_core_connection(connection_id)
        + OPEN_CFW_APP_CONNECTION_TIMER_OFFSET;
    open_cfw_app_core_store_u16(
        timer + OPEN_CFW_APP_TIMER_PARAMETER_OFFSET, connection_id
    );
    timer[OPEN_CFW_APP_TIMER_EVENT_OFFSET] =
        OPEN_CFW_APP_CONNECTION_UPDATE_EVENT;
    timer[OPEN_CFW_APP_TIMER_HANDLER_OFFSET] = OPEN_CFW_APP_HANDLER_ID;
    open_cfw_cordio_wsf_timer_start_ms(
        (void *)timer, OPEN_CFW_APP_CONNECTION_UPDATE_DELAY_MS
    );
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_CORE_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_CORE_SERVER_HASH_ONLY)
void open_cfw_app_server_handle_database_hash_update(
    open_cfw_app_server_event_t *message
)
{
    open_cfw_app_core_u8 *current_hash;
    open_cfw_app_core_u8 *new_hash;
    open_cfw_app_core_u32 index;
    int different = 0;

    if (message == (open_cfw_app_server_event_t *)0
        || message->value == (open_cfw_app_core_u8 *)0) {
        return;
    }
    new_hash = message->value;
    current_hash = open_cfw_app_database_hash_get();
    if (current_hash != (open_cfw_app_core_u8 *)0) {
        for (index = 0U; index < OPEN_CFW_APP_DATABASE_HASH_LENGTH; ++index) {
            if (current_hash[index] != new_hash[index]) {
                different = 1;
                break;
            }
        }
        if (!different) {
            return;
        }
    }
    open_cfw_app_database_hash_set(new_hash);
    open_cfw_app_database_set_clients_change_aware_state(
        OPEN_CFW_APP_DATABASE_HANDLE_NONE,
        OPEN_CFW_APP_CLIENT_CHANGE_UNAWARE
    );
    open_cfw_cordio_atts_set_clients_change_awareness_state(
        0U, OPEN_CFW_APP_CLIENT_CHANGE_UNAWARE
    );
    open_cfw_cordio_gatt_send_service_changed_indication(
        0U, OPEN_CFW_APP_ATT_HANDLE_START, OPEN_CFW_APP_ATT_HANDLE_MAX
    );
}
#endif
