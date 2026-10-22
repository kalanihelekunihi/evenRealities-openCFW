/* Apollo-side GX8002 control link, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\audio\service_codec_host.c
 * (module tag "codec.host"), native 0x57ba88..0x57dc40.
 *
 * Transport: UART channel 3 (Apollo UART3, 0x4003c000) at 115200 baud,
 * opened per transaction by gx8002_host_init and closed by
 * semantic_gx8002_uart_cleanup. Every frame is a 14-byte "BUXX" header plus
 * an optional body of at most 16 bytes (body CRC included):
 *   +0  magic "BUXX"
 *   +4  command u16 LE: low byte TYPE (command id), high byte NR (0x01
 *       request, 0x02 response, 0x03 asynchronous codec event)
 *   +6  sequence u8 (host counter at RAM 0x20075013, wraps)
 *   +7  flags u8, bit 0 = 4-byte body CRC-32 appended
 *   +8  body length u16 LE (payload + 4 when flag bit 0)
 *   +10 header CRC-32 (zlib, reflected 0xedb88320) over bytes 0..9
 * gx8002_unpack_message expands a received frame into the 26-byte
 * g2_gx8002_message_t below (heap copy of the payload at +14). */
#ifndef G2_GX8002_HOST_LOCAL_H
#define G2_GX8002_HOST_LOCAL_H

#include <stdint.h>

#define GX8002_FAMILY_REQUEST 0x100u /* NR byte of host requests */
#define GX8002_ATTEMPTS 3
#define GX8002_SVC_TIMEOUT 200u      /* ticks, every SVC_* wrapper */
#define GX8002_RX_CAPACITY 30u       /* RX scratch 0x2007397c..0x20073999 */

/* Command ids (TYPE byte). Request is 0x01xx; the codec answers 0x02xx
 * with a 2-byte status (0x0202 version: 4 bytes), except 0x010e and
 * 0x010f, which the codec answers with the request command and 1 byte. */
enum {
    GX8002_CMD_READ_VERSION = 0x02u,
    GX8002_CMD_SWITCH_BF_MODE = 0x07u,
    GX8002_CMD_SWITCH_WAKEUP_MODE = 0x08u,
    GX8002_CMD_SET_MIC_GAIN = 0x0bu,
    GX8002_CMD_DMIC_OPEN = 0x0cu,
    GX8002_CMD_DMIC_CLOSE = 0x0du,
    GX8002_CMD_MIC_DELAY_1BIT = 0x0eu,
    GX8002_CMD_I2S_OUTPUT = 0x0fu,
    GX8002_CMD_QUERY_MIC_STATE = 0x70u,
};

/* Asynchronous codec events (0x03xx frames, read by GX8002_GetVoiceEvent). */
enum {
    GX8002_EVENT_WAKEUP = 0x0cu, /* keyword/wake detected */
    GX8002_EVENT_VAD = 0x0du,    /* value 1 = voice, 0 = silence */
};

/* Unpacked message, packed 26-byte stack record used by every caller. */
typedef struct __attribute__((packed)) {
    uint8_t magic[4];     /* +0x00 */
    uint8_t type;         /* +0x04 command low byte */
    uint8_t nr;           /* +0x05 command high byte */
    uint8_t seq;          /* +0x06 */
    uint8_t flags;        /* +0x07 */
    uint16_t length;      /* +0x08 wire body length */
    uint32_t header_crc;  /* +0x0a */
    uint8_t *body;        /* +0x0e heap copy, freed by semantic_gx8002_free_message */
    uint16_t body_length; /* +0x12 payload bytes (CRC excluded) */
    uint32_t body_crc;    /* +0x14 */
    uint16_t total;       /* +0x18 wire bytes consumed */
} g2_gx8002_message_t;
_Static_assert(sizeof(g2_gx8002_message_t) == 26u, "stock 26-byte message record");

/* Output of GX8002_GetVoiceEvent. */
typedef struct {
    uint8_t id;     /* +0 event TYPE byte (0x0c / 0x0d) */
    uint8_t pad;    /* +1 */
    uint16_t value; /* +2 first two body bytes, LE */
} g2_gx8002_voice_event_t;
_Static_assert(sizeof(g2_gx8002_voice_event_t) == 4u, "voice event record");

/* Assigned stock functions defined in this directory. */
int32_t semantic_gx8002_magic_matches(const void *frame);
int32_t gx8002_uart_read_blocking(uint8_t *buffer, uint16_t capacity, uint32_t timeout);
int32_t GX8002_ReadVersion(uint8_t version[4], uint32_t timeout);
int32_t GX8002_SwitchBFMode(uint8_t *status, uint32_t timeout);
int32_t GX8002_SwitchWakeupMode(uint8_t *status, uint32_t timeout);
int32_t GX8002_QueryMicState(uint16_t *state, uint32_t timeout);
int32_t GX8002_SetMicGain(uint8_t gain, uint16_t *status, uint32_t timeout);
int32_t GX8002_MicDelay1Bit(uint8_t *status, uint32_t timeout);
int32_t SVC_SwitchBFMode(void);
int32_t SVC_SwitchWakeupMode(void);
int32_t SVC_SetMicGain(uint8_t gain);
int32_t SVC_CodecMicDelay1Bit(void);
int32_t GX8002_GetVoiceEvent(g2_gx8002_voice_event_t *event);

/* Stock codec.host functions already reconstructed elsewhere in g2/src under
 * these names (address and TSV name in each comment). */
extern int32_t audio_transaction_init(void);   /* gx8002_host_init 0x57ba88 */
extern void audio_transaction_cleanup(void);   /* semantic_gx8002_uart_cleanup 0x57baec */
extern int32_t audio_transaction_extract(const void *wire, uint32_t available,
                                         void *message); /* gx8002_unpack_message 0x57bd06 */
extern int32_t audio_transaction_exchange(void *buffer, uint32_t capacity,
                                          uint16_t *length,
                                          uint32_t timeout); /* gx8002_read_uart_data 0x57c442 */
extern int32_t audio_send_transaction(uint32_t code, uint32_t family,
                                      const void *payload, uint32_t length,
                                      uint32_t flags, void *message,
                                      uint32_t timeout); /* gx8002_send_and_wait_response 0x57c512 */
extern void audio_release_transaction(void *message); /* semantic_gx8002_free_message 0x57c640 */

/* Shared helpers. */
extern void audio_uart_buffer_zero(void *buffer, uint32_t length, uint32_t fill); /* 0x43c0e4 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t level, const char *module, const char *file,
                               const char *function, uint32_t line,
                               const char *format, ...); /* 0x43d574 */
/* mask = (level << 26) | (argument count << 22); level 1 error .. 4 debug. */
extern uint32_t compress_log_output(uint32_t mask, const char *format,
                                    const char *copy, ...); /* 0x43ce9e */

/* Stock LOG expansion: extended record when flag bit 1, compressed record
 * when bit 0 or bit 2. Uses the including file's `module` and `file`. */
#define GX8002_LOG(level, mask, function, line, format, simple, ...)            \
    do {                                                                        \
        if (audio_log_flags() & 2u)                                             \
            audio_log_extended((level), module, file, (function), (line),       \
                               (format), ##__VA_ARGS__);                        \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))               \
            (void)compress_log_output((mask), (simple), (simple),               \
                                      ##__VA_ARGS__);                           \
    } while (0)

#endif
