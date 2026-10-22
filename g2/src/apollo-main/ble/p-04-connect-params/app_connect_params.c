/* BLE peripheral connection-parameter manager, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_connect_params.c (tag "ble.param").
 * Native _bleSlaveConnUpdate 0x476cbc, _bleConnParaConnectEvt 0x477774,
 * _connUpdateFinishInd 0x477adc, APP_ConnectParamOTASetFastMode 0x4781f4 and
 * APP_ConnectParamHandler 0x4782dc; literal pools 0x477740, 0x477a6c,
 * 0x478270 and 0x4786b4.
 *
 * Modes are the custom WSF events EVEN_CONN_PARAMS_FAST (0xa3) and
 * EVEN_CONN_PARAMS_SLOW (0xa4). Requests are deferred through the firmware
 * event loop to _connectParamReq (0x47761c), which posts
 * EVEN_SLAVE_CONN_PARAM_REQ (0xb9) back to this handler. The remaining
 * functions of this stock file (_isConnParamsFast/Slow, _connectParamReq_impl,
 * _connectParamReq, ble_msgtx_*, APP_ConnectParamESSSetFastMode) are defined in
 * g2/src/apollo-main/ble/ble-conn, ble-connect, ble-slave, ble-connected and ble-fast. */
#include <stdint.h>
#include <stddef.h>

enum {
    MODE_FAST = 0xa3u,                 /* EVEN_CONN_PARAMS_FAST */
    MODE_SLOW = 0xa4u,                 /* EVEN_CONN_PARAMS_SLOW */
    EVT_SLAVE_CONN_PARAM_REQ = 0xb9u,  /* EVEN_SLAVE_CONN_PARAM_REQ */
    DM_CONN_OPEN_IND = 0x27u,
    DM_CONN_CLOSE_IND = 0x28u,
    DM_CONN_UPDATE_IND = 0x29u,
    DM_REM_CONN_PARAM_REQ_IND = 0x40u,
    DM_ROLE_SLAVE = 1u,
    HCI_ERR_CMD_DISALLOWED = 0x0cu,
    HCI_ERR_UNACCEPT_CONN_INTERVAL = 0x3bu,
    PHONE_ANDROID = 4u,
    APP_CONN_MAX = 3u,
};

/* Fast/slow classification in 1.25 ms units (see _isConnParamsFast/Slow). */
#define FAST_LIMIT_FIRST_CONNECT 25
#define FAST_LIMIT_DEFAULT 72

/* wsfMsgHdr_t */
typedef struct {
    uint16_t param;  /* +0 connection id */
    uint8_t event;   /* +2 */
    uint8_t status;  /* +3 */
} g2_wsf_msg_hdr_t;

/* hciLeConnCmplEvt_t */
typedef struct {
    g2_wsf_msg_hdr_t hdr;    /* +0x00 */
    uint8_t status;          /* +0x04 */
    uint16_t handle;         /* +0x06 */
    uint8_t role;            /* +0x08 */
    uint8_t addr_type;       /* +0x09 */
    uint8_t peer_addr[6];    /* +0x0a */
    uint16_t conn_interval;  /* +0x10 */
    uint16_t conn_latency;   /* +0x12 */
    uint16_t sup_timeout;    /* +0x14 */
} g2_hci_conn_cmpl_evt_t;
_Static_assert(offsetof(g2_hci_conn_cmpl_evt_t, conn_interval) == 0x10, "hciLeConnCmplEvt_t");

/* hciLeConnUpdateCmplEvt_t */
typedef struct {
    g2_wsf_msg_hdr_t hdr;    /* +0x00 */
    uint8_t status;          /* +0x04 */
    uint16_t handle;         /* +0x06 */
    uint16_t conn_interval;  /* +0x08 */
    uint16_t conn_latency;   /* +0x0a */
    uint16_t sup_timeout;    /* +0x0c */
} g2_hci_conn_update_evt_t;

/* hciLeRemConnParamReqEvt_t */
typedef struct {
    g2_wsf_msg_hdr_t hdr;    /* +0x00 */
    uint16_t handle;         /* +0x04 */
    uint16_t interval_min;   /* +0x06 */
    uint16_t interval_max;   /* +0x08 */
    uint16_t latency;        /* +0x0a */
    uint16_t timeout;        /* +0x0c */
} g2_hci_rem_conn_param_req_evt_t;

/* 12-byte EVEN_SLAVE_CONN_PARAM_REQ message built by _connectParamReq. */
typedef struct {
    g2_wsf_msg_hdr_t hdr;    /* +0x00 */
    uint8_t reserved[4];     /* +0x04 */
    uint16_t mode;           /* +0x08 */
} g2_conn_param_req_msg_t;

/* appUpdateCfg_t-shaped 16-byte ROM profiles at 0x784ea0/0x784eb0/0x784ec0. */
typedef struct {
    uint32_t idle_period;        /* +0x00 */
    uint16_t conn_interval_min;  /* +0x04 */
    uint16_t conn_interval_max;  /* +0x06 */
    uint16_t conn_latency;       /* +0x08 */
    uint16_t sup_timeout;        /* +0x0a */
    uint8_t max_attempts;        /* +0x0c */
} g2_conn_profile_t;
_Static_assert(sizeof(g2_conn_profile_t) == 16, "profile record is 16 bytes");

/* Cordio appConnCb_t (0x30 bytes per connection, array at RAM 0x200717b0). */
typedef struct {
    void *db_handle;          /* +0x00 */
    uint8_t conn_id;          /* +0x04 */
    uint8_t bonded;           /* +0x05 */
    uint8_t bond_by_ltk;      /* +0x06 */
    uint8_t bond_by_pairing;  /* +0x07 */
    uint8_t initiating_sec;   /* +0x08 */
    uint8_t set_connectable;  /* +0x09 */
    uint8_t conn_was_idle;    /* +0x0a */
    uint8_t rcvd_keys;        /* +0x0b */
    uint8_t attempts;         /* +0x0c */
    uint8_t rest[0x23];       /* +0x0d */
} g2_app_conn_cb_t;
_Static_assert(sizeof(g2_app_conn_cb_t) == 0x30, "appConnCb_t stride");

/* Live parameter record behind the pointer cell 0x2007433c. */
typedef struct {
    uint8_t head[0x18];
    uint16_t conn_interval;  /* +0x18 */
    uint16_t conn_latency;   /* +0x1a */
    uint16_t sup_timeout;    /* +0x1c */
    uint8_t is_fast;         /* +0x1e */
} g2_conn_param_state_t;

/* hciConnSpec_t */
typedef struct {
    uint16_t conn_interval_min;
    uint16_t conn_interval_max;
    uint16_t conn_latency;
    uint16_t sup_timeout;
    uint16_t min_ce_len;
    uint16_t max_ce_len;
} g2_hci_conn_spec_t;

extern volatile uint8_t audio_ble_requested_conn_mode;             /* RAM 0x20004541 sCurrentParamsHopeUpdataMode */
extern volatile uint8_t audio_ble_current_conn_mode;               /* RAM 0x20004542 */
extern volatile uint8_t audio_tracepoint_pull_connection_flag_20074f8f; /* RAM 0x20074f8f sFirstConnectFlag */
extern volatile uint8_t audio_ble_fast_mode_throttle_enabled;      /* RAM 0x20074f90 */
extern volatile uint8_t audio_ble_connect_request_pending;         /* RAM 0x20074f91 */
extern uint32_t audio_ble_fast_mode_last_reject_tick;              /* RAM 0x20074340 */
extern uint8_t *audio_ble_cached_conn_params;                      /* RAM 0x2007433c pointer cell */
extern const uint8_t *audio_ble_msgtx_table_slot;                  /* RAM 0x2007435c selected profile */
extern uint8_t audio_ble_discovery_connection_records_200717b0[];  /* RAM 0x200717b0 appConnCb[] */
extern const uint8_t audio_ble_conn_param_slow_profile_784ea0[16]; /* ROM 0x784ea0 72..84, lat 4, 6 s */
extern const uint8_t audio_ble_msgtx_table[16];                    /* ROM 0x784eb0 iOS fast 12..24 */
extern const uint8_t audio_ble_conn_param_fast_profile_784ec0[16]; /* ROM 0x784ec0 Android fast 12..24 */

extern uint16_t DmConnCheckIdle(uint8_t conn_id);                  /* 0x4b73a2 */
extern void DmConnUpdate(uint8_t conn_id, g2_hci_conn_spec_t *spec); /* 0x4b6d26 */
extern uint8_t DmConnRole(uint8_t conn_id);                        /* 0x4b73c4 */
extern void *dmGetConnParamPtr(void);                              /* 0x46efcc */
extern uint32_t settings_get_terminal_mode(void);                  /* 0x46c630 */
extern uint32_t osKernelGetTickCount(void);                        /* 0x4490cc */
extern uint8_t app_ble_phone_type_get_4b8128(void);                /* byte at RAM 0x200737b0 */
extern uint32_t audio_ble_is_conn_params_slow(const void *params);  /* _isConnParamsSlow 0x476fe2 */
extern void audio_ble_connect_param_request(uint8_t mode);         /* _connectParamReq 0x47761c */
extern void audio_ble_connect_param_request_impl(uint8_t mode);    /* _connectParamReq_impl 0x47720c */
extern uint32_t audio_event_loop_remove_delayed(void (*)(void));   /* fw_event_loop_remove_delayed 0x476ace */
extern void audio_event_loop_push_delayed(void (*)(void), uint32_t, uint32_t); /* fw_event_loop_push_delayed 0x47697e */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "ble.param"; /* ROM 0x78a0b8 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_connect_params.c"; /* ROM 0x6f81bc */
static const char slave_update_fn[] = "_bleSlaveConnUpdate";        /* ROM 0x77dce0 */
static const char connect_evt_fn[] = "_bleConnParaConnectEvt";      /* ROM 0x774fcc */
static const char update_finish_fn[] = "_connUpdateFinishInd";      /* ROM 0x774ffc */
static const char ota_fast_fn[] = "APP_ConnectParamOTASetFastMode"; /* ROM 0x75dd10 */
static const char handler_fn[] = "APP_ConnectParamHandler";         /* ROM 0x775014 */

static const char mode_fast[] = "fast"; /* ROM 0x78ca04 */
static const char mode_slow[] = "slow"; /* ROM 0x78ca0c */

static const char check_idle[] = "DmConnCheckIdle %d, %d, 0x%x"; /* ROM 0x75dc50 */
static const char check_idle_short[] = "[ble.param]DmConnCheckIdle %d, %d, 0x%x"; /* ROM 0x74756c */
static const char opened[] = "connection opened"; /* ROM 0x77dd58 */
static const char opened_short[] = "[ble.param]connection opened"; /* ROM 0x75dcd0 */
static const char handle_msg[] = "handle = 0x%x"; /* ROM 0x784e80 */
static const char handle_short[] = "[ble.param]handle = 0x%x"; /* ROM 0x769200 */
static const char role_msg[] = "role = 0x%x"; /* ROM 0x78a0c4 */
static const char role_short[] = "[ble.param]role = 0x%x"; /* ROM 0x774fe4 */
static const char peer_msg[] = "peer addr = %02x%02x%02x%02x%02x%02x"; /* ROM 0x747594 */
static const char peer_short[] = "[ble.param]peer addr = %02x%02x%02x%02x%02x%02x"; /* ROM 0x731664 */
static const char interval_msg[] = "connInterval = %d ms"; /* ROM 0x774fb4 */
static const char interval_short[] = "[ble.param]connInterval = %d ms"; /* ROM 0x75dcb0 */
static const char latency_msg[] = "connLatency = %d"; /* ROM 0x77dd08 */
static const char latency_short[] = "[ble.param]connLatency = %d"; /* ROM 0x7691e4 */
static const char timeout_msg[] = "supTimeout = %d ms"; /* ROM 0x77dd1c */
static const char timeout_short[] = "[ble.param]supTimeout = %d ms"; /* ROM 0x75dc90 */
static const char opened_mode[] = "connection opened conn_params %d is %s"; /* ROM 0x7475bc */
static const char opened_mode_short[] = "[ble.param]connection opened conn_params %d is %s"; /* ROM 0x726bb4 */
static const char update_status[] = "connection update status = 0x%x role = %d(0=master)"; /* ROM 0x726be8 */
static const char update_status_short[] =
    "[ble.param]connection update status = 0x%x role = %d(0=master)"; /* ROM 0x708f24 */
static const char new_params[] = "new:%d,%d(%d)"; /* ROM 0x784e90 */
static const char new_params_short[] = "[ble.param]new:%d,%d(%d)"; /* ROM 0x76921c */
static const char hope_mode[] = "conn_params update_event sCurrentParamsHopeUpdataMode=%s"; /* ROM 0x712424 */
static const char hope_mode_short[] =
    "[ble.param]conn_params update_event sCurrentParamsHopeUpdataMode=%s"; /* ROM 0x7000a0 */
static const char new_vs_slow[] = "  new:%d,%d(%d)  slow:%d,%d(%d)"; /* ROM 0x75dc70 */
static const char new_vs_slow_short[] = "[ble.param]  new:%d,%d(%d)  slow:%d,%d(%d)"; /* ROM 0x73bf88 */
static const char update_failed[] = "Connection parameter update failed/rejected with status 0x%02x"; /* ROM 0x708f64 */
static const char update_failed_short[] =
    "[ble.param]Connection parameter update failed/rejected with status 0x%02x"; /* ROM 0x6f1684 */
static const char peer_rejected[] =
    "Connection parameter update rejected by peer (status=0x%02x), will retry after 30s"; /* ROM 0x6e6184 */
static const char peer_rejected_short[] =
    "[ble.param]Connection parameter update rejected by peer (status=0x%02x), will retry after 30s"; /* ROM 0x6dc3f4 */
static const char mode_fail[] = "conn_params update %s fail xxxxxxxxxxx"; /* ROM 0x7475e4 */
static const char mode_fail_short[] = "[ble.param]conn_params update %s fail xxxxxxxxxxx"; /* ROM 0x726c1c */
static const char retry_30s[] = "Connection parameter update failed, will retry after 30s"; /* ROM 0x712460 */
static const char retry_30s_short[] =
    "[ble.param]Connection parameter update failed, will retry after 30s"; /* ROM 0x7000e4 */
static const char mode_ok[] = "conn_params update %s ok *********"; /* ROM 0x751cf8 */
static const char mode_ok_short[] = "[ble.param]conn_params update %s ok *********"; /* ROM 0x731694 */
static const char first_connect[] = "--> sFirstConnectFlag sCurrentParamsHopeUpdataMode = %d"; /* ROM 0x71be40 */
static const char first_connect_short[] =
    "[ble.param]--> sFirstConnectFlag sCurrentParamsHopeUpdataMode = %d"; /* ROM 0x700128 */
static const char ota_fast_msg[] = "APP_ConnectParamOTASetFastMode"; /* ROM 0x75dd30 */
static const char ota_fast_short[] = "[ble.param]APP_ConnectParamOTASetFastMode"; /* ROM 0x73bfe0 */
static const char fast_invalid[] = "EVEN_CONN_PARAMS_FAST: invalid connId %d, skip"; /* ROM 0x7316c4 */
static const char fast_invalid_short[] = "[ble.param]EVEN_CONN_PARAMS_FAST: invalid connId %d, skip"; /* ROM 0x71249c */
static const char fast_msg[] = "EVEN_CONN_PARAMS_FAST pMsg---->0x%x"; /* ROM 0x751d1c */
static const char fast_msg_short[] = "[ble.param]EVEN_CONN_PARAMS_FAST pMsg---->0x%x"; /* ROM 0x7316f4 */
static const char android_fast[] = "android conn_params set fast %d %d ##############"; /* ROM 0x726c50 */
static const char android_fast_short[] = "[ble.param]android conn_params set fast %d %d ##############"; /* ROM 0x708fa4 */
static const char ios_fast[] = "IOS conn_params set fast %d %d ##############"; /* ROM 0x731724 */
static const char ios_fast_short[] = "[ble.param]IOS conn_params set fast %d %d ##############"; /* ROM 0x7124d8 */
static const char slow_invalid[] = "EVEN_CONN_PARAMS_SLOW: invalid connId %d, skip"; /* ROM 0x731754 */
static const char slow_invalid_short[] = "[ble.param]EVEN_CONN_PARAMS_SLOW: invalid connId %d, skip"; /* ROM 0x712514 */
static const char slow_msg[] = "EVEN_CONN_PARAMS_SLOW pMsg---->0x%x"; /* ROM 0x751d40 */
static const char slow_msg_short[] = "[ble.param]EVEN_CONN_PARAMS_SLOW pMsg---->0x%x"; /* ROM 0x731784 */
static const char set_slow[] = "conn_params set slow %d %d @@@@@@@@@@@@@@@"; /* ROM 0x73c00c */
static const char set_slow_short[] = "[ble.param]conn_params set slow %d %d @@@@@@@@@@@@@@@"; /* ROM 0x71be78 */
static const char peer_initiator[] = "connect params updata is peer initiator"; /* ROM 0x74760c */
static const char peer_initiator_short[] = "[ble.param]connect params updata is peer initiator"; /* ROM 0x726c84 */
static const char rem_param_req[] = "DM_REM_CONN_PARAM_REQ_IND, [Min Max] = [%d, %d] %d,%d"; /* ROM 0x71beb0 */
static const char rem_param_req_short[] =
    "[ble.param]DM_REM_CONN_PARAM_REQ_IND, [Min Max] = [%d, %d] %d,%d"; /* ROM 0x70016c */
static const char slave_req[] = "EVEN_SLAVE_CONN_PARAM_REQ mode = %d"; /* ROM 0x751d64 */
static const char slave_req_short[] = "[ble.param]EVEN_SLAVE_CONN_PARAM_REQ mode = %d"; /* ROM 0x7317b4 */

#define PARAM_LOG(level, mask, fn, line, fmt, short_fmt, ...)                                \
    do {                                                                                     \
        if (audio_log_flags() & 2u)                                                          \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (fmt), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                            \
            (void)compress_log_output((mask), (short_fmt), (short_fmt), ##__VA_ARGS__);      \
    } while (0)

#define MODE_NAME(mode) ((mode) == MODE_FAST ? mode_fast : mode_slow)
#define CONNECT_PARAM_REQ ((void (*)(void))audio_ble_connect_param_request)

static g2_conn_param_state_t *param_state(void)
{
    return (g2_conn_param_state_t *)(void *)audio_ble_cached_conn_params;
}

static const g2_conn_profile_t *selected_profile(void)
{
    return (const g2_conn_profile_t *)(const void *)audio_ble_msgtx_table_slot;
}

/* Submits the selected profile once the link has been idle for two consecutive
 * checks; otherwise records the idle state and re-arms _connectParamReq after
 * 2 s (fast) or 4 s (slow). */
void _bleSlaveConnUpdate(uint8_t mode, g2_app_conn_cb_t *cb)
{
    uint8_t idle = DmConnCheckIdle(cb->conn_id) == 0u;

    PARAM_LOG(4u, 0x10c00000u, slave_update_fn, 0xa0u, check_idle, check_idle_short,
              idle, cb->conn_was_idle, DmConnCheckIdle(cb->conn_id));
    if (idle && cb->conn_was_idle) {
        g2_hci_conn_spec_t spec;
        cb->attempts++;
        spec.conn_interval_min = selected_profile()->conn_interval_min;
        spec.conn_interval_max = selected_profile()->conn_interval_max;
        spec.conn_latency = selected_profile()->conn_latency;
        spec.sup_timeout = selected_profile()->sup_timeout;
        spec.min_ce_len = 0u;
        spec.max_ce_len = 0xffffu;
        DmConnUpdate(cb->conn_id, &spec);
    } else {
        cb->conn_was_idle = idle;
        (void)audio_event_loop_remove_delayed(CONNECT_PARAM_REQ);
        audio_event_loop_push_delayed(CONNECT_PARAM_REQ, mode, mode == MODE_FAST ? 2000u : 4000u);
    }
}

/* DM_CONN_OPEN_IND as peripheral: cache the link parameters, classify them and
 * schedule the one-minute move to slow mode unless terminal mode is set. */
void _bleConnParaConnectEvt(const g2_hci_conn_cmpl_evt_t *evt)
{
    PARAM_LOG(4u, 0x10000000u, connect_evt_fn, 0x141u, opened, opened_short);
    PARAM_LOG(4u, 0x10400000u, connect_evt_fn, 0x142u, handle_msg, handle_short, evt->handle);
    PARAM_LOG(4u, 0x10400000u, connect_evt_fn, 0x143u, role_msg, role_short, evt->role);
    PARAM_LOG(4u, 0x11800000u, connect_evt_fn, 0x144u, peer_msg, peer_short,
              evt->peer_addr[5], evt->peer_addr[4], evt->peer_addr[3],
              evt->peer_addr[2], evt->peer_addr[1], evt->peer_addr[0]);
    PARAM_LOG(4u, 0x10400000u, connect_evt_fn, 0x145u, interval_msg, interval_short,
              evt->conn_interval * 1250 / 1000);
    PARAM_LOG(4u, 0x10400000u, connect_evt_fn, 0x146u, latency_msg, latency_short, evt->conn_latency);
    PARAM_LOG(4u, 0x10400000u, connect_evt_fn, 0x147u, timeout_msg, timeout_short,
              evt->sup_timeout * 10000 / 1000);

    param_state()->conn_interval = evt->conn_interval;
    param_state()->conn_latency = evt->conn_latency;
    param_state()->sup_timeout = evt->sup_timeout;
    audio_ble_current_conn_mode = (uint8_t)audio_ble_is_conn_params_slow(param_state());
    audio_ble_requested_conn_mode = audio_ble_current_conn_mode;
    audio_tracepoint_pull_connection_flag_20074f8f = 1u;

    PARAM_LOG(4u, 0x10800000u, connect_evt_fn, 0x14eu, opened_mode, opened_mode_short,
              evt->conn_interval, MODE_NAME(audio_ble_current_conn_mode));
    (void)audio_event_loop_remove_delayed(CONNECT_PARAM_REQ);
    if (settings_get_terminal_mode() == 0u)
        audio_event_loop_push_delayed(CONNECT_PARAM_REQ, MODE_SLOW, 60000u);
}

/* DM_CONN_UPDATE_IND. As peripheral: accept the update if it reached the
 * requested mode, otherwise retry (30 s after a peer rejection 0x0c/0x3b,
 * 10 s after another failure status, 2/4 s after a wrong-mode success). While
 * the first-connect flag is set, a reached fast mode re-arms the 60 s slow move. */
void _connUpdateFinishInd(const g2_hci_conn_update_evt_t *evt)
{
    uint8_t conn_id = (uint8_t)evt->hdr.param;
    uint8_t rejected;
    uint8_t reached;

    (void)dmGetConnParamPtr();
    PARAM_LOG(4u, 0x10800000u, update_finish_fn, 0x161u, update_status, update_status_short,
              evt->status, DmConnRole(conn_id));
    PARAM_LOG(4u, 0x10c00000u, update_finish_fn, 0x162u, new_params, new_params_short,
              evt->conn_interval, evt->conn_interval, evt->conn_latency);
    PARAM_LOG(4u, 0x10400000u, update_finish_fn, 0x163u, interval_msg, interval_short,
              evt->conn_interval * 1250 / 1000);
    PARAM_LOG(4u, 0x10400000u, update_finish_fn, 0x164u, latency_msg, latency_short, evt->conn_latency);
    PARAM_LOG(4u, 0x10400000u, update_finish_fn, 0x165u, timeout_msg, timeout_short,
              evt->sup_timeout * 10000 / 1000);
    if (DmConnRole(conn_id) != DM_ROLE_SLAVE)
        return;

    const g2_conn_profile_t *slow = (const g2_conn_profile_t *)(const void *)audio_ble_conn_param_slow_profile_784ea0;
    PARAM_LOG(4u, 0x10400000u, update_finish_fn, 0x169u, hope_mode, hope_mode_short,
              MODE_NAME(audio_ble_requested_conn_mode));
    PARAM_LOG(4u, 0x11800000u, update_finish_fn, 0x16au, new_vs_slow, new_vs_slow_short,
              evt->conn_interval, evt->conn_interval, evt->conn_latency,
              slow->conn_interval_min, slow->conn_interval_max, slow->conn_latency);

    rejected = 0u;
    if (evt->status != 0u) {
        rejected = 1u;
        PARAM_LOG(2u, 0x08400000u, update_finish_fn, 0x172u, update_failed, update_failed_short, evt->status);
        if (evt->status == HCI_ERR_CMD_DISALLOWED || evt->status == HCI_ERR_UNACCEPT_CONN_INTERVAL) {
            PARAM_LOG(2u, 0x08400000u, update_finish_fn, 0x177u, peer_rejected, peer_rejected_short,
                      evt->status);
            audio_ble_fast_mode_last_reject_tick = osKernelGetTickCount();
            audio_ble_fast_mode_throttle_enabled = 1u;
            audio_ble_connect_request_pending = 0u;
            (void)audio_event_loop_remove_delayed(CONNECT_PARAM_REQ);
            audio_event_loop_push_delayed(CONNECT_PARAM_REQ, audio_ble_requested_conn_mode, 30000u);
            return;
        }
    }

    if (audio_tracepoint_pull_connection_flag_20074f8f != 0u)
        reached = (int)evt->conn_interval < FAST_LIMIT_DEFAULT ? MODE_FAST : MODE_SLOW;
    else
        reached = (int)evt->conn_interval < FAST_LIMIT_FIRST_CONNECT ? MODE_FAST : MODE_SLOW;

    if (reached == audio_ble_requested_conn_mode) {
        param_state()->conn_interval = evt->conn_interval;
        param_state()->conn_latency = evt->conn_latency;
        param_state()->sup_timeout = evt->sup_timeout;
        audio_ble_current_conn_mode = audio_ble_requested_conn_mode;
        param_state()->is_fast = audio_ble_requested_conn_mode == MODE_FAST;
        PARAM_LOG(3u, 0x0c400000u, update_finish_fn, 0x1a5u, mode_ok, mode_ok_short,
                  MODE_NAME(audio_ble_requested_conn_mode));
        audio_ble_fast_mode_throttle_enabled = 0u;
        audio_ble_connect_request_pending = 0u;
    } else {
        PARAM_LOG(1u, 0x04400000u, update_finish_fn, 0x18du, mode_fail, mode_fail_short,
                  MODE_NAME(audio_ble_requested_conn_mode));
        if (rejected) {
            /* The message says 30 s; the stock delay is 10 s. */
            PARAM_LOG(2u, 0x08000000u, update_finish_fn, 0x191u, retry_30s, retry_30s_short);
            audio_ble_fast_mode_last_reject_tick = osKernelGetTickCount();
            audio_ble_fast_mode_throttle_enabled = 1u;
            audio_ble_connect_request_pending = 0u;
            (void)audio_event_loop_remove_delayed(CONNECT_PARAM_REQ);
            audio_event_loop_push_delayed(CONNECT_PARAM_REQ, audio_ble_requested_conn_mode, 10000u);
        } else {
            audio_ble_fast_mode_throttle_enabled = 0u;
            audio_ble_connect_request_pending = 0u;
            (void)audio_event_loop_remove_delayed(CONNECT_PARAM_REQ);
            audio_event_loop_push_delayed(CONNECT_PARAM_REQ, audio_ble_requested_conn_mode,
                                          audio_ble_requested_conn_mode == MODE_FAST ? 2000u : 4000u);
        }
    }

    if (audio_tracepoint_pull_connection_flag_20074f8f != 0u) {
        PARAM_LOG(4u, 0x10400000u, update_finish_fn, 0x1adu, first_connect, first_connect_short,
                  audio_ble_requested_conn_mode);
        if (audio_ble_requested_conn_mode == MODE_SLOW) {
            audio_tracepoint_pull_connection_flag_20074f8f = 0u;
        } else {
            (void)audio_event_loop_remove_delayed(CONNECT_PARAM_REQ);
            audio_event_loop_push_delayed(CONNECT_PARAM_REQ, MODE_SLOW, 60000u);
        }
    }
}

/* OTA start: clear the first-connect flag and request fast mode immediately
 * (no rejection throttle, unlike APP_ConnectParamESSSetFastMode). */
void APP_ConnectParamOTASetFastMode(void)
{
    PARAM_LOG(4u, 0x10000000u, ota_fast_fn, 499u, ota_fast_msg, ota_fast_short);
    audio_tracepoint_pull_connection_flag_20074f8f = 0u;
    (void)audio_event_loop_remove_delayed(CONNECT_PARAM_REQ);
    audio_event_loop_push_delayed(CONNECT_PARAM_REQ, MODE_FAST, 0u);
}

/* WSF handler for DM connection events and the EVEN_* parameter events. */
void APP_ConnectParamHandler(uint8_t event, const g2_wsf_msg_hdr_t *msg)
{
    (void)event;
    if (msg == NULL)
        return;

    g2_app_conn_cb_t *cb = NULL;
    if (msg->param != 0u && msg->param < APP_CONN_MAX + 1u)
        cb = (g2_app_conn_cb_t *)(void *)audio_ble_discovery_connection_records_200717b0 + (msg->param - 1u);

    switch (msg->event) {
    case DM_CONN_OPEN_IND:
        if (DmConnRole((uint8_t)msg->param) == DM_ROLE_SLAVE)
            _bleConnParaConnectEvt((const g2_hci_conn_cmpl_evt_t *)(const void *)msg);
        break;
    case DM_CONN_CLOSE_IND:
        (void)audio_event_loop_remove_delayed(CONNECT_PARAM_REQ);
        audio_ble_connect_request_pending = 0u;
        break;
    case DM_CONN_UPDATE_IND:
        _connUpdateFinishInd((const g2_hci_conn_update_evt_t *)(const void *)msg);
        break;
    case DM_REM_CONN_PARAM_REQ_IND: {
        const g2_hci_rem_conn_param_req_evt_t *req = (const g2_hci_rem_conn_param_req_evt_t *)(const void *)msg;
        PARAM_LOG(4u, 0x10000000u, handler_fn, 0x23eu, peer_initiator, peer_initiator_short);
        PARAM_LOG(4u, 0x11000000u, handler_fn, 0x243u, rem_param_req, rem_param_req_short,
                  req->interval_min, req->interval_max, req->latency, req->timeout);
        break;
    }
    case MODE_FAST:
        if (cb == NULL) {
            PARAM_LOG(1u, 0x04400000u, handler_fn, 0x20eu, fast_invalid, fast_invalid_short, msg->param);
            audio_ble_connect_request_pending = 0u;
            break;
        }
        PARAM_LOG(4u, 0x10400000u, handler_fn, 0x212u, fast_msg, fast_msg_short, msg);
        if (app_ble_phone_type_get_4b8128() == PHONE_ANDROID) {
            audio_ble_msgtx_table_slot = audio_ble_conn_param_fast_profile_784ec0;
            PARAM_LOG(4u, 0x10800000u, handler_fn, 0x215u, android_fast, android_fast_short,
                      selected_profile()->conn_interval_min, selected_profile()->conn_interval_max);
            _bleSlaveConnUpdate(MODE_FAST, cb);
        } else {
            audio_ble_msgtx_table_slot = audio_ble_msgtx_table;
            PARAM_LOG(4u, 0x10800000u, handler_fn, 0x219u, ios_fast, ios_fast_short,
                      selected_profile()->conn_interval_min, selected_profile()->conn_interval_max);
            _bleSlaveConnUpdate(MODE_FAST, cb);
        }
        audio_ble_requested_conn_mode = MODE_FAST;
        break;
    case MODE_SLOW:
        if (cb == NULL) {
            PARAM_LOG(1u, 0x04400000u, handler_fn, 0x222u, slow_invalid, slow_invalid_short, msg->param);
            audio_ble_connect_request_pending = 0u;
            break;
        }
        PARAM_LOG(4u, 0x10400000u, handler_fn, 0x226u, slow_msg, slow_msg_short, msg);
        audio_ble_msgtx_table_slot = audio_ble_conn_param_slow_profile_784ea0;
        PARAM_LOG(4u, 0x10800000u, handler_fn, 0x228u, set_slow, set_slow_short,
                  selected_profile()->conn_interval_min, selected_profile()->conn_interval_max);
        _bleSlaveConnUpdate(MODE_SLOW, cb);
        audio_ble_requested_conn_mode = MODE_SLOW;
        break;
    case EVT_SLAVE_CONN_PARAM_REQ: {
        uint8_t mode = (uint8_t)((const g2_conn_param_req_msg_t *)(const void *)msg)->mode;
        PARAM_LOG(4u, 0x10400000u, handler_fn, 0x249u, slave_req, slave_req_short, mode);
        audio_ble_connect_param_request_impl(mode);
        break;
    }
    default:
        break;
    }
}
