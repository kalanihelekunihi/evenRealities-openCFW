/* Dashboard extension layout-PB file transfer, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_ext.c.
 * Native 0x500824..0x501065, 0x501108..0x501165, 0x5011d0..0x5017a3;
 * literal pools 0x501166..0x5011cf, 0x5017a4..0x501d5b (shared with
 * 0x501d5c), 0x5020e8..0x502137.
 *
 * Phone app <-> glasses protocol on BLE pb service 0x1f, all messages encoded
 * from one tx record (RAM 0x20369e1c) into a 0x400-byte buffer (RAM 0x2037919c):
 *   STEP1 APP_REQUEST_PB_FILE_INFO      -> response cmd 1 (exists + two layout strings)
 *   STEP2 APP_REQUEST_UPGRADE_PB_FILE   -> response cmd 3, display blocked 10 s,
 *                                          receive cache reset, then STEP3
 *   STEP3 OS_NOTIFY_PB_FILE_TRANSMIT_START -> notify cmd 4
 *   STEP4 send_pb_file_data fragments   -> response cmd 6 per fragment (status 0 ok, 1 reset)
 *   STEP5 OS_NOITFY_PB_FILE_UPDATE_SUCCESS -> notify cmd 7 (status 0 ok, 1 failed)
 * Fragments accumulate in a 0x5000-byte cache (RAM 0x2031f5e4). A complete,
 * uncompressed file is written to /configure/dashboard_ext.proto.tmp, renamed
 * over /configure/dashboard_ext.proto and reloaded (0x501d5c); the slave then
 * tells its peer on sync channel 0x1f.
 *
 * Already defined elsewhere: dashboard_ext_report_pb_state_to_peer 0x501066
 * (audio_uart_service_prepare9, app/service-prepare9) and
 * dashboard_ext_load_layout_pb_file 0x501d5c (audio_uart_service_prepare8,
 * app/service-prepare8). */
#include <stdint.h>
#include <stddef.h>

#define DASH_EXT_PB_SERVICE 0x1fu
#define DASH_EXT_TX_BUFFER_SIZE 0x400u
#define DASH_EXT_FILE_MAX 0x5000u

/* nanopb 0.4 pb_ostream_t. */
typedef struct {
    void *callback;         /* +0x00 */
    void *state;            /* +0x04 */
    uint32_t max_size;      /* +0x08 */
    uint32_t bytes_written; /* +0x0c */
    const char *errmsg;     /* +0x10 */
} g2_pb_ostream_t;
_Static_assert(sizeof(g2_pb_ostream_t) == 0x14u, "pb_ostream_t is 20 bytes");

/* Decoded tx message (nanopb struct for the descriptor at ROM 0x776664). */
typedef struct {
    uint8_t cmd_id;            /* +0x00 */
    uint8_t reserved_01[3];
    uint32_t magic_random;     /* +0x04 */
    uint16_t which_payload;    /* +0x08 oneof tag */
    uint8_t reserved_0a[2];
    union {
        struct {
            uint32_t exists;   /* +0x0c */
            char text_a[16];   /* +0x10 from 0x5020f0 */
            char text_b[32];   /* +0x20 from 0x502108 */
        } file_info;
        uint32_t status;       /* +0x0c */
        struct {
            uint32_t session;       /* +0x0c */
            uint32_t total;         /* +0x10 */
            uint32_t compress;      /* +0x14 */
            uint32_t frag_idx;      /* +0x18 */
            uint32_t frag_pkt_size; /* +0x1c */
            uint32_t status;        /* +0x20 */
        } data_ack;
        uint8_t raw[0x1018];
    } u;                       /* +0x0c */
} g2_dash_ext_tx_msg_t;
_Static_assert(sizeof(g2_dash_ext_tx_msg_t) == 0x1024u, "dashboard ext tx record is 0x1024 bytes");

/* Layout-PB receive cache. */
typedef struct {
    uint8_t active;            /* +0x00 */
    uint8_t reserved_01[3];
    uint32_t session;          /* +0x04 */
    uint32_t total;            /* +0x08 */
    uint32_t compress;         /* +0x0c */
    uint32_t last_idx;         /* +0x10 */
    uint32_t received;         /* +0x14 */
    uint32_t frags;            /* +0x18 */
    uint8_t data[DASH_EXT_FILE_MAX]; /* +0x1c */
} g2_dash_ext_recv_t;
_Static_assert(sizeof(g2_dash_ext_recv_t) == 0x501cu, "dashboard ext receive cache is 0x501c bytes");

/* STEP4 fragment as handed in by the pb rx dispatcher. */
typedef struct {
    uint32_t session;          /* +0x00 */
    uint32_t total;            /* +0x04 */
    uint32_t compress;         /* +0x08 */
    uint32_t frag_idx;         /* +0x0c */
    uint32_t frag_pkt_size;    /* +0x10 */
    uint16_t raw_len;          /* +0x14 */
    uint8_t data[];            /* +0x16 */
} g2_dash_ext_fragment_t;
_Static_assert(offsetof(g2_dash_ext_fragment_t, data) == 0x16u, "fragment bytes start at +0x16");

extern g2_dash_ext_recv_t g2_dash_ext_recv;            /* RAM 0x2031f5e4 */
extern uint8_t g2_dash_ext_tx_buffer[DASH_EXT_TX_BUFFER_SIZE]; /* RAM 0x2037919c */
extern g2_dash_ext_tx_msg_t g2_dash_ext_tx_msg;        /* RAM 0x20369e1c */
extern uint32_t g2_dash_ext_upgrade_magic;             /* RAM 0x20074430 */
extern const uint8_t g2_dash_ext_pb_fields[];          /* ROM 0x776664 pb_msgdesc_t */

extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* strncpy 0x44b5a0 */
extern void audio_pb_ostream_from_buffer(g2_pb_ostream_t *out, void *buf, uint32_t size); /* 0x4905f4 */
extern uint32_t audio_pb_encode(g2_pb_ostream_t *stream, const void *fields, const void *src); /* 0x490c32 */
extern uint32_t Thread_MsgPbTxByBle(uint8_t type, uint8_t command, const void *payload, uint16_t length);     /* 0x475b14 */
extern uint32_t Thread_MsgPbNotifyByBle(uint8_t type, uint8_t command, const void *payload, uint16_t length); /* 0x475c1a */
extern uint32_t audio_uart_pb_file_exists(void); /* dashboard_layout_pb_file_exists 0x55876a */
extern const char *dashboard_ext_layout_text_a_get_5020f0(void); /* "" until a layout is loaded */
extern const char *dashboard_ext_layout_text_b_get_502108(void); /* "" until a layout is loaded */
extern uint32_t audio_uart_device_role_get(void); /* 0x45a568, 1 = master, 2 = slave */
extern void audio_uart_master_control(uint32_t enable); /* 0x464cba */
extern int32_t DispStartBlockingEn_45bca0(uint32_t timeout_ms);
extern void audio_uart_task_delay(uint32_t ticks); /* 0x454b4c */
extern int32_t dashboard_layout_ensure_configure_dir_558632(void); /* 0 = ok */
extern void *file_open(const char *path, const char *mode);  /* 0x474550 */
extern uint32_t file_write(const void *buf, uint32_t size, uint32_t count, void *file); /* 0x474682 */
extern int32_t file_close(void *file);                       /* 0x4745f4 */
extern int32_t file_remove(const char *path);                /* 0x47498c */
extern int32_t file_rename(const char *from, const char *to); /* 0x474a02 */
extern uint32_t audio_uart_service_prepare8(void); /* dashboard_ext_load_layout_pb_file 0x501d5c */
extern uint32_t audio_uart_handshake_send(uint32_t channel, const void *bytes, uint32_t size, uint32_t flags,
                                          uint32_t timeout); /* 0x465480 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

#define LOG_E(level, fn, line, ...)                                                          \
    do {                                                                                     \
        if (audio_log_flags() & 2u)                                                          \
            audio_log_extended((level), module_tag, source_file, (fn), (line), __VA_ARGS__); \
    } while (0)
#define LOG_C(code, ...)                                                \
    do {                                                                \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))       \
            (void)compress_log_output((code), __VA_ARGS__);             \
    } while (0)

static const char module_tag[] = "dashboard.ext"; /* ROM 0x785900 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard_ext.c"; /* ROM 0x6f9914 */
static const char tx_fn[] = "dashboard_ext_pb_tx_dispatch";              /* ROM 0x75f0b0 */
static const char info_fn[] = "handle_request_pb_file_info";             /* ROM 0x76aa48 */
static const char upgrade_fn[] = "handle_request_upgrade_pb_file";       /* ROM 0x75f0d0 */
static const char start_fn[] = "handle_notify_pb_file_transmit_start";   /* ROM 0x748dcc */
static const char status_fn[] = "handle_notify_pb_file_update_status";   /* ROM 0x75330c */
static const char persist_fn[] = "dashboard_ext_persist_layout_pb_file"; /* ROM 0x748df4 */
static const char complete_fn[] = "check_layout_pb_recv_complete";       /* ROM 0x75f110 */
static const char data_fn[] = "handle_send_pb_file_data";                /* ROM 0x76aa64 */

static const char err_none[] = "(none)"; /* ROM 0x78d2c4 */
static const char encode_failed[] = "pb_encode failed: %s"; /* ROM 0x77646c */
static const char encode_failed_short[] = "[dashboard.ext]pb_encode failed: %s"; /* ROM 0x7532e8 */
static const char str_tx[] = "tx";         /* ROM 0x500bf0 (code pool) */
static const char str_notify[] = "notify"; /* ROM 0x78d2cc */
static const char ble_failed[] = "BLE %s failed, ret = %d"; /* ROM 0x776484 */
static const char ble_failed_short[] = "[dashboard.ext]BLE %s failed, ret = %d"; /* ROM 0x748da4 */
static const char str_notification[] = "notification"; /* ROM 0x785910 */
static const char str_response[] = "response";         /* ROM 0x78a760 */
static const char sent[] = "%s sent: cmd_id=%d, magic_random=%u, bytes=%u"; /* ROM 0x732c24 */
static const char sent_short[] = "[dashboard.ext]%s sent: cmd_id=%d, magic_random=%u, bytes=%u"; /* ROM 0x70a864 */
static const char step1[] = "STEP1: handle APP_REQUEST_PB_FILE_INFO, magic=%u"; /* ROM 0x72854c */
static const char step1_short[] = "[dashboard.ext]STEP1: handle APP_REQUEST_PB_FILE_INFO, magic=%u"; /* ROM 0x70a8a4 */
static const char step2[] = "STEP2: handle APP_REQUEST_UPGRADE_PB_FILE, magic=%u"; /* ROM 0x728580 */
static const char step2_short[] =
    "[dashboard.ext]STEP2: handle APP_REQUEST_UPGRADE_PB_FILE, magic=%u"; /* ROM 0x701b30 */
static const char step3[] = "STEP3: send OS_NOTIFY_PB_FILE_TRANSMIT_START, magic=%u"; /* ROM 0x71d7d8 */
static const char step3_short[] =
    "[dashboard.ext]STEP3: send OS_NOTIFY_PB_FILE_TRANSMIT_START, magic=%u"; /* ROM 0x6f995c */
static const char str_success[] = "success"; /* ROM 0x78d2d4 */
static const char str_failed[] = "failed";   /* ROM 0x78d2dc */
static const char step5[] = "STEP5: send OS_NOITFY_PB_FILE_UPDATE_SUCCESS, magic=%u, cmd=%u(%s)"; /* ROM 0x701b74 */
static const char step5_short[] =
    "[dashboard.ext]STEP5: send OS_NOITFY_PB_FILE_UPDATE_SUCCESS, magic=%u, cmd=%u(%s)"; /* ROM 0x6e7048 */
static const char persist_args[] = "persist layout pb: invalid args data=%p size=%u"; /* ROM 0x732c54 */
static const char persist_args_short[] =
    "[dashboard.ext]persist layout pb: invalid args data=%p size=%u"; /* ROM 0x70a8e4 */
static const char persist_dir[] = "persist layout pb: ensure configure dir failed"; /* ROM 0x732c84 */
static const char persist_dir_short[] =
    "[dashboard.ext]persist layout pb: ensure configure dir failed"; /* ROM 0x70a924 */
static const char tmp_path[] = "/configure/dashboard_ext.proto.tmp"; /* ROM 0x753408 */
static const char mode_wb[] = "wb"; /* ROM 0x500efc (code pool) */
static const char persist_open[] = "persist layout pb: fopen tmp failed: %s"; /* ROM 0x748e1c */
static const char persist_open_short[] = "[dashboard.ext]persist layout pb: fopen tmp failed: %s"; /* ROM 0x71d810 */
static const char persist_short_write[] =
    "persist layout pb: short write/fclose, written=%u/%u, fclose=%d"; /* ROM 0x70a964 */
static const char persist_short_write_short[] =
    "[dashboard.ext]persist layout pb: short write/fclose, written=%u/%u, fclose=%d"; /* ROM 0x6eca28 */
static const char final_path[] = "/configure/dashboard_ext.proto"; /* ROM 0x75f0f0 */
static const char persist_rename[] = "persist layout pb: rename failed: %s -> %s"; /* ROM 0x73d874 */
static const char persist_rename_short[] =
    "[dashboard.ext]persist layout pb: rename failed: %s -> %s"; /* ROM 0x713c84 */
static const char persist_ok[] = "persist layout pb: %u bytes saved to %s"; /* ROM 0x748e44 */
static const char persist_ok_short[] = "[dashboard.ext]persist layout pb: %u bytes saved to %s"; /* ROM 0x71d848 */
static const char recv_done[] = "layout pb file fully received, session=%u total=%u frags=%u"; /* ROM 0x713cc0 */
static const char recv_done_short[] =
    "[dashboard.ext]layout pb file fully received, session=%u total=%u frags=%u"; /* ROM 0x6f2b4c */
static const char recv_compress[] = "layout pb: unsupported compress_mode=%u, skip persistence"; /* ROM 0x713cfc */
static const char recv_compress_short[] =
    "[dashboard.ext]layout pb: unsupported compress_mode=%u, skip persistence"; /* ROM 0x6f2b98 */
static const char recv_persist_failed[] = "layout pb persist failed, file unchanged"; /* ROM 0x73d8a0 */
static const char recv_persist_failed_short[] =
    "[dashboard.ext]layout pb persist failed, file unchanged"; /* ROM 0x71d880 */
static const char s4_null[] = "STEP4: data NULL"; /* ROM 0x77ebcc */
static const char s4_null_short[] = "[dashboard.ext]STEP4: data NULL"; /* ROM 0x75f130 */
static const char s4_hdr[] =
    "STEP4: session=%u total=%u compress=%u frag_idx=%u frag_pkt_size=%u raw=%u"; /* ROM 0x6f2c30 */
static const char s4_hdr_short[] =
    "[dashboard.ext]STEP4: session=%u total=%u compress=%u frag_idx=%u frag_pkt_size=%u raw=%u"; /* ROM 0x6dfefc */
static const char s4_empty[] = "STEP4: empty fragment, ignore (frag_idx=%u)"; /* ROM 0x73d8cc */
static const char s4_empty_short[] = "[dashboard.ext]STEP4: empty fragment, ignore (frag_idx=%u)"; /* ROM 0x713d38 */
static const char s4_range[] = "STEP4: total_size %u out of range (max %u), reset"; /* ROM 0x7285b4 */
static const char s4_range_short[] =
    "[dashboard.ext]STEP4: total_size %u out of range (max %u), reset"; /* ROM 0x701bb8 */
static const char s4_first_idx[] = "STEP4: first packet but frag_idx=%u (expect 0), drop"; /* ROM 0x71d8b8 */
static const char s4_first_idx_short[] =
    "[dashboard.ext]STEP4: first packet but frag_idx=%u (expect 0), drop"; /* ROM 0x701bfc */
static const char s4_first_raw[] = "STEP4: first packet raw=%u > total=%u, drop"; /* ROM 0x73d8f8 */
static const char s4_first_raw_short[] = "[dashboard.ext]STEP4: first packet raw=%u > total=%u, drop"; /* ROM 0x713d74 */
static const char s4_start[] = "STEP4: session %u start, first frag bytes=%u/%u"; /* ROM 0x732cb4 */
static const char s4_start_short[] = "[dashboard.ext]STEP4: session %u start, first frag bytes=%u/%u"; /* ROM 0x70a9e4 */
static const char s4_mismatch[] = "STEP4: session/order mismatch, reset cache"; /* ROM 0x73d924 */
static const char s4_mismatch_short[] = "[dashboard.ext]STEP4: session/order mismatch, reset cache"; /* ROM 0x713db0 */
static const char s4_cached[] = "  cached: sid=%u total=%u compress=%u last_idx=%u"; /* ROM 0x7285e8 */
static const char s4_cached_short[] =
    "[dashboard.ext]  cached: sid=%u total=%u compress=%u last_idx=%u"; /* ROM 0x701c40 */
static const char s4_incoming[] = "  incoming: sid=%u total=%u compress=%u idx=%u"; /* ROM 0x732ce4 */
static const char s4_incoming_short[] = "[dashboard.ext]  incoming: sid=%u total=%u compress=%u idx=%u"; /* ROM 0x70aa24 */
static const char s4_overflow[] = "STEP4: bytes overflow (acc=%u + raw=%u > total=%u / max=%u), reset"; /* ROM 0x701c84 */
static const char s4_overflow_short[] =
    "[dashboard.ext]STEP4: bytes overflow (acc=%u + raw=%u > total=%u / max=%u), reset"; /* ROM 0x6e709c */
static const char s4_ok[] = "STEP4: session %u frag_idx=%u OK, acc=%u/%u, total_frags=%u"; /* ROM 0x713dec */
static const char s4_ok_short[] =
    "[dashboard.ext]STEP4: session %u frag_idx=%u OK, acc=%u/%u, total_frags=%u"; /* ROM 0x6f2c7c */

void dashboard_ext_recv_ctx_reset_500824(void)
{
    (void)aeabi_memset_43c0e4(&g2_dash_ext_recv, sizeof g2_dash_ext_recv, 0);
    g2_dash_ext_recv.active = 0u;
}

/* Encodes g2_dash_ext_tx_msg and sends it as a response (notify = 0) or
 * notification (notify = 1). Returns 0, -1 on encode failure, or the BLE error. */
int32_t dashboard_ext_pb_tx_dispatch_50083e(uint8_t notify)
{
    g2_pb_ostream_t initial;
    g2_pb_ostream_t stream;
    uint32_t ret;

    (void)aeabi_memset_43c0e4(g2_dash_ext_tx_buffer, DASH_EXT_TX_BUFFER_SIZE, 0);
    audio_pb_ostream_from_buffer(&initial, g2_dash_ext_tx_buffer, DASH_EXT_TX_BUFFER_SIZE);
    (void)aeabi_memcpy4_439c04(&stream, &initial, sizeof stream);
    if (audio_pb_encode(&stream, g2_dash_ext_pb_fields, &g2_dash_ext_tx_msg) == 0u) {
        LOG_E(1u, tx_fn, 0x91u, encode_failed, stream.errmsg != NULL ? stream.errmsg : err_none);
        LOG_C(0x04400000u, encode_failed_short, encode_failed_short,
              stream.errmsg != NULL ? stream.errmsg : err_none);
        return -1;
    }
    if (notify)
        ret = Thread_MsgPbNotifyByBle(1u, DASH_EXT_PB_SERVICE, g2_dash_ext_tx_buffer, (uint16_t)stream.bytes_written);
    else
        ret = Thread_MsgPbTxByBle(1u, DASH_EXT_PB_SERVICE, g2_dash_ext_tx_buffer, (uint16_t)stream.bytes_written);
    if (ret != 0u) {
        LOG_E(1u, tx_fn, 0xa3u, ble_failed, notify ? str_notify : str_tx, ret);
        LOG_C(0x04800000u, ble_failed_short, ble_failed_short, notify ? str_notify : str_tx, ret);
        return (int32_t)ret;
    }
    LOG_E(4u, tx_fn, 0xabu, sent, notify ? str_notification : str_response, g2_dash_ext_tx_msg.cmd_id,
          g2_dash_ext_tx_msg.magic_random, stream.bytes_written);
    LOG_C(0x11000000u, sent_short, sent_short, notify ? str_notification : str_response, g2_dash_ext_tx_msg.cmd_id,
          g2_dash_ext_tx_msg.magic_random, stream.bytes_written);
    return 0;
}

void dashboard_ext_pb_tx_response_500a02(void)
{
    (void)dashboard_ext_pb_tx_dispatch_50083e(0u);
}

void dashboard_ext_pb_tx_notify_500a0c(void)
{
    (void)dashboard_ext_pb_tx_dispatch_50083e(1u);
}

static void tx_msg_begin(uint8_t cmd_id, uint32_t magic, uint16_t which)
{
    (void)aeabi_memset_43c0e4(&g2_dash_ext_tx_msg, sizeof g2_dash_ext_tx_msg, 0);
    g2_dash_ext_tx_msg.cmd_id = cmd_id;
    g2_dash_ext_tx_msg.magic_random = magic;
    g2_dash_ext_tx_msg.which_payload = which;
}

/* STEP1 */
void handle_request_pb_file_info_500a16(uint32_t magic)
{
    const char *text_a;
    const char *text_b;

    LOG_E(3u, info_fn, 0xc5u, step1, magic);
    LOG_C(0x0c400000u, step1_short, step1_short, magic);
    tx_msg_begin(1u, magic, 4u);
    g2_dash_ext_tx_msg.u.file_info.exists = (audio_uart_pb_file_exists() != 0u) ? 1u : 0u;
    if (g2_dash_ext_tx_msg.u.file_info.exists == 1u) {
        text_a = dashboard_ext_layout_text_a_get_5020f0();
        text_b = dashboard_ext_layout_text_b_get_502108();
        (void)audio_settings_copy_text(g2_dash_ext_tx_msg.u.file_info.text_a, text_a,
                                       sizeof g2_dash_ext_tx_msg.u.file_info.text_a - 1u);
        g2_dash_ext_tx_msg.u.file_info.text_a[sizeof g2_dash_ext_tx_msg.u.file_info.text_a - 1u] = '\0';
        (void)audio_settings_copy_text(g2_dash_ext_tx_msg.u.file_info.text_b, text_b,
                                       sizeof g2_dash_ext_tx_msg.u.file_info.text_b - 1u);
        g2_dash_ext_tx_msg.u.file_info.text_b[sizeof g2_dash_ext_tx_msg.u.file_info.text_b - 1u] = '\0';
    }
    dashboard_ext_pb_tx_response_500a02();
}

void handle_notify_pb_file_transmit_start_500b7c(uint32_t magic);

/* STEP2: acknowledge, hold the display for up to 10 s, then announce STEP3. */
void handle_request_upgrade_pb_file_500ade(uint32_t magic)
{
    LOG_E(3u, upgrade_fn, 0xf4u, step2, magic);
    LOG_C(0x0c400000u, step2_short, step2_short, magic);
    g2_dash_ext_upgrade_magic = magic;
    tx_msg_begin(3u, magic, 6u);
    g2_dash_ext_tx_msg.u.status = 0u;
    dashboard_ext_pb_tx_response_500a02();
    if (audio_uart_device_role_get() == 1u)
        audio_uart_master_control(0u);
    (void)DispStartBlockingEn_45bca0(10000u);
    audio_uart_task_delay(800u);
    dashboard_ext_recv_ctx_reset_500824();
    handle_notify_pb_file_transmit_start_500b7c(magic);
}

/* STEP3 */
void handle_notify_pb_file_transmit_start_500b7c(uint32_t magic)
{
    LOG_E(3u, start_fn, 0x11fu, step3, magic);
    LOG_C(0x0c400000u, step3_short, step3_short, magic);
    tx_msg_begin(4u, magic, 7u);
    g2_dash_ext_tx_msg.u.status = 1u;
    dashboard_ext_pb_tx_notify_500a0c();
}

/* STEP5: status 0 = updated, 1 = failed. */
void handle_notify_pb_file_update_status_500bf4(uint8_t success)
{
    uint32_t status = success ? 0u : 1u;

    LOG_E(3u, status_fn, 0x142u, step5, g2_dash_ext_upgrade_magic, status, success ? str_success : str_failed);
    LOG_C(0x0cc00000u, step5_short, step5_short, g2_dash_ext_upgrade_magic, status,
          success ? str_success : str_failed);
    tx_msg_begin(7u, g2_dash_ext_upgrade_magic, 10u);
    g2_dash_ext_tx_msg.u.status = status;
    dashboard_ext_pb_tx_notify_500a0c();
}

/* Writes the received layout to the .tmp file and renames it into place. */
int32_t dashboard_ext_persist_layout_pb_file_500cb0(const void *data, uint32_t size)
{
    void *file;
    uint32_t written;
    int32_t rc;

    if (data == NULL || size == 0u) {
        LOG_E(1u, persist_fn, 0x16du, persist_args, data, size);
        LOG_C(0x04800000u, persist_args_short, persist_args_short, data, size);
        return -1;
    }
    if (dashboard_layout_ensure_configure_dir_558632() != 0) {
        LOG_E(1u, persist_fn, 0x172u, persist_dir);
        LOG_C(0x04000000u, persist_dir_short, persist_dir_short);
        return -1;
    }
    (void)file_remove(tmp_path);
    file = file_open(tmp_path, mode_wb);
    if (file == NULL) {
        LOG_E(1u, persist_fn, 0x17du, persist_open, tmp_path);
        LOG_C(0x04400000u, persist_open_short, persist_open_short, tmp_path);
        return -1;
    }
    written = file_write(data, 1u, size, file);
    rc = file_close(file);
    if (written != size || rc != 0) {
        LOG_E(1u, persist_fn, 0x185u, persist_short_write, written, size, rc);
        LOG_C(0x04c00000u, persist_short_write_short, persist_short_write_short, written, size, rc);
        (void)file_remove(tmp_path);
        return -1;
    }
    if (file_rename(tmp_path, final_path) != 0) {
        LOG_E(1u, persist_fn, 0x18fu, persist_rename, tmp_path, final_path);
        LOG_C(0x04800000u, persist_rename_short, persist_rename_short, tmp_path, final_path);
        (void)file_remove(tmp_path);
        return -1;
    }
    LOG_E(3u, persist_fn, 0x195u, persist_ok, size, final_path);
    LOG_C(0x0c800000u, persist_ok_short, persist_ok_short, size, final_path);
    return 0;
}

void check_layout_pb_recv_complete_500f00(void)
{
    uint8_t packet[6];
    int32_t ret;

    if (!g2_dash_ext_recv.active || g2_dash_ext_recv.received != g2_dash_ext_recv.total)
        return;
    LOG_E(3u, complete_fn, 0x1acu, recv_done, g2_dash_ext_recv.session, g2_dash_ext_recv.total,
          g2_dash_ext_recv.frags);
    LOG_C(0x0cc00000u, recv_done_short, recv_done_short, g2_dash_ext_recv.session, g2_dash_ext_recv.total,
          g2_dash_ext_recv.frags);
    if (g2_dash_ext_recv.compress != 0u) {
        LOG_E(2u, complete_fn, 0x1b4u, recv_compress, g2_dash_ext_recv.compress);
        LOG_C(0x08400000u, recv_compress_short, recv_compress_short, g2_dash_ext_recv.compress);
        dashboard_ext_recv_ctx_reset_500824();
        handle_notify_pb_file_update_status_500bf4(0u);
        return;
    }
    ret = dashboard_ext_persist_layout_pb_file_500cb0(g2_dash_ext_recv.data, g2_dash_ext_recv.received);
    dashboard_ext_recv_ctx_reset_500824();
    if (ret != 0) {
        LOG_E(1u, complete_fn, 0x1c1u, recv_persist_failed);
        LOG_C(0x04000000u, recv_persist_failed_short, recv_persist_failed_short);
        handle_notify_pb_file_update_status_500bf4(0u);
        return;
    }
    (void)audio_uart_service_prepare8();
    if (audio_uart_device_role_get() == 2u) {
        /* Slave: tell the peer the layout file changed (record 1). */
        audio_uart_task_delay(100u);
        (void)aeabi_memset_43c0e4(packet, sizeof packet, 0);
        (void)aeabi_memset_43c0e4(packet, sizeof packet, 0);
        packet[0] = 1u;
        (void)audio_uart_handshake_send(DASH_EXT_PB_SERVICE, packet, sizeof packet, 0u, 5u);
    }
}

/* STEP4 per-fragment response, status 0 = accepted, 1 = cache reset. */
void dashboard_ext_send_pb_file_data_ack_501108(uint32_t magic, uint32_t session, uint32_t total,
                                                uint32_t compress, uint32_t frag_idx, uint32_t frag_pkt_size,
                                                uint32_t status)
{
    tx_msg_begin(6u, magic, 9u);
    g2_dash_ext_tx_msg.u.data_ack.session = session;
    g2_dash_ext_tx_msg.u.data_ack.total = total;
    g2_dash_ext_tx_msg.u.data_ack.compress = compress;
    g2_dash_ext_tx_msg.u.data_ack.frag_idx = frag_idx;
    g2_dash_ext_tx_msg.u.data_ack.frag_pkt_size = frag_pkt_size;
    g2_dash_ext_tx_msg.u.data_ack.status = status;
    dashboard_ext_pb_tx_response_500a02();
}

/* STEP4: fragments must arrive in order (idx 0 opens a session; each next idx
 * is last_idx + 1 with the same session/total/compress). Any error resets the
 * cache and answers status 1. */
void handle_send_pb_file_data_5011d0(uint32_t magic, const g2_dash_ext_fragment_t *frag)
{
    uint32_t session;
    uint32_t total;
    uint32_t compress;
    uint32_t frag_idx;
    uint32_t frag_pkt_size;
    uint32_t raw;
    g2_dash_ext_recv_t *ctx;

    if (frag == NULL) {
        LOG_E(1u, data_fn, 0x20fu, s4_null);
        LOG_C(0x04000000u, s4_null_short, s4_null_short);
        return;
    }
    session = frag->session;
    total = frag->total;
    compress = frag->compress;
    frag_idx = frag->frag_idx;
    frag_pkt_size = frag->frag_pkt_size;
    raw = frag->raw_len;
    LOG_E(4u, data_fn, 0x21du, s4_hdr, session, total, compress, frag_idx, frag_pkt_size, raw);
    LOG_C(0x11800000u, s4_hdr_short, s4_hdr_short, session, total, compress, frag_idx, frag_pkt_size, raw);

    if (raw == 0u) {
        LOG_E(2u, data_fn, 0x221u, s4_empty, frag_idx);
        LOG_C(0x08400000u, s4_empty_short, s4_empty_short, frag_idx);
        dashboard_ext_recv_ctx_reset_500824();
        dashboard_ext_send_pb_file_data_ack_501108(magic, session, total, compress, frag_idx, frag_pkt_size, 1u);
        return;
    }
    if (total == 0u || total > DASH_EXT_FILE_MAX) {
        LOG_E(1u, data_fn, 0x22bu, s4_range, total, DASH_EXT_FILE_MAX);
        LOG_C(0x04800000u, s4_range_short, s4_range_short, total, DASH_EXT_FILE_MAX);
        dashboard_ext_recv_ctx_reset_500824();
        dashboard_ext_send_pb_file_data_ack_501108(magic, session, total, compress, frag_idx, frag_pkt_size, 1u);
        return;
    }

    ctx = &g2_dash_ext_recv;
    if (!ctx->active) {
        if (frag_idx != 0u) {
            LOG_E(2u, data_fn, 0x236u, s4_first_idx, frag_idx);
            LOG_C(0x08400000u, s4_first_idx_short, s4_first_idx_short, frag_idx);
            dashboard_ext_recv_ctx_reset_500824();
            dashboard_ext_send_pb_file_data_ack_501108(magic, session, total, compress, frag_idx, frag_pkt_size,
                                                       1u);
            return;
        }
        if (total < raw) {
            LOG_E(1u, data_fn, 0x23fu, s4_first_raw, raw, total);
            LOG_C(0x04800000u, s4_first_raw_short, s4_first_raw_short, raw, total);
            dashboard_ext_recv_ctx_reset_500824();
            dashboard_ext_send_pb_file_data_ack_501108(magic, session, total, compress, frag_idx, frag_pkt_size,
                                                       1u);
            return;
        }
        dashboard_ext_recv_ctx_reset_500824();
        ctx->active = 1u;
        ctx->session = session;
        ctx->total = total;
        ctx->compress = compress;
        ctx->last_idx = frag_idx;
        ctx->frags = 1u;
        (void)audio_queue_copy_bytes(ctx->data, frag->data, raw);
        ctx->received = raw;
        LOG_E(3u, data_fn, 0x253u, s4_start, session, raw, total);
        LOG_C(0x0cc00000u, s4_start_short, s4_start_short, session, raw, total);
        dashboard_ext_send_pb_file_data_ack_501108(magic, session, total, compress, frag_idx, frag_pkt_size, 0u);
        check_layout_pb_recv_complete_500f00();
        return;
    }

    if (ctx->session != session || ctx->total != total || ctx->compress != compress ||
        ctx->last_idx + 1u != frag_idx) {
        LOG_E(2u, data_fn, 0x262u, s4_mismatch);
        LOG_C(0x08000000u, s4_mismatch_short, s4_mismatch_short);
        LOG_E(2u, data_fn, 0x267u, s4_cached, ctx->session, ctx->total, ctx->compress, ctx->last_idx);
        LOG_C(0x09000000u, s4_cached_short, s4_cached_short, ctx->session, ctx->total, ctx->compress,
              ctx->last_idx);
        LOG_E(2u, data_fn, 0x26au, s4_incoming, session, total, compress, frag_idx);
        LOG_C(0x09000000u, s4_incoming_short, s4_incoming_short, session, total, compress, frag_idx);
        dashboard_ext_recv_ctx_reset_500824();
        dashboard_ext_send_pb_file_data_ack_501108(magic, session, total, compress, frag_idx, frag_pkt_size, 1u);
        return;
    }
    if (total < raw + ctx->received) {
        LOG_E(1u, data_fn, 0x276u, s4_overflow, ctx->received, raw, total, DASH_EXT_FILE_MAX);
        LOG_C(0x05000000u, s4_overflow_short, s4_overflow_short, ctx->received, raw, total, DASH_EXT_FILE_MAX);
        dashboard_ext_recv_ctx_reset_500824();
        dashboard_ext_send_pb_file_data_ack_501108(magic, session, total, compress, frag_idx, frag_pkt_size, 1u);
        return;
    }
    (void)audio_queue_copy_bytes(&ctx->data[ctx->received], frag->data, raw);
    ctx->received = raw + ctx->received;
    ctx->last_idx = frag_idx;
    ctx->frags++;
    LOG_E(4u, data_fn, 0x289u, s4_ok, ctx->session, frag_idx, ctx->received, ctx->total, ctx->frags);
    LOG_C(0x11400000u, s4_ok_short, s4_ok_short, ctx->session, frag_idx, ctx->received, ctx->total, ctx->frags);
    dashboard_ext_send_pb_file_data_ack_501108(magic, session, total, compress, frag_idx, frag_pkt_size, 0u);
    check_layout_pb_recv_complete_500f00();
}
