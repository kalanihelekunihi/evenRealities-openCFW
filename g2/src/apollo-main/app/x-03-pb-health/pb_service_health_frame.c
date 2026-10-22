/* Health protobuf frame entry, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\pb_service_health\pb_service_health.c
 * (path ROM 0x6de134, module tag "pb.health" ROM 0x78b720).
 * Native 0x55a350..0x55a557 (APP_PbRxHealthFrameDataProcess); literal pool
 * 0x55ab94..0x55abc7 and 0x55ad54 shared with app/a-55-pb-health, which holds
 * the PB_Rx* / APP_PbTxEncode* handlers it dispatches to.
 *
 * Decodes the frame into the 0x31c-byte receive message (RAM 0x200f5aa8) with
 * the health message descriptor and dispatches on command_id: 1 single data,
 * 2 mult data, 3 single highlight, 4 mult highlight. The PB_Rx* handler stores
 * the payload (+4) and, when it returns 0, the matching APP_PbTxEncode* echoes
 * it back with the request's magic (+1); its status is returned. Other
 * results: 2 NULL data, 0x2b decode failure, 1 unknown command or Rx failure.
 * Called from the health storage page (ui/a-39-health-page). */
#include <stdint.h>
#include <stddef.h>

#include "g2_health_data_manager.h"

#define HEALTH_MSG_SIZE 0x31cu

#define HEALTH_CMD_SINGLE_DATA      1u
#define HEALTH_CMD_MULT_DATA        2u
#define HEALTH_CMD_SINGLE_HIGHLIGHT 3u
#define HEALTH_CMD_MULT_HIGHLIGHT   4u

/* nanopb 0.4 pb_istream_t. */
typedef struct {
    void *callback;      /* +0x00 */
    void *state;         /* +0x04 */
    uint32_t bytes_left; /* +0x08 */
    const char *errmsg;  /* +0x0c */
} g2_pb_istream_t;
_Static_assert(sizeof(g2_pb_istream_t) == 16u, "nanopb istream");

/* Decoded health request: command_id +0, magic_random +1, oneof body +4. */
typedef union {
    struct {
        uint8_t command_id; /* +0x0 */
        uint8_t magic;      /* +0x1 */
        uint8_t pad[2];
        union {
            g2_health_pb_data_t single;
            g2_health_pb_mult_data_t mult;
            g2_health_pb_highlight_t single_highlight;
            g2_health_pb_mult_highlight_t mult_highlight;
        } body;             /* +0x4 */
    } f;
    uint8_t raw[HEALTH_MSG_SIZE];
} g2_health_pb_rx_msg_t;
_Static_assert(offsetof(g2_health_pb_rx_msg_t, f.body) == 4u, "rx body offset");
_Static_assert(sizeof(g2_health_pb_rx_msg_t) == HEALTH_MSG_SIZE, "rx message size");

extern g2_health_pb_rx_msg_t g2_health_pb_rx_msg_200f5aa8; /* RAM 0x200f5aa8 */
extern const uint8_t g2_health_pb_descriptor[];            /* ROM 0x777a14 pb_msgdesc_t */

extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);    /* 0x43c0e4 */
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len); /* 0x439c04 */
extern void audio_uart_pb_stream_init(g2_pb_istream_t *out, const void *buf,
                                      uint32_t size);                       /* pb_istream_from_buffer 0x48f49c */
extern uint32_t audio_uart_pb_decode(void *stream, const void *fields, void *dst); /* pb_decode 0x490120 */
extern uint32_t audio_log_flags(void);                                          /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                              /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

extern uint32_t PB_RxHealthSingleData(uint8_t magic, const g2_health_pb_data_t *data);
extern uint32_t APP_PbTxEncodeHealthSingleData(uint8_t magic, const g2_health_pb_data_t *data);
extern uint32_t PB_RxHealthMultData(uint8_t magic, const g2_health_pb_mult_data_t *data);
extern uint32_t APP_PbTxEncodeHealthMultData(uint8_t magic, const g2_health_pb_mult_data_t *data);
extern uint32_t PB_RxHealthSingleHighlight(uint8_t magic, const g2_health_pb_highlight_t *highlight);
extern uint32_t APP_PbTxEncodeHealthSingleHighlight(uint8_t magic,
                                                    const g2_health_pb_highlight_t *highlight);
extern uint32_t PB_RxHealthMultHighlight(uint8_t magic,
                                         const g2_health_pb_mult_highlight_t *highlights);
extern uint32_t APP_PbTxEncodeHealthMultHighlight(uint8_t magic,
                                                  const g2_health_pb_mult_highlight_t *highlights);

uint32_t APP_PbRxHealthFrameDataProcess_55a350(const uint8_t *data, uint16_t len);

static const char module_tag[] = "pb.health"; /* ROM 0x78b720 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_health\\pb_service_health.c"; /* ROM 0x6de134 */
static const char fn_frame[] = "APP_PbRxHealthFrameDataProcess";              /* ROM 0x763450 */
static const char len_text[] = "len=%d";                                      /* ROM 0x78decc */
static const char len_short[] = "[pb.health]len=%d";                          /* ROM 0x781e44 */
static const char null_text[] = "pData is NULL";                              /* ROM 0x787dd0 */
static const char null_short[] = "[pb.health]pData is NULL";                  /* ROM 0x76f6bc */
static const char decode_fail[] = "Decoding failed: %s";                      /* ROM 0x781e58 */
static const char decode_fail_short[] = "[pb.health]Decoding failed: %s";     /* ROM 0x763470 */
static const char none_text[] = "(none)";                                     /* ROM 0x78ded4 */
static const char cmd_text[] = "health command_id: %d";                       /* ROM 0x77a30c */
static const char cmd_short[] = "[pb.health]health command_id: %d";           /* ROM 0x757a10 */

#define LOG_E(level, line, ...)                                                                  \
    do {                                                                                         \
        if ((audio_log_flags() & 2u) != 0u)                                                      \
            audio_log_extended((level), module_tag, source_file, fn_frame, (line), __VA_ARGS__); \
    } while (0)
#define LOG_C(code, text, ...)                                                \
    do {                                                                      \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u) \
            (void)compress_log_output((code), (text), (text), ##__VA_ARGS__); \
    } while (0)

uint32_t APP_PbRxHealthFrameDataProcess_55a350(const uint8_t *data, uint16_t len)
{
    g2_health_pb_rx_msg_t *const msg = &g2_health_pb_rx_msg_200f5aa8;
    g2_pb_istream_t initial, stream;
    uint8_t magic;

    LOG_E(4u, 47u, len_text, (uint32_t)len);
    LOG_C(0x10400000u, len_short, (uint32_t)len);
    if (data == NULL) {
        LOG_E(1u, 49u, null_text);
        LOG_C(0x04000000u, null_short);
        return 2u;
    }

    (void)aeabi_memset_43c0e4(msg, HEALTH_MSG_SIZE, 0);
    audio_uart_pb_stream_init(&initial, data, len);
    (void)aeabi_memcpy4_439c04(&stream, &initial, sizeof stream);
    if ((uint8_t)audio_uart_pb_decode(&stream, g2_health_pb_descriptor, msg) == 0u) {
        LOG_E(1u, 59u, decode_fail, stream.errmsg != NULL ? stream.errmsg : none_text);
        LOG_C(0x04400000u, decode_fail_short, stream.errmsg != NULL ? stream.errmsg : none_text);
        return 0x2bu;
    }

    LOG_E(4u, 63u, cmd_text, (uint32_t)msg->f.command_id);
    LOG_C(0x10400000u, cmd_short, (uint32_t)msg->f.command_id);
    magic = msg->f.magic;
    switch (msg->f.command_id) {
    case HEALTH_CMD_SINGLE_DATA:
        if (PB_RxHealthSingleData(magic, &msg->f.body.single) != 0u)
            break;
        return APP_PbTxEncodeHealthSingleData(msg->f.magic, &msg->f.body.single);
    case HEALTH_CMD_MULT_DATA:
        if (PB_RxHealthMultData(magic, &msg->f.body.mult) != 0u)
            break;
        return APP_PbTxEncodeHealthMultData(msg->f.magic, &msg->f.body.mult);
    case HEALTH_CMD_SINGLE_HIGHLIGHT:
        if (PB_RxHealthSingleHighlight(magic, &msg->f.body.single_highlight) != 0u)
            break;
        return APP_PbTxEncodeHealthSingleHighlight(msg->f.magic, &msg->f.body.single_highlight);
    case HEALTH_CMD_MULT_HIGHLIGHT:
        if (PB_RxHealthMultHighlight(magic, &msg->f.body.mult_highlight) != 0u)
            break;
        return APP_PbTxEncodeHealthMultHighlight(msg->f.magic, &msg->f.body.mult_highlight);
    default:
        break;
    }
    return 1u;
}
