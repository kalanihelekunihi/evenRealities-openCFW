/* Production peer-sync handler, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\ux\ux_production\ux_production.c
 * (UX_LocalProductionSyncHandler). Native 0x5f9924..0x5f9c25; literal pool
 * 0x5f9c28..0x5f9c8b. The inventory row 0x5f98d0 starts inside the literal
 * pool of UX_BatterySyncHandler (0x5f98d0..0x5f9923 is data).
 *
 * Registered for sync application 0x102 in the UI registry (ROM 0x6a4700).
 * Commands: OPEN_MIC / CLOSE_MIC drive GPIO 134; DEVICE_SYNC_TEST with
 * payload 0xAA ("send") is answered with a DEVICE_SYNC_TEST carrying 0x55
 * ("recv"), and receiving 0x55 sets the flag the production test polls. */
#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint16_t command;      /* +0x0 eProductionCommandId */
    uint16_t msg_len;      /* +0x2 */
    uint8_t msg_self_role; /* +0x4 */
    uint8_t msg_peer_role; /* +0x5 */
    uint8_t reserved[2];   /* +0x6 */
    const uint8_t *msg_buf; /* +0x8 */
} g2_production_msg_t;
_Static_assert(sizeof(g2_production_msg_t) == 12u, "production sync message is 12 bytes");

enum {
    PRODUCTION_OPEN_MIC = 1,
    PRODUCTION_CLOSE_MIC = 2,
    PRODUCTION_DEVICE_SYNC_TEST = 3,
};
#define PRODUCTION_SYNC_APP 0x102u
#define DEVICE_SYNC_SEND_DATA 0xaau
#define DEVICE_SYNC_RECV_DATA 0x55u
#define MASTER_ROLE 1u
#define MIC_POWER_PIN 134u

extern uint8_t g2_production_sync_recv_data;           /* RAM 0x20004557, initialised to 0x55 */
extern volatile uint8_t g2_pt_peer_sync_ack_20075004;  /* RAM 0x20075004 device_sync_test_flag */

extern uint8_t audio_uart_device_role_get(void); /* 0x45a568, 1 = master */
extern uint32_t g2_codec_pin_write(uint32_t pin, uint32_t value); /* 0x53a5be */
extern uint32_t audio_uart_request_send(uint32_t app, const void *data, uint32_t len, uint32_t flags); /* 0x4651e0 */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* ROM 0x78c8f0: {3, 1, 0, 0, {0, 0}, &g2_production_sync_recv_data}. */
static const g2_production_msg_t sync_recv_reply = {
    PRODUCTION_DEVICE_SYNC_TEST, 1u, 0u, 0u, {0u, 0u}, &g2_production_sync_recv_data};

static const char module_tag[] = "ux.production"; /* ROM 0x789f10 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\ux\\ux_production\\ux_production.c"; /* ROM 0x6f7ca4 */
static const char handler_fn[] = "UX_LocalProductionSyncHandler"; /* ROM 0x7680b0 */
static const char raw_fmt[] = "raw_data = 0x%x,len = %d"; /* ROM 0x774704 */
static const char raw_fmt_short[] = "[ux.production]raw_data = 0x%x,len = %d"; /* ROM 0x751364 */
static const char self_fmt[] = "pMsg->head.msg_self_role = %d(MASTER_ROLE = %d)"; /* ROM 0x73b564 */
static const char self_fmt_short[] = "[ux.production]pMsg->head.msg_self_role = %d(MASTER_ROLE = %d)"; /* ROM 0x711c24 */
static const char peer_fmt[] = "pMsg->head.msg_peer_role = %d %d"; /* ROM 0x75d2a8 */
static const char peer_fmt_short[] = "[ux.production]pMsg->head.msg_peer_role = %d %d"; /* ROM 0x73b594 */
static const char open_mic[] = "eProductionCommandId_OPEN_MIC"; /* ROM 0x7680d0 */
static const char open_mic_short[] = "[ux.production]eProductionCommandId_OPEN_MIC"; /* ROM 0x73b5c4 */
static const char close_mic[] = "eDevCfgCommandId_PRODUCTION_CLOSE_MIC"; /* ROM 0x75138c */
static const char close_mic_short[] = "[ux.production]eDevCfgCommandId_PRODUCTION_CLOSE_MIC"; /* ROM 0x726100 */
static const char sync_test[] = "eProductionCommandId_DEVICE_SYNC_TEST"; /* ROM 0x7513b4 */
static const char sync_test_short[] = "[ux.production]eProductionCommandId_DEVICE_SYNC_TEST"; /* ROM 0x726138 */
static const char len_invalid[] = "pMsg->head.msg_len is invalid"; /* ROM 0x7680f0 */
static const char len_invalid_short[] = "[ux.production]pMsg->head.msg_len is invalid"; /* ROM 0x73b5f4 */
static const char buf_fmt[] = "pMsg->msg_buf[0] = %d"; /* ROM 0x77d7d4 */
static const char buf_fmt_short[] = "[ux.production]pMsg->msg_buf[0] = %d"; /* ROM 0x7513dc */
static const char send_data[] = "DEVICE_SYNC_SEND_DATA, send DEVICE_SYNC_RECV_DATA"; /* ROM 0x730c94 */
static const char send_data_short[] = "[ux.production]DEVICE_SYNC_SEND_DATA, send DEVICE_SYNC_RECV_DATA"; /* ROM 0x708708 */
static const char recv_data[] = "DEVICE_SYNC_RECV_DATA, set device_sync_test_flag = true"; /* ROM 0x726170 */
static const char recv_data_short[] = "[ux.production]DEVICE_SYNC_RECV_DATA, set device_sync_test_flag = true"; /* ROM 0x6ff62c */

#define LOG_COMPRESSED() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

/* UX_LocalProductionSyncHandler(context, msg, len): 0, or -1 for a malformed
 * DEVICE_SYNC_TEST. */
uint32_t audio_uart_registry_callback_5f9924(void *context, const g2_production_msg_t *msg, uint32_t len)
{
    (void)context;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, handler_fn, 21u, raw_fmt, msg, len);
    if (LOG_COMPRESSED())
        (void)compress_log_output(0x10800000u, raw_fmt_short, raw_fmt_short, msg, len);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, handler_fn, 22u, self_fmt, msg->msg_self_role, MASTER_ROLE);
    if (LOG_COMPRESSED())
        (void)compress_log_output(0x10800000u, self_fmt_short, self_fmt_short, msg->msg_self_role, MASTER_ROLE);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, handler_fn, 23u, peer_fmt, msg->msg_peer_role,
                           audio_uart_device_role_get());
    if (LOG_COMPRESSED())
        (void)compress_log_output(0x10800000u, peer_fmt_short, peer_fmt_short, msg->msg_peer_role,
                                  audio_uart_device_role_get());

    switch (msg->command) {
    case PRODUCTION_OPEN_MIC:
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module_tag, source_file, handler_fn, 28u, open_mic);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0xc000000u, open_mic_short, open_mic_short);
        (void)g2_codec_pin_write(MIC_POWER_PIN, 1u);
        break;
    case PRODUCTION_CLOSE_MIC:
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module_tag, source_file, handler_fn, 34u, close_mic);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0xc000000u, close_mic_short, close_mic_short);
        (void)g2_codec_pin_write(MIC_POWER_PIN, 0u);
        break;
    case PRODUCTION_DEVICE_SYNC_TEST:
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module_tag, source_file, handler_fn, 40u, sync_test);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0xc000000u, sync_test_short, sync_test_short);
        if (msg->msg_len != 1u || msg->msg_buf == NULL) {
            if (audio_log_flags() & 2u)
                audio_log_extended(1u, module_tag, source_file, handler_fn, 44u, len_invalid);
            if (LOG_COMPRESSED())
                (void)compress_log_output(0x4000000u, len_invalid_short, len_invalid_short);
            return 0xffffffffu;
        }
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module_tag, source_file, handler_fn, 47u, buf_fmt, msg->msg_buf[0]);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0xc400000u, buf_fmt_short, buf_fmt_short, msg->msg_buf[0]);
        if (msg->msg_buf[0] == DEVICE_SYNC_SEND_DATA) {
            if (audio_log_flags() & 2u)
                audio_log_extended(3u, module_tag, source_file, handler_fn, 50u, send_data);
            if (LOG_COMPRESSED())
                (void)compress_log_output(0xc000000u, send_data_short, send_data_short);
            g2_production_msg_t reply = sync_recv_reply;
            reply.msg_self_role = audio_uart_device_role_get();
            reply.msg_peer_role = audio_uart_device_role_get() == MASTER_ROLE ? 2u : 1u;
            (void)audio_uart_request_send(PRODUCTION_SYNC_APP, &reply, sizeof reply, 0u);
        } else if (msg->msg_buf[0] == DEVICE_SYNC_RECV_DATA) {
            if (audio_log_flags() & 2u)
                audio_log_extended(3u, module_tag, source_file, handler_fn, 63u, recv_data);
            if (LOG_COMPRESSED())
                (void)compress_log_output(0xc000000u, recv_data_short, recv_data_short);
            g2_pt_peer_sync_ack_20075004 = 1u;
        }
        break;
    default:
        break;
    }
    return 0u;
}
