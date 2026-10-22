/* Shared layout for the EvenHub protobuf reply / event encoders of stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\evenhub_data_parser.c
 * (evenhub_data_parser.c and evenhub_data_parser_fp.c in this directory). */
#ifndef G2_EVENHUB_DATA_PARSER_PRIVATE_H
#define G2_EVENHUB_DATA_PARSER_PRIVATE_H

#include <stdint.h>
#include <stddef.h>

#define EVENHUB_APP_ID          0xe0u   /* BLE / sync service id */
#define EVENHUB_TX_MSG_SIZE     0x3758u
#define EVENHUB_TX_BUFFER_SIZE  0x38ecu

/* Outgoing EvenHub message (RAM 0x20340b48, shares the descriptor of the
 * decoded rx message). The submessage starts at +4; device events carry a
 * second oneof tag at +4 and their fields from +8. */
typedef struct {
    uint8_t cmd;      /* +0 */
    uint8_t seq;      /* +1 magic / sequence echoed from the request */
    uint16_t which;   /* +2 oneof tag of the submessage */
    uint8_t body[EVENHUB_TX_MSG_SIZE - 4u]; /* +4 */
} g2_evenhub_tx_msg_t;
_Static_assert(sizeof(g2_evenhub_tx_msg_t) == EVENHUB_TX_MSG_SIZE, "evenhub tx message");

/* cmd 2 / which 0xd device event, field offsets from the message start. */
enum {
    EVENHUB_DEV_WHICH_OFF = 0x04,      /* u16: 1 list, 2 text, 3 system */
    EVENHUB_DEV_SYS_EVENT_OFF = 0x08,  /* u8 system event type */
    EVENHUB_DEV_SYS_DEVICE_OFF = 0x09, /* u8 input device (1, 2, 3) */
    EVENHUB_DEV_SYS_IMU_OFF = 0x0a,    /* u8 has-IMU flag */
    EVENHUB_DEV_SYS_X_OFF = 0x0c,      /* f32 */
    EVENHUB_DEV_SYS_Y_OFF = 0x10,      /* f32 */
    EVENHUB_DEV_SYS_Z_OFF = 0x14,      /* f32 */
    EVENHUB_DEV_SYS_EXIT_OFF = 0x18,   /* u32 */
    EVENHUB_DEV_CTR_ID_OFF = 0x08,     /* u32 container id (list / text) */
    EVENHUB_DEV_CTR_NAME_OFF = 0x0c,   /* char[16] container name */
    EVENHUB_DEV_TEXT_EVENT_OFF = 0x1c, /* u8 */
    EVENHUB_DEV_LIST_INDEX_OFF = 0x5c, /* u32 selected item index */
    EVENHUB_DEV_LIST_EVENT_OFF = 0x60, /* u8 */
};

/* nanopb 0.4 pb_ostream_t. */
typedef struct {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
} g2_pb_ostream_t;
_Static_assert(sizeof(g2_pb_ostream_t) == 20u, "nanopb ostream");

extern g2_evenhub_tx_msg_t g2_evenhub_tx_msg_20340b48;               /* RAM 0x20340b48 */
extern uint8_t g2_evenhub_tx_buffer_203362c4[EVENHUB_TX_BUFFER_SIZE]; /* RAM 0x203362c4 */
extern const uint8_t g2_evenhub_pb_msg_fields_77754c[];               /* ROM 0x77754c nanopb descriptor */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);                /* 0x43c0e4 */
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* word copy */
extern void audio_pb_ostream_from_buffer(g2_pb_ostream_t *out, void *buf, uint32_t size);   /* 0x4905f4 */
extern uint32_t audio_pb_encode(void *stream, const void *fields, const void *src);          /* pb_encode 0x490c32 */
extern uint32_t Thread_MsgPbNotifyByBle(uint8_t type, uint8_t command, const void *payload, uint16_t length); /* 0x475c1a */

/* evenhub_lock_data / evenhub_unlock_data (evenhub_data_parser.c). */
void evenhub_lock_data_4d9b4a(void);
void evenhub_unlock_data_4d9ba6(void);

#define EVENHUB_PARSER_MODULE "evenhub.data_parser" /* ROM 0x77f3b0 */
#define EVENHUB_PARSER_SOURCE "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenHub\\evenhub_data_parser.c" /* ROM 0x6f3434 */

#define EH_DP_LOG(level, fn, line, mask, fmt, ...) do { \
    if (audio_log_flags() & 2u) \
        audio_log_extended((level), EVENHUB_PARSER_MODULE, EVENHUB_PARSER_SOURCE, (fn), (line), fmt, \
                           ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) \
        (void)compress_log_output((mask), "[evenhub.data_parser]" fmt, "[evenhub.data_parser]" fmt, \
                                  ##__VA_ARGS__); \
} while (0)

/* Lock, clear the tx message and packet buffer, and return the message. */
static inline __attribute__((always_inline)) g2_evenhub_tx_msg_t *evenhub_tx_begin(void)
{
    evenhub_lock_data_4d9b4a();
    audio_uart_buffer_zero(&g2_evenhub_tx_msg_20340b48, EVENHUB_TX_MSG_SIZE, 0u);
    audio_uart_buffer_zero(g2_evenhub_tx_buffer_203362c4, EVENHUB_TX_BUFFER_SIZE, 0u);
    return &g2_evenhub_tx_msg_20340b48;
}

/* Unlock, then encode the tx message into the packet buffer (stock encodes
 * after releasing the lock). Returns the pb_encode result. */
static inline __attribute__((always_inline)) uint32_t evenhub_tx_encode(g2_pb_ostream_t *stream)
{
    g2_pb_ostream_t initial;
    evenhub_unlock_data_4d9ba6();
    audio_pb_ostream_from_buffer(&initial, g2_evenhub_tx_buffer_203362c4, EVENHUB_TX_BUFFER_SIZE);
    (void)audio_uart_display_area_copy_439c04(stream, &initial, sizeof *stream);
    return audio_pb_encode(stream, g2_evenhub_pb_msg_fields_77754c, &g2_evenhub_tx_msg_20340b48);
}

static inline __attribute__((always_inline)) void evenhub_put_u8(uint32_t offset, uint8_t value)
{
    ((uint8_t *)&g2_evenhub_tx_msg_20340b48)[offset] = value;
}

static inline __attribute__((always_inline)) void evenhub_put_u16(uint32_t offset, uint16_t value)
{
    *(uint16_t *)(void *)((uint8_t *)&g2_evenhub_tx_msg_20340b48 + offset) = value;
}

static inline __attribute__((always_inline)) void evenhub_put_u32(uint32_t offset, uint32_t value)
{
    *(uint32_t *)(void *)((uint8_t *)&g2_evenhub_tx_msg_20340b48 + offset) = value;
}

#endif /* G2_EVENHUB_DATA_PARSER_PRIVATE_H */
