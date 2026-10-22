/* Cordio application discovery API, product variant of stock
 * D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-profiles\sources\apps\app\app_disc.c
 * (upstream third-party/upstream/cordio/ble-profiles/sources/af/app_disc.c).
 * Native 0x532eb4..0x532fed AppDiscSetHdlList, 0x53303c..0x53327f AppDiscComplete,
 * 0x5332b4..0x533451 AppDiscFindService, 0x533474..0x533621 AppDiscConfigure;
 * literal pools 0x533458..0x533470, 0x533624..0x533628, 0x533864..0x5338a0.
 *
 * Differences from upstream: every entry rejects connId 0 with an
 * "Invalid connId in ..." warning routed through the vendor trace ladder
 * (APP_TRACE_WARN), and AppDiscComplete logs through the product logger
 * (module "app.disc") instead of APP_TRACE_INFO2. The appDiscCb rows are
 * RAM 0x200733fc (3 x 16 bytes, DM_CONN_MAX 3). */
#include <stdint.h>

typedef struct {
    uint8_t *pDiscCb;       /* +0x0 attcDiscCb_t, WsfBufAlloc(0x14) */
    uint16_t *pHdlList;     /* +0x4 */
    uint8_t connCfgStatus;  /* +0x8 */
    uint8_t cmplStatus;     /* +0x9 */
    uint8_t hdlListLen;     /* +0xa */
    uint8_t inProgress;     /* +0xb */
    uint8_t alreadySecure;  /* +0xc */
    uint8_t secRequired;    /* +0xd */
    uint8_t scPending;      /* +0xe */
    uint8_t pad;            /* +0xf */
} app_disc_cb_t;
_Static_assert(sizeof(app_disc_cb_t) == 0x10, "appDiscCb row is 16 bytes");

/* attcDiscCb_t public fields */
#define DISC_CHAR_LIST   0x0u  /* attcDiscChar_t ** */
#define DISC_HDL_LIST    0x4u  /* uint16_t * */
#define DISC_CFG_LIST    0x8u  /* attcDiscCfg_t * */
#define DISC_CHAR_LEN    0xcu
#define DISC_CFG_LEN     0xdu
#define ATTC_DISC_CB_LEN 0x14u

enum {
    APP_DISC_IDLE = 0u, APP_DISC_SVC_DISC_IN_PROGRESS = 1u, APP_DISC_CFG_IN_PROGRESS = 2u,
};
enum { APP_DISC_CMPL = 4u, APP_DISC_CFG_CONN_START = 7u, APP_DISC_CFG_CMPL = 8u };
#define DM_IDLE_APP_DISC 8u
#define DM_CONN_IDLE 0u
#define DM_CONN_BUSY 1u

extern uint8_t audio_ble_subsystem_rows_200733fc[]; /* RAM 0x200733fc appDiscCb[3] */
extern uintptr_t audio_ble_service_dispatch_20074348; /* RAM 0x20074348 appDiscCback */

extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *, const void *, uint32_t); /* strncmp */
extern void WsfTrace(const char *, const char *, ...); /* 0x52a63c */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void DmConnSetIdle(uint8_t, uint16_t, uint8_t); /* 0x4b71dc */
extern void *WsfBufAlloc(uint16_t); /* 0x530446 */
extern void WsfBufFree(void *); /* 0x5304d4 */
extern void AttcDiscService(uint8_t connId, void *pCb, uint8_t uuidLen, const uint8_t *pUuid); /* 0x56bf12 */
extern uint8_t AttcDiscConfigStart(uint8_t connId, void *pCb); /* 0x56c388 */
extern uint8_t *audio_ble_pair_record(uint8_t); /* 0x4bb07c AppDbGetHdl */
extern uint8_t audio_ble_connection_is_active_4bad26(uint8_t); /* AppCheckBonded */
extern void audio_ble_pair_record_clear_a(uint8_t *, uint8_t); /* 0x47b488 AppDbSetDiscStatus */
extern void audio_ble_pair_record_attach(uint8_t *, uint32_t); /* 0x47b48e AppDbSetHdlList */

static const char t_warn[] = "WARN"; /* ROM 0x78ca6c */
static const char t_err[] = "ERR";   /* inline pools 0x532ffc/0x533284/0x533458/0x5336c0 */
static const char t_info[] = "INFO"; /* ROM 0x78ca74 */
static const char t_app[] = "APP";   /* inline pools 0x533004/0x533288/0x533460/0x5336c4 */
static const char t_hci[] = "HCI";   /* inline pools 0x533020/0x533294/0x533628 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_disc.c"; /* ROM 0x6dc694 */
static const char fn_set_hdl[] = "AppDiscSetHdlList"; /* ROM 0x77de84 */
static const char fn_complete[] = "AppDiscComplete"; /* ROM 0x784fe0 */
static const char fn_find[] = "AppDiscFindService"; /* ROM 0x77de98 */
static const char fn_configure[] = "AppDiscConfigure"; /* ROM 0x77deac */
static const char s_bad_set_hdl[] = "Invalid connId in AppDiscSetHdlList: %d"; /* ROM 0x7479a4 */
static const char s_bad_complete[] = "Invalid connId in AppDiscComplete: %d, status: %d"; /* ROM 0x727094 */
static const char s_bad_find[] = "Invalid connId in AppDiscDiscoverChars: %d"; /* ROM 0x73c2a0 */
static const char s_bad_configure[] = "Invalid connId in AppDiscDiscoverCfgs: %d"; /* ROM 0x73c2cc */
static const char module_tag[] = "app.disc"; /* ROM 0x78a148 */
static const char s_complete[] = "AppDiscComplete connId:%d status:0x%02x"; /* ROM 0x7479cc */
static const char c_complete[] = "[app.disc]AppDiscComplete connId:%d status:0x%02x"; /* ROM 0x7270c8 */

/* APP_TRACE_WARN in this build: the vendor logger when HCI tracing is
 * enabled (level from the WARN/ERR/INFO tag match), else WsfTrace. */
#define APP_TRACE_WARN(fn, line, msg, ...)                                                   \
    do {                                                                                     \
        uint8_t level_;                                                                      \
        if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&                               \
            audio_ble_hci_vendor_compare_44b610(t_warn, t_err, 3u) == 0) level_ = 1u;       \
        else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&                          \
                 audio_ble_hci_vendor_compare_44b610(t_warn, t_warn, 4u) == 0) level_ = 2u; \
        else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&                          \
                 audio_ble_hci_vendor_compare_44b610(t_warn, t_info, 4u) == 0) level_ = 3u; \
        else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u) level_ = 4u;               \
        else {                                                                               \
            if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||                           \
                audio_ble_hci_vendor_compare_44b610(t_app, t_hci, 3u) != 0)                 \
                WsfTrace(t_warn, msg, __VA_ARGS__);                                          \
            break;                                                                           \
        }                                                                                    \
        if (audio_log_flags() & 2u)                                                          \
            audio_log_extended(level_, t_app, source_file, fn, line, msg, __VA_ARGS__);      \
    } while (0)

static app_disc_cb_t *disc_cb(uint8_t connId)
{
    return &((app_disc_cb_t *)(void *)audio_ble_subsystem_rows_200733fc)[connId - 1u];
}

static void put_word(uint8_t *p, uint32_t off, uint32_t v)
{
    *(uint32_t *)(void *)(p + off) = v;
}

/* Stock 0x532eb4 */
void app_disc_set_hdl_list_532eb4(uint8_t connId, uint8_t hdlListLen, uint16_t *pHdlList)
{
    if (connId == 0u) {
        APP_TRACE_WARN(fn_set_hdl, 0x368u, s_bad_set_hdl, (uint32_t)connId);
        return;
    }
    app_disc_cb_t *cb = disc_cb(connId);
    cb->hdlListLen = hdlListLen;
    cb->pHdlList = pHdlList;
}

/* Stock 0x53303c */
void app_disc_complete_53303c(uint8_t connId, uint8_t status)
{
    if (connId == 0u) {
        APP_TRACE_WARN(fn_complete, 0x37fu, s_bad_complete, (uint32_t)connId, (uint32_t)status);
        return;
    }
    app_disc_cb_t *cb = disc_cb(connId);
    DmConnSetIdle(connId, DM_IDLE_APP_DISC, DM_CONN_IDLE);
    if (!(status == APP_DISC_CFG_CMPL && cb->connCfgStatus == APP_DISC_CFG_CONN_START))
        cb->cmplStatus = status;
    cb->inProgress = APP_DISC_IDLE;
    if (cb->pDiscCb != 0) {
        WsfBufFree(cb->pDiscCb);
        cb->pDiscCb = 0;
    }
    uint8_t *hdl = audio_ble_pair_record(connId);
    if (hdl != 0) {
        /* configuration complete is only stored for bonded peers */
        uint8_t disc_complete = audio_ble_connection_is_active_4bad26(connId) ? APP_DISC_CFG_CMPL : APP_DISC_CMPL;
        if (!(status == APP_DISC_CFG_CMPL && cb->connCfgStatus == APP_DISC_CFG_CONN_START) &&
            status <= disc_complete)
            audio_ble_pair_record_clear_a(hdl, status);
        if (cb->pHdlList != 0 && status == APP_DISC_CMPL)
            audio_ble_pair_record_attach(hdl, (uint32_t)(uintptr_t)cb->pHdlList);
    }
    if (status == APP_DISC_CFG_CMPL)
        cb->connCfgStatus = APP_DISC_CFG_CMPL;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_complete, 0x3b3u, s_complete,
                           (uint32_t)connId, (uint32_t)status);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10800000u, c_complete, c_complete, (uint32_t)connId, (uint32_t)status);
}

/* Stock 0x5332b4 */
void app_disc_find_service_5332b4(uint8_t connection, uint8_t uuid_length,
                                  const uint8_t *uuid, uint8_t list_length,
                                  void *characteristics, uint16_t *handles)
{
    if (connection == 0u) {
        APP_TRACE_WARN(fn_find, 0x3c9u, s_bad_find, (uint32_t)connection);
        return;
    }
    app_disc_cb_t *cb = disc_cb(connection);
    if (cb->pDiscCb == 0)
        cb->pDiscCb = (uint8_t *)WsfBufAlloc(ATTC_DISC_CB_LEN);
    if (cb->pDiscCb != 0) {
        DmConnSetIdle(connection, DM_IDLE_APP_DISC, DM_CONN_BUSY);
        cb->inProgress = APP_DISC_SVC_DISC_IN_PROGRESS;
        put_word(cb->pDiscCb, DISC_CHAR_LIST, (uint32_t)(uintptr_t)characteristics);
        put_word(cb->pDiscCb, DISC_HDL_LIST, (uint32_t)(uintptr_t)handles);
        cb->pDiscCb[DISC_CHAR_LEN] = list_length;
        AttcDiscService(connection, cb->pDiscCb, uuid_length, uuid);
    }
}

/* Stock 0x533474 */
void app_disc_configure_533474(uint8_t connId, uint8_t status, uint8_t cfgListLen,
                               const void *pCfgList, uint8_t hdlListLen, uint16_t *pHdlList)
{
    if (connId == 0u) {
        APP_TRACE_WARN(fn_configure, 0x3f4u, s_bad_configure, (uint32_t)connId);
        return;
    }
    app_disc_cb_t *cb = disc_cb(connId);
    if (cb->pDiscCb == 0)
        cb->pDiscCb = (uint8_t *)WsfBufAlloc(ATTC_DISC_CB_LEN);
    if (cb->pDiscCb != 0) {
        DmConnSetIdle(connId, DM_IDLE_APP_DISC, DM_CONN_BUSY);
        cb->inProgress = APP_DISC_CFG_IN_PROGRESS;
        if (status == APP_DISC_CFG_CONN_START)
            cb->connCfgStatus = APP_DISC_CFG_CONN_START;
        put_word(cb->pDiscCb, DISC_CFG_LIST, (uint32_t)(uintptr_t)pCfgList);
        cb->pDiscCb[DISC_CFG_LEN] = cfgListLen;
        put_word(cb->pDiscCb, DISC_HDL_LIST, (uint32_t)(uintptr_t)pHdlList);
        cb->pDiscCb[DISC_CHAR_LEN] = hdlListLen;
        /* nothing to configure: report APP_DISC_CFG_CMPL at once */
        if (AttcDiscConfigStart(connId, cb->pDiscCb) == 0u)
            ((void (*)(uint8_t, uint8_t))audio_ble_service_dispatch_20074348)(connId, APP_DISC_CFG_CMPL);
    }
}
