/* Ring central scan path, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble_central.c.
 * Native 0x49f97c..0x49fb0a and 0x49fb14..0x4a01fc; literal pool from 0x4a02ac.
 *
 * The master control block (pointer cell RAM 0x200742fc) carries the WSF
 * handler id at +0x56, the scan state at +0x58 (0 idle, 1 scanning, 2 scan
 * start indicated) and the auto-connect flag at +0x59. The connection-target
 * block (pointer cell RAM 0x20074300) keeps the best candidate seen while
 * scanning: +4 bond handle, +8 host address type, +9 BD address, +0x15
 * "connect when the scan stops", +0x16 best RSSI.
 *
 * _ringLinkStateName 0x49f828, _SetRingLinkState 0x49f870 and
 * _masterConnectCancel 0x4a01fc are implemented in ble/ble-ring and
 * ble/ble-master. */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Cordio hciConnSpec_t. */
typedef struct {
    uint16_t conn_interval_min; /* +0x0 */
    uint16_t conn_interval_max; /* +0x2 */
    uint16_t conn_latency;      /* +0x4 */
    uint16_t sup_timeout;       /* +0x6 */
    uint16_t min_ce_len;        /* +0x8 */
    uint16_t max_ce_len;        /* +0xa */
} g2_hci_conn_spec_t;
_Static_assert(sizeof(g2_hci_conn_spec_t) == 12u, "hciConnSpec_t");

/* Cordio appMasterCfg_t (ROM 0x78c9e4: 100 ms / 80 ms, 10 s, general, active). */
typedef struct {
    uint16_t scan_interval; /* +0x0 */
    uint16_t scan_window;   /* +0x2 */
    uint16_t scan_duration; /* +0x4 */
    uint8_t disc_mode;      /* +0x6 */
    uint8_t scan_type;      /* +0x7 */
} g2_app_master_cfg_t;
_Static_assert(sizeof(g2_app_master_cfg_t) == 8u, "appMasterCfg_t");

/* Cordio dmEvt_t for DM_SCAN_REPORT_IND (hciLeAdvReportEvt_t). */
typedef struct {
    uint16_t param;              /* +0x00 wsfMsgHdr_t */
    uint8_t event;               /* +0x02 */
    uint8_t status;              /* +0x03 */
    uint8_t *data;               /* +0x04 */
    uint8_t len;                 /* +0x08 */
    int8_t rssi;                 /* +0x09 */
    uint8_t event_type;          /* +0x0a */
    uint8_t addr_type;           /* +0x0b */
    uint8_t addr[6];             /* +0x0c little endian */
    uint8_t direct_addr_type;    /* +0x12 */
    uint8_t direct_addr[6];      /* +0x13 */
} g2_scan_report_t;
_Static_assert(offsetof(g2_scan_report_t, addr) == 0x0cu, "scanReport.addr");
_Static_assert(offsetof(g2_scan_report_t, direct_addr) == 0x13u, "scanReport.directAddr");

enum {
    MASTER_HANDLER_ID = 0x56,
    MASTER_SCAN_STATE = 0x58,
    MASTER_AUTO_CONNECT = 0x59,
};
enum {
    TARGET_DB_HDL = 0x04,
    TARGET_ADDR_TYPE = 0x08,
    TARGET_ADDR = 0x09,
    TARGET_DO_CONNECT = 0x15,
    TARGET_BEST_RSSI = 0x16,
};

#define DM_ADV_TYPE_SHORT_NAME 8u
#define DM_ADV_TYPE_LOCAL_NAME 9u
#define DM_ADDR_RANDOM 1u
#define DM_DISC_MODE_GENERAL 1u
#define APP_RESOLVE_DIRECT_RPA 1u
#define SCAN_FILTER_LOG_ALL 4u
#define SCAN_FLAG_LOG_ALL 0x04u
#define SCAN_FLAG_AUTO_CONNECT 0x10u
#define SCAN_FLAG_STOP 0x20u
#define SCAN_DURATION_MS 10000u
#define RECONNECT_DELAY_MS 1500u
#define RECONNECT_WAIT_LIMIT 50u

extern uint8_t *audio_ble_master_context;                    /* pointer cell RAM 0x200742fc */
extern uint8_t *audio_ble_master_mode_slot;                  /* pointer cell RAM 0x20074300 */
extern volatile uint16_t audio_ble_master_connect_wait;      /* RAM 0x20074f18 */
extern uint8_t g2_ble_master_scan_filter_20074f81;           /* RAM 0x20074f81 */
extern uint8_t audio_ble_master_target_address[6];           /* RAM 0x200003c0 */
extern const uint8_t audio_ble_master_registration_table[8]; /* ROM 0x78c9e4 appMasterCfg_t */
extern const g2_hci_conn_spec_t g2_ble_master_conn_spec_78a04c; /* ROM 0x78a04c 20-40 ms, 6 s */

extern void DmConnSetConnSpec(const g2_hci_conn_spec_t *spec);          /* 0x4b6de6 */
extern void DmConnSetScanInterval(uint16_t interval, uint16_t window);  /* 0x4b6dd4 */
extern uint8_t *DmFindAdType(uint8_t ad_type, uint16_t len, uint8_t *data); /* 0x4d2a06 */
extern uint8_t DmHostAddrType(uint8_t addr_type);                       /* 0x4d2aa8 */
extern void AppAdvStart(uint8_t mode);                                  /* 0x4b2d22 */
extern void AppAdvStop(void);                                           /* 0x4b2d62 */
extern void AppScanStart(uint8_t mode, uint8_t scan_type, uint16_t duration); /* 0x50337c */
extern void AppScanStop(void);                                          /* 0x5033b2 */
extern uint8_t AppConnOpen(uint8_t addr_type, uint8_t *addr, uint32_t db_hdl); /* 0x5033ca */
extern void app_master_resolve_addr_503ffc(void *msg, uint32_t db_hdl, uint8_t resolve_type);
extern uint32_t audio_ble_pair_record_find_47ad74(uint32_t addr_type, const void *addr); /* AppDbFindByAddr */
extern uint32_t app_db_resolve_and_connect_by_addr_47a8c4(uint8_t addr_type, const uint8_t *addr);
extern uint8_t audio_ble_app_adv_state(void);                           /* 0x4b46a8 */
extern void central_schedule_master_connect_004a2618(uint32_t delay_ms, uint8_t arg);
extern void central_cancel_connect_retry_work_004a17f4(void);
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);     /* 0x43c0e4 */
extern void audio_uart_checksum_copy(void *dst, const void *src, uint32_t len); /* 0x439be4 */
extern int32_t g2_lfs_memcmp(const void *a, const void *b, uint32_t len);       /* 0x4751c8 */
extern void audio_dump_hex(const char *label, uint32_t width, const uint8_t *data, uint32_t len); /* 0x43dacc */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "ble.master"; /* ROM 0x78a028 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c"; /* ROM 0x6ff9b8 */
static const char scan_stop_fn[] = "_bleMasterScanStop"; /* ROM 0x77db14 */
static const char do_connect[] = "pEvenMasterConnInfo->doConnect true"; /* ROM 0x7518e4 */
static const char do_connect_short[] = "[ble.master]pEvenMasterConnInfo->doConnect true"; /* ROM 0x731124 */
static const char conn_id[] = "master connId = %d"; /* ROM 0x77db28 */
static const char conn_id_short[] = "[ble.master]master connId = %d"; /* ROM 0x75d7f0 */
static const char auto_connect[] = "pEvenMasterCb->autoConnect true"; /* ROM 0x75d810 */
static const char auto_connect_short[] = "[ble.master]pEvenMasterCb->autoConnect true"; /* ROM 0x73bb94 */
static const char master_scan_fn[] = "_masterScan"; /* ROM 0x78a034 */
static const char scan_start[] = "start = %d"; /* ROM 0x78a040 */
static const char scan_start_short[] = "[ble.master]start = %d"; /* ROM 0x774d74 */
static const char stop_scan[] = "stop scan %d"; /* ROM 0x784d00 */
static const char stop_scan_short[] = "[ble.master]stop scan %d"; /* ROM 0x768d30 */
static const char adv_stop_first[] = "AppAdvStop first"; /* ROM 0x77db3c */
static const char adv_stop_first_short[] = "[ble.master]AppAdvStop first"; /* ROM 0x75d830 */
static const char scanning_stop[] = "scanning, stop scan first"; /* ROM 0x768d4c */
static const char scanning_stop_short[] = "[ble.master]scanning, stop scan first"; /* ROM 0x74701c */
static const char scan_report_fn[] = "_bleMasterScanReport"; /* ROM 0x774d8c */
static const char found[] = "Found: 0x%02x:%02x:%02x:%02x:%02x:%02x rssi: %d %s, addrtype = %d"; /* ROM 0x6ff9fc */
static const char found_short[] =
    "[ble.master]Found: 0x%02x:%02x:%02x:%02x:%02x:%02x rssi: %d %s, addrtype = %d"; /* ROM 0x6eb0d8 */
static const char scan_label[] = "scan"; /* ROM 0x78c9c4 */
static const char paired[] =
    "_bleMasterScanReport: Found paired record, device address %02X:%02X:%02X:%02X:%02X:%02X"; /* ROM 0x6e2120 */
static const char paired_short[] =
    "[ble.master]_bleMasterScanReport: Found paired record, device address %02X:%02X:%02X:%02X:%02X:%02X"; /* ROM 0x6d9cb0 */
static const char direct_rpa[] = "_bleMasterScanReport: Resolving direct address RPA"; /* ROM 0x726498 */
static const char direct_rpa_short[] = "[ble.master]_bleMasterScanReport: Resolving direct address RPA"; /* ROM 0x7089e4 */
static const char rpa_detected[] =
    "_bleMasterScanReport: Detected RPA address, attempting to resolve %02X:%02X:%02X:%02X:%02X:%02X"; /* ROM 0x6dc034 */
static const char rpa_detected_short[] =
    "[ble.master]_bleMasterScanReport: Detected RPA address, attempting to resolve %02X:%02X:%02X:%02X:%02X:%02X"; /* ROM 0x6a5974 */
static const char rpa_started[] = "_bleMasterScanReport: RPA resolution process started"; /* ROM 0x71b8c8 */
static const char rpa_started_short[] = "[ble.master]_bleMasterScanReport: RPA resolution process started"; /* ROM 0x6ffa40 */
static const char rpa_failed[] = "_bleMasterScanReport: RPA resolution failed, no matching IRK found"; /* ROM 0x6ffa84 */
static const char rpa_failed_short[] =
    "[ble.master]_bleMasterScanReport: RPA resolution failed, no matching IRK found"; /* ROM 0x6eb128 */
static const char non_rpa[] =
    "_bleMasterScanReport: Attempting to resolve non-RPA address %02X:%02X:%02X:%02X:%02X:%02X"; /* ROM 0x6df320 */
static const char non_rpa_short[] =
    "[ble.master]_bleMasterScanReport: Attempting to resolve non-RPA address %02X:%02X:%02X:%02X:%02X:%02X"; /* ROM 0x6d8384 */
static const char matched[] = "_bleMasterScanReport: Found matching paired record"; /* ROM 0x7264cc */
static const char matched_short[] = "[ble.master]_bleMasterScanReport: Found matching paired record"; /* ROM 0x708a24 */
static const char report_rssi[] = "pMsg->scanReport.rssi = %d"; /* ROM 0x768d68 */
static const char report_rssi_short[] = "[ble.master]pMsg->scanReport.rssi = %d"; /* ROM 0x747044 */

#define LOG_EXT_ON() ((audio_log_flags() & 2u) != 0u)
#define LOG_CMP_ON() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
#define RPA_ADDR(type, addr) ((type) == DM_ADDR_RANDOM && ((addr)[5] & 0xc0u) == 0x40u)

/* Restore the ring connection parameters and scan interval/window. */
void ring_master_reconnect(const void *msg)
{
    (void)msg;
    const g2_app_master_cfg_t *cfg = (const g2_app_master_cfg_t *)(const void *)audio_ble_master_registration_table;
    DmConnSetConnSpec(&g2_ble_master_conn_spec_78a04c);
    DmConnSetScanInterval(cfg->scan_interval, cfg->scan_window);
}

/* DM_SCAN_START_IND: mark scanning and reset the best-RSSI candidate. */
void ring_master_scan_start(const g2_scan_report_t *msg)
{
    if (msg->status != 0u)
        return;
    audio_ble_master_context[MASTER_SCAN_STATE] = 2u;
    audio_ble_master_mode_slot[TARGET_BEST_RSSI] = (uint8_t)-128;
}

/* DM_SCAN_STOP_IND: connect to the chosen target, or rearm reconnect/advertising. */
void _bleMasterScanStop(const g2_scan_report_t *msg)
{
    if (msg->status != 0u)
        return;
    audio_ble_master_context[MASTER_SCAN_STATE] = 0u;
    if (audio_ble_master_mode_slot[TARGET_DO_CONNECT] != 0u) {
        if (LOG_EXT_ON())
            audio_log_extended(4u, module_tag, source_file, scan_stop_fn, 0xf4u, do_connect);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x10000000u, do_connect_short, do_connect_short);
        audio_ble_master_context[MASTER_AUTO_CONNECT] = 0u;
        uint8_t conn = AppConnOpen(audio_ble_master_mode_slot[TARGET_ADDR_TYPE], audio_ble_master_mode_slot + TARGET_ADDR,
                                   *(uint32_t *)(void *)(audio_ble_master_mode_slot + TARGET_DB_HDL));
        if (LOG_EXT_ON())
            audio_log_extended(4u, module_tag, source_file, scan_stop_fn, 0xf8u, conn_id, conn);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x10400000u, conn_id_short, conn_id_short, conn);
        audio_ble_master_mode_slot[TARGET_DO_CONNECT] = 0u;
        return;
    }
    if (audio_ble_master_context[MASTER_AUTO_CONNECT] == 0u) {
        AppAdvStart(DM_DISC_MODE_GENERAL);
        return;
    }
    if (LOG_EXT_ON())
        audio_log_extended(4u, module_tag, source_file, scan_stop_fn, 0xfbu, auto_connect);
    if (LOG_CMP_ON())
        (void)compress_log_output(0x10000000u, auto_connect_short, auto_connect_short);
    audio_ble_master_context[MASTER_AUTO_CONNECT] = 0u;
    central_schedule_master_connect_004a2618(RECONNECT_DELAY_MS, 0u);
    audio_ble_master_connect_wait++;
    if (audio_ble_master_connect_wait > RECONNECT_WAIT_LIMIT) {
        audio_ble_master_connect_wait = 0u;
        central_cancel_connect_retry_work_004a17f4();
    }
}

/* Scan request: bit 2 logs every report (no auto connect), bit 4 enables
 * auto connect, bit 5 stops the running scan. */
void _masterScan(uint8_t flags)
{
    if (LOG_EXT_ON())
        audio_log_extended(4u, module_tag, source_file, master_scan_fn, 0x10bu, scan_start, (uint32_t)flags);
    if (LOG_CMP_ON())
        (void)compress_log_output(0x10400000u, scan_start_short, scan_start_short, (uint32_t)flags);
    g2_ble_master_scan_filter_20074f81 = 0u;
    if ((flags & SCAN_FLAG_LOG_ALL) != 0u) {
        g2_ble_master_scan_filter_20074f81 = SCAN_FILTER_LOG_ALL;
        audio_ble_master_context[MASTER_AUTO_CONNECT] = 0u;
    } else if ((flags & SCAN_FLAG_AUTO_CONNECT) != 0u) {
        audio_ble_master_context[MASTER_AUTO_CONNECT] = 1u;
    }
    if ((flags & SCAN_FLAG_STOP) != 0u) {
        if (LOG_EXT_ON())
            audio_log_extended(4u, module_tag, source_file, master_scan_fn, 0x115u, stop_scan,
                               audio_ble_master_context[MASTER_SCAN_STATE]);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x10400000u, stop_scan_short, stop_scan_short,
                                      audio_ble_master_context[MASTER_SCAN_STATE]);
        if (audio_ble_master_context[MASTER_SCAN_STATE] != 0u)
            AppScanStop();
        return;
    }
    audio_ble_master_mode_slot[TARGET_DO_CONNECT] = 0u;
    if (audio_ble_app_adv_state() != 0u) {
        if (LOG_EXT_ON())
            audio_log_extended(4u, module_tag, source_file, master_scan_fn, 0x11cu, adv_stop_first);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x10000000u, adv_stop_first_short, adv_stop_first_short);
        AppAdvStop();
    }
    if (audio_ble_master_context[MASTER_SCAN_STATE] == 0u) {
        const g2_app_master_cfg_t *cfg =
            (const g2_app_master_cfg_t *)(const void *)audio_ble_master_registration_table;
        audio_ble_master_context[MASTER_SCAN_STATE] = 1u;
        AppScanStart(cfg->disc_mode, cfg->scan_type, SCAN_DURATION_MS);
        return;
    }
    if (LOG_EXT_ON())
        audio_log_extended(4u, module_tag, source_file, master_scan_fn, 0x121u, scanning_stop);
    if (LOG_CMP_ON())
        (void)compress_log_output(0x10000000u, scanning_stop_short, scanning_stop_short);
    AppScanStop();
}

static void log_found(const g2_scan_report_t *msg, uint32_t line, const char *name)
{
    if (LOG_EXT_ON())
        audio_log_extended(4u, module_tag, source_file, scan_report_fn, line, found,
                           msg->addr[5], msg->addr[4], msg->addr[3], msg->addr[2], msg->addr[1],
                           msg->addr[0], (int32_t)msg->rssi, name, DmHostAddrType(msg->addr_type));
    if (LOG_CMP_ON())
        (void)compress_log_output(0x12400000u, found_short, found_short, msg->addr[5], msg->addr[4],
                                  msg->addr[3], msg->addr[2], msg->addr[1], msg->addr[0],
                                  (int32_t)msg->rssi, name, DmHostAddrType(msg->addr_type));
}

static void log_addr(const g2_scan_report_t *msg, uint8_t level, uint32_t line, uint32_t flags,
                     const char *message, const char *compact)
{
    if (LOG_EXT_ON())
        audio_log_extended(level, module_tag, source_file, scan_report_fn, line, message,
                           msg->addr[5], msg->addr[4], msg->addr[3], msg->addr[2], msg->addr[1],
                           msg->addr[0]);
    if (LOG_CMP_ON())
        (void)compress_log_output(flags, compact, compact, msg->addr[5], msg->addr[4], msg->addr[3],
                                  msg->addr[2], msg->addr[1], msg->addr[0]);
}

static void log_plain(uint8_t level, uint32_t line, uint32_t flags, const char *message,
                      const char *compact)
{
    if (LOG_EXT_ON())
        audio_log_extended(level, module_tag, source_file, scan_report_fn, line, message);
    if (LOG_CMP_ON())
        (void)compress_log_output(flags, compact, compact);
}

/* DM_SCAN_REPORT_IND: only the configured ring address is considered; the
 * strongest report becomes the connection target and stops the scan. */
void _bleMasterScanReport(g2_scan_report_t *msg)
{
    char name[32];
    bool candidate = false;
    uint32_t db_hdl;
    uint8_t *ad;

    audio_uart_buffer_zero(name, sizeof name, 0u);
    if (audio_ble_master_context[MASTER_SCAN_STATE] == 0u)
        return;
    ad = DmFindAdType(DM_ADV_TYPE_LOCAL_NAME, msg->len, msg->data);
    if (ad != NULL) {
        audio_uart_checksum_copy(name, ad + 2, (uint32_t)ad[0] - 1u);
    } else {
        ad = DmFindAdType(DM_ADV_TYPE_SHORT_NAME, msg->len, msg->data);
        if (ad != NULL)
            audio_uart_checksum_copy(name, ad + 2, (uint32_t)ad[0] - 1u);
    }
    if (g2_ble_master_scan_filter_20074f81 == SCAN_FILTER_LOG_ALL) {
        log_found(msg, 0x162u, name);
        return;
    }
    if (g2_lfs_memcmp(msg->addr, audio_ble_master_target_address, 6u) == 0) {
        audio_dump_hex(scan_label, 16u, msg->data, msg->len);
        log_found(msg, 0x170u, name);
        candidate = true;
    }
    if (g2_lfs_memcmp(msg->addr, audio_ble_master_target_address, 6u) != 0)
        return;
    db_hdl = audio_ble_pair_record_find_47ad74(msg->addr_type, msg->addr);
    if (db_hdl != 0u) {
        log_addr(msg, 3u, 0x17bu, 0x0d800000u, paired, paired_short);
        if (RPA_ADDR(msg->direct_addr_type, msg->direct_addr)) {
            log_plain(4u, 0x180u, 0x10000000u, direct_rpa, direct_rpa_short);
            app_master_resolve_addr_503ffc(msg, db_hdl, APP_RESOLVE_DIRECT_RPA);
        } else {
            candidate = true;
        }
    } else if (RPA_ADDR(msg->addr_type, msg->addr)) {
        log_addr(msg, 3u, 0x18du, 0x0d800000u, rpa_detected, rpa_detected_short);
        if (app_db_resolve_and_connect_by_addr_47a8c4(msg->addr_type, msg->addr) != 0u) {
            log_plain(4u, 0x192u, 0x10000000u, rpa_started, rpa_started_short);
            return;
        }
        log_plain(2u, 0x198u, 0x08000000u, rpa_failed, rpa_failed_short);
    } else {
        log_addr(msg, 4u, 0x1a0u, 0x11800000u, non_rpa, non_rpa_short);
        if (app_db_resolve_and_connect_by_addr_47a8c4(msg->addr_type, msg->addr) != 0u)
            log_plain(4u, 0x1a4u, 0x10000000u, matched, matched_short);
        candidate = true;
    }
    if (!candidate)
        return;
    if (LOG_EXT_ON())
        audio_log_extended(4u, module_tag, source_file, scan_report_fn, 0x1abu, report_rssi, (int32_t)msg->rssi);
    if (LOG_CMP_ON())
        (void)compress_log_output(0x10400000u, report_rssi_short, report_rssi_short, (int32_t)msg->rssi);
    if ((int8_t)audio_ble_master_mode_slot[TARGET_BEST_RSSI] >= msg->rssi)
        return;
    audio_ble_master_mode_slot[TARGET_BEST_RSSI] = (uint8_t)msg->rssi;
    audio_ble_master_mode_slot[TARGET_ADDR_TYPE] = DmHostAddrType(msg->addr_type);
    audio_uart_checksum_copy(audio_ble_master_mode_slot + TARGET_ADDR, msg->addr, 6u);
    *(uint32_t *)(void *)(audio_ble_master_mode_slot + TARGET_DB_HDL) = db_hdl;
    audio_ble_master_mode_slot[TARGET_DO_CONNECT] = 1u;
    AppScanStop();
}
