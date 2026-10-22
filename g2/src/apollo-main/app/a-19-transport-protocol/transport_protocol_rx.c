/* Transport protocol (TPL) receive path, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\transport_protocol\transport_protocol.c.
 * Native _getOrCreateContext 0x4b8a12, packet bitmap helpers 0x4b8bdc/0x4b8c14,
 * _rxSyncEventCallback 0x4b8f7c and TPL_ReceivePacket 0x4b910c..0x4b9605;
 * literal pools 0x4b90ec..0x4b910b, 0x4b960c..0x4b961b, 0x4b99d8..0x4b99eb and
 * 0x4b9a04..0x4b9a47.
 *
 * Other functions of this source live in app/tpl-* (TPL_Init 0x4b892c,
 * tpl_context_free 0x4b8ba2, tpl_schedule_rx_timeout 0x4b8c44,
 * _rxNextPacketTimeout 0x4b8c6c, TPL_RxPacketTimeoutHandler 0x4b8da2,
 * _tplReponse 0x4b9012, receive-context reset 0x4b9984).
 *
 * Packet header (8 bytes, payload follows at +8):
 *   [0] 0xAA magic   [1] source id (low nibble) / destination id (high nibble)
 *   [2] syncID       [3] payload length       [4] packetTotalNum
 *   [5] packetNum (1-based)                    [6] serviceID
 *   [7] bit 5: sender wants a sync result, bits 1..4: tplRet
 * The last (or only) packet ends with a CRC-16 over the whole message. */
#include <stdint.h>

#define TPL_MAGIC        0xAAu
#define TPL_HEADER_LEN   8u
#define TPL_MAX_CONTEXTS 4u
#define TPL_ATT_OVERHEAD 11u /* ATT MTU minus per-packet overhead gives the data size */

enum {
    TPL_OK = 0u,
    TPL_ERR_CRC = 1u,
    TPL_ERR_NULL = 6u,
    TPL_ERR_MAGIC = 10u,
    TPL_ERR_SHORT = 11u,
    TPL_ERR_DUPLICATE = 13u,
};

/* Reassembly context, 56-byte rows at RAM 0x20070dc8 (audio_tpl_contexts). */
typedef struct {
    uint8_t service_id;    /* +0x00 header[6] */
    uint8_t sync_id;       /* +0x01 header[2] */
    uint16_t received;     /* +0x02 bytes stored so far */
    uint8_t source_id;     /* +0x04 header[1] & 0xf */
    uint8_t destination;   /* +0x05 header[1] >> 4 */
    uint8_t pad06[2];
    uint8_t *buffer;       /* +0x08 file-heap buffer */
    uint8_t pad0c[4];
    uint8_t seen[32];      /* +0x10 received-packet bitmap */
    uint8_t used;          /* +0x30 */
    uint8_t seen_count;    /* +0x31 */
    uint8_t expected;      /* +0x32 header[4] */
    uint8_t pipe;          /* +0x33 */
    uint8_t pad34[4];
} tpl_rx_context_t;
_Static_assert(sizeof(tpl_rx_context_t) == 56, "TPL context row");

/* Service row 0 at RAM 0x20071414 (20 bytes, written by TPL_Init). */
typedef int32_t (*tpl_sync_cb_t)(int32_t status);
typedef void (*tpl_rx_sync_cb_t)(uint16_t service, const uint8_t *data, uint16_t len, tpl_sync_cb_t done);
typedef void (*tpl_rx_cb_t)(uint8_t service, const uint8_t *data, uint16_t len);
typedef struct {
    uint8_t service;            /* +0x00 */
    uint8_t pad01[3];
    tpl_rx_sync_cb_t rx_sync;   /* +0x04 data needing a sync result (header[7] bit 5) */
    tpl_rx_cb_t rx;             /* +0x08 plain data */
    void *tx;                   /* +0x0c */
    void *response;             /* +0x10 */
} tpl_service_row_t;
_Static_assert(sizeof(tpl_service_row_t) == 20, "TPL service row");

extern uint8_t audio_tpl_contexts[TPL_MAX_CONTEXTS * 56u]; /* RAM 0x20070dc8 */
extern uint8_t audio_tpl_service_table[];                   /* RAM 0x20071414 */

/* Single-packet message length, RAM 0x20074b08 (only this file uses it). */
uint32_t g2_tpl_rx_total_length __attribute__((section(".g2_ram_20074b08"), used));

extern uint16_t slave_cmd_pipe_get_0046f2c6(void);                          /* negotiated ATT MTU */
extern void *file_heap_allocate(uint32_t size);                             /* 0x474cd2 */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern uint16_t audio_uart_hand_checksum_49acd4(const void *bytes, uint32_t length,
                                                const uint16_t *seed); /* CRC-16 0x49acd4 */
extern uint32_t audio_event_loop_remove_delayed(void (*callback)(void));   /* 0x476ace */
extern void audio_tpl_rx_next_packet_timeout(const uint8_t *ids);           /* _rxNextPacketTimeout 0x4b8c6c */
extern void tpl_context_free_004b8ba2(uint8_t *context);
extern void tpl_schedule_rx_timeout_004b8c44(uint8_t pipe, uint8_t service, uint8_t sync);
extern void audio_tpl_response(uint8_t pipe, uint8_t sync, uint8_t service, uint8_t code); /* _tplReponse 0x4b9012 */
extern void tpl_reset_receive_contexts_004b9984(void);

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char s_module[] = "prot.tran"; /* ROM 0x78c7ac */
static const char s_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\transport_protocol\\transport_protocol.c"; /* ROM 0x6dec74 */
static const char s_get_ctx[] = "_getOrCreateContext"; /* ROM 0x78461c */
static const char s_malloc[] = "Malloc failed! expectedPackets = %d maxDataPerPkt = %d Size needed:%d"; /* ROM 0x6fe78c */
static const char s_malloc_short[] =
    "[prot.tran]Malloc failed! expectedPackets = %d maxDataPerPkt = %d Size needed:%d"; /* ROM 0x6ea6c0 */
static const char s_sync_cb[] = "_rxSyncEventCallback"; /* ROM 0x77d0cc */
static const char s_sync_status[] = "SyncStatus = %d"; /* ROM 0x789cb0 */
static const char s_sync_status_short[] = "[prot.tran]SyncStatus = %d"; /* ROM 0x773d64 */
static const char s_sync_error[] =
    "!!!!!!!!!!!!!!!Dual-Glasses Communication ERROR = %d!!!!!!!!!!!!!!!"; /* ROM 0x70786c */
static const char s_sync_error_short[] =
    "[prot.tran]!!!!!!!!!!!!!!!Dual-Glasses Communication ERROR = %d!!!!!!!!!!!!!!!"; /* ROM 0x6f08a8 */
static const char s_receive[] = "TPL_ReceivePacket"; /* ROM via 0x4b9a08 */
static const char s_tpl_ret[] = "pHeader->b.tplRet = %d"; /* ROM 0x77d0e4 */
static const char s_tpl_ret_short[] = "[prot.tran]pHeader->b.tplRet = %d"; /* ROM 0x75c0f0 */
static const char s_total[] = "rx totalLength = %d"; /* ROM 0x784658 */
static const char s_total_short[] = "[prot.tran]rx totalLength = %d"; /* ROM 0x767230 */
static const char s_crc[] = "rx crc = 0x%x(0x%x)"; /* ROM 0x78466c */
static const char s_crc_short[] = "[prot.tran]rx crc = 0x%x(0x%x)"; /* ROM 0x767250 */
static const char s_pipe[] = "rx pipe error pipeID = %d error"; /* ROM 0x767270 */
static const char s_pipe_short[] = "[prot.tran]rx pipe error pipeID = %d error"; /* ROM 0x745c1c */
static const char s_mismatch[] = "packetTotalNum mismatch! header=%u, expected=%u, packetNum=%u"; /* ROM 0x710b24 */
static const char s_mismatch_short[] =
    "[prot.tran]packetTotalNum mismatch! header=%u, expected=%u, packetNum=%u"; /* ROM 0x6f6fe0 */

/* Stock log macro: extended record when flag bit 1 is set, compressed record
 * when flag bit 0 or bit 2 is set. */
#define TPL_LOG(level, func, line, cflags, msg, short_msg, ...)                              \
    do {                                                                                     \
        if ((audio_log_flags() & 2u) != 0u)                                                  \
            audio_log_extended((level), s_module, s_path, (func), (line), (msg), __VA_ARGS__); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                \
            (void)compress_log_output((cflags), (short_msg), (short_msg), __VA_ARGS__);      \
    } while (0)

static tpl_rx_context_t *tpl_context_row(uint32_t index)
{
    return (tpl_rx_context_t *)(void *)(audio_tpl_contexts + index * sizeof(tpl_rx_context_t));
}

static const tpl_service_row_t *tpl_service_row0(void)
{
    return (const tpl_service_row_t *)(const void *)audio_tpl_service_table;
}

/* Finds the context of this (service, sync, source, destination, pipe) message;
 * a first packet (packetNum 1) allocates a free row and a buffer sized for
 * packetTotalNum packets of (MTU - 11) bytes. */
tpl_rx_context_t *_getOrCreateContext(const uint8_t *header, uint8_t pipe)
{
    tpl_rx_context_t *ctx = 0;
    uint16_t per_packet = (uint16_t)(slave_cmd_pipe_get_0046f2c6() - TPL_ATT_OVERHEAD);

    for (uint32_t i = 0u; i < TPL_MAX_CONTEXTS; i++) {
        tpl_rx_context_t *row = tpl_context_row(i);
        if (row->used != 0u && row->service_id == header[6] && row->sync_id == header[2] &&
            row->source_id == (header[1] & 0x0fu) && row->destination == (uint8_t)(header[1] >> 4) &&
            row->pipe == pipe) {
            ctx = row;
            break;
        }
    }
    if (ctx != 0 || header[5] != 1u)
        return ctx;

    for (uint32_t i = 0u; i < TPL_MAX_CONTEXTS; i++) {
        tpl_rx_context_t *row = tpl_context_row(i);
        if (row->used != 0u)
            continue;
        audio_uart_buffer_zero(row, 0x32u, 0u);
        row->used = 1u;
        row->service_id = header[6];
        row->sync_id = header[2];
        row->source_id = header[1] & 0x0fu;
        row->destination = (uint8_t)(header[1] >> 4);
        row->expected = header[4];
        row->pipe = pipe;
        row->received = 0u;
        row->buffer = file_heap_allocate((uint32_t)row->expected * per_packet);
        if (row->buffer != 0)
            return row;
        TPL_LOG(1u, s_get_ctx, 0xbau, 0x04c00000u, s_malloc, s_malloc_short,
                row->expected, per_packet, (uint32_t)row->expected * per_packet);
        row->used = 0u;
        return 0;
    }
    return 0;
}

void tpl_context_mark_packet_004b8bdc(tpl_rx_context_t *ctx, uint8_t index)
{
    ctx->seen[index >> 3] |= (uint8_t)(1u << (index % 8u));
    ctx->seen_count++;
}

uint8_t tpl_context_packet_seen_004b8c14(const tpl_rx_context_t *ctx, uint8_t index)
{
    return (ctx->seen[index >> 3] & (1u << (index % 8u))) != 0u ? 1u : 0u;
}

/* Completion handed to the service's rx_sync callback; non-zero means the
 * peer glasses did not accept the message. */
int32_t _rxSyncEventCallback(int32_t status)
{
    TPL_LOG(4u, s_sync_cb, 0x13cu, 0x10400000u, s_sync_status, s_sync_status_short, status);
    if (status != 0)
        TPL_LOG(1u, s_sync_cb, 0x13eu, 0x04400000u, s_sync_error, s_sync_error_short, status);
    return status;
}

static uint16_t tpl_read_le16(const uint8_t *p)
{
    return (uint16_t)(p[0] | ((uint16_t)p[1] << 8));
}

/* Hands a complete, CRC-checked message to service row 0 (pipe 0 only). */
static void tpl_deliver(uint8_t pipe, const uint8_t *header, const uint8_t *data, uint16_t len,
                        uint32_t line)
{
    const tpl_service_row_t *svc = tpl_service_row0();

    if (pipe != 0u) {
        TPL_LOG(1u, s_receive, line, 0x04400000u, s_pipe, s_pipe_short, pipe);
        return;
    }
    if (((header[7] >> 5) & 1u) != 0u && svc->rx_sync != 0)
        svc->rx_sync(header[6], data, len, _rxSyncEventCallback);
    else if (((header[7] >> 5) & 1u) == 0u && svc->rx != 0)
        svc->rx(header[6], data, len);
}

uint32_t TPL_ReceivePacket(uint8_t pipe, const uint8_t *packet, uint16_t length)
{
    if (packet == 0) {
        tpl_reset_receive_contexts_004b9984();
        return TPL_ERR_NULL;
    }
    if (length < TPL_HEADER_LEN) {
        tpl_reset_receive_contexts_004b9984();
        return TPL_ERR_SHORT;
    }
    if (packet[0] != TPL_MAGIC) {
        tpl_reset_receive_contexts_004b9984();
        return TPL_ERR_MAGIC;
    }

    /* Header-only packet: a result code from the peer. */
    if (packet[3] == 0u && length == TPL_HEADER_LEN) {
        TPL_LOG(3u, s_receive, 400u, 0x0c400000u, s_tpl_ret, s_tpl_ret_short,
                (uint8_t)((packet[7] >> 1) & 0x0fu));
        tpl_reset_receive_contexts_004b9984();
        return TPL_OK;
    }

    (void)audio_event_loop_remove_delayed((void (*)(void))audio_tpl_rx_next_packet_timeout);

    if (packet[4] == 1u) {
        g2_tpl_rx_total_length = (uint32_t)packet[3] - 2u;
        uint16_t rx_crc = tpl_read_le16(packet + TPL_HEADER_LEN + g2_tpl_rx_total_length);
        uint16_t crc = audio_uart_hand_checksum_49acd4(packet + TPL_HEADER_LEN, g2_tpl_rx_total_length, 0);
        TPL_LOG(4u, s_receive, 0x1a7u, 0x10400000u, s_total, s_total_short, g2_tpl_rx_total_length);
        TPL_LOG(4u, s_receive, 0x1a8u, 0x10800000u, s_crc, s_crc_short, rx_crc, crc);
        if (crc == rx_crc)
            tpl_deliver(pipe, packet, packet + TPL_HEADER_LEN, (uint16_t)g2_tpl_rx_total_length, 0x1b5u);
        else
            audio_tpl_response(pipe, packet[2], packet[6], 1u);
        return TPL_OK;
    }

    tpl_rx_context_t *ctx = _getOrCreateContext(packet, pipe);
    if (ctx == 0) {
        if (packet[5] < packet[4]) {
            tpl_schedule_rx_timeout_004b8c44(pipe, packet[6], packet[2]);
            return TPL_OK;
        }
        audio_tpl_response(pipe, packet[2], packet[6], 1u);
        return TPL_ERR_CRC;
    }
    if (packet[4] != ctx->expected) {
        TPL_LOG(1u, s_receive, 0x1cbu, 0x04c00000u, s_mismatch, s_mismatch_short,
                packet[4], ctx->expected, packet[5]);
        tpl_context_free_004b8ba2((uint8_t *)ctx);
        audio_tpl_response(pipe, packet[2], packet[6], 1u);
        return TPL_ERR_CRC;
    }
    if (tpl_context_packet_seen_004b8c14(ctx, (uint8_t)(packet[5] - 1u)) != 0u) {
        if (packet[5] < packet[4])
            tpl_schedule_rx_timeout_004b8c44(pipe, packet[6], packet[2]);
        else
            tpl_context_free_004b8ba2((uint8_t *)ctx);
        return TPL_ERR_DUPLICATE;
    }

    (void)audio_queue_copy_bytes(ctx->buffer + ctx->received, packet + TPL_HEADER_LEN, packet[3]);
    tpl_context_mark_packet_004b8bdc(ctx, (uint8_t)(packet[5] - 1u));
    ctx->received = (uint16_t)(ctx->received + packet[3]);
    if (packet[5] < packet[4]) {
        tpl_schedule_rx_timeout_004b8c44(pipe, packet[6], packet[2]);
        return TPL_OK;
    }

    ctx->received = (uint16_t)(ctx->received - 2u);
    uint16_t rx_crc = tpl_read_le16(ctx->buffer + ctx->received);
    uint16_t crc = audio_uart_hand_checksum_49acd4(ctx->buffer, ctx->received, 0);
    TPL_LOG(4u, s_receive, 0x1eeu, 0x10400000u, s_total, s_total_short, ctx->received);
    TPL_LOG(4u, s_receive, 0x1efu, 0x10800000u, s_crc, s_crc_short, rx_crc, crc);
    (void)audio_event_loop_remove_delayed((void (*)(void))audio_tpl_rx_next_packet_timeout);
    if (crc == rx_crc) {
        tpl_deliver(pipe, packet, ctx->buffer, ctx->received, 0x1ffu);
        tpl_context_free_004b8ba2((uint8_t *)ctx);
        return TPL_OK;
    }
    tpl_context_free_004b8ba2((uint8_t *)ctx);
    audio_tpl_response(pipe, packet[2], packet[6], 1u);
    return TPL_ERR_CRC;
}
