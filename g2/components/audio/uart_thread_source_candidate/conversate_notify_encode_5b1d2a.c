/* Apollo Main APP_PbConversateTxEncodeNotify, 0x5b1d2a..0x5b1e51. */
#include <stdint.h>

struct conversate_notify_ostream {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
};
_Static_assert(sizeof(struct conversate_notify_ostream) == 20u,
               "nanopb ostream ABI");

extern uint8_t audio_conversate_response_frame_200f4808[4012];
extern uint8_t audio_conversate_response_encoded_2037c2a0[256];
extern uint8_t audio_conversate_last_magic_20074ff8;
extern const uint8_t audio_conversate_response_descriptor_775b24[];
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_pb_ostream_from_buffer(struct conversate_notify_ostream *,
                                         void *, uint32_t);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern uint32_t audio_pb_encode(struct conversate_notify_ostream *, const void *,
                                const void *);
extern uint8_t audio_uart_device_role_get(void);
extern uint32_t audio_ring_pb_tx_ble_475c1a(uint32_t, uint32_t, const void *,
                                             uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "pb.conversate";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_conversate\\pb_service_conversate.c";
static const char function[] = "APP_PbConversateTxEncodeNotify";
static const char null_message[] = "pNotify is NULL";
static const char null_short[] = "[pb.conversate]pNotify is NULL";
static const char encode_message[] = "Encoding failed: %s";
static const char encode_short[] = "[pb.conversate]Encoding failed: %s";
static const char none[] = "(none)";

uint32_t audio_conversate_ui_close_notify_5b1d2a(const uint16_t *notification)
{
    if (notification == 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, source, function, 0x61u,
                               null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, null_short, null_short);
        return 6u;
    }

    uint8_t *const frame = audio_conversate_response_frame_200f4808;
    uint8_t *const encoded = audio_conversate_response_encoded_2037c2a0;
    audio_uart_buffer_zero(frame, 4012u, 0u);
    frame[0] = 0xa1u;
    frame[1] = (uint8_t)(audio_conversate_last_magic_20074ff8 + 1u);
    *(uint16_t *)(void *)(frame + 2u) = 9u;
    *(uint16_t *)(void *)(frame + 4u) = *notification;

    struct conversate_notify_ostream initial, stream;
    audio_pb_ostream_from_buffer(&initial, encoded, 256u);
    (void)audio_uart_display_area_copy_439c04(&stream, &initial, 20u);
    if (!(uint8_t)audio_pb_encode(&stream,
                                  audio_conversate_response_descriptor_775b24,
                                  frame)) {
        const char *const error = stream.errmsg ? stream.errmsg : none;
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, source, function, 0x6eu,
                               encode_message, error);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04400000u, encode_short,
                                        encode_short, error);
        return 5u;
    }
    const uint32_t length = stream.bytes_written;
    if (audio_uart_device_role_get() == 1u)
        (void)audio_ring_pb_tx_ble_475c1a(1u, 11u, encoded,
                                           (uint16_t)length);
    return 0u;
}
