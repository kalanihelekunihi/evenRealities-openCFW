/* Transport protocol packet sender, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\transport_protocol\transport_protocol.c.
 * Native TPL_SendPacket 0x4b9640..0x4b9980 (literal pool 0x4b99fc..0x4b9a78).
 *
 * The payload is staged in a 4 KiB static buffer, CRC16 (0x49acd4, seed 0) is
 * taken over the whole payload, and the payload is split into frames of
 * (pipe MTU - 11) bytes. Each frame is an 8-byte header followed by its slice;
 * the last frame also carries the CRC and its length byte counts it (+2).
 * Frames go to the TPL service-0 send callback (row +0x0c); only pipe 0 is
 * served, any other pipe logs "sourceID" and is skipped without an error. */
#include <stdint.h>

/* 8-byte frame header, ROM template 0x78ec74 = aa 02 00 00 00 00 00 00. */
typedef struct {
    uint8_t magic;        /* +0 0xaa */
    uint8_t ids;          /* +1 low nibble sourceID (2), high nibble destinationID */
    uint8_t sequence;     /* +2 low byte of osKernelGetTickCount */
    uint8_t frame_length; /* +3 payload bytes in this frame (+2 CRC on the last) */
    uint8_t frame_count;  /* +4 */
    uint8_t frame_index;  /* +5 1-based */
    uint8_t command;      /* +6 */
    uint8_t flags;        /* +7 bit0 notify */
} g2_tpl_header_t;
_Static_assert(sizeof(g2_tpl_header_t) == 8u, "TPL frame header");

#define TPL_STATIC_BUFFER_SIZE 0x1000u
#define TPL_FRAME_BUFFER_SIZE  0x101u

extern uint8_t audio_tpl_service_table[];         /* RAM 0x20071414, row 0 send callback +0x0c */
extern void *audio_tpl_send_mutex;                /* RAM 0x20074b00 */
extern uint8_t g2_tpl_send_payload_buffer[TPL_STATIC_BUFFER_SIZE]; /* RAM 0x2036fe40 */
extern uint8_t g2_tpl_send_frame_buffer[TPL_FRAME_BUFFER_SIZE];    /* RAM 0x2037c080 */
extern const g2_tpl_header_t g2_tpl_header_template; /* ROM 0x78ec74 */

extern uint16_t slave_cmd_pipe_get_0046f2c6(void);
extern uint16_t audio_uart_hand_checksum_49acd4(const void *data, uint32_t length, const uint16_t *seed);
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);    /* 0x43c0e4 */
extern void audio_uart_checksum_copy(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);                  /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                                    /* 0x44981c */
extern uint32_t osKernelGetTickCount(void);                                    /* 0x4490cc */
extern uint32_t audio_log_flags(void);                                         /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "prot.tran"; /* ROM 0x78c7ac */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\transport_protocol\\transport_protocol.c"; /* ROM 0x6dec74 */
static const char fn_send[] = "TPL_SendPacket"; /* ROM 0x789cc0 */
static const char too_long[] = "Data length %d exceeds static buffer size %d"; /* ROM 0x73a574 */
static const char too_long_short[] = "[prot.tran]Data length %d exceeds static buffer size %d"; /* ROM 0x724ff0 */
static const char no_mutex[] = "Send buffer mutex not initialized"; /* ROM 0x75c114 */
static const char no_mutex_short[] = "[prot.tran]Send buffer mutex not initialized"; /* ROM 0x73a5a4 */
static const char mutex_fail[] = "Failed to acquire send buffer mutex, possible deadlock or timeout"; /* ROM 0x7078b0 */
static const char mutex_fail_short[] = "[prot.tran]Failed to acquire send buffer mutex, possible deadlock or timeout"; /* ROM 0x6f08f8 */
static const char pipe_error[] = "tx pipe error header.b.sourceID = %d error"; /* ROM 0x745c48 */
static const char pipe_error_short[] = "[prot.tran]tx pipe error header.b.sourceID = %d error"; /* ROM 0x725028 */
static const char tx_error[] = "tx ret = %d error"; /* ROM 0x784630 */
static const char tx_error_short[] = "[prot.tran]tx ret = %d error"; /* ROM 0x767210 */

static int log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static int log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

/* Returns 0 ok, 4 mutex missing/busy, 11 bad argument or oversize, else the
 * transport callback's error code. */
uint8_t TPL_SendPacket(uint8_t pipe, uint8_t notify, uint8_t destination_id, uint8_t command,
                       const uint8_t *payload, uint16_t length)
{
    if (payload == 0 || length == 0u)
        return 11u;
    if (length >= TPL_STATIC_BUFFER_SIZE + 1u) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_send, 0x221u, too_long,
                               (uint32_t)length, TPL_STATIC_BUFFER_SIZE);
        if (log_compressed_on())
            (void)compress_log_output(0x04800000u, too_long_short, too_long_short,
                                      (uint32_t)length, TPL_STATIC_BUFFER_SIZE);
        return 11u;
    }

    uint16_t mtu = (uint16_t)(slave_cmd_pipe_get_0046f2c6() - 11u);
    if (audio_tpl_send_mutex == 0) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_send, 0x22au, no_mutex);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, no_mutex_short, no_mutex_short);
        return 4u;
    }
    if (osMutexAcquire(audio_tpl_send_mutex, 100u) != 0) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_send, 0x230u, mutex_fail);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, mutex_fail_short, mutex_fail_short);
        return 4u;
    }

    uint8_t *staged = g2_tpl_send_payload_buffer;
    uint8_t *frame = g2_tpl_send_frame_buffer;
    audio_uart_buffer_zero(staged, TPL_STATIC_BUFFER_SIZE, 0u);
    audio_uart_buffer_zero(frame, TPL_FRAME_BUFFER_SIZE, 0u);
    audio_uart_checksum_copy(staged, payload, length);
    uint16_t crc = audio_uart_hand_checksum_49acd4(staged, length, 0);

    uint16_t count = (uint16_t)(((int32_t)mtu + (int32_t)length - 1) / (int32_t)mtu);
    g2_tpl_header_t header = g2_tpl_header_template;
    header.ids = (uint8_t)((header.ids & 0x0fu) | (uint8_t)(destination_id << 4));
    header.sequence = (uint8_t)osKernelGetTickCount();
    header.frame_count = (uint8_t)count;
    header.command = command;
    header.flags = (uint8_t)((header.flags & 0xfeu) | (notify & 1u));

    for (uint8_t index = 1u; index <= count; ++index) {
        uint16_t offset = (uint16_t)((index - 1u) * mtu);
        uint16_t slice = (index == count) ? (uint16_t)(length - offset) : mtu;
        header.frame_length = (uint8_t)((index == count) ? slice + 2u : slice);
        header.frame_index = index;
        audio_uart_checksum_copy(frame, &header, sizeof header);
        audio_uart_checksum_copy(frame + 8u, staged + offset, slice);
        if (index == count)
            audio_uart_checksum_copy(frame + 8u + slice, &crc, 2u);

        uint8_t result = 0u;
        if (pipe == 0u) {
            uintptr_t callback;
            __builtin_memcpy(&callback, audio_tpl_service_table + 0x0cu, sizeof callback);
            if (callback != 0u)
                result = ((uint8_t (*)(uint8_t *, uint16_t))callback)(frame,
                                                                      (uint16_t)(header.frame_length + 8u));
        } else {
            if (log_extended_on())
                audio_log_extended(1u, module_tag, source_file, fn_send, 0x293u, pipe_error,
                                   (uint32_t)(header.ids & 0x0fu));
            if (log_compressed_on())
                (void)compress_log_output(0x04400000u, pipe_error_short, pipe_error_short,
                                          (uint32_t)(header.ids & 0x0fu));
        }
        if (result != 0u) {
            if (log_extended_on())
                audio_log_extended(1u, module_tag, source_file, fn_send, 0x298u, tx_error,
                                   (uint32_t)result);
            if (log_compressed_on())
                (void)compress_log_output(0x04400000u, tx_error_short, tx_error_short,
                                          (uint32_t)result);
            (void)osMutexRelease(audio_tpl_send_mutex);
            return result;
        }
    }
    (void)osMutexRelease(audio_tpl_send_mutex);
    return 0u;
}
