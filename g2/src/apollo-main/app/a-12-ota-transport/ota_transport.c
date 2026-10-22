/* OTA service BLE transport framing, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\ota_service\ota_transport.c
 * (log tag "ota.tran"). Native 0x48d87c..0x48e0ab, literal pool
 * 0x48e0ac..0x48e153.
 *
 * Frame (8-byte header, payload, CRC on the final frame):
 *   +0 0xAA magic        +1 low nibble 2 (service), high nibble = type
 *   +2 sync id           +3 payload length (final frame: +2 for the CRC)
 *   +4 total frames      +5 frame number (1-based)
 *   +6 command           +7 bit0 notify flag, bit5 "no callback" on 0xC0/0xC2
 *   +8 payload ...       final frame: payload, then CRC16 (seed 0, LE)
 * RX commands: 0xC0 single-frame control (payload byte 0 == 2 opens a
 * reassembly into the 0x1020-byte static buffer), 0xC1 multi-frame data with
 * a 1500 ms inter-frame timeout, 0xC2 single-frame control. TX splits the
 * payload into (ATT MTU - 11)-byte frames.
 * Return codes: 0 ok, 1 CRC error, 4 no resource, 8 not authenticated,
 * 10 bad magic, 11 bad argument, else the transport TX error. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define OTA_FRAME_MAGIC 0xaau
#define OTA_FRAME_HEADER_LEN 8u
#define OTA_CMD_CONTROL 0xc0u
#define OTA_CMD_DATA 0xc1u
#define OTA_CMD_CONTROL2 0xc2u
#define OTA_RX_BUFFER_LEN 0x1020u
#define OTA_TX_FRAME_LEN 0xf7u
#define OTA_RX_FRAME_TIMEOUT_MS 1500u

/* Transport callbacks (RAM 0x20003058) installed by the OTA service. */
typedef struct {
    void (*rx)(uint8_t command, const uint8_t *data, uint16_t length);  /* +0 */
    uint8_t (*tx)(const uint8_t *frame, uint16_t length);               /* +4 */
} g2_ota_transport_cb_t;
_Static_assert(sizeof(g2_ota_transport_cb_t) == 8u, "OTA transport callbacks");

extern g2_ota_transport_cb_t g2_ota_transport_callbacks_20003058; /* RAM 0x20003058 */
extern uint8_t *g2_ota_rx_static_buf_2000304c;    /* RAM 0x2000304c, 0x1020-byte RX buffer */
extern uint8_t *g2_ota_tx_data_buf_20003050;      /* RAM 0x20003050, 0x1020-byte TX copy */
extern uint8_t *g2_ota_tx_frame_buf_20003054;     /* RAM 0x20003054, 0xf7-byte TX frame */
extern uint32_t g2_ota_rx_total_len_20074850;     /* RAM 0x20074850, _g_totalLenRx */
extern uint8_t *g2_ota_rx_data_buf_20074854;      /* RAM 0x20074854, pDataBuf */
extern uint8_t g2_ota_rx_active_20074ff4;         /* RAM 0x20074ff4 */
extern uint8_t g2_ota_rx_error_pending_20074ff5;  /* RAM 0x20074ff5 */
extern uint8_t g2_ota_rx_error_sync_id_20074ff6;  /* RAM 0x20074ff6 */
extern uint8_t g2_ota_sync_id_20074ff7;           /* RAM 0x20074ff7 */
extern uint8_t g2_ota_shared_buffer_20354c78[];   /* RAM 0x20354c78 */

extern uint16_t audio_uart_hand_checksum_49acd4(const void *data, uint32_t length,
                                                const uint16_t *seed); /* CRC16 */
extern uint16_t slave_cmd_pipe_get_0046f2c6(void); /* negotiated ATT MTU */
extern void semantic_OtaNotifyStatus3(uint8_t command); /* 0x44871a, CRC error reply */
extern void semantic_OtaNotifyStatus4(uint8_t command); /* 0x4486ec, timeout reply */
extern void semantic_OtaNotifyStatus5(uint8_t command); /* 0x44874c, no-resource reply */
extern void fw_event_loop_push_delayed(void (*callback)(void), uint32_t argument,
                                       uint32_t delay_ms);                 /* 0x47697e */
extern uint32_t fw_event_loop_remove_delayed(void (*callback)(void));      /* 0x476ace */
extern void file_heap_free(void *buffer);                                  /* 0x474d16 */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* memset 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t level, const char *module, const char *file,
                               const char *function, uint32_t line,
                               const char *format, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t mask, const char *format,
                                    const char *copy, ...); /* 0x43ce9e */

static const char module[] = "ota.tran"; /* ROM 0x78b678 */
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ota_service\\ota_transport.c"; /* ROM 0x6e9070 */

static const char fn_timeout[] = "_otaRxNextPacketTimeout"; /* ROM 0x779ea4 */
static const char reply_timeout[] = "OTA_ReplyTimeoutToAPP"; /* ROM 0x779ebc */
static const char reply_timeout_s[] = "[ota.tran]OTA_ReplyTimeoutToAPP"; /* ROM 0x762e10 */
static const char fn_rx[] = "OTA_ReceivePacket"; /* ROM 0x781750 */
static const char ignore[] = "error send ignore, packetNum = %d, syncID = %d"; /* ROM 0x736584 */
static const char ignore_s[] = "[ota.tran]error send ignore, packetNum = %d, syncID = %d"; /* ROM 0x717410 */
static const char cmd_crc[] = "cmd OTA_ReplyCrcErrorToAPP"; /* ROM 0x76f3c8 */
static const char cmd_crc_s[] = "[ota.tran]cmd OTA_ReplyCrcErrorToAPP"; /* ROM 0x74c0bc */
static const char malloc_failed[] = "Malloc failed!"; /* ROM 0x787c40 */
static const char malloc_failed_s[] = "[ota.tran]Malloc failed!"; /* ROM 0x76f3e4 */
static const char no_res[] = "OTA_ReplyNoResourcesToAPP"; /* ROM 0x76f400 */
static const char no_res_s[] = "[ota.tran]OTA_ReplyNoResourcesToAPP"; /* ROM 0x75756c */
static const char overflow[] =
    "Buffer overflow! _g_totalLenRx=%d, packetLen=%d, packetNum=%d, packetTotalNum=%d"; /* ROM 0x6e90c4 */
static const char overflow_s[] =
    "[ota.tran]Buffer overflow! _g_totalLenRx=%d, packetLen=%d, packetNum=%d, packetTotalNum=%d"; /* ROM 0x6e10f4 */
static const char free_buf[] = "free pDataBuf = 0x%x"; /* ROM 0x779eec */
static const char free_buf_s[] = "[ota.tran]free pDataBuf = 0x%x"; /* ROM 0x762e70 */
static const char rx_total[] = "rx totalLength = %d"; /* ROM 0x781764 */
static const char rx_total_s[] = "[ota.tran]rx totalLength = %d"; /* ROM 0x762e30 */
static const char rx_crc[] = "rx crc = 0x%x(0x%x)"; /* ROM 0x781778 */
static const char rx_crc_s[] = "[ota.tran]rx crc = 0x%x(0x%x)"; /* ROM 0x762e50 */
static const char reply_crc[] = "OTA_ReplyCrcErrorToAPP"; /* ROM 0x779ed4 */
static const char reply_crc_s[] = "[ota.tran]OTA_ReplyCrcErrorToAPP"; /* ROM 0x757590 */
static const char fn_tx[] = "OTA_SendPacket"; /* ROM 0x787c50 */
static const char not_auth[] = "------not auth------"; /* ROM 0x779f04 */
static const char not_auth_s[] = "[ota.tran]------not auth------"; /* ROM 0x762e90 */
static const char tx_error[] = "tx ret = %d error"; /* ROM 0x78178c */
static const char tx_error_s[] = "[ota.tran]tx ret = %d error"; /* ROM 0x76f41c */

/* TX header template (ROM 0x78de5c). */
static const uint8_t tx_header_template[OTA_FRAME_HEADER_LEN] = {
    OTA_FRAME_MAGIC, 0x02u, 0u, 0u, 0u, 0u, 0u, 0u,
};

#define TRAN_LOG(level, mask, function, line, format, simple, ...)              \
    do {                                                                        \
        if (audio_log_flags() & 2u)                                             \
            audio_log_extended((level), module, file, (function), (line),       \
                               (format), ##__VA_ARGS__);                        \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))               \
            (void)compress_log_output((mask), (simple), (simple),               \
                                      ##__VA_ARGS__);                           \
    } while (0)

void ota_rx_next_packet_timeout_48d87c(void);
uint32_t ota_transport_receive_48d8d8(const uint8_t *packet, uint16_t length);
uint32_t ota_transport_send_48de40(uint8_t notify, uint8_t type, uint8_t command,
                                   const uint8_t *payload, uint16_t length);
uint8_t *svc_android_notify_buffer_48e0a8(void);

static uint16_t get_u16(const uint8_t *p)
{
    return *(const uint16_t *)(const void *)p;
}

/* Remember the failing sync id so its remaining frames are ignored. */
static void rx_fail(const uint8_t *packet)
{
    g2_ota_rx_error_pending_20074ff5 = 1u;
    g2_ota_rx_error_sync_id_20074ff6 = packet[2];
    semantic_OtaNotifyStatus3(packet[6]);
}

/* 0xC0 / 0xC2: whole message in one frame, CRC over payload. */
static void rx_single_frame(const uint8_t *packet, uint32_t line)
{
    uint16_t crc_rx;
    uint16_t crc;

    g2_ota_rx_active_20074ff4 = 1u;
    g2_ota_rx_total_len_20074850 = (uint32_t)packet[3] - 2u;
    crc_rx = get_u16(packet + g2_ota_rx_total_len_20074850 + OTA_FRAME_HEADER_LEN);
    crc = audio_uart_hand_checksum_49acd4(packet + OTA_FRAME_HEADER_LEN,
                                          g2_ota_rx_total_len_20074850, NULL);
    if (crc == crc_rx) {
        if (((packet[7] >> 5) & 1u) == 0u && g2_ota_transport_callbacks_20003058.rx != NULL)
            g2_ota_transport_callbacks_20003058.rx(packet[6], packet + OTA_FRAME_HEADER_LEN,
                                                   (uint16_t)g2_ota_rx_total_len_20074850);
    } else {
        TRAN_LOG(4u, 0x10000000u, fn_rx, line, cmd_crc, cmd_crc_s);
        rx_fail(packet);
    }
}

/* 0x48d87c: _otaRxNextPacketTimeout (delayed event; no symbol row in the
 * inventory). */
void ota_rx_next_packet_timeout_48d87c(void)
{
    TRAN_LOG(4u, 0x10000000u, fn_timeout, 0x3cu, reply_timeout, reply_timeout_s);
    g2_ota_rx_total_len_20074850 = 0u;
    g2_ota_rx_error_pending_20074ff5 = 1u;
    semantic_OtaNotifyStatus4(OTA_CMD_DATA);
}

/* 0x48d8d8: OTA_ReceivePacket. */
uint32_t ota_transport_receive_48d8d8(const uint8_t *packet, uint16_t length)
{
    uint16_t crc_rx;
    uint16_t crc;

    if (packet[0] != OTA_FRAME_MAGIC)
        return 10u;
    if (packet[3] == 0u && length == OTA_FRAME_HEADER_LEN)
        return 0u;
    g2_ota_sync_id_20074ff7 = packet[2];
    if (g2_ota_rx_error_pending_20074ff5 != 0u && packet[5] >= 2u &&
        packet[2] == g2_ota_rx_error_sync_id_20074ff6) {
        TRAN_LOG(4u, 0x10800000u, fn_rx, 99u, ignore, ignore_s, packet[5], packet[2]);
        return 0u;
    }

    if (packet[6] == OTA_CMD_CONTROL) {
        rx_single_frame(packet, 0x75u);
        if (packet[6] == OTA_CMD_CONTROL && packet[OTA_FRAME_HEADER_LEN] == 2u) {
            /* Start of a multi-frame transfer: claim the static buffer. */
            g2_ota_rx_total_len_20074850 = 0u;
            g2_ota_rx_data_buf_20074854 = NULL;
            g2_ota_rx_error_pending_20074ff5 = 0u;
            g2_ota_rx_error_sync_id_20074ff6 = 0u;
            g2_ota_rx_data_buf_20074854 = g2_ota_rx_static_buf_2000304c;
            if (g2_ota_rx_data_buf_20074854 == NULL) {
                TRAN_LOG(1u, 0x04000000u, fn_rx, 0x87u, malloc_failed, malloc_failed_s);
                TRAN_LOG(1u, 0x04000000u, fn_rx, 0x88u, no_res, no_res_s);
                g2_ota_rx_error_pending_20074ff5 = 1u;
                g2_ota_rx_error_sync_id_20074ff6 = packet[2];
                semantic_OtaNotifyStatus5(packet[6]);
                return 4u;
            }
            audio_uart_buffer_zero(g2_ota_rx_data_buf_20074854, OTA_RX_BUFFER_LEN, 0u);
        }
    } else if (packet[6] == OTA_CMD_DATA) {
        (void)fw_event_loop_remove_delayed(ota_rx_next_packet_timeout_48d87c);
        g2_ota_rx_error_pending_20074ff5 = 0u;
        if (g2_ota_rx_data_buf_20074854 == NULL && packet[5] < packet[4])
            return 4u;
        if (g2_ota_rx_total_len_20074850 + packet[3] > OTA_RX_BUFFER_LEN) {
            TRAN_LOG(1u, 0x05000000u, fn_rx, 0xa2u, overflow, overflow_s,
                     g2_ota_rx_total_len_20074850, packet[3], packet[5], packet[4]);
            g2_ota_rx_total_len_20074850 = 0u;
            rx_fail(packet);
            return 4u;
        }
        (void)audio_queue_copy_bytes(g2_ota_rx_data_buf_20074854 + g2_ota_rx_total_len_20074850,
                                     packet + OTA_FRAME_HEADER_LEN, packet[3]);
        g2_ota_rx_total_len_20074850 += packet[3];
        if (packet[5] < packet[4]) {
            fw_event_loop_push_delayed(ota_rx_next_packet_timeout_48d87c, 0u,
                                       OTA_RX_FRAME_TIMEOUT_MS);
            return 0u;
        }
        g2_ota_rx_total_len_20074850 -= 2u;
        crc_rx = get_u16(g2_ota_rx_data_buf_20074854 + g2_ota_rx_total_len_20074850);
        crc = audio_uart_hand_checksum_49acd4(g2_ota_rx_data_buf_20074854,
                                              g2_ota_rx_total_len_20074850, NULL);
        if (crc != crc_rx) {
            TRAN_LOG(4u, 0x10400000u, fn_rx, 0xc1u, rx_total, rx_total_s,
                     g2_ota_rx_total_len_20074850);
            TRAN_LOG(4u, 0x10800000u, fn_rx, 0xc2u, rx_crc, rx_crc_s, crc_rx, crc);
            if (g2_ota_rx_data_buf_20074854 != g2_ota_rx_static_buf_2000304c)
                file_heap_free(g2_ota_rx_data_buf_20074854);
            TRAN_LOG(1u, 0x04000000u, fn_rx, 199u, reply_crc, reply_crc_s);
            g2_ota_rx_total_len_20074850 = 0u;
            rx_fail(packet);
            return 1u;
        }
        if (g2_ota_transport_callbacks_20003058.rx != NULL)
            g2_ota_transport_callbacks_20003058.rx(packet[6], g2_ota_rx_data_buf_20074854,
                                                   (uint16_t)g2_ota_rx_total_len_20074850);
        if (g2_ota_rx_data_buf_20074854 != g2_ota_rx_static_buf_2000304c) {
            TRAN_LOG(4u, 0x10400000u, fn_rx, 0xd0u, free_buf, free_buf_s,
                     g2_ota_rx_data_buf_20074854);
            file_heap_free(g2_ota_rx_data_buf_20074854);
        }
        g2_ota_rx_data_buf_20074854 = NULL;
        g2_ota_rx_total_len_20074850 = 0u;
    } else if (packet[6] == OTA_CMD_CONTROL2) {
        rx_single_frame(packet, 0xe3u);
    }
    return 0u;
}

/* 0x48de40: OTA_SendPacket. The authentication gate is compiled as a
 * constant-true test in stock (movs r0,#1 / cmp r0,#0). */
uint32_t ota_transport_send_48de40(uint8_t notify, uint8_t type, uint8_t command,
                                   const uint8_t *payload, uint16_t length)
{
    const bool authenticated = true;
    uint16_t chunk;
    uint16_t total;
    uint16_t offset;
    uint16_t n;
    uint16_t crc;
    uint8_t *data;
    uint8_t *frame;
    uint8_t header[OTA_FRAME_HEADER_LEN];
    uint8_t status;

    if (payload == NULL || length == 0u)
        return 11u;
    if (!authenticated) {
        TRAN_LOG(4u, 0x10000000u, fn_tx, 0xf5u, not_auth, not_auth_s);
        return 8u;
    }
    chunk = (uint16_t)(slave_cmd_pipe_get_0046f2c6() - 11u);
    data = g2_ota_tx_data_buf_20003050;
    if (data == NULL)
        return 4u;
    audio_uart_buffer_zero(data, OTA_RX_BUFFER_LEN, 0u);
    (void)audio_queue_copy_bytes(data, payload, length);
    frame = g2_ota_tx_frame_buf_20003054;
    if (frame == NULL)
        return 4u;
    audio_uart_buffer_zero(frame, OTA_TX_FRAME_LEN, 0u);
    crc = audio_uart_hand_checksum_49acd4(data, length, NULL);
    total = (uint16_t)((int32_t)((uint32_t)chunk + length + 1u) / (int32_t)chunk);

    for (uint32_t i = 0u; i < OTA_FRAME_HEADER_LEN; i++)
        header[i] = tx_header_template[i];
    header[1] = (uint8_t)((header[1] & 0x0fu) | (uint8_t)(type << 4));
    header[2] = g2_ota_sync_id_20074ff7;
    header[4] = (uint8_t)total;
    header[6] = command;
    header[7] = (uint8_t)((header[7] & 0xfeu) | (notify & 1u));

    for (uint8_t i = 1u; (uint16_t)i <= total; i++) {
        offset = (uint16_t)((int16_t)(i - 1) * (int16_t)chunk);
        n = (i == total) ? (uint16_t)(length - offset) : chunk;
        header[3] = (uint8_t)((i == total) ? n + 2u : n);
        header[5] = i;
        (void)audio_queue_copy_bytes(frame, header, OTA_FRAME_HEADER_LEN);
        (void)audio_queue_copy_bytes(frame + OTA_FRAME_HEADER_LEN, data + offset, n);
        if (i == total)
            (void)audio_queue_copy_bytes(frame + n + OTA_FRAME_HEADER_LEN, &crc, 2u);
        status = 0u;
        if (g2_ota_transport_callbacks_20003058.tx != NULL)
            status = g2_ota_transport_callbacks_20003058.tx(
                frame, (uint16_t)(header[3] + OTA_FRAME_HEADER_LEN));
        if (status != 0u) {
            TRAN_LOG(1u, 0x04400000u, fn_tx, 0x13fu, tx_error, tx_error_s, status);
            if (data != g2_ota_tx_data_buf_20003050)
                file_heap_free(data);
            if (frame != g2_ota_tx_frame_buf_20003054)
                file_heap_free(frame);
            return status;
        }
    }
    if (data != g2_ota_tx_data_buf_20003050)
        file_heap_free(data);
    if (frame != g2_ota_tx_frame_buf_20003054)
        file_heap_free(frame);
    return 0u;
}

/* 0x48e0a8: base of the shared 0x20354c78 buffer (also used by the EFS
 * service for Android notification messages). */
uint8_t *svc_android_notify_buffer_48e0a8(void)
{
    return g2_ota_shared_buffer_20354c78;
}
