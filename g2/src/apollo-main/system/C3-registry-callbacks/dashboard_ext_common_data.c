/* dashboard_ext_common_data_handler, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_ext.c.
 * Native 0x501820..0x501d09; literal pool words in the shared dashboard_ext.c pool
 * 0x501d18..0x50261b. The rest of the TU is app/a-39-dashboard-ext/dashboard_ext_pb_file.c.
 * UI registry row 04 (pb service 0x1f) primary handler. Reconstructed 2026-10-21 (C3)
 * from the 2.2.6.10 disassembly; compiles, byte identity not established.
 *
 * Registry primary handler ABI: (event type, data, length); always returns 0.
 *   event 5 (peer sync record from the other arm, first byte = record id):
 *     1 update-success: cancel display blocking, notify the phone (STEP5 ok), master
 *       starts the dashboard display;
 *     3 peer state (master only, byte 1 = slave has the layout file): the arm that still
 *       has dashboard_ext.proto deletes it locally (master) or tells the slave to delete
 *       it (record 4) so both arms stay consistent;
 *     4 delete command (slave only): delete the local layout file.
 *   event 0 (phone pb frame): nanopb-decode a DashboardExtPackage into RAM 0x20368df8 and
 *     dispatch STEP1/STEP2/STEP4 by cmd_id; OS->APP cmd ids are ignored. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define DASH_EXT_PB_SERVICE 0x1fu
#define DASH_EXT_EVENT_PB_FRAME 0u
#define DASH_EXT_EVENT_PEER 5u
#define DASH_EXT_WHICH_FILE_DATA 8u
#define DEVICE_ROLE_MASTER 1u
#define DEVICE_ROLE_SLAVE 2u

/* Peer sync record ids (first byte, sync channel 0x1f). */
#define DASH_EXT_PEER_UPDATE_SUCCESS 1u
#define DASH_EXT_PEER_STATE 3u
#define DASH_EXT_PEER_DELETE 4u

/* DashboardExtPackage cmd ids. */
#define DASH_EXT_CMD_APP_REQUEST_PB_FILE_INFO 0u
#define DASH_EXT_CMD_APP_REQUEST_UPGRADE_PB_FILE 2u
#define DASH_EXT_CMD_APP_SEND_PB_FILE_DATA 5u
#define DASH_EXT_CMD_LAST 7u

/* nanopb 0.4 pb_istream_t. */
typedef struct g2_pb_istream {
    bool (*callback)(struct g2_pb_istream *stream, uint8_t *buf, size_t count);
    void *state;
    size_t bytes_left;
    const char *errmsg; /* +0x0c */
} g2_pb_istream_t;
_Static_assert(sizeof(g2_pb_istream_t) == 16u, "pb_istream_t ABI");

/* Decoded DashboardExtPackage (same nanopb struct as the tx record in dashboard_ext_pb_file.c). */
typedef struct {
    uint8_t cmd_id;         /* +0x00 */
    uint8_t reserved_01[3];
    uint32_t magic_random;  /* +0x04 */
    uint16_t which_payload; /* +0x08 oneof tag */
    uint8_t reserved_0a[2];
    uint8_t payload[0x1018]; /* +0x0c; APP_SEND_PB_FILE_DATA fragment for which 8 */
} g2_dash_ext_rx_msg_t;
_Static_assert(sizeof(g2_dash_ext_rx_msg_t) == 0x1024u, "dashboard ext rx record is 0x1024 bytes");

extern g2_dash_ext_rx_msg_t g2_dash_ext_rx_msg_20368df8; /* RAM 0x20368df8 */
extern volatile uint8_t audio_uart_dashboard_ready;      /* RAM 0x20074fa5 */
extern const uint8_t g2_dash_ext_pb_fields[];            /* ROM 0x776664 pb_msgdesc_t */

extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* memset 0x43c0e4 */
extern g2_pb_istream_t pb_istream_from_buffer(const uint8_t *buf, size_t msglen); /* 0x48f49c */
extern bool pb_decode(g2_pb_istream_t *stream, const void *fields, void *dest);  /* 0x490120 */
extern uint32_t audio_uart_device_role_get(void); /* 0x45a568, 1 = master, 2 = slave */
extern uint32_t audio_uart_pb_file_exists(void);  /* dashboard_layout_pb_file_exists 0x55876a */
extern int32_t dashboard_layout_pb_file_delete_558804(void);
extern void DispStartBlockingCancel_45be6c(void);
extern void audio_uart_master_display_start(uint32_t id, const void *payload, uint16_t length,
                                            uint32_t extra); /* MasterDisplayStart 0x464b2e */
extern uint32_t audio_uart_handshake_send(uint32_t channel, const void *bytes, uint32_t size, uint32_t flags,
                                          uint32_t timeout); /* 0x465480 */
extern void handle_request_pb_file_info_500a16(uint32_t magic);
extern void handle_request_upgrade_pb_file_500ade(uint32_t magic);
extern void handle_notify_pb_file_update_status_500bf4(uint8_t success);
extern void handle_send_pb_file_data_5011d0(uint32_t magic, const void *frag); /* g2_dash_ext_fragment_t */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *,
                               ...);                                            /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char tag[] = "dashboard.ext"; /* ROM 0x785900 */
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard_ext.c"; /* ROM 0x6f9914 */
static const char fn[] = "dashboard_ext_common_data_handler"; /* ROM 0x753330 */
static const char bad_params[] = "invalid params: raw_data=%p, len=%u"; /* ROM 0x753354 */
static const char bad_params_s[] = "[dashboard.ext]invalid params: raw_data=%p, len=%u"; /* ROM 0x72861c */
static const char update_ok[] = "dashboard_ext recv: DASHBOARD_EXT_PB_FILE_UPDATE_SUCCESS_DATA_PACKET"; /* ROM 0x6f99a4 */
static const char update_ok_s[] =
    "[dashboard.ext]dashboard_ext recv: DASHBOARD_EXT_PB_FILE_UPDATE_SUCCESS_DATA_PACKET"; /* ROM 0x6e70f0 */
static const char peer_state[] = "dashboard_ext recv PEER_STATE: master_exists=%d slave_exists=%d"; /* ROM 0x70aa64 */
static const char peer_state_s[] =
    "[dashboard.ext]dashboard_ext recv PEER_STATE: master_exists=%d slave_exists=%d"; /* ROM 0x6eca78 */
static const char slave_lost[] = "[SEVERE] slave lost dashboard_ext.proto (suspect FS bad-link format), "
                                 "master deletes local file to keep consistency"; /* ROM 0x69edf4 */
static const char slave_lost_s[] = "[dashboard.ext][SEVERE] slave lost dashboard_ext.proto (suspect FS bad-link "
                                   "format), master deletes local file to keep consistency"; /* ROM 0x6d4cac */
static const char master_lost[] = "[SEVERE] master lost dashboard_ext.proto (suspect FS bad-link format), "
                                  "command slave to delete to keep consistency"; /* ROM 0x69f1ec */
static const char master_lost_s[] = "[dashboard.ext][SEVERE] master lost dashboard_ext.proto (suspect FS bad-link "
                                    "format), command slave to delete to keep consistency"; /* ROM 0x6d4d30 */
static const char slave_delete[] = "[SEVERE] received master delete command, slave deletes local "
                                   "dashboard_ext.proto to keep consistency"; /* ROM 0x6d8934 */
static const char slave_delete_s[] = "[dashboard.ext][SEVERE] received master delete command, slave deletes local "
                                     "dashboard_ext.proto to keep consistency"; /* ROM 0x69f5e4 */
static const char none[] = "(none)"; /* ROM 0x78d2c4 */
static const char decode_failed[] = "DashboardExtPackage decode failed: %s"; /* ROM 0x748e94 */
static const char decode_failed_s[] = "[dashboard.ext]DashboardExtPackage decode failed: %s"; /* ROM 0x71d8f0 */
static const char decoded[] = "DashboardExtPackage decoded: cmd_id=%d, magic_random=%u, which=%d"; /* ROM 0x701cc8 */
static const char decoded_s[] =
    "[dashboard.ext]DashboardExtPackage decoded: cmd_id=%d, magic_random=%u, which=%d"; /* ROM 0x6e7144 */
static const char which_mismatch[] = "cmd APP_SEND_PB_FILE_DATA but which_msg_type=%d mismatch"; /* ROM 0x713e28 */
static const char which_mismatch_s[] =
    "[dashboard.ext]cmd APP_SEND_PB_FILE_DATA but which_msg_type=%d mismatch"; /* ROM 0x6f99ec */
static const char ignore[] = "received OS->APP cmd_id=%d, ignore"; /* ROM 0x753378 */
static const char ignore_s[] = "[dashboard.ext]received OS->APP cmd_id=%d, ignore"; /* ROM 0x728650 */
static const char unknown_cmd[] = "unknown cmd_id=%d"; /* ROM 0x77ebe0 */
static const char unknown_cmd_s[] = "[dashboard.ext]unknown cmd_id=%d"; /* ROM 0x75339c */
static const char unknown_event[] = "unknown eventType=%d"; /* ROM 0x77649c */
static const char unknown_event_s[] = "[dashboard.ext]unknown eventType=%d"; /* ROM 0x7533c0 */

#define DX_LOG(level, line, cflags, text, short_text, ...)                                  \
    do {                                                                                    \
        if ((audio_log_flags() & 2u) != 0u)                                                 \
            audio_log_extended((level), tag, file, fn, (line), (text), ##__VA_ARGS__);      \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)               \
            (void)compress_log_output((cflags), (short_text), (short_text), ##__VA_ARGS__); \
    } while (0)

uint32_t audio_uart_registry_callback_501820(uint32_t event, const uint8_t *raw_data, uint32_t len);

static void dashboard_ext_peer_record(const uint8_t *raw_data, uint32_t len)
{
    if (raw_data[0] == DASH_EXT_PEER_UPDATE_SUCCESS) {
        DX_LOG(3u, 0x2a4u, 0x0c000000u, update_ok, update_ok_s);
        DispStartBlockingCancel_45be6c();
        handle_notify_pb_file_update_status_500bf4(1u);
        if (audio_uart_device_role_get() == DEVICE_ROLE_MASTER)
            audio_uart_master_display_start(1u, NULL, 0u, 0u);
    } else if (raw_data[0] == DASH_EXT_PEER_STATE) {
        uint8_t slave_exists;
        uint8_t master_exists;
        if (audio_uart_device_role_get() != DEVICE_ROLE_MASTER || len < 2u)
            return;
        slave_exists = raw_data[1] != 0u ? 1u : 0u;
        master_exists = (uint8_t)audio_uart_pb_file_exists();
        DX_LOG(3u, 0x2b3u, 0x0c800000u, peer_state, peer_state_s, master_exists, slave_exists);
        if (master_exists != 0u && slave_exists == 0u) {
            DX_LOG(1u, 0x2b7u, 0x04000000u, slave_lost, slave_lost_s);
            (void)dashboard_layout_pb_file_delete_558804();
            audio_uart_dashboard_ready = 0u;
        } else if (master_exists == 0u && slave_exists != 0u) {
            uint8_t packet[6];
            DX_LOG(1u, 0x2bdu, 0x04000000u, master_lost, master_lost_s);
            audio_uart_dashboard_ready = 0u;
            audio_uart_buffer_zero(packet, sizeof packet, 0u);
            packet[0] = DASH_EXT_PEER_DELETE;
            (void)audio_uart_handshake_send(DASH_EXT_PB_SERVICE, packet, sizeof packet, 0u, 5u);
        }
    } else if (raw_data[0] == DASH_EXT_PEER_DELETE) {
        if (audio_uart_device_role_get() == DEVICE_ROLE_SLAVE && audio_uart_pb_file_exists() != 0u) {
            DX_LOG(1u, 0x2cdu, 0x04000000u, slave_delete, slave_delete_s);
            (void)dashboard_layout_pb_file_delete_558804();
            audio_uart_dashboard_ready = 0u;
        }
    }
}

/* Stock 0x00501820 (dashboard_ext_common_data_handler) */
uint32_t audio_uart_registry_callback_501820(uint32_t event, const uint8_t *raw_data, uint32_t len)
{
    g2_dash_ext_rx_msg_t *msg = &g2_dash_ext_rx_msg_20368df8;
    g2_pb_istream_t stream;
    uint32_t magic;

    if (raw_data == NULL || len == 0u) {
        DX_LOG(1u, 0x29du, 0x04800000u, bad_params, bad_params_s, raw_data, len);
        return 0u;
    }
    if (event == DASH_EXT_EVENT_PEER) {
        dashboard_ext_peer_record(raw_data, len);
        return 0u;
    }
    if (event != DASH_EXT_EVENT_PB_FRAME) {
        DX_LOG(2u, 0x305u, 0x08400000u, unknown_event, unknown_event_s, event);
        return 0u;
    }

    audio_uart_buffer_zero(msg, sizeof *msg, 0u);
    stream = pb_istream_from_buffer(raw_data, len);
    if (!pb_decode(&stream, g2_dash_ext_pb_fields, msg)) {
        DX_LOG(1u, 0x2d9u, 0x04400000u, decode_failed, decode_failed_s,
               stream.errmsg != NULL ? stream.errmsg : none);
        return 0u;
    }
    DX_LOG(4u, 0x2e0u, 0x10c00000u, decoded, decoded_s, msg->cmd_id, msg->magic_random, msg->which_payload);
    magic = msg->magic_random;
    switch (msg->cmd_id) {
    case DASH_EXT_CMD_APP_REQUEST_PB_FILE_INFO:
        handle_request_pb_file_info_500a16(magic);
        break;
    case DASH_EXT_CMD_APP_REQUEST_UPGRADE_PB_FILE:
        handle_request_upgrade_pb_file_500ade(magic);
        break;
    case DASH_EXT_CMD_APP_SEND_PB_FILE_DATA:
        if (msg->which_payload == DASH_EXT_WHICH_FILE_DATA)
            handle_send_pb_file_data_5011d0(magic, msg->payload);
        else
            DX_LOG(2u, 0x2f2u, 0x08400000u, which_mismatch, which_mismatch_s, msg->which_payload);
        break;
    case 1u:
    case 3u:
    case 4u:
    case 6u:
    case DASH_EXT_CMD_LAST:
        DX_LOG(2u, 0x2fdu, 0x08400000u, ignore, ignore_s, msg->cmd_id);
        break;
    default:
        DX_LOG(2u, 0x301u, 0x08400000u, unknown_cmd, unknown_cmd_s, msg->cmd_id);
        break;
    }
    return 0u;
}
