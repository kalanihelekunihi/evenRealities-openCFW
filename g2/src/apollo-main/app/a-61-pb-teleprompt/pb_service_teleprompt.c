/* Teleprompt protobuf receive/transmit handlers, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\pb_service_teleprompt\pb_service_teleprompt.c
 * (path ROM 0x6d9634, module tag "pb.teleprompt" ROM 0x787f10).
 * Native 0x5885b4..0x588cf1 (APP_PbRxTelepromptFrameDataProcess ..
 * APP_PbTxEncodeScrollSync), literal pool 0x588cf4..0x588d73.
 *
 * All messages share one nanopb descriptor (ROM 0x77c304, 0xf58-byte
 * struct): [command_id u8][magic_random u8][oneof tag u16][payload]. The Rx
 * path decodes into the caller's message, hex-dumps up to 32 input bytes and
 * drops a frame whose magic repeats the previous one within 3 s. Tx encoders
 * build the shared message RAM 0x200f873c into the 256-byte packet RAM
 * 0x2037c9a0 and, on the master side only, send it on service 6: the common
 * response (0xa6 / tag 12) with Thread_MsgPbTxByBle, every other command with
 * Thread_MsgPbNotifyByBle and magic = last received magic + 1.
 * Return codes: 0 ok, 5 decode failure, 6 NULL input, 13 duplicate,
 * 0x2b encode failure. */
#include <stdint.h>
#include <stddef.h>

#define TP_SERVICE_ID      6u
#define TP_PACKET_SIZE     0x100u
#define TP_MSG_SIZE        0xf58u
#define TP_DUP_WINDOW_MS   3000u

enum {
    TP_CMD_STATUS_NOTIFY = 0xa1u,
    TP_CMD_FILE_LIST_REQUEST = 0xa2u,
    TP_CMD_FILE_SELECT = 0xa3u,
    TP_CMD_PAGE_DATA_REQUEST = 0xa4u,
    TP_CMD_SCROLL_SYNC = 0xa5u,
    TP_CMD_COMM_RESP = 0xa6u,
};

enum {
    TP_RX_OK = 0u,
    TP_RX_DECODE_FAILED = 5u,
    TP_RX_NULL = 6u,
    TP_RX_DUPLICATE = 0x0du,
    TP_TX_ENCODE_FAILED = 0x2bu,
};

typedef struct {
    uint8_t command_id;   /* +0x00 */
    uint8_t magic_random; /* +0x01 */
    uint16_t which;       /* +0x02 */
    union {
        uint8_t u8;       /* comm resp status, file list request */
        uint16_t u16;     /* status notify */
        uint32_t u32;     /* page data request */
        uint32_t scroll_sync[3];
        uint8_t file_select[0x42];
        uint8_t raw[TP_MSG_SIZE - 4u];
    } u;                  /* +0x04 */
} g2_teleprompt_pb_msg_t;
_Static_assert(sizeof(g2_teleprompt_pb_msg_t) == TP_MSG_SIZE, "stock memset size");

/* nanopb 0.4 streams */
typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *errmsg;
} g2_pb_istream_t;
typedef struct {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
} g2_pb_ostream_t;
_Static_assert(sizeof(g2_pb_istream_t) == 16u, "nanopb istream");
_Static_assert(sizeof(g2_pb_ostream_t) == 20u, "nanopb ostream");

extern g2_teleprompt_pb_msg_t g2_teleprompt_pb_tx_msg_200f873c;   /* RAM 0x200f873c */
extern uint8_t g2_teleprompt_pb_tx_packet_2037c9a0[TP_PACKET_SIZE]; /* RAM 0x2037c9a0 */
extern uint8_t g2_teleprompt_pb_last_magic_20074ffe;              /* RAM 0x20074ffe */
extern uint32_t g2_teleprompt_pb_last_tick_20074870;              /* RAM 0x20074870 */
extern const uint8_t g2_teleprompt_pb_msgdesc_77c304[];           /* ROM 0x77c304 pb_msgdesc_t */

extern uint32_t audio_log_flags(void);                                          /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                              /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void audio_dump_hex(const char *label, uint32_t width, const uint8_t *data,
                           uint32_t length);                                    /* 0x43dacc elog hexdump */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);      /* 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);  /* memcpy 0x439be4 */
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* 0x439c04 */
extern uint32_t osKernelGetTickCount(void);                                     /* 0x4490cc */
extern uint8_t audio_uart_device_role_get(void);                                /* 0x45a568, 1 = master */
extern void audio_uart_pb_stream_init(g2_pb_istream_t *out, const void *buf, uint32_t size); /* pb_istream_from_buffer 0x48f49c */
extern uint32_t audio_uart_pb_decode(void *stream, const void *fields, void *dst);           /* pb_decode 0x490120 */
extern void audio_pb_ostream_from_buffer(g2_pb_ostream_t *out, void *buf, uint32_t size);   /* 0x4905f4 */
extern uint32_t audio_pb_encode(void *stream, const void *fields, const void *src);         /* pb_encode 0x490c32 */
extern uint32_t Thread_MsgPbTxByBle(uint8_t type, uint8_t command, const void *payload,
                                    uint16_t length);                           /* 0x475b14 */
extern uint32_t Thread_MsgPbNotifyByBle(uint8_t type, uint8_t command, const void *payload,
                                        uint16_t length);                       /* 0x475c1a */

static const char module_tag[] = "pb.teleprompt"; /* ROM 0x787f10 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_teleprompt\\pb_service_teleprompt.c"; /* ROM 0x6d9634 */
static const char none_text[] = "(none)"; /* ROM 0x78df74 */

static const char fn_rx[] = "APP_PbRxTelepromptFrameDataProcess"; /* ROM 0x757e90 */
static const char fn_comm_resp[] = "APP_PbTelepromptTxEncodeCommResp"; /* ROM 0x757ed8 */
static const char fn_status_notify[] = "APP_PbTxEncodeStatusNotify"; /* ROM 0x76faac */
static const char fn_file_list_request[] = "APP_PbTxEncodeFileListRequest"; /* ROM 0x7637f0 */
static const char fn_file_select[] = "APP_PbTxEncodeFileSelect"; /* ROM 0x76fac8 */
static const char fn_page_data_request[] = "APP_PbTxEncodePageDataRequest"; /* ROM 0x763830 */
static const char fn_scroll_sync[] = "APP_PbTxEncodeScrollSync"; /* ROM 0x76fb00 */

static const char dump_rx[] = "Teleprompt_pb_rx"; /* ROM 0x7824ac */
static const char dump_resp[] = "Teleprompt_pb_resp"; /* ROM 0x7824e8 */
static const char dump_notify[] = "Teleprompt_pb_notify"; /* ROM 0x77a6cc */
static const char dump_file_list_request[] = "Teleprompt_pb_file_list_request"; /* ROM 0x763810 */
static const char dump_file_select[] = "Teleprompt_pb_file_select"; /* ROM 0x76fae4 */
static const char dump_page_data_request[] = "Teleprompt_pb_page_data_request"; /* ROM 0x763850 */
static const char dump_scroll_sync[] = "Teleprompt_pb_scroll_sync"; /* ROM 0x76fb1c */

static const char msg_null[] = "pData or message is NULL"; /* ROM 0x76fa90 */
static const char msg_null_s[] = "[pb.teleprompt]pData or message is NULL"; /* ROM 0x74c6d4 */
static const char msg_decode_failed[] = "Decoding failed: %s"; /* ROM 0x7824c0 */
static const char msg_decode_failed_s[] = "[pb.teleprompt]Decoding failed: %s"; /* ROM 0x757eb4 */
static const char msg_command[] = "command_id: %d, magic number = %d, last magic number = %d"; /* ROM 0x7178c0 */
static const char msg_command_s[] = "[pb.teleprompt]command_id: %d, magic number = %d, last magic number = %d"; /* ROM 0x6f514c */
static const char msg_duplicate[] = "Duplicate message detected: magic_random = %d, time_elapsed = %d ms, ignore"; /* ROM 0x6f5198 */
static const char msg_duplicate_s[] = "[pb.teleprompt]Duplicate message detected: magic_random = %d, time_elapsed = %d ms, ignore"; /* ROM 0x6e12c0 */
static const char msg_encode_failed[] = "Encoding failed: %s"; /* ROM 0x7824d4 */
static const char msg_encode_failed_s[] = "[pb.teleprompt]Encoding failed: %s"; /* ROM 0x757efc */

#define TP_LOG(level, fn, line, cflags, name, ...)                                                 \
    do {                                                                                          \
        if ((audio_log_flags() & 2u) != 0u)                                                       \
            audio_log_extended((level), module_tag, source_file, (fn), (line), name,              \
                               ##__VA_ARGS__);                                                    \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                     \
            (void)compress_log_output((cflags), name##_s, name##_s, ##__VA_ARGS__);              \
    } while (0)

uint32_t APP_PbRxTelepromptFrameDataProcess(const uint8_t *data, uint16_t len,
                                            g2_teleprompt_pb_msg_t *msg)
{
    g2_pb_istream_t tmp;
    g2_pb_istream_t stream;
    uint32_t now;
    uint32_t elapsed;

    if (data == NULL || msg == NULL) {
        TP_LOG(1u, fn_rx, 0x40u, 0x04000000u, msg_null);
        return TP_RX_NULL;
    }
    audio_dump_hex(dump_rx, 0x10u, data, (uint16_t)(len > 0x20u ? 0x20u : len));
    audio_uart_pb_stream_init(&tmp, data, len);
    (void)audio_uart_display_area_copy_439c04(&stream, &tmp, sizeof stream);
    if ((uint8_t)audio_uart_pb_decode(&stream, g2_teleprompt_pb_msgdesc_77c304, msg) == 0u) {
        TP_LOG(1u, fn_rx, 0x47u, 0x04400000u, msg_decode_failed,
               stream.errmsg != NULL ? stream.errmsg : none_text);
        return TP_RX_DECODE_FAILED;
    }
    TP_LOG(3u, fn_rx, 0x4au, 0x0cc00000u, msg_command, msg->command_id, msg->magic_random,
           g2_teleprompt_pb_last_magic_20074ffe);
    now = osKernelGetTickCount();
    elapsed = now - g2_teleprompt_pb_last_tick_20074870;
    if (msg->magic_random == g2_teleprompt_pb_last_magic_20074ffe && elapsed < TP_DUP_WINDOW_MS) {
        TP_LOG(2u, fn_rx, 0x51u, 0x08800000u, msg_duplicate, g2_teleprompt_pb_last_magic_20074ffe,
               elapsed);
        return TP_RX_DUPLICATE;
    }
    g2_teleprompt_pb_last_magic_20074ffe = msg->magic_random;
    g2_teleprompt_pb_last_tick_20074870 = now;
    return TP_RX_OK;
}

/* Clears the shared message and writes its header. */
static g2_teleprompt_pb_msg_t *tx_begin(uint8_t command, uint8_t magic, uint16_t which)
{
    g2_teleprompt_pb_msg_t *msg = &g2_teleprompt_pb_tx_msg_200f873c;

    (void)aeabi_memset_43c0e4(msg, TP_MSG_SIZE, 0);
    msg->command_id = command;
    msg->magic_random = magic;
    msg->which = which;
    return msg;
}

/* Encodes the shared message; on success dumps it and, on the master,
 * sends it (response through Tx, everything else through Notify). */
static uint32_t tx_finish(const char *fn, uint32_t line, const char *dump, uint8_t notify)
{
    g2_pb_ostream_t tmp;
    g2_pb_ostream_t stream;
    uint16_t written;

    audio_pb_ostream_from_buffer(&tmp, g2_teleprompt_pb_tx_packet_2037c9a0, TP_PACKET_SIZE);
    (void)audio_uart_display_area_copy_439c04(&stream, &tmp, sizeof stream);
    if ((uint8_t)audio_pb_encode(&stream, g2_teleprompt_pb_msgdesc_77c304,
                                 &g2_teleprompt_pb_tx_msg_200f873c) == 0u) {
        TP_LOG(1u, fn, line, 0x04400000u, msg_encode_failed,
               stream.errmsg != NULL ? stream.errmsg : none_text);
        return TP_TX_ENCODE_FAILED;
    }
    written = (uint16_t)stream.bytes_written;
    audio_dump_hex(dump, 0x10u, g2_teleprompt_pb_tx_packet_2037c9a0, written);
    if (audio_uart_device_role_get() == 1u) {
        if (notify != 0u)
            (void)Thread_MsgPbNotifyByBle(1u, TP_SERVICE_ID, g2_teleprompt_pb_tx_packet_2037c9a0, written);
        else
            (void)Thread_MsgPbTxByBle(1u, TP_SERVICE_ID, g2_teleprompt_pb_tx_packet_2037c9a0, written);
    }
    return 0u;
}

/* Common response to a received frame: echoes its magic, status 0 ok / 1 error. */
uint32_t APP_PbTelepromptTxEncodeCommResp(uint8_t magic, const uint8_t *status)
{
    g2_teleprompt_pb_msg_t *msg = tx_begin(TP_CMD_COMM_RESP, magic, 12u);
    msg->u.u8 = *status;
    return tx_finish(fn_comm_resp, 0x6au, dump_resp, 0u);
}

uint32_t APP_PbTxEncodeStatusNotify(const uint16_t *status)
{
    g2_teleprompt_pb_msg_t *msg =
        tx_begin(TP_CMD_STATUS_NOTIFY, (uint8_t)(g2_teleprompt_pb_last_magic_20074ffe + 1u), 7u);
    msg->u.u16 = *status;
    return tx_finish(fn_status_notify, 0x84u, dump_notify, 1u);
}

uint32_t APP_PbTxEncodeFileListRequest(const uint8_t *request)
{
    g2_teleprompt_pb_msg_t *msg =
        tx_begin(TP_CMD_FILE_LIST_REQUEST, (uint8_t)(g2_teleprompt_pb_last_magic_20074ffe + 1u), 8u);
    msg->u.u8 = *request;
    return tx_finish(fn_file_list_request, 0x9eu, dump_file_list_request, 1u);
}

/* request: {u16 name_len; char name[0x40]} (66 bytes). */
uint32_t APP_PbTxEncodeFileSelect(const void *request)
{
    g2_teleprompt_pb_msg_t *msg =
        tx_begin(TP_CMD_FILE_SELECT, (uint8_t)(g2_teleprompt_pb_last_magic_20074ffe + 1u), 9u);
    (void)audio_queue_copy_bytes(msg->u.file_select, request, sizeof msg->u.file_select);
    return tx_finish(fn_file_select, 0xb8u, dump_file_select, 1u);
}

uint32_t APP_PbTxEncodePageDataRequest(const uint32_t *page)
{
    g2_teleprompt_pb_msg_t *msg =
        tx_begin(TP_CMD_PAGE_DATA_REQUEST, (uint8_t)(g2_teleprompt_pb_last_magic_20074ffe + 1u), 10u);
    msg->u.u32 = *page;
    return tx_finish(fn_page_data_request, 0xd2u, dump_page_data_request, 1u);
}

/* sync: {page_id, line_id, mode}. */
uint32_t APP_PbTxEncodeScrollSync(const uint32_t *sync)
{
    g2_teleprompt_pb_msg_t *msg =
        tx_begin(TP_CMD_SCROLL_SYNC, (uint8_t)(g2_teleprompt_pb_last_magic_20074ffe + 1u), 11u);
    msg->u.scroll_sync[0] = sync[0];
    msg->u.scroll_sync[1] = sync[1];
    msg->u.scroll_sync[2] = sync[2];
    return tx_finish(fn_scroll_sync, 0xecu, dump_scroll_sync, 1u);
}
