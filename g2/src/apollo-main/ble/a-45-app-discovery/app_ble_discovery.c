/* Product GATT discovery state machine, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble_discovery.c.
 * Native 0x5355e0..0x53609b APP_BleServerDiscCback (registered with
 * AppDiscRegister in app_ble_startup.c); literal pool 0x53609c..0x53618b.
 * APP_StartServiceDiscovery 0x5354c2 from the same file is
 * ble/ble-service/display_ble_service_discovery_enqueue.c.
 *
 * Role 0 (master) is the ring link: ring handles state[0..4], GATT handles
 * via row 4, then the ring service, then two CCC writes. Role 1 (slave) is
 * the phone link: handles from state+0x2a (8), GATT, then ANCS (if the ANCS
 * discovery starts), then four CCC writes. state+0x57 is discState and
 * state+0x5a the ANCS retry counter. */
#include <stdint.h>

/* Cordio app_api.h discovery status values in this build */
enum {
    APP_DISC_INIT = 0u, APP_DISC_READ_DATABASE_HASH = 1u, APP_DISC_SEC_REQUIRED = 2u,
    APP_DISC_START = 3u, APP_DISC_CMPL = 4u, APP_DISC_FAILED = 5u, APP_DISC_CFG_START = 6u,
    APP_DISC_CFG_CONN_START = 7u, APP_DISC_CFG_CMPL = 8u,
};
#define DM_ROLE_MASTER 0u
#define DM_ROLE_SLAVE 1u
#define EVEN_BLE_DISC_SLAVE_ANCS_SVC 1u
#define RING_EVT_DISC_DONE 4u
#define STATE_DISC_STATE 0x57u
#define STATE_ANCS_RETRY 0x5au
#define SLAVE_HDL_OFFSET 0x2au /* bytes: uint16_t index 21 */

/* RAM 0x20074310..0x20074327, filled by audio_ble_profile_handler_init:
 * [0] discovery state/handle block, [2] slave GATT handles, [3] ANCS handles,
 * [4] master GATT handles, [5] ring handles. */
extern uint32_t audio_ble_profile_runtime_rows[6];
extern const uint8_t g2_disc_cfg_list_master[2][8]; /* ROM 0x784dc0 attcDiscCfg_t[2] */
extern const uint8_t g2_disc_cfg_list_slave[4][8];  /* ROM 0x75daf0 attcDiscCfg_t[4] */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern uint8_t DmConnRole(uint8_t); /* 0x4b73c4 */
extern uint8_t app_ble_phone_type_get_4b8128(void);
extern void app_disc_set_hdl_list_532eb4(uint8_t connId, uint8_t hdlListLen, uint16_t *pHdlList);
extern void app_disc_complete_53303c(uint8_t connId, uint8_t status);
extern void app_disc_configure_533474(uint8_t connId, uint8_t status, uint8_t cfgListLen,
                                      const void *pCfgList, uint8_t hdlListLen, uint16_t *pHdlList);
extern void audio_ble_service_discovery_followup_5336e0(uint8_t connection); /* AppDiscReadDatabaseHash */
extern void AppMasterSecurityReq_503ea8(uint8_t conn_id);
extern void GattDiscover_4b59c0(uint8_t connection, uint16_t *handles);
extern void APP_BleRingSvcDiscover(uint8_t conn_id, uint16_t *handles); /* 0x4c487c */
extern uint8_t APP_BleAnccSvcDiscover(uint8_t conn_id, uint16_t *handles); /* 0x4bf82c */
extern uint32_t Thread_SendEvtToRingTask(uint32_t flags); /* 0x4c543e */

static const char module_tag[] = "ble.disc"; /* ROM 0x78a058 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_discovery.c"; /* ROM 0x6f7fc4 */
static const char fn_name[] = "APP_BleServerDiscCback"; /* ROM 0x774eac */
static const char s_init[] = "APP_DISC_INIT DmConnRole(connId) = %d"; /* ROM 0x74733c */
static const char c_init[] = "[ble.disc]APP_DISC_INIT DmConnRole(connId) = %d"; /* ROM 0x731394 */
static const char s_init_reset[] = "[Service Discovery] Reset discState in APP_DISC_INIT: discState=%d"; /* ROM 0x6ffe3c */
static const char c_init_reset[] = "[ble.disc][Service Discovery] Reset discState in APP_DISC_INIT: discState=%d"; /* ROM 0x6eb3a8 */
static const char s_dbh[] = "APP_DISC_READ_DATABASE_HASH"; /* ROM 0x768f60 */
static const char c_dbh[] = "[ble.disc]APP_DISC_READ_DATABASE_HASH"; /* ROM 0x747364 */
static const char s_sec[] = "APP_DISC_SEC_REQUIRED"; /* ROM 0x774ec4 */
static const char c_sec[] = "[ble.disc]APP_DISC_SEC_REQUIRED"; /* ROM 0x75da70 */
static const char s_start[] = "APP_DISC_START"; /* ROM 0x784da0 */
static const char c_start[] = "[ble.disc]APP_DISC_START"; /* ROM 0x768f7c */
static const char s_failed[] = "APP_DISC_FAILED, discState = %d role %d(%d)"; /* ROM 0x73be54 */
static const char c_failed[] = "[ble.disc]APP_DISC_FAILED, discState = %d role %d(%d)"; /* ROM 0x71bc10 */
static const char s_cmpl[] = "APP_DISC_CMPL, discState = %d role %d(%d), status = %d"; /* ROM 0x71bc48 */
static const char c_cmpl[] = "[ble.disc]APP_DISC_CMPL, discState = %d role %d(%d), status = %d"; /* ROM 0x6ffe80 */
static const char s_fallthrough[] = "[Service Discovery] Fall-through from APP_DISC_FAILED, discState = %d"; /* ROM 0x6f8054 */
static const char c_fallthrough[] = "[ble.disc][Service Discovery] Fall-through from APP_DISC_FAILED, discState = %d"; /* ROM 0x6eb3f8 */
static const char s_ancs_ok[] = "[ANCS] Service discovery succeeded, reset retry counter"; /* ROM 0x71bc80 */
static const char c_ancs_ok[] = "[ble.disc][ANCS] Service discovery succeeded, reset retry counter"; /* ROM 0x6ffec4 */
static const char s_after_inc[] = "[Service Discovery] After discState++, discState=%d, EVEN_BLE_DISC_SLAVE_ANCS_SVC=%d"; /* ROM 0x6e2228 */
static const char c_after_inc[] = "[ble.disc][Service Discovery] After discState++, discState=%d, EVEN_BLE_DISC_SLAVE_ANCS_SVC=%d"; /* ROM 0x6dc2d4 */
static const char s_ring[] = "discover Ring service = %d role %d(%d)"; /* ROM 0x74738c */
static const char c_ring[] = "[ble.disc]discover Ring service = %d role %d(%d)"; /* ROM 0x7269ac */
static const char s_done[] = "discovery complete"; /* ROM 0x77dbc8 */
static const char c_done[] = "[ble.disc]discovery complete"; /* ROM 0x75da90 */
static const char s_hdl[] = "*pHdl = 0x%04x"; /* ROM 0x784db0 */
static const char c_hdl[] = "[ble.disc]*pHdl = 0x%04x"; /* ROM 0x768f98 */
static const char s_slave[] = "[Service Discovery] SLAVE role: discState=%d, EVEN_BLE_DISC_SLAVE_ANCS_SVC=%d, phoneType=%d"; /* ROM 0x6df3d8 */
static const char c_slave[] = "[ble.disc][Service Discovery] SLAVE role: discState=%d, EVEN_BLE_DISC_SLAVE_ANCS_SVC=%d, phoneType=%d"; /* ROM 0x6d83ec */
static const char s_match[] = "[Service Discovery] discState matches EVEN_BLE_DISC_SLAVE_ANCS_SVC"; /* ROM 0x6fff08 */
static const char c_match[] = "[ble.disc][Service Discovery] discState matches EVEN_BLE_DISC_SLAVE_ANCS_SVC"; /* ROM 0x6eb448 */
static const char s_ancs_start[] = "[Service Discovery] Starting ANCS service discovery"; /* ROM 0x7269e0 */
static const char c_ancs_start[] = "[ble.disc][Service Discovery] Starting ANCS service discovery"; /* ROM 0x708da4 */
static const char s_ancs_busy[] = "Discovering ANCS."; /* ROM 0x77dbdc */
static const char c_ancs_busy[] = "[ble.disc]Discovering ANCS."; /* ROM 0x768fb4 */
static const char s_ancs_fail[] = "[Service Discovery] left ANCS service discovery failed, skipping ANCS discovery"; /* ROM 0x6eb498 */
static const char c_ancs_fail[] = "[ble.disc][Service Discovery] left ANCS service discovery failed, skipping ANCS discovery"; /* ROM 0x6df434 */
static const char s_ancs_skip[] = "[Service Discovery] discState (%d) != EVEN_BLE_DISC_SLAVE_ANCS_SVC (%d), skipping ANCS discovery"; /* ROM 0x6d9ddc */
static const char c_ancs_skip[] = "[ble.disc][Service Discovery] discState (%d) != EVEN_BLE_DISC_SLAVE_ANCS_SVC (%d), skipping ANCS discovery"; /* ROM 0x6a62a4 */
static const char s_ancs_done[] = "Finished ANCS discovering."; /* ROM 0x768fd0 */
static const char c_ancs_done[] = "[ble.disc]Finished ANCS discovering."; /* ROM 0x7473b4 */
static const char s_cfg[] = "start configuration"; /* ROM 0x77dbf0 */
static const char c_cfg[] = "[ble.disc]start configuration"; /* ROM 0x75dab0 */
static const char s_cfg_start[] = "APP_DISC_CFG_START"; /* ROM 0x77dc04 */
static const char c_cfg_start[] = "[ble.disc]APP_DISC_CFG_START"; /* ROM 0x75dad0 */
static const char s_cfg_cmpl[] = "APP_DISC_CFG_CMPL"; /* ROM 0x77dc18 */
static const char c_cfg_cmpl[] = "[ble.disc]APP_DISC_CFG_CMPL"; /* ROM 0x768fec */
static const char s_ancs_hdl[] = "ANCS Handles - NS: 0x%04x, NS_CCC: 0x%04x, CP: 0x%04x, DS: 0x%04x, DS_CCC: 0x%04x"; /* ROM 0x6e5ee4 */
static const char c_ancs_hdl[] = "[ble.disc]ANCS Handles - NS: 0x%04x, NS_CCC: 0x%04x, CP: 0x%04x, DS: 0x%04x, DS_CCC: 0x%04x"; /* ROM 0x6df490 */
static const char s_cfg_conn[] = "APP_DISC_CFG_CONN_START"; /* ROM 0x774edc */
static const char c_cfg_conn[] = "[ble.disc]APP_DISC_CFG_CONN_START"; /* ROM 0x751b6c */

/* Product LOG macros: full log on flag bit 1, compressed log (code =
 * level << 26 | argc << 22) on flag bit 0 or 2. Arguments are evaluated
 * separately in each branch, as in stock. */
#define DISC_LOG0(level, line, plain, compact)                                                 \
    do {                                                                                       \
        if (audio_log_flags() & 2u)                                                            \
            audio_log_extended((level), module_tag, source_file, fn_name, (line), plain);      \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                              \
            (void)compress_log_output((uint32_t)(level) << 26, compact, compact);              \
    } while (0)
#define DISC_LOGN(level, line, argc, plain, compact, ...)                                      \
    do {                                                                                       \
        if (audio_log_flags() & 2u)                                                            \
            audio_log_extended((level), module_tag, source_file, fn_name, (line), plain,       \
                               __VA_ARGS__);                                                   \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                              \
            (void)compress_log_output(((uint32_t)(level) << 26) | ((uint32_t)(argc) << 22),     \
                                      compact, compact, __VA_ARGS__);                          \
    } while (0)

static uint8_t *disc_state(void)
{
    return (uint8_t *)(uintptr_t)audio_ble_profile_runtime_rows[0];
}

static uint16_t *row_handles(uint32_t row)
{
    return (uint16_t *)(uintptr_t)audio_ble_profile_runtime_rows[row];
}

void APP_BleServerDiscCback(uint8_t connId, uint8_t status)
{
    switch (status) {
    case APP_DISC_INIT:
        DISC_LOGN(4u, 0x121u, 1u, s_init, c_init, (uint32_t)DmConnRole(connId));
        if (DmConnRole(connId) == DM_ROLE_MASTER) {
            disc_state()[STATE_DISC_STATE] = 0u;
            app_disc_set_hdl_list_532eb4(connId, 5u, (uint16_t *)(void *)disc_state());
        } else {
            disc_state()[STATE_DISC_STATE] = 0u;
            app_disc_set_hdl_list_532eb4(connId, 8u, (uint16_t *)(void *)(disc_state() + SLAVE_HDL_OFFSET));
        }
        DISC_LOGN(4u, 0x131u, 1u, s_init_reset, c_init_reset, (uint32_t)disc_state()[STATE_DISC_STATE]);
        return;

    case APP_DISC_READ_DATABASE_HASH:
        DISC_LOG0(4u, 0x135u, s_dbh, c_dbh);
        audio_ble_service_discovery_followup_5336e0(connId);
        return;

    case APP_DISC_SEC_REQUIRED:
        DISC_LOG0(4u, 0x13bu, s_sec, c_sec);
        if (DmConnRole(connId) == DM_ROLE_MASTER)
            AppMasterSecurityReq_503ea8(connId);
        return;

    case APP_DISC_START:
        DISC_LOG0(4u, 0x148u, s_start, c_start);
        disc_state()[STATE_ANCS_RETRY] = 0u;
        if (DmConnRole(connId) == DM_ROLE_MASTER) {
            disc_state()[STATE_DISC_STATE] = 0u;
            GattDiscover_4b59c0(connId, row_handles(4u));
        } else {
            disc_state()[STATE_DISC_STATE] = 0u;
            GattDiscover_4b59c0(connId, row_handles(2u));
        }
        return;

    case APP_DISC_FAILED:
        DISC_LOGN(2u, 0x16eu, 3u, s_failed, c_failed, (uint32_t)disc_state()[STATE_DISC_STATE],
                 (uint32_t)DmConnRole(connId), 0u);
        disc_state()[STATE_DISC_STATE]++;
        /* fall through */
    case APP_DISC_CMPL:
        DISC_LOGN(4u, 0x19du, 4u, s_cmpl, c_cmpl, (uint32_t)disc_state()[STATE_DISC_STATE],
                 (uint32_t)DmConnRole(connId), 0u, (uint32_t)status);
        if (status != APP_DISC_CMPL && status != APP_DISC_CFG_CMPL) {
            DISC_LOGN(2u, 0x1a3u, 1u, s_fallthrough, c_fallthrough, (uint32_t)disc_state()[STATE_DISC_STATE]);
            disc_state()[STATE_DISC_STATE]++;
            return;
        }
        if (DmConnRole(connId) == DM_ROLE_SLAVE &&
            disc_state()[STATE_DISC_STATE] == EVEN_BLE_DISC_SLAVE_ANCS_SVC) {
            DISC_LOG0(3u, 0x1b1u, s_ancs_ok, c_ancs_ok);
            disc_state()[STATE_ANCS_RETRY] = 0u;
        }
        if (status == APP_DISC_CMPL) {
            disc_state()[STATE_DISC_STATE]++;
            DISC_LOGN(3u, 0x1bdu, 2u, s_after_inc, c_after_inc, (uint32_t)disc_state()[STATE_DISC_STATE],
                     (uint32_t)EVEN_BLE_DISC_SLAVE_ANCS_SVC);
        }
        if (DmConnRole(connId) == DM_ROLE_MASTER) {
            if (disc_state()[STATE_DISC_STATE] == 1u) {
                DISC_LOGN(4u, 0x1c7u, 3u, s_ring, c_ring, (uint32_t)disc_state()[STATE_DISC_STATE],
                         (uint32_t)DmConnRole(connId), 0u);
                APP_BleRingSvcDiscover(connId, row_handles(5u));
            } else if (disc_state()[STATE_DISC_STATE] == 2u) {
                DISC_LOG0(4u, 0x1cfu, s_done, c_done);
                const uint16_t *hdl = (const uint16_t *)(const void *)disc_state();
                for (uint8_t n = 5u; n != 0u; n--) {
                    DISC_LOGN(4u, 0x1d4u, 1u, s_hdl, c_hdl, (uint32_t)*hdl);
                    hdl++;
                }
                app_disc_complete_53303c(connId, APP_DISC_CMPL);
                app_disc_configure_533474(connId, APP_DISC_CFG_START, 2u, g2_disc_cfg_list_master, 5u,
                                          (uint16_t *)(void *)disc_state());
            }
            return;
        }
        DISC_LOGN(4u, 0x1e4u, 3u, s_slave, c_slave, (uint32_t)disc_state()[STATE_DISC_STATE],
                 (uint32_t)EVEN_BLE_DISC_SLAVE_ANCS_SVC, (uint32_t)app_ble_phone_type_get_4b8128());
        if (disc_state()[STATE_DISC_STATE] == EVEN_BLE_DISC_SLAVE_ANCS_SVC) {
            DISC_LOG0(4u, 0x1e7u, s_match, c_match);
            DISC_LOG0(3u, 0x1ebu, s_ancs_start, c_ancs_start);
            if (APP_BleAnccSvcDiscover(connId, row_handles(3u)) == 0u) {
                /* ANCS service absent: skip straight to configuration */
                DISC_LOG0(2u, 0x1efu, s_ancs_fail, c_ancs_fail);
                disc_state()[STATE_DISC_STATE]++;
            } else {
                DISC_LOG0(4u, 0x1edu, s_ancs_busy, c_ancs_busy);
            }
        } else {
            DISC_LOGN(2u, 0x1fcu, 2u, s_ancs_skip, c_ancs_skip, (uint32_t)disc_state()[STATE_DISC_STATE],
                     (uint32_t)EVEN_BLE_DISC_SLAVE_ANCS_SVC);
        }
        if (disc_state()[STATE_DISC_STATE] == 2u) {
            DISC_LOG0(4u, 0x203u, s_done, c_done);
            app_disc_complete_53303c(connId, APP_DISC_CMPL);
            DISC_LOG0(4u, 0x205u, s_ancs_done, c_ancs_done);
            DISC_LOG0(4u, 0x207u, s_cfg, c_cfg);
            app_disc_configure_533474(connId, APP_DISC_CFG_START, 4u, g2_disc_cfg_list_slave, 8u,
                                      (uint16_t *)(void *)(disc_state() + SLAVE_HDL_OFFSET));
        }
        return;

    case APP_DISC_CFG_START:
        DISC_LOG0(4u, 0x210u, s_cfg_start, c_cfg_start);
        if (DmConnRole(connId) == DM_ROLE_MASTER)
            app_disc_configure_533474(connId, APP_DISC_CFG_START, 2u, g2_disc_cfg_list_master, 5u,
                                      (uint16_t *)(void *)disc_state());
        else
            app_disc_configure_533474(connId, APP_DISC_CFG_START, 4u, g2_disc_cfg_list_slave, 8u,
                                      (uint16_t *)(void *)(disc_state() + SLAVE_HDL_OFFSET));
        return;

    case APP_DISC_CFG_CONN_START:
        DISC_LOG0(4u, 0x234u, s_cfg_conn, c_cfg_conn);
        return;

    case APP_DISC_CFG_CMPL:
        app_disc_complete_53303c(connId, APP_DISC_CFG_CMPL);
        DISC_LOG0(4u, 0x223u, s_cfg_cmpl, c_cfg_cmpl);
        if (DmConnRole(connId) == DM_ROLE_MASTER) {
            (void)Thread_SendEvtToRingTask(RING_EVT_DISC_DONE);
            return;
        }
        if (audio_ble_profile_runtime_rows[3] != 0u) {
            const uint16_t *h = row_handles(3u);
            DISC_LOGN(4u, 0x22eu, 5u, s_ancs_hdl, c_ancs_hdl, (uint32_t)h[0], (uint32_t)h[1],
                     (uint32_t)h[2], (uint32_t)h[3], (uint32_t)h[4]);
        }
        return;

    default:
        return;
    }
}
