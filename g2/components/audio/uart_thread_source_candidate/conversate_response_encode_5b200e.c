/* Native APP_PbConversateTxEncodeCommResp 0x5b200e..0x5b212d. */
#include <stdint.h>

struct conversate_ostream {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
};
_Static_assert(sizeof(struct conversate_ostream) == 20u, "nanopb ostream ABI");

extern uint8_t audio_conversate_response_frame_200f4808[4012];
extern uint8_t audio_conversate_response_encoded_2037c2a0[256];
extern const uint8_t audio_conversate_response_descriptor_775b24[];
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_pb_ostream_from_buffer(struct conversate_ostream *, void *, uint32_t);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern uint32_t audio_pb_encode(struct conversate_ostream *, const void *, const void *);
extern void audio_dump_hex(const char *, uint32_t, const uint8_t *, uint32_t);
extern uint8_t audio_uart_device_role_get(void);
extern uint32_t audio_ring_pb_tx_ble_475b14(uint32_t, uint32_t, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "pb.conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_conversate\\pb_service_conversate.c";
static const char function[] = "APP_PbConversateTxEncodeCommResp";
static const char none[] = "(none)";
static const char null_message[] = "pResp is NULL";
static const char null_short[] = "[pb.conversate]pResp is NULL";
static const char encode_message[] = "Encoding failed: %s";
static const char encode_short[] = "[pb.conversate]Encoding failed: %s";
static const char dump_label[] = "Conversate_pb_resp";

uint32_t audio_conversate_respond_5b200e(const uint8_t *response,
                                            uint32_t command) {
    if (response == 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 177u,
                               null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, null_short, null_short);
        return 6u;
    }
    uint8_t *const frame = audio_conversate_response_frame_200f4808;
    uint8_t *const encoded = audio_conversate_response_encoded_2037c2a0;
    audio_uart_buffer_zero(frame, 4012u, 0u);
    frame[0] = 0xa2u;
    frame[1] = (uint8_t)command;
    frame[2] = 10u;
    frame[3] = 0u;
    frame[4] = response[0];
    struct conversate_ostream stream, encoded_stream;
    audio_pb_ostream_from_buffer(&stream, encoded, 256u);
    (void)audio_uart_display_area_copy_439c04(&encoded_stream, &stream, 20u);
    if (!(uint8_t)audio_pb_encode(&encoded_stream,
                                  audio_conversate_response_descriptor_775b24,
                                  frame)) {
        const char *error = encoded_stream.errmsg ? encoded_stream.errmsg : none;
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 190u,
                               encode_message, error);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04400000u, encode_short, encode_short, error);
        return 5u;
    }
    const uint32_t length = (uint16_t)encoded_stream.bytes_written;
    audio_dump_hex(dump_label, 16u, encoded, length);
    if (audio_uart_device_role_get() == 1u)
        (void)audio_ring_pb_tx_ble_475b14(1u, 11u, encoded, length);
    return 0u;
}
