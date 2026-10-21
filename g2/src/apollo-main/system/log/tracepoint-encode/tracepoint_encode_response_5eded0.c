/* Stock Main tracepoint_encode_response 0x5eded0 and bounded TX RAM. */
#include <stdint.h>

struct tracepoint_ostream {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
};
_Static_assert(sizeof(struct tracepoint_ostream) == 20u, "nanopb ostream ABI");

uint8_t audio_tracepoint_encoded_buffer[0x300]
    __attribute__((section(".bss.opencfw.tracepoint.encoded"), aligned(4), used));
_Static_assert(sizeof(audio_tracepoint_encoded_buffer) == 0x300u,
               "stock tracepoint TX clear span");

extern const uint8_t audio_tracepoint_message_descriptor[];
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_pb_ostream_from_buffer(struct tracepoint_ostream *, void *, uint32_t);
extern void audio_uart_checksum_copy(void *, const void *, uint32_t);
extern uint32_t audio_pb_encode(struct tracepoint_ostream *, const void *, const void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "tp.setting";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\tracepoint\\tracepoint_setting.c";
static const char function[] = "tracepoint_encode_response";
static const char none[] = "(none)";
static const char fail_msg[] = "tracepoint protobuf encode failed: %s";
static const char fail_short[] = "[tp.setting]tracepoint protobuf encode failed: %s";
static const char success_msg[] = "tracepoint encode rsp cmd=%d which=%u len=%u";
static const char success_short[] = "[tp.setting]tracepoint encode rsp cmd=%d which=%u len=%u";

uint32_t audio_tracepoint_encode_response_5eded0(const uint8_t *message,
                                                   uint16_t *length)
{
    struct tracepoint_ostream initial, stream;
    audio_uart_buffer_zero(audio_tracepoint_encoded_buffer, 0x300u, 0u);
    audio_pb_ostream_from_buffer(&initial, audio_tracepoint_encoded_buffer, 0x300u);
    audio_uart_checksum_copy(&stream, &initial, 20u);
    if (audio_pb_encode(&stream, audio_tracepoint_message_descriptor, message) == 0u) {
        const char *error = stream.errmsg ? stream.errmsg : none;
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 0xe4u, fail_msg, error);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04400000u, fail_short, fail_short, error);
        return UINT32_MAX;
    }
    *length = (uint16_t)stream.bytes_written;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0xeau, success_msg,
                           message[0], (uint16_t)(message[2] | ((uint16_t)message[3] << 8)),
                           *length);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10c00000u, success_short, success_short,
                                    message[0],
                                    (uint16_t)(message[2] | ((uint16_t)message[3] << 8)),
                                    *length);
    return 0u;
}
