/* Onboarding protobuf service, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\pb_service_onboarding\pb_service_onboarding.c.
 * Native 0x4a78d0..0x4a833c (APP_PbRxOnboardingFrameDataProcess .. APP_PbTxEncodeOnboardingEvent);
 * APP_PbNotifyEncodeOnboardingEvent 0x4a8368 follows in app/onboarding-event.
 *
 * Phone frames (BLE service id 0x10) decode with the nanopb descriptor at ROM
 * 0x779c94 into a 16-byte message: command_id 1 = config, 2 = heartbeat,
 * 3 = event, each answered with the same command id and the request's
 * magic_random. Notifies use the module sequence byte instead. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint8_t process_id;   /* +0 */
    uint8_t substep;      /* +1, always 0 in replies */
} g2_onboarding_config_t;

typedef struct {
    uint8_t status;       /* +0 0 = onboarding app in front, 8 = not */
} g2_onboarding_heartbeat_t;

typedef struct {
    uint8_t event;        /* +0 */
    uint32_t param;       /* +4 */
    uint8_t flag;         /* +8, always 0 in replies */
} g2_onboarding_event_t;
_Static_assert(sizeof(g2_onboarding_event_t) == 12u, "event submessage");

/* Top-level message (RAM 0x200f622c rx, 0x200f623c tx). */
typedef struct {
    uint8_t command_id;       /* +0 */
    uint8_t magic_random;     /* +1 */
    uint16_t which_payload;   /* +2 oneof tag: 3 config, 4 heartbeat, 5 event */
    union {
        g2_onboarding_config_t config;
        g2_onboarding_heartbeat_t heartbeat;
        g2_onboarding_event_t event;
    } payload;                /* +4 */
} g2_onboarding_msg_t;
_Static_assert(sizeof(g2_onboarding_msg_t) == 16u, "onboarding message");

/* nanopb 0.4 pb_istream_t / pb_ostream_t. */
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

/* APP_errorFaultHandler record; the ROM templates carry code 0, the caller sets 1. */
typedef struct {
    uint32_t type;            /* +0x00 */
    uint16_t code;            /* +0x04 */
    uint16_t reserved;
    const char *path;         /* +0x08 */
    const char *function;     /* +0x0c */
    uint32_t line;            /* +0x10 */
} g2_fault_record_t;
_Static_assert(sizeof(g2_fault_record_t) == 20u, "fault record");

enum { ONBOARDING_CMD_CONFIG = 1u, ONBOARDING_CMD_HEARTBEAT = 2u, ONBOARDING_CMD_EVENT = 3u };
enum { ONBOARDING_TAG_CONFIG = 3u, ONBOARDING_TAG_HEARTBEAT = 4u, ONBOARDING_TAG_EVENT = 5u };
#define ONBOARDING_SERVICE_ID 0x10u
#define ONBOARDING_APP_ID     0x10u
#define PB_TX_BUFFER_SIZE     256u

g2_onboarding_msg_t g2_onboarding_rx_msg;                            /* RAM 0x200f622c */
extern uint8_t audio_onboarding_event_packet_200f612c[PB_TX_BUFFER_SIZE];  /* RAM 0x200f612c */
extern g2_onboarding_msg_t audio_onboarding_event_state_200f623c;   /* RAM 0x200f623c */
extern uint8_t audio_onboarding_event_sequence_20074ffb;            /* RAM 0x20074ffb */
extern const uint8_t audio_onboarding_event_descriptor_779c94[];    /* ROM 0x779c94 pb_msgdesc_t */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);                /* 0x43c0e4 */
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* word copy */
extern void audio_uart_pb_stream_init(g2_pb_istream_t *out, const void *buf, uint32_t size); /* pb_istream_from_buffer 0x48f49c */
extern uint32_t audio_uart_pb_decode(void *stream, const void *fields, void *dest);          /* pb_decode 0x490120 */
extern void audio_pb_ostream_from_buffer(g2_pb_ostream_t *out, void *buf, uint32_t size);   /* 0x4905f4 */
extern uint32_t audio_pb_encode(void *stream, const void *fields, const void *src);          /* pb_encode 0x490c32 */
extern void APP_errorFaultHandler(const g2_fault_record_t *record);
extern uint32_t Thread_MsgPbTxByBle(uint8_t type, uint8_t command, const void *payload, uint16_t length);
extern uint32_t Thread_MsgPbNotifyByBle(uint8_t type, uint8_t command, const void *payload, uint16_t length);
/* Stock passes the decoded submessage size in r2 (2 config, 12 event); the
 * handler body (0x47e2d0) only reads type and data. */
extern uint32_t onboarding_common_data_handler(uint8_t type, const void *data, uint32_t size);
extern uint32_t audio_log_wake_allowed(void);                   /* 0x443484: RAM 0x20074f2c == 1 */
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t app_id);
extern uint32_t audio_uart_lcd_status(void);                     /* 0x49eb8e: RAM 0x20074edc */

static const char module_tag[] = "pb.onboarding"; /* ROM 0x787e20 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_onboarding\\pb_service_onboarding.c"; /* ROM 0x6d95cc */
static const char fn_frame[] = "APP_PbRxOnboardingFrameDataProcess";      /* ROM 0x757ae8 */
static const char fn_rx_config[] = "PB_RxOnboardingConfig";               /* ROM 0x77a48c */
static const char fn_tx_config[] = "APP_PbTxEncodeOnboardingConfig";      /* ROM 0x7635d0 */
static const char fn_notify_config[] = "APP_PbNotifyEncodeOnboardingConfig"; /* ROM 0x757b54 */
static const char fn_rx_heartbeat[] = "PB_RxOnboardingHeartbeat";         /* ROM 0x76f7b8 */
static const char fn_tx_heartbeat[] = "APP_PbTxEncodeOnboardingHeartbeat"; /* ROM 0x757b78 */
static const char fn_rx_event[] = "PB_RxOnboardingEvent";                 /* ROM 0x77a4bc */
static const char fn_tx_event[] = "APP_PbTxEncodeOnboardingEvent";        /* ROM 0x7635f0 */
static const char none_text[] = "(none)";                                 /* ROM 0x78def4 */

/* ROM 0x782010..0x78209b: one fault template per NULL check. */
static const g2_fault_record_t fault_rx_config = {0u, 0u, 0u, source_file, fn_rx_config, 0x67u};
static const g2_fault_record_t fault_tx_config = {0u, 0u, 0u, source_file, fn_tx_config, 0x75u};
static const g2_fault_record_t fault_notify_config = {0u, 0u, 0u, source_file, fn_notify_config, 0x98u};
static const g2_fault_record_t fault_rx_heartbeat = {0u, 0u, 0u, source_file, fn_rx_heartbeat, 0xbcu};
static const g2_fault_record_t fault_tx_heartbeat = {0u, 0u, 0u, source_file, fn_tx_heartbeat, 0xc9u};
static const g2_fault_record_t fault_rx_event = {0u, 0u, 0u, source_file, fn_rx_event, 0xf0u};
static const g2_fault_record_t fault_tx_event = {0u, 0u, 0u, source_file, fn_tx_event, 0xfeu};

#define ONB_LOG(level, fn, line, mask, fmt, ...) do { \
    if (audio_log_flags() & 2u) \
        audio_log_extended((level), module_tag, source_file, (fn), (line), fmt, ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) \
        (void)compress_log_output((mask), "[pb.onboarding]" fmt, "[pb.onboarding]" fmt, ##__VA_ARGS__); \
} while (0)

/* Stock NULL guard: raise the fault record, then log and return 2. */
#define ONB_CHECK_NULL(ptr, record, fn, line) do { \
    if ((ptr) == NULL) { \
        g2_fault_record_t fault_; \
        (void)audio_uart_display_area_copy_439c04(&fault_, &(record), sizeof fault_); \
        fault_.code = 1u; \
        APP_errorFaultHandler(&fault_); \
    } \
    if ((ptr) == NULL) { \
        ONB_LOG(1u, (fn), (line), 0x04000000u, "POINTER NULL"); \
        return 2u; \
    } \
} while (0)

uint32_t PB_RxOnboardingConfig(uint8_t magic, const g2_onboarding_config_t *config);
uint32_t APP_PbTxEncodeOnboardingConfig(uint8_t magic, const g2_onboarding_config_t *config);
uint32_t PB_RxOnboardingHeartbeat(uint8_t magic, const g2_onboarding_heartbeat_t *heartbeat);
uint32_t APP_PbTxEncodeOnboardingHeartbeat(uint8_t magic, const g2_onboarding_heartbeat_t *heartbeat);
uint32_t PB_RxOnboardingEvent(uint8_t magic, const g2_onboarding_event_t *event);
uint32_t APP_PbTxEncodeOnboardingEvent(uint8_t magic, const g2_onboarding_event_t *event);

/* Returns 0 ok, 1 handler/unknown command, 2 NULL, 0x2b decode failure. */
uint32_t APP_PbRxOnboardingFrameDataProcess(const uint8_t *data, uint16_t length)
{
    ONB_LOG(4u, fn_frame, 0x30u, 0x10400000u, "len=%d", length);
    if (data == NULL) {
        ONB_LOG(1u, fn_frame, 0x32u, 0x04000000u, "pData is NULL");
        return 2u;
    }
    g2_onboarding_msg_t *msg = &g2_onboarding_rx_msg;
    audio_uart_buffer_zero(msg, sizeof *msg, 0u);
    g2_pb_istream_t initial, stream;
    audio_uart_pb_stream_init(&initial, data, length);
    (void)audio_uart_display_area_copy_439c04(&stream, &initial, sizeof stream);
    if (audio_uart_pb_decode(&stream, audio_onboarding_event_descriptor_779c94, msg) == 0u) {
        ONB_LOG(1u, fn_frame, 0x3cu, 0x04400000u, "Decoding failed: %s",
                stream.errmsg != NULL ? stream.errmsg : none_text);
        return 0x2bu;
    }
    ONB_LOG(4u, fn_frame, 0x40u, 0x10400000u, "onboarding command_id: %d", msg->command_id);
    switch (msg->command_id) {
    case ONBOARDING_CMD_CONFIG:
        if (PB_RxOnboardingConfig(msg->magic_random, &msg->payload.config) != 0u)
            return 1u;
        return APP_PbTxEncodeOnboardingConfig(msg->magic_random, &msg->payload.config);
    case ONBOARDING_CMD_HEARTBEAT:
        if (PB_RxOnboardingHeartbeat(msg->magic_random, &msg->payload.heartbeat) != 0u)
            return 1u;
        return APP_PbTxEncodeOnboardingHeartbeat(msg->magic_random, &msg->payload.heartbeat);
    case ONBOARDING_CMD_EVENT:
        if (PB_RxOnboardingEvent(msg->magic_random, &msg->payload.event) != 0u)
            return 1u;
        return APP_PbTxEncodeOnboardingEvent(msg->magic_random, &msg->payload.event);
    default:
        ONB_LOG(2u, fn_frame, 0x5du, 0x08400000u, "Unknown command_id: %d", msg->command_id);
        return 1u;
    }
}

uint32_t PB_RxOnboardingConfig(uint8_t magic, const g2_onboarding_config_t *config)
{
    (void)magic;
    ONB_CHECK_NULL(config, fault_rx_config, fn_rx_config, 0x69u);
    ONB_LOG(4u, fn_rx_config, 0x6du, 0x10400000u, "pConfig: process_id = %d", config->process_id);
    (void)onboarding_common_data_handler(1u, config, sizeof *config);
    return 0u;
}

/* Shared tail of the encoders (inlined into each stock body): log the length,
 * report failure or hand the 256-byte packet to the BLE thread as a response
 * (notify == 0) or notify. */
static inline __attribute__((always_inline)) uint32_t
onboarding_send(const char *fn, uint32_t line_len, uint32_t line_fail, uint32_t encoded,
                const g2_pb_ostream_t *stream, uint8_t notify)
{
    uint16_t written = (uint16_t)stream->bytes_written;
    ONB_LOG(4u, fn, line_len, 0x10400000u, "txLen = %d", written);
    if (encoded == 0u) {
        ONB_LOG(1u, fn, line_fail, 0x04400000u, "Encoding failed: %s\n",
                stream->errmsg != NULL ? stream->errmsg : none_text);
        return 0x2bu;
    }
    if (notify)
        (void)Thread_MsgPbNotifyByBle(1u, ONBOARDING_SERVICE_ID, audio_onboarding_event_packet_200f612c, written);
    else
        (void)Thread_MsgPbTxByBle(1u, ONBOARDING_SERVICE_ID, audio_onboarding_event_packet_200f612c, written);
    return 0u;
}

static inline __attribute__((always_inline)) void onboarding_open_stream(g2_pb_ostream_t *stream)
{
    g2_pb_ostream_t initial;
    audio_pb_ostream_from_buffer(&initial, audio_onboarding_event_packet_200f612c, PB_TX_BUFFER_SIZE);
    (void)audio_uart_display_area_copy_439c04(stream, &initial, sizeof *stream);
}

uint32_t APP_PbTxEncodeOnboardingConfig(uint8_t magic, const g2_onboarding_config_t *config)
{
    ONB_CHECK_NULL(config, fault_tx_config, fn_tx_config, 0x77u);
    g2_pb_ostream_t stream;
    onboarding_open_stream(&stream);
    g2_onboarding_msg_t *tx = &audio_onboarding_event_state_200f623c;
    audio_uart_buffer_zero(tx, sizeof *tx, 0u);
    tx->command_id = ONBOARDING_CMD_CONFIG;
    tx->magic_random = magic;
    tx->which_payload = ONBOARDING_TAG_CONFIG;
    tx->payload.config.process_id = config->process_id;
    tx->payload.config.substep = 0u;
    uint32_t encoded = (uint8_t)audio_pb_encode(&stream, audio_onboarding_event_descriptor_779c94, tx);
    return onboarding_send(fn_tx_config, 0x8bu, 0x8eu, encoded, &stream, 0u);
}

uint32_t APP_PbNotifyEncodeOnboardingConfig(uint32_t unused, const g2_onboarding_config_t *config)
{
    (void)unused;
    ONB_CHECK_NULL(config, fault_notify_config, fn_notify_config, 0x9au);
    g2_pb_ostream_t stream;
    onboarding_open_stream(&stream);
    g2_onboarding_msg_t *tx = &audio_onboarding_event_state_200f623c;
    audio_uart_buffer_zero(tx, sizeof *tx, 0u);
    tx->command_id = ONBOARDING_CMD_CONFIG;
    tx->magic_random = audio_onboarding_event_sequence_20074ffb++;
    tx->which_payload = ONBOARDING_TAG_CONFIG;
    tx->payload.config.process_id = config->process_id;
    uint32_t encoded = (uint8_t)audio_pb_encode(&stream, audio_onboarding_event_descriptor_779c94, tx);
    return onboarding_send(fn_notify_config, 0xadu, 0xb1u, encoded, &stream, 1u);
}

uint32_t PB_RxOnboardingHeartbeat(uint8_t magic, const g2_onboarding_heartbeat_t *heartbeat)
{
    (void)magic;
    ONB_CHECK_NULL(heartbeat, fault_rx_heartbeat, fn_rx_heartbeat, 0xbeu);
    return 0u;
}

uint32_t APP_PbTxEncodeOnboardingHeartbeat(uint8_t magic, const g2_onboarding_heartbeat_t *heartbeat)
{
    ONB_CHECK_NULL(heartbeat, fault_tx_heartbeat, fn_tx_heartbeat, 0xcbu);
    g2_pb_ostream_t stream;
    onboarding_open_stream(&stream);
    g2_onboarding_msg_t *tx = &audio_onboarding_event_state_200f623c;
    audio_uart_buffer_zero(tx, sizeof *tx, 0u);
    tx->command_id = ONBOARDING_CMD_HEARTBEAT;
    tx->magic_random = magic;
    tx->which_payload = ONBOARDING_TAG_HEARTBEAT;
    if (audio_log_wake_allowed() == 1u && audio_quicklist_refresh_enabled_4434d0(ONBOARDING_APP_ID) == 1u)
        tx->payload.heartbeat.status = 0u;
    else
        tx->payload.heartbeat.status = 8u;
    uint32_t encoded = (uint8_t)audio_pb_encode(&stream, audio_onboarding_event_descriptor_779c94, tx);
    return onboarding_send(fn_tx_heartbeat, 0xe2u, 0xe5u, encoded, &stream, 0u);
}

uint32_t PB_RxOnboardingEvent(uint8_t magic, const g2_onboarding_event_t *event)
{
    (void)magic;
    ONB_CHECK_NULL(event, fault_rx_event, fn_rx_event, 0xf2u);
    ONB_LOG(4u, fn_rx_event, 0xf6u, 0x10800000u, "pEvent: event = %d, event_param = %d",
            event->event, event->param);
    (void)onboarding_common_data_handler(3u, event, sizeof *event);
    return 0u;
}

/* Event 1 answers with 1 when the display status cell reads 2, else 0. */
uint32_t APP_PbTxEncodeOnboardingEvent(uint8_t magic, const g2_onboarding_event_t *event)
{
    ONB_CHECK_NULL(event, fault_tx_event, fn_tx_event, 0x100u);
    g2_pb_ostream_t stream;
    onboarding_open_stream(&stream);
    g2_onboarding_msg_t *tx = &audio_onboarding_event_state_200f623c;
    audio_uart_buffer_zero(tx, sizeof *tx, 0u);
    tx->command_id = ONBOARDING_CMD_EVENT;
    tx->magic_random = magic;
    tx->which_payload = ONBOARDING_TAG_EVENT;
    tx->payload.event.event = event->event;
    if (tx->payload.event.event == 1u)
        tx->payload.event.param = audio_uart_lcd_status() == 2u;
    else
        tx->payload.event.param = event->param;
    tx->payload.event.flag = 0u;
    uint32_t encoded = (uint8_t)audio_pb_encode(&stream, audio_onboarding_event_descriptor_779c94, tx);
    return onboarding_send(fn_tx_event, 0x119u, 0x11cu, encoded, &stream, 0u);
}
