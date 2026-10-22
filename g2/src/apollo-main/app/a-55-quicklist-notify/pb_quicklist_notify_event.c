/* QuickList event notification encoder, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\pb_service_quicklist\pb_service_quicklist.c
 * (path ROM 0x6db358, module tag "pb.quicklist" ROM 0x787ea0).
 * Native APP_PbNotifyEncodeQuicklistEvent 0x55960c..0x559777, literal pool
 * 0x5597c8..0x5597ef; NULL fault template ROM 0x7823d0 (line 0x17c).
 *
 * Root message command 3 / oneof tag 5 (event), magic from the rolling
 * notify sequence byte, sent with Thread_MsgPbNotifyByBle on service 0x0c.
 * The packet and message buffers are shared with the QuickList Tx encoders
 * (app/quicklist-tx). Event payload: event byte at +0, uid at +4. */
#include <stdint.h>
#include <stddef.h>

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

/* QuickList event (caller ui/a-35-quicklist-page). */
typedef struct {
    uint8_t event;  /* +0x00 */
    uint8_t pad[3];
    uint32_t uid;   /* +0x04 */
} g2_quicklist_event_t;

#define QUICKLIST_SERVICE_ID   0x0cu
#define QUICKLIST_PACKET_SIZE  0x400u
#define QUICKLIST_STATE_SIZE   0x1238u
#define QUICKLIST_CMD_EVENT    3u
#define QUICKLIST_TAG_EVENT    5u

extern uint8_t audio_quicklist_tx_packet[0x400];   /* RAM 0x2037a5a0 */
extern uint8_t audio_quicklist_tx_state[0x1238];   /* RAM 0x200f7484 */
extern const uint8_t audio_quicklist_pb_descriptor[]; /* ROM 0x77b02c */
extern volatile uint8_t g2_quicklist_notify_seq;   /* RAM 0x20074ffd, notify magic counter */

extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);   /* 0x439c04 */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);      /* 0x43c0e4 */
extern void audio_pb_ostream_from_buffer(g2_pb_ostream_t *out, void *buf, uint32_t size); /* 0x4905f4 */
extern uint32_t audio_pb_encode(void *stream, const void *fields, const void *src);       /* pb_encode 0x490c32 */
extern uint32_t Thread_MsgPbNotifyByBle(uint8_t type, uint8_t command, const void *payload,
                                        uint16_t length);                       /* 0x475c1a */
extern void APP_errorFaultHandler(const g2_fault_record_t *record);             /* 0x509b48 */
extern uint32_t audio_log_flags(void);                                          /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                              /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "pb.quicklist"; /* ROM 0x787ea0 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_quicklist\\pb_service_quicklist.c"; /* ROM 0x6db358 */
static const char fn_notify_event[] = "APP_PbNotifyEncodeQuicklistEvent"; /* ROM 0x757d4c */
static const char null_text[] = "PORINT NULL";                       /* ROM 0x78b798 */
static const char null_short[] = "[pb.quicklist]PORINT NULL";        /* ROM 0x76f9b0 */
static const char tx_len_text[] = "txLen = %d";                      /* ROM 0x78b7a4 */
static const char tx_len_short[] = "[pb.quicklist]txLen = %d";       /* ROM 0x76f9cc */
static const char encode_fail[] = "Encoding failed: %s\n";           /* ROM 0x77a594 */
static const char encode_fail_short[] = "[pb.quicklist]Encoding failed: %s\n"; /* ROM 0x757d04 */
static const char none_text[] = "(none)";                            /* ROM 0x78df44 */

static const g2_fault_record_t fault_notify_event = {0u, 0u, 0u, source_file, fn_notify_event, 0x17cu}; /* ROM 0x7823d0 */

#define LOG_EXT_ON() ((audio_log_flags() & 2u) != 0u)
#define LOG_CMP_ON() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

int32_t APP_PbNotifyEncodeQuicklistEvent(uint32_t unused, const g2_quicklist_event_t *event)
{
    (void)unused;
    if (event == NULL) {
        g2_fault_record_t fault;
        (void)aeabi_memcpy4_439c04(&fault, &fault_notify_event, sizeof fault);
        fault.code = 1u;
        APP_errorFaultHandler(&fault);
        if (LOG_EXT_ON())
            audio_log_extended(1u, module_tag, source_file, fn_notify_event, 0x17eu, null_text);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x04000000u, null_short, null_short);
        return 2;
    }

    g2_pb_ostream_t initial, stream;
    audio_pb_ostream_from_buffer(&initial, audio_quicklist_tx_packet, QUICKLIST_PACKET_SIZE);
    (void)aeabi_memcpy4_439c04(&stream, &initial, sizeof stream);

    uint8_t *msg = audio_quicklist_tx_state;
    (void)aeabi_memset_43c0e4(msg, QUICKLIST_STATE_SIZE, 0);
    msg[0] = QUICKLIST_CMD_EVENT;
    msg[1] = g2_quicklist_notify_seq;
    g2_quicklist_notify_seq = (uint8_t)(g2_quicklist_notify_seq + 1u);
    *(uint16_t *)(void *)(msg + 2) = QUICKLIST_TAG_EVENT;
    msg[8] = event->event;
    *(uint32_t *)(void *)(msg + 0x0c) = event->uid;

    uint8_t encoded = (uint8_t)audio_pb_encode(&stream, audio_quicklist_pb_descriptor, msg);
    uint16_t written = (uint16_t)stream.bytes_written;
    if (LOG_EXT_ON())
        audio_log_extended(4u, module_tag, source_file, fn_notify_event, 0x192u, tx_len_text, written);
    if (LOG_CMP_ON())
        (void)compress_log_output(0x10400000u, tx_len_short, tx_len_short, written);
    if (encoded == 0u) {
        if (LOG_EXT_ON())
            audio_log_extended(1u, module_tag, source_file, fn_notify_event, 0x195u, encode_fail,
                               stream.errmsg != NULL ? stream.errmsg : none_text);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x04400000u, encode_fail_short, encode_fail_short,
                                      stream.errmsg != NULL ? stream.errmsg : none_text);
        return 0x2b;
    }
    (void)Thread_MsgPbNotifyByBle(1u, QUICKLIST_SERVICE_ID, audio_quicklist_tx_packet, written);
    return 0;
}
