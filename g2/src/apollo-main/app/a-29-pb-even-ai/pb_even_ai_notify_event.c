/* EvenAI event notification encoder, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\pb_service_even_ai\pb_service_even_ai.c.
 * Native 0x4e4cb8..0x4e4e49; literal pools 0x4e50d4, 0x4e51b0..0x4e51bf,
 * 0x4e4f20, 0x4e5334, 0x4e5454..0x4e5473.
 *
 * Same message as APP_PbTxEncodeEvenAIEvent (command 8, oneof tag 10, one
 * event byte) but the sequence comes from the local notify counter and the
 * frame goes out through Thread_MsgPbNotifyByBle on service 7. The sibling
 * notify encoders (Ctrl 0x4e3788, VADInfo 0x4e3b80) are in
 * audio/even-ai/even_ai_notify_encoders_4e3788.c. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* nanopb 0.4.9 pb_ostream_t (PB_NO_ERRMSG not set), 20 bytes. */
typedef struct g2_pb_ostream {
    bool (*callback)(struct g2_pb_ostream *stream, const uint8_t *buf, size_t count);
    void *state;
    size_t max_size;
    size_t bytes_written; /* +0x0c */
    const char *errmsg;   /* +0x10 */
} g2_pb_ostream_t;
_Static_assert(sizeof(g2_pb_ostream_t) == 20u, "pb_ostream_t ABI");

/* Record passed to APP_errorFaultHandler; ROM template 0x781d90. */
typedef struct {
    uint32_t type;        /* +0x00 */
    uint32_t detail;      /* +0x04 low half set to 1 */
    const char *path;     /* +0x08 */
    const char *function; /* +0x0c */
    uint32_t line;        /* +0x10 */
} g2_even_ai_fault_record_t;
_Static_assert(sizeof(g2_even_ai_fault_record_t) == 20u, "fault record ABI");

#define EVEN_AI_CMD_EVENT 8u
#define EVEN_AI_ONEOF_EVENT 10u
#define EVEN_AI_PB_SERVICE 7u
#define EVEN_AI_MESSAGE_SIZE 0x20cu

extern uint8_t audio_even_ai_tx_buffer_2037c4a0[256];                     /* RAM 0x2037c4a0 */
extern uint8_t audio_even_ai_proto_message_200f5884[EVEN_AI_MESSAGE_SIZE]; /* RAM 0x200f5884 */
extern uint8_t audio_even_ai_notify_sequence_20074ff9;                    /* RAM 0x20074ff9 */
extern const uint8_t audio_even_ai_decode_fields[];                       /* ROM 0x777144 pb_msgdesc_t */

extern g2_pb_ostream_t pb_ostream_from_buffer(uint8_t *buf, size_t bufsize); /* 0x4905f4 */
extern bool pb_encode(g2_pb_ostream_t *stream, const void *fields, const void *src); /* 0x490c32 */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void audio_ring_pb_assert_509b48(const g2_even_ai_fault_record_t *record); /* APP_errorFaultHandler */
extern uint32_t audio_ring_pb_tx_ble_475c1a(uint32_t type, uint32_t service, const void *data,
                                            uint32_t length);             /* Thread_MsgPbNotifyByBle */
extern uint32_t audio_log_flags(void);                                    /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                       /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "pb.evenai"; /* ROM 0x78b6f0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_even_ai\\pb_service_even_ai.c"; /* ROM 0x6de0d4 */
static const char notify_event_fn[] = "APP_PbNotifyEncodeEvenAIEvent"; /* ROM 0x763370 */
static const char null_msg[] = "PORINT NULL"; /* ROM 0x78b6fc */
static const char null_short[] = "[pb.evenai]PORINT NULL"; /* ROM 0x77a18c */
static const char tx_len_msg[] = "txLen = %d"; /* ROM 0x78b708 */
static const char tx_len_short[] = "[pb.evenai]txLen = %d"; /* ROM 0x77a1a4 */
static const char encode_err_msg[] = "Encoding failed: %s\n"; /* ROM 0x77a1bc */
static const char encode_err_short[] = "[pb.evenai]Encoding failed: %s\n"; /* ROM via 0x4e4f20 */
static const char none_text[] = "(none)"; /* ROM 0x78deb4 */

static const g2_even_ai_fault_record_t notify_event_fault = {
    0u, 0u, source_file, notify_event_fn, 0x2dbu
}; /* ROM 0x781d90 */

#define LOG_COMPRESSED() \
    ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

/* Returns 0 sent, 2 NULL event, 0x2b encode failure. */
uint32_t APP_PbNotifyEncodeEvenAIEvent(uint32_t unused, const uint8_t *event) {
    (void)unused;
    if (event == NULL) {
        g2_even_ai_fault_record_t fault = notify_event_fault;
        *(uint16_t *)(void *)&fault.detail = 1u;
        audio_ring_pb_assert_509b48(&fault);
    }
    if (event == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, notify_event_fn, 0x2ddu, null_msg);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x04000000u, null_short, null_short);
        return 2u;
    }

    g2_pb_ostream_t stream = pb_ostream_from_buffer(audio_even_ai_tx_buffer_2037c4a0, 256u);
    uint8_t *message = audio_even_ai_proto_message_200f5884;
    (void)aeabi_memset_43c0e4(message, EVEN_AI_MESSAGE_SIZE, 0);
    message[0] = EVEN_AI_CMD_EVENT;
    message[1] = audio_even_ai_notify_sequence_20074ff9++;
    *(uint16_t *)(void *)(message + 2) = EVEN_AI_ONEOF_EVENT;
    message[4] = event[0];
    bool encoded = pb_encode(&stream, audio_even_ai_decode_fields, message);
    uint32_t length = stream.bytes_written;

    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, notify_event_fn, 0x2f0u, tx_len_msg,
                           length & 0xffffu);
    if (LOG_COMPRESSED())
        (void)compress_log_output(0x10400000u, tx_len_short, tx_len_short, length & 0xffffu);
    if (!encoded) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, notify_event_fn, 0x2f3u,
                               encode_err_msg, stream.errmsg != NULL ? stream.errmsg : none_text);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x04400000u, encode_err_short, encode_err_short,
                                      stream.errmsg != NULL ? stream.errmsg : none_text);
        return 0x2bu;
    }
    (void)audio_ring_pb_tx_ble_475c1a(1u, EVEN_AI_PB_SERVICE, audio_even_ai_tx_buffer_2037c4a0,
                                       length & 0xffffu);
    return 0u;
}
