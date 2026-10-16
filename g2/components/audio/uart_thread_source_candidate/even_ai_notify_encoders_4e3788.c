/* Stock EvenAI local control/VAD notification encoders 0x4e3788/0x4e3b80.
 * Success path uses the authenticated nanopb descriptor and BLE notify body.
 */
#include <stdint.h>
#include "pb_encode.h"

struct even_ai_notify_fault_record {
    uint32_t type, detail;
    const char *path, *function;
    uint32_t line;
};
_Static_assert(sizeof(struct even_ai_notify_fault_record) == 20u, "fault ABI");

extern uint8_t audio_even_ai_tx_buffer_2037c4a0[256];
extern uint8_t audio_even_ai_proto_message_200f5884[0x20c];
extern const pb_msgdesc_t audio_even_ai_decode_fields;
extern void audio_ring_pb_assert_509b48(const struct even_ai_notify_fault_record *);
extern uint32_t audio_ring_pb_tx_ble_475c1a(uint32_t, uint32_t, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

extern uint8_t audio_even_ai_notify_sequence_20074ff9;

static const char module[] = "pb.evenai";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_even_ai\\pb_service_even_ai.c";
static const char null_text[] = "PORINT NULL";
static const char null_short[] = "[pb.evenai]PORINT NULL";
static const char tx_text[] = "txLen = %d";
static const char tx_short[] = "[pb.evenai]txLen = %d";
static const char error_text[] = "Encoding failed: %s\n";
static const char error_short[] = "[pb.evenai]Encoding failed: %s\n";
static const char none[] = "(none)";

struct notify_config {
    const char *function;
    uint32_t fault_line, null_line, length_line, error_line;
    uint8_t command, oneof;
};
static const struct notify_config ctrl = {
    "APP_PbNotifyEncodeEvenAICtrl", 0xecu, 0xeeu, 0x101u, 0x104u, 1u, 3u
};
static const struct notify_config vad = {
    "APP_PbNotifyEncodeEvenAIVADInfo", 0x146u, 0x148u, 0x15bu, 0x15eu, 2u, 4u
};

static uint32_t encode(const struct notify_config *config, const void *payload) {
    if (payload == 0) {
        struct even_ai_notify_fault_record fault = {
            0u, 1u, path, config->function, config->fault_line
        };
        audio_ring_pb_assert_509b48(&fault);
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, config->function,
                               config->null_line, null_text);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, null_short, null_short);
        return 2u;
    }
    pb_ostream_t stream = pb_ostream_from_buffer(audio_even_ai_tx_buffer_2037c4a0,
                                                 256u);
    for (uint32_t i = 0; i < 0x20cu; ++i)
        audio_even_ai_proto_message_200f5884[i] = 0u;
    audio_even_ai_proto_message_200f5884[0] = config->command;
    audio_even_ai_proto_message_200f5884[1] = audio_even_ai_notify_sequence_20074ff9++;
    audio_even_ai_proto_message_200f5884[2] = config->oneof;
    audio_even_ai_proto_message_200f5884[4] = *(const uint8_t *)payload;
    uint32_t encoded = pb_encode(&stream, &audio_even_ai_decode_fields,
                                 audio_even_ai_proto_message_200f5884) ? 1u : 0u;
    uint32_t length = (uint32_t)stream.bytes_written & 0xffffu;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, config->function,
                           config->length_line, tx_text, length);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10400000u, tx_short, tx_short, length);
    if (encoded == 0u) {
        const char *error = stream.errmsg ? stream.errmsg : none;
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, config->function,
                               config->error_line, error_text, error);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04400000u, error_short,
                                        error_short, error);
        return 0x2bu;
    }
    (void)audio_ring_pb_tx_ble_475c1a(1u, 7u,
                                       audio_even_ai_tx_buffer_2037c4a0, length);
    return 0u;
}

uint32_t audio_even_ai_encode_ctrl_4e3788(uint32_t unused, const void *payload) {
    (void)unused;
    return encode(&ctrl, payload);
}

uint32_t audio_even_ai_encode_vad_4e3b80(uint32_t unused, const void *payload) {
    (void)unused;
    return encode(&vad, payload);
}
