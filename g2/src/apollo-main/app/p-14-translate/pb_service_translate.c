/* Translate protobuf service 0x05, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\pb_service_translate\pb_service_translate.c.
 * Native 0x59f53c..0x59fa68; literal pool 0x59fa68..0x59fae0.
 *
 * Envelope (TX object RAM 0x200f9ee4, 0x854 bytes): byte 0 = command id
 * (0xa1 notify, 0xa2 response, 0xa3 mode switch), byte 1 = magic, u16 at +2 =
 * payload tag (5 notify, 7 response, 6 mode switch), payload at +4. The encoded
 * frame goes into the 0x100-byte buffer at RAM 0x2037caa0 and is sent on route 1,
 * service 5, by the master only. Notify-type envelopes use last RX magic + 1
 * without storing it. RX rejects a repeated magic within 3000 ms (status 13). */
#include <stdint.h>
#include <stddef.h>

/* nanopb pb_istream_t (16 bytes). */
typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *errmsg; /* +0xc */
} g2_pb_istream_t;
_Static_assert(sizeof(g2_pb_istream_t) == 16u, "nanopb istream ABI");

/* nanopb pb_ostream_t (20 bytes). */
typedef struct {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written; /* +0xc */
    const char *errmsg;     /* +0x10 */
} g2_pb_ostream_t;
_Static_assert(sizeof(g2_pb_ostream_t) == 20u, "nanopb ostream ABI");

typedef struct {
    uint8_t command_id;     /* +0x000 */
    uint8_t magic_random;   /* +0x001 */
    uint16_t which_payload; /* +0x002 */
    uint8_t payload[0x850]; /* +0x004 */
} g2_translate_pb_msg_t;
_Static_assert(sizeof(g2_translate_pb_msg_t) == 0x854u, "stock memset length");

struct pb_msgdesc_candidate;
extern const struct pb_msgdesc_candidate g2_translate_pb_msgdesc; /* ROM 0x77ce5c */
extern g2_translate_pb_msg_t g2_translate_pb_tx_msg;               /* RAM 0x200f9ee4 */
extern uint8_t g2_translate_pb_tx_buffer[0x100];                   /* RAM 0x2037caa0 */
extern uint8_t g2_translate_pb_last_magic;                         /* RAM 0x20075000 */
extern uint32_t g2_translate_pb_last_rx_tick;                      /* RAM 0x20074878 */

extern uint32_t osKernelGetTickCount(void);
extern uint32_t audio_log_flags(void);                                       /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);                 /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void audio_dump_hex(const char *, uint32_t, const uint8_t *, uint32_t);  /* 0x43dacc */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);              /* memset(p, n, c) 0x43c0e4 */
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t); /* aligned memcpy */
extern void audio_uart_pb_stream_init(g2_pb_istream_t *, const void *, uint32_t);  /* 0x48f49c */
extern uint32_t audio_uart_pb_decode(void *, const void *, void *);          /* 0x490120 */
extern void audio_pb_ostream_from_buffer(g2_pb_ostream_t *, void *, uint32_t); /* 0x4905f4 */
extern uint32_t audio_pb_encode(void *, const void *, const void *);         /* 0x490c32 */
extern uint8_t audio_uart_device_role_get(void);                             /* 0x45a568, 1 = master */
extern uint32_t audio_ring_pb_tx_ble_475b14(uint32_t, uint32_t, const void *, uint32_t); /* Thread_MsgPbTxByBle */
extern uint32_t audio_ring_pb_tx_ble_475c1a(uint32_t, uint32_t, const void *, uint32_t); /* Thread_MsgPbNotifyByBle */

#define TRANSLATE_PB_SERVICE 5u
#define TRANSLATE_PB_DUPLICATE_WINDOW_MS 3000u

static const char module[] = "pb.translate"; /* ROM 0x787f20 */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_translate\\pb_service_translate.c"; /* ROM 0x6db4e8 */
static const char none[] = "(none)"; /* ROM 0x78df84 */

static const char fn_rx[] = "APP_PbTranslateRxFrameDataProcess"; /* ROM 0x757ff8 */
static const char msg_rx_null[] = "pData or message is NULL"; /* ROM 0x76fba8 */
static const char short_rx_null[] = "[pb.translate]pData or message is NULL"; /* ROM 0x74c83c */
static const char hex_rx[] = "Translate_pb_rx"; /* ROM 0x787f30 */
static const char msg_decode[] = "Decoding failed: %s"; /* ROM 0x7824fc */
static const char short_decode[] = "[pb.translate]Decoding failed: %s"; /* ROM 0x75801c */
static const char msg_command[] =
    "command_id: %d, magic number = %d, last magic number = %d"; /* ROM 0x717974 */
static const char short_command[] =
    "[pb.translate]command_id: %d, magic number = %d, last magic number = %d"; /* ROM 0x6fbec4 */
static const char msg_duplicate[] =
    "Duplicate message detected: magic_random = %d, time_elapsed = %d ms, ignore"; /* ROM 0x6f52c8 */
static const char short_duplicate[] =
    "[pb.translate]Duplicate message detected: magic_random = %d, time_elapsed = %d ms, ignore"; /* ROM 0x6e131c */

static const char msg_encode[] = "Encoding failed: %s"; /* ROM 0x782510 */
static const char short_encode[] = "[pb.translate]Encoding failed: %s"; /* ROM 0x758040 */

static const char fn_notify[] = "APP_PbTranslateTxEncodeNotify"; /* ROM 0x763950 */
static const char msg_notify_null[] = "pNotify is NULL"; /* ROM 0x787f40 */
static const char short_notify_null[] = "[pb.translate]pNotify is NULL"; /* ROM 0x763970 */

static const char fn_resp[] = "APP_PbTranslateTxEncodeCommResp"; /* ROM 0x763990 */
static const char msg_resp_null[] = "pResp is NULL"; /* ROM 0x787f50 */
static const char short_resp_null[] = "[pb.translate]pResp is NULL"; /* ROM 0x76fbc4 */
static const char hex_resp[] = "Translate_pb_resp"; /* ROM 0x782524 */

static const char fn_mode[] = "APP_PbTranslateTxEncodeModeSwitch"; /* ROM 0x758064 */
static const char msg_mode_null[] = "pModeSwitch is NULL"; /* ROM 0x782538 */
static const char short_mode_null[] = "[pb.translate]pModeSwitch is NULL"; /* ROM 0x758088 */

static inline void log_null(const char *fn, uint32_t line, const char *msg, const char *short_msg)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(1u, module, path, fn, line, msg);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x4000000u, short_msg, short_msg);
}

static inline void log_encode_failed(const char *fn, uint32_t line, const g2_pb_ostream_t *stream)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(1u, module, path, fn, line, msg_encode,
                           stream->errmsg != NULL ? stream->errmsg : none);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x4400000u, short_encode, short_encode,
                                  stream->errmsg != NULL ? stream->errmsg : none);
}

/* Encodes g2_translate_pb_tx_msg into the TX buffer; returns 1 on success. */
static inline uint32_t encode_tx(g2_pb_ostream_t *stream)
{
    g2_pb_ostream_t initial;
    audio_pb_ostream_from_buffer(&initial, g2_translate_pb_tx_buffer, sizeof g2_translate_pb_tx_buffer);
    (void)audio_uart_display_area_copy_439c04(stream, &initial, sizeof *stream);
    return (uint8_t)audio_pb_encode(stream, &g2_translate_pb_msgdesc, &g2_translate_pb_tx_msg);
}

/* Returns 0 accepted, 5 decode failure, 6 null input, 13 duplicate magic. */
uint32_t APP_PbTranslateRxFrameDataProcess(const uint8_t *data, uint16_t length,
                                           g2_translate_pb_msg_t *msg)
{
    if (data == NULL || msg == NULL) {
        log_null(fn_rx, 0x3fu, msg_rx_null, short_rx_null);
        return 6u;
    }
    audio_dump_hex(hex_rx, 16u, data, length > 0x20u ? 0x20u : length);

    g2_pb_istream_t initial, stream;
    audio_uart_pb_stream_init(&initial, data, length);
    (void)audio_uart_display_area_copy_439c04(&stream, &initial, sizeof stream);
    if ((uint8_t)audio_uart_pb_decode(&stream, &g2_translate_pb_msgdesc, msg) == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, fn_rx, 0x46u, msg_decode,
                               stream.errmsg != NULL ? stream.errmsg : none);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compress_log_output(0x4400000u, short_decode, short_decode,
                                      stream.errmsg != NULL ? stream.errmsg : none);
        return 5u;
    }

    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, fn_rx, 0x49u, msg_command, msg->command_id,
                           msg->magic_random, g2_translate_pb_last_magic);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0xcc00000u, short_command, short_command, msg->command_id,
                                  msg->magic_random, g2_translate_pb_last_magic);

    uint32_t now = osKernelGetTickCount();
    uint32_t elapsed = now - g2_translate_pb_last_rx_tick;
    if (msg->magic_random == g2_translate_pb_last_magic &&
        elapsed < TRANSLATE_PB_DUPLICATE_WINDOW_MS) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_rx, 0x50u, msg_duplicate,
                               g2_translate_pb_last_magic, elapsed);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compress_log_output(0x8800000u, short_duplicate, short_duplicate,
                                      g2_translate_pb_last_magic, elapsed);
        return 13u;
    }
    g2_translate_pb_last_magic = msg->magic_random;
    g2_translate_pb_last_rx_tick = now;
    return 0u;
}

/* Subtype 5 notify (u16 value), sent as a BLE notification. */
uint32_t APP_PbTranslateTxEncodeNotify(const uint16_t *notify)
{
    if (notify == NULL) {
        log_null(fn_notify, 0x62u, msg_notify_null, short_notify_null);
        return 6u;
    }
    g2_translate_pb_msg_t *tx = &g2_translate_pb_tx_msg;
    audio_uart_buffer_zero(tx, sizeof *tx, 0u);
    tx->command_id = 0xa1u;
    tx->magic_random = (uint8_t)(g2_translate_pb_last_magic + 1u);
    tx->which_payload = 5u;
    *(uint16_t *)(void *)tx->payload = *notify;

    g2_pb_ostream_t stream;
    if (encode_tx(&stream) == 0u) {
        log_encode_failed(fn_notify, 0x6fu, &stream);
        return 5u;
    }
    if (audio_uart_device_role_get() == 1u)
        (void)audio_ring_pb_tx_ble_475c1a(1u, TRANSLATE_PB_SERVICE, g2_translate_pb_tx_buffer,
                                          (uint16_t)stream.bytes_written);
    return 0u;
}

/* Subtype 7 command response (u8 status) echoing the request magic. */
uint32_t APP_PbTranslateTxEncodeCommResp(const uint8_t *resp, uint8_t magic)
{
    if (resp == NULL) {
        log_null(fn_resp, 0x80u, msg_resp_null, short_resp_null);
        return 6u;
    }
    g2_translate_pb_msg_t *tx = &g2_translate_pb_tx_msg;
    audio_uart_buffer_zero(tx, sizeof *tx, 0u);
    tx->command_id = 0xa2u;
    tx->magic_random = magic;
    tx->which_payload = 7u;
    tx->payload[0] = *resp;

    g2_pb_ostream_t stream;
    if (encode_tx(&stream) == 0u) {
        log_encode_failed(fn_resp, 0x8du, &stream);
        return 5u;
    }
    audio_dump_hex(hex_resp, 16u, g2_translate_pb_tx_buffer, (uint16_t)stream.bytes_written);
    if (audio_uart_device_role_get() == 1u)
        (void)audio_ring_pb_tx_ble_475b14(1u, TRANSLATE_PB_SERVICE, g2_translate_pb_tx_buffer,
                                          (uint16_t)stream.bytes_written);
    return 0u;
}

/* Subtype 6 mode switch (u32 value), sent as a BLE notification. */
uint32_t APP_PbTranslateTxEncodeModeSwitch(const uint32_t *mode_switch)
{
    if (mode_switch == NULL) {
        log_null(fn_mode, 0xbfu, msg_mode_null, short_mode_null);
        return 6u;
    }
    g2_translate_pb_msg_t *tx = &g2_translate_pb_tx_msg;
    audio_uart_buffer_zero(tx, sizeof *tx, 0u);
    tx->command_id = 0xa3u;
    tx->magic_random = (uint8_t)(g2_translate_pb_last_magic + 1u);
    tx->which_payload = 6u;
    *(uint32_t *)(void *)tx->payload = *mode_switch;

    g2_pb_ostream_t stream;
    if (encode_tx(&stream) == 0u) {
        log_encode_failed(fn_mode, 0xccu, &stream);
        return 5u;
    }
    if (audio_uart_device_role_get() == 1u)
        (void)audio_ring_pb_tx_ble_475c1a(1u, TRANSLATE_PB_SERVICE, g2_translate_pb_tx_buffer,
                                          (uint16_t)stream.bytes_written);
    return 0u;
}
