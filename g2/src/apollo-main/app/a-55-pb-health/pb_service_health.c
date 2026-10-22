/* Health protobuf receive/transmit handlers, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\pb_service_health\pb_service_health.c
 * (path ROM 0x6de134, module tag "pb.health" ROM 0x78b720).
 * Native 0x55a558..0x55b209 (PB_RxHealthSingleData .. APP_PbTxEncodeHealthMultHighlight),
 * literal pools 0x55ab94..0x55abdf, 0x55ad54..0x55ad77, 0x55af00..0x55af13,
 * 0x55b058..0x55b06b, 0x55b20c..0x55b2a3; NULL fault templates ROM 0x781e80..0x781f1f.
 *
 * APP_PbRxHealthFrameDataProcess (0x55a350, same file, not in this unit)
 * decodes a frame and hands the payload to the PB_Rx* handler, which stores it
 * through the health data manager (ui/a-55-health-data-manager). The Tx
 * encoders build command_id / oneof tag 1/3 single data, 2/4 mult data,
 * 3/5 single highlight and 4/6 mult highlight into the shared 0x31c-byte
 * message and 256-byte packet, then send on service 0x0e. Only the type
 * (and per-highlight +0x104 byte) of mult data / highlights is copied.
 *
 * The single-data info log promotes floats with vcvt.f64.f32: build with
 * profile g2-apollo-main-20. */
#include <stdint.h>
#include <stddef.h>

#include "g2_health_data_manager.h"

/* nanopb 0.4 pb_ostream_t. */
typedef struct {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
} g2_pb_ostream_t;
_Static_assert(sizeof(g2_pb_ostream_t) == 20u, "nanopb ostream");

/* APP_errorFaultHandler record; the ROM templates carry code 0, the caller sets 1. */
typedef struct {
    uint32_t type;        /* +0x00 */
    uint16_t code;        /* +0x04 */
    uint16_t reserved;
    const char *path;     /* +0x08 */
    const char *function; /* +0x0c */
    uint32_t line;        /* +0x10 */
} g2_fault_record_t;
_Static_assert(sizeof(g2_fault_record_t) == 20u, "fault record");

#define HEALTH_SERVICE_ID   0x0eu
#define HEALTH_PACKET_SIZE  0x100u
#define HEALTH_MSG_SIZE     0x31cu

/* Tx message offsets (command header +0, submessage at +4). */
#define HEALTH_MSG_CMD        0x000u
#define HEALTH_MSG_MAGIC      0x001u
#define HEALTH_MSG_TAG        0x002u
#define HEALTH_MSG_BODY       0x004u

extern uint8_t g2_health_pb_tx_packet[HEALTH_PACKET_SIZE]; /* RAM 0x2037c6a0 */
extern uint8_t g2_health_pb_tx_msg[HEALTH_MSG_SIZE];       /* RAM 0x200f5dc4 */
extern const uint8_t g2_health_pb_descriptor[];            /* ROM 0x777a14 pb_msgdesc_t */

extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);   /* 0x439c04 */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);      /* 0x43c0e4 */
extern void audio_pb_ostream_from_buffer(g2_pb_ostream_t *out, void *buf, uint32_t size); /* 0x4905f4 */
extern uint32_t audio_pb_encode(void *stream, const void *fields, const void *src);       /* pb_encode 0x490c32 */
extern uint32_t Thread_MsgPbTxByBle(uint8_t type, uint8_t command, const void *payload,
                                    uint16_t length);                           /* 0x475b14 */
extern void APP_errorFaultHandler(const g2_fault_record_t *record);             /* 0x509b48 */
extern uint32_t audio_log_flags(void);                                          /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                              /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "pb.health"; /* ROM 0x78b720 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_health\\pb_service_health.c"; /* ROM 0x6de134 */
static const char fn_rx_single[] = "PB_RxHealthSingleData";                    /* ROM 0x77a324 */
static const char fn_tx_single[] = "APP_PbTxEncodeHealthSingleData";           /* ROM 0x763490 */
static const char fn_rx_mult[] = "PB_RxHealthMultData";                        /* ROM 0x781e6c */
static const char fn_tx_mult[] = "APP_PbTxEncodeHealthMultData";               /* ROM 0x7634d0 */
static const char fn_rx_single_hl[] = "PB_RxHealthSingleHighlight";            /* ROM 0x76f6d8 */
static const char fn_tx_single_hl[] = "APP_PbTxEncodeHealthSingleHighlight";   /* ROM 0x757a34 */
static const char fn_rx_mult_hl[] = "PB_RxHealthMultHighlight";                /* ROM 0x76f6f4 */
static const char fn_tx_mult_hl[] = "APP_PbTxEncodeHealthMultHighlight";       /* ROM 0x757a7c */

static const char null_text[] = "POINTER NULL";               /* ROM 0x787de0 */
static const char null_short[] = "[pb.health]POINTER NULL";   /* ROM 0x77a33c */
static const char tx_len_text[] = "txLen = %d";               /* ROM 0x78b72c */
static const char tx_len_short[] = "[pb.health]txLen = %d";   /* ROM 0x77a354 */
static const char encode_fail[] = "Encoding failed: %s\n";    /* ROM 0x77a36c */
static const char encode_fail_short[] = "[pb.health]Encoding failed: %s\n"; /* ROM 0x7634b0 */
static const char none_text[] = "(none)";                     /* ROM 0x78ded4 */

static const char single_info[] = "pSingleData:data_type = %d, goal = %d, value = %f, avg_value = %f, duration = %d, trend = %d"; /* ROM 0x6de194 */
static const char single_info_s[] = "[pb.health]pSingleData:data_type = %d, goal = %d, value = %f, avg_value = %f, duration = %d, trend = %d"; /* ROM 0x6d9564 */
static const char single_fail[] = "Failed to save single health data, error=%d";             /* ROM 0x741368 */
static const char single_fail_s[] = "[pb.health]Failed to save single health data, error=%d"; /* ROM 0x7212e8 */
static const char single_ok[] = "Health single data saved successfully: type=%d";            /* ROM 0x736734 */
static const char single_ok_s[] = "[pb.health]Health single data saved successfully: type=%d"; /* ROM 0x717578 */
static const char mult_info[] = "pMultData:data_type = %d, data_set_count = %d";             /* ROM 0x736764 */
static const char mult_info_s[] = "[pb.health]pMultData:data_type = %d, data_set_count = %d"; /* ROM 0x7175b4 */
static const char mult_fail[] = "Failed to save mult health data, error=%d";                 /* ROM 0x741394 */
static const char mult_fail_s[] = "[pb.health]Failed to save mult health data, error=%d";    /* ROM 0x721320 */
static const char mult_ok[] = "Health mult data saved successfully: type=%d, count=%d";      /* ROM 0x721358 */
static const char mult_ok_s[] = "[pb.health]Health mult data saved successfully: type=%d, count=%d"; /* ROM 0x7046c0 */
static const char shl_info[] = "pSingleHighlight:data_type = %d, text_size = %d";            /* ROM 0x736794 */
static const char shl_info_s[] = "[pb.health]pSingleHighlight:data_type = %d, text_size = %d"; /* ROM 0x7175f0 */
static const char shl_fail[] = "Failed to save single health highlight, error=%d";           /* ROM 0x72bb54 */
static const char shl_fail_s[] = "[pb.health]Failed to save single health highlight, error=%d"; /* ROM 0x71762c */
static const char shl_ok[] = "Health single highlight saved successfully: type=%d";          /* ROM 0x72bb88 */
static const char shl_ok_s[] = "[pb.health]Health single highlight saved successfully: type=%d"; /* ROM 0x70d924 */
static const char mhl_info[] = "pMultHighlight:Highlight_count = %d";                        /* ROM 0x757a58 */
static const char mhl_info_s[] = "[pb.health]pMultHighlight:Highlight_count = %d";           /* ROM 0x7367c4 */
static const char mhl_fail[] = "Failed to save mult health highlight, error=%d";             /* ROM 0x7367f4 */
static const char mhl_fail_s[] = "[pb.health]Failed to save mult health highlight, error=%d"; /* ROM 0x717668 */
static const char mhl_ok[] = "Health mult highlight saved successfully: count=%d";           /* ROM 0x72bbbc */
static const char mhl_ok_s[] = "[pb.health]Health mult highlight saved successfully: count=%d"; /* ROM 0x70d964 */

static const g2_fault_record_t fault_rx_single = {0u, 0u, 0u, source_file, fn_rx_single, 0x6du};       /* ROM 0x781e80 */
static const g2_fault_record_t fault_tx_single = {0u, 0u, 0u, source_file, fn_tx_single, 0x84u};       /* ROM 0x781e94 */
static const g2_fault_record_t fault_rx_mult = {0u, 0u, 0u, source_file, fn_rx_mult, 0xd5u};           /* ROM 0x781ea8 */
static const g2_fault_record_t fault_tx_mult = {0u, 0u, 0u, source_file, fn_tx_mult, 0xedu};           /* ROM 0x781ebc */
static const g2_fault_record_t fault_rx_single_hl = {0u, 0u, 0u, source_file, fn_rx_single_hl, 0x139u}; /* ROM 0x781ed0 */
static const g2_fault_record_t fault_tx_single_hl = {0u, 0u, 0u, source_file, fn_tx_single_hl, 0x150u}; /* ROM 0x781ee4 */
static const g2_fault_record_t fault_rx_mult_hl = {0u, 0u, 0u, source_file, fn_rx_mult_hl, 0x176u};    /* ROM 0x781ef8 */
static const g2_fault_record_t fault_tx_mult_hl = {0u, 0u, 0u, source_file, fn_tx_mult_hl, 0x18eu};    /* ROM 0x781f0c */

#define LOG_E(level, fn, line, ...)                                                          \
    do {                                                                                     \
        if ((audio_log_flags() & 2u) != 0u)                                                  \
            audio_log_extended((level), module_tag, source_file, (fn), (line), __VA_ARGS__); \
    } while (0)
#define LOG_C(code, text, ...)                                                    \
    do {                                                                          \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)     \
            (void)compress_log_output((code), (text), (text), ##__VA_ARGS__);     \
    } while (0)

static void raise_fault(const g2_fault_record_t *record)
{
    g2_fault_record_t fault;
    (void)aeabi_memcpy4_439c04(&fault, record, sizeof fault);
    fault.code = 1u;
    APP_errorFaultHandler(&fault);
}

/* Common NULL path of every handler: fault record, log, return 2. */
static uint32_t null_input(const g2_fault_record_t *record, uint32_t line)
{
    raise_fault(record);
    LOG_E(1u, record->function, line, null_text);
    LOG_C(0x04000000u, null_short);
    return 2u;
}

/* Clears the shared message and writes the command header; returns it. */
static uint8_t *msg_begin(g2_pb_ostream_t *stream, uint8_t command, uint8_t magic, uint16_t tag)
{
    g2_pb_ostream_t initial;
    audio_pb_ostream_from_buffer(&initial, g2_health_pb_tx_packet, HEALTH_PACKET_SIZE);
    (void)aeabi_memcpy4_439c04(stream, &initial, sizeof *stream);
    uint8_t *msg = g2_health_pb_tx_msg;
    (void)aeabi_memset_43c0e4(msg, HEALTH_MSG_SIZE, 0);
    msg[HEALTH_MSG_CMD] = command;
    msg[HEALTH_MSG_MAGIC] = magic;
    *(uint16_t *)(void *)(msg + HEALTH_MSG_TAG) = tag;
    return msg;
}

/* Encodes the shared message and sends it; 0 sent, 0x2b encode failure. */
static uint32_t msg_send(g2_pb_ostream_t *stream, const char *fn, uint32_t len_line, uint32_t err_line)
{
    uint8_t encoded = (uint8_t)audio_pb_encode(stream, g2_health_pb_descriptor, g2_health_pb_tx_msg);
    uint16_t written = (uint16_t)stream->bytes_written;
    LOG_E(4u, fn, len_line, tx_len_text, written);
    LOG_C(0x10400000u, tx_len_short, written);
    if (encoded == 0u) {
        LOG_E(1u, fn, err_line, encode_fail, stream->errmsg != NULL ? stream->errmsg : none_text);
        LOG_C(0x04400000u, encode_fail_short, stream->errmsg != NULL ? stream->errmsg : none_text);
        return 0x2bu;
    }
    (void)Thread_MsgPbTxByBle(1u, HEALTH_SERVICE_ID, g2_health_pb_tx_packet, written);
    return 0u;
}

uint32_t PB_RxHealthSingleData(uint8_t magic, const g2_health_pb_data_t *data)
{
    (void)magic;
    if (data == NULL)
        return null_input(&fault_rx_single, 0x6fu);
    LOG_E(4u, fn_rx_single, 0x74u, single_info, data->type, data->goal, (double)data->value,
          (double)data->avg_value, data->duration, data->trend);
    LOG_C(0x11800000u, single_info_s, data->type, data->goal, (double)data->value,
          (double)data->avg_value, data->duration, data->trend);
    uint8_t rc = health_data_save_single_5598cc(data);
    if (rc != 0u) {
        LOG_E(1u, fn_rx_single, 0x79u, single_fail, rc);
        LOG_C(0x04400000u, single_fail_s, rc);
        return 1u;
    }
    LOG_E(3u, fn_rx_single, 0x7du, single_ok, data->type);
    LOG_C(0x0c400000u, single_ok_s, data->type);
    return 0u;
}

uint32_t APP_PbTxEncodeHealthSingleData(uint8_t magic, const g2_health_pb_data_t *data)
{
    if (data == NULL)
        return null_input(&fault_tx_single, 0x86u);
    g2_pb_ostream_t stream;
    uint8_t *msg = msg_begin(&stream, 1u, magic, 3u);
    msg[0x04] = data->type;
    *(uint32_t *)(void *)(msg + 0x08) = data->goal;
    *(float *)(void *)(msg + 0x0c) = data->value;
    *(float *)(void *)(msg + 0x10) = data->avg_value;
    *(uint32_t *)(void *)(msg + 0x14) = data->duration;
    msg[0x19] = data->trend;
    msg[0x18] = 0u;
    return msg_send(&stream, fn_tx_single, 0x9fu, 0xa2u);
}

uint32_t PB_RxHealthMultData(uint8_t magic, const g2_health_pb_mult_data_t *data)
{
    (void)magic;
    if (data == NULL)
        return null_input(&fault_rx_mult, 0xd7u);
    LOG_E(4u, fn_rx_mult, 0xdcu, mult_info, data->type, data->count);
    LOG_C(0x10800000u, mult_info_s, data->type, data->count);
    uint8_t rc = health_data_save_mult_559ad2(data);
    if (rc != 0u) {
        LOG_E(1u, fn_rx_mult, 0xe1u, mult_fail, rc);
        LOG_C(0x04400000u, mult_fail_s, rc);
        return 1u;
    }
    LOG_E(3u, fn_rx_mult, 0xe6u, mult_ok, data->type, data->count);
    LOG_C(0x0c800000u, mult_ok_s, data->type, data->count);
    return 0u;
}

uint32_t APP_PbTxEncodeHealthMultData(uint8_t magic, const g2_health_pb_mult_data_t *data)
{
    if (data == NULL)
        return null_input(&fault_tx_mult, 0xefu);
    g2_pb_ostream_t stream;
    uint8_t *msg = msg_begin(&stream, 2u, magic, 4u);
    msg[0x04] = data->type;
    msg[0xc8] = 0u;
    return msg_send(&stream, fn_tx_mult, 0x104u, 0x107u);
}

uint32_t PB_RxHealthSingleHighlight(uint8_t magic, const g2_health_pb_highlight_t *highlight)
{
    (void)magic;
    if (highlight == NULL)
        return null_input(&fault_rx_single_hl, 0x13bu);
    LOG_E(4u, fn_rx_single_hl, 0x140u, shl_info, highlight->type, highlight->text_size);
    LOG_C(0x10800000u, shl_info_s, highlight->type, highlight->text_size);
    uint8_t rc = health_data_save_single_highlight_559dfc(highlight);
    if (rc != 0u) {
        LOG_E(1u, fn_rx_single_hl, 0x145u, shl_fail, rc);
        LOG_C(0x04400000u, shl_fail_s, rc);
        return 1u;
    }
    LOG_E(3u, fn_rx_single_hl, 0x149u, shl_ok, highlight->type);
    LOG_C(0x0c400000u, shl_ok_s, highlight->type);
    return 0u;
}

uint32_t APP_PbTxEncodeHealthSingleHighlight(uint8_t magic, const g2_health_pb_highlight_t *highlight)
{
    if (highlight == NULL)
        return null_input(&fault_tx_single_hl, 0x152u);
    g2_pb_ostream_t stream;
    uint8_t *msg = msg_begin(&stream, 3u, magic, 5u);
    msg[0x004] = highlight->type;
    msg[0x108] = 0u;
    return msg_send(&stream, fn_tx_single_hl, 0x168u, 0x16bu);
}

uint32_t PB_RxHealthMultHighlight(uint8_t magic, const g2_health_pb_mult_highlight_t *highlights)
{
    (void)magic;
    if (highlights == NULL)
        return null_input(&fault_rx_mult_hl, 0x178u);
    LOG_E(4u, fn_rx_mult_hl, 0x17du, mhl_info, highlights->count);
    LOG_C(0x10400000u, mhl_info_s, highlights->count);
    uint8_t rc = health_data_save_mult_highlight_559fb8(highlights);
    if (rc != 0u) {
        LOG_E(1u, fn_rx_mult_hl, 0x182u, mhl_fail, rc);
        LOG_C(0x04400000u, mhl_fail_s, rc);
        return 1u;
    }
    LOG_E(3u, fn_rx_mult_hl, 0x187u, mhl_ok, highlights->count);
    LOG_C(0x0c400000u, mhl_ok_s, highlights->count);
    return 0u;
}

uint32_t APP_PbTxEncodeHealthMultHighlight(uint8_t magic, const g2_health_pb_mult_highlight_t *highlights)
{
    if (highlights == NULL)
        return null_input(&fault_tx_mult_hl, 0x190u);
    g2_pb_ostream_t stream;
    uint8_t *msg = msg_begin(&stream, 4u, magic, 6u);
    *(uint16_t *)(void *)(msg + 0x004) = highlights->count;
    for (int32_t i = 0; i < (int32_t)highlights->count; i++) {
        msg[0x006 + (uint32_t)i * 0x106u] = highlights->item[i].type;
        msg[0x10a + (uint32_t)i * 0x106u] = highlights->item[i].flag104;
    }
    msg[0x318] = 0u;
    return msg_send(&stream, fn_tx_mult_hl, 0x1adu, 0x1b0u);
}
