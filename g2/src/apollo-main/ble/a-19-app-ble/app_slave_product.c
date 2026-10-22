/* Product variants of Cordio app_slave.c, stock
 * D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-profiles\sources\apps\app\app_slave.c.
 * Native appSlaveResolvedAddrInd 0x4b3792..0x4b38f1 and AppSlaveProcDmMsg
 * 0x4b3ca4..0x4b422f; literal pools 0x4b3c8c..0x4b3ca3, 0x4b3f8c..0x4b3f93,
 * 0x4b416c, 0x4b4230..0x4b423f, 0x4b42e4..0x4b42ef, 0x4b4504, 0x4b46f0..0x4b471b.
 *
 * Differences from public Cordio af/app_slave.c:
 *  - appSlaveResolvedAddrInd logs when no resolution is in progress; on a
 *    resolved RPA it restores the bonded CCC table, client-supported-features
 *    record, CSRK and sign counter (work public Cordio does at connection
 *    open), sets the "peer resolved" flag at RAM 0x20074f93, and on the way out
 *    sends a slave security request when the link has no bond record.
 *  - AppSlaveProcDmMsg ignores DM_CONN_UPDATE_IND, logs data-length changes,
 *    requests 251-byte / 2120 us PDUs when the peer's remote features include
 *    LE Data Packet Length Extension, and reboots the EM9305 and resets DM on
 *    event 0x79 (hardware error in this stack's event numbering). The
 *    connection control block lookup also tests hdr.param against 0x20/0x79.
 * Other app_slave.c functions live in ble/ble-app and ble/u-02-cordio-variants. */
#include <stdint.h>
#include <stddef.h>

/* Cordio DM event ids as compared by the stock code. */
#define DM_RESET_CMPL_IND           0x20u
#define DM_ADV_STOP_IND             0x22u
#define DM_CONN_OPEN_IND            0x27u
#define DM_CONN_CLOSE_IND           0x28u
#define DM_CONN_UPDATE_IND          0x29u
#define DM_PRIV_RESOLVED_ADDR_IND   0x37u
#define DM_REM_CONN_PARAM_REQ_IND   0x40u
#define DM_CONN_DATA_LEN_CHANGE_IND 0x41u
#define DM_ADV_SET_STOP_IND         0x48u
#define DM_REMOTE_FEATURES_IND      0x57u
#define DM_HW_ERROR_IND             0x79u

#define HCI_SUCCESS                 0x00u
#define HCI_ERR_AUTH_FAILURE        0x05u
#define DM_KEY_IRK                  0x04u
#define DM_KEY_CSRK                 0x08u
#define ATTS_CLIENT_CHANGE_PENDING  0x03u /* change-aware state that needs a Service Changed */
#define HCI_LE_SUP_FEAT_DATA_LEN_EXT 0x20u /* remote features byte 0, bit 5 */
#define APP_DLE_TX_OCTETS           0xfbu
#define APP_DLE_TX_TIME_US          0x848u

/* Cordio wsfMsgHdr_t / dmEvt_t head. */
typedef struct {
    uint16_t param;  /* +0 connection id */
    uint8_t event;   /* +2 */
    uint8_t status;  /* +3 */
} app_dm_hdr_t;

/* Cordio appConnCb_t, 0x30-byte rows at RAM 0x200717b0. */
typedef struct {
    void *db_hdl;     /* +0x00 */
    uint8_t conn_id;  /* +0x04 */
    uint8_t rest[0x2b];
} app_conn_cb_t;
_Static_assert(sizeof(app_conn_cb_t) == 0x30, "appConnCb_t row");

/* Cordio appSecCfg_t behind the pointer cell 0x20074358. */
typedef struct {
    uint8_t auth;          /* +0 */
    uint8_t pad[3];
    uint8_t initiate_sec;  /* +4 */
} app_sec_cfg_t;

/* appSlaveCb (RAM 0x200719c8) fields used here. */
#define APP_SLAVE_FIND_LTK     0x6cu
#define APP_SLAVE_DB_HDL       0x70u
#define APP_SLAVE_IN_PROGRESS  0x74u
#define APP_SLAVE_ADV_STOP_CB  0x78u
/* appDbRec_t fields used here. */
#define APP_DB_CCC_TBL         0x6cu
#define APP_DB_PEER_SIGN_CNT   0x80u

extern uint8_t audio_ble_subsystem_link_state_200719c8[];       /* appSlaveCb, RAM 0x200719c8 */
extern uint8_t audio_ble_atts_connection_rows[];                /* appConnCb[], RAM 0x200717b0 */
extern const app_sec_cfg_t *audio_ble_comm_profile_slot;        /* pAppSecCfg, RAM 0x20074358 */
extern volatile uint8_t g2_app_slave_peer_resolved;            /* RAM 0x20074f93 */

extern void AttsCccInitTable(uint8_t conn_id, uint16_t *ccc_tbl);                       /* 0x52c244 */
extern void AttsCsfConnOpen(uint8_t conn_id, uint8_t change_aware_state, uint8_t *csf); /* 0x52d370 */
extern void GattSendServiceChangedInd(uint8_t conn_id, uint16_t start, uint16_t end);    /* 0x4b5a44 */
extern void AttsSetCsrk(uint8_t conn_id, uint8_t *csrk, uint8_t authenticated);          /* 0x52dbb8 */
extern void AttsSetSignCounter(uint8_t conn_id, uint32_t sign_counter);                  /* 0x52dbd6 */
extern const uint8_t *DmConnPeerAddr(uint8_t conn_id);                                   /* 0x4b6eea */
extern void DmPrivResolveAddr(const uint8_t *addr, const uint8_t *irk, uint16_t param);  /* 0x4d27f6 */
extern void DmSecSlaveReq(uint8_t conn_id, uint8_t auth);                                /* 0x52bb00 */
extern void DmConnSetDataLen(uint8_t conn_id, uint16_t tx_octets, uint16_t tx_time);    /* 0x4b6e6c */
extern void DmDevReset(void);                                                            /* 0x4b3026 */
extern void HciDrvRadioBoot(uint8_t cold_boot);                                          /* 0x4b48a6 */
extern void WsfTrace(const char *level, const char *format, ...);                        /* 0x52a63c */

extern void audio_ble_pair_record_flags_47b40c(uint32_t db_hdl, void *change_aware_state,
                                               uint32_t *csf);          /* AppDbGetCsfRecord */
extern uint32_t audio_ble_link_mask_select_47ae78(uint32_t db_hdl, uint8_t type,
                                                  uint8_t *sec_level);  /* AppDbGetKey */
extern uint32_t audio_ble_pair_record_next_47a630(uint32_t db_hdl);    /* AppDbGetNextRecord */
extern void audio_ble_slave_resolve_4b36b2(void *conn_cb);              /* appSecRspLtk */
extern void audio_ble_subsystem_child_4b32d4(void);                     /* appSlaveAdvModeInit */
extern void appSlaveConnOpen_4b36fc(void *event, uint8_t *conn_cb);
extern void app_slave_conn_close_4b3720(const app_dm_hdr_t *event, app_conn_cb_t *conn_cb);
extern void app_slave_remote_conn_param_req_4b38f2(const app_dm_hdr_t *event, app_conn_cb_t *conn_cb);

extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *a, const char *b, uint32_t n); /* strncmp 0x44b610 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char s_app[] = "APP";   /* ROM 0x4b4234 / 0x4b3f90 */
static const char s_err[] = "ERR";   /* ROM 0x4b423c / 0x4b3f8c */
static const char s_hci[] = "HCI";   /* ROM 0x4b4504 / 0x4b416c */
static const char s_info[] = "INFO"; /* ROM 0x78cb54 */
static const char s_warn[] = "WARN"; /* ROM 0x78cb5c */
static const char s_module[] = "app_slave"; /* ROM 0x78a2ec */
static const char s_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_slave.c"; /* ROM 0x6da160 */
static const char s_resolved[] = "appSlaveResolvedAddrInd"; /* ROM 0x7754f4 */
static const char s_not_in_progress[] =
    "appSlaveResolvedAddrInd: Address resolution not in progress, ignoring result"; /* ROM 0x6eb8f8 */
static const char s_not_in_progress_short[] =
    "[app_slave]appSlaveResolvedAddrInd: Address resolution not in progress, ignoring result"; /* ROM 0x6e26a0 */
static const char s_proc_dm[] = "AppSlaveProcDmMsg"; /* ROM 0x77e118 */
static const char s_data_len[] = "data length exchange, status= %d, maxRXLen= %d, maxTXlen= %d"; /* ROM 0x7096a4 */
static const char s_remote_feat[] = "remote feature: 0x%x,  DLE:0x%x"; /* ROM 0x75e090 */
static const char s_dle_yes[] = "Remote device support DLE"; /* ROM 0x769890 */
static const char s_dle_no[] = "Remote device doesn't support DLE"; /* ROM 0x7520e8 */

/* Cordio APP_TRACE_INFOn expansion of this build: the level string picks the
 * extended-log level (ERR 1, WARN 2, INFO 3, other 4) when vendor logging is
 * enabled; otherwise the record goes to WsfTrace unless the module is HCI.
 * Every call site here uses level "INFO" and module "APP". */
#define APP_TRACE(line, ...)                                                                   \
    do {                                                                                            \
        uint8_t lvl_ = 0u;                                                                          \
        if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u && audio_l2c_strncmp(s_info, s_err, 3u) == 0)       \
            lvl_ = 1u;                                                                              \
        else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u && audio_l2c_strncmp(s_info, s_warn, 4u) == 0) \
            lvl_ = 2u;                                                                              \
        else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u && audio_l2c_strncmp(s_info, s_info, 4u) == 0) \
            lvl_ = 3u;                                                                              \
        else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u)                                   \
            lvl_ = 4u;                                                                              \
        if (lvl_ != 0u) {                                                                           \
            if ((audio_log_flags() & 2u) != 0u)                                                     \
                audio_log_extended(lvl_, s_app, s_path, s_proc_dm, (line), __VA_ARGS__);           \
        } else if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||                               \
                   audio_l2c_strncmp(s_app, s_hci, 3u) != 0) {                                      \
            WsfTrace(s_info, __VA_ARGS__);                                                          \
        }                                                                                           \
    } while (0)

static uint32_t rd32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static void wr32(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)v;
    p[1] = (uint8_t)(v >> 8);
    p[2] = (uint8_t)(v >> 16);
    p[3] = (uint8_t)(v >> 24);
}

void appSlaveResolvedAddrInd_4b3792(const app_dm_hdr_t *msg, app_conn_cb_t *cb)
{
    uint8_t *const slave = audio_ble_subsystem_link_state_200719c8;

    if (slave[APP_SLAVE_IN_PROGRESS] == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, s_module, s_path, s_resolved, 0x270u, s_not_in_progress);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compress_log_output(0x08000000u, s_not_in_progress_short, s_not_in_progress_short);
        return;
    }

    if (msg->status == HCI_SUCCESS) {
        g2_app_slave_peer_resolved = 1u;
        cb->db_hdl = (void *)(uintptr_t)rd32(slave + APP_SLAVE_DB_HDL);
        if (cb->db_hdl != NULL) {
            uint8_t *rec = (uint8_t *)cb->db_hdl;
            uint8_t change_aware;
            uint32_t csf;
            if ((uintptr_t)rec + APP_DB_CCC_TBL != 0u)
                AttsCccInitTable(cb->conn_id, (uint16_t *)(void *)(rec + APP_DB_CCC_TBL));
            audio_ble_pair_record_flags_47b40c((uint32_t)(uintptr_t)rec, &change_aware, &csf);
            AttsCsfConnOpen(cb->conn_id, change_aware, (uint8_t *)(uintptr_t)csf);
            if (change_aware == ATTS_CLIENT_CHANGE_PENDING)
                GattSendServiceChangedInd(cb->conn_id, 1u, 0xffffu);
            uint32_t csrk = audio_ble_link_mask_select_47ae78((uint32_t)(uintptr_t)rec, DM_KEY_CSRK, NULL);
            if (csrk != 0u) {
                AttsSetCsrk(cb->conn_id, (uint8_t *)(uintptr_t)csrk, 0u);
                AttsSetSignCounter(cb->conn_id, rd32((uint8_t *)cb->db_hdl + APP_DB_PEER_SIGN_CNT));
            }
        }
        /* LTK was requested while the master's address was being resolved. */
        if (slave[APP_SLAVE_FIND_LTK] != 0u) {
            audio_ble_slave_resolve_4b36b2(cb);
            slave[APP_SLAVE_FIND_LTK] = 0u;
        }
    } else if (msg->status == HCI_ERR_AUTH_FAILURE && rd32(slave + APP_SLAVE_DB_HDL) != 0u) {
        /* Not resolved: try the IRK of the next bonded record. */
        if (audio_ble_link_mask_select_47ae78(rd32(slave + APP_SLAVE_DB_HDL), DM_KEY_IRK, NULL) != 0u)
            (void)DmConnPeerAddr(cb->conn_id);
        wr32(slave + APP_SLAVE_DB_HDL, audio_ble_pair_record_next_47a630(rd32(slave + APP_SLAVE_DB_HDL)));
        if (rd32(slave + APP_SLAVE_DB_HDL) != 0u) {
            uint32_t irk = audio_ble_link_mask_select_47ae78(rd32(slave + APP_SLAVE_DB_HDL), DM_KEY_IRK, NULL);
            if (irk != 0u) {
                DmPrivResolveAddr(DmConnPeerAddr(cb->conn_id), (const uint8_t *)(uintptr_t)irk, msg->param);
                return; /* not done yet */
            }
        }
    }

    slave[APP_SLAVE_IN_PROGRESS] = 0u;
    if (cb->db_hdl == NULL && audio_ble_comm_profile_slot->initiate_sec != 0u)
        DmSecSlaveReq(cb->conn_id, audio_ble_comm_profile_slot->auth);
}

void AppSlaveProcDmMsg_4b3ca4(const app_dm_hdr_t *msg)
{
    app_conn_cb_t *cb = NULL;
    uint8_t *const slave = audio_ble_subsystem_link_state_200719c8;

    if (msg->event != DM_ADV_STOP_IND && msg->event != DM_ADV_SET_STOP_IND &&
        msg->param != DM_RESET_CMPL_IND && msg->param != DM_HW_ERROR_IND &&
        msg->param != 0u && msg->param < 4u)
        cb = (app_conn_cb_t *)(void *)(audio_ble_atts_connection_rows + (uint32_t)msg->param * 0x30u - 0x30u);

    switch (msg->event) {
    case DM_RESET_CMPL_IND:
        audio_ble_subsystem_child_4b32d4();
        break;

    case DM_ADV_STOP_IND:
    case DM_ADV_SET_STOP_IND: {
        void (*adv_stop_cb)(const app_dm_hdr_t *) =
            (void (*)(const app_dm_hdr_t *))(uintptr_t)rd32(slave + APP_SLAVE_ADV_STOP_CB);
        if (adv_stop_cb != NULL)
            adv_stop_cb(msg);
        break;
    }

    case DM_CONN_OPEN_IND:
        appSlaveConnOpen_4b36fc((void *)(uintptr_t)msg, (uint8_t *)cb);
        break;

    case DM_CONN_CLOSE_IND:
        app_slave_conn_close_4b3720(msg, cb);
        break;

    case DM_CONN_UPDATE_IND:
        break;

    case DM_PRIV_RESOLVED_ADDR_IND:
        appSlaveResolvedAddrInd_4b3792(msg, cb);
        break;

    case DM_REM_CONN_PARAM_REQ_IND:
        app_slave_remote_conn_param_req_4b38f2(msg, cb);
        break;

    case DM_CONN_DATA_LEN_CHANGE_IND: {
        /* hciLeDataLenChangeEvt_t: +6 maxTxOctets, +10 maxRxOctets. */
        const uint16_t *f = (const uint16_t *)(const void *)msg;
        APP_TRACE(0x574u, s_data_len, msg->status, f[5], f[3]);
        break;
    }

    case DM_REMOTE_FEATURES_IND: {
        const uint8_t *features = (const uint8_t *)(const void *)msg + 8u;
        uint8_t dle = features[0] & HCI_LE_SUP_FEAT_DATA_LEN_EXT;
        APP_TRACE(0x55bu, s_remote_feat, features[0], dle);
        if (dle == HCI_LE_SUP_FEAT_DATA_LEN_EXT) {
            APP_TRACE(0x55eu, s_dle_yes);
            DmConnSetDataLen((uint8_t)msg->param, APP_DLE_TX_OCTETS, APP_DLE_TX_TIME_US);
        } else {
            APP_TRACE(0x563u, s_dle_no);
        }
        break;
    }

    case DM_HW_ERROR_IND:
        HciDrvRadioBoot(0u);
        DmDevReset();
        break;

    default:
        break;
    }
}
