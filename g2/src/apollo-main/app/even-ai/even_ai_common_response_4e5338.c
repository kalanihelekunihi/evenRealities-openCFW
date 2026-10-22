/* Apollo main APP_PbTxEncodeEvenAICommResp at 0x4e5338.
 * The shared buffers and BLE transport are separate source providers.
 */
#include <stdint.h>
#include "pb_encode.h"

extern uint8_t audio_even_ai_tx_buffer_2037c4a0[256];
extern uint8_t audio_even_ai_proto_message_200f5884[0x20c];
extern const pb_msgdesc_t audio_even_ai_decode_fields;
extern uint32_t audio_ring_pb_tx_ble_475b14(uint32_t, uint32_t, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "pb.evenai";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_even_ai\\pb_service_even_ai.c";
static const char function[] = "APP_PbTxEncodeEvenAICommResp";
static const char length_text[] = "txLen = %d";
static const char length_short[] = "[pb.evenai]txLen = %d";
static const char error_text[] = "Encoding failed: %s\n";
static const char error_short[] = "[pb.evenai]Encoding failed: %s\n";
static const char none[] = "(none)";

/* Stock 0x4E5338 (APP_PbTxEncodeEvenAICommResp) */
uint32_t audio_even_ai_encode_common(uint8_t sequence, const void *payload) {
    pb_ostream_t stream = pb_ostream_from_buffer(audio_even_ai_tx_buffer_2037c4a0,
                                                 256u);
    for (uint32_t i = 0; i < 0x20cu; ++i)
        audio_even_ai_proto_message_200f5884[i] = 0u;
    uint8_t *message = audio_even_ai_proto_message_200f5884;
    message[0] = 0xa1u;
    message[1] = sequence;
    message[2] = 12u;
    message[4] = *(const uint8_t *)payload;
    uint32_t encoded = pb_encode(&stream, &audio_even_ai_decode_fields, message) ? 1u : 0u;
    uint32_t length = (uint32_t)stream.bytes_written & 0xffffu;
    if (encoded == 0u) {
        const char *error = stream.errmsg != 0 ? stream.errmsg : none;
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 899u, error_text, error);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04400000u, error_short, error_short, error);
        return 0x2bu;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0x388u, length_text, length);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, length_short, length_short, length);
    (void)audio_ring_pb_tx_ble_475b14(1u, 7u,
                                       audio_even_ai_tx_buffer_2037c4a0, length);
    return 0u;
}
