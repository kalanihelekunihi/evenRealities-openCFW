/* SPDX-License-Identifier: Apache-2.0 */

/* G2 Cordio master application-framework leaves. */

typedef unsigned char open_cfw_app_master_u8;
typedef unsigned short open_cfw_app_master_u16;
typedef unsigned int open_cfw_app_master_u32;

typedef char open_cfw_app_master_u16_is_two_bytes[
    sizeof(open_cfw_app_master_u16) == 2U ? 1 : -1
];
typedef char open_cfw_app_master_u32_is_four_bytes[
    sizeof(open_cfw_app_master_u32) == 4U ? 1 : -1
];

enum {
    OPEN_CFW_APP_MASTER_CONNECTION_MAX = 3,
    OPEN_CFW_APP_MASTER_CONNECTION_STRIDE = 0x30,
    OPEN_CFW_APP_MASTER_DB_HANDLE_OFFSET = 0,
    OPEN_CFW_APP_MASTER_CONNECTION_ID_OFFSET = 4,
    OPEN_CFW_APP_MASTER_INITIATING_SECURITY_OFFSET = 8,
    OPEN_CFW_APP_MASTER_SCAN_RESULT_STRIDE = 15,
    OPEN_CFW_APP_MASTER_SCAN_INDEX_OFFSET = 0x97,
    OPEN_CFW_APP_MASTER_RESOLUTION_ACTIVE_OFFSET = 0x9C,
    OPEN_CFW_APP_MASTER_SECURITY_INITIATE_OFFSET = 4,
    OPEN_CFW_APP_MASTER_DM_CLIENT_APP = 3,
    OPEN_CFW_APP_MASTER_DATABASE_HANDLE_NONE = 0,
    OPEN_CFW_APP_MASTER_SECURITY_LEVEL_NONE = 0,
    OPEN_CFW_APP_MASTER_HCI_SUCCESS = 0
};

#ifdef OPEN_CFW_CORDIO_APP_MASTER_PRODUCTION
#define OPEN_CFW_APP_MASTER_STATE \
    ((volatile open_cfw_app_master_u8 *)0x20071670U)
#define OPEN_CFW_APP_MASTER_CONNECTION_STATE \
    ((volatile open_cfw_app_master_u8 *)0x200717B0U)
#define OPEN_CFW_APP_MASTER_SECURITY_CONFIG \
    (*(volatile open_cfw_app_master_u8 * volatile *)0x20074358U)
#else
extern volatile open_cfw_app_master_u8 open_cfw_app_master_runtime_state[0xA0];
extern volatile open_cfw_app_master_u8
    open_cfw_app_master_connection_state[
        OPEN_CFW_APP_MASTER_CONNECTION_MAX
        * OPEN_CFW_APP_MASTER_CONNECTION_STRIDE
    ];
extern volatile open_cfw_app_master_u8 *open_cfw_app_master_security_config;
#define OPEN_CFW_APP_MASTER_STATE open_cfw_app_master_runtime_state
#define OPEN_CFW_APP_MASTER_CONNECTION_STATE \
    open_cfw_app_master_connection_state
#define OPEN_CFW_APP_MASTER_SECURITY_CONFIG \
    open_cfw_app_master_security_config
#endif

open_cfw_app_master_u8 open_cfw_cordio_dm_connection_open(
    open_cfw_app_master_u8, open_cfw_app_master_u8,
    open_cfw_app_master_u8, open_cfw_app_master_u8 *
);
int open_cfw_app_database_record_in_use(open_cfw_app_master_u32);
open_cfw_app_master_u32 open_cfw_app_database_find_by_address(
    open_cfw_app_master_u8, open_cfw_app_master_u8 *
);
int open_cfw_mram_handle_resolved_address(
    const volatile open_cfw_app_master_u8 *, open_cfw_app_master_u16
);
open_cfw_app_master_u8 open_cfw_cordio_dm_connection_security_level(
    open_cfw_app_master_u8
);
void open_cfw_app_master_initiate_security_internal(
    open_cfw_app_master_u8, open_cfw_app_master_u8,
    volatile open_cfw_app_master_u8 *
);

void open_cfw_app_master_scan_stop_event(const void *);
void open_cfw_app_master_resolved_address_event(const void *);
open_cfw_app_master_u8 open_cfw_app_master_connection_open(
    open_cfw_app_master_u8, open_cfw_app_master_u8,
    open_cfw_app_master_u8 *, open_cfw_app_master_u32
);
void open_cfw_app_master_security_request(open_cfw_app_master_u8);

#if !defined(OPEN_CFW_CORDIO_APP_MASTER_SCAN_STOP_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_MASTER_RESOLVED_ADDRESS_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_MASTER_CONNECTION_OPEN_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_MASTER_SECURITY_REQUEST_ONLY)
#define OPEN_CFW_CORDIO_APP_MASTER_BUILD_ALL 1
#endif

static __attribute__((always_inline, unused)) inline open_cfw_app_master_u16
open_cfw_app_master_load_u16(const volatile open_cfw_app_master_u8 *value)
{
    return (open_cfw_app_master_u16)value[0]
        | (open_cfw_app_master_u16)(
            (open_cfw_app_master_u16)value[1] << 8U
        );
}

static __attribute__((always_inline, unused)) inline void
open_cfw_app_master_store_u32(
    volatile open_cfw_app_master_u8 *value, open_cfw_app_master_u32 data
)
{
    value[0] = (open_cfw_app_master_u8)data;
    value[1] = (open_cfw_app_master_u8)(data >> 8U);
    value[2] = (open_cfw_app_master_u8)(data >> 16U);
    value[3] = (open_cfw_app_master_u8)(data >> 24U);
}

static __attribute__((always_inline, unused)) inline volatile open_cfw_app_master_u8 *
open_cfw_app_master_connection(open_cfw_app_master_u8 connection_id)
{
    return OPEN_CFW_APP_MASTER_CONNECTION_STATE
        + (open_cfw_app_master_u32)(connection_id - 1U)
            * OPEN_CFW_APP_MASTER_CONNECTION_STRIDE;
}

#if defined(OPEN_CFW_CORDIO_APP_MASTER_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_MASTER_SCAN_STOP_ONLY)
void open_cfw_app_master_scan_stop_event(const void *message)
{
    /* The G2 body contains diagnostics only; scan state is owned by DM. */
    (void)message;
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_MASTER_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_MASTER_RESOLVED_ADDRESS_ONLY)
void open_cfw_app_master_resolved_address_event(const void *message)
{
    const volatile open_cfw_app_master_u8 *event =
        (const volatile open_cfw_app_master_u8 *)message;
    open_cfw_app_master_u8 index;
    if (event == (const volatile open_cfw_app_master_u8 *)0
        || OPEN_CFW_APP_MASTER_STATE[
            OPEN_CFW_APP_MASTER_RESOLUTION_ACTIVE_OFFSET
        ] == 0U) {
        return;
    }
    index = OPEN_CFW_APP_MASTER_STATE[
        OPEN_CFW_APP_MASTER_SCAN_INDEX_OFFSET
    ];
    if (event[3] == OPEN_CFW_APP_MASTER_HCI_SUCCESS) {
        (void)open_cfw_mram_handle_resolved_address(
            OPEN_CFW_APP_MASTER_STATE
                + (open_cfw_app_master_u32)index
                    * OPEN_CFW_APP_MASTER_SCAN_RESULT_STRIDE,
            open_cfw_app_master_load_u16(event)
        );
    }
    OPEN_CFW_APP_MASTER_STATE[
        OPEN_CFW_APP_MASTER_RESOLUTION_ACTIVE_OFFSET
    ] = 0U;
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_MASTER_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_MASTER_CONNECTION_OPEN_ONLY)
open_cfw_app_master_u8 open_cfw_app_master_connection_open(
    open_cfw_app_master_u8 initiator_phys,
    open_cfw_app_master_u8 address_type,
    open_cfw_app_master_u8 *address,
    open_cfw_app_master_u32 database_handle
)
{
    open_cfw_app_master_u8 connection_id;
    volatile open_cfw_app_master_u8 *connection;
    if (address == (open_cfw_app_master_u8 *)0) {
        return 0U;
    }
    connection_id = open_cfw_cordio_dm_connection_open(
        OPEN_CFW_APP_MASTER_DM_CLIENT_APP, initiator_phys,
        address_type, address
    );
    if (connection_id == 0U
        || connection_id > OPEN_CFW_APP_MASTER_CONNECTION_MAX) {
        return connection_id;
    }
    connection = open_cfw_app_master_connection(connection_id);
    connection[OPEN_CFW_APP_MASTER_CONNECTION_ID_OFFSET] = connection_id;
    if (database_handle == OPEN_CFW_APP_MASTER_DATABASE_HANDLE_NONE
        || !open_cfw_app_database_record_in_use(database_handle)) {
        database_handle = open_cfw_app_database_find_by_address(
            address_type, address
        );
    }
    open_cfw_app_master_store_u32(
        connection + OPEN_CFW_APP_MASTER_DB_HANDLE_OFFSET,
        database_handle
    );
    return connection_id;
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_MASTER_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_MASTER_SECURITY_REQUEST_ONLY)
void open_cfw_app_master_security_request(
    open_cfw_app_master_u8 connection_id
)
{
    volatile open_cfw_app_master_u8 *connection;
    volatile open_cfw_app_master_u8 *config =
        OPEN_CFW_APP_MASTER_SECURITY_CONFIG;
    if (connection_id == 0U
        || connection_id > OPEN_CFW_APP_MASTER_CONNECTION_MAX
        || config == (volatile open_cfw_app_master_u8 *)0) {
        return;
    }
    connection = open_cfw_app_master_connection(connection_id);
    if (config[OPEN_CFW_APP_MASTER_SECURITY_INITIATE_OFFSET] == 0U
        && connection[OPEN_CFW_APP_MASTER_INITIATING_SECURITY_OFFSET] == 0U
        && open_cfw_cordio_dm_connection_security_level(connection_id)
            == OPEN_CFW_APP_MASTER_SECURITY_LEVEL_NONE) {
        open_cfw_app_master_initiate_security_internal(
            connection_id, 1U, connection
        );
    }
}
#endif
