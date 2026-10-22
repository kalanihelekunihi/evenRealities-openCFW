/* EFS service BLE transport framing, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\efs_service\efs_transport.c
 * (log tag "efs.tran"). Native 0x4d0d24..0x4d1546, literal pool
 * 0x4d1548..0x4d15e7. Sibling of ota_transport.c (same frame layout).
 *
 * Frame (8-byte header, payload, CRC on the final frame):
 *   +0 0xAA magic        +1 low nibble 2, high nibble = type
 *   +2 sync id (TX: low byte of osKernelGetTickCount)
 *   +3 payload length (final frame: +2 for the CRC)
 *   +4 total frames      +5 frame number (1-based)
 *   +6 command           +7 bit0 notify flag, bit5 "no callback" on 0xC4/0xC6
 *   +8 payload ...       final frame: payload, then CRC16 (seed 0, LE)
 * RX commands: 0xC4 single-frame control (payload byte 0 == 1 opens a
 * reassembly into the 0x1020-byte static buffer), 0xC5 multi-frame data with
 * a 1500 ms inter-frame timeout, 0xC6 single-frame control. TX splits the
 * payload into (ATT MTU - 11)-byte frames.
 * Return codes: 0 ok, 1 CRC error, 4 no resource, 8 not authenticated,
 * 10 bad magic, 11 bad argument, else the transport TX error. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#include "g2_efs_service.h"

#define EFS_FRAME_MAGIC 0xaau
#define EFS_FRAME_HEADER_LEN 8u
#define EFS_RX_BUFFER_LEN 0x1020u
#define EFS_TX_FRAME_LEN 0xf7u
#define EFS_RX_FRAME_TIMEOUT_MS 1500u

/* Transport callbacks (RAM 0x2000096c) installed by the EFS service. */
typedef struct {
    void (*rx)(uint8_t command, const uint8_t *data, uint16_t length);  /* +0 */
    uint8_t (*tx)(const uint8_t *frame, uint16_t length);               /* +4 */
} g2_efs_transport_cb_t;
_Static_assert(sizeof(g2_efs_transport_cb_t) == 8u, "EFS transport callbacks");

extern g2_efs_transport_cb_t g2_efs_transport_callbacks_2000096c; /* RAM 0x2000096c */
extern uint8_t *g2_efs_rx_static_buf_20000960;  /* RAM 0x20000960, 0x1020-byte RX buffer */
extern uint8_t *g2_efs_tx_data_buf_20000964;    /* RAM 0x20000964, 0x1020-byte TX copy */
extern uint8_t *g2_efs_tx_frame_buf_20000968;   /* RAM 0x20000968, 0xf7-byte TX frame */
extern uint32_t g2_efs_rx_total_len_20074564;   /* RAM 0x20074564, _g_totalLenRx */
extern uint8_t *g2_efs_rx_data_buf_20074568;    /* RAM 0x20074568, pDataBuf */
extern uint8_t g2_efs_rx_active_20074fbd;       /* RAM 0x20074fbd */
extern uint8_t g2_efs_rx_error_pending_20074fbe; /* RAM 0x20074fbe */
extern uint8_t g2_efs_rx_error_sync_id_20074fbf; /* RAM 0x20074fbf */

extern uint16_t audio_uart_hand_checksum_49acd4(const void *data, uint32_t length,
                                                const uint16_t *seed); /* CRC16 */
extern uint16_t slave_cmd_pipe_get_0046f2c6(void); /* negotiated ATT MTU */
extern uint32_t osKernelGetTickCount(void);         /* 0x4490cc */
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

static const char module[] = "efs.tran"; /* ROM 0x78a964 */
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\efs_service\\efs_transport.c"; /* ROM 0x6e78d0 */

static const char fn_timeout[] = "_efsRxNextPacketTimeout"; /* ROM 0x777054 */
static const char reply_timeout[] = "EFS_ReplyTimeoutToAPP"; /* ROM 0x77706c */
static const char reply_timeout_s[] = "[efs.tran]EFS_ReplyTimeoutToAPP"; /* ROM 0x75fcb0 */
static const char fn_rx[] = "EFS_ReceivePacket"; /* ROM 0x77f284 */
static const char ignore[] = "error send ignore, packetNum = %d, syncID = %d"; /* ROM 0x733dc4 */
static const char ignore_s[] = "[efs.tran]error send ignore, packetNum = %d, syncID = %d"; /* ROM 0x714b0c */
static const char cmd_crc[] = "cmd EFS_ReplyCrcErrorToAPP"; /* ROM 0x76b5a8 */
static const char cmd_crc_s[] = "[efs.tran]cmd EFS_ReplyCrcErrorToAPP"; /* ROM 0x749d94 */
static const char malloc_failed[] = "Malloc failed!"; /* ROM 0x785d90 */
static const char malloc_failed_s[] = "[efs.tran]Malloc failed!"; /* ROM 0x76b5c4 */
static const char no_res[] = "EFS_ReplyNoResourcesToAPP"; /* ROM 0x76b5e0 */
static const char no_res_s[] = "[efs.tran]EFS_ReplyNoResourcesToAPP"; /* ROM 0x754260 */
static const char overflow[] =
    "Buffer overflow! _g_totalLenRx=%d, packetLen=%d, packetNum=%d, packetTotalNum=%d"; /* ROM 0x6e7924 */
static const char overflow_s[] =
    "[efs.tran]Buffer overflow! _g_totalLenRx=%d, packetLen=%d, packetNum=%d, packetTotalNum=%d"; /* ROM 0x6e0124 */
static const char free_buf[] = "free pDataBuf = 0x%x"; /* ROM 0x77709c */
static const char free_buf_s[] = "[efs.tran]free pDataBuf = 0x%x"; /* ROM 0x75fd10 */
static const char rx_total[] = "rx totalLength = %d"; /* ROM 0x77f298 */
static const char rx_total_s[] = "[efs.tran]rx totalLength = %d"; /* ROM 0x75fcd0 */
static const char rx_crc[] = "rx crc = 0x%x(0x%x)"; /* ROM 0x77f2ac */
static const char rx_crc_s[] = "[efs.tran]rx crc = 0x%x(0x%x)"; /* ROM 0x75fcf0 */
static const char reply_crc[] = "EFS_ReplyCrcErrorToAPP"; /* ROM 0x777084 */
static const char reply_crc_s[] = "[efs.tran]EFS_ReplyCrcErrorToAPP"; /* ROM 0x754284 */
static const char fn_tx[] = "EFS_SendPacket"; /* ROM 0x785da0 */
static const char not_auth[] = "------not auth------"; /* ROM 0x7770b4 */
static const char not_auth_s[] = "[efs.tran]------not auth------"; /* ROM 0x75fd30 */
static const char tx_error[] = "tx ret = %d error"; /* ROM 0x77f2c0 */
static const char tx_error_s[] = "[efs.tran]tx ret = %d error"; /* ROM 0x76b5fc */

/* TX header template (ROM 0x78d4b4). */
static const uint8_t tx_header_template[EFS_FRAME_HEADER_LEN] = {
    EFS_FRAME_MAGIC, 0x02u, 0u, 0u, 0u, 0u, 0u, 0u,
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

void efs_rx_next_packet_timeout_4d0d24(void);
uint32_t efs_transport_receive_4d0d80(const uint8_t *packet, uint16_t length);
uint32_t efs_transport_send_4d12de(uint8_t notify, uint8_t type, uint8_t command,
                                   const uint8_t *payload, uint16_t length);

static uint16_t get_u16(const uint8_t *p)
{
    return *(const uint16_t *)(const void *)p;
}

/* Remember the failing sync id so its remaining frames are ignored, and
 * answer {1,2} (CRC error / no buffer) to the phone. */
static void rx_fail(const uint8_t *packet)
{
    g2_efs_rx_error_pending_20074fbe = 1u;
    g2_efs_rx_error_sync_id_20074fbf = packet[2];
    semantic_EfsNotifyStatus2(packet[6]);
}

/* 0xC4 / 0xC6: whole message in one frame, CRC over payload. The CRC-error
 * log is level 1 (mask 0x04000000) for 0xC4 and level 4 (0x10000000) for
 * 0xC6. */
static void rx_single_frame(const uint8_t *packet, uint8_t level, uint32_t mask,
                            uint32_t line)
{
    uint16_t crc_rx;
    uint16_t crc;

    g2_efs_rx_active_20074fbd = 1u;
    g2_efs_rx_total_len_20074564 = (uint32_t)packet[3] - 2u;
    crc_rx = get_u16(packet + g2_efs_rx_total_len_20074564 + EFS_FRAME_HEADER_LEN);
    crc = audio_uart_hand_checksum_49acd4(packet + EFS_FRAME_HEADER_LEN,
                                          g2_efs_rx_total_len_20074564, NULL);
    if (crc == crc_rx) {
        if (((packet[7] >> 5) & 1u) == 0u && g2_efs_transport_callbacks_2000096c.rx != NULL)
            g2_efs_transport_callbacks_2000096c.rx(packet[6], packet + EFS_FRAME_HEADER_LEN,
                                                   (uint16_t)g2_efs_rx_total_len_20074564);
    } else {
        TRAN_LOG(level, mask, fn_rx, line, cmd_crc, cmd_crc_s);
        rx_fail(packet);
    }
}

/* 0x4d0d24: _efsRxNextPacketTimeout (delayed event; no symbol row in the
 * inventory). Replies {1,4} on 0xC5. */
void efs_rx_next_packet_timeout_4d0d24(void)
{
    TRAN_LOG(4u, 0x10000000u, fn_timeout, 0x3au, reply_timeout, reply_timeout_s);
    g2_efs_rx_total_len_20074564 = 0u;
    g2_efs_rx_error_pending_20074fbe = 1u;
    semantic_EfsNotifyStatus4(G2_EFS_CMD_IMPORT_DATA);
}

/* 0x4d0d80: EFS_ReceivePacket. Unlike OTA_ReceivePacket it does not record
 * the RX sync id. */
uint32_t efs_transport_receive_4d0d80(const uint8_t *packet, uint16_t length)
{
    uint16_t crc_rx;
    uint16_t crc;

    if (packet[0] != EFS_FRAME_MAGIC)
        return 10u;
    if (packet[3] == 0u && length == EFS_FRAME_HEADER_LEN)
        return 0u;
    if (g2_efs_rx_error_pending_20074fbe != 0u && packet[5] >= 2u &&
        packet[2] == g2_efs_rx_error_sync_id_20074fbf) {
        TRAN_LOG(4u, 0x10800000u, fn_rx, 0x61u, ignore, ignore_s, packet[5], packet[2]);
        return 0u;
    }

    if (packet[6] == G2_EFS_CMD_IMPORT_CONTROL) {
        rx_single_frame(packet, 1u, 0x04000000u, 0x73u);
        if (packet[6] == G2_EFS_CMD_IMPORT_CONTROL && packet[EFS_FRAME_HEADER_LEN] == 1u) {
            /* Data-begin subcommand: claim the static reassembly buffer. */
            g2_efs_rx_total_len_20074564 = 0u;
            g2_efs_rx_data_buf_20074568 = NULL;
            g2_efs_rx_error_pending_20074fbe = 0u;
            g2_efs_rx_error_sync_id_20074fbf = 0u;
            g2_efs_rx_data_buf_20074568 = g2_efs_rx_static_buf_20000960;
            if (g2_efs_rx_data_buf_20074568 == NULL) {
                TRAN_LOG(1u, 0x04000000u, fn_rx, 0x85u, malloc_failed, malloc_failed_s);
                TRAN_LOG(1u, 0x04000000u, fn_rx, 0x86u, no_res, no_res_s);
                g2_efs_rx_error_pending_20074fbe = 1u;
                g2_efs_rx_error_sync_id_20074fbf = packet[2];
                semantic_EfsNotifyStatus5(packet[6]);
                return 4u;
            }
            audio_uart_buffer_zero(g2_efs_rx_data_buf_20074568, EFS_RX_BUFFER_LEN, 0u);
        }
    } else if (packet[6] == G2_EFS_CMD_IMPORT_DATA) {
        (void)fw_event_loop_remove_delayed(efs_rx_next_packet_timeout_4d0d24);
        g2_efs_rx_error_pending_20074fbe = 0u;
        if (g2_efs_rx_data_buf_20074568 == NULL && packet[5] < packet[4])
            return 4u;
        if (g2_efs_rx_total_len_20074564 + packet[3] > EFS_RX_BUFFER_LEN) {
            TRAN_LOG(1u, 0x05000000u, fn_rx, 0xa0u, overflow, overflow_s,
                     g2_efs_rx_total_len_20074564, packet[3], packet[5], packet[4]);
            g2_efs_rx_total_len_20074564 = 0u;
            rx_fail(packet);
            return 4u;
        }
        (void)audio_queue_copy_bytes(g2_efs_rx_data_buf_20074568 + g2_efs_rx_total_len_20074564,
                                     packet + EFS_FRAME_HEADER_LEN, packet[3]);
        g2_efs_rx_total_len_20074564 += packet[3];
        if (packet[5] < packet[4]) {
            fw_event_loop_push_delayed(efs_rx_next_packet_timeout_4d0d24, 0u,
                                       EFS_RX_FRAME_TIMEOUT_MS);
            return 0u;
        }
        g2_efs_rx_total_len_20074564 -= 2u;
        crc_rx = get_u16(g2_efs_rx_data_buf_20074568 + g2_efs_rx_total_len_20074564);
        crc = audio_uart_hand_checksum_49acd4(g2_efs_rx_data_buf_20074568,
                                              g2_efs_rx_total_len_20074564, NULL);
        if (crc != crc_rx) {
            TRAN_LOG(4u, 0x10400000u, fn_rx, 0xbfu, rx_total, rx_total_s,
                     g2_efs_rx_total_len_20074564);
            TRAN_LOG(4u, 0x10800000u, fn_rx, 0xc0u, rx_crc, rx_crc_s, crc_rx, crc);
            if (g2_efs_rx_data_buf_20074568 != g2_efs_rx_static_buf_20000960)
                file_heap_free(g2_efs_rx_data_buf_20074568);
            TRAN_LOG(1u, 0x04000000u, fn_rx, 0xc5u, reply_crc, reply_crc_s);
            g2_efs_rx_total_len_20074564 = 0u;
            rx_fail(packet);
            return 1u;
        }
        if (g2_efs_transport_callbacks_2000096c.rx != NULL)
            g2_efs_transport_callbacks_2000096c.rx(packet[6], g2_efs_rx_data_buf_20074568,
                                                   (uint16_t)g2_efs_rx_total_len_20074564);
        if (g2_efs_rx_data_buf_20074568 != g2_efs_rx_static_buf_20000960) {
            TRAN_LOG(4u, 0x10400000u, fn_rx, 0xceu, free_buf, free_buf_s,
                     g2_efs_rx_data_buf_20074568);
            file_heap_free(g2_efs_rx_data_buf_20074568);
        }
        g2_efs_rx_data_buf_20074568 = NULL;
        g2_efs_rx_total_len_20074564 = 0u;
    } else if (packet[6] == G2_EFS_CMD_EXPORT_CONTROL) {
        rx_single_frame(packet, 4u, 0x10000000u, 0xe1u);
    }
    return 0u;
}

/* 0x4d12de: EFS_SendPacket. The authentication gate is compiled as a
 * constant-true test in stock (movs r0,#1 / cmp r0,#0). The stock return
 * type is a uint8_t status (zero-extended). */
uint32_t efs_transport_send_4d12de(uint8_t notify, uint8_t type, uint8_t command,
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
    uint8_t header[EFS_FRAME_HEADER_LEN];
    uint8_t status;

    if (payload == NULL || length == 0u)
        return 11u;
    if (!authenticated) {
        TRAN_LOG(4u, 0x10000000u, fn_tx, 0xf3u, not_auth, not_auth_s);
        return 8u;
    }
    chunk = (uint16_t)(slave_cmd_pipe_get_0046f2c6() - 11u);
    data = g2_efs_tx_data_buf_20000964;
    if (data == NULL)
        return 4u;
    audio_uart_buffer_zero(data, EFS_RX_BUFFER_LEN, 0u);
    (void)audio_queue_copy_bytes(data, payload, length);
    frame = g2_efs_tx_frame_buf_20000968;
    if (frame == NULL)
        return 4u;
    audio_uart_buffer_zero(frame, EFS_TX_FRAME_LEN, 0u);
    crc = audio_uart_hand_checksum_49acd4(data, length, NULL);
    total = (uint16_t)((int32_t)((uint32_t)chunk + length + 1u) / (int32_t)chunk);

    for (uint32_t i = 0u; i < EFS_FRAME_HEADER_LEN; i++)
        header[i] = tx_header_template[i];
    header[1] = (uint8_t)((header[1] & 0x0fu) | (uint8_t)(type << 4));
    header[2] = (uint8_t)osKernelGetTickCount();
    header[4] = (uint8_t)total;
    header[6] = command;
    header[7] = (uint8_t)((header[7] & 0xfeu) | (notify & 1u));

    for (uint8_t i = 1u; (uint16_t)i <= total; i++) {
        offset = (uint16_t)((int16_t)(i - 1) * (int16_t)chunk);
        n = (i == total) ? (uint16_t)(length - offset) : chunk;
        header[3] = (uint8_t)((i == total) ? n + 2u : n);
        header[5] = i;
        (void)audio_queue_copy_bytes(frame, header, EFS_FRAME_HEADER_LEN);
        (void)audio_queue_copy_bytes(frame + EFS_FRAME_HEADER_LEN, data + offset, n);
        if (i == total)
            (void)audio_queue_copy_bytes(frame + n + EFS_FRAME_HEADER_LEN, &crc, 2u);
        status = 0u;
        if (g2_efs_transport_callbacks_2000096c.tx != NULL)
            status = g2_efs_transport_callbacks_2000096c.tx(
                frame, (uint16_t)(header[3] + EFS_FRAME_HEADER_LEN));
        if (status != 0u) {
            TRAN_LOG(1u, 0x04400000u, fn_tx, 0x13eu, tx_error, tx_error_s, status);
            if (data != g2_efs_tx_data_buf_20000964)
                file_heap_free(data);
            if (frame != g2_efs_tx_frame_buf_20000968)
                file_heap_free(frame);
            return status;
        }
    }
    if (data != g2_efs_tx_data_buf_20000964)
        file_heap_free(data);
    if (frame != g2_efs_tx_frame_buf_20000968)
        file_heap_free(frame);
    return 0u;
}
