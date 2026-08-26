/* SPDX-License-Identifier: Apache-2.0 */

/*
 * Cordio application-framework legacy master/slave adapter for G2.
 *
 * The behavior is derived from the authenticated AmbiqSuite 2.5.1 sources,
 * with the G2 advertising retry extension recovered from the stock image.
 * The state/configuration locations and callback values below are part of the
 * linked G2 ABI.  Each entry can be built as an isolated overlay leaf.
 */

typedef unsigned char open_cfw_app_u8;
typedef unsigned short open_cfw_app_u16;
typedef unsigned int open_cfw_app_u32;

typedef char open_cfw_app_u16_is_two_bytes[
    sizeof(open_cfw_app_u16) == 2U ? 1 : -1
];
typedef char open_cfw_app_u32_is_four_bytes[
    sizeof(open_cfw_app_u32) == 4U ? 1 : -1
];

enum {
    OPEN_CFW_APP_ADV_STATE_1 = 0,
    OPEN_CFW_APP_ADV_STOPPED = 3,
    OPEN_CFW_APP_SCAN_MODE_LEGACY = 0,
    OPEN_CFW_APP_SCAN_MODE_NONE = 0xFF,
    OPEN_CFW_APP_DM_ADV_STOP_IND = 0x22,
    OPEN_CFW_APP_DM_CONN_OPEN_IND = 0x27,
    OPEN_CFW_APP_DM_CONN_CLOSE_IND = 0x28,
    OPEN_CFW_APP_DM_ADV_SET_STOP_IND = 0x48,
    OPEN_CFW_APP_HCI_SUCCESS = 0,
    OPEN_CFW_APP_PHY_LE_1M = 1,
    OPEN_CFW_APP_ADV_DATA_MAX = 31,
    OPEN_CFW_APP_STOCK_LEGACY_STOP_CALLBACK = 0x004B2AFF,
    OPEN_CFW_APP_STOCK_LEGACY_RESTART_CALLBACK = 0x004B2B91
};

#ifdef OPEN_CFW_CORDIO_APP_LEGACY_PRODUCTION
#define OPEN_CFW_APP_MASTER_STATE ((volatile open_cfw_app_u8 *)0x20071670U)
#define OPEN_CFW_APP_SLAVE_STATE ((volatile open_cfw_app_u8 *)0x200719C8U)
#define OPEN_CFW_APP_ADV_CONFIG \
    (*(volatile open_cfw_app_u8 * volatile *)0x2007434CU)
#define OPEN_CFW_APP_MASTER_CONFIG \
    (*(volatile open_cfw_app_u8 * volatile *)0x20074354U)
#define OPEN_CFW_APP_RETRY_FLAG (*(volatile open_cfw_app_u8 *)0x20074F94U)
#define OPEN_CFW_APP_RETRY_TIMER ((volatile open_cfw_app_u8 *)0x20073DF4U)
#define OPEN_CFW_APP_HANDLER_ID (*(volatile open_cfw_app_u8 *)0x20074F92U)
#else
extern volatile open_cfw_app_u8 open_cfw_app_master_state[0xA0];
extern volatile open_cfw_app_u8 open_cfw_app_slave_state[0x80];
extern volatile open_cfw_app_u8 *open_cfw_app_adv_config;
extern volatile open_cfw_app_u8 *open_cfw_app_master_config;
extern volatile open_cfw_app_u8 open_cfw_app_retry_flag;
extern volatile open_cfw_app_u8 open_cfw_app_retry_timer[16];
extern volatile open_cfw_app_u8 open_cfw_app_handler_id;
#define OPEN_CFW_APP_MASTER_STATE open_cfw_app_master_state
#define OPEN_CFW_APP_SLAVE_STATE open_cfw_app_slave_state
#define OPEN_CFW_APP_ADV_CONFIG open_cfw_app_adv_config
#define OPEN_CFW_APP_MASTER_CONFIG open_cfw_app_master_config
#define OPEN_CFW_APP_RETRY_FLAG open_cfw_app_retry_flag
#define OPEN_CFW_APP_RETRY_TIMER open_cfw_app_retry_timer
#define OPEN_CFW_APP_HANDLER_ID open_cfw_app_handler_id
#endif

void open_cfw_cordio_dm_scan_set_interval(
    open_cfw_app_u8, open_cfw_app_u16 *, open_cfw_app_u16 *
);
void open_cfw_cordio_dm_scan_start(
    open_cfw_app_u8, open_cfw_app_u8, const open_cfw_app_u8 *,
    open_cfw_app_u8, open_cfw_app_u16, open_cfw_app_u16
);
void open_cfw_cordio_dm_scan_stop(void);
open_cfw_app_u8 open_cfw_app_connection_open_internal(
    open_cfw_app_u8, open_cfw_app_u8, open_cfw_app_u8 *, void *
);
open_cfw_app_u8 open_cfw_cordio_dm_advertising_extended_mode(open_cfw_app_u8);
void open_cfw_app_advertising_start_internal(
    open_cfw_app_u8, open_cfw_app_u8 *, open_cfw_app_u16 *,
    open_cfw_app_u16 *, open_cfw_app_u8 *, open_cfw_app_u8
);
void open_cfw_app_slave_advertising_start_internal(
    open_cfw_app_u8, open_cfw_app_u8 *, open_cfw_app_u16 *,
    open_cfw_app_u16 *, open_cfw_app_u8 *, open_cfw_app_u8,
    open_cfw_app_u8
);
void open_cfw_app_advertising_stop_internal(
    open_cfw_app_u8, open_cfw_app_u8 *
);
void open_cfw_app_advertising_set_data_internal(
    open_cfw_app_u8, open_cfw_app_u8, open_cfw_app_u16,
    open_cfw_app_u8 *, open_cfw_app_u16, open_cfw_app_u16
);
void open_cfw_app_advertising_set_type_internal(
    open_cfw_app_u8, open_cfw_app_u8, open_cfw_app_u16,
    open_cfw_app_u16, open_cfw_app_u8, open_cfw_app_u8
);
void open_cfw_cordio_wsf_timer_start_ms(void *, open_cfw_app_u32);
void open_cfw_cordio_wsf_timer_stop(void *);

int open_cfw_app_master_scan_mode(void);
void open_cfw_app_scan_start(
    open_cfw_app_u8, open_cfw_app_u8, open_cfw_app_u16
);
void open_cfw_app_scan_stop(void);
open_cfw_app_u8 open_cfw_app_connection_open(
    open_cfw_app_u8, open_cfw_app_u8 *, void *
);
void open_cfw_app_slave_legacy_advertising_start(void);
void open_cfw_app_slave_legacy_advertising_type_changed(void *);
void open_cfw_app_slave_legacy_advertising_next_state(void *);
void open_cfw_app_slave_legacy_advertising_stop(void *);
void open_cfw_app_slave_legacy_advertising_restart(void *);
int open_cfw_app_slave_legacy_advertising_mode(void);
void open_cfw_app_advertising_set_data(
    open_cfw_app_u8, open_cfw_app_u8, open_cfw_app_u8 *
);
void open_cfw_app_advertising_start(open_cfw_app_u8);
void open_cfw_app_advertising_stop(void);
void open_cfw_app_advertising_set_type(open_cfw_app_u8);

#if !defined(OPEN_CFW_CORDIO_APP_LEGACY_MASTER_MODE_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_LEGACY_SCAN_START_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_LEGACY_SCAN_STOP_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_LEGACY_CONNECTION_OPEN_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_START_INTERNAL_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_TYPE_CHANGED_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_NEXT_STATE_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_STOP_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_RESTART_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_MODE_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_SET_DATA_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_START_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_STOP_ONLY) && \
    !defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_SET_TYPE_ONLY)
#define OPEN_CFW_CORDIO_APP_LEGACY_BUILD_ALL 1
#endif

static __attribute__((always_inline, unused)) inline open_cfw_app_u16
open_cfw_app_load_u16(const volatile open_cfw_app_u8 *value)
{
    return (open_cfw_app_u16)value[0]
        | (open_cfw_app_u16)((open_cfw_app_u16)value[1] << 8U);
}

static __attribute__((always_inline, unused)) inline open_cfw_app_u32
open_cfw_app_load_u32(const volatile open_cfw_app_u8 *value)
{
    return (open_cfw_app_u32)value[0]
        | ((open_cfw_app_u32)value[1] << 8U)
        | ((open_cfw_app_u32)value[2] << 16U)
        | ((open_cfw_app_u32)value[3] << 24U);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_app_store_u16(volatile open_cfw_app_u8 *value, open_cfw_app_u16 data)
{
    value[0] = (open_cfw_app_u8)data;
    value[1] = (open_cfw_app_u8)(data >> 8U);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_app_store_u32(volatile open_cfw_app_u8 *value, open_cfw_app_u32 data)
{
    value[0] = (open_cfw_app_u8)data;
    value[1] = (open_cfw_app_u8)(data >> 8U);
    value[2] = (open_cfw_app_u8)(data >> 16U);
    value[3] = (open_cfw_app_u8)(data >> 24U);
}

static __attribute__((always_inline, unused)) inline int
open_cfw_app_extended_advertising(void)
{
    return open_cfw_cordio_dm_advertising_extended_mode(0U) != 0U;
}

static __attribute__((always_inline, unused)) inline void
open_cfw_app_schedule_legacy_retry(open_cfw_app_u32 milliseconds)
{
    if (OPEN_CFW_APP_RETRY_FLAG == 0U) {
        OPEN_CFW_APP_RETRY_FLAG = 1U;
        open_cfw_app_store_u16(OPEN_CFW_APP_RETRY_TIMER + 8U, 0U);
        OPEN_CFW_APP_RETRY_TIMER[10] = OPEN_CFW_APP_DM_ADV_STOP_IND;
        OPEN_CFW_APP_RETRY_TIMER[12] = OPEN_CFW_APP_HANDLER_ID;
        open_cfw_cordio_wsf_timer_start_ms(
            (void *)OPEN_CFW_APP_RETRY_TIMER, milliseconds
        );
    }
}

#if defined(OPEN_CFW_CORDIO_APP_LEGACY_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_LEGACY_MASTER_MODE_ONLY)
int open_cfw_app_master_scan_mode(void)
{
    open_cfw_app_u8 mode = OPEN_CFW_APP_MASTER_STATE[0x9DU];
    if (mode == OPEN_CFW_APP_SCAN_MODE_NONE) {
        OPEN_CFW_APP_MASTER_STATE[0x9DU] = OPEN_CFW_APP_SCAN_MODE_LEGACY;
        return 1;
    }
    return mode == OPEN_CFW_APP_SCAN_MODE_LEGACY;
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_LEGACY_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_LEGACY_SCAN_START_ONLY)
void open_cfw_app_scan_start(
    open_cfw_app_u8 mode, open_cfw_app_u8 scan_type,
    open_cfw_app_u16 duration
)
{
    volatile open_cfw_app_u8 *config;
    open_cfw_app_u8 type = scan_type;
    if (!open_cfw_app_master_scan_mode()) {
        return;
    }
    config = OPEN_CFW_APP_MASTER_CONFIG;
    if (config == (volatile open_cfw_app_u8 *)0) {
        return;
    }
    open_cfw_cordio_dm_scan_set_interval(
        OPEN_CFW_APP_PHY_LE_1M,
        (open_cfw_app_u16 *)(void *)config,
        (open_cfw_app_u16 *)(void *)(config + 2U)
    );
    open_cfw_cordio_dm_scan_start(
        OPEN_CFW_APP_PHY_LE_1M, mode, &type, 1U, duration, 0U
    );
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_LEGACY_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_LEGACY_SCAN_STOP_ONLY)
void open_cfw_app_scan_stop(void)
{
    if (open_cfw_app_master_scan_mode()) {
        OPEN_CFW_APP_MASTER_STATE[0x9CU] = 0U;
        open_cfw_cordio_dm_scan_stop();
    }
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_LEGACY_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_LEGACY_CONNECTION_OPEN_ONLY)
open_cfw_app_u8 open_cfw_app_connection_open(
    open_cfw_app_u8 address_type, open_cfw_app_u8 *address,
    void *database_handle
)
{
    if (!open_cfw_app_master_scan_mode()) {
        return 0U;
    }
    return open_cfw_app_connection_open_internal(
        OPEN_CFW_APP_PHY_LE_1M, address_type, address, database_handle
    );
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_LEGACY_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_START_INTERNAL_ONLY)
void open_cfw_app_slave_legacy_advertising_start(void)
{
    volatile open_cfw_app_u8 *config = OPEN_CFW_APP_ADV_CONFIG;
    open_cfw_app_u8 state = OPEN_CFW_APP_SLAVE_STATE[0x57U];
    open_cfw_app_u16 interval;
    open_cfw_app_u8 handle = 0U;
    open_cfw_app_u8 maximum_events = 0U;
    if (config == (volatile open_cfw_app_u8 *)0 || state >= 3U) {
        OPEN_CFW_APP_SLAVE_STATE[0x57U] = OPEN_CFW_APP_ADV_STOPPED;
        return;
    }
    interval = open_cfw_app_load_u16(config + 6U + (open_cfw_app_u32)state * 2U);
    if (interval == 0U) {
        OPEN_CFW_APP_SLAVE_STATE[0x57U] = OPEN_CFW_APP_ADV_STOPPED;
        return;
    }
    if (open_cfw_app_extended_advertising()) {
        open_cfw_app_schedule_legacy_retry(200U);
        return;
    }
    open_cfw_app_advertising_start_internal(
        1U, &handle, &interval,
        (open_cfw_app_u16 *)(void *)(config + (open_cfw_app_u32)state * 2U),
        &maximum_events, 1U
    );
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_LEGACY_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_TYPE_CHANGED_ONLY)
void open_cfw_app_slave_legacy_advertising_type_changed(void *message)
{
    (void)message;
    OPEN_CFW_APP_SLAVE_STATE[0x5BU] = 0U;
    OPEN_CFW_APP_SLAVE_STATE[0x57U] = OPEN_CFW_APP_ADV_STATE_1;
    open_cfw_app_slave_legacy_advertising_start();
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_LEGACY_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_NEXT_STATE_ONLY)
void open_cfw_app_slave_legacy_advertising_next_state(void *message)
{
    open_cfw_app_u8 state;
    (void)message;
    state = (open_cfw_app_u8)(OPEN_CFW_APP_SLAVE_STATE[0x57U] + 1U);
    OPEN_CFW_APP_SLAVE_STATE[0x57U] = state;
    if (state < OPEN_CFW_APP_ADV_STOPPED) {
        if (open_cfw_app_extended_advertising()) {
            open_cfw_app_schedule_legacy_retry(200U);
        } else {
            open_cfw_app_slave_legacy_advertising_start();
        }
    }
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_LEGACY_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_STOP_CALLBACK_ONLY)
void open_cfw_app_slave_legacy_advertising_stop(void *message)
{
    const open_cfw_app_u8 *event = (const open_cfw_app_u8 *)message;
    open_cfw_app_u8 event_id;
    if (event == (const open_cfw_app_u8 *)0) {
        return;
    }
    event_id = event[2];
    if (event_id == OPEN_CFW_APP_DM_ADV_SET_STOP_IND
        && event[4] == OPEN_CFW_APP_HCI_SUCCESS) {
        return;
    }
    if (event_id == OPEN_CFW_APP_DM_ADV_STOP_IND) {
        int extended = open_cfw_app_extended_advertising();
        if (OPEN_CFW_APP_RETRY_FLAG != 0U) {
            if (extended) {
                open_cfw_cordio_wsf_timer_start_ms(
                    (void *)OPEN_CFW_APP_RETRY_TIMER, 100U
                );
                return;
            }
            OPEN_CFW_APP_RETRY_FLAG = 0U;
            open_cfw_cordio_wsf_timer_stop((void *)OPEN_CFW_APP_RETRY_TIMER);
        } else if (extended) {
            open_cfw_app_schedule_legacy_retry(100U);
            return;
        }
    }
    if (OPEN_CFW_APP_SLAVE_STATE[0x5BU] != 0U) {
        open_cfw_app_slave_legacy_advertising_type_changed(message);
    } else {
        open_cfw_app_slave_legacy_advertising_next_state(message);
    }
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_LEGACY_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_RESTART_CALLBACK_ONLY)
void open_cfw_app_slave_legacy_advertising_restart(void *message)
{
    const open_cfw_app_u8 *event = (const open_cfw_app_u8 *)message;
    if (event == (const open_cfw_app_u8 *)0) {
        return;
    }
    if (event[2] == OPEN_CFW_APP_DM_CONN_CLOSE_IND) {
        if (OPEN_CFW_APP_SLAVE_STATE[0x75U] != 0U) {
            OPEN_CFW_APP_SLAVE_STATE[0x75U] = 0U;
            return;
        }
    } else if (event[2] == OPEN_CFW_APP_DM_CONN_OPEN_IND) {
        if (OPEN_CFW_APP_SLAVE_STATE[0x75U] != 0U) {
            OPEN_CFW_APP_SLAVE_STATE[0x75U] = 0U;
            return;
        }
        OPEN_CFW_APP_SLAVE_STATE[0x57U] = OPEN_CFW_APP_ADV_STOPPED;
    }
    if (OPEN_CFW_APP_SLAVE_STATE[0x57U] == OPEN_CFW_APP_ADV_STOPPED) {
        OPEN_CFW_APP_SLAVE_STATE[0x57U] = OPEN_CFW_APP_ADV_STATE_1;
        open_cfw_app_slave_legacy_advertising_start();
    }
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_LEGACY_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_MODE_ONLY)
int open_cfw_app_slave_legacy_advertising_mode(void)
{
    open_cfw_app_u32 callback = open_cfw_app_load_u32(
        OPEN_CFW_APP_SLAVE_STATE + 0x78U
    );
    if (callback == 0U) {
        open_cfw_app_store_u32(
            OPEN_CFW_APP_SLAVE_STATE + 0x78U,
            OPEN_CFW_APP_STOCK_LEGACY_STOP_CALLBACK
        );
        open_cfw_app_store_u32(
            OPEN_CFW_APP_SLAVE_STATE + 0x7CU,
            OPEN_CFW_APP_STOCK_LEGACY_RESTART_CALLBACK
        );
        return 1;
    }
    return callback == OPEN_CFW_APP_STOCK_LEGACY_STOP_CALLBACK;
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_LEGACY_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_SET_DATA_ONLY)
void open_cfw_app_advertising_set_data(
    open_cfw_app_u8 location, open_cfw_app_u8 length,
    open_cfw_app_u8 *data
)
{
    if (!open_cfw_app_slave_legacy_advertising_mode()) {
        return;
    }
    if (length > OPEN_CFW_APP_ADV_DATA_MAX) {
        length = OPEN_CFW_APP_ADV_DATA_MAX;
    }
    open_cfw_app_advertising_set_data_internal(
        0U, location, length, data,
        OPEN_CFW_APP_ADV_DATA_MAX, OPEN_CFW_APP_ADV_DATA_MAX
    );
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_LEGACY_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_START_ONLY)
void open_cfw_app_advertising_start(open_cfw_app_u8 mode)
{
    volatile open_cfw_app_u8 *config;
    open_cfw_app_u8 handle = 0U;
    open_cfw_app_u8 maximum_events = 0U;
    if (!open_cfw_app_slave_legacy_advertising_mode()) {
        return;
    }
    config = OPEN_CFW_APP_ADV_CONFIG;
    if (config == (volatile open_cfw_app_u8 *)0) {
        return;
    }
    OPEN_CFW_APP_SLAVE_STATE[0x57U] = OPEN_CFW_APP_ADV_STATE_1;
    open_cfw_app_slave_advertising_start_internal(
        1U, &handle,
        (open_cfw_app_u16 *)(void *)(config + 6U),
        (open_cfw_app_u16 *)(void *)config,
        &maximum_events, 1U, mode
    );
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_LEGACY_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_STOP_ONLY)
void open_cfw_app_advertising_stop(void)
{
    open_cfw_app_u8 handle = 0U;
    if (open_cfw_app_slave_legacy_advertising_mode()) {
        open_cfw_app_advertising_stop_internal(1U, &handle);
    }
}
#endif

#if defined(OPEN_CFW_CORDIO_APP_LEGACY_BUILD_ALL) || \
    defined(OPEN_CFW_CORDIO_APP_LEGACY_ADV_SET_TYPE_ONLY)
void open_cfw_app_advertising_set_type(open_cfw_app_u8 advertising_type)
{
    volatile open_cfw_app_u8 *config;
    if (!open_cfw_app_slave_legacy_advertising_mode()) {
        return;
    }
    config = OPEN_CFW_APP_ADV_CONFIG;
    if (config == (volatile open_cfw_app_u8 *)0) {
        return;
    }
    OPEN_CFW_APP_SLAVE_STATE[0x57U] = OPEN_CFW_APP_ADV_STATE_1;
    open_cfw_app_advertising_set_type_internal(
        0U, advertising_type,
        open_cfw_app_load_u16(config + 6U),
        open_cfw_app_load_u16(config), 0U, 1U
    );
}
#endif
