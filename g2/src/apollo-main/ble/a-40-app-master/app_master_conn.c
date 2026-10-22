/* Cordio master connection helpers, stock
 * D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-profiles\sources\apps\app\app_master.c.
 * appConnOpen native 0x503d1e..0x503ea1 ("ERR" literal 0x503ea4),
 * AppMasterSecurityReq native 0x503ea8..0x503fef ("APP"/"HCI" literals
 * 0x503ff0/0x503ff8); shared literal pool 0x5040c0..0x50412b.
 *
 * Upstream Cordio (third-party/upstream/cordio ble-profiles/sources/af/app_master.c)
 * with the stock appConnCb lookup check: a zero connection ID logs
 * "Invalid connId in AppMasterConnOpen: %d" through the Ambiq APP_TRACE_WARN1
 * expansion (level by label compare, product logger when the HCI log cell is
 * set, WsfTrace otherwise) and returns. In appConnOpen the check sits behind
 * the connId != DM_CONN_ID_NONE test, so it cannot fire. */
#include <stdint.h>

#define DM_CLIENT_ID_APP 3u
#define APP_CONN_CB_SIZE 0x30u

/* appConnCb_t (48 bytes), array at RAM 0x200717b0. */
typedef struct {
    uint32_t db_hdl;          /* +0x00 */
    uint8_t conn_id;          /* +0x04 */
    uint8_t pad05[3];
    uint8_t initiating_sec;   /* +0x08 */
    uint8_t rest[0x27];
} g2_app_conn_cb_t;
_Static_assert(sizeof(g2_app_conn_cb_t) == APP_CONN_CB_SIZE, "appConnCb_t is 48 bytes");

/* appSecCfg_t: initiateSec at +4. */
typedef struct {
    uint8_t auth;
    uint8_t i_key_dist;
    uint8_t r_key_dist;
    uint8_t oob;
    uint8_t initiate_sec; /* +0x04 */
} g2_app_sec_cfg_t;

extern uint8_t audio_ble_discovery_connection_records_200717b0[]; /* appConnCb[DM_CONN_MAX] */
extern const g2_app_sec_cfg_t *g2_app_sec_cfg;                 /* RAM 0x20074358 pAppSecCfg */

extern uint8_t DmConnOpen(uint8_t client_id, uint8_t init_phys, uint8_t addr_type,
                          const uint8_t *addr); /* 0x55bcc0 */
extern uint32_t AppDbRecordInUse_47a5d0(uint32_t db_hdl);
extern uint32_t audio_ble_pair_record_find_47ad74(uint32_t addr_type, const void *addr); /* AppDbFindByAddr */
extern uint8_t audio_ble_dm_sec_level_4b71b2(uint8_t conn_id); /* DmConnSecLevel */
extern void audio_ble_master_row_dispatch_503498(uint32_t conn_id, uint32_t initiate_pairing,
                                                 void *conn_cb); /* appMasterInitiateSec */
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *, const char *, uint32_t); /* 0x44b610 */
extern void audio_ble_wsf_trace(const char *, const char *, ...); /* WsfTrace 0x52a63c */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */

static const char error_label[] = "ERR";  /* ROM 0x503ea4 and 0x5040c0 */
static const char info_label[] = "INFO";  /* ROM 0x78cb34 */
static const char warn_label[] = "WARN";  /* ROM 0x78cb3c */
static const char app_label[] = "APP";    /* ROM 0x503ff0 */
static const char hci_label[] = "HCI";    /* ROM 0x503ff8 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_master.c"; /* ROM 0x6da098 */
static const char conn_open_fn[] = "appConnOpen"; /* ROM 0x78a2bc */
static const char security_req_fn[] = "AppMasterSecurityReq"; /* ROM 0x7754ac */
static const char invalid_conn_id[] = "Invalid connId in AppMasterConnOpen: %d"; /* ROM 0x747a1c */

/* APP_TRACE_WARN1(invalid_conn_id, conn_id) as expanded by the stock build. */
static void trace_invalid_conn_id(const char *fn, uint32_t line, uint8_t conn_id)
{
    uint8_t level;

    if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
        audio_l2c_strncmp(warn_label, error_label, 3u) == 0)
        level = 1u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
             audio_l2c_strncmp(warn_label, warn_label, 4u) == 0)
        level = 2u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
             audio_l2c_strncmp(warn_label, info_label, 4u) == 0)
        level = 3u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u)
        level = 4u;
    else {
        if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
            audio_l2c_strncmp(app_label, hci_label, 3u) != 0)
            audio_ble_wsf_trace(warn_label, invalid_conn_id, conn_id);
        return;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(level, app_label, source_file, fn, line, invalid_conn_id, conn_id);
}

static g2_app_conn_cb_t *conn_cb(uint8_t conn_id)
{
    return (g2_app_conn_cb_t *)&audio_ble_discovery_connection_records_200717b0
        [(uint32_t)conn_id * APP_CONN_CB_SIZE - APP_CONN_CB_SIZE];
}

uint8_t appConnOpen_503d1e(uint8_t init_phys, uint8_t addr_type, uint8_t *addr, uint32_t db_hdl)
{
    uint8_t conn_id = DmConnOpen(DM_CLIENT_ID_APP, init_phys, addr_type, addr);

    if (conn_id != 0u) {
        if (conn_id == 0u) {
            trace_invalid_conn_id(conn_open_fn, 0x37eu, conn_id);
            return 0u;
        }
        g2_app_conn_cb_t *cb = conn_cb(conn_id);
        cb->conn_id = conn_id;
        if (db_hdl != 0u && AppDbRecordInUse_47a5d0(db_hdl) != 0u)
            cb->db_hdl = db_hdl;
        else
            cb->db_hdl = audio_ble_pair_record_find_47ad74(addr_type, addr);
    }
    return conn_id;
}

/* Starts pairing unless security is already configured to start, in progress, or present. */
void AppMasterSecurityReq_503ea8(uint8_t conn_id)
{
    if (conn_id == 0u) {
        trace_invalid_conn_id(security_req_fn, 0x3a5u, conn_id);
        return;
    }
    g2_app_conn_cb_t *cb = conn_cb(conn_id);
    if (g2_app_sec_cfg->initiate_sec == 0u && cb->initiating_sec == 0u &&
        audio_ble_dm_sec_level_4b71b2(conn_id) == 0u)
        audio_ble_master_row_dispatch_503498(conn_id, 1u, cb);
}
