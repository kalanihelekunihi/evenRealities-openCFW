/* BLE central (ring master) message path, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble_central.c.
 * Native 0x4a02e8..0x4a1518 and 0x4a1660..0x4a19ba:
 *   _masterConnect 0x4a02e8, dmDiscCancel 0x4a04fa, _bleMasterGetCB 0x4a0530,
 *   _masterProcMsg 0x4a06d4, _masterMaybeNotifyRingConnectFailure 0x4a1660,
 *   _masterConnectEventRetry 0x4a1840.
 *
 * _masterProcMsg is the central half of the BLE application WSF handler
 * (ring_dm_event_dispatch 0x4a19c0 calls it before APP_BleRingProcMsg). It
 * consumes Cordio ATT/DM callback events for the master link plus the
 * product EVEN_MASTER_* messages (0xae..0xb4) posted by APP_Master*Event.
 * Ring link states (_SetRingLinkState): 0 idle, 1 opening, 2 connected,
 * 3 local disconnecting, 4 hand-switch disconnect, 5 open cancelled, 6 unpair. */
#include <stdint.h>
#include <stddef.h>

/* wsfMsgHdr_t plus the event bodies this handler reads. */
typedef struct {
    uint16_t param;  /* +0 connection id for DM/ATT events */
    uint8_t event;   /* +2 */
    uint8_t status;  /* +3 */
} g2_wsf_msg_hdr_t;

typedef union {
    g2_wsf_msg_hdr_t hdr;
    struct { /* hciLeConnCmplEvt_t (DM_CONN_OPEN_IND) */
        g2_wsf_msg_hdr_t hdr;
        uint8_t status, reserved5;
        uint16_t handle;          /* +6 */
        uint8_t role, addr_type;  /* +8, +9 */
        uint8_t peer_addr[6];     /* +10 */
        uint16_t conn_interval;   /* +16, 1.25 ms units */
    } open;
    struct { /* hciDisconnectCmplEvt_t (DM_CONN_CLOSE_IND) */
        g2_wsf_msg_hdr_t hdr;
        uint8_t status, reserved5;
        uint16_t handle;          /* +6 */
        uint8_t reason;           /* +8 HCI error code */
    } close;
    struct { /* hciLeConnUpdateCmplEvt_t (DM_CONN_UPDATE_IND) */
        g2_wsf_msg_hdr_t hdr;
        uint8_t status, reserved5; /* +4 */
        uint16_t handle;          /* +6 */
        uint16_t conn_interval;   /* +8 */
    } update;
    struct { /* hciReadRssiCmdCmplEvt_t (DM_CONN_READ_RSSI_IND) */
        g2_wsf_msg_hdr_t hdr;
        uint8_t status, reserved5;
        uint16_t handle;          /* +6 */
        int8_t rssi;              /* +8 */
    } rssi;
    struct { /* attEvt_t (ATT_MTU_UPDATE_IND) */
        g2_wsf_msg_hdr_t hdr;
        uint8_t *value;           /* +4 */
        uint16_t value_len;       /* +8 */
        uint16_t handle;          /* +10 */
        uint8_t continuing, reserved13;
        uint16_t mtu;             /* +14 */
    } att;
    struct { /* 12-byte EVEN_MASTER_* message built by APP_Master*Event */
        g2_wsf_msg_hdr_t hdr;
        const uint8_t *addr;      /* +4 UNPAIR_DEV: addr[6] then addr type */
        uint16_t value;           /* +8 connect state / disconnect flags / scan state */
    } even;
} g2_master_msg_t;
_Static_assert(offsetof(g2_master_msg_t, open.conn_interval) == 16u, "hciLeConnCmplEvt_t");
_Static_assert(offsetof(g2_master_msg_t, att.mtu) == 14u, "attEvt_t mtu");
_Static_assert(offsetof(g2_master_msg_t, even.value) == 8u, "EVEN_MASTER message");

/* Master context (pointer cell RAM 0x200742fc, also shadowed at 0x20074304). */
typedef struct {
    uint8_t reserved_00[0x55];
    uint8_t conn_id;     /* +0x55 MConnId, 0 when no master link */
    uint8_t handler_id;  /* +0x56 WSF handler for EVEN_MASTER_* messages */
    uint8_t reserved_57[2];
    uint8_t flag_59;     /* +0x59 cleared on every connect attempt */
} g2_ble_master_ctx_t;

/* Master connection parameters (pointer cell RAM 0x20074300). */
typedef struct {
    uint8_t reserved_00[4];
    void *db_handle;     /* +0x04 appDbHdl_t of a bonded record, or NULL */
    uint8_t addr_type;   /* +0x08 */
    uint8_t addr[6];     /* +0x09 target address, LSB first */
    uint8_t reserved_0f[6];
    uint8_t flag_15;     /* +0x15 cleared on every connect attempt */
    uint8_t reserved_16[0x0e];
    uint16_t mtu;        /* +0x24 negotiated ATT MTU */
} g2_ble_master_conn_t;
_Static_assert(offsetof(g2_ble_master_conn_t, flag_15) == 0x15u, "conn cfg flag");
_Static_assert(offsetof(g2_ble_master_conn_t, mtu) == 0x24u, "conn cfg mtu");

/* appMasterCfg_t at ROM 0x78c9e4: {0xa0, 0x80, 10000 ms, discMode 0, scanType 1}. */
typedef struct {
    uint16_t scan_interval;
    uint16_t scan_window;
    uint16_t scan_duration;
    uint8_t disc_mode;
    uint8_t scan_type;
} g2_app_master_cfg_t;

enum {
    ATTC_READ_RSP = 0x05, ATTC_WRITE_RSP = 0x09, ATTC_WRITE_CMD_RSP = 0x0a,
    ATTC_HANDLE_VALUE_NTF = 0x0d, ATTC_HANDLE_VALUE_IND = 0x0e,
    ATTS_DB_HASH_CALC_CMPL_IND = 0x15, ATT_MTU_UPDATE_IND = 0x16,
    DM_SCAN_START_IND = 0x24, DM_SCAN_STOP_IND = 0x25, DM_SCAN_REPORT_IND = 0x26,
    DM_CONN_OPEN_IND = 0x27, DM_CONN_CLOSE_IND = 0x28, DM_CONN_UPDATE_IND = 0x29,
    DM_SEC_ENCRYPT_FAIL_IND = 0x2d, DM_CONN_READ_RSSI_IND = 0x39,
    EVEN_MASTER_CONNECT_EVT = 0xae, EVEN_MASTER_DISCONNECT_EVT = 0xaf,
    EVEN_MASTER_CONNECT_CANCEL_EVT = 0xb0, EVEN_MASTER_UNPAIR_DEV_EVT = 0xb1,
    EVEN_MASTER_SCAN_EVT = 0xb2, EVEN_MASTER_READ_RSSI_EVT = 0xb3,
    EVEN_MASTER_SET_PHY_EVT = 0xb4
};
enum { DM_ROLE_MASTER = 0u };
enum { HCI_ERR_CONN_TIMEOUT = 0x08u, HCI_ERR_CONN_FAIL = 0x3eu };
/* EVEN_MASTER_DISCONNECT_EVT flag bits (APP_MasterConnectEvent / UnpairConnId). */
enum { DISC_FLAG_DISCONNECT = 0x002u, DISC_FLAG_UNPAIR = 0x040u, DISC_FLAG_BY_LOCAL = 0x100u };
enum { RING_LINK_IDLE = 0u, RING_LINK_OPENING = 1u, RING_LINK_CONNECTED = 2u,
       RING_LINK_LOCAL_DISCONNECTING = 3u, RING_LINK_SWITCH_DISCONNECTING = 4u,
       RING_LINK_OPEN_CANCELLED = 5u, RING_LINK_UNPAIRING = 6u };
#define RING_CONN_EVENT_TICK_KEY 0x10102u  /* event-report key, ROM pool 0x4a15bc */

extern g2_ble_master_ctx_t *audio_ble_master_context;      /* RAM 0x200742fc */
extern g2_ble_master_conn_t *audio_ble_master_mode_slot;   /* RAM 0x20074300 */
extern g2_ble_master_ctx_t *audio_ble_master_state_shadow; /* RAM 0x20074304 */
extern uint8_t *g2_ble_master_conn_ccb;                     /* RAM 0x200742f8, row of 0x200717b0 */
extern uint8_t audio_ble_atts_connection_rows[];            /* RAM 0x200717b0, 0x30-byte rows */
extern uint32_t g2_ble_master_short_interval_tick;          /* RAM 0x2007430c */
extern volatile uint16_t audio_ble_master_connect_wait;     /* RAM 0x20074f18 retry count */
extern volatile uint8_t audio_ble_master_failure_notify;    /* RAM 0x20074f82 */
extern volatile uint8_t audio_ble_master_failure_count;     /* RAM 0x20074f83 */
extern volatile uint8_t audio_ble_master_connection_flag;   /* RAM 0x20074f84 auto-retry */
extern volatile uint8_t audio_ble_ring_link_state;          /* RAM 0x20074f85 */
extern volatile uint8_t audio_ble_master_open_connection;   /* RAM 0x20074f86 */
extern volatile uint8_t audio_ble_master_publish_flag;      /* RAM 0x20074f88 */
extern volatile uint8_t audio_ble_master_link_ready;        /* RAM 0x20074f89 */
extern uint8_t audio_ble_master_target_address[6];          /* RAM 0x200003c0 */
extern const g2_app_master_cfg_t audio_ble_master_registration_table; /* ROM 0x78c9e4 */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);      /* 0x439be4 */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);         /* 0x43c0e4 */
extern void elog_hexdump_43dacc(const char *name, uint32_t width, const uint8_t *buf, uint32_t size);
extern uint32_t osKernelGetTickCount(void);
extern void fw_event_loop_push_delayed(void (*callback)(void), uint32_t argument, uint32_t delay_ms);
extern uint32_t fw_event_loop_remove_delayed(void (*callback)(void));
extern void _SetRingLinkState(uint8_t state, const char *reason);
extern const char *_ringLinkStateName(uint8_t state);
extern void ring_master_reconnect(const g2_master_msg_t *msg);
extern void ring_master_scan_start(const g2_master_msg_t *msg);
extern void _bleMasterScanStop(const g2_master_msg_t *msg);
extern void _bleMasterScanReport(const g2_master_msg_t *msg);
extern void _masterScan(uint8_t state);
extern void _masterConnectCancel(uint8_t conn_id);
extern void central_emit_ring_link_event_004a153c(uint8_t event);
extern void central_publish_ring_link_ready_work_004a285c(void);
extern void central_schedule_master_connect_004a2618(uint32_t delay_ms, uint8_t from_retry);
extern void APP_MasterClearRingConnectFailureNotifyAfterRetry(void);
extern uint32_t PB_TxEncodeNotifyRingConnectInfo(uint32_t reason);
extern void RING_ConnectPolicyResetRingConnectInfoThrottle(void);
extern void thread_ble_wsf_tx_complete_notify(void);
extern int32_t Thread_MsgRxFromBle(uint32_t id, const void *bytes, uint32_t length);
extern void rpc_system_ble_status_sync_4b82e8(uint8_t state);
extern void ring_wear_state_reset_4728a0(void);
extern uint32_t ring_set_phy_process_472596(uint8_t conn_id);
extern void audio_uart_ring_wear_persist_48eb32(uint32_t key, uint32_t length, const void *payload);
extern uint8_t *audio_setting_unit_record_get_466010(void);
extern void audio_uart_ring_unpair_publish_hand_4661a6(void);
extern const uint8_t *AppMasterSecGetAddr(void);
extern void AppMasterSecClearAddr(void);
extern void *audio_ble_pair_record_find_47ad74(uint8_t addr_type, const uint8_t *addr); /* AppDbFindByAddr */
extern uint8_t app_db_paired_count_47a676(uint8_t role);
extern void ble_pair_record_remove_47b59c(uint8_t addr_type, const uint8_t *addr);
extern void app_conn_close_4bb04a(uint8_t conn_id); /* DmConnClose(DM_CLIENT_ID_APP, id, 0x13) */
extern uint8_t AppConnOpen(uint8_t addr_type, const uint8_t *addr, void *db_handle);
extern uint8_t DmConnRole(uint8_t conn_id);
extern const uint8_t *DmConnPeerAddr(uint8_t conn_id);
extern void DmConnReadRssi(uint8_t conn_id);
extern void DmConnSetScanInterval(uint16_t scan_interval, uint16_t scan_window);
extern uint8_t GattValueUpdate(const g2_ble_master_ctx_t *ctx, const g2_master_msg_t *msg);

static const char module_tag[] = "ble.master"; /* ROM 0x78a028 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c"; /* ROM 0x6ff9b8 */
static const char fn_connect[] = "_masterConnect";                       /* ROM 0x784d10 */
static const char fn_get_cb[] = "_bleMasterGetCB";                       /* ROM 0x784d20 */
static const char fn_proc_msg[] = "_masterProcMsg";                       /* ROM 0x784d30 */
static const char fn_maybe_notify[] = "_masterMaybeNotifyRingConnectFailure"; /* ROM 0x747184 */
static const char fn_retry[] = "_masterConnectEventRetry";               /* ROM 0x768e10 */

/* Stock log macro: extended text when flag bit 1 is set, "[ble.master]"-prefixed
 * compressed record when bit 0 or 2 is set. mask = level << 26 | argc << 22. */
#define MASTER_LOG(level, fn, line, mask, fmt, ...) do { \
    if (audio_log_flags() & 2u) \
        audio_log_extended((level), module_tag, source_file, (fn), (line), fmt, ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) \
        (void)compress_log_output((mask), "[ble.master]" fmt, "[ble.master]" fmt, ##__VA_ARGS__); \
} while (0)

void _masterMaybeNotifyRingConnectFailure(uint8_t reason);
void _masterConnectEventRetry(uint8_t reason);

#define EVT_CB(fn) ((void (*)(void))(fn))

void _masterConnect(uint8_t event)
{
    if (!(event & 1u))
        return;
    MASTER_LOG(4u, fn_connect, 0x1d0u, 0x10000000u, "_masterConnect: APP_BLE_MASTER_CONNECT_EVT");
    if (audio_ble_ring_link_state == RING_LINK_OPENING) {
        MASTER_LOG(3u, fn_connect, 0x1d6u, 0x0c000000u, "_masterConnect: already OPENING, return");
        return;
    }
    _SetRingLinkState(RING_LINK_OPENING, "_masterConnect: AppConnOpen");
    g2_ble_master_conn_t *conn = audio_ble_master_mode_slot;
    conn->addr_type = 1u;
    (void)audio_queue_copy_bytes(conn->addr, audio_ble_master_target_address, 6u);
    void *db_handle = audio_ble_pair_record_find_47ad74(conn->addr_type, conn->addr);
    if (db_handle != NULL)
        MASTER_LOG(3u, fn_connect, 0x1e1u, 0x0d800000u,
                   "_masterConnect: Found paired record, device address %02X:%02X:%02X:%02X:%02X:%02X",
                   conn->addr[5], conn->addr[4], conn->addr[3], conn->addr[2], conn->addr[1], conn->addr[0]);
    conn->db_handle = db_handle;
    DmConnSetScanInterval(audio_ble_master_registration_table.scan_interval,
                          audio_ble_master_registration_table.scan_window);
    audio_ble_master_publish_flag = 0u;
    audio_ble_master_link_ready = 0u;
    uint8_t conn_id = AppConnOpen(conn->addr_type, conn->addr, conn->db_handle);
    MASTER_LOG(4u, fn_connect, 0x1eau, 0x10400000u, "_masterConnect: master connId = %d", conn_id);
    audio_ble_master_context->flag_59 = 0u;
    conn->flag_15 = 0u;
    if (conn_id == 0u) {
        _SetRingLinkState(RING_LINK_IDLE, "_masterConnect: AppConnOpen failed");
        return;
    }
    /* A 4 s guard cancels an OPEN that never completes. */
    audio_ble_master_open_connection = conn_id;
    (void)fw_event_loop_remove_delayed(EVT_CB(_masterConnectCancel));
    fw_event_loop_push_delayed(EVT_CB(_masterConnectCancel), conn_id, 4000u);
}

/* Read/notification responses on the master link go to the GATT client cache.
 * The stock body tests the result and does nothing with it. */
void dmDiscCancel(const g2_master_msg_t *msg)
{
    if (msg->hdr.status == 0u)
        (void)GattValueUpdate(audio_ble_master_state_shadow, msg);
}

void _bleMasterGetCB(const g2_master_msg_t *msg)
{
    g2_ble_master_conn_ccb = audio_ble_atts_connection_rows + (uint32_t)msg->hdr.param * 0x30u - 0x30u;
    audio_ble_master_context->conn_id = (uint8_t)msg->hdr.param;
    MASTER_LOG(4u, fn_get_cb, 0x221u, 0x10400000u, "MASTER ble_connect = 0x%x", g2_ble_master_conn_ccb);
    MASTER_LOG(4u, fn_get_cb, 0x222u, 0x10400000u, "MASTER MConnId = 0x%x", audio_ble_master_context->conn_id);
}

static void master_conn_close(const g2_master_msg_t *msg, uint8_t conn_id)
{
    MASTER_LOG(4u, fn_proc_msg, 0x298u, 0x10800000u, "DM_CONN_CLOSE_IND connId = %d, role = %d",
               conn_id, DmConnRole(conn_id));
    if (conn_id == 0u || DmConnRole(conn_id) != DM_ROLE_MASTER)
        return;
    RING_ConnectPolicyResetRingConnectInfoThrottle();
    uint8_t previous = audio_ble_ring_link_state;
    audio_ble_master_context->conn_id = 0u;
    audio_ble_master_open_connection = 0u;
    g2_ble_master_short_interval_tick = 0u;
    ring_wear_state_reset_4728a0();
    (void)fw_event_loop_remove_delayed(EVT_CB(_masterConnectCancel));
    uint8_t reason = msg->close.reason != 0u ? msg->close.reason : HCI_ERR_CONN_TIMEOUT;
    (void)fw_event_loop_remove_delayed(EVT_CB(PB_TxEncodeNotifyRingConnectInfo));
    (void)fw_event_loop_remove_delayed(central_publish_ring_link_ready_work_004a285c);
    if (previous != RING_LINK_OPEN_CANCELLED && audio_ble_master_link_ready != 0u) {
        rpc_system_ble_status_sync_4b82e8(2u);
        audio_ble_master_link_ready = 0u;
    } else if (previous != RING_LINK_OPEN_CANCELLED) {
        MASTER_LOG(3u, fn_proc_msg, 0x2b8u, 0x0c000000u,
                   "Skip RING_DISCONNECTED notify: link never reached GATT ready");
    }
    MASTER_LOG(3u, fn_proc_msg, 0x2bbu, 0x0cc00000u,
               ">>> DM_ROLE_MASTER disconnect connId=%d reason=0x%x preState=%s <<<",
               conn_id, msg->close.reason, _ringLinkStateName(previous));

    if (previous == RING_LINK_UNPAIRING) {
        const uint8_t *addr = AppMasterSecGetAddr();
        if (addr != NULL)
            ble_pair_record_remove_47b59c(addr[6], addr);
        AppMasterSecClearAddr();
        APP_MasterClearRingConnectFailureNotifyAfterRetry();
        audio_ble_master_connect_wait = 0u;
        _SetRingLinkState(RING_LINK_IDLE, "unpair-close");
        return;
    }
    _masterMaybeNotifyRingConnectFailure(reason);
    if (previous == RING_LINK_LOCAL_DISCONNECTING) {
        MASTER_LOG(3u, fn_proc_msg, 0x2ccu, 0x0c000000u, "Connection terminated by local");
        APP_MasterClearRingConnectFailureNotifyAfterRetry();
        audio_ble_master_connect_wait = 0u;
        central_emit_ring_link_event_004a153c(4u);
        audio_ble_master_publish_flag = 0u;
        _SetRingLinkState(RING_LINK_IDLE, "local-disconnect-close");
        return;
    }
    if (previous == RING_LINK_SWITCH_DISCONNECTING) {
        MASTER_LOG(3u, fn_proc_msg, 0x2d3u, 0x0c000000u,
                   "Connection terminated by hand switch, silent for app notify");
        APP_MasterClearRingConnectFailureNotifyAfterRetry();
        audio_ble_master_connect_wait = 0u;
        audio_ble_master_publish_flag = 0u;
        _SetRingLinkState(RING_LINK_IDLE, "switch-disconnect-close");
        return;
    }
    if (previous == RING_LINK_OPEN_CANCELLED)
        MASTER_LOG(3u, fn_proc_msg, 0x2dcu, 0x0c400000u,
                   "OPEN timeout cancel, will retry with count=%d", audio_ble_master_connect_wait);
    else
        MASTER_LOG(3u, fn_proc_msg, 0x2dfu, 0x0c800000u,
                   "Connection closed unexpectedly (reason=0x%02x), will retry with count=%d",
                   msg->close.reason, audio_ble_master_connect_wait);
    central_emit_ring_link_event_004a153c(audio_ble_master_publish_flag != 0u ? 4u : 5u);
    audio_ble_master_publish_flag = 0u;
    _SetRingLinkState(RING_LINK_IDLE,
                      previous == RING_LINK_OPEN_CANCELLED ? "cancel-close" : "abnormal-close");
    _masterConnectEventRetry(reason);
}

void _masterProcMsg(const g2_master_msg_t *msg)
{
    uint8_t conn_id = (uint8_t)msg->hdr.param;
    switch (msg->hdr.event) {
    case ATTC_READ_RSP:
    case ATTC_HANDLE_VALUE_NTF:
    case ATTC_HANDLE_VALUE_IND:
        if (conn_id != 0u && DmConnRole(conn_id) == DM_ROLE_MASTER)
            dmDiscCancel(msg);
        break;

    case ATTC_WRITE_RSP:
    case ATTC_WRITE_CMD_RSP:
        if (conn_id == 0u || DmConnRole(conn_id) != DM_ROLE_MASTER)
            break;
        MASTER_LOG(4u, fn_proc_msg, 0x241u, 0x10000000u, "DM_ROLE_MASTER ATTC_WRITE_RSP");
        thread_ble_wsf_tx_complete_notify();
        break;

    case ATTS_DB_HASH_CALC_CMPL_IND:
        MASTER_LOG(4u, fn_proc_msg, 0x256u, 0x10000000u, "ATTS_DB_HASH_CALC_CMPL_IND");
        ring_master_reconnect(msg);
        break;

    case ATT_MTU_UPDATE_IND:
        if (conn_id == 0u || DmConnRole(conn_id) != DM_ROLE_MASTER)
            break;
        audio_ble_master_mode_slot->mtu = msg->att.mtu;
        MASTER_LOG(4u, fn_proc_msg, 0x25du, 0x10400000u, "Master Negotiated MTU = %d",
                   audio_ble_master_mode_slot->mtu);
        break;

    case DM_SCAN_START_IND:
        MASTER_LOG(4u, fn_proc_msg, 0x247u, 0x10000000u, "DM_SCAN_START_IND");
        ring_master_scan_start(msg);
        break;

    case DM_SCAN_STOP_IND:
        MASTER_LOG(4u, fn_proc_msg, 0x24cu, 0x10000000u, "DM_SCAN_STOP_IND");
        _bleMasterScanStop(msg);
        break;

    case DM_SCAN_REPORT_IND:
        _bleMasterScanReport(msg);
        break;

    case DM_CONN_OPEN_IND: {
        MASTER_LOG(4u, fn_proc_msg, 0x262u, 0x10800000u, "DM_CONN_OPEN_IND connId = %d, role = %d",
                   conn_id, DmConnRole(conn_id));
        if (conn_id == 0u || DmConnRole(conn_id) != DM_ROLE_MASTER)
            break;
        audio_ble_master_connect_wait = 0u;
        audio_ble_master_open_connection = 0u;
        _SetRingLinkState(RING_LINK_CONNECTED, "DM_CONN_OPEN_IND");
        (void)fw_event_loop_remove_delayed(EVT_CB(_masterConnectCancel));
        _bleMasterGetCB(msg);
        /* Start timing a short (< 31.25 ms) connection interval; DM_CONN_UPDATE_IND reports it. */
        if (msg->open.conn_interval < 25u)
            g2_ble_master_short_interval_tick = osKernelGetTickCount();
        else
            g2_ble_master_short_interval_tick = 0u;
        (void)fw_event_loop_remove_delayed(central_publish_ring_link_ready_work_004a285c);
        fw_event_loop_push_delayed(central_publish_ring_link_ready_work_004a285c, 0u, 6000u);
        uint8_t paired = app_db_paired_count_47a676(1u);
        MASTER_LOG(3u, fn_proc_msg, 0x277u, 0x0c400000u, "Current paired devices: Master=%d", paired);
        DmConnReadRssi(conn_id);
        break;
    }

    case DM_CONN_CLOSE_IND:
        master_conn_close(msg, conn_id);
        break;

    case DM_CONN_UPDATE_IND:
        if (conn_id == 0u || DmConnRole(conn_id) != DM_ROLE_MASTER)
            break;
        MASTER_LOG(3u, fn_proc_msg, 0x287u, 0x0cc00000u,
                   "ring conn update status=0x%02x connInterval=%d (%d ms)", msg->update.status,
                   msg->update.conn_interval, (uint32_t)msg->update.conn_interval * 1250u / 1000u);
        if (msg->update.status != 0u)
            break;
        if (msg->update.conn_interval < 25u) {
            if (g2_ble_master_short_interval_tick == 0u)
                g2_ble_master_short_interval_tick = osKernelGetTickCount();
        } else if (g2_ble_master_short_interval_tick != 0u) {
            uint32_t elapsed = osKernelGetTickCount() - g2_ble_master_short_interval_tick;
            audio_uart_ring_wear_persist_48eb32(RING_CONN_EVENT_TICK_KEY, 1u, &elapsed);
            g2_ble_master_short_interval_tick = 0u;
        }
        break;

    case DM_CONN_READ_RSSI_IND: {
        if (conn_id == 0u || DmConnRole(conn_id) != DM_ROLE_MASTER)
            break;
        if (msg->hdr.status != 0u) {
            MASTER_LOG(2u, fn_proc_msg, 0x2f9u, 0x08400000u, "Failed to read RSSI, status: 0x%02X",
                       msg->hdr.status);
            break;
        }
        int8_t rssi = msg->rssi.rssi;
        const uint8_t *peer = DmConnPeerAddr(conn_id);
        MASTER_LOG(3u, fn_proc_msg, 0x2f7u, 0x0dc00000u,
                   "Master connected to slave RSSI: %d dBm, Peer Address: %02X:%02X:%02X:%02X:%02X:%02X",
                   rssi, peer[5], peer[4], peer[3], peer[2], peer[1], peer[0]);
        break;
    }

    case DM_SEC_ENCRYPT_FAIL_IND:
        MASTER_LOG(4u, fn_proc_msg, 0x2ffu, 0x10000000u, "DM_SEC_ENCRYPT_FAIL_IND");
        (void)Thread_MsgRxFromBle(0x200u, audio_ble_master_target_address, 6u);
        break;

    case EVEN_MASTER_CONNECT_EVT: {
        if (conn_id != 0u)
            break;
        uint8_t state = (uint8_t)msg->even.value;
        MASTER_LOG(4u, fn_proc_msg, 0x306u, 0x10400000u, "EVEN_MASTER_CONNECT_EVT state = %d", state);
        MASTER_LOG(3u, fn_proc_msg, 0x307u, 0x0cc00000u, "ring addr[5-3] = %02X:%02X:%02X:",
                   audio_ble_master_target_address[5], audio_ble_master_target_address[4],
                   audio_ble_master_target_address[3]);
        MASTER_LOG(3u, fn_proc_msg, 0x308u, 0x0cc00000u, "ring addr[2-0] = %02X:%02X:%02X",
                   audio_ble_master_target_address[2], audio_ble_master_target_address[1],
                   audio_ble_master_target_address[0]);
        ble_pair_record_remove_47b59c(1u, audio_ble_master_target_address);
        AppMasterSecClearAddr();
        _masterConnect(1u);
        break;
    }

    case EVEN_MASTER_DISCONNECT_EVT: {
        if (conn_id == 0u || DmConnRole(conn_id) != DM_ROLE_MASTER)
            break;
        uint16_t flags = msg->even.value;
        MASTER_LOG(3u, fn_proc_msg, 0x315u, 0x0c400000u, "EVEN_MASTER_DISCONNECT_EVT event = %d", flags);
        if (flags & DISC_FLAG_UNPAIR)
            _SetRingLinkState(RING_LINK_UNPAIRING, "EVEN_MASTER_DISCONNECT_EVT(UNPAIR)");
        else if ((flags & DISC_FLAG_DISCONNECT) && (flags & DISC_FLAG_BY_LOCAL))
            _SetRingLinkState(RING_LINK_LOCAL_DISCONNECTING, "EVEN_MASTER_DISCONNECT_EVT(BY_LOCAL)");
        else if (flags & DISC_FLAG_DISCONNECT)
            MASTER_LOG(3u, fn_proc_msg, 0x324u, 0x0c000000u,
                       "EVEN_MASTER_DISCONNECT_EVT: peer/remote initiated, no state change");
        if ((flags & DISC_FLAG_DISCONNECT) && conn_id != 0u) {
            MASTER_LOG(4u, fn_proc_msg, 0x328u, 0x10000000u, "APP_BLE_MASTER_DISCONNECT_EVT");
            app_conn_close_4bb04a(conn_id);
        }
        break;
    }

    case EVEN_MASTER_CONNECT_CANCEL_EVT:
        if (conn_id == 0u)
            break;
        MASTER_LOG(4u, fn_proc_msg, 0x334u, 0x10400000u, "EVEN_MASTER_CONNECT_CANCEL_EVT connId=%d", conn_id);
        _SetRingLinkState(RING_LINK_OPEN_CANCELLED, "EVEN_MASTER_CONNECT_CANCEL_EVT");
        app_conn_close_4bb04a(conn_id);
        break;

    case EVEN_MASTER_UNPAIR_DEV_EVT: {
        const uint8_t *addr = msg->even.addr;
        elog_hexdump_43dacc("EVEN_MASTER_UNPAIR_DEV_EVT", 16u, addr, 6u);
        MASTER_LOG(4u, fn_proc_msg, 0x33fu, 0x10400000u, "EVEN_MASTER_UNPAIR_DEV_EVT addrType = %d", addr[6]);
        ble_pair_record_remove_47b59c(addr[6], addr);
        AppMasterSecClearAddr();
        /* Forget the ring MAC in the settings record (+12, all-FF = unset) and publish. */
        audio_uart_buffer_zero(audio_setting_unit_record_get_466010() + 12u, 6u, 0xffu);
        audio_uart_ring_unpair_publish_hand_4661a6();
        break;
    }

    case EVEN_MASTER_SCAN_EVT: {
        if (conn_id == 0u || DmConnRole(conn_id) != DM_ROLE_MASTER)
            break;
        uint8_t state = (uint8_t)msg->even.value;
        MASTER_LOG(4u, fn_proc_msg, 0x34bu, 0x10400000u, "EVEN_MASTER_SCAN_EVT state = %d", state);
        _masterScan(state);
        break;
    }

    case EVEN_MASTER_READ_RSSI_EVT:
        if (audio_ble_master_context->conn_id == 0u ||
            DmConnRole(audio_ble_master_context->conn_id) != DM_ROLE_MASTER)
            break;
        MASTER_LOG(4u, fn_proc_msg, 0x353u, 0x10400000u,
                   "EVEN_MASTER_READ_RSSI_EVT: Reading RSSI for connId = %d", audio_ble_master_context->conn_id);
        DmConnReadRssi(audio_ble_master_context->conn_id);
        break;

    case EVEN_MASTER_SET_PHY_EVT:
        if (audio_ble_master_context->conn_id == 0u ||
            DmConnRole(audio_ble_master_context->conn_id) != DM_ROLE_MASTER)
            break;
        MASTER_LOG(4u, fn_proc_msg, 0x35fu, 0x10400000u,
                   "EVEN_MASTER_SET_PHY_EVT: Setting PHY for connId = %d", audio_ble_master_context->conn_id);
        (void)ring_set_phy_process_472596(audio_ble_master_context->conn_id);
        break;

    default:
        break;
    }
}

/* Supervision timeout (0x08) notifies at once; other reasons only once the
 * notify was armed and on the second failure (never for 0x3e conn-fail). */
void _masterMaybeNotifyRingConnectFailure(uint8_t reason)
{
    if (audio_ble_master_connection_flag != 0u) {
        MASTER_LOG(3u, fn_maybe_notify, 0x383u, 0x0c400000u,
                   "Skip ring connect failure notify for auto retry, reason=%d", reason);
        return;
    }
    if (reason != HCI_ERR_CONN_TIMEOUT) {
        if (audio_ble_master_failure_notify == 0u) {
            MASTER_LOG(3u, fn_maybe_notify, 0x389u, 0x0c400000u,
                       "Ring connect failure notify not armed, reason=%d", reason);
            return;
        }
        audio_ble_master_failure_count++;
        if (reason == HCI_ERR_CONN_FAIL || audio_ble_master_failure_count < 2u) {
            MASTER_LOG(3u, fn_maybe_notify, 0x38fu, 0x0c400000u,
                       "Skip ring connect failure notify for first failure, reason=%d", reason);
            return;
        }
    }
    MASTER_LOG(3u, fn_maybe_notify, 0x394u, 0x0c400000u,
               "Notify ring connect failure after second failure, reason=%d", reason);
    audio_ble_master_failure_notify = 0u;
    audio_ble_master_failure_count = 0u;
    fw_event_loop_push_delayed(EVT_CB(PB_TxEncodeNotifyRingConnectInfo), reason, 1000u);
}

/* Back-off: 2 s for the first 10 retries, then (n - 10) * 10 s, capped at 30 min
 * from retry 190 on. A 0x3e near miss resets the count and retries in 2 s. */
void _masterConnectEventRetry(uint8_t reason)
{
    if (reason == HCI_ERR_CONN_FAIL) {
        audio_ble_master_connect_wait = 0u;
        MASTER_LOG(3u, fn_retry, 0x3aeu, 0x0c400000u,
                   "_masterConnectEventRetry: reason=0x%02x (conn-fail near miss), reset cnt, scheduleDelay = 2000 ms",
                   reason);
        central_schedule_master_connect_004a2618(2000u, 1u);
        return;
    }
    audio_ble_master_connect_wait++;
    MASTER_LOG(3u, fn_retry, 0x3b5u, 0x0c400000u, "_masterConnectEventRetry: retryCnt = %d",
               audio_ble_master_connect_wait);
    uint32_t interval = 1800000u;
    if (audio_ble_master_connect_wait >= 190u)
        MASTER_LOG(3u, fn_retry, 0x3bdu, 0x0c000000u,
                   "_masterConnectEventRetry: retryCnt >= 30, switch to 30 min interval");
    else if (audio_ble_master_connect_wait <= 10u)
        interval = 2000u;
    else
        interval = ((uint32_t)audio_ble_master_connect_wait - 10u) * 10000u;
    MASTER_LOG(3u, fn_retry, 0x3c9u, 0x0c800000u,
               "_masterConnectEventRetry: reason=0x%02x nextInterval = %lu ms", reason, (unsigned long)interval);
    central_schedule_master_connect_004a2618(interval, 1u);
}
